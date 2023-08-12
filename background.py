import filecmp
import os
import queue
import shutil
import sys
import tempfile
import threading
import time

import pystray
from PIL import Image
from pystray import MenuItem as item
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from backups import BackupHandler
from communications import CommsManager
from configs import Config
from file_system import *
from logs import Logger
from melder import (MeldHandler, get_meld_path, launch_meld,
                    prompt_enter_config, prompt_install_meld,
                    wait_for_meld_installation)
from mod_archive import ModArchive, ModStatus
from notifs import RateLimitedNotifier, show_notification
from utils import file_selector_dialog, resource_path
from ZipUtils import czip
from ZipUtils.czip import ZipHandler


def delete_file_from_zip(zip_file_path: str, file_to_delete: str) -> dict:
    import json
    import subprocess
    """
    Delete a file from a zip archive.

    Parameters:
        zip_file_path (str): The path to the zip archive.
        file_to_delete (str): The relative path of the file to delete within the zip archive.
                              Note: Relative paths should use forward slashes ("/") even on Windows.

    Returns:
        dict: A dictionary containing the result of the operation. The dictionary will have two keys:
            - 'Success': A boolean indicating if the deletion was successful.
            - 'Path': The path of the file that was deleted if successful, or an error message if unsuccessful.
    """
    input_data = {
        "ZipFilePath": zip_file_path,
        "FileToDelete": file_to_delete
    }
    json_input = json.dumps(input_data)
    result = subprocess.run(["ZipUtils/resources/ZipProc.exe"], input=json_input, text=True, capture_output=True)

    try:
        result_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        result_data = {"Success": False, "Path": "Invalid JSON format."}

    return result_data
class FileChangeHandler(FileSystemEventHandler):
    
    def __init__(self, mod, notifications) -> None:
        super().__init__()
        self.mod = mod
        self.zip_handler = ZipHandler(self.mod.packed_path)
        self.rate_limiter = RateLimitedNotifier(enabled=notifications)
        self.event_queue = queue.Queue()
        self.events = []

        # Start the daemon thread
        self.event_processor_thread = threading.Thread(target=self.dequeue_events)
        self.event_processor_thread.daemon = True
        self.event_processor_thread.start()

    def add_event(self, event):
        '''adds attrs commonpath and relative path to simplify reconstructing file structure from mod directory root'''
        absolute_path = event.src_path
        print(event.event_type, file = sys.stderr)
        if event.event_type == "moved":
            absolute_path = event.dest_path
        event.common_path = os.path.commonpath([absolute_path, self.mod.unpacked_path])
        event.relative_path = os.path.relpath(absolute_path, self.mod.unpacked_path)
        self.event_queue.put(event)
        
    def process_events(self):
        # called from dequeue_events process_events provides a thread-safe scope to work on the self.events list
        # Any directory level operations or numerous individual operations will cause a complete repack and returns early.
        # The goal is to perform operations at a time complexity of O(m) using czip unless the cumulative time is 
        # greater than the time complexity of update_archive at O(n*m). It should be possible to obsolete update_archive
        # by removing the zipfile overhead and event batches in czip. This is left as an exercise for future me
        
        #events types are lower case: created, modified, deleted, and moved

        creations     = []
        modifications = []
        deletions     = []        
        movements     = []


        for event in self.events:
            if event.is_directory:
                print("Detected folder change. Full repack.", file=sys.stderr)
                update_archive(self.mod.unpacked_path, self.mod.packed_path, delay=0.1)
                self.mod.status = 'sync'
                return
            
            elif event.event_type == 'created' and os.path.exists(event.src_path):
                if 'goutputstream' not in event.src_path:
                    print(event, file=sys.stderr)
                    creations.append(event)
            elif event.event_type == 'modified' and os.path.exists(event.src_path):
                if 'goutputstream' not in event.src_path:
                    print(event, file=sys.stderr)
                    modifications.append(event)
            elif event.event_type == 'deleted':
                print(event, file=sys.stderr)
                deletions.append(event)
            elif event.event_type == 'moved' and os.path.exists(event.dest_path):
                print(event, file=sys.stderr)
                movements.append(event)
        
        IO_count = len(creations) + len(modifications) + len(deletions) + len(movements)
        if IO_count > 10:
            update_archive(self.mod.unpacked_path, self.mod.packed_path, delay=0.1)
            self.mod.status = 'sync'
            return
        # order of operations → delete then create
        # modify will be a combination of delete → create
        
        for event in deletions:
            delete_file_from_zip(self.mod.packed_path, event.relative_path)
        for event in movements:
            if 'goutputstream' in event.src_path:
                delete_file_from_zip(self.mod.packed_path,event.relative_path)
        
        with zipfile.ZipFile(self.mod.packed_path, 'a') as mod_pak:
            write_paths = []
            for event in creations:
                path_args = (event.src_path, event.relative_path)
                if path_args not in write_paths:
                    write_paths.append(path_args)
            for event in modifications:
                path_args = (event.src_path, event.relative_path)
                if path_args not in write_paths:
                    write_paths.append(path_args)
            for event in movements:
                path_args = (event.dest_path, event.relative_path)
                if path_args not in write_paths:
                    write_paths.append(path_args)  
            for path_args in write_paths:
                print(f'WRITE TASK {path_args}', file=sys.stderr)
                src, dst = path_args
                src, dst = src.replace('\\', '/'), dst.replace('\\', '/')
                mod_pak.write(src, dst, compress_type = zipfile.ZIP_DEFLATED)            
        #clear the event list before returning to dequeue
        self.events.clear()
        
        #Confirm repacking occured on front-end
        self.mod.status = 'sync'
    
    def dequeue_events(self):
        while True:
            # Sleep for 1 second before checking the queue
            time.sleep(2)
            
            batch = []
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                batch.append(event)
            
            # Transfer the batch to the main list
            self.events.extend(batch)
            
            # Call the process_events method to process the batch
            self.process_events()

    def on_created(self, event):
        print(f"on_created event: {event}", file=sys.stderr)
        self.add_event(event) 
        self.mod.status = 'desync'
        
    def on_deleted(self, event):
        print(f"on_deleted event: {event}", file=sys.stderr)
        self.add_event(event)  
        self.mod.status = 'desync'     
           
    def on_modified(self, event):
        print(f"event: {event}", file=sys.stderr)
        self.add_event(event)  
        self.mod.status = 'desync'
        
    def on_moved(self, event):
        print(f"on_moved event: {event}", file=sys.stderr)
        self.add_event(event)  
        self.mod.status = 'desync'        

