import os
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from meld_install import prompt_install_meld, launch_meld, get_meld_path, wait_for_meld_installation
from file_system import *

#TODO:
#! Protect against catastrophic failures
# Implement rolling backups  
# Simple GUI for configuration
# GUI to monitor repack status
# Prune rewrites to update mod archive
#BUG: Unexpected rewrite loop occasionally on startup

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, mod_unpack_path, mod_pak) -> None:
        self.mod_unpack_path = mod_unpack_path
        self.mod_pak = mod_pak
    def on_modified(self, event):
        if not event.is_directory:
            # Check if the modified file is in the mod_unpack_path
            print('Change detected! Do not exit while saving...')
            # print(f'Modified file: {event.src_path}')
            if os.path.commonpath([self.mod_unpack_path]) == self.mod_unpack_path:
                update_archive(self.mod_unpack_path, self.mod_pak)
                print('Saved changes!')

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    deep_scan = config.getboolean('Scan', 'deep_scan')
    source_pak_0 = config.get('Paths', 'source_pak_0')
    source_pak_1 = config.get('Paths', 'source_pak_1')
    mod_pak = config.get('Paths', 'mod_pak')
    overwrite_default = config.getboolean('Misc', 'overwrite_default')
    hide_unpacked_content = config.getboolean('Misc', 'hide_unpacked_content')
    meld_config_path = config.get('Meld', 'path', fallback=None)
    use_meld = config.getboolean('Meld', 'use_meld')
    return deep_scan, source_pak_0, source_pak_1, mod_pak, overwrite_default, hide_unpacked_content, meld_config_path, use_meld
    
class MeldHandler:
    def __init__(self, mod_unpack_path, merged_unpack_path, use_meld, meld_config_path=None):
        self.mod_unpack_path = mod_unpack_path
        self.merged_unpack_path = merged_unpack_path
        self.use_meld = use_meld
        self.meld_config_path = meld_config_path
        self.meld_process = None

    def handle(self):
        if self.use_meld: 
            meld_path = get_meld_path(meld_config_path=self.meld_config_path)
            if not meld_path:
                prompt_install_meld()
                wait_for_meld_installation()
            try:
                self.meld_process = launch_meld(meld_path, self.mod_unpack_path, self.merged_unpack_path)
                print("Launching Meld for review...")
            except FileNotFoundError:
                print('\nMeld does not appear in PATH or specified path is incorrect. Please install from \
                    https://meldmerge.org/ or specify the correct path in the config.ini file.')
                meld_path = wait_for_meld_installation()
                self.meld_process = launch_meld(meld_path, self.mod_unpack_path, self.merged_unpack_path)

    def poll(self):
        return self.meld_process.poll() if self.meld_process else None

class ObserverHandler:
    def __init__(self, mod_unpack_path, mod_pak):
        self.mod_unpack_path = mod_unpack_path
        self.mod_pak = mod_pak
        self.file_observer = Observer()
        self.event_handler = FileChangeHandler(mod_unpack_path=self.mod_unpack_path, mod_pak=self.mod_pak)

    def start(self):
        self.file_observer.schedule(self.event_handler, path=self.mod_unpack_path, recursive=True)
        self.file_observer.start()

    def stop(self):
        self.file_observer.stop()
        self.file_observer.join()

def main():
    deep_scan_enabled, source_pak_0, source_pak_1, mod_path, overwrite_default, \
        hide_unpacked_content, meld_config_path, use_meld = read_config()

    mod_pak = choose_mod_pak(mod_path)
    
    mod_unpack_path = f"Unpacked\\{file_basename(mod_pak)}_mod_scripts"
    merged_unpack_path = f'Unpacked\\{file_basename(mod_pak)}_source_scripts'

    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                         " Try running from ./steamapps/common/Dying Light 2/ph/source/"
      
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              
    
    mod_file_names = get_mod_files(mod_pak)

    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)

    prompt_to_overwrite(mod_pak, mod_unpack_path, deep_scan_enabled, overwrite_default)
    
    if hide_unpacked_content:
        set_folders_hidden(['Unpacked', merged_unpack_path, mod_unpack_path])
    else:
        remove_hidden_attributes(['Unpacked', merged_unpack_path, mod_unpack_path])

    print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → ./{mod_unpack_path}\nUnpacked source scripts → ./{merged_unpack_path}\n")
    
    meld_handler = MeldHandler(mod_unpack_path, merged_unpack_path, use_meld, meld_config_path)
    meld_handler.handle()

    observer_handler = ObserverHandler(mod_unpack_path, mod_pak)
    observer_handler.start()

    try:
        while meld_handler.poll() is None:
            time.sleep(1)
    finally:
        observer_handler.stop()

    print('Meld process has exited. Exiting script...')


if __name__ == '__main__':
    main()

