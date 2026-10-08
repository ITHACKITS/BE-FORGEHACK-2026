import subprocess

GH = r"C:\Users\arya4\AppData\Local\Microsoft\WinGet\Links\gh.exe"

def run_graphql(mutation):
    cmd = [GH, "api", "graphql", "-f", f"query={mutation}"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print("ERR:", res.stderr)
    return res.stdout

# 1. Update Sprint colors
mut_sprint = """
mutation {
  updateProjectV2Field(input: {
    fieldId: "PVTSSF_lADOFBBJ5M4BlWtIzhkiLOw"
    singleSelectOptions: [
      { id: "0b788355", name: "Sprint 1", color: BLUE, description: "Fondasi & Desain" },
      { id: "77696216", name: "Sprint 2", color: PURPLE, description: "Pengembangan Inti" },
      { id: "4d6a78c0", name: "Sprint 3", color: GREEN, description: "Integrasi & QA" },
      { id: "e18b8b13", name: "Sprint 4", color: PINK, description: "Buffer & Submit" }
    ]
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        name
        options { id name color }
      }
    }
  }
}
"""
print("Updating Sprint...")
print(run_graphql(mut_sprint))

# 2. Update Area colors
mut_area = """
mutation {
  updateProjectV2Field(input: {
    fieldId: "PVTSSF_lADOFBBJ5M4BlWtIzhkiM_w"
    singleSelectOptions: [
      { id: "b21e9e37", name: "Setup", color: GRAY, description: "Repositori & Konfigurasi Awal" },
      { id: "17a51759", name: "BE Gunung", color: RED, description: "Backend Simulasi Erupsi Gunung Api" },
      { id: "5d3639e8", name: "BE Karhutla", color: ORANGE, description: "Backend Simulasi Karhutla & FIRMS" },
      { id: "d5e19f42", name: "FE", color: BLUE, description: "Frontend Aplikasi Web" },
      { id: "be871920", name: "UI/UX", color: PURPLE, description: "Desain Antarmuka & Prototipe" },
      { id: "c9cab9bb", name: "Deck", color: YELLOW, description: "Pitch Deck Presentasi" },
      { id: "36950219", name: "Video", color: PINK, description: "Video Demonstrasi YouTube" },
      { id: "d7d52294", name: "Proposal", color: GREEN, description: "Proposal Solusi JOINTS 2026" },
      { id: "cdadfc67", name: "QA", color: BLUE, description: "Quality Assurance & Uji Validasi" },
      { id: "d1648b0b", name: "Bug", color: RED, description: "Perbaikan Bug & Error" }
    ]
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        name
        options { id name color }
      }
    }
  }
}
"""
print("Updating Area...")
print(run_graphql(mut_area))
print("All field colors updated successfully!")
