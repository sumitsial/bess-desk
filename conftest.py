"""Make the package importable in tests without installing it."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
