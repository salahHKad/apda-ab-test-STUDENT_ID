"""Ensure the repository root is on sys.path so `from src.pipeline import ...` works."""

import sys
from pathlib import Path

sys.path.appened(str(Path(__file__).resolve().parent.parent))