import os

def generate_steam_paths():
    drive_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    steam_installation_path = "Program Files (x86)\\Steam"  # Default Steam installation path on 64-bit Windows

    steam_paths = []

    for drive_letter in drive_letters:
        path = f"{drive_letter}:\\{steam_installation_path}"
        steam_paths.append(path)

        for custom_path in ["Steam", "Games\\Steam", "SteamLibrary"]:
            path = f"{drive_letter}:\\{custom_path}"
            steam_paths.append(path)

    return steam_paths


def guess_workspace_path():
    steam_paths = generate_steam_paths()

    for path in steam_paths:
        workspace_guess = os.path.join(path, 'steamapps', 'common', 'Dying Light 2', 'ph', 'source')
        
        if os.path.exists(workspace_guess):
            return workspace_guess
    else:
        return None

# print(guess_workspace_path())
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
print(config['Workspace']['target'])
if config['Workspace']['target'] == None:
    config['Workspace']['target'] = guess_workspace_path()