class ObserverHandler:
    def __init__(self, mod, notifications):
        self.mod = mod
        self.mod_unpack_path = mod.unpacked_path
        self.mod_pak = mod.packed_path
        self.notifications = notifications
        self.file_observer = Observer()
        self.event_handler = FileChangeHandler(mod, notifications)
    def start(self):
        self.file_observer.schedule(self.event_handler, path=self.mod_unpack_path, recursive=True)
        self.file_observer.start()

    def stop(self):
        self.file_observer.stop()
        self.file_observer.join()

def tray_thread():
    def prefs():
        # Start the GUI thread
        if bring_window_to_front_by_pid(comms.request('pid')): #-> boolready to enter config bool
            pass
    # Create a function to handle the kill action
    def kill_action(icon, item):
        # backend should run independently from frontend. This gives a hand should user decide not to use GUI.py
        icon.stop()
        os.kill(os.getpid(), 9)
    # Create a function to build the system tray menu
    def build_menu():
        menu = (
            item('Close', kill_action),
            # item('Pak Tools', prefs)
        )
        return menu
    # Load the application icon
    icon_path = 'icon64.ico'
    icon_image = Image.open(icon_path)
    # Create the system tray icon
    icon = pystray.Icon('Gazi Guard', icon_image, 'Gazi Guard', menu=build_menu())
    icon.run()
    
            
