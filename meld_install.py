import tkinter as tk
from tkinter import messagebox
import os, time, subprocess, shutil
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
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('Meld', 'path', where_meld)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)
    if where_meld:
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