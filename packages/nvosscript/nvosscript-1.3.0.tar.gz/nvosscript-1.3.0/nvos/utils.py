import os


def check_workspace_exist(current_path):
    if current_path == os.path.dirname(current_path):
        return "", False
    for file_name in os.listdir(current_path):
        if ".ndtc" == file_name:
            return current_path, True
    return check_workspace_exist(os.path.dirname(current_path))


def check_subdirectory_workspace_exist(current_path, index=0):
    for file_name in os.listdir(current_path):
        if ".ndtc" == file_name and index >= 1:
            return os.path.join(current_path, file_name), True
    for file_name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, file_name)):
            index = index + 1
            subdirectory_workspace, result = check_subdirectory_workspace_exist(os.path.join(current_path, file_name),
                                                                                index)
            if result:
                return subdirectory_workspace, result
    return "", False


