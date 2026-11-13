import json

with open("results/coherence_audit_raw.json", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    print(f"=== Page {item['page']}: {item['title']} ===")
    print(f"CHUNK A (len {item['chunk_a_len']}): {item['chunk_a'][:150]}...")
    print(f"CHUNK B (len {item['chunk_b_len']}): {item['chunk_b'][:150]}...")
    print()
