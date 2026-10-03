import os
import shutil
from threading import Thread

from .utils.yamlutils import load_yaml


class FolderOrganizer:
    def __init__(self, yaml_path: str, folder_path: str):
        self.yaml_map = (
            load_yaml(yaml_path)
            if yaml_path.lower().endswith((".yaml", ".yml"))
            else {}
        )
        self.folder_path = folder_path

    def _get_unique_filename(self, target_folder, filename):
        base_name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename

        while os.path.exists(os.path.join(target_folder, new_filename)):
            new_filename = f"{base_name}_{counter}{ext}"
            counter += 1

        return new_filename

    def _organize_files(self, category_folder, extensions, folder_path):
        if not extensions:
            return
        for ext in extensions:
            for file in os.listdir(folder_path):
                if file.lower().endswith(ext.lower()):
                    base_name, file_ext = os.path.splitext(file)
                    lowercase_ext = file_ext.lower()
                    new_filename = f"{base_name}{lowercase_ext}"
                    unique_filename = self._get_unique_filename(
                        category_folder, new_filename
                    )
                    shutil.move(
                        os.path.join(folder_path, file),
                        os.path.join(category_folder, unique_filename),
                    )

    def _organize_folder(self):
        yaml_map = self.yaml_map
        folder_path = self.folder_path
        for category, value in yaml_map.items():
            if isinstance(value, list):
                category_folder = os.path.join(folder_path, category)
                if not os.path.exists(category_folder):
                    os.makedirs(category_folder)
                self._organize_files(category_folder, value, folder_path)
            elif isinstance(value, dict):
                for subcategory, extensions in value.items():
                    subcategory_folder = os.path.join(
                        folder_path, category, subcategory
                    )
                    if not os.path.exists(subcategory_folder):
                        os.makedirs(subcategory_folder)
                    self._organize_files(subcategory_folder, extensions, folder_path)

    def run(self):
        self._organize_folder()
