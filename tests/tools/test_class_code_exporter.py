"""Tests for the organized full-project source export."""

from pathlib import Path

from tools.class_code_exporter import ClassCodeExporter


def test_exports_all_python_modules_in_layer_order_and_excludes_tests(
    tmp_path: Path,
) -> None:
    (tmp_path / "view").mkdir()
    (tmp_path / "game").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "view" / "screen.py").write_text(
        "def draw():\n    return None\n",
        encoding="utf-8",
    )
    (tmp_path / "game" / "engine.py").write_text(
        "class Engine:\n    pass\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_engine.py").write_text(
        "class TestEngine:\n    pass\n",
        encoding="utf-8",
    )

    exporter = ClassCodeExporter(tmp_path)

    assert exporter.update() is True
    content = (tmp_path / "all_classes_code.txt").read_text(encoding="utf-8")
    assert "Files included: 2" in content
    assert "FILE: game/engine.py" in content
    assert "FILE: view/screen.py" in content
    assert "test_engine.py" not in content
    assert content.index("SECTION: game") < content.index("SECTION: view")
    assert exporter.update() is False
