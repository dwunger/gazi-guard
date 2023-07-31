import os
import sys
import threading
import time

import pystray
from PIL import Image

from pystray import MenuItem as item
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from abstract_message import AbstractMessage
from backups import BackupHandler
from configs import Config
from file_system import *
from melder import (MeldHandler, get_meld_path, launch_meld,
                    prompt_enter_config, prompt_install_meld,
                    wait_for_meld_installation)
from notifs import RateLimitedNotifier, show_notification
from utils import resource_path
from logs import Logger
#BUG #?(sort of): need to generate a flag if process holds archive hostage. For example, 7zip likes to prevent writes to an open archive, but this is currently not detected, so writes are lost
#!QUIRK: App tray icon managed from main.py as separate process from GUI process
#!QUIRK: prints with '*' prefix interpreted by std out as commands as per abstract_message construct
#TODO: Update status of repack in GUI - Done with some caveats. Would be best to centralize mod_pak status to class and handle updates internally


# class FileChangeHandler(FileSystemEventHandler):
#     """Handle file or directory modification."""
#     def __init__(self, mod) -> None:
#         self.mod = mod
#         self.rate_limiter = RateLimitedNotifier()

#     def on_modified(self, event):
#         comms.send_message(comms.message.data('on_modified_event'))
#         self.mod.status = 'desync'
#         # Check if the modified file or directory is in the mod.unpacked_path
#         if os.path.commonpath([self.mod.unpacked_path, event.src_path]) == self.mod.unpacked_path:
#             # Get the relative path of the modified file or directory
#             relative_path = os.path.relpath(event.src_path, self.mod.unpacked_path)
#             # Update archive with modified file or directory
#             update_archive(event.src_path, self.mod.packed_path, relative_path, delay=0.2)
#             self.mod.status = 'sync'
#             self.rate_limiter.notify(title='Gazi Guard', message='Changes saved!')
#         else:
#             self.mod.status = 'sync' 

#     @staticmethod
#     def _is_file_access_done(file_path):
#         '''race condition with meld'''
#         try:
#             with open(file_path, 'r'):
#                 return True
#         except IOError:
#             return False

class FileChangeHandler(FileSystemEventHandler):
    # def __init__(self, mod_unpack_path, mod_pak, copy_to) -> None:
    def __init__(self, mod, notifications) -> None:
        self.mod = mod
        # self.copy_to = copy_to

        self.rate_limiter = RateLimitedNotifier(enabled=notifications)

    def on_modified(self, event):
        logger.log_variable("event", event)
        comms.send_message(comms.message.data('on_modified_event'))
        mod.status = 'desync'
        if not event.is_directory:
            # Check if the modified file is in the mod.unpacked_path
            if os.path.commonpath([self.mod.unpacked_path]) == self.mod.unpacked_path:
                logger.log_variable("    self.mod.unpacked_path", self.mod.unpacked_path)
                logger.log_variable("    self.mod.packed_path", self.mod.packed_path)
                update_archive(self.mod.unpacked_path, self.mod.packed_path, delay = 0.4)
                mod.status = 'sync'
                # if self.copy_to:
                #     update_archive(self.mod.unpacked_path, self.copy_to)
                self.rate_limiter.notify(title='Gazi Guard', message='Changes saved!')
        mod.status = 'sync'    
    @staticmethod
    def _is_file_access_done(file_path):
        '''race condition with meld'''
        try:
            with open(file_path, 'r'):
                return True
        except IOError:
            return False
class ModArchive:
    def __init__(self, comms):
        # Path to the mod archive
        self.comms = comms
        self.status = 'sync'
        self.action = 'Initialized. No changes detected.'
        self.unpacked_path = None
        self.packed_path = None
        comms.send_message(comms.message.action(self.action))
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, state):

        if state == 'desync':
            self.action = 'Updating...'
            
        if state == 'sync':
            self.action = 'Repacked!'
        comms.send_message(comms.message.set(state))            
        comms.send_message(comms.message.action(self.action))
        self._status = state

