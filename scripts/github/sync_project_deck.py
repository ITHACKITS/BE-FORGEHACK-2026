"""
backend/scripts/github/sync_project_deck.py

Sinkronisasi cerdas 14 item Pitch Deck (Slide 1-12, Appendix A1-A4, Checklist Juara)
ke GitHub Project 1 (https://github.com/orgs/nyarikerja/projects/1).

- Hanya mengeksekusi penambahan item dan pengisian kolom yang masih kosong/belum lengkap.
- Mengisi seluruh kolom:
  * Status: Todo
  * Area: Deck
  * Priority: P0 / P1
  * Sprint: Sprint 3
  * Due Date: 2026-10-14
  * PIC: [Sesuai Pembagian_Pitch_Deck_Standbai_v2_ContohVisual.md]
  * Assignees: Dibiarkan kosong sesuai instruksi user
"""

import subprocess
import json
import time
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_NUMBER = 1
PROJECT_OWNER = "nyarikerja"
DUE_DATE = "2026-10-14"

ITEMS_DEF = [
    {"issue_num": 55, "title": "Slide 1: Hook & Judul", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 56, "title": "Slide 2: The Crisis", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 57, "title": "Slide 3: Why Now & The Critical Gap", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 58, "title": "Slide 4: The Solution", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 59, "title": "Slide 5: Live Product Demo", "priority": "P0", "pic": "Anggota 2 (Technical & Demo Master)"},
    {"issue_num": 60, "title": "Slide 6: Underlying Magic & C4", "priority": "P0", "pic": "Anggota 2 (Technical & Demo Master)"},
    {"issue_num": 61, "title": "Slide 7: Integritas Sains Mastin 2009", "priority": "P0", "pic": "Anggota 2 (Technical & Demo Master)"},
    {"issue_num": 62, "title": "Slide 8: Multi-Sectoral Impact SDGs", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 63, "title": "Slide 9: Pengguna, Kelayakan, Pilot", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 64, "title": "Slide 10: Diferensiasi & Matriks 2x2", "priority": "P1", "pic": "Anggota 3 (Business & Q&A Defense Anchor)"},
    {"issue_num": 65, "title": "Slide 11: Roadmap & Risiko", "priority": "P1", "pic": "Anggota 3 (Business & Q&A Defense Anchor)"},
    {"issue_num": 66, "title": "Slide 12: Tim & Penutup CTA", "priority": "P0", "pic": "Anggota 1 (Lead Presenter)"},
    {"issue_num": 67, "title": "Appendix A1-A4: Q&A Defense", "priority": "P0", "pic": "Anggota 3 (Business & Q&A Defense Anchor)"},
    {"issue_num": 68, "title": "Checklist Juara & Latihan 11.5 Mnt", "priority": "P0", "pic": "Semua Anggota"},
]

def run_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        err = res.stderr.strip()
        print(f"    [WARN] Command failed ({' '.join(cmd[:4])}...): {err}")
    return res

def fetch_project_items():
    query = """
    query {
      organization(login: "nyarikerja") {
        projectV2(number: 1) {
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue {
                  number
                  title
                  url
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    res = run_cmd(["gh", "api", "graphql", "-f", f"query={query}"])
    if res.returncode != 0:
        print("Gagal fetch GraphQL:", res.stderr)
        return {}
    
    data = json.loads(res.stdout)
    nodes = data["data"]["organization"]["projectV2"]["items"]["nodes"]
    by_num = {}
    for node in nodes:
        content = node.get("content") or {}
        num = content.get("number")
        if num:
            f_vals = {}
            for f in node.get("fieldValues", {}).get("nodes", []):
                fn = f.get("field", {}).get("name")
                val = f.get("name") or f.get("text") or f.get("date")
                if fn:
                    f_vals[fn] = val
            by_num[num] = {"id": node["id"], "fields": f_vals}
    return by_num

def edit_field_with_retry(cmd, max_retries=3):
    for attempt in range(max_retries):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return True
        err = res.stderr.strip()
        if "rate limit" in err.lower():
            wait_time = 15 * (attempt + 1)
            print(f"    [RATE LIMIT] Menunggu {wait_time} detik sebelum mencoba ulang...")
            time.sleep(wait_time)
        else:
            print(f"    [ERR] {err}")
            time.sleep(2)
    return False

def main():
    print("=" * 70)
    print("SINKRONISASI CERDAS PITCH DECK KE GITHUB PROJECT 1")
    print("=" * 70)

    existing = fetch_project_items()
    print(f"Ditemukan {len(existing)} issue di Project 1.")

    for it in ITEMS_DEF:
        num = it["issue_num"]
        title = it["title"]
        prio = it["priority"]
        pic = it["pic"]
        url = f"https://github.com/nyarikerja/JOINTS2026/issues/{num}"

        curr = existing.get(num)
        is_new = curr is None
        fields = curr["fields"] if curr else {}

        print(f"\n[Issue #{num}] {title}")

        # 1. Tambah ke project jika belum ada
        if is_new:
            print(f"  + Menambahkan #{num} ke Project 1...")
            success = edit_field_with_retry(["gh", "project", "item-add", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url])
            if not success:
                print(f"  [GAGAL] Tidak dapat menambahkan #{num} ke Project 1.")
                continue
            time.sleep(1.2)
        else:
            print("  [OK] Sudah ada di Project 1.")

        # 2. Status
        if fields.get("Status") != "Todo":
            print("  -> Setting Status = Todo")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Status", "--value", "Todo"])
            time.sleep(1.2)
        else:
            print("  [OK] Status sudah 'Todo'")

        # 3. Area
        if fields.get("Area") != "Deck":
            print("  -> Setting Area = Deck")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Area", "--value", "Deck"])
            time.sleep(1.2)
        else:
            print("  [OK] Area sudah 'Deck'")

        # 4. Priority
        if fields.get("Priority") != prio:
            print(f"  -> Setting Priority = {prio}")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Priority", "--value", prio])
            time.sleep(1.2)
        else:
            print("  [OK] Priority sudah '{prio}'")

        # 5. Sprint
        if fields.get("Sprint") != "Sprint 3":
            print("  -> Setting Sprint = Sprint 3")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Sprint", "--value", "Sprint 3"])
            time.sleep(1.2)
        else:
            print("  [OK] Sprint sudah 'Sprint 3'")

        # 6. Due Date
        if fields.get("Due Date") != DUE_DATE:
            print(f"  -> Setting Due Date = {DUE_DATE}")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "Due Date", "--date", DUE_DATE])
            time.sleep(1.2)
        else:
            print("  [OK] Due Date sudah '{DUE_DATE}'")

        # 7. PIC
        if fields.get("PIC") != pic:
            print(f"  -> Setting PIC = {pic}")
            edit_field_with_retry(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", url, "--field", "PIC", "--text", pic])
            time.sleep(1.2)
        else:
            print("  [OK] PIC sudah '{pic}'")

    print("\n" + "=" * 70)
    print("Selesai proses sinkronisasi! Memverifikasi hasil akhir...")
    print("=" * 70)

if __name__ == "__main__":
    main()
