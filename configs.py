import configparser
from utils import resource_path, guess_workspace_path, guess_mod_pack_path
from melder import get_meld_path
import os
#FOR REFERENCE:
# def generate_steam_paths():
#     drive_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     steam_installation_path = "Program Files (x86)\\Steam"  # Default Steam installation path on 64-bit Windows

#     steam_paths = []

#     for drive_letter in drive_letters:
#         path = f"{drive_letter}:\\{steam_installation_path}"
#         steam_paths.append(path)

#         for custom_path in ["Steam", "Games\\Steam", "SteamLibrary"]:
#             path = f"{drive_letter}:\\{custom_path}"
#             steam_paths.append(path)

#     return steam_paths

# def guess_workspace_path():
#     steam_paths = generate_steam_paths()

#     for path in steam_paths:
#         workspace_guess = os.path.join(path, 'steamapps', 'common', 'Dying Light 2', 'ph', 'source')
        
#         if os.path.exists(workspace_guess):
#             return workspace_guess
#     else:
#         return None
    
# def guess_mod_pack_path(target_workspace):
#     for i in range(2,16):
#         filename = f'data{i}.pak'
#         guess = os.path.join(target_workspace, filename)
#         if os.path.exists(guess):
#             return guess
#     else:
#         return None
# def resource_path(relative_path):
#     """standardize relative references"""
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)


# def get_meld_path(meld_config_path=None):
#     if meld_config_path:
#         return meld_config_path    
#     where_meld = shutil.which('meld')
#     if where_meld:
#         config = configparser.ConfigParser()
#         config.read('config.ini')
#         config.set('Meld', 'path', where_meld)
#         with open('config.ini', 'w') as config_file:
#             config.write(config_file)
#         add_config_notes()
#         return where_meld
#     else:
#         return None

