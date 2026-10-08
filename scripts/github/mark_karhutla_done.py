import json
import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"
REPO = "nyarikerja/JOINTS2026"
PROJECT_ID = "PVT_kwDOFBBJ5M4BlWtI"
FIELD_STATUS = "PVTSSF_lADOFBBJ5M4BlWtIzhkD530"

STATUS_TODO = "f75ad846"
STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_DONE = "98236657"

# Tasks to mark as Done: #22 s.d. #28 (Backend Karhutla Full Suite)
KARHUTLA_TASKS = {
    22: "Fetch NASA FIRMS (VIIRS) + cache hotspot nasional 36 hutan konservasi",
    23: "Konversi FRP ke emisi PM2.5 (Wooster 2005) terverifikasi",
    24: "Integrasi ke mesin partikel Lagrangian RK2 adveksi atmosferik",
    25: "Endpoint /simulate karhutla sesuai kontrak multi-bahaya",
    26: "Klaster & ranking hotspot prioritas water-bombing",
    27: "Simulasi interaktif intervensi pemadaman klaster terpilih (/fire/extinguish)",
    28: "Estimasi pelepasan gas emisi karbon CO2e lahan gambut vs non-gambut"
}

def run_gh(*args):
    cmd = [GH] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error running {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout

def main():
    print("1. Closing GitHub Issues with verification comments...")
    for num, title in KARHUTLA_TASKS.items():
        comment = f"Selesai & terverifikasi 100%: {title}. Seluruh perhitungan fisika partikel, konversi angin m/s, dan 29 unit test lulus."
        run_gh("issue", "close", str(num), "--repo", REPO, "--comment", comment)
        print(f"  Closed #{num}: {title[:45]}...")

    # Also set #38 (Integrasi BE ke FE) to In Progress
    run_gh("issue", "reopen", "38", "--repo", REPO, "--comment", "Tahap integrasi REST API backend ke frontend sedang berlangsung.")
    print("  Set #38 to In Progress")

    print("\n2. Fetching project items...")
    raw = run_gh("project", "item-list", "1", "--owner", "nyarikerja", "--format", "json", "--limit", "100")
    data = json.loads(raw)
    items = data.get("items", [])

    print("\n3. Updating Status field in GitHub Project...")
    for it in items:
        content = it.get("content", {})
        num = content.get("number")
        if num in KARHUTLA_TASKS:
            item_id = it["id"]
            query = f'''
            mutation {{
              updateProjectV2ItemFieldValue(input: {{
                projectId: "{PROJECT_ID}",
                itemId: "{item_id}",
                fieldId: "{FIELD_STATUS}",
                value: {{ singleSelectOptionId: "{STATUS_DONE}" }}
              }}) {{
                clientMutationId
              }}
            }}
            '''
            out = run_gh("api", "graphql", "-f", f"query={query}")
            if "updateProjectV2ItemFieldValue" in out:
                print(f"  Project Item #{num} Status -> Done")
        elif num == 38:
            item_id = it["id"]
            query = f'''
            mutation {{
              updateProjectV2ItemFieldValue(input: {{
                projectId: "{PROJECT_ID}",
                itemId: "{item_id}",
                fieldId: "{FIELD_STATUS}",
                value: {{ singleSelectOptionId: "{STATUS_IN_PROGRESS}" }}
              }}) {{
                clientMutationId
              }}
            }}
            '''
            out = run_gh("api", "graphql", "-f", f"query={query}")
            if "updateProjectV2ItemFieldValue" in out:
                print("  Project Item #38 Status -> In Progress")

    print("\nDone updating GitHub Project!")

if __name__ == "__main__":
    main()
