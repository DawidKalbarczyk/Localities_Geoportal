"""Pozwala uruchamiać testy także spoza katalogu projektu."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