class ObserverHandler:
    # def __init__(self, mod_unpack_path, mod_pak, copy_to):
    def __init__(self, mod, notifications):
        self.mod = mod
        self.mod_unpack_path = mod.unpacked_path
        self.mod_pak = mod.packed_path
        self.notifications = notifications
        # self.copy_to = copy_to
        self.file_observer = Observer()
        # self.event_handler = FileChangeHandler(mod_unpack_path=self.mod_unpack_path, mod_pak=self.mod_pak, copy_to=self.copy_to)
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



    # if not mod_path:
    # time.sleep(10)
    # logger.log_variable('')
    backup_path = os.path.join(target_workspace, 'Unpacked\\backups\\')
    # mod.packed_path = choose_mod_pak(os.path.join(target_workspace,mod_path), target_workspace)
    
    # logger.log_variable("mod.packed_path", mod.packed_path)
    # logger.log_variable("target_workspace", target_workspace)
    # # logger.log_variable("copy_to", copy_to)
    # # logger.log_variable("deep_scan_enabled", deep_scan_enabled)
    # # logger.log_variable("source_pak_0", source_pak_0)
    # # logger.log_variable("source_pak_1", source_pak_1)
    # logger.log_variable("mod_path", mod_path)
    # logger.log_variable("overwrite_default", overwrite_default)
    # logger.log_variable("hide_unpacked_content", hide_unpacked_content)
    # logger.log_variable("meld_config_path", meld_config_path)
    # logger.log_variable("use_meld", use_meld)
    # logger.log_variable("backup_enabled", backup_enabled)
    # logger.log_variable("backup_count", backup_count)
    #immediate backup on selection
    if backup_enabled:
        backup_handler = BackupHandler(backup_path, backup_count, mod.packed_path)
    source_pak_0 = os.path.join(target_workspace, source_pak_0)
    source_pak_1 = os.path.join(target_workspace, source_pak_1)
    mod.unpacked_path =  os.path.join(target_workspace, f"Unpacked\\{file_basename(mod.packed_path)}_mod_scripts")
    merged_unpack_path = os.path.join(target_workspace, f'Unpacked\\{file_basename(mod.packed_path)}_source_scripts')
    if config.force_refresh_mod_scripts:
        logger.log_warning('Force Refresh Mod Enabled! Deleting Unpacked Mod Scripts')
        shutil.rmtree(mod.unpacked_path)   
    if config.force_refresh_source_scripts:
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

class CommsManager():
    def __init__(self):
        self.running = False
        self.listener_thread = None
        self.message = AbstractMessage()
        self.inbox = {}
    def request(self,item):
        self.send_message(self.message.request(item))
        
        while item not in self.inbox:
            time.sleep(0.01)
        return self.inbox[item]
            
        
    def listen(self):
        '''starts daemon thread '''
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def stop(self):
        self.running = False
        if self.listener_thread is not None:
            self.listener_thread.join()

    def _listen(self):
        while self.running:
            # Receive messages from the frontend
            stdin = sys.stdin.readline().strip()
            stdin = [line.strip('*') for line in stdin.split('\n') if line.startswith('*')]
            # logger_iter(stdin)
            for line in stdin:
                # Process the received message
                response = self.process_message(line)
                # Send the response back to the frontend
                if response:
                    self.send_message(response)
            
    def process_message(self, data):
        # Add your custom logic here based on the received message
   
        payload_type, payload = data.split(":")
        
        return self.compose_response(payload_type, payload)
    

    def send_message(self, response):
        # Send the response back to the frontend
        
        print(response, flush=True)
        sys.stdout.flush()
        sys.stderr.flush()

    def compose_response(self, payload_type, payload):
        #map message type and payload to a response for return value
        #start with exhaustive switching
        if payload_type == 'request':
            if payload == 'pid':
                return self.message.pid(os.getpid())
        if payload_type == 'pid':
            #no response
            self.inbox[payload_type]=int(payload)
            return None
            

def main():
    merged_unpack_path, use_meld, meld_config_path, copy_to, notifications = initialize_workspace()
    # logger.log_variable("merged_unpack_path", merged_unpack_path)
    # logger.log_variable("use_meld", use_meld)
    # logger.log_variable("meld_config_path", meld_config_path)
    # logger.log_variable("copy_to", copy_to)
    
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
