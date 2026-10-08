import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"

def main():
    p = subprocess.run([GH, "project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100"], capture_output=True, text=True, encoding="utf-8")
    data = json.loads(p.stdout)
    items = data.get("items", [])

    done_items = []
    for it in items:
        if it.get("status") == "Done":
            c = it.get("content", {})
            done_items.append({
                "number": c.get("number"),
                "title": c.get("title", it.get("title")),
                "area": it.get("area"),
                "sprint": it.get("sprint"),
                "pic": it.get("pIC"),
                "due": it.get("due Date"),
                "body": c.get("body", "")
            })

    # Sort by issue number
    done_items.sort(key=lambda x: (x["number"] or 0))
    print(f"Total Done items: {len(done_items)}")
    for d in done_items:
        print(f"#{d['number']:<2} | [{d['area']}] | [{d['sprint']}] | {d['title']} | PIC: {d['pic']} | Due: {d['due']}")

if __name__ == "__main__":
    main()
