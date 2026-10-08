import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"
REPO = "nyarikerja/JOINTS2026"
PROJECT_ID = "PVT_kwDOFBBJ5M4BlWtI"
FIELD_STATUS = "PVTSSF_lADOFBBJ5M4BlWtIzhkD530"

STATUS_TODO = "f75ad846"
STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_DONE = "98236657"

# Issues to adjust:
# #44 -> Todo
# #50 -> Todo
# #51 -> Todo
# #38 -> Todo (or In Progress)
TARGETS = {
    44: STATUS_TODO,
    50: STATUS_TODO,
    51: STATUS_TODO,
    38: STATUS_TODO,
}

def run_gh(*args):
    cmd = [GH] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error running {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout

def main():
    print("1. Reopening issues on GitHub...")
    for issue_num in TARGETS:
        out = run_gh("issue", "reopen", str(issue_num), "--repo", REPO)
        print(f"  Reopened #{issue_num}: {out.strip()}")

    print("\n2. Fetching items from project...")
    raw = run_gh("project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100")
    data = json.loads(raw)
    items = data.get("items", [])

    print("\n3. Updating Status field in GitHub Project...")
    for it in items:
        content = it.get("content", {})
        num = content.get("number")
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
            out = run_gh("api", "graphql", "-f", f"query={query}")
            status_name = "Todo" if desired_status == STATUS_TODO else "In Progress"
            print(f"  Updated #{num} in Project to: {status_name}")

    print("\nFinished successfully!")

if __name__ == "__main__":
    main()
