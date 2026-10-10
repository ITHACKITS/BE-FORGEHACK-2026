"""
app/core/offline.py

Offline guard. When STANDBAI_OFFLINE=1, outbound network calls are blocked
and only local files under data/ are used.
"""

import os

# Accepted as a fallback for one release (PRD §4.2); remove after the rename settles.
_LEGACY_OFFLINE_VAR = "UDARASIAGA_OFFLINE"


class OfflineGuardException(RuntimeError):
    """Raised when an outbound call is attempted while offline mode is on."""
    pass


def is_offline() -> bool:
    """Return True when offline mode is on. Defaults to online (`0`)."""
    value = os.environ.get("STANDBAI_OFFLINE")
    if value is None:
        value = os.environ.get(_LEGACY_OFFLINE_VAR, "0")
    return value.strip() == "1"


def assert_online_allowed(source_name: str = "external source"):
    """Raise OfflineGuardException if outbound calls are not allowed."""
    if is_offline():
        raise OfflineGuardException(
            f"Network call to {source_name} blocked: STANDBAI_OFFLINE=1. "
            f"Use local data from data/events."
        )
