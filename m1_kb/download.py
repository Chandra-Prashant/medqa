import json, time
from Bio import Entrez

Entrez.email = "pc079105@gmail.com"   # required by NCBI

FILTER = ' AND (Review[pt] OR Meta-Analysis[pt] OR Guideline[pt] OR "Systematic Review"[pt]) AND 2015:2026[dp] AND english[lang] AND hasabstract'

TOPICS = [
    '"diabetes mellitus, type 2"[MeSH] AND therapy',
    '"hypertension"[MeSH] AND "antihypertensive agents"[MeSH]',
    '"asthma"[MeSH] AND therapy',
    '"migraine disorders"[MeSH] AND therapy',
    '"drug resistance, bacterial"[MeSH] AND antibiotics',
    '"depressive disorder"[MeSH] AND therapy',
    '"COVID-19"[MeSH] AND symptoms',
    '"heart failure"[MeSH] AND therapy',
    '"renal insufficiency, chronic"[MeSH] AND therapy',
    '"vaccines"[MeSH] AND "adverse effects"[sh]',
]
PER_TOPIC = 300

def search(term, n):
    h = Entrez.esearch(db="pubmed", term=term + FILTER, retmax=n, sort="relevance")
    return Entrez.read(h)["IdList"]

def fetch(ids):
    h = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
    return Entrez.read(h)["PubmedArticle"]

seen, out = set(), []
for topic in TOPICS:
    ids = [i for i in search(topic, PER_TOPIC) if i not in seen]
    for k in range(0, len(ids), 100):
        for art in fetch(ids[k:k+100]):
            mc = art["MedlineCitation"]; a = mc["Article"]
            parts = a.get("Abstract", {}).get("AbstractText", [])
            abstract = " ".join(str(p) for p in parts).strip()
            pmid = str(mc["PMID"])
            if abstract and pmid not in seen:
                seen.add(pmid)
                out.append({"doc_id": pmid, "title": str(a["ArticleTitle"]),
                            "text": abstract, "source": f"PubMed:{pmid}"})
        time.sleep(0.4)   # stay under NCBI rate limits
    print(topic, len(out))

with open("data/raw/abstracts.jsonl", "w") as f:
    for r in out: f.write(json.dumps(r) + "\n")