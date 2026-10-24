import pickle, faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
index = faiss.read_index("data/processed/index.faiss")
chunks = pickle.load(open("data/processed/chunks.pkl", "rb"))
PREFIX = "Represent this sentence for searching relevant passages: "

def retrieve(q, k=10):
    qe = model.encode([PREFIX + q], normalize_embeddings=True)
    scores, ids = index.search(qe, k)
    return [{**chunks[i], "score": float(s)} for s, i in zip(scores[0], ids[0])]

if __name__ == "__main__":
    for r in retrieve("What is the first-line treatment for type 2 diabetes?", 5):
        print(round(r["score"], 3), r["source"], r["text"][:150], "\n")