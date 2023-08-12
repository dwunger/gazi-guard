from enum import Enum
from communications import CommsManager
import os
class ModStatus(Enum):
    SYNC = "sync"
    DESYNC = "desync"

        
class ModArchive:
    def __init__(self, comms):
        # Path to the mod archive
        #comms is an instance of CommsManager. Instances of CommsManager should be kept at 1 per process
        self.comms = comms
        self.status = 'sync'
        self.action = 'Initialized. No changes detected.'
        self.unpacked_path = None
        self.packed_path = None
        self.comms.send_message(self.comms.message.action(self.action))
        self.unpacked_file_count = None
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, state):

        if state == 'desync':
            self.action = 'Updating...'
            
        if state == 'sync':
            self.action = 'Repacked!'
        self.comms.send_message(self.comms.message.set(state))            
        self.comms.send_message(self.comms.message.action(self.action))
        self._status = state
    def get_unpacked_file_count(self):
        if self.unpacked_path:
            self.unpacked_file_count = self.recursive_count(self.unpacked_path)
            return self.unpacked_file_count  # Return the file count for clarity
        else:
            print("Warning: unpacked_path not set.")  # Debugging print
            return 0  # If unpacked_path isn't set, return 0

    @staticmethod
    def recursive_count(path):
        '''This is not *necessarily* synchronized with the mod package file count'''

        if not os.path.exists(path):  # Base case: If the path doesn't exist, return 0
            print(f"Path doesn't exist: {path}")  # Debugging print
            return 0

        folder_array = os.scandir(path)
        files = 0
        for entry in folder_array:
            print(f"Inspecting: {entry.path}")  # Debugging print

            if entry.is_file():
                files += 1
            elif entry.is_dir():
                file_count = ModArchive.recursive_count(entry.path)
                files += file_count
        return files