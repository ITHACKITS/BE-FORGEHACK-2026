import subprocess
import json

query = """
query {
  organization(login: "nyarikerja") {
    projectV2(number: 1) {
      id
      title
      items(first: 50) {
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
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

res = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"], capture_output=True, text=True)
if res.returncode != 0:
    print("Error:", res.stderr)
else:
    data = json.loads(res.stdout)
    items = data["data"]["organization"]["projectV2"]["items"]["nodes"]
    print(f"Total items in Project 1: {len(items)}\n")
    for it in items:
        content = it.get("content") or {}
        num = content.get("number")
        title = content.get("title", "Untitled")
        f_vals = {}
        for f in it.get("fieldValues", {}).get("nodes", []):
            fn = f.get("field", {}).get("name")
            val = f.get("name") or f.get("text") or f.get("date")
            if fn:
                f_vals[fn] = val
        print(f"#{num} | {title} | Status={f_vals.get('Status')} | Priority={f_vals.get('Priority')} | PIC={f_vals.get('PIC')} | Sprint={f_vals.get('Sprint')} | Area={f_vals.get('Area')} | Due={f_vals.get('Due Date')}")
