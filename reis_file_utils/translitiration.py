import os

def translitirate(text: str, translit_map: dict) -> str:
    name, extension = os.path.splitext(text)

    for original, replacement in translit_map.items():
        name = name.replace(original, replacement)
    return name + extension


def rename_files_in_folder(folder_path, yaml_path):
    translit_map = load_yaml(yaml_path)
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            new_file_name = translitirate(file_name, translit_map)

            old_file_path = os.path.join(folder_path, file_name)
            new_file_path = os.path.join(folder_path, new_file_name)

            os.rename(old_file_path, new_file_path)


def run():
    yaml_path = AppGUI.select_file("Select yaml mapping file")
    if yaml_path == "":
        return
    folder_path = AppGUI.select_folder("Select folder containing files for renaming")
    if folder_path == "":
        return
    userApproved = (
        True
        if input(
            f"Using map from '{yaml_path}' to rename files in '{folder_path}' (Y/N):\n"
        ).upper()
        == "Y"
        else False
    )
    if userApproved:
        rename_files_in_folder(folder_path, yaml_path)
