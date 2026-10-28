import json, sys
from pathlib import Path
from tqdm import tqdm
from m2_retrieval.rerank import retrieve_reranked
from m3_generation.llm import chat, MODEL

MIN_SCORE = 0.05   # drop evidence the reranker scores as irrelevant
ABSTAIN = "The provided evidence does not contain enough information to answer this question."

SYS_LLM = ("You are a careful health information assistant. Answer the question in under 150 words. "
           "Do not give a diagnosis or personal medical advice.")
SYS_RAG = ("You are a careful health information assistant. Answer the question using ONLY the numbered "
           "evidence provided.\n"
           "- Every factual sentence must end with citation(s) such as [1] or [2][3] matching the evidence numbers.\n"
           "- Do not use outside knowledge.\n"
           f"- If the evidence does not answer the question, reply exactly: \"{ABSTAIN}\"\n"
           "- Do not give a diagnosis or personal medical advice. Keep the answer under 150 words.")

def llm_only(q):
    return chat([{"role": "system", "content": SYS_LLM}, {"role": "user", "content": q}])

def rag(q, evidence):
    if not evidence:
        return ABSTAIN
    ev = "\n\n".join(f"[{i+1}] (PubMed:{e['doc_id']}) {e['text']}" for i, e in enumerate(evidence))
    return chat([{"role": "system", "content": SYS_RAG},
                 {"role": "user", "content": f"Evidence:\n{ev}\n\nQuestion: {q}"}])

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    qs = [json.loads(l) for l in open("configs/questions.jsonl")][:limit]
    Path("results").mkdir(exist_ok=True)
    with open("results/answers.jsonl", "w") as out:
        for item in tqdm(qs):
            ret = retrieve_reranked(item["question"], k_final=5)
            ev = [e for e in ret if e["rerank_score"] >= MIN_SCORE]
            rec = {**item, "model": MODEL,
                   "llm_only": llm_only(item["question"]),
                   "rag": rag(item["question"], ev),
                   "evidence": [{"doc_id": e["doc_id"], "source": e["source"],
                                 "rerank_score": round(e["rerank_score"], 3), "text": e["text"]} for e in ev],
                   "top_rerank_score": round(ret[0]["rerank_score"], 3) if ret else None}
            out.write(json.dumps(rec) + "\n")