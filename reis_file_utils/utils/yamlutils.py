from yaml import safe_load

def load_yaml(file_path: str) -> dict:
    with open(file_path, mode="r", encoding="utf-8") as file:
        return safe_load(file)
