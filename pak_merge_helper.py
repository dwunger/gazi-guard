import zipfile
import os
import sys 
import subprocess

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

def main():
    # Define the paths to source .pak files
    source_pak_0 = 'data0.pak'
    source_pak_1 = 'data1.pak'
    mod_pak = choose_mod_pak('mod.pak')
    
    mod_unpack_path = increment_path(f"{mod_pak}_mod_scripts")
    merged_unpack_path = increment_path(f'{mod_pak}_source_scripts')

    file_missing_error = "\nOne or both source pak files are missing (data0.pak and/or data1.pak)." \
                        " Try running from ./steamapps/common/Dying Light 2/ph/source/"
      
    verify_source_paks_exist(source_pak_0, source_pak_1, file_missing_error)              
    
    # Open the mod.pak file and get the list of file names
    mod_file_names = get_mod_files(mod_pak)

    # Unzip relevant scripts from source_pak_0 and source_pak_1 to ./source_scripts/                
    extract_source_scripts(source_pak_0, mod_file_names, merged_unpack_path)
    extract_source_scripts(source_pak_1, mod_file_names, merged_unpack_path)

    # Unzip mod.pak to mod_scripts/
    with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
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
