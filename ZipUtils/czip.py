import json
import subprocess
import os, sys
def resource_path(relative_path):
    """standardize relative references, copied from utils"""
    
    # List of file names to be redirected to AppData

    redirect_files = ['config.ini', 'LOG_INFO.log']


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

def remove_from_zip(zip_file_path: str, file_to_delete: str) -> dict:
    """
    Delete a file from a zip archive.

    Parameters:
        zip_file_path (str): The path to the zip archive.
        file_to_delete (str): The relative path of the file to delete within the zip archive.
                              Note: Relative paths should use forward slashes ("/") even on Windows.

    Returns:
        dict: A dictionary containing the result of the operation. The dictionary will have two keys:
            - 'Success': A boolean indicating if the deletion was successful.
            - 'Path': The path of the file that was deleted if successful, or an error message if unsuccessful.
    """
    input_data = {
        "ZipFilePath": zip_file_path,
        "FileToDelete": file_to_delete
    }
    json_input = json.dumps(input_data)
    result = subprocess.run(["ZipUtils/resources/ZipProc.exe"], input=json_input, text=True, capture_output=True)

    try:
        result_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        result_data = {"Success": False, "Path": "Invalid JSON format."}

    return result_data

'''
Version without inheritance from zipfile
'''
class ZipHandler:
    def __init__(self, zip_file_path: str):
        """
        Initialize the ZipHandler with the path to the zip archive.

        Parameters:
            zip_file_path (str): The path to the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.
        """
        self.zip_file_path = zip_file_path

    def remove(self, file_to_remove: str) -> dict:
        """
        Remove a file from the zip archive.

        Parameters:
            file_to_remove (str): The relative path of the file to remove within the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary will have two keys:
                - 'Success': A boolean indicating if the removal was successful.
                - 'Path': The path of the file that was removed if successful, or an error message if unsuccessful.
        """
        input_data = {
            "ZipFilePath": self.zip_file_path,
            "FileToRemove": file_to_remove
        }
        json_input = json.dumps(input_data)
        result = subprocess.run(["ZipUtils/resources/ZipProc.exe"], input=json_input, text=True, capture_output=True)

        try:
            result_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            result_data = {"Success": False, "Path": "Invalid JSON format."}

        return result_data

    def overwrite(self, existing_file: str, new_file_path: str) -> dict:
        """
        Overwrite an existing file in the zip archive with a new file.

        Parameters:
            existing_file (str): The relative path of the file to be overwritten within the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.
            new_file_path (str): The path to the new file that will replace the existing file.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary will have two keys:
                - 'Success': A boolean indicating if the overwrite was successful.
                - 'Path': The path of the file that was overwritten if successful, or an error message if unsuccessful.
        """
        # Remove the existing file from the zip archive
        result_remove = self.zip_remove(existing_file)

        if result_remove['Success']:
            # Add the new file to the zip archive
            input_data = {
                "ZipFilePath": self.zip_file_path,
                "NewFilePath": new_file_path
            }
            json_input = json.dumps(input_data)
            result_add = subprocess.run(["ZipUtils/resources/ZipProc.exe"], input=json_input, text=True, capture_output=True)

            try:
                result_data = json.loads(result_add.stdout)
            except json.JSONDecodeError:
                result_data = {"Success": False, "Path": "Invalid JSON format."}

            return result_data
        else:
            # If removal failed, return the remove operation result
            return result_remove
        
    # ALiases
    zip_remove = remove
    rm = remove
    delete = remove
    rmfile = remove
    remove_file = remove
    removefile = remove
    replace = overwrite

'''
With Inheritance from Zipfile. Work in progress
class ZipHandler(zipfile.ZipFile):
    def __init__(self, zip_file_path: str, mode='r', *args, **kwargs):
        """
        Initialize the ZipHandler with the path to the zip archive.

        Parameters:
            zip_file_path (str): The path to the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.
            mode (str): The mode in which the zip file should be opened. Default is 'r' (read mode).
                        Refer to the zipfile.ZipFile documentation for available modes.
        """
        super().__init__(zip_file_path, mode, *args, **kwargs)

    def remove(self, file_to_remove: str) -> dict:
        """
        Remove a file from the zip archive.

        Parameters:
            file_to_remove (str): The relative path of the file to remove within the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary will have two keys:
                - 'Success': A boolean indicating if the removal was successful.
                - 'Path': The path of the file that was removed if successful, or an error message if unsuccessful.
        """
        try:
            self.remove(file_to_remove)
            return {"Success": True, "Path": file_to_remove}
        except KeyError:
            return {"Success": False, "Path": f"File not found: {file_to_remove}"}

    def overwrite(self, existing_file: str, new_file_path: str) -> dict:
        """
        Overwrite an existing file in the zip archive with a new file.

        Parameters:
            existing_file (str): The relative path of the file to be overwritten within the zip archive.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.
            new_file_path (str): The path to the new file that will replace the existing file.
                                  Note: Relative paths should use forward slashes ("/") even on Windows.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary will have two keys:
                - 'Success': A boolean indicating if the overwrite was successful.
                - 'Path': The path of the file that was overwritten if successful, or an error message if unsuccessful.
        """
        try:
            # Remove the existing file from the zip archive
            self.remove(existing_file)
            # Add the new file to the zip archive
            self.write(new_file_path, existing_file)
            return {"Success": True, "Path": existing_file}
        except Exception as e:
            return {"Success": False, "Path": str(e)}

    # Aliases
    rm = remove
    delete = remove
    rmfile = remove
    remove_file = remove
    removefile = remove
    replace = overwrite

'''