# TODO: Write an exception to create default config file ☑ Needs testing
# TODO: Handle config file corruption with rewrite ☑ Needs testing
class Config:
    docs = None
    config_template = '''
    [Scan]
    deep_scan = False

    [Paths]
    source_pak_0 = data0.pak
    source_pak_1 = data1.pak
    mod_pak = 

    [Workspace]
    target = 

    [Meld]
    enable = True
    path = 

    [Backups]
    enable = True
    count = 10

    [Misc]
    overwrite_default = True
    hide_unpacked_content = True
    notifications = False
    always_on_top = True
    # mod_pak = X:\SteamLibrary\steamapps\common\Dying Light 2\ph\source\data3.pak
    # target = X:\SteamLibrary\steamapps\common\Dying Light 2\ph\source
    '''
    def __init__(self):
        self.config_path = resource_path('config.ini')
        self.config_parser = configparser.ConfigParser()

        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        if not self._load_config():
            self._create_default_config()
            self._load_config()  # Reload the default configuration

        if not (self.config_parser.has_section('Workspace') and self.config_parser.has_section('Paths') and self.config_parser.has_section('Meld') and self.config_parser.has_section('Scan') and self.config_parser.has_section('Misc')):
            self._create_default_config()
            self._load_config()  # Reload the default configuration if required sections do not exist

        self.assign_requirements()

        self.properties = [
            'target_workspace', 'deep_scan', 'source_pak_0', 'source_pak_1',
            'mod_pak', 'overwrite_default', 'hide_unpacked_content', 'meld_config_path',
            'use_meld', 'backup_enabled', 'backup_count', 'notifications', 'always_on_top'
        ]

    def _load_config(self):
        try:
            self.config_parser.read(self.config_path)
            return True
        except configparser.Error:
            return False
    def _create_default_config(self):
        with open(self.config_path, 'w') as configfile:
            configfile.write(self.config_template)
            
    def add_config_notes(self):
        with open(self.config_path, 'a') as file:
            if Config.docs:
                file.write(Config.docs)    
    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            self.config_parser.write(config_file)            
    def assign_requirements(self):
        if self.config_parser.get('Workspace', 'target')=='':
            self.target_workspace = guess_workspace_path()
        if self.config_parser.get('Paths', 'mod_pak') == '':
            self.mod_pak = guess_mod_pack_path(self.target_workspace)
            
        if self.meld_config_path == '':
            self.meld_config_path = get_meld_path()
        self.save_config()

    @property
    def target_workspace(self):
        """Folder containing source materials: source_pak_0, source_pak_1, and mod_pak"""
        return resource_path(self.config_parser.get('Workspace', 'target'))

    @target_workspace.setter
    def target_workspace(self, value):
        self.config_parser.set('Workspace', 'target', value)
        self.save_config()


    @property
    def copy_to(self):
        """No official support. Manages copy of repacked mod at path"""
        return self.config_parser.get('Dev', 'copyto', fallback=None)
    
    @copy_to.setter
    def copy_to(self, value):
        self.config_parser.set('Dev', 'copyto', value)
        self.save_config()
    
    @property
    def deep_scan(self):
        """Compares files line-wise for changes"""
        return self.config_parser.getboolean('Scan', 'deep_scan')
    
    @deep_scan.setter
    def deep_scan(self, value):
        self.config_parser.set('Scan', 'deep_scan', str(value))
        self.save_config()
    
    @property
    def source_pak_0(self):
        """Str: Path to data0.pak"""
        return self.config_parser.get('Paths', 'source_pak_0')
    
    @source_pak_0.setter
    def source_pak_0(self, value):
        self.config_parser.set('Paths', 'source_pak_0', value)
        self.save_config()
    
    @property
    def source_pak_1(self):
        """Str: Path to data1.pak"""
        return self.config_parser.get('Paths', 'source_pak_1')
    
    @source_pak_1.setter
    def source_pak_1(self, value):
        self.config_parser.set('Paths', 'source_pak_1', value)
        self.save_config()
    
    @property
    def mod_pak(self):
        """Str: Path to dataX.pak"""
        return self.config_parser.get('Paths', 'mod_pak')
    
    @mod_pak.setter
    def mod_pak(self, value):
        self.config_parser.set('Paths', 'mod_pak', value)
        self.save_config()

    @property
    def overwrite_default(self):
        """Bool: True -> mod_pak overwrites changes to unpacked archive on new load of this tool
                  False -> unpacked archive overwrites changes to mod_pak on new load of this tool"""
        return self.config_parser.getboolean('Misc', 'overwrite_default')
    
    @overwrite_default.setter
    def overwrite_default(self, value):
        self.config_parser.set('Misc', 'overwrite_default', str(value))
        self.save_config()
    
    @property
    def hide_unpacked_content(self):
        """Set OS hidden flag to unpacked directory"""
        return self.config_parser.getboolean('Misc', 'hide_unpacked_content')
    
    @hide_unpacked_content.setter
    def hide_unpacked_content(self, value):
        self.config_parser.set('Misc', 'hide_unpacked_content', str(value))
        self.save_config()
    
    @property
    def meld_config_path(self):
        """Path to Meld as per config.ini. Falls back to None"""
        return self.config_parser.get('Meld', 'path', fallback=None)
    
    @meld_config_path.setter
    def meld_config_path(self, value):
        self.config_parser.set('Meld', 'path', value)
        self.save_config()
    
    @property
    def use_meld(self):
        """Bool: Launch Meld"""
        return self.config_parser.getboolean('Meld', 'enable')
    
    @use_meld.setter
    def use_meld(self, value):
        self.config_parser.set('Meld', 'enable', str(value))
        self.save_config()
    
    @property
    def backup_enabled(self):
        """Bool: Create backup of mod_pak on startup"""
        return self.config_parser.getboolean('Backups', 'enable')
    
    @backup_enabled.setter
    def backup_enabled(self, value):
        self.config_parser.set('Backups', 'enable', str(value))
        self.save_config()
    @property
    def notifications(self):
        """Bool: Create backup of mod_pak on startup"""
        return self.config_parser.getboolean('Misc', 'notifications')
    
    @notifications.setter
    def notifications(self, value):
        self.config_parser.set('Misc', 'notifications', str(value))
        self.save_config()
        
    @property
    def backup_count(self):
        """Int: Number of rolling backups for backup manager to retain"""
        return self.config_parser.getint('Backups', 'count')
    
    @backup_count.setter
    def backup_count(self, value):
        self.config_parser.set('Backups', 'count', str(value))
        self.save_config()
        
    @property
    def always_on_top(self):
        """Bool: Create backup of mod_pak on startup"""
        return self.config_parser.getboolean('Misc', 'always_on_top', fallback=True)
    
    @always_on_top.setter
    def always_on_top(self, value):
        self.config_parser.set('Misc', 'always_on_top', str(value))
        self.save_config()
    def dump_settings(self):
        """
        Dump the settings as a tuple in the following order:
        1. target_workspace: folder containing source materials: source_pak_0, source_pak_1, and mod_pak
        2. copy_to: no official support. Manages copy of repacked mod at path
        3. deep_scan: Compares files line-wise for changes
        4. source_pak_0: Str: path to data0.pak
        5. source_pak_1: Str: path to data1.pak
        6. mod_pak: Str: path to dataX.pak
        7. overwrite_default: Bool: true -> mod_pak overwrites changes to unpacked archive on new load of this tool
                              Bool: false -> unpacked archive overwrites changes to mod_pak on new load of this tool
        8. hide_unpacked_content: set OS hidden flag to unpacked directory
        9. meld_config_path: Path to Meld as per config.ini. Falls back to None
        10. use_meld: Bool: launch meld
        11. backup_enabled: Bool: create backup of mod_pak on startup 
        12. backup_count: Int: number of rolling backups for backup manager to retain
        """
        return (
            self.target_workspace, self.copy_to, self.deep_scan, self.source_pak_0,
            self.source_pak_1, self.mod_pak, self.overwrite_default,
            self.hide_unpacked_content, self.meld_config_path, self.use_meld,
            self.backup_enabled, self.backup_count, self.notifications
        )

