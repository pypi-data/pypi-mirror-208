# Clean Folder

Clean Folder is a Python package that provides a command-line interface for sorting files within a folder. It helps organize cluttered directories by moving files into specific subfolders based on their file types. Additionally, it offers an optional backup feature that creates an archive of the folder before sorting.

## Installation

You can install Clean Folder using pip:

```shell
pip install clean-folder_by_MK
```

## Usage

To use Clean Folder, open a command prompt or terminal and run the `clean-folder` command followed by the path to the folder you want to sort. The path argument is required.

```shell
clean-folder /path/to/folder
```

### Optional Backup (for now only for Windows based systems)

You can include the optional `backup` argument to create a backup of the folder before sorting the files. This can be useful to preserve the original state of the folder in case you want to revert the changes.

```shell
clean-folder /path/to/folder backup
```

The backup will be created as an archive file with the `backpup` appenden to the name, e.g., `/path/to/folder_backup.zip`.

## Example

Let's consider an example where we want to sort the files in the `~/Documents` folder with a backup:

```shell
clean-folder ~/Documents backup
```

This command will organize the files within `~/Documents` into subfolders based on their file types. A backup of the `~/Documents` folder will be created before sorting.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/takeRednotBlue/Python-core/blob/main-chgd/hw7/HW_project/clean_folder_by_MK/LICENSE) file for details.


## Acknowledgements

Clean Folder makes use of the following libraries:

- [shutil](https://docs.python.org/3/library/shutil.html): File and directory management operations
- [pathlib](https://docs.python.org/3/library/pathlib.html): Object-oriented filesystem paths
- [datetime](https://docs.python.org/3/library/datetime.html): Date and time manipulation
- [re](https://docs.python.org/3/library/re.html): Regular expression operations

These libraries greatly contribute to the functionality and efficiency of Clean Folder.

## Authors

- Maksym Klym - [GitHub](https://github.com/takeRednotBlue)
