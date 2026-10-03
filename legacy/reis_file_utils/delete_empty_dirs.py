from os import listdir, path, walk, rmdir


# def walk_dir_and_delete_empty(path_: str):
#     unable_to_delete = []
#     for root, dirs, files in walk(path_):
#         for dir_ in dirs:
#             dir_path = path.join(root, dir_)
#             try:
#                 if not listdir(dir_path):
#                     rmdir(dir_path)
#                     print(f"Deleted: {dir_path}")
#             except PermissionError as e:
#                 print(f"Unable to delete {dir_path}. Skipping...")
#                 unable_to_delete.append(dir_path)
#                 continue

#     if unable_to_delete:
#         Cprint.print("Unable to delete the following items:", Cprint.RED)
#         Cprint.print("\n".join(unable_to_delete), Cprint.RED)


# def run():
#     folder_path = AppGUI.select_folder()
#     userApproved = True if input(f"Selected directory '{folder_path}' to delete empty folders (Y/N):\n").upper()== "Y"else False
#     if userApproved:
#         walk_dir_and_delete_empty(folder_path)
