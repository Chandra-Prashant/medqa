import csv, os
from collections import Counter
from m4_verification.verify import verify, NLI_MODEL

m = {"S": "SUPPORTED", "I": "INSUFFICIENT", "C": "CONTRADICTED"}
rows = [r for r in csv.DictReader(open("results/manual_check.csv")) if r["human_label (S/I/C)"].strip()]
conf, ok = Counter(), 0
for r in rows:
    ev = [{"text": t} for t in r["all_evidence"].split(" || ")]
    pred = verify(r["claim"], ev)["label"]
    human = m[r["human_label (S/I/C)"].strip().upper()]
    ok += pred == human
    conf[(pred, human)] += 1
print(NLI_MODEL, f"| agreement {ok}/{len(rows)}")
for (p, h), v in sorted(conf.items()):
    print(f"  verifier={p:13s} human={h:13s} {v}")