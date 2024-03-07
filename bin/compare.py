import xml.etree.ElementTree as ET
import argparse
import sys
import os
import re
import logging
from datetime import datetime

logging.basicConfig(filename='mhl_comparison.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_most_recent_mhl(directory):
    logging.info(f"Searching for the most recent MHL file in directory: {directory}")
    if not os.path.isdir(directory):
        logging.error(f"Directory not found: {directory}")
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")
    mhl_files = [f for f in os.listdir(directory) if re.match(r'^master_\d{4}-\d{2}-\d{2}_\d{6}\.mhl$', f)]
    if not mhl_files:
        logging.error("No MHL files found in the specified directory.")
        raise FileNotFoundError("No MHL files found in the specified directory.")
    
    dates_files = [(datetime.strptime(f[7:23], '%Y-%m-%d_%H%M%S'), f) for f in mhl_files]
    most_recent_file = max(dates_files, key=lambda x: x[0])[1]
    logging.info(f"Most recent MHL file found: {most_recent_file}")
    return os.path.join(directory, most_recent_file)

def parse_mhl(mhl_path):
    logging.info(f"Parsing MHL file: {mhl_path}")
    if not os.path.exists(mhl_path):
        logging.error(f"MHL file not found: {mhl_path}")
        raise FileNotFoundError(f"The MHL file '{mhl_path}' does not exist.")
    try:
        tree = ET.parse(mhl_path)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Error parsing MHL file '{mhl_path}': {e}")
        raise ValueError(f"Error parsing MHL file '{mhl_path}': {e}")

    hash_values = set()
    for hash_element in root.findall('.//hash'):
        for hash_type in ['xxhash64', 'xxhash64be', 'md5', 'sha1']:
            hash_tag = hash_element.find(f'.//{hash_type}')
            if hash_tag is not None:
                hash_values.add(hash_tag.text)

    return hash_values

def compare_mhls(master_mhl_path, target_mhl_path, output_file):
    logging.info("Comparing MHL files.")
    try:
        master_hashes = parse_mhl(master_mhl_path)
        target_hashes = parse_mhl(target_mhl_path)
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(e)
    except ValueError as e:
        logging.error(e)
        sys.exit(e)

    missing_hashes = master_hashes - target_hashes

    try:
        tree = ET.parse(master_mhl_path)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Error parsing MHL file '{master_mhl_path}': {e}")
        sys.exit(f"Error parsing MHL file '{master_mhl_path}': {e}")

    missing_files = []
    for hash_element in root.findall('.//hash'):
        file_element = hash_element.find('file')
        for hash_type in ['xxhash64', 'xxhash64be', 'md5', 'sha1']:
            hash_tag = hash_element.find(f'.//{hash_type}')
            if hash_tag is not None and hash_tag.text in missing_hashes:
                if file_element is not None:
                    missing_files.append(file_element.text)
                    break

    try:
        with open(output_file, 'w') as f:
            for file_path in sorted(missing_files):
                f.write(f"{file_path}\n")
        logging.info(f"Differences written to {output_file}")
    except IOError as e:
        logging.error(f"Failed to write to output file '{output_file}': {e}")
        sys.exit(f"Failed to write to output file '{output_file}': {e}")

    return missing_files

def main():
    logging.info("MHL comparison script started.")
    parser = argparse.ArgumentParser(description='Compare two MHL files and output differences.')
    parser.add_argument('--master_mhl_path', type=str, help='Path to the master MHL file')
    parser.add_argument('--target_mhl_path', type=str, help='Path to the target MHL file')
    parser.add_argument('output_file', type=str, help='Output file to store differences', nargs='?')
    
    args = parser.parse_args()

    if not args.output_file:
        args.output_file = input("Enter the output file path for differences: ")
    
    if not args.master_mhl_path or not os.path.exists(args.master_mhl_path):
        logging.error("Master MHL file path is missing or does not exist.")
        sys.exit("Error: Master MHL file path is missing or does not exist.")
    if not args.target_mhl_path or not os.path.exists(args.target_mhl_path):
        logging.error("Target MHL file path is missing or does not exist.")
        sys.exit("Error: Target MHL file path is missing or does not exist.")

    try:
        compare_mhls(args.master_mhl_path, args.target_mhl_path, args.output_file)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(f"An error occurred: {e}")

    logging.info("MHL comparison script completed.")

if __name__ == "__main__":
    main()
