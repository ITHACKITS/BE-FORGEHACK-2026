import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"
REPO = "nyarikerja/JOINTS2026"
PROJECT_ID = "PVT_kwDOFBBJ5M4BlWtI"
FIELD_STATUS = "PVTSSF_lADOFBBJ5M4BlWtIzhkD530"

STATUS_TODO = "f75ad846"
STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_DONE = "98236657"

TARGETS = {
    1: STATUS_IN_PROGRESS,
    22: STATUS_IN_PROGRESS,
    23: STATUS_IN_PROGRESS,
    24: STATUS_IN_PROGRESS,
    25: STATUS_IN_PROGRESS,
    26: STATUS_IN_PROGRESS,
    27: STATUS_IN_PROGRESS,
    28: STATUS_IN_PROGRESS,
    39: STATUS_TODO,
}

def run_gh(*args):
    cmd = [GH] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error running {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout

def main():
    print("1. Reopening issues on GitHub...")
    for num in TARGETS:
        run_gh("issue", "reopen", str(num), "--repo", REPO)
        print(f"  Reopened #{num}")

    print("\n2. Fetching project items...")
    raw = run_gh("project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100")
    data = json.loads(raw)
    items = data.get("items", [])

    print("\n3. Updating Status field in Project...")
    for it in items:
        num = it.get("content", {}).get("number")
        if num in TARGETS:
            item_id = it["id"]
            desired_status = TARGETS[num]
            query = f'''
            mutation {{
              updateProjectV2ItemFieldValue(input: {{
                projectId: "{PROJECT_ID}",
                itemId: "{item_id}",
                fieldId: "{FIELD_STATUS}",
                value: {{ singleSelectOptionId: "{desired_status}" }}
              }}) {{
                clientMutationId
              }}
            }}
            '''
            run_gh("api", "graphql", "-f", f"query={query}")
            status_name = "In Progress" if desired_status == STATUS_IN_PROGRESS else "Todo"
            print(f"  Updated #{num} in Project to: {status_name}")

    print("\nSuccessfully adjusted all 9 tasks!")

if __name__ == "__main__":
    main()
