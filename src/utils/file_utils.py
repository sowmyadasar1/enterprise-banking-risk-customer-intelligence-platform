import os
import json
from pathlib import Path
from typing import Union, Dict, Any


def ensure_directory_exists(dir_path: Union[str, Path]) -> None:
    """Creates a directory if it does not exist."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Reads a JSON file and returns its content as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(
    data: Dict[str, Any], file_path: Union[str, Path], indent: int = 4
) -> None:
    """Writes a dictionary to a JSON file."""
    ensure_directory_exists(Path(file_path).parent)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Returns the size of a file in Megabytes."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0
