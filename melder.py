import tkinter as tk
from tkinter import messagebox
import os, time, subprocess, shutil

from utils import resource_path

def add_config_notes():
    note = '''\n\n; NOTES
; Overwrite: 
; Context - Tool does not manage cache states between sessions.
; Situation - If changes are made to unpacked files while tool is closed, how should these changes be handled 
; next time this tool runs:
;
;   - true:  mod_pak (dataX.pak) is the master copy of the mod. Untracked changes to the 
;            unpacked mod directory will be overwritten.
;   - false: The unpacked mod is the master copy. Untracked changes to mod_pak (dataX.pak) 
;            will be overwritten
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

def prompt_enter_config():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion("Please save any changes", "Editor will be closed. Continue to settings?", type = messagebox.YESNO)
    
    if response == 'yes':
        return True
    else:
        return False
    
def prompt_delete_backups(message):
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion("Unexpected Backups Found", message, type = messagebox.YESNO)
    
    return response

def prompt_to_restart():
    root = tk.Tk()
    root.withdraw()
    
    # Set the prompt dialog on top
    root.attributes('-topmost', True)
    
    response = messagebox.askokcancel("Restarting Background Process and Meld", 'Please save any changes before pressing continue')
    
    # Restore the normal behavior after the dialog is closed
    root.attributes('-topmost', False)
    
    return response

def launch_meld(meld_path,mod_unpack_path,merged_unpack_path):
    meld_command = meld_path if meld_path else 'meld'
    return subprocess.Popen([meld_command, mod_unpack_path, merged_unpack_path])


def get_meld_path(meld_config_path=None):
    if meld_config_path:
        return meld_config_path
    program_files = os.environ.get('PROGRAMFILES')
    program_files_x86 = os.environ.get('PROGRAMFILES(X86)')
    possible_paths = [
        shutil.which('meld'),
        os.path.join(program_files, 'Meld/Meld.exe') if program_files else None,
        os.path.join(program_files_x86, 'Meld/Meld.exe') if program_files_x86 else None
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            # set_meld_path(path)
            return path
            
    return None
def wait_for_meld_installation():
    # meld_path = "C:/Program Files/Meld/Meld.exe"
    # meld_installed = os.path.exists(meld_path)
    meld_path = None
    while not meld_path:
        meld_path = get_meld_path()
        time.sleep(0.5)  # Wait for 1 second before checking again
    return meld_path

class MeldHandler:
    def __init__(self, mod_unpack_path, merged_unpack_path, use_meld, meld_config_path=None):
        self.mod_unpack_path = mod_unpack_path
        self.merged_unpack_path = merged_unpack_path
        self.use_meld = use_meld
        self.meld_config_path = meld_config_path
        self.meld_process = None

    def handle(self):
        if self.use_meld: 
            if self.meld_config_path is None:
                self.meld_config_path = get_meld_path(meld_config_path=None)

            if not self.meld_config_path:
                prompt_install_meld()
                wait_for_meld_installation()
            try:
                self.meld_process = launch_meld(self.meld_config_path, self.mod_unpack_path, self.merged_unpack_path)
                # print("Launching Meld for review...")
            except FileNotFoundError:
                print('\nMeld does not appear in PATH or specified path is incorrect. Please install from \
                    https://meldmerge.org/ or specify the correct path in the config.ini file.')
                self.meld_config_path = wait_for_meld_installation()
                self.meld_process = launch_meld(self.meld_config_path, self.mod_unpack_path, self.merged_unpack_path)

    def poll(self):
        return self.meld_process.poll() if self.meld_process else None
