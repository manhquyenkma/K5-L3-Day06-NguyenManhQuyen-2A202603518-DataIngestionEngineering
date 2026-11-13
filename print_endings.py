import json

with open("results/coherence_audit_raw.json", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    print(f"Page {item['page']}:")
    print(f"  CHUNK A (ends at): ...{repr(item['chunk_a'][-60:])}")
    print(f"  CHUNK B (ends at): ...{repr(item['chunk_b'][-60:])}")
    print()
