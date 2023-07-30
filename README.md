# GaziGuard - Dying Light 2 Mod Version Control Tool

GaziGuard is an advanced tool designed to aid mod developers in tracking changes between updates, maintaining, and updating their Dying Light 2 mods. The tool's primary function is to facilitate seamless comparison and merging of changes in the mod files, using Meld, a popular visual diff, and merge tool. Additionally, GaziGuard also monitors the mod's directory for any changes and repacks the mod automatically, significantly reducing the time and effort required for manual repacking.

## Key Features
- Automatic repacking of mods upon detection of file modifications in the mod directory
- Integrated with Meld for file comparison and merging
- LED indicator to display the repacking status of the mod
- Toast notifications when successfully repacks
- Backup management for the mod files
- Convenient system tray icon for application control
- Easy configuration through a GUI for setting preferences

## Installation
GaziGuard is provided as a Windows installable package through Inno Setup, complete with binaries and DLLs. Additionally, a zipped version is also available for those preferring not to use an installer.

## Usage
Upon installation, launch the GaziGuard application. You'll notice a system tray icon for controlling the application and an LED indicator that shows the repacking status of the mod. Your mod should `auto-magically` appear in the Meld visual diff editor.

![GaziGuard UI Sample](https://github.com/dwunger/gazi-guard/blob/main/UI_sample.jpg?raw=true)

### Configuration
GaziGuard uses heuristics to build its configuration file. Should it make any mistakes, be sure to set your preferences through the GUI settings. Point the tool to your mod script path by following these steps:

1. `File` → `Options`
2. Drop down and select your mod script.
3. Apply and restart

If you would prefer to use another editor, you should be able to point it to any editor which supports launching diffs from the command line: `editor.exe` `dir1` `dir2`. Point the tool to your editor of choice in options.

### Using Meld for File Comparison and Merging
If Meld is not installed or its path is not specified, GaziGuard will prompt you to download and install it. Once installed, GaziGuard will automatically open Meld with the directories of your source scripts and mod scripts for comparison and merging.

### Automatic Repacking and Backup
GaziGuard automatically repacks your mod whenever a change is detected in the mod directory. The repacking status is displayed on the LED indicator. GaziGuard also manages backups of your mod files to prevent accidental data loss.

## Output

Upon execution, the script generates two directories (hidden by default):

1. `Unpacked/mod_scripts/` - Contains the unpacked files from your mod.
2. `Unpacked/source_scripts/` - Contains the unpacked files from the base game's data.pak.

## Build from source
1. Pip install all requirements:
   * `test.py` will dump such a list of requirements, but will need pruning
2. Build the executables:
   * Run `python setup.py` → Binaries build to `dist/merged_output_%timestamp%`
3. Create an installer (optional):
   * Update `install_script.iss` with the build path to the new binaries and compile!
   * This will require an existing installation of Meld.

## Limitations
GaziGuard assumes that your target workspace contains data0.pak, data1.pak, and your mod following this naming scheme. On initial setup, the tool will pick the lower data index as your mod. If the archive names in your setup are different, you will need to make this change in the options.

## Contributions
We welcome contributions to improve GaziGuard. Please fork the repository and create a pull request with your changes.
