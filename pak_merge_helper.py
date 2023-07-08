import zipfile
import os
import sys 
import subprocess
import filecmp
import shutil
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import stat


def progressbar(it, prefix="", size=60, out=sys.stdout):
    #left for reference, but no longer needed
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)
    
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

def update_archive(source_path, target_path):
    with zipfile.ZipFile(target_path, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(source_path):
            for filename in filenames:
                # Create complete filepath of file in directory


                filePath = os.path.join(foldername, filename)         
                # Add file to zip
                zipf.write(filePath, os.path.relpath(filePath, source_path))
                
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    deep_scan = config.getboolean('Scan', 'deep_scan')
    source_pak_0 = config.get('Paths', 'source_pak_0')
    source_pak_1 = config.get('Paths', 'source_pak_1')
    mod_pak = config.get('Paths', 'mod_pak')
    overwrite_default = config.getboolean('Misc', 'overwrite_default')
    hide_unpacked_content = config.getboolean('Misc', 'hide_unpacked_content')
    meld_path = config.get('Meld', 'path', fallback=None)

    return deep_scan, source_pak_0, source_pak_1, mod_pak, overwrite_default, hide_unpacked_content, meld_path

def set_folder_hidden(folder_path):
    if os.name == 'nt':
        try:
            # For Windows
            import win32api, win32con
            FILE_ATTRIBUTE_HIDDEN = 0x02
            win32api.SetFileAttributes(folder_path, FILE_ATTRIBUTE_HIDDEN)
            print(f"The folder '{folder_path}' is now hidden.")
        except ImportError:
            print("win32api and win32con modules are required on Windows.")

    else:
        try:
            # For Linux/Mac
            os.chflags(folder_path, os.stat(folder_path).st_flags | stat.UF_HIDDEN)
            print(f"The folder '{folder_path}' is now hidden.")
        except AttributeError:
            print("os.chflags is not supported on this platform.")
        except OSError as e:
            print(f"Error occurred: {e}")

def remove_hidden_attribute(folder_path):
    if os.name == 'nt':
        try:
            # For Windows
            import win32api, win32con
            FILE_ATTRIBUTE_HIDDEN = 0x02
            win32api.SetFileAttributes(folder_path, win32con.FILE_ATTRIBUTE_NORMAL)
            print(f"The hidden attribute has been removed from the folder '{folder_path}'.")
        except ImportError:
            print("win32api and win32con modules are required on Windows.")

    else:
        try:
            # For Linux/Mac
            flags = os.stat(folder_path).st_flags
            if flags & stat.UF_HIDDEN:
                flags &= ~stat.UF_HIDDEN
                os.chflags(folder_path, flags)
                print(f"The hidden attribute has been removed from the folder '{folder_path}'.")
            else:
                print(f"The folder '{folder_path}' is not hidden.")
        except AttributeError:
            print("os.chflags is not supported on this platform.")
        except OSError as e:
            print(f"Error occurred: {e}")

def are_dirs_identical(dir1, dir2):
    # Compare files in the directories
    comparison = filecmp.dircmp(dir1, dir2)
    # Directories are not the same if there are any files that differ
    if comparison.diff_files or comparison.left_only or comparison.right_only:
        return False
    # Recurse into subdirectories
    for subdir in comparison.common_dirs:
        if not are_dirs_identical(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
    # No differences found
    return True

def directory_matches_zip(dir_path, zip_file):
    """
    Check if a directory has the same files as a ZipFile.
    """
    log = False
    # Get a list of all files in dir_path
    dir_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dir_path) for f in filenames]
    dir_files = [file.replace(dir_path + os.sep, '').replace(os.sep, '/') for file in dir_files]  # Make paths relative to dir_path and use forward slash

    zip_files = [name for name in zip_file.namelist() if not name.endswith('/')]  # Remove directories
    if log:
        for i in range(min(len(dir_files), len(zip_files))):
            print(dir_files[i], '|', zip_files[i])
    
    return set(dir_files) == set(zip_files)

def increment_path(base_path):
    if base_path not in os.listdir():
        return base_path + '/'
    count = 1
    while True:
        incremented_path = base_path + str(count)
        if incremented_path not in os.listdir():
            return incremented_path + '/'  
        count += 1
def choose_mod_pak(mod_pak):
    if not os.path.exists(mod_pak):
        dir_list = [f for f in os.listdir() if f.endswith('.pak')]
        for idx, file in enumerate(dir_list):
            print(f'{idx} : {file}')
        mod_idx = input("Enter mod archive index: ")
        mod_pak = dir_list[int(mod_idx)]    
        return mod_pak
    else:
        return mod_pak
        