# config = Config()
# print("hi mom")
# print(config.properties)

# def read_config():
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     target_workspace = config.get('Workspace', 'target', fallback='')
#     copy_to = config.get('Dev', 'copyto', fallback=None)
#     deep_scan = config.getboolean('Scan', 'deep_scan')
#     source_pak_0 = config.get('Paths', 'source_pak_0')
#     source_pak_1 = config.get('Paths', 'source_pak_1')
#     mod_pak = config.get('Paths', 'mod_pak')
#     overwrite_default = config.getboolean('Misc', 'overwrite_default')
#     hide_unpacked_content = config.getboolean('Misc', 'hide_unpacked_content')
#     meld_config_path = config.get('Meld', 'path', fallback=None)
#     use_meld = config.getboolean('Meld', 'enable')
#     backup_enabled = config.getboolean('Backups', 'enable')
#     backup_count = config.getint('Backups', 'count')
#     return target_workspace, copy_to, deep_scan, source_pak_0, source_pak_1, mod_pak, overwrite_default, hide_unpacked_content, meld_config_path, use_meld, backup_enabled, backup_count



#docs = ''
#     docs = '''\n\n; NOTES
# # Overwrite: 
# # Context - Tool does not manage cache states between sessions.
# # Situation - If changes are made to unpacked files while tool is closed, how should these changes be handled 
# # next time this tool runs:
# #
# #   - true:  mod_pak (dataX.pak) is the master copy of the mod. Untracked changes to the 
# #            unpacked mod directory will be overwritten.
# #   - false: The unpacked mod is the master copy. Untracked changes to mod_pak (dataX.pak) 
# #            will be overwritten
# # Hide: 
# # The tool must unpack archives to work with their contents. Should the unpacked contents be hidden?
# '''    
