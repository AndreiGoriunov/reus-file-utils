import PySimpleGUI as sg

from reis_file_utils.thread_handlers import folder_organizer_handler
from reis_file_utils.window_config import *


class GUI:
    def __init__(self):
        self.current_window = MAIN_MENU
        self.location = None
        self._create_new_window()
        self._main_loop()

    def _create_new_window(self):
        window_details = LAYOUT_CONFIG.get(self.current_window, {})
        title = window_details.get("title", "")
        layout = window_details.get("layout", [])()

        # Create the window without specifying the location
        if self.location:
            new_window = sg.Window(title, layout, icon=ICON, location=self.location)
        else:
            new_window = sg.Window(title, layout, icon=ICON)

        self.window = new_window

    def _main_loop(self):
        while True:
            event, values = self.window.read()
            if not event == sg.WINDOW_CLOSED:
                self.location = self.window.CurrentLocation()
            # Handle the events
            if event == "Organize":
                folder_organizer_handler(self.window, values)
            elif event in LAYOUT_CONFIG:
                self.window.close()
                self.current_window = event
                self._create_new_window()
            elif event == sg.WINDOW_CLOSED:
                self.window.close()
                break
            else:
                pass
