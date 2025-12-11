import os
import json
import logging
from functools import wraps


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass


def logged(exception_cls, mode="file"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("JsonLogger")
            if not logger.hasHandlers():
                logger.setLevel(logging.ERROR)
                if mode == "file":
                    handler = logging.FileHandler("json_operations.log", encoding="utf-8")
                else:
                    handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            try:
                return func(*args, **kwargs)
            except exception_cls as e:
                logger.error(f"Error in '{func.__name__}': {e}")
                raise e
        return wrapper
    return decorator


class JsonFileManager:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"Файл '{self.file_path}' не знайдено")

    @logged(FileNotFound, mode="file")
    def create_file(self, initial_data=None):
        if os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                if initial_data is None:
                    json.dump([], f, ensure_ascii=False, indent=4)
                else:
                    json.dump(initial_data, f, ensure_ascii=False, indent=4)
        except OSError as e:
            raise FileNotFound(f"Не вдалося створити файл: {e}")

    @logged(FileCorrupted, mode="file")
    def read_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"Файл '{self.file_path}' не знайдено")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileCorrupted(f"Файл містить некоректний JSON: {e}")
        except Exception as e:
            raise FileCorrupted(f"Помилка читання файлу: {e}")

    @logged(FileCorrupted, mode="file")
    def write_file(self, data):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"Файл '{self.file_path}' не знайдено")
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise FileCorrupted(f"Помилка запису файлу: {e}")

    @logged(FileCorrupted, mode="file")
    def append_file(self, new_data, force_error=False):
        if not os.path.exists(self.file_path):
            raise FileNotFound(f"Файл '{self.file_path}' не знайдено")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                current_data = json.load(f)

            if not isinstance(current_data, list):
                current_data = [current_data] if current_data else []

            current_ids = [item.get("id", 0) for item in current_data if isinstance(item, dict)]
            new_id = max(current_ids) + 1 if current_ids else 1

            current_data.append(new_data)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)

            if force_error:
                raise FileCorrupted("Штучна помилка для тесту логування")

        except json.JSONDecodeError as e:
            raise FileCorrupted(f"Файл містить некоректний JSON: {e}")
        except Exception as e:
            raise FileCorrupted(f"Помилка допису (append): {e}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    file_name = "File_Json.json"

    if os.path.exists(file_name):
        os.remove(file_name)

    manager_creator = JsonFileManager.__new__(JsonFileManager)
    manager_creator.file_path = file_name
    manager_creator.create_file()

    manager = JsonFileManager(file_name)

    manager.append_file({"user": "Andriy", "role": "admin"})
    manager.append_file({"user": "Oksana", "role": "editor"})
    manager.append_file({"user": "Petro", "role": "viewer"})

    try:
        manager.append_file({"user": "TestError", "role": "tester"}, force_error=True)
    except FileCorrupted:
        pass

    data = manager.read_file()
    print(json.dumps(data, indent=4, ensure_ascii=False))