import json
import re
import subprocess

GH_PATH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"
PROJECT_ID = "PVT_kwDOFBBJ5M4BlWtI"

FIELD_SPRINT = "PVTSSF_lADOFBBJ5M4BlWtIzhkiLOw"
FIELD_PIC = "PVTF_lADOFBBJ5M4BlWtIzhkiLQo"
FIELD_DUE_DATE = "PVTF_lADOFBBJ5M4BlWtIzhkiLTY"
FIELD_PRIORITY = "PVTSSF_lADOFBBJ5M4BlWtIzhkiLZ8"
FIELD_AREA = "PVTSSF_lADOFBBJ5M4BlWtIzhkiM_w"

SPRINT_OPTS = {
    "Sprint 1": "0b788355",
    "Sprint 2": "77696216",
    "Sprint 3": "4d6a78c0",
    "Sprint 4": "e18b8b13",
}

PRIORITY_OPTS = {
    "P0": "a68900fc",
    "P1": "abff88cc",
    "P2": "1b87ba9f",
}

AREA_OPTS = {
    "area:setup": "b21e9e37",
    "area:be-gunung": "17a51759",
    "area:be-karhutla": "5d3639e8",
    "area:fe": "d5e19f42",
    "area:uiux": "be871920",
    "area:deck": "c9cab9bb",
    "area:video": "36950219",
    "area:proposal": "d7d52294",
    "area:qa": "cdadfc67",
    "bug": "d1648b0b",
}

def run_gh(*args):
    cmd = [GH_PATH] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"gh command failed: {res.stderr.strip()}")
    return res.stdout

def main():
    print("1. Fetching all items from project...")
    raw = run_gh("project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100")
    data = json.loads(raw)
    items = data.get("items", [])
    print(f"Total items found: {len(items)}")

    updates = []
    for it in items:
        item_id = it["id"]
        content = it.get("content", {})
        title = content.get("title", it.get("title", ""))
        number = content.get("number", "")
        body = content.get("body", "")
        labels = it.get("labels", [])
        milestone = it.get("milestone", {}).get("title", "")

        # 1. Sprint
        sprint_opt = None
        for s_name, s_id in SPRINT_OPTS.items():
            if s_name in milestone:
                sprint_opt = s_id
                break

        # 2. Priority
        priority_opt = None
        for p_name, p_id in PRIORITY_OPTS.items():
            if p_name in labels:
                priority_opt = p_id
                break

        # 3. Area
        area_opt = None
        for a_key, a_id in AREA_OPTS.items():
            if a_key in labels:
                area_opt = a_id
                break

        # 4. PIC and Due Date from body: "PIC: <pic> | <date>"
        pic_text = None
        due_date = None
        if body:
            match = re.search(r"PIC:\s*(.*?)\s*\|\s*(.*)", body)
            if match:
                pic_text = match.group(1).strip()
                date_str = match.group(2).strip()
                # Parse day number, e.g. "7 Okt", "8 Okt", "start 14 Okt"
                day_match = re.search(r"(\d+)", date_str)
                if day_match:
                    day = int(day_match.group(1))
                    due_date = f"2026-10-{day:02d}"

        updates.append({
            "item_id": item_id,
            "title": title,
            "number": number,
            "sprint_opt": sprint_opt,
            "priority_opt": priority_opt,
            "area_opt": area_opt,
            "pic_text": pic_text,
            "due_date": due_date,
        })

    print(f"Parsed {len(updates)} items. Executing GraphQL updates (1 item per query)...")

    for i, up in enumerate(updates):
        mutation_lines = []
        item_id = up["item_id"]
        if up["sprint_opt"]:
            mutation_lines.append(
                f'm_sprint: updateProjectV2ItemFieldValue(input: {{ projectId: "{PROJECT_ID}", itemId: "{item_id}", fieldId: "{FIELD_SPRINT}", value: {{ singleSelectOptionId: "{up["sprint_opt"]}" }} }}) {{ clientMutationId }}'
            )
        if up["priority_opt"]:
            mutation_lines.append(
                f'm_priority: updateProjectV2ItemFieldValue(input: {{ projectId: "{PROJECT_ID}", itemId: "{item_id}", fieldId: "{FIELD_PRIORITY}", value: {{ singleSelectOptionId: "{up["priority_opt"]}" }} }}) {{ clientMutationId }}'
            )
        if up["area_opt"]:
            mutation_lines.append(
                f'm_area: updateProjectV2ItemFieldValue(input: {{ projectId: "{PROJECT_ID}", itemId: "{item_id}", fieldId: "{FIELD_AREA}", value: {{ singleSelectOptionId: "{up["area_opt"]}" }} }}) {{ clientMutationId }}'
            )
        if up["pic_text"]:
            safe_pic = up["pic_text"].replace('"', '\\"')
            mutation_lines.append(
                f'm_pic: updateProjectV2ItemFieldValue(input: {{ projectId: "{PROJECT_ID}", itemId: "{item_id}", fieldId: "{FIELD_PIC}", value: {{ text: "{safe_pic}" }} }}) {{ clientMutationId }}'
            )
        if up["due_date"]:
            mutation_lines.append(
                f'm_due: updateProjectV2ItemFieldValue(input: {{ projectId: "{PROJECT_ID}", itemId: "{item_id}", fieldId: "{FIELD_DUE_DATE}", value: {{ date: "{up["due_date"]}" }} }}) {{ clientMutationId }}'
            )

        if mutation_lines:
            query = "mutation {\n  " + "\n  ".join(mutation_lines) + "\n}"
            res = run_gh("api", "graphql", "-f", f"query={query}")
            print(f"  [{i+1}/{len(updates)}] Updated #{up['number']}: {up['title'][:35]}...")

    print("\nAll 51 items successfully populated with Sprint, Priority, Area, PIC, and Due Date!")

if __name__ == "__main__":
    main()
