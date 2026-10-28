import json, re, sys, os
from m3_generation.llm import chat, MODEL

SYS = """You split a health answer into atomic factual claims for fact-checking.
Rules:
- Each claim states ONE fact. If a sentence joins two facts with 'and', make two claims.
- Each claim must make sense on its own: name the subject explicitly. Never write 'the same review', 'this study', 'these trials', 'it' or 'they'.
- State the finding directly. Do not write 'the evidence supports', 'studies show' or 'the review found'. For example write 'SGLT2 inhibitors lower the risk of kidney failure in type 2 diabetes', not 'The review found that SGLT2 inhibitors lower the risk of kidney failure'.
- Keep numbers, units and population details exactly as in the answer.
- Skip advice (for example 'see a doctor') and hedged statements that make no factual claim.
- Copy the citation numbers that follow the claim in the answer into "cites" (empty list if none).
- Output ONLY a JSON list like [{"claim": "...", "cites": [1, 2]}] with no other text."""

ABSTAIN = "does not contain enough information"

def parse(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)

def extract(answer):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": answer}]
    model = os.getenv("EXTRACT_MODEL") or MODEL
    effort = "low" if "gpt-oss" in model else None
    for temp in (0.0, 0.3):          # the second try uses a different cache key
        raw = chat(msgs, temperature=temp, max_tokens=1500, model=model, effort=effort)
        try:
            return parse(raw)
        except Exception:
            continue
    raise ValueError("could not parse claims")

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "rag"      # "rag" or "llm_only"
    n_ok = n_bad = 0
    with open(f"results/claims_{key}.jsonl", "w") as out:
        for line in open("results/answers.jsonl"):
            r = json.loads(line)
            if key == "rag" and ABSTAIN in r["rag"]:
                continue
            try:
                claims = extract(r[key]); n_ok += 1
            except Exception as e:
                print("parse failed for", r["id"], e); claims = []; n_bad += 1
            out.write(json.dumps({"id": r["id"], "system": key, "claims": claims}) + "\n")
    print(f"{key}: extracted for {n_ok} answers, {n_bad} failed")