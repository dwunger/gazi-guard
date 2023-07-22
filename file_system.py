import filecmp
import shutil
import zipfile
import stat
import os
import py7zr
import zipfile
import tempfile
import shutil
import ctypes
import time
from utils import guess_mod_pack_path
def bring_window_to_front_by_pid(pid):
    try:
        # Find the window handle using the process ID
        hwnd = ctypes.windll.user32.FindWindowW(None, None)  # You can provide a window title or class name if available

        # Bring the window to the front
        if hwnd:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Failed to bring window to front: {e}")

def update_archive(source_path, target_path, delay = 0.1):
    #race condition with Meld. There's probably a better way to deal with this
    #tried a spinlock type approach, but this raises an error on Meld's end
    time.sleep(delay)
    with zipfile.ZipFile(target_path, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(source_path):
            for filename in filenames:
                # Create complete filepath of file in directory
                filePath = os.path.join(foldername, filename)
                try:        
                    # Add file to zip
                    zipf.write(filePath, os.path.relpath(filePath, source_path))
                except FileNotFoundError:
                    print(f"Warning: File {filePath} was not found.")
                    continue

def set_folder_hidden(folder_path):
    if os.name == 'nt':
        try:
            # For Windows
            import win32api, win32con
            FILE_ATTRIBUTE_HIDDEN = 0x02
            win32api.SetFileAttributes(folder_path, FILE_ATTRIBUTE_HIDDEN)
            #print(f"The folder '{folder_path}' is now hidden.")
        except ImportError:
            #print("win32api and win32con modules are required on Windows.")
            pass
    else:
        try:
            # For Linux/Mac
            os.chflags(folder_path, os.stat(folder_path).st_flags | stat.UF_HIDDEN)
            #print(f"The folder '{folder_path}' is now hidden.")
        except AttributeError:
            #print("os.chflags is not supported on this platform.")
            pass
        except OSError as e:
            #print(f"Error occurred: {e}")
            pass

def set_folders_hidden(paths):
    for path in paths:
        set_folder_hidden(path)

def remove_hidden_attribute(folder_path):
    if os.name == 'nt':
        try:
            # For Windows
            import win32api, win32con
            FILE_ATTRIBUTE_HIDDEN = 0x02
            win32api.SetFileAttributes(folder_path, win32con.FILE_ATTRIBUTE_NORMAL)
            #print(f"The hidden attribute has been removed from the folder '{folder_path}'.")
        except ImportError:
            #print("win32api and win32con modules are required on Windows.")
            pass
    else:
        try:
            # For Linux/Mac
            flags = os.stat(folder_path).st_flags
            if flags & stat.UF_HIDDEN:
                flags &= ~stat.UF_HIDDEN
                os.chflags(folder_path, flags)
                #print(f"The hidden attribute has been removed from the folder '{folder_path}'.")
            else:
                #print(f"The folder '{folder_path}' is not hidden.")
                pass
        except AttributeError:
            #print("os.chflags is not supported on this platform.")
            pass
        except OSError as e:
            #print(f"Error occurred: {e}")
            pass

def remove_hidden_attributes(paths):
    for path in paths:
        remove_hidden_attribute(path)

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

def prompt_to_overwrite(mod_pak, mod_unpack_path, deep_scan_enabled, overwrite_default):
    #TODO: Clean this up
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
        if os.path.exists(mod_unpack_path) and directory_matches_zip(mod_unpack_path, mod_zip):
            #print("The mod scripts are already extracted.")
            if deep_scan_enabled == True:
                mod_zip.extractall('temp')
                if are_dirs_identical('temp', mod_unpack_path):
                    #print('Changes were detected!')
                    if overwrite_default != True:
                        #print("Exiting without overwriting.")
                        return
                    if os.path.exists(mod_unpack_path):
                        shutil.rmtree(mod_unpack_path)
                    mod_zip.extractall(mod_unpack_path)
        else:
            # overwrite = 'y'
            # if os.path.exists(mod_unpack_path):
            #     overwrite = input(f"{mod_unpack_path} already exists. Overwrite? (y/n) ")
            if overwrite_default == False:
                #print("Exiting without overwriting.")
                return
            if os.path.exists(mod_unpack_path):
                shutil.rmtree(mod_unpack_path)
            mod_zip.extractall(mod_unpack_path)

# def get_mod_files(mod_pak):
#     with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
#         return mod_zip.namelist()

def get_mod_files(mod_pak):
    try:
        with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
            return mod_zip.namelist()
    except zipfile.BadZipFile:
        # Fallback method for LZMA2
        with tempfile.TemporaryDirectory() as temp_dir:
            with py7zr.SevenZipFile(mod_pak, mode='r') as z:
                z.extractall(path=temp_dir)
            temp_zip_path = os.path.join(temp_dir, "temp.zip")
            with zipfile.ZipFile(temp_zip_path, 'w') as zipf:
                for foldername, subfolders, filenames in os.walk(temp_dir):
                    for filename in filenames:
                        zipf.write(os.path.join(foldername, filename),
                                   os.path.relpath(os.path.join(foldername, filename), temp_dir),
                                   compress_type=zipfile.ZIP_DEFLATED)
            # Replace original .pak file with new Zip file
            os.remove(mod_pak)
            shutil.move(temp_zip_path, mod_pak)
            with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
                return mod_zip.namelist()



# import tarfile

# def get_mod_files(mod_pak):
#     with tarfile.open(mod_pak, 'r:gz') as mod_tar:
#         return mod_tar.getnames()

def verify_source_paks_exist(source_pak_0, source_pak_1, error_message):
    if not os.path.exists(source_pak_0) or not os.path.exists(source_pak_1):
        raise FileNotFoundError(error_message)

def file_basename(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

def increment_path(base_path):
    if base_path not in os.listdir():
        return base_path + '/'
    count = 1
    while True:
        incremented_path = base_path + str(count)
        if incremented_path not in os.listdir():
            return incremented_path + '/'  
        count += 1

def choose_mod_pak(mod_pak, target_workspace):

    #print (mod_pak)
    if not os.path.exists(mod_pak):
        #TODO: create a prompt to select and find a good spot to synchronize a pause on front- and backend
        mod_pak = guess_mod_pack_path(target_workspace)
        
        # dir_list = [f for f in os.listdir(target_workspace) if f.endswith('.pak')]
        # # for idx, file in enumerate(dir_list):
        # #     #print(f'{idx} : {file}')
        #     # pass
        # mod_idx = input("Enter mod archive index: ")
        # mod_pak = dir_list[int(mod_idx)]
        # mod_pak = os.path.join(target_workspace, mod_pak) 
        return mod_pak
    else:
        return None
    
def extract_source_scripts(source_archive, mod_file_names, destination):
    '''args: source archive path, list of candidate files to extract, extract to path'''
    #pass source_pak_0 and source_pak_1
    with zipfile.ZipFile(source_archive, 'r') as zip_ref:
        table = set(zip_ref.namelist())
        #print(zip_ref.namelist()[0:10])
        #print(mod_file_names[0:10])
        for file in mod_file_names:
            if file in table:
                zip_ref.extract(file, path=destination)
            
def set_folder_attribute(hide_unpacked_content, target_workspace, merged_unpack_path, mod_unpack_path):
    if hide_unpacked_content:
        try:
            set_folders_hidden([os.path.join(target_workspace, 'Unpacked'), merged_unpack_path, mod_unpack_path])
        except Exception as e:
            print('An error occurred while setting folders hidden:', str(e))
    else:
        try:
            remove_hidden_attributes([os.path.join(target_workspace, 'Unpacked'), merged_unpack_path, mod_unpack_path])
        except Exception as e:
            print('An error occurred while removing hidden attributes:', str(e))