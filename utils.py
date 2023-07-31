import sys 
import os

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
def guess_mod_pack_path(target_workspace):
    for i in range(2,16):
        filename = f'data{i}.pak'
        guess = os.path.join(target_workspace, filename)
        if os.path.exists(guess):
            return guess
    else:
        return None
        
def contains(file_path, search_string):
    """
    Search for a matching string in a text document.

    This function opens the specified text file, reads it line by line, and checks
    if the given search string is present in any of the lines.

    Parameters:
        file_path (str): The path to the text document to search in.
        search_string (str): The string to search for in the text document.

    Returns:
        bool: True if the search string is found in the document, False otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if search_string in line:
                    return True
        return False
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False

def guess_workspace_path():
    steam_paths = generate_steam_paths()

    for path in steam_paths:
        workspace_guess = os.path.join(path, 'steamapps', 'common', 'Dying Light 2', 'ph', 'source')
        
        if os.path.exists(workspace_guess):
            return workspace_guess
    else:
        return None


# def resource_path(relative_path):
#     """standardize relative references"""
    
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)


def resource_path(relative_path):
    """standardize relative references"""
    
    # List of file names to be redirected to AppData
    redirect_files = ['config.ini', 'mylog.log']

    # Check if the relative_path is in the list
    if os.path.basename(relative_path) in redirect_files:
        # Redirect to the AppData folder
        appdata_path = os.getenv('APPDATA')
        new_path = os.path.join(appdata_path, 'GaziGuard', relative_path)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        return new_path

    # If the path is not in the list, fall back to the old behavior
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def get_int_date():
    import datetime
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")
run_number = get_int_date()
