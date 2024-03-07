import subprocess
import os
import sys
import logging
from datetime import datetime
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("mhl_process.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

def run_mhl_tool_for_directory(directory, hash_option, script_directory, output_directory):
    logging.info(f"Generating MHLs for directory: {directory} using {hash_option}")

    mhl_tool_path = os.path.join(script_directory, 'mhl')
    command = [
        mhl_tool_path, 'seal', '-t', hash_option, 
        '--output-folder', output_directory, directory
    ]

    try:
        result = subprocess.run(command, check=True, cwd=script_directory, text=True, capture_output=True)
        logging.info(f"MHL generation output for {directory}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to generate MHLs for {directory} with error: {e.stderr}")
        sys.exit(f"Error generating MHLs for directory: {directory}. Check mhl_process.log for details.")
def update_mhl_entries_with_full_path(directory):
    logging.info(f"Updating MHL entries with full paths in directory: {directory}")

    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.mhl'):
                    mhl_path = os.path.join(root, file)
                    tree = ET.parse(mhl_path)
                    root_element = tree.getroot()

                    for hash_tag in root_element.findall('.//hash'):
                        file_tag = hash_tag.find('file')
                        if file_tag is not None:
                            full_path = os.path.abspath(os.path.join(root, file_tag.text))
                            file_tag.text = full_path

                    tree.write(mhl_path)
    except Exception as e:
        logging.error(f"Error updating MHL entries in {directory}: {e}")
        sys.exit(f"Error updating MHL entries in directory: {directory}")

def compile_and_cleanup_mhl(directory):
    logging.info(f"Compiling and cleaning up MHL files in directory: {directory}")

    master_mhl_path = os.path.join(directory, f"master_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.mhl")

    try:
        with open(master_mhl_path, 'w') as master_mhl:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.mhl') and not file.startswith("master_"):
                        individual_mhl_path = os.path.join(root, file)
                        with open(individual_mhl_path, 'r') as individual_mhl:
                            master_mhl.write(individual_mhl.read() + "\n\n")
                        os.remove(individual_mhl_path)
    except Exception as e:
        logging.error(f"Error compiling/cleaning up MHL files in {directory}: {e}")
        sys.exit(f"Error during compilation/cleanup in directory: {directory}")

def main(master_path, target_path, hash_option):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    logging.info("Starting MHL processing.")

    for directory in [master_path, target_path]:
        run_mhl_tool_for_directory(directory, hash_option, script_directory, directory)
        update_mhl_entries_with_full_path(directory)
        compile_and_cleanup_mhl(directory)
    
    logging.info("MHL processing complete.")
    print("MHL processing complete.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        logging.error("Incorrect number of arguments provided.")
        print("Usage: python3 create_mhl.py <master_directory> <target_directory> <hash_option>")
        sys.exit(1)
    
    _, master_dir, target_dir, hash_opt = sys.argv
    main(master_dir, target_dir, hash_opt)
