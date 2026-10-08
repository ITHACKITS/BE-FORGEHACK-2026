import json
import urllib.request

req = urllib.request.Request(
    'http://127.0.0.1:8000/simulate',
    data=json.dumps({
        'hazard': 'fire',
        'mode': 'auto',
        'source': {'event_id': 'live_kalimantan'},
        'horizon_hours': 48,
        'n_members': 5,
        'seed': 42,
        'thresholds': {'min': 0.9, 'mid': 0.5, 'max': 0.05}
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read())
    run_id = data['run_id']
    print("Run ID:", run_id)

for hour in [0, 6, 12, 24]:
    with urllib.request.urlopen(f'http://127.0.0.1:8000/runs/{run_id}/tiers?t={hour}') as t_res:
        t_data = json.loads(t_res.read())
        features = t_data.get('features', [])
        print(f"Hour {hour}: features count = {len(features)}")
        if features:
            print(" - feature properties:", features[0].get('properties'))

with urllib.request.urlopen(f'http://127.0.0.1:8000/runs/{run_id}/impact') as imp_res:
    imp = json.loads(imp_res.read())
    print("Population exposed median:", imp.get('population_exposed', {}).get('median'))
    print("Area exposed median:", imp.get('area_exposed_km2', {}).get('median'))
