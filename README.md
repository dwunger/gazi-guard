# Dying Light 2 Mod Update Helper

This Python script helps mod developers to prepare their Dying Light 2 mods for updates. It extracts the necessary mod files, creates two directories for comparison, and uses Meld for reviewing differences and merging updates as required. Furthermore, it automatically saves and updates changes in the `.pak` file whenever a file modification is detected in the mod directory.

## Prerequisites

- Python 3.x
- [Meld](https://meldmerge.org/) for comparison and review of files. If Meld is not installed or its path is not specified in the PATH environment variable, you may need to manually drag and drop the output directories to Meld or use any other file comparison tool of your preference.

## Usage

1. Place the script in the `./steamapps/common/Dying Light 2/ph/source/` directory or create an equivalent workspace.
2. Run the tool
3. Follow the prompts and instructions provided for first time setup

## Output

Upon execution, the script generates two directories:

1. `mod_scripts/` - Contains the unpacked files from your mod.
2. `source_scripts/` - Contains the unpacked files from the base game's data.pak.
   
🌟🌟🌟
This tool introduces an automatic update feature. It monitors the `mod_scripts/` directory for any changes and instantly updates the corresponding `.pak` file with the modified mod contents. This feature saves developers from manually repacking the mod each time a change is made.

## Configuration

The script uses a `config.ini` file for various settings, such as:

- Deep scan options for file and directory comparisons.
- Paths to source pak files.
- Path to mod pak file.
- Hide unpacked content option (makes the unpacked directories hidden).
- Path to Meld (optional).

Adjust these settings as needed before running the script.

## Limitations

The script assumes that the default data.pak archives are named `data0.pak` and `data1.pak`. If the archive names in your setup are different, adjust the source code accordingly.

## Contributions

Contributions are welcome to improve this tool. Please fork the repository and create a pull request with your changes.
