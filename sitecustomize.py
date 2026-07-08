import importlib.util
import os
import sys

# PROJECT_ROOT הוא תיקיית הריצה (sys.path[0]) — לא תיקיית הקובץ הזה,
# כי הקובץ הזה מועתק ל-site-packages אבל הפרויקט נמצא איפשהו אחר.
PROJECT_ROOT = sys.path[0] if sys.path else os.getcwd()
IO_PACKAGE_DIR = os.path.join(PROJECT_ROOT, "io")
IO_INIT_FILE = os.path.join(IO_PACKAGE_DIR, "__init__.py")

if os.path.isdir(IO_PACKAGE_DIR) and os.path.exists(IO_INIT_FILE):
    spec = importlib.util.spec_from_file_location(
        "io",
        IO_INIT_FILE,
        submodule_search_locations=[IO_PACKAGE_DIR],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["io"] = module
    spec.loader.exec_module(module)
