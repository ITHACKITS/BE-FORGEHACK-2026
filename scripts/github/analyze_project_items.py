import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"

def main():
    p = subprocess.run([GH, "project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100"], capture_output=True, text=True, encoding="utf-8")
    data = json.loads(p.stdout)
    items = data.get("items", [])
    print(f"Total items in Project: {len(items)}")

    # Group by Area and Sprint
    by_area = {}
    by_sprint = {}
    by_pic = {}

    if items:
        print("Sample item keys:", list(items[0].keys()))
        print("Sample item:", json.dumps(items[0], indent=2))


if __name__ == "__main__":
    main()
