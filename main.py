import subprocess
import os
import glob

def menu():
    print("\nSelect an operation to perform:")
    print("1. Create MHLs")
    print("2. Compare Target to Master")
    print("3. Sync MHLs")
    print("4. Exit")
    choice = input("Enter choice (1/2/3/4): ")
    return choice

def find_latest_mhl_file(directory):
    """Find the latest MHL file in the given directory."""
    list_of_mhl_files = glob.glob(os.path.join(directory, '*.mhl'))
    latest_mhl_file = max(list_of_mhl_files, key=os.path.getctime, default=None)
    return latest_mhl_file

def run_create_mhls():
    print("Available hash algorithms:")
    print("1. xxhash64")
    print("2. xxhash64be")
    print("3. md5")
    print("4. sha1")
    hash_choice = input("Select a hash algorithm (1-4): ")
    
    hash_algorithms = {
        '1': 'xxhash64',
        '2': 'xxhash64be',
        '3': 'md5',
        '4': 'sha1'
    }
    
    selected_algorithm = hash_algorithms.get(hash_choice, None)
    if not selected_algorithm:
        print("Invalid choice. Please select a valid option.")
        return

    global master_directory_path
    global target_directory_path
    master_directory_path = input("Enter the master directory path: ")
    target_directory_path = input("Enter the target directory path: ")
    
    create_mhl_script_path = os.path.join(os.path.dirname(__file__), 'bin', 'create_mhl.py')
    subprocess.run(['python3', create_mhl_script_path, master_directory_path, target_directory_path, selected_algorithm], check=True)
    
    print("\nMHL creation completed for both master and target directories.")
    print("1. Return to main menu")
    print("2. Compare MHL files to see which files are in the master but not in the target")
    post_choice = input("Enter your choice (1 or 2): ")

    if post_choice == '1':
        return
    elif post_choice == '2':
        master_mhl_file = find_latest_mhl_file(master_directory_path)
        target_mhl_file = find_latest_mhl_file(target_directory_path)
        
        if not master_mhl_file or not target_mhl_file:
            print("Error: Could not find MHL files for comparison.")
            return

        # Call run_compare_mhls with the paths of the created MHL files
        run_compare_mhls(manual_paths=False, master_mhl_path=master_mhl_file, target_mhl_path=target_mhl_file)

def run_compare_mhls(manual_paths=True, master_mhl_path=None, target_mhl_path=None):
    global target_directory_path  # Ensure this global variable is defined elsewhere in your script

    if manual_paths:
        # Ask for paths if running in manual mode
        master_mhl_path = input("Enter the path to the master MHL file: ")
        target_mhl_path = input("Enter the path to the target MHL file: ")
    else:
        # When paths are provided, ensure they're used directly
        if not master_mhl_path or not target_mhl_path:
            print("MHL file paths must be provided for automatic comparison.")
            return
    
    output_file_name = "comparison_results.txt"
    comparison_results_path = os.path.join(target_directory_path, output_file_name)

    # Construct the path to the compare.py script
    compare_script_path = os.path.join(os.path.dirname(__file__), 'bin', 'compare.py')

    # Execute the comparison script as a subprocess using named arguments for the paths
    command = [
        'python3', compare_script_path,
        '--master_mhl_path', master_mhl_path,
        '--target_mhl_path', target_mhl_path,
        comparison_results_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Comparison complete. Differences are saved in {comparison_results_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during comparison: {e}")

    # Option after comparison for syncing
    print("\nDo you want to sync the files now?")
    print("1. Yes")
    print("2. No, return to main menu")
    sync_choice = input("Enter your choice (1 or 2): ")
    if sync_choice == '1':
        # Proceed with syncing using the generated comparison_results.txt
        run_sync_mhls(comparison_results_path=comparison_results_path)



def run_sync_mhls(comparison_results_path=None):
    if comparison_results_path is None:
        # Manual mode: ask for the comparison results file path
        comparison_results_path = input("Enter the path to the comparison results file: ")
    
    if not os.path.exists(comparison_results_path):
        print("Error: Comparison results file does not exist.")
        return

    # Construct the path to the sync_files.py script
    sync_script_path = os.path.join(os.path.dirname(__file__), 'bin', 'sync_files.py')

    # Call the sync_files.py script as a subprocess
    subprocess.run(['python3', sync_script_path, comparison_results_path, master_directory_path, target_directory_path], check=True)
    print("Syncing complete. Files have been synchronized to the target directory.")


def main():
    while True:
        user_choice = menu()
        if user_choice == '1':
            run_create_mhls()
        elif user_choice == '2':
            run_compare_mhls()
        elif user_choice == '3':
            run_sync_mhls()
        elif user_choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

if __name__ == "__main__":
    main()
