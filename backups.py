import os 
import glob
import zipfile
import time
class BackupHandler:
    def __init__(self, backup_path, backup_count, mod_pak):
        self.backup_path = backup_path
        self.backup_count = backup_count
        self.mod_pak = mod_pak
        self.handle_backup()

    def handle_backup(self):
        # Ensure the backup directory exists
        os.makedirs(self.backup_path, exist_ok=True)

        # Compress the mod_pak file
        timestamp = int(time.time())
        compressed_file = os.path.join(self.backup_path, f'backup_{timestamp}.pak')
        with zipfile.ZipFile(compressed_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.mod_pak, os.path.basename(self.mod_pak))

        # Get a list of all backup files
        all_backups = glob.glob(os.path.join(self.backup_path, 'backup_*.pak'))
        
        #block if deleting more than one backup
        files_to_delete = len(all_backups) - self.backup_count 
        if files_to_delete > 1:
            delete_choice = input(f"{files_to_delete} backups were found! Only {self.backup_count} were expected. Delete oldest \nDelete {self.backup_count - files_to_delete} oldest backups? y/n")
            if delete_choice != 'y':
                return

        # If the number of backups exceeds the maximum allowed count
        while len(all_backups) > self.backup_count:
            all_backups = glob.glob(os.path.join(self.backup_path, 'backup_*.pak'))
            # Sort the backups by their creation times (obtained from filenames)
            sorted_backups = sorted(all_backups, key=lambda f: int(f.split('_')[-1].split('.')[0]))

            # Delete the oldest backup file
            os.remove(sorted_backups[0])
            