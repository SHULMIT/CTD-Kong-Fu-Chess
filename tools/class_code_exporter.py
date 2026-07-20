"""Create one organized text file containing the full Python implementation."""

from __future__ import annotations

import os
from pathlib import Path


class ClassCodeExporter:
    """Exports every non-test Python module, grouped by project layer."""

    DEFAULT_OUTPUT_DIRECTORY = Path()

    _EXCLUDED_DIRECTORIES = {
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "tests",
        "texttests",
    }
    _LAYER_ORDER = {
        name: index
        for index, name in enumerate(
            (
                "main.py",
                "app",
                "controller",
                "game",
                "realtime",
                "rules",
                "model",
                "board_io",
                "errors",
                "config",
                "runner",
                "view",
                "tools",
            )
        )
    }

    def __init__(self, project_root: Path, output_name: str = "all_classes_code.txt") -> None:
        self._project_root = project_root
        self._output_path = project_root / self.DEFAULT_OUTPUT_DIRECTORY / output_name

    def update(self) -> bool:
        """Write the export only when its content changed.

        Returns ``True`` when the text file was updated.
        """
        content = self._build_content()
        if self._output_path.exists() and self._output_path.read_text(encoding="utf-8") == content:
            return False

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text(content, encoding="utf-8")
        return True

    def _build_content(self) -> str:
        source_files = self._source_files()
        grouped_files = self._group_files(source_files)
        parts = [
            "PROJECT - FULL PYTHON SOURCE CODE",
            "=" * 70,
            f"Files included: {len(source_files)}",
            "Tests, caches, virtual environments, and generated files are excluded.",
            "",
            "CONTENTS",
            "-" * 70,
        ]

        for group_name, files in grouped_files:
            parts.append(f"{group_name} ({len(files)} files)")
            parts.extend(
                f"  - {source_file.relative_to(self._project_root).as_posix()}"
                for source_file in files
            )

        for group_name, files in grouped_files:
            parts.extend(
                [
                    "",
                    "#" * 70,
                    f"SECTION: {group_name}",
                    "#" * 70,
                ]
            )
            for source_file in files:
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

    def _source_files(self) -> list[Path]:
        files: list[Path] = []
        for directory, subdirectories, filenames in os.walk(self._project_root):
            subdirectories[:] = [
                name for name in subdirectories if name not in self._EXCLUDED_DIRECTORIES
            ]
            for filename in filenames:
                source_file = Path(directory) / filename
                if source_file.suffix == ".py":
                    files.append(source_file)

        return sorted(files, key=self._file_sort_key)

    def _group_files(self, files: list[Path]) -> list[tuple[str, list[Path]]]:
        groups: dict[str, list[Path]] = {}
        for source_file in files:
            relative_path = source_file.relative_to(self._project_root)
            group_name = relative_path.parts[0]
            groups.setdefault(group_name, []).append(source_file)
        return list(groups.items())

    def _file_sort_key(self, source_file: Path) -> tuple[int, str]:
        relative_path = source_file.relative_to(self._project_root)
        group_name = relative_path.parts[0]
        group_order = self._LAYER_ORDER.get(group_name, len(self._LAYER_ORDER))
        return group_order, relative_path.as_posix().lower()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    changed = ClassCodeExporter(root).update()
    output_path = ClassCodeExporter.DEFAULT_OUTPUT_DIRECTORY / "all_classes_code.txt"
    print(f"Updated {output_path}" if changed else f"{output_path} is already up to date")
