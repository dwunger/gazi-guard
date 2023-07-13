import tkinter as tk
from tkinter import messagebox
import os, time, subprocess, shutil
import configparser
def add_config_notes():
    note = '''\n\n; NOTES
; Overwrite: 
; If changes are made to unpacked files using a different editor, how should these changes be handled 
; next time this tool runs:
;
;   - true:  mod_pak (dataX.pak) is the master copy of the mod. Untracked changes to the 
;            unpacked mod directory will be overwritten.
;   - false: The unpacked mod is the master copy. Untracked changes to mod_pak (dataX.pak) 
;            will be overwritte
; Hide: 
; The tool must unpack archives to work with their contents. Should the unpacked contents be hidden?
'''
    with open("config.ini", "a") as config:
        config.write(note)
def prompt_open_with_program(url):
    os.startfile(url)

def prompt_install_meld():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion("Meld Not Installed", "Meld does not appear to be installed. If Meld is \
        installed, please add the installation path to config.ini or add to user PATH. Proceed to download page?")
    
    if response == 'yes':
        url = "https://meldmerge.org/"
        prompt_open_with_program(url)
    
def launch_meld(meld_path,mod_unpack_path,merged_unpack_path):
    meld_command = meld_path if meld_path else 'meld'
    return subprocess.Popen([meld_command, mod_unpack_path, merged_unpack_path])

def get_meld_path(meld_config_path=None):
    if meld_config_path:
        return meld_config_path    
    where_meld = shutil.which('meld')
    if where_meld:
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('Meld', 'path', where_meld)
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
        add_config_notes()
        return where_meld
    else:
        return None
def wait_for_meld_installation():
    # meld_path = "C:/Program Files/Meld/Meld.exe"
    # meld_installed = os.path.exists(meld_path)
    meld_path = None
    while not meld_path:
        meld_path = get_meld_path()
        time.sleep(0.5)  # Wait for 1 second before checking again
    return meld_path