import os
import sys
import shutil
import logging
import argparse

# Initialize logging
logging.basicConfig(filename='file_sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sync_files_to_target(comparison_results_path, master_dir, target_dir):
    """
    Sync files listed in the comparison results to the target directory,
    preserving the original directory structure under a new 'from_master' folder.
    """
    logging.info("Starting file synchronization.")
    target_sync_dir = os.path.join(target_dir, "from_master")

    try:
        with open(comparison_results_path, 'r') as file:
            for line in file:
                file_path = line.strip()
                if file_path:
                    relative_path = os.path.relpath(file_path, master_dir)
                    target_file_path = os.path.join(target_sync_dir, relative_path)

                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

                    shutil.copy2(file_path, target_file_path)
                    print(f"Synced: {file_path} to {target_file_path}")
                    logging.info(f"Synced: {file_path} to {target_file_path}")

        print("Syncing complete.")
        logging.info("File synchronization completed successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"Permission error: {e}")
        print(f"Error: Permission denied - {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        print(f"Error: An unexpected error occurred - {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync files from master to target based on comparison results.")
    parser.add_argument("comparison_results_path", type=str, help="Path to the comparison results file.")
    parser.add_argument("master_dir", type=str, help="Path to the master directory.")
    parser.add_argument("target_dir", type=str, help="Path to the target directory.")

    args = parser.parse_args()

    sync_files_to_target(args.comparison_results_path, args.master_dir, args.target_dir)
