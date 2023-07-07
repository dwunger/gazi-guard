import zipfile
import os
import sys 
import subprocess
import filecmp
import shutil

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
    dir_files = set(os.listdir(dir_path))
    zip_files = set(zip_file.namelist())

    return dir_files == zip_files
def directory_matches_zip(dir_path, zip_file):
    """
    Check if a directory has the same files as a ZipFile.
    """
    # Get a list of all files in dir_path
    dir_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dir_path) for f in filenames]
    dir_files = [file.replace(dir_path + '/', '') for file in dir_files]  # Make paths relative to dir_path

    # Get a list of all files in zip_file
    zip_files = [name for name in zip_file.namelist() if not name.endswith('/')]  # Remove directories

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
    
def extract_source_scripts(source_archive, mod_file_names, destination):
    '''args: source archive path, list of candidate files to extract, extract to path'''
    #pass source_pak_0 and source_pak_1
    with zipfile.ZipFile(source_archive, 'r') as zip_ref:
        table = set(zip_ref.namelist())
        for file in mod_file_names:
            if file in table:
                zip_ref.extract(file, path=destination)

def get_mod_files(mod_pak):
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
        return mod_zip.namelist()

def verify_source_paks_exist(source_pak_0, source_pak_1, error_message):
    if not os.path.exists(source_pak_0) or not os.path.exists(source_pak_1):
        raise FileNotFoundError(error_message)

def file_basename(filename):
    return filename.rsplit('.')[0]

def main():
    # Define the paths to source .pak files
    source_pak_0 = 'data0.pak'
    source_pak_1 = 'data1.pak'
    mod_pak = choose_mod_pak('mod.pak')

    mod_unpack_path = f"{file_basename(mod_pak)}_mod_scripts"
    merged_unpack_path = f'{file_basename(mod_pak)}_source_scripts'

    # Check source pak files
    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                        " Try running from ./steamapps/common/Dying Light 2/ph/source/"
      
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              
    
    # Open the mod.pak file and get the list of file names
    mod_file_names = get_mod_files(mod_pak)

    # Unzip relevant scripts from source_pak_0 and source_pak_1 to ./{data_n}_source_scripts/                
    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)

    # Open mod.pak without unzipping
    # Inside the main function...
    # Open mod.pak without unzipping
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
        # If the target directory exists and matches the contents of the .pak file,
        # then there's no need to unzip again
        if os.path.exists(mod_unpack_path) and directory_matches_zip(mod_unpack_path, mod_zip):
            print("The mod scripts are already extracted and up-to-date.")
            identical_check = input("Do you want to check for identical content? (y/n) ")
            if identical_check.lower() == "y":
                # Here you can add the logic to compare the content of the files in the directory and the .pak
            else:
                mod_zip.extractall('temp')
                if
        else:
            # Prompt to overwrite or increment path
            overwrite = input(f"{mod_unpack_path} already exists. Overwrite? (y/n) ")
            if overwrite.lower() != "y":
                print("Exiting without overwriting.")
                return
            if os.path.exists(mod_unpack_path):
                shutil.rmtree(mod_unpack_path)  # Remove existing directory
            # Unzip mod.pak to mod_unpack_path
            mod_zip.extractall(mod_unpack_path)

    print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → ./{mod_unpack_path}\nUnpacked source scripts → ./{merged_unpack_path}\n")

    try:
        # Start 2-way comparison with Meld using subprocess.Popen
        subprocess.Popen(['meld', mod_unpack_path, merged_unpack_path])
        print("Launching Meld for review...")
    except FileNotFoundError:
        print('\nMeld does not appear in PATH. Please install from https://meld.app/ or get the source code "\
            "\nfrom https://gitlab.gnome.org/GNOME/meld and add to user/system PATH to initiate comparison directly.\n')

if __name__ == '__main__':
    main()
