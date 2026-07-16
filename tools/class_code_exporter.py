"""Create a single text file containing the project's implementation classes."""

from __future__ import annotations

import os
import re
from pathlib import Path


class ClassCodeExporter:
    """Exports every non-test Python module that declares a class."""

    _EXCLUDED_DIRECTORIES = {
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "tests",
        "texttests",
    }
    _CLASS_DECLARATION = re.compile(r"^\s*class\s+", re.MULTILINE)

    def __init__(self, project_root: Path, output_name: str = "all_classes_code.txt") -> None:
        self._project_root = project_root
        self._output_path = project_root / output_name

    def update(self) -> bool:
        """Write the export only when its content changed.

        Returns ``True`` when the text file was updated.
        """
        content = self._build_content()
        if self._output_path.exists() and self._output_path.read_text(encoding="utf-8") == content:
            return False

        self._output_path.write_text(content, encoding="utf-8")
        return True

    def _build_content(self) -> str:
        parts = [
            "PROJECT CLASSES - FULL SOURCE CODE",
            "=" * 70,
            "Test files and helper files are excluded.",
        ]

        for source_file in self._class_files():
            relative_path = source_file.relative_to(self._project_root).as_posix()
            parts.extend(
                [
                    "",
                    "=" * 70,
                    f"FILE: {relative_path}",
                    "=" * 70,
                    source_file.read_text(encoding="utf-8").rstrip(),
                ]
            )

        return "\n".join(parts) + "\n"

    def _class_files(self) -> list[Path]:
        files: list[Path] = []
        for directory, subdirectories, filenames in os.walk(self._project_root):
            subdirectories[:] = [
                name for name in subdirectories if name not in self._EXCLUDED_DIRECTORIES
            ]
            for filename in filenames:
                source_file = Path(directory) / filename
                if self._is_class_file(source_file):
                    files.append(source_file)

        return sorted(files, key=lambda path: path.as_posix().lower())

    def _is_class_file(self, source_file: Path) -> bool:
        if source_file.suffix != ".py" or source_file.name == "_verify5.py":
            return False
        return bool(self._CLASS_DECLARATION.search(source_file.read_text(encoding="utf-8")))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    changed = ClassCodeExporter(root).update()
    print("Updated all_classes_code.txt" if changed else "all_classes_code.txt is already up to date")
