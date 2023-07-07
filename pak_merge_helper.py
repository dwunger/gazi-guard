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

# Unzip relevant scripts from source_pak_0 and source_pak_1 to ./source_scripts/
with zipfile.ZipFile(source_pak_0, 'r') as zip_ref:
    table = set(zip_ref.namelist())
    for file in mod_files:
        if file in table:
            zip_ref.extract(file, path=merged_unpack_path)

with zipfile.ZipFile(source_pak_1, 'r') as zip_ref:
    table = set(zip_ref.namelist())
    for file in mod_files:
        if file in table:
            zip_ref.extract(file, path=merged_unpack_path)

# Unzip mod.pak to mod_scripts/
with zipfile.ZipFile(mod_pak, 'r') as mod_zip:
    mod_zip.extractall(mod_unpack_path)

print(f"\n\nComparison complete! \n\nSee for output:\nUnpacked mod scripts → ./{mod_unpack_path}\nUnpacked source scripts → ./{merged_unpack_path}\n")

try:
    # Start 2-way comparison with Meld using subprocess.Popen
    subprocess.Popen(['meld', mod_unpack_path, merged_unpack_path])
    print("Launching Meld for review...")
except FileNotFoundError:
    print('\nMeld does not appear in PATH. Please install from https://meld.app/ or get the source code \nfrom https://gitlab.gnome.org/GNOME/meld and add to user/system PATH to initiate comparison directly.\n')
