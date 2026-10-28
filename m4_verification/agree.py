import csv
from collections import Counter
m = {"S": "SUPPORTED", "I": "INSUFFICIENT", "C": "CONTRADICTED"}
rows = [r for r in csv.DictReader(open("results/manual_check.csv")) if r["human_label (S/I/C)"].strip()]
pairs = Counter((r["auto_label"], m[r["human_label (S/I/C)"].strip().upper()]) for r in rows)
agree = sum(v for (a, h), v in pairs.items() if a == h)
print(f"agreement: {agree}/{len(rows)}")
for (a, h), v in sorted(pairs.items()):
    print(f"  verifier={a:13s} human={h:13s} {v}")