import subprocess
import os
import glob
import logging

logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Application started.")

def menu():
    logging.info("Displaying menu.")
    print("\nSelect an operation to perform:")
    print("1. Create MHLs")
    print("2. Compare Target to Master")
    print("3. Sync MHLs")
    print("4. Exit")
    choice = input("Enter choice (1/2/3/4): ")
    logging.info(f"User selected: {choice}")
    return choice

def find_latest_mhl_file(directory):
    logging.info(f"Finding latest MHL file in directory: {directory}")
    list_of_mhl_files = glob.glob(os.path.join(directory, '*.mhl'))
    latest_mhl_file = max(list_of_mhl_files, key=os.path.getctime, default=None)
    logging.info(f"Latest MHL file found: {latest_mhl_file}")
    return latest_mhl_file

def run_create_mhls():
    logging.info("Running create MHLs process.")
    print("Available hash algorithms:")
    print("1. xxhash64")
    print("2. xxhash64be")
    print("3. md5")
    print("4. sha1")
    hash_choice = input("Select a hash algorithm (1-4): ")
    logging.info(f"Hash algorithm selected: {hash_choice}")
    
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
    try:
        subprocess.run(['python3', create_mhl_script_path, master_directory_path, target_directory_path, selected_algorithm], check=True)
        logging.info("MHL creation completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during MHL creation: {e}")
        print(f"Error: {e}")
    
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
        run_compare_mhls(manual_paths=False, master_mhl_path=master_mhl_file, target_mhl_path=target_mhl_file)

def run_compare_mhls(manual_paths=True, master_mhl_path=None, target_mhl_path=None):
    logging.info("Running compare MHLs process.")
    global target_directory_path

    if manual_paths:
        master_mhl_path = input("Enter the path to the master MHL file: ")
        target_mhl_path = input("Enter the path to the target MHL file: ")
    else:
        if not master_mhl_path or not target_mhl_path:
            print("MHL file paths must be provided for automatic comparison.")
            return
    
    output_file_name = "comparison_results.txt"
    comparison_results_path = os.path.join(target_directory_path, output_file_name)

    compare_script_path = os.path.join(os.path.dirname(__file__), 'bin', 'compare.py')

    command = [
        'python3', compare_script_path,
        '--master_mhl_path', master_mhl_path,
        '--target_mhl_path', target_mhl_path,
        comparison_results_path
    ]

    try:
        subprocess.run(command, check=True)
        logging.info("Comparison completed successfully.")
        print(f"Comparison complete. Differences are saved in {comparison_results_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during comparison: {e}")
        print(f"An error occurred during comparison: {e}")

    print("\nDo you want to sync the files now?")
    print("1. Yes")
    print("2. No, return to main menu")
    sync_choice = input("Enter your choice (1 or 2): ")
    if sync_choice == '1':
        run_sync_mhls(comparison_results_path=comparison_results_path)



def run_sync_mhls(comparison_results_path=None):
    logging.info("Running sync MHLs process.")
    if comparison_results_path is None:
        comparison_results_path = input("Enter the path to the comparison results file: ")
    
    if not os.path.exists(comparison_results_path):
        print("Error: Comparison results file does not exist.")
        return

    sync_script_path = os.path.join(os.path.dirname(__file__), 'bin', 'sync_files.py')

    try:
        subprocess.run(['python3', sync_script_path, comparison_results_path, master_directory_path, target_directory_path], check=True)
        logging.info("Syncing completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during syncing: {e}")
        print(f"Error: {e}")


def main():
    logging.info("Entering main loop.")
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
