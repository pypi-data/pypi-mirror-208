import os

def get_path(folder_name, file_name):
    cwd = os.getcwd()
    return f"{cwd}/{folder_name}/{file_name}"