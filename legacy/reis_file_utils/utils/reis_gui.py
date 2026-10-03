import tkinter as tk
from abc import ABC
from tkinter import filedialog
from typing import Callable, List, Optional


class Widget:
    def __init__(
        self, widget_type: str, display_name: str, function: Optional[Callable] = None
    ):
        self.widget_type = widget_type
        self.display_name = display_name
        self.function = function


class AppFrame(ABC, tk.Frame):
    pady = 10
    current_row = 0

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.entries_var = {}  # Store references to StringVars
        self._add_back_to_menu_button()  # Add the back button

    def _add_back_to_menu_button(self):
        back_button = tk.Button(
            self, text="Back to Menu", command=self._back_to_main_menu
        )
        back_button.grid(
            row=AppFrame.current_row,
            column=0,
            columnspan=3,
            pady=AppFrame.pady,
            padx=5,
            sticky="ew",
        )
        AppFrame.current_row += 1  # Increment the row count

    def _back_to_main_menu(self):
        if isinstance(self.master, AppGUI):  # Check if the master is of type AppGUI
            self.master.back_to_main_menu()

    @classmethod
    def navigate_to(cls, app):
        frame_instance = cls(master=app)
        app.add_frame(frame_instance)

    def create_widgets(self, widgets: List[Widget]):
        for widget in widgets:
            if widget.widget_type == "button":
                if widget.function is not None:
                    btn = tk.Button(
                        self, text=widget.display_name, command=widget.function
                    )
                else:
                    btn = tk.Button(self, text=widget.display_name)
                btn.grid(row=AppFrame.current_row, column=0, columnspan=3, pady=AppFrame.pady, padx=5, sticky="ew")
                AppFrame.current_row += 1  # Increment the row count

            elif widget.widget_type == "file_prompt":
                self._create_file_folder_prompt(widget.display_name, "file")

            elif widget.widget_type == "folder_prompt":
                self._create_file_folder_prompt(widget.display_name, "folder")

    def _create_file_folder_prompt(self, display_name, prompt_type):
        label = tk.Label(self, text=display_name)
        var = tk.StringVar()
        entry = tk.Entry(self, textvariable=var, width=40)

        if prompt_type == "file":
            btn = tk.Button(
                self,
                text="Browse",
                command=lambda e=entry, v=var: self._populate_entry(
                    e, v, AppFrame._select_file()
                ),
            )
        else:
            btn = tk.Button(
                self,
                text="Browse",
                command=lambda e=entry, v=var: self._populate_entry(
                    e, v, AppFrame._select_folder()
                ),
            )

        # Store reference
        self.entries_var[display_name] = var

        # Place them using grid
        label.grid(row=AppFrame.current_row, column=0, pady=AppFrame.pady, sticky="w")
        entry.grid(
            row=AppFrame.current_row, column=1, pady=AppFrame.pady, padx=5, sticky="ew"
        )
        btn.grid(row=AppFrame.current_row, column=2, pady=AppFrame.pady, padx=5)
        AppFrame.current_row += 1  # Increment the row count

    @staticmethod
    def _select_folder(prompt: str = "Select a folder") -> str:
        root = tk.Tk()  # Creating a temporary root window
        root.withdraw()  # Hide the root window
        path = filedialog.askdirectory(title=prompt, parent=root)
        root.destroy()
        return path

    @staticmethod
    def _select_file(prompt: str = "Select a file") -> str:
        root = tk.Tk()  # Creating a temporary root window
        root.withdraw()  # Hide the root window
        path = filedialog.askopenfilename(title=prompt, parent=root)
        root.destroy()
        return path

    def _populate_entry(self, entry, var, value):
        var.set(value)


class AppGUI(tk.Tk):
    def __init__(self, title: str, main_menu_widgets: List[Widget]):
        super().__init__()
        self.title(title)

        # Stack to hold frame instances for navigation
        self.frames_stack = []

        # Create the main menu frame using the widgets passed
        self.main_menu_frame = self.create_main_menu_frame(main_menu_widgets)
        self.main_menu_frame.pack(fill=tk.BOTH, expand=True)

    def create_main_menu_frame(self, main_menu_widgets: List[Widget]):
        frame = MainMenuFrame(main_menu_widgets, master=self)
        return frame

    def back_to_main_menu(self):
        if self.frames_stack:
            # Remove and destroy the current frame from the stack
            current_frame = self.frames_stack.pop()
            current_frame.destroy()

            # Show the main menu
            self.main_menu_frame.pack(fill=tk.BOTH, expand=True)

    def add_frame(self, frame: AppFrame):
        # Hide the current frame
        if self.frames_stack:
            self.frames_stack[-1].pack_forget()
        else:
            self.main_menu_frame.pack_forget()

        # Push the new frame to the stack and display it
        self.frames_stack.append(frame)
        frame.pack(fill=tk.BOTH, expand=True)

    def quit_app(self):
        self.destroy()

    def run(self):
        self.mainloop()
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window
        root.attributes("-topmost", True)
        return root


class MainMenuFrame(AppFrame):
    def __init__(self, widgets: List[Widget], master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Add those widgets to the main menu frame
        self.create_widgets(widgets)

    def _add_back_to_menu_button(self):
        # Override the method so that MainMenuFrame doesn't display the "Back to Menu" button
        pass
