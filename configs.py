import configparser
from utils import resource_path
class Config:
    docs = 'Note'
#     docs = '''\n\n; NOTES
# ; Overwrite: 
# ; Context - Tool does not manage cache states between sessions.
# ; Situation - If changes are made to unpacked files while tool is closed, how should these changes be handled 
# ; next time this tool runs:
# ;
# ;   - true:  mod_pak (dataX.pak) is the master copy of the mod. Untracked changes to the 
# ;            unpacked mod directory will be overwritten.
# ;   - false: The unpacked mod is the master copy. Untracked changes to mod_pak (dataX.pak) 
# ;            will be overwritten
# ; Hide: 
# ; The tool must unpack archives to work with their contents. Should the unpacked contents be hidden?
# '''    
    def __init__(self):
        self.config_path = resource_path('config.ini')
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(self.config_path)
        # self.properties = [attr for attr in vars(self) if isinstance(getattr(self, attr), property)]
        # Couldn't get this to work. Do not use as it may not be up to date:
        self.properties = [
            'target_workspace', 'deep_scan', 'source_pak_0', 'source_pak_1',
            'mod_pak', 'overwrite_default', 'hide_unpacked_content', 'meld_config_path',
            'use_meld', 'backup_enabled', 'backup_count'
        ]

    def add_config_notes(self):
        with open(self.config_path, 'a') as file:
            file.write(Config.docs)    
            
    @property
    def target_workspace(self):
        """Folder containing source materials: source_pak_0, source_pak_1, and mod_pak"""
        return resource_path(self.config_parser.get('Workspace', 'target', fallback=''))
    
    @target_workspace.setter
    def target_workspace(self, value):
        self.config_parser.set('Workspace', 'target', value)
        self.add_config_notes()
    
    @property
    def copy_to(self):
        """No official support. Manages copy of repacked mod at path"""
        return self.config_parser.get('Dev', 'copyto', fallback=None)
    
    @copy_to.setter
    def copy_to(self, value):
        self.config_parser.set('Dev', 'copyto', value)
        self.add_config_notes()
    
    @property
    def deep_scan(self):
        """Compares files line-wise for changes"""
        return self.config_parser.getboolean('Scan', 'deep_scan')
    
    @deep_scan.setter
    def deep_scan(self, value):
        self.config_parser.set('Scan', 'deep_scan', str(value))
        self.add_config_notes()
    
    @property
    def source_pak_0(self):
        """Str: Path to data0.pak"""
        return self.config_parser.get('Paths', 'source_pak_0')
    
    @source_pak_0.setter
    def source_pak_0(self, value):
        self.config_parser.set('Paths', 'source_pak_0', value)
        self.add_config_notes()
    
    @property
    def source_pak_1(self):
        """Str: Path to data1.pak"""
        return self.config_parser.get('Paths', 'source_pak_1')
    
    @source_pak_1.setter
    def source_pak_1(self, value):
        self.config_parser.set('Paths', 'source_pak_1', value)
        self.add_config_notes()
    
    @property
    def mod_pak(self):
        """Str: Path to dataX.pak"""
        return self.config_parser.get('Paths', 'mod_pak')
    
    @mod_pak.setter
    def mod_pak(self, value):
        self.config_parser.set('Paths', 'mod_pak', value)
        self.add_config_notes()
    
    @property
    def overwrite_default(self):
        """Bool: True -> mod_pak overwrites changes to unpacked archive on new load of this tool
                  False -> unpacked archive overwrites changes to mod_pak on new load of this tool"""
        return self.config_parser.getboolean('Misc', 'overwrite_default')
    
    @overwrite_default.setter
    def overwrite_default(self, value):
        self.config_parser.set('Misc', 'overwrite_default', str(value))
        self.add_config_notes()
    
    @property
    def hide_unpacked_content(self):
        """Set OS hidden flag to unpacked directory"""
        return self.config_parser.getboolean('Misc', 'hide_unpacked_content')
    
    @hide_unpacked_content.setter
    def hide_unpacked_content(self, value):
        self.config_parser.set('Misc', 'hide_unpacked_content', str(value))
        self.add_config_notes()
    
    @property
    def meld_config_path(self):
        """Path to Meld as per config.ini. Falls back to None"""
        return self.config_parser.get('Meld', 'path', fallback=None)
    
    @meld_config_path.setter
    def meld_config_path(self, value):
        self.config_parser.set('Meld', 'path', value)
        self.add_config_notes()
    
    @property
    def use_meld(self):
        """Bool: Launch Meld"""
        return self.config_parser.getboolean('Meld', 'enable')
    
    @use_meld.setter
    def use_meld(self, value):
        self.config_parser.set('Meld', 'enable', str(value))
        self.add_config_notes()
    
    @property
    def backup_enabled(self):
        """Bool: Create backup of mod_pak on startup"""
        return self.config_parser.getboolean('Backups', 'enable')
    
    @backup_enabled.setter
    def backup_enabled(self, value):
        self.config_parser.set('Backups', 'enable', str(value))
        self.add_config_notes()
    
    @property
    def backup_count(self):
        """Int: Number of rolling backups for backup manager to retain"""
        return self.config_parser.getint('Backups', 'count')
    
    @backup_count.setter
    def backup_count(self, value):
        self.config_parser.set('Backups', 'count', str(value))
        self.add_config_notes()
    
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
            self.backup_enabled, self.backup_count
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