def initialize_workspace():
    #this was broke off from main() as no threading was necessary.
    config = Config()
    target_workspace, copy_to, deep_scan_enabled, source_pak_0, source_pak_1, mod.packed_path, overwrite_default, \
        hide_unpacked_content, meld_config_path, use_meld, backup_enabled, backup_count, notifications = config.dump_settings()

    logger.log_info(f"\ntarget_workspace: {target_workspace}\nmod.packed_path: {mod.packed_path}\nmeld_config_path: {meld_config_path}")
    
    with zipfile.ZipFile(mod.packed_path, 'r') as zip_read:
        if len(zip_read.namelist()) == 0:
            with zipfile.ZipFile(mod.packed_path, 'w') as zip:
                zip.writestr("GENERATED", "This file was automatically generated.")
    if target_workspace is None or not os.path.exists(target_workspace):
        logger.log_warning('target_workspace is None:')
        user_selection = file_selector_dialog("Folder containing data0.pak, data1.pak, and dataX.pak")
        config.target_workspace, target_workspace = user_selection, user_selection

    if mod.packed_path is None or not os.path.exists(mod.packed_path):
        logger.log_warning('mod.packed_path is None:')
        user_selection = file_selector_dialog("Please select your mod 'dataX.pak'", file_extension="*.pak", file_type_description="Compressed Mod")
        config.mod_pak, mod.packed_path = user_selection, user_selection

                

    if meld_config_path is None or not os.path.exists(meld_config_path):
        # this should be handled already, but the old handle is broken. This serves as a backup until the old method is fixed.
        logger.log_warning('meld_config_path is None')
        user_selection = file_selector_dialog("Please select Meld.exe", file_extension="*.exe", file_type_description="Meld Executable")
        config.meld_config_path, meld_config_path = user_selection, user_selection

    backup_path = os.path.join(target_workspace, 'Unpacked\\backups\\')
    #region LOGGING VARS
    # mod.packed_path = choose_mod_pak(os.path.join(target_workspace,mod_path), target_workspace)
    logger.log_variable("mod.packed_path", mod.packed_path)
    logger.log_variable("target_workspace", target_workspace)
    logger.log_variable("copy_to", copy_to)
    logger.log_variable("deep_scan_enabled", deep_scan_enabled)
    logger.log_variable("source_pak_0", source_pak_0)
    logger.log_variable("source_pak_1", source_pak_1)
    logger.log_variable("mod.unpacked_path", mod.unpacked_path)
    logger.log_variable("overwrite_default", overwrite_default)
    logger.log_variable("hide_unpacked_content", hide_unpacked_content)
    logger.log_variable("meld_config_path", meld_config_path)
    logger.log_variable("use_meld", use_meld)
    logger.log_variable("backup_enabled", backup_enabled)
    logger.log_variable("backup_count", backup_count)
    #immediate backup on selection
    #endregion
    
    if backup_enabled:
        backup_handler = BackupHandler(backup_path, backup_count, mod.packed_path)
    source_pak_0 = os.path.join(target_workspace, source_pak_0)
    source_pak_1 = os.path.join(target_workspace, source_pak_1)
    mod.unpacked_path =  os.path.join(target_workspace, f"Unpacked\\{file_basename(mod.packed_path)}_mod_scripts")
    merged_unpack_path = os.path.join(target_workspace, f'Unpacked\\{file_basename(mod.packed_path)}_source_scripts')
    if config.force_refresh_mod_scripts and os.path.exists(mod.unpacked_path):
        logger.log_warning('Force Refresh Mod Enabled! Deleting Unpacked Mod Scripts')
        shutil.rmtree(mod.unpacked_path)   
    if config.force_refresh_source_scripts and os.path.exists(mod.unpacked_path):
        logger.log_warning('Force Refresh Source Enabled! Deleting Source Scripts')
        shutil.rmtree(merged_unpack_path)   
    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                         " Try running from ./steamapps/common/Dying Light 2/ph/source/"
                         
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              
    # logger.log_variable('mod.packed_path***', mod.packed_path)
    mod_file_names = get_mod_files(mod.packed_path)         

    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)
    
    prompt_to_overwrite(mod.packed_path, mod.unpacked_path, deep_scan_enabled, overwrite_default)
    
    set_folder_attribute(hide_unpacked_content, target_workspace, merged_unpack_path, mod.unpacked_path)

    return (merged_unpack_path, use_meld, meld_config_path, copy_to, notifications)



def main():
    merged_unpack_path, use_meld, meld_config_path, copy_to, notifications = initialize_workspace()
    
    #region LOGGING MAINLOOP VARS
    # logger.log_variable("merged_unpack_path", merged_unpack_path)
    # logger.log_variable("use_meld", use_meld)
    # logger.log_variable("meld_config_path", meld_config_path)
    # logger.log_variable("copy_to", copy_to)
    #endregion
    
    # Create the system tray icon
    tray = threading.Thread(target=tray_thread)
    tray.daemon = True  # Allow the program to exit even if the thread is running
    tray.start()

    meld_handler = MeldHandler(mod.unpacked_path, merged_unpack_path, use_meld, meld_config_path) #abs path, abs path, bool, config path
    meld_handler.handle()
    meld_pid = int(meld_handler.meld_process.pid)
    comms.send_message(comms.message.edior_pid(meld_pid))
    comms.send_message(comms.message.set('sync'))
    observer_handler = ObserverHandler(mod, notifications) #removed copy_to
    observer_handler.start()
    
    try:
        while meld_handler.poll() is None:
            comms.send_message(comms.message.awake('main'))
            comms.send_message(comms.message.set(mod.status))
            time.sleep(1)
    finally:
        observer_handler.stop()

    # print('Meld process has exited. Exiting script...')


if __name__ == '__main__':
    logger = Logger()
    logger.log_info("Logger Started")
    comms = CommsManager()
    comms.listen()
    mod = ModArchive(comms)        
    # Run the main program
    main()
