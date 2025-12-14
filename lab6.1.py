import os
import json
import logging
from functools import wraps


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass


LOGGER_NAME = "JsonLogger"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.ERROR)

if not logger.hasHandlers():
    handler = logging.FileHandler("json_operations.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def logged(exception_cls):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_cls as e:
                logger.error(f"Error in '{func.__name__}': {e}")
                raise
        return wrapper
    return decorator


class JsonFileManager:
    def __init__(self, file_path):
        self.file_path = file_path


    @logged(FileNotFound)
    def create_file(self, initial_data=None):
        if os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(
                    initial_data if initial_data is not None else [],
                    f,
                    ensure_ascii=False,
                    indent=4
                )
        except OSError as e:
            raise FileNotFound(f"Failed to create file: {e}")

    @logged(FileCorrupted)
    def read_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"File '{self.file_path}' not found")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileCorrupted(f"The file contains an invalid JSON: {e}")

    @logged(FileCorrupted)
    def write_file(self, data):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"File '{self.file_path}' not found")
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise FileCorrupted(f"File writing error: {e}")

    @logged(FileCorrupted)
    def append_file(self, new_data, force_error=False):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"File '{self.file_path}' not found")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                current_data = json.load(f)

            if not isinstance(current_data, list):
                current_data = [current_data] if current_data else []

            current_ids = [
                item.get("id", 0)
                for item in current_data
                if isinstance(item, dict)
            ]

            new_id = max(current_ids) + 1 if current_ids else 1
            new_data["id"] = new_id

            current_data.append(new_data)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)

            if force_error:
                raise FileCorrupted("Artificial error for logging text")

        except json.JSONDecodeError as e:
            raise FileCorrupted(f"The file contains an invalid JSON: {e}")
        except Exception as e:
            raise FileCorrupted(f"Failed to append data (append): {e}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    file_name = "data.json"

    if os.path.exists(file_name):
        os.remove(file_name)

    manager = JsonFileManager(file_name)

    manager.create_file()

    manager.append_file({"user": "Andriy", "role": "admin"})
    manager.append_file({"user": "Oksana", "role": "editor"})
    manager.append_file({"user": "Petro", "role": "viewer"})

    try:
        manager.append_file(
            {"user": "TestError", "role": "tester"},
            force_error=True
        )
    except FileCorrupted as e:
        print(f"Caught expected error: {e}")

    data = manager.read_file()
    print(json.dumps(data, indent=4, ensure_ascii=False))
