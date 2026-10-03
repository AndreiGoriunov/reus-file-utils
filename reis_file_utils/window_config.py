import PySimpleGUI as sg

MAIN_MENU = "Main Menu"
FOLDER_ORGANIZER = "Folder Organizer"
FILE_TRANSLITERATION = "File Transliteration"
DELETE_EMPTY_DIRS = "Delete Empty Directories"
MIN_WIDTH = 50
ICON = "icon.ico"

def main_menu_layout():
    return [
        [sg.Text(MAIN_MENU)],
        [sg.Text("", size=(MIN_WIDTH, 0))],
        [sg.Button(FOLDER_ORGANIZER)],
        [sg.Button(FILE_TRANSLITERATION)],
        [sg.Button(DELETE_EMPTY_DIRS)],
    ]


def folder_organizer_layout():
    return [
        [sg.Text(FOLDER_ORGANIZER)],
        [sg.Text("", size=(MIN_WIDTH, 0))],
        [
            sg.Text("Select a File:", size=(12, 1)),
            sg.InputText(key="-FILE-"),
            sg.FileBrowse(),
        ],
        [
            sg.Text("Select a Folder:", size=(12, 1)),
            sg.InputText(key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Button("Organize", key="Organize"),
            sg.Text("", size=(20, 0), key="-FEEDBACK-"),
        ],
        [sg.Button("Back", key=MAIN_MENU)],
    ]


def file_transliteration_layout():
    return [
        [sg.Text(FILE_TRANSLITERATION)],
        [sg.Text("", size=(MIN_WIDTH, 0))],
        [sg.Button("Back", key=MAIN_MENU)],
    ]


def delete_empty_dirs_layout():
    return [
        [sg.Text(DELETE_EMPTY_DIRS)],
        [sg.Text("", size=(MIN_WIDTH, 0))],
        [sg.Button("Back", key=MAIN_MENU)],
    ]


LAYOUT_CONFIG = {
    MAIN_MENU: {"title": MAIN_MENU, "layout": main_menu_layout},
    FOLDER_ORGANIZER: {"title": FOLDER_ORGANIZER, "layout": folder_organizer_layout},
    FILE_TRANSLITERATION: {
        "title": FILE_TRANSLITERATION,
        "layout": file_transliteration_layout,
    },
    DELETE_EMPTY_DIRS: {"title": DELETE_EMPTY_DIRS, "layout": delete_empty_dirs_layout},
}
