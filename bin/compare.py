import xml.etree.ElementTree as ET
import argparse
import sys
import os
import re
from datetime import datetime

def find_most_recent_mhl(directory):
    """Find the most recent MHL file in the specified directory based on the naming convention."""
    mhl_files = [f for f in os.listdir(directory) if re.match(r'^master_\d{4}-\d{2}-\d{2}_\d{6}\.mhl$', f)]
    if not mhl_files:
        raise FileNotFoundError("No MHL files found in the specified directory.")
    
    # Parse the dates from the filenames and find the most recent
    dates_files = [(datetime.strptime(f[7:23], '%Y-%m-%d_%H%M%S'), f) for f in mhl_files]
    most_recent_file = max(dates_files, key=lambda x: x[0])[1]
    return os.path.join(directory, most_recent_file)

def parse_mhl(mhl_path):
    """Parse an MHL file and return a set of hash values."""
    tree = ET.parse(mhl_path)
    root = tree.getroot()
    hash_values = set()

    for hash_element in root.findall('.//hash'):
        # Attempt to find various hash elements and add them to the set
        for hash_type in ['xxhash64', 'xxhash64be', 'md5', 'sha1']:
            hash_tag = hash_element.find(f'.//{hash_type}')
            if hash_tag is not None:
                hash_values.add(hash_tag.text)

    return hash_values

def compare_mhls(master_mhl_path, target_mhl_path, output_file):
    """Compare hash values in two MHL files and write file paths of missing items to output file."""
    master_hashes = parse_mhl(master_mhl_path)
    target_hashes = parse_mhl(target_mhl_path)

    # Find hashes present in master but not in target
    missing_hashes = master_hashes - target_hashes

    # Now, find which files these hashes correspond to in the master MHL
    tree = ET.parse(master_mhl_path)
    root = tree.getroot()
    missing_files = []

    for hash_element in root.findall('.//hash'):
        file_element = hash_element.find('file')
        for hash_type in ['xxhash3', 'xxhash64', 'xxhash64be', 'md5', 'sha1', 'sha256']:
            hash_tag = hash_element.find(f'.//{hash_type}')
            if hash_tag is not None and hash_tag.text in missing_hashes:
                if file_element is not None:
                    missing_files.append(file_element.text)
                    break  # Stop checking other hash types if one is found missing

    # Write the file paths of missing items to the output file
    with open(output_file, 'w') as f:
        for file_path in sorted(missing_files):
            f.write(f"{file_path}\n")

    return missing_files

    

def main():
    parser = argparse.ArgumentParser(description='Compare two MHL files and output differences.')
    parser.add_argument('--master_mhl_path', type=str, help='Path to the master MHL file')
    parser.add_argument('--target_mhl_path', type=str, help='Path to the target MHL file')
    parser.add_argument('output_file', type=str, help='Output file to store differences', nargs='?')
    
    args = parser.parse_args()

    if not args.output_file:
        # Assuming interactive mode if no output file is provided
        args.output_file = input("Enter the output file path for differences: ")

    if not args.master_mhl_path:
        args.master_mhl_path = input("Enter the path to the master MHL file: ")
    if not args.target_mhl_path:
        args.target_mhl_path = input("Enter the path to the target MHL file: ")

    compare_mhls(args.master_mhl_path, args.target_mhl_path, args.output_file)

if __name__ == "__main__":
    main()

