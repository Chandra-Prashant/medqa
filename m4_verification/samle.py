import csv, json, random
random.seed(0)
pick= []
answers = {json.loads(l)["id"]: json.loads(l) for l in open("results/answers.jsonl")}
rows = [json.loads(l) for l in open("results/verified_rag.jsonl")]
sizes = {"SUPPORTED": 10, "INSUFFICIENT": 20, "CONTRADICTED": 10}
for lab, n in sizes.items():
    g = [r for r in rows if r["label"] == lab]
    pick += random.sample(g, min(n, len(g)))
with open("results/manual_check.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "claim", "auto_label", "verifier_window", "all_evidence", "human_label (S/I/C)"])
    for r in pick:
        ev = " || ".join(e["text"] for e in answers[r["id"]]["evidence"])
        w.writerow([r["id"], r["claim"], r["label"], r["window"], ev, ""])
print(len(pick), "rows written to results/manual_check.csv")