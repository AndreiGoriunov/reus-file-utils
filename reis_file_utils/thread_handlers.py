import PySimpleGUI as sg
from threading import Thread

from reis_file_utils.folder_organizer import FolderOrganizer


def folder_organizer_handler(window: sg.Window, values):
    selected_file = values["-FILE-"]
    selected_folder = values["-FOLDER-"]
    window["-FEEDBACK-"].update("Organizing... Please wait.")
    window.refresh()
    thread = Thread(target=FolderOrganizer(selected_file, selected_folder).run)
    thread.start()
    while True:
        event, values = window.read(timeout=100)  # checks every 100 ms
        if event == sg.WINDOW_CLOSED:
            window.close()
            return
        if not thread.is_alive():  # if the thread has finished its job
            window["-FEEDBACK-"].update("Finished.")
            break
