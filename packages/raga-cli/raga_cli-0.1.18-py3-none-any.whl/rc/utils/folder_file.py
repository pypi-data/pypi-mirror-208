import os


def get_non_empty_folders(folders):
    non_empty_folders = []

    for folder_path in folders:
        try:
            # Check if the folder exists
            if not os.path.exists(folder_path):
                print(f"Folder '{folder_path}' does not exist")
                continue

            # Check if the folder is empty
            is_empty = True
            for root, dirs, files in os.walk(folder_path):
                if files or dirs:
                    for file_name in files:
                        if not file_name.startswith('.'):  # Exclude hidden files
                            is_empty = False
                            break
                    if not is_empty:
                        break

            if not is_empty:
                non_empty_folders.append(folder_path)

        except OSError as e:
            print(f"Error occurred while checking folder '{folder_path}': {e}")

    return non_empty_folders


def check_empty_dirs(directory):
    for root, dirs, files in os.walk(directory):
        if ".rc" in dirs:
            dirs.remove(".rc")  # Exclude .rc folder from traversal
        if ".git" in dirs:
            dirs.remove(".git")  # Exclude .git folder from traversal

        if not dirs and not files:
            return True

    return False


def check_root_folder():
    root_folder = '.'
    excluded_files = ['.rc', '.gitignore', '.git', '.dvcignore']
    excluded_extensions = ['.dvc']

    files = []
    for file in os.listdir(root_folder):
        if file not in excluded_files and not any(file.endswith(ext) for ext in excluded_extensions) and not os.path.isdir(os.path.join(root_folder, file)):
            files.append(file)

    return bool(files)