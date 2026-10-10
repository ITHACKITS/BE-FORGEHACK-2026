"""
scripts/generators/snapshot_wind_grid.py

Download the national wind grid (16-day Open-Meteo forecast, 2° grid) and store it as
data/layers/wind_grid_snapshot.json, which /layers/wind and /layers/smoke-paths use
when STANDBAI_OFFLINE=1 or when Open-Meteo is unreachable.

Usage:
    python scripts/generators/snapshot_wind_grid.py            # writes the snapshot file
    python scripts/generators/snapshot_wind_grid.py --stdout   # prints JSON (e.g. from a container)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.offline import assert_online_allowed  # noqa: E402
from app.services import weather_grid  # noqa: E402


def main() -> None:
    assert_online_allowed("Open-Meteo wind grid snapshot")
    data = weather_grid.fetch_grid()
    if "--stdout" in sys.argv:
        sys.stdout.write(json.dumps(data, separators=(",", ":")))
        return
    weather_grid.save_snapshot(data)
    print(
        f"Saved {weather_grid.SNAPSHOT_FILE} ({len(data['times'])} steps, "
        f"{data['grid']['nlat']}x{data['grid']['nlon']} points, fetched {data['fetched_at']})"
    )


if __name__ == "__main__":
    main()
