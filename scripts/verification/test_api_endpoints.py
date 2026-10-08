import json
import urllib.request


def get(path):
    with urllib.request.urlopen(f'http://127.0.0.1:8000{path}') as res:
        return json.loads(res.read())

def post(path, data=None):
    req = urllib.request.Request(
        f'http://127.0.0.1:8000{path}',
        data=json.dumps(data).encode() if data else b'{}',
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

print("=== 1. SYNC LIVE ===")
sync = post('/layers/sync-live')
print("Sync status:", sync.get('status'), "| Latency ms:", sync.get('latency_ms'), "| Timestamp:", sync.get('timestamp'))

print("\n=== 2. SUMMARY KPI ===")
kpi = get('/layers/summary-kpi')
print("Volcanoes total:", kpi.get('volcanoes_monitored_total'), "| Status counts:", kpi.get('status_counts'))

print("\n=== 3. SIMULATE POST /simulate ===")
payload = {
    'hazard': 'volcano',
    'mode': 'auto',
    'source': {'event_id': 'anak_krakatau_2026_09'},
    'horizon_hours': 48,
    'n_members': 5,
    'seed': 42,
    'thresholds': {'min': 0.9, 'mid': 0.5, 'max': 0.05}
}
sim = post('/simulate', payload)
run_id = sim['run_id']
print("Run ID:", run_id, "| Scenario:", sim.get('scenario_label'))
print("Disclaimer:", sim.get('disclaimer'))

print("\n=== 4. IMPACT RANGES ===")
impact = get(f'/runs/{run_id}/impact')
print("Population exposed median:", impact['population_exposed']['median'])
print("Schools exposed median:", impact['schools_exposed']['median'])
print("Healthcare exposed median:", impact['healthcare_exposed']['median'])

print("\n=== 5. FACILITIES IMPACTED ===")
fac = get(f'/runs/{run_id}/facilities-impacted')
print("Schools count:", fac.get('total_schools_exposed'), "| Hospitals count:", fac.get('total_hospitals_exposed'))
for s in fac.get('schools', [])[:2]:
    print(f" - {s['name']} ({s['district']}): Prob={s['exposure_probability']:.0%} | ETA={s['estimated_arrival_hr']}h | Rec={s['operational_recommendation'][:45]}...")

print("\n=== 6. HEALTH & MASK GUIDANCE ===")
health = get(f'/runs/{run_id}/health-guidance')
print("Required Mask:", health['mask_guidance']['required_mask_type'])
print("Surgical Mask Warning:", health['mask_guidance']['surgical_mask_warning'][:70])
print("Eye Safety Contact Lens Warning:", health['eye_safety']['softlens_warning'][:70])
