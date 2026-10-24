import json, pickle, faiss, torch, numpy as np
from sentence_transformers import SentenceTransformer

def chunk(text, size=200, overlap=40):
    w = text.split()
    if len(w) <= size: return [text]
    return [" ".join(w[i:i+size]) for i in range(0, len(w), size - overlap)]

chunks = []
for line in open("data/raw/abstracts.jsonl"):
    d = json.loads(line)
    for j, c in enumerate(chunk(d["text"])):
        chunks.append({"doc_id": d["doc_id"], "chunk_id": f'{d["doc_id"]}_{j}',
                       "text": f'{d["title"]}. {c}', "source": d["source"]})

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer("BAAI/bge-small-en-v1.5", device=device)
emb = model.encode([c["text"] for c in chunks], batch_size=64,
                   normalize_embeddings=True, show_progress_bar=True)

index = faiss.IndexFlatIP(emb.shape[1])
index.add(np.asarray(emb, dtype="float32"))
faiss.write_index(index, "data/processed/index.faiss")
pickle.dump(chunks, open("data/processed/chunks.pkl", "wb"))
print(len(chunks), "chunks indexed")