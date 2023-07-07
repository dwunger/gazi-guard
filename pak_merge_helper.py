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
    
def progressbar(it, prefix="", size=60, out=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)
    
# Define the paths to your source .pak files
source_pak_0 = 'data0.pak'
source_pak_1 = 'data1.pak'

# Define the path to your mod .pak file
mod_pak = 'mod.pak' # previously data4.pak
mod_unpack_path = increment_path("mod_scripts")
# Define the path for the new pak file that contains merged content
merged_unpack_path = increment_path('source_scripts')
merged_pak = merged_unpack_path[0:-1] + '.pak' # -> source_scripts.pak

# Define the list of files in mod.pak
mod_files = []
if not os.path.exists(source_pak_0) or not os.path.exists(source_pak_1):
    raise FileNotFoundError("\n\nOne or both source pak files are missing (data0.pak and/or data1.pak). Try running from ./steamapps/common/Dying Light 2/ph/source/")
                            
if not os.path.exists(mod_pak):
    for idx, file in enumerate(os.listdir()):
        print(f'{idx} : {file}')
    mod_idx = input("Enter mod archive index: ")
    mod_pak = os.listdir()[int(mod_idx)]

# Open the mod.pak file and get the list of file names
with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
    mod_files = mod_zip.namelist()

# Open the source_pak_1 file and merged_source.pak file
with zipfile.ZipFile(source_pak_1, 'r') as source_1_zip:
    with zipfile.ZipFile(merged_pak, 'w') as merged_zip:
        for file in progressbar(mod_files, prefix="Generating source template: "):
            # Check if file exists in source_pak_1
            if file in source_1_zip.namelist():
                # If it does, copy the file from source_pak_1 to merged_source.pak
                with source_1_zip.open(file) as source_file:
                    with merged_zip.open(file, 'w') as dest_file:
                        dest_file.write(source_file.read())
            else:
                # If not found in source_pak_1, fall back to source_pak_0
                with zipfile.ZipFile(source_pak_0, 'r') as source_0_zip:
                    if file in source_0_zip.namelist():
                        with source_0_zip.open(file) as source_file:
                            with merged_zip.open(file, 'w') as dest_file:
                                dest_file.write(source_file.read())

# Unzip merged_source.pak to source_scripts folder
with zipfile.ZipFile(merged_pak, 'r') as merged_zip:
    merged_zip.extractall(merged_unpack_path)

# Unzip mod.pak to mod_scripts/
with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
    mod_zip.extractall(mod_unpack_path)

os.remove(merged_pak)

print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → ./{mod_unpack_path}\nUnpacked source scripts → ./{merged_unpack_path}\n")

try:
    # Start 2-way comparison with Meld using subprocess.Popen
    subprocess.Popen(['meld', mod_unpack_path, merged_unpack_path])
    print("Launching Meld for review...")
except FileNotFoundError:
    print('\nMeld does not appear in PATH. Please install from https://meld.app/ or get the source code \nfrom https://gitlab.gnome.org/GNOME/meld and add to user/system PATH to initiate comparison directly.\n')
