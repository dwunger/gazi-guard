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

#BUG #?(sort of): need to generate a flag if process holds archive hostage. For example, 7zip likes to prevent writes to an open archive, but this is currently not detected, so writes are lost
#!QUIRK: App tray icon managed from main.py as separate process from GUI process

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, mod_unpack_path, mod_pak, copy_to) -> None:
        self.mod_unpack_path = mod_unpack_path
        self.mod_pak = mod_pak
        self.copy_to = copy_to
        self.rate_limiter = RateLimitedNotifier()
    def on_modified(self, event):
        if not event.is_directory:
            # Check if the modified file is in the mod_unpack_path
            #print('Change detected! Do not exit while saving...')
            # print(f'Modified file: {event.src_path}')
            if os.path.commonpath([self.mod_unpack_path]) == self.mod_unpack_path:
                # Example usage
                # rate_limiter.notify('Pak Tools', 'Mod is being updated...')
                update_archive(self.mod_unpack_path, self.mod_pak)
                if self.copy_to:
                    update_archive(self.mod_unpack_path, self.copy_to)
                self.rate_limiter.notify(title='Pak Tools', message='Changes saved!')

class ObserverHandler:
    def __init__(self, mod_unpack_path, mod_pak, copy_to):
        self.mod_unpack_path = mod_unpack_path
        self.mod_pak = mod_pak
        self.copy_to = copy_to
        self.file_observer = Observer()
        self.event_handler = FileChangeHandler(mod_unpack_path=self.mod_unpack_path, mod_pak=self.mod_pak, copy_to=self.copy_to)

    def start(self):
        self.file_observer.schedule(self.event_handler, path=self.mod_unpack_path, recursive=True)
        self.file_observer.start()

    def stop(self):
        self.file_observer.stop()
        self.file_observer.join()

def tray_thread():
    def prefs():
        # Start the GUI thread
        if prompt_enter_config(): #-> boolready to enter config bool
            pass
    # Create a function to handle the kill action
    def kill_action(icon, item):
        # backend should run independently from frontend. This gives a hand should user decide not to use views.py
        icon.stop()
        os.kill(os.getpid(), 9)
    # Create a function to build the system tray menu
    def build_menu():
        menu = (
            item('Close', kill_action),
            item('Preferences', prefs)
        )
        return menu
    # Load the application icon
    icon_path = 'icon64.ico'
    icon_image = Image.open(icon_path)
    # Create the system tray icon
    icon = pystray.Icon('Pak Tools', icon_image, 'Pak Tools', menu=build_menu())
    icon.run()
    
            
def initialize_workspace():
    config = Config()
    
    target_workspace, copy_to, deep_scan_enabled, source_pak_0, source_pak_1, mod_path, overwrite_default, \
        hide_unpacked_content, meld_config_path, use_meld, backup_enabled, backup_count = config.dump_settings()
    backup_path = os.path.join(target_workspace, 'Unpacked\\backups\\')
    mod_pak = choose_mod_pak(os.path.join(target_workspace,mod_path), target_workspace)

    #immediate backup on selection
    if backup_enabled:
        backup_handler = BackupHandler(backup_path, backup_count, mod_pak)
    source_pak_0 = os.path.join(target_workspace, source_pak_0)
    source_pak_1 = os.path.join(target_workspace, source_pak_1)
    mod_unpack_path =  os.path.join(target_workspace, f"Unpacked\\{file_basename(mod_pak)}_mod_scripts")
    merged_unpack_path = os.path.join(target_workspace, f'Unpacked\\{file_basename(mod_pak)}_source_scripts')

    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                         " Try running from ./steamapps/common/Dying Light 2/ph/source/"
    
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              

    mod_file_names = get_mod_files(mod_pak)        

    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)
    
    prompt_to_overwrite(mod_pak, mod_unpack_path, deep_scan_enabled, overwrite_default)
    
    set_folder_attribute(hide_unpacked_content, target_workspace, merged_unpack_path, mod_unpack_path)
    #print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → {mod_unpack_path}\nUnpacked source scripts → {merged_unpack_path}\n")
    # print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts > {mod_unpack_path}\nUnpacked source scripts > {merged_unpack_path}\n")
    return (mod_unpack_path, merged_unpack_path, use_meld, meld_config_path, copy_to, mod_pak)
def get_int_date():
    import datetime
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")
run_number = get_int_date()

log_file = f"LOG_{run_number}.log"
if os.path.exists(log_file):
    os.remove(log_file)
def logger_iter(iterable):
    with open(log_file, 'a+') as log:
        log.write('#######MAIN########\n')
        log.write('iterable: \n')
        log.writelines(iterable)
        log.write('\n')
        log.write('#######MAIN########\n')
def logger_str(text):
    with open(log_file, 'a+') as log:
        log.write('#######MAIN########\n')
        log.write(text + "\n")
        log.write('#######MAIN########\n')
class CommsManager():

    def __init__(self):
        self.running = False
        self.listener_thread = None
        self.message = AbstractMessage()

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
            logger_iter(stdin)
            for line in stdin:
                # Process the received message
                response = self.process_message(line)
                # Send the response back to the frontend
                self.send_response(response)
            
    def process_message(self, data):
        # Add your custom logic here based on the received message
   
        payload_type, payload = data.split(":")
        
        return self.get_response(payload_type, payload)

    def send_response(self, response):
        # Send the response back to the frontend
        
        print(response, flush=True)
        sys.stdout.flush()
        sys.stderr.flush()

        
    def get_response(self, payload_type, payload):
        #map message type and payload to a response for return value
        #start with exhaustive switching
        if payload_type == 'request':
            if payload == 'pid':
                return self.message.pid(os.getpid())
            

def main():
    mod_unpack_path, merged_unpack_path, use_meld, meld_config_path, copy_to, mod_pak = initialize_workspace()

    # Create the system tray icon
    tray = threading.Thread(target=tray_thread)
    tray.daemon = True  # Allow the program to exit even if the thread is running
    tray.start()

    meld_handler = MeldHandler(mod_unpack_path, merged_unpack_path, use_meld, meld_config_path) #abs path, abs path, bool, config path
    meld_handler.handle()
    meld_pid = int(meld_handler.meld_process.pid)
    listener.send_response(listener.message.edior_pid(meld_pid))

    observer_handler = ObserverHandler(mod_unpack_path, mod_pak, copy_to)
    observer_handler.start()
    
    try:
        while meld_handler.poll() is None:
            time.sleep(1)
    finally:
        observer_handler.stop()

    # print('Meld process has exited. Exiting script...')


if __name__ == '__main__':
    listener = CommsManager()
    listener.listen()
    # Run the main program
    main()
