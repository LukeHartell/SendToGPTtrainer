"""Welcome"""

# Hi, this is SendToGPTtrainer.
# This program can help you add scources to your chatbot in GPT-trainer.

# Simply right-click the file or folder you want to add, and click "Send to GPT-trainer".
# If there is already a file with the same name in the database, you will be prompted for options.

# There is no installation-file for this yet, so you'll have to follow the get started section below.
# When you have completed the guide, you are left with an EXE-file, that you can share with others to let them upload to your bot. (Be careful please).

"""Get started"""

# 1     First you'll need to configure this .py script, and make sure it works for you.
#   a     Configure the script in the configuration section below.
#   b     Make sure you have python and all dependencies installed.
#   c     Use CMD as admin to execute the script
#         C:\>python "C:\Path\To\SendToTrainer.py" --help
#         To add the "Send to GPT-trainer" option in the context menu use --add-context-menu
#   d     Make sure to remove the option again for now. Use --remove-context-menu


# 2     Then you'll have to use auto-py-to-exe to compile it to an exe-file.
#   a     Install auto-py-to-exe if you havn't already.
#   b     Use the provided auto-py-to-exeConfig.json, but make sure to corret the path.


# 3     I suggest placing the EXE in C:\Program Files\SendToGPTtrainer.
#         It is not important, as you will never execute it manually.
#         However, it is important that the EXE is not moved after the context-menu has been added.
#         If you need to move the EXE, you'll have to remove the context menu option and add it again.


# 4     Add the context menu option for real this time.
#   a     To add context menu option use CMD as admin to execute the EXE.
#         C:\Path\To\SendToTrainer>SendToGPTtrainer.exe --add-context-menu
#         This adds the menu for all users on the computer and also saves the location of the EXE.


"""Configuration"""

# UUID to the bot
uuid = ""

# API key from GPT-trainer
# https://guide.gpt-trainer.com/api-key
api_token = ""

# Limits for uplaod.
max_items = 25 # This is the max number of files that can be uploaded at once
max_file_size = 50 * 1024 * 1024  # 50 MB per file

# Password to add the context-menu
context_menu_password = "P@ssw0rd" # User will be prompted for this password when using --add-context-menu


""""""



import winreg as reg
import os
import sys
import requests

upload_api_url = f"https://app.gpt-trainer.com/api/v1/chatbot/{uuid}/data-source/upload"
list_sources_api_url = f"https://app.gpt-trainer.com/api/v1/chatbot/{uuid}/data-sources"
supported_file_types = {'.pdf', '.docx', '.txt', '.md', '.csv', '.xlsx', '.xls', '.tex'}

def add_to_context_menu():
    script_path = os.path.abspath(__file__)
    python_executable = sys.executable  # Path to the Python executable
    key_paths = [
        r"Directory\shell\Send to GPT-trainer",
        r"*\shell\Send to GPT-trainer"  # * indicates all files
    ]
    
    try:
        for key_path in key_paths:
            command_key_path = os.path.join(key_path, 'command')
            reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
            reg.CreateKey(reg.HKEY_CLASSES_ROOT, command_key_path)
            
            with reg.OpenKey(reg.HKEY_CLASSES_ROOT, command_key_path, 0, reg.KEY_WRITE) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, f'"{python_executable}" "{script_path}" "%1"')

        print("Context menu items added successfully!")
    except Exception as e:
        print(f"Failed to add context menu items: {e}")

def remove_from_context_menu():
    key_paths = [
        r"Directory\shell\Send to GPT-trainer",
        r"*\shell\Send to GPT-trainer"
    ]
    
    try:
        for key_path in key_paths:
            reg.DeleteKey(reg.HKEY_CLASSES_ROOT, os.path.join(key_path, 'command'))
            reg.DeleteKey(reg.HKEY_CLASSES_ROOT, key_path)
        
        print("Context menu items removed successfully!")
    except Exception as e:
        print(f"Failed to remove context menu items: {e}")

def prompt_for_action(file_name):
    while True:
        print(f"File '{file_name}' already exists in GPT-trainer.")
        print(f"[1] upload anyway [2] overwrite [3] cancel upload")
        action = input(f">").strip()
        if action in ["1", "2", "3"]:
            return action
        else:
            print("Invalid option. Please choose '1', '2', or '3'.")

