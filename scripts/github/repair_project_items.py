"""
scripts/github/repair_project_items.py

Memastikan issue #63, #64, #65 terdaftar sempurna di Project 1
dengan kolom: Status=Todo, Area=Deck, Priority=P0/P1, Sprint=Sprint 3, Due Date=2026-10-14, PIC=...
"""

import subprocess
import time

PROJECT_NUMBER = 1
PROJECT_OWNER = "nyarikerja"

REPAIRS = [
    {
        "url": "https://github.com/nyarikerja/JOINTS2026/issues/63",
        "priority": "P0",
        "pic": "Anggota 1 (Lead Presenter)"
    },
    {
        "url": "https://github.com/nyarikerja/JOINTS2026/issues/64",
        "priority": "P1",
        "pic": "Anggota 3 (Business & Q&A Defense Anchor)"
    },
    {
        "url": "https://github.com/nyarikerja/JOINTS2026/issues/65",
        "priority": "P1",
        "pic": "Anggota 3 (Business & Q&A Defense Anchor)"
    }
]

for r in REPAIRS:
    url = r["url"]
    prio = r["priority"]
    pic = r["pic"]
    print(f"Repairing {url}...")
    subprocess.run(["gh", "project", "item-add", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url], capture_output=True)
    time.sleep(1)
    for field, val in [("Status", "Todo"), ("Area", "Deck"), ("Priority", prio), ("Sprint", "Sprint 3")]:
        subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", field, "--value", val], capture_output=True)
        time.sleep(1)
    subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Due Date", "--date", "2026-10-14"], capture_output=True)
    time.sleep(1)
    subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "PIC", "--text", pic], capture_output=True)
    time.sleep(1)
    print(f"Done repairing {url}!")

print("All repairs complete!")
