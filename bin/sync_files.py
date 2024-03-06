import os
import shutil

def sync_files_to_target(comparison_results_path, master_dir, target_dir):
    """
    Sync files listed in the comparison results to the target directory,
    preserving the original directory structure under a new 'from_master' folder.
    """
    target_sync_dir = os.path.join(target_dir, "from_master")

    with open(comparison_results_path, 'r') as file:
        for line in file:
            file_path = line.strip()
            if file_path:
                relative_path = os.path.relpath(file_path, master_dir)
                target_file_path = os.path.join(target_sync_dir, relative_path)

                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

                shutil.copy2(file_path, target_file_path)
                print(f"Synced: {file_path} to {target_file_path}")

    print("Syncing complete.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync files from master to target based on comparison results.")
    parser.add_argument("comparison_results_path", type=str, help="Path to the comparison results file.")
    parser.add_argument("master_dir", type=str, help="Path to the master directory.")
    parser.add_argument("target_dir", type=str, help="Path to the target directory.")

    args = parser.parse_args()

    sync_files_to_target(args.comparison_results_path, args.master_dir, args.target_dir)
