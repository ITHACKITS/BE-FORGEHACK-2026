import subprocess
import json

for num in range(55, 70):
    res = subprocess.run(["gh", "api", f"repos/nyarikerja/JOINTS2026/issues/{num}"], capture_output=True, text=True)
    if res.returncode == 0:
        d = json.loads(res.stdout)
        print(f"#{num}: {d.get('title')}")
    else:
        print(f"#{num}: Not found ({res.stderr.strip()})")