def fetch_existing_files():
    headers = {'Authorization': f'Bearer {api_token}'}
    try:
        response = requests.get(list_sources_api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching existing files: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def delete_file(uuid):
    headers = {'Authorization': f'Bearer {api_token}'}
    delete_url = f"https://app.gpt-trainer.com/api/v1/data-source/{uuid}/delete"
    try:
        response = requests.post(delete_url, headers=headers)
        if response.status_code == 200:
            print(f"Deleted old version")
        else:
            print(f"Could not delete old version: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception occurred while deleting file: {e}")

def upload_file(file_path):
    file_name = os.path.basename(file_path)
    print(f"Uploading file: {file_name}")
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file)}
            headers = {'Authorization': f'Bearer {api_token}'}
            response = requests.post(upload_api_url, files=files, headers=headers)
        if response.status_code == 200:
            return True, ""
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, str(e)

def upload_directory(dir_path):
    success_count = 0
    failure_list = []
    existing_files = fetch_existing_files()
    existing_file_dict = {file['file_name']: file['uuid'] for file in existing_files}
    files_to_upload = []

    for root, _, files in os.walk(dir_path):
        for file in files:
            if len(files_to_upload) >= max_items:
                break
            file_path = os.path.join(root, file)
            if os.path.splitext(file_path)[1] in supported_file_types:
                if os.path.getsize(file_path) > max_file_size:
                    failure_list.append((file_path, "File size exceeds maximum limit"))
                    continue
                files_to_upload.append(file_path)
            else:
                print(f"Unsupported file format: {file_path}")

    for file_path in files_to_upload:
        file_name = os.path.basename(file_path)
        if file_name in existing_file_dict:
            action = prompt_for_action(file_name)
            if action == "2":  # Overwrite
                print(f"Overwriting file: {file_name}")
                delete_file(existing_file_dict[file_name])
            elif action == "3":  # Cancel
                print(f"Upload canceled for file: {file_name}")
                continue
        success, reason = upload_file(file_path)
        if success:
            success_count += 1
        else:
            failure_list.append((file_path, reason))
            
    return success_count, failure_list

def main():
    if len(sys.argv) < 2:
        print("No file or directory specified.\nTo use this application, rightclick a file or directory and select 'Send to GPT-trainer' in the context menu.\n\nIf you don't have this option, you will need to add it")
        print("Execute this program with CMD as admin and use --help for more info.")
        input()
        return
    
    path = sys.argv[1]
    if not os.path.exists(path):
        print("Specified path does not exist.")
        input()
        return

    if os.path.isfile(path):
        if os.path.splitext(path)[1] not in supported_file_types:
            print("Unsupported file format.")
            input()
            return
        if os.path.getsize(path) > max_file_size:
            print("File size exceeds maximum limit.")
            input()
            return
        
        print(f"Uploading file: {path}")
        existing_files = fetch_existing_files()
        file_name = os.path.basename(path)
        existing_file_dict = {file['file_name']: file['uuid'] for file in existing_files}
        
        if file_name in existing_file_dict:
            action = prompt_for_action(file_name)
            if action == "2":  # Overwrite
                print(f"Overwriting file: {file_name}")
                delete_file(existing_file_dict[file_name])
            elif action == "3":  # Cancel
                print(f"Upload canceled for file: {file_name}")
                return

        success, reason = upload_file(path)
        if success:
            print("File uploaded successfully!")
        else:
            print(f"File upload failed: {reason}")
    elif os.path.isdir(path):
        print(f"Uploading directory: {path}")
        success_count, failure_list = upload_directory(path)
        print(f"All {success_count} items added successfully!")
        if failure_list:
            print("The following items failed to upload:")
            for file_path, reason in failure_list:
                print(f"- {file_path}: {reason}")
    else:
        print("Unsupported path type.")

    input("Press any key to exit")
    exit()

def check_password_and_add_context_menu():
    password = input("Enter password to add context menu: ").strip()
    if password == context_menu_password:
        add_to_context_menu()
    else:
        print("Incorrect password. Context menu not added.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("--add-context-menu           Adds 'Send to GPT-trainer' option in context menu")
            print("--remove-context-menu        Removes 'Send to GPT-trainer' option in context menu")

        elif sys.argv[1] == "--add-context-menu":
            check_password_and_add_context_menu() # Use this line to prompt user for password before adding context-menu
            # add_to_context_menu() # Use this line to skip the need for password when adding context-menu

        elif sys.argv[1] == "--remove-context-menu":
            remove_from_context_menu()
        else:
            main()
    else:
        main()