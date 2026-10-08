import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"

def main():
    p = subprocess.run([GH, "project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100"], capture_output=True, text=True, encoding="utf-8")
    data = json.loads(p.stdout)
    items = data.get("items", [])

    status_summary = {}
    print(f"{'#':<4} | {'Status':<12} | {'Area':<12} | {'Sprint':<10} | {'Title'}")
    print("-" * 80)
    for it in items:
        num = it.get("content", {}).get("number", "?")
        title = it.get("content", {}).get("title", it.get("title", ""))
        status = it.get("status", "No Status")
        area = it.get("area", "")
        sprint = it.get("sprint", "")
        status_summary[status] = status_summary.get(status, 0) + 1
        print(f"#{num:<3} | {status:<12} | {area:<12} | {sprint:<10} | {title[:40]}")

    print("\nSummary status count:", status_summary)

if __name__ == "__main__":
    main()
