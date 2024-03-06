import subprocess
import os
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

def run_mhl_tool_for_directory(directory, hash_option, script_directory, output_directory):
    """
    Use the MHL tool to generate MHL files for the entire directory.
    """
    print(f"Generating MHLs for directory: {directory} using {hash_option}")
    command = [
        'mhl', 'seal', '-t', hash_option, 
        '--output-folder', output_directory, directory
    ]

    subprocess.run(command, check=True, cwd=script_directory)

def update_mhl_entries_with_full_path(directory):
    """
    Update MHL entries to include full file paths.
    """
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

def compile_and_cleanup_mhl(directory):
    """
    Compile individual MHL files into a master MHL file and remove the individual ones.
    """
    master_mhl_path = os.path.join(directory, f"master_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.mhl")
    with open(master_mhl_path, 'w') as master_mhl:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.mhl') and not file.startswith("master_"):
                    individual_mhl_path = os.path.join(root, file)
                    with open(individual_mhl_path, 'r') as individual_mhl:
                        master_mhl.write(individual_mhl.read() + "\n\n")
                    os.remove(individual_mhl_path)  # Remove the individual MHL file

def main(master_path, target_path, hash_option):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    for directory in [master_path, target_path]:
        run_mhl_tool_for_directory(directory, hash_option, script_directory, directory)
        update_mhl_entries_with_full_path(directory)
        compile_and_cleanup_mhl(directory)
    
    print("MHL processing complete.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 create_mhl.py <master_directory> <target_directory> <hash_option>")
        sys.exit(1)
    
    _, master_dir, target_dir, hash_opt = sys.argv
    main(master_dir, target_dir, hash_opt)
