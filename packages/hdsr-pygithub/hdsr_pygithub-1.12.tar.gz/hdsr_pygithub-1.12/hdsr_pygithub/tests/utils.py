from pathlib import Path
from typing import List


def _remove_dir_recursively(dir_path: Path) -> None:
    for child in dir_path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            _remove_dir_recursively(dir_path=child)
    dir_path.rmdir()


def _get_files_recursively(dir_path: Path, files_found: List[Path]) -> List[Path]:
    for child in dir_path.glob("*"):
        if child.is_dir():
            _get_files_recursively(dir_path=child, files_found=files_found)
        else:
            files_found.append(child)
    return files_found
