# Dying Light 2 Mod Update Helper

This repository contains a Python script which helps mod developers in preparing their Dying Light 2 mods for updates. The script extracts only the relevant mod files, creates two directories, and compares them using Meld to quickly review differences and merge updates as needed. Changes in the mod are automatically saved and updated in the `.pak` file whenever the script detects a file change.

## Prerequisites

1. Python 3.x
2. [Meld](https://meldmerge.org/) for comparison and review of the files. If Meld is not installed or available in PATH, you will need to manually drag and drop the output directories to Meld or any other comparison tool you prefer.

## Usage

1. Place the script in the `./steamapps/common/Dying Light 2/ph/source/` directory.
2. Run the script with Python.
3. Follow the script's instructions.

## Output

At the end of the script execution, you will find two directories:

1. `mod_scripts/` - Contains the unpacked files from your mod.
2. `source_scripts/` - Contains the unpacked files from the base game's data.pak.

The script also provides an automatic update feature. It monitors the `mod_scripts/` directory for any changes and instantly updates the corresponding `.pak` file with the new mod contents. This saves the developers the manual effort of re-packing the mod whenever a change is made.

## Configuration

The script uses a `config.ini` file for various settings, which includes:

- Deep scan option for comparing files and directories
- Source pak files paths
- Mod pak file path
- Overwrite default behavior
- Hide unpacked content (makes the unpacked directories hidden)
- Meld path (optional)

Please adjust these settings as per your requirements before running the script.

## Limitations

This script assumes the default data.pak archives are named `data0.pak` and `data1.pak`. If the archive names differ in your setup, please adjust the source code accordingly.

## Contributions

Contributions to improve the script are welcome. Please fork the repository and create a pull request with your changes.
