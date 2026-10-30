import json, os, re, sys
import numpy as np
from sentence_transformers import CrossEncoder

NLI_MODEL = os.getenv("NLI_MODEL", "cross-encoder/nli-deberta-v3-base")
TAG = os.getenv("NLI_TAG", "")
nli = CrossEncoder(NLI_MODEL, max_length=512)

_id2 = {int(k): v.lower() for k, v in nli.model.config.id2label.items()}
I_CON = [k for k, v in _id2.items() if v.startswith("contra")][0]
I_ENT = [k for k, v in _id2.items() if v.startswith("entail")][0]
print("NLI label order:", _id2)

T_SUP = 0.5      # entailment needed to call a claim SUPPORTED
T_CON = 0.9      # contradiction needed (in a relevant window) to call it CONTRADICTED
STOP = set("the a an of in on for with and or to is are was were be been has have had that this it its as by from at than".split())

def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3 and w not in STOP}

def overlap(claim, win):
    c = words(claim)
    return len(c & words(win)) / max(1, len(c))

def windows(text, size=2):
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if s.strip()]
    if len(sents) <= size:
        return [" ".join(sents)]
    return [" ".join(sents[i:i + size]) for i in range(len(sents) - size + 1)]

def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def verify(claim, evidence):
    claim = claim.strip()
    if claim and claim[-1] not in ".!?":
        claim += "."          # labels flipped on a missing full stop, so normalise
    wins = [(ci, w) for ci, e in enumerate(evidence, 1) for w in windows(e["text"])]
    probs = softmax(np.asarray(nli.predict([(w, claim) for _, w in wins], batch_size=32)))
    ent, con = probs[:, I_ENT], probs[:, I_CON]
    rel = np.array([overlap(claim, w) >= 0.3 for _, w in wins])
    con_rel = np.where(rel, con, 0.0)
    b = int(ent.argmax())
    if ent[b] >= T_SUP:
        label = "SUPPORTED"
    elif con_rel.max() >= T_CON:
        label, b = "CONTRADICTED", int(con_rel.argmax())
    else:
        label = "INSUFFICIENT"
    return {"label": label, "entail": round(float(ent[b]), 3), "contra": round(float(con_rel.max()), 3),
            "best_chunk": wins[b][0], "window": wins[b][1][:250]}

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "rag"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    answers = {json.loads(l)["id"]: json.loads(l) for l in open("results/answers.jsonl")}
    counts = {"SUPPORTED": 0, "CONTRADICTED": 0, "INSUFFICIENT": 0}
    cite_ok = cite_n = 0
    recs = [json.loads(l) for l in open(f"results/claims_{key}.jsonl")][:limit]
    with open(f"results/verified_{key}{TAG}.jsonl", "w") as out:
        for rec in recs:
            ev = answers[rec["id"]]["evidence"]
            if not ev:
                continue
            for c in rec["claims"]:
                v = verify(c["claim"], ev)
                counts[v["label"]] += 1
                if key == "rag" and v["label"] == "SUPPORTED" and c.get("cites"):
                    cite_n += 1; cite_ok += v["best_chunk"] in c["cites"]
                out.write(json.dumps({"id": rec["id"], **c, **v}) + "\n")
    total = sum(counts.values())
    print(key, counts, "total claims:", total)
    if total:
        print("supported rate:", round(counts["SUPPORTED"] / total, 3),
              "| unsupported rate:", round(1 - counts["SUPPORTED"] / total, 3))
    if cite_n:
        print("supported claims whose best chunk is one they cited:", cite_ok, "/", cite_n)