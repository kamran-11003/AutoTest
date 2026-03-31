import json

d = json.load(open('data/generated_tests/site3_register_after_20260401_021901.json', encoding='utf-8'))
bva = d['test_results']['test_cases']['bva']

print("=== BVA structure sample ===")
if bva:
    print(json.dumps(bva[0], indent=2)[:500])
    print("\n--- Keys:", list(bva[0].keys()))

print("\n=== ALL BVA with 'email' in any key ===")
for t in bva:
    tid = t.get('test_id') or t.get('id') or t.get('name') or str(t.keys())
    target = t.get('target_field') or t.get('field') or t.get('field_name') or ''
    if 'email' in str(tid).lower() or 'email' in str(target).lower():
        print(json.dumps(t, indent=2)[:600])
        print("---")
