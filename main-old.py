import tkinter as tk
from reis_file_utils.frames.folder_organizer import FolderOrganizerFrame
from reis_file_utils.utils.reis_gui import AppGUI, MainMenuFrame, Widget

# def main_menu():
#     print("Rei's KXA File Utils")
#     print("===========================")
#     print("1. Transliterate File Names")
#     print("2. Folder Organizer")
#     print("3. Delete Empty Dirs")
#     print("4. Exit")
#     print("===========================")

#     while True:
#         choice: str = input("Enter util # to use: ")
#         if choice == "1":
#             print("Transliterate File Names")
#             translitiration.run()
#             break
#         if choice == "2":
#             print("Folder Organizer")
#             folder_organizer.run()
#             break
#         if choice == "3":
#             print("Delete Empty Directories")
#             delete_empty_dirs.run()
#             break
#         if choice == "4":
#             print("Goodbye!")
#             break
#         else:
#             print("Invalid choice. Please try again.")



if __name__ == "__main__":
    main_menu_widgets = [
        Widget("button", "Folder Organizer", lambda: FolderOrganizerFrame.navigate_to(app)),
        # ... [your other widgets here]
    ]
    app = AppGUI("Rei's File Utilities", main_menu_widgets)
    app.run()
