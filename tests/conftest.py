import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_DIR = ROOT / "py"
if str(PY_DIR) not in sys.path:
    sys.path.insert(0, str(PY_DIR))
