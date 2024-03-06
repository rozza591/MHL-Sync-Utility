# MHL Sync Utility

The MHL Sync Utility is a Python-based tool designed to facilitate the synchronization and integrity verification of media files across different storage locations using Media Hash List (MHL) files. MHL files contain checksums (hashes) for media files, providing a reliable method to ensure files are transferred accurately and remain unaltered during the sync process.

## Features

- **MHL Creation**: Automates the generation of MHL files for directories, capturing file states using robust hashing algorithms (xxhash64, xxhash64be, MD5, SHA1) to suit various security and performance needs.
- **Comparison**: Efficiently compares MHL files between a "master" and a "target" directory to swiftly identify missing or altered files, guaranteeing data integrity between the source and destination.
- **Synchronization**: Leverages comparison results to synchronize files from the master to the target directory, ensuring the target accurately reflects the master. This includes copying missing files and optionally updating those that have changed.
- **Versatile Operation Modes**: Supports both interactive and automated modes, allowing manual oversight or seamless integration into automated workflows for data management.
- **Comprehensive Reporting**: Generates detailed reports on the comparison and synchronization activities, including synced, missing, or altered files, facilitating transparency and auditability.

## Usage

- **Launching the Utility**
```python3 main.py```
This will start the menu where you can interact with the tool. Either follow each step from start to finish, or use certain utilities if you already have pre generated MHL files you wish to compare.

## Installation

Start by cloning the repository and installing Python 3.x if not already installed:
`git clone https://github.com/yourusername/mhl-sync-utility.git`
`cd mhl-sync-utility`

