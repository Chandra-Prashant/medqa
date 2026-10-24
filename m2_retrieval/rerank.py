from sentence_transformers import CrossEncoder
from m2_retrieval.search import retrieve

reranker = CrossEncoder("BAAI/bge-reranker-base", max_length=512)

def retrieve_reranked(q, k_candidates=30, k_final=5):
    cands = retrieve(q, k_candidates)
    scores = reranker.predict([(q, c["text"]) for c in cands])
    for c, s in zip(cands, scores):
        c["rerank_score"] = float(s)
    cands.sort(key=lambda c: c["rerank_score"], reverse=True)
    seen, out = set(), []
    for c in cands:                      # keep best chunk per document
        if c["doc_id"] not in seen:
            seen.add(c["doc_id"])
            out.append(c)
        if len(out) == k_final:
            break
    return out

if __name__ == "__main__":
    for q in ["What is the first-line treatment for type 2 diabetes?",
              "How is hypertension treated in older adults?",
              "How is a broken femur treated?"]:
        print("\nQ:", q)
        for r in retrieve_reranked(q):
            print(round(r["rerank_score"], 2), r["source"], r["text"][:100])