def extract_source_scripts(source_archive, mod_file_names, destination):
    '''args: source archive path, list of candidate files to extract, extract to path'''
    #pass source_pak_0 and source_pak_1
    with zipfile.ZipFile(source_archive, 'r') as zip_ref:
        table = set(zip_ref.namelist())
        for file in mod_file_names:
            if file in table:
                zip_ref.extract(file, path=destination)

def prompt_to_overwrite(mod_pak, mod_unpack_path, deep_scan_enabled, overwrite_default):
    #TODO: Clean this up
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
        if os.path.exists(mod_unpack_path) and directory_matches_zip(mod_unpack_path, mod_zip):
            print("The mod scripts are already extracted.")
            if deep_scan_enabled == True:
                mod_zip.extractall('temp')
                if are_dirs_identical('temp', mod_unpack_path):
                    print('Changes were detected!')
                    if overwrite_default != True:
                        print("Exiting without overwriting.")
                        return
                    if os.path.exists(mod_unpack_path):
                        shutil.rmtree(mod_unpack_path)
                    mod_zip.extractall(mod_unpack_path)
        else:
            overwrite = 'y'
            if os.path.exists(mod_unpack_path):
                overwrite = input(f"{mod_unpack_path} already exists. Overwrite? (y/n) ")
            if overwrite.lower() != "y":
                print("Exiting without overwriting.")
                return
            if os.path.exists(mod_unpack_path):
                shutil.rmtree(mod_unpack_path)
            mod_zip.extractall(mod_unpack_path)

def get_mod_files(mod_pak):
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
        return mod_zip.namelist()

def verify_source_paks_exist(source_pak_0, source_pak_1, error_message):
    if not os.path.exists(source_pak_0) or not os.path.exists(source_pak_1):
        raise FileNotFoundError(error_message)

def file_basename(filename):
    return filename.rsplit('.')[0]

def main():
    deep_scan_enabled, source_pak_0, source_pak_1, mod_path, overwrite_default, hide_unpacked_content, meld_path = read_config()

    # Define the paths to source .pak files
    source_pak_0 = 'data0.pak'
    source_pak_1 = 'data1.pak'
    mod_pak = choose_mod_pak(mod_path)

    mod_unpack_path = f"Unpacked\\{file_basename(mod_pak)}_mod_scripts"
    merged_unpack_path = f'Unpacked\\{file_basename(mod_pak)}_source_scripts'

    # Check source pak files
    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                        " Try running from ./steamapps/common/Dying Light 2/ph/source/"
      
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              
    
    # Open the mod.pak file and get the list of file names
    mod_file_names = get_mod_files(mod_pak)

    # Unzip relevant scripts from source_pak_0 and source_pak_1 to ./{data_n}_source_scripts/                
    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)

    prompt_to_overwrite(mod_pak, mod_unpack_path, deep_scan_enabled, overwrite_default)
    
    if hide_unpacked_content:
        set_folder_hidden('Unpacked')
        set_folder_hidden(merged_unpack_path)            
        set_folder_hidden(mod_unpack_path)
    else:
        remove_hidden_attribute('Unpacked')
        remove_hidden_attribute(merged_unpack_path)
        remove_hidden_attribute(mod_unpack_path)
    print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → ./{mod_unpack_path}\nUnpacked source scripts → ./{merged_unpack_path}\n")
    
    # Instantiate event handler and observer
    file_observer = Observer()
    event_handler = FileChangeHandler(mod_unpack_path=mod_unpack_path, mod_pak=mod_pak)

    try:
        meld_command = meld_path if meld_path else 'meld'
        meld_process = subprocess.Popen([meld_command, mod_unpack_path, merged_unpack_path])
        print("Launching Meld for review...")
    except FileNotFoundError:
        print('\nMeld does not appear in PATH or specified path is incorrect. Please install from https://meldmerge.org/ or specify the correct path in the config.ini file.')
    print("Success!")

        # Set the observer to monitor the directory for changes
    file_observer.schedule(event_handler, path=mod_unpack_path, recursive=True)
    file_observer.start()

    try:
        while meld_process.poll() is None:
            # Sleep while waiting for the Meld process to finish
            time.sleep(1)
    finally:
        file_observer.stop()
        file_observer.join()
    
    #when meld exits, script may exit
    print('Meld process has exited. Exiting script...')


if __name__ == '__main__':
    main()
