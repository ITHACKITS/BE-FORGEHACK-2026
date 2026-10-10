"""
tests/conftest.py

Tests run offline (AGENTS.md principle 6). Set before any app module is imported.
"""

import os

os.environ["STANDBAI_OFFLINE"] = "1"
