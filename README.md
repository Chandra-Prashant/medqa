# MedQA-Grounded: Evidence-Grounded and Self-Correcting LLM Pipeline for Healthcare Question Answering

B.Tech Project (COP4982), Department of Computer Engineering, Zakir Husain College of Engineering and Technology, Aligarh Muslim University.

**Authors:** Prashant Chandra, Siddhant Varshney
**Supervisor:** Asst. Prof. Muneeb Hasan Khan

> **Status: Phase-I complete (tag `phase1-v0.1`).** Modules M1 to M4 are working prototypes. M5 and M6 and the verifier improvements are planned for Phase-II. This repository is research code, not a medical device, and its answers must not be used for clinical decisions.

---

## What this project does

Large language models answer medical questions fluently but can state unsupported claims. This project builds a pipeline that answers only from retrieved evidence, checks each claim in the answer against that evidence, and (in Phase-II) corrects or withholds claims that are not supported.

```
Question
   |
   v
M2  Retrieve (bge-small + FAISS) -> Rerank (bge-reranker-base)  -> top-5 evidence chunks
   |
   v
M3  Generate answer ONLY from the evidence (abstain if evidence is missing)
   |
   v
M4  Extract atomic claims -> verify each against the evidence (NLI)
   |
   v
M5  Correct / abstain on unsupported claims                      [Phase-II]
M6  Evaluate (RAG vs LLM-only vs full pipeline)                   [Phase-II]
```

## Modules and status

| Module | Folder | Status | What it does |
|---|---|---|---|
| M1 Knowledge base | `m1_kb/` | Done | Downloads PubMed review abstracts (MeSH and publication-type filters), chunks and embeds them, builds a FAISS index |
| M2 Retrieval | `m2_retrieval/` | Done | Dense retrieval followed by cross-encoder reranking, de-duplicated by document |
| M3 Generation | `m3_generation/` | Done (prototype) | Evidence-only answers via an OpenAI-compatible API, with an abstention rule and a disk cache |
| M4 Verification | `m4_verification/` | Prototype | Atomic claim extraction and sentence-window NLI verification |
| M5 Correction | `m5_correction/` | Phase-II | Correct or abstain on unsupported claims |
| M6 Evaluation | `m6_eval/` | Partial | Question set (48 questions) done; full evaluation in Phase-II |

## Knowledge base

- Source: PubMed, via NCBI E-utilities (Biopython).
- Selection: MeSH topic queries, restricted to Review, Meta-Analysis, Guideline and Systematic Review publication types, 2015 to 2026, English, with abstract.
- Size: 2,980 abstracts, 5,822 chunks (200 words, 40-word overlap, title prefix).
- Embeddings: `BAAI/bge-small-en-v1.5` (normalised), `faiss.IndexFlatIP`.
- Reranker: `BAAI/bge-reranker-base`.

## Setup

Tested on macOS (Apple Silicon, 8 GB) with Anaconda and Python 3.

```bash
git clone https://github.com/Chandra-Prashant/medqa.git
cd medqa
conda create -n medqa python=3.11 -y && conda activate medqa
pip install -r requirements.txt   # if present; otherwise install the packages below
pip install biopython faiss-cpu sentence-transformers openai python-dotenv torch
```

Create a `.env` file in the project root (never commit it):

```
LLM_API_KEY=<your key>
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
EXTRACT_MODEL=openai/gpt-oss-120b
```

On macOS, if you see an OpenMP "libomp already initialized" error:

```bash
export KMP_DUPLICATE_LIB_OK=TRUE
```

## Running the pipeline

Run all commands from the project root.

```bash
# M1: build the knowledge base
python -m m1_kb.download
python -m m1_kb.build_index

# M2: try retrieval
python -m m2_retrieval.rerank

# Question set (48 questions)
python -m m6_eval.make_questions

# M3: generate answers (optional limit for a quick test)
python -m m3_generation.run 5
python -m m3_generation.run

# M4: extract and verify claims
python -m m4_verification.extract rag
python -m m4_verification.verify rag

# Manual-check sample and agreement
python -m m4_verification.sample
python -m m4_verification.agree
```

LLM calls are cached in `data/llm_cache/`, so re-runs do not repeat paid or rate-limited calls. `data/` is git-ignored.

## Repository layout

```
configs/        question set and settings
data/           raw abstracts, index, caches (git-ignored)
logs/           run logs
m1_kb/          knowledge-base construction
m2_retrieval/   retrieval and reranking
m3_generation/  answer generation
m4_verification/ claim extraction and verification
m5_correction/  (Phase-II)
m6_eval/        question set and evaluation
results/        outputs; frozen Phase-I results in results/phase1/
```

## Phase-I results

- **Retrieval:** on-topic questions retrieve relevant evidence; off-topic questions score low and trigger abstention.
- **Generation:** 48 questions (10 topics with 4 on-topic questions each, plus near-topic and off-topic checks for abstention).
- **Claim extraction:** 395 atomic claims from 38 answers.
- **Verifier manual check:** 40 claims sampled by label (10 supported, 20 insufficient, 10 contradicted). The labels were produced by an LLM annotator (Claude) against the retrieved evidence; they are not independent human labels.

| Verifier label | Annotator: Supported | Annotator: Insufficient | Annotator: Contradicted |
|---|---|---|---|
| Supported (10) | 8 | 2 | 0 |
| Insufficient (20) | 16 | 4 | 0 |
| Contradicted (10) | 5 | 5 | 0 |

Agreement is 12 of 40. The sample is stratified, so these are per-label figures, not population rates.

## Known limitations

- The NLI verifier under-detects support: most claims it labels INSUFFICIENT were judged supported on manual check.
- The CONTRADICTED label is unreliable and should not be used as a result.
- The corpus text contains HTML (`&minus;`, `<i>`, `<sup>`) that degrades verification of numeric claims.
- The manual-check labels come from an LLM annotator, not independent human annotators.
- Claim extraction skips hedged statements and advice.
- Using an LLM as both generator and judge would be circular; the final evaluation needs an independent judge.

## Phase-II plan

1. Clean the evidence text and select a better verifier (alternative NLI models, LLM second pass), compared on the labelled sample.
2. M5: correction and abstention for unsupported claims.
3. M6: full comparison of LLM-only, RAG and the full pipeline, using independent human annotators and inter-annotator agreement (Cohen's kappa).
4. Larger question set and corpus.
5. Demo interface and final report.

## Safety note

Outputs are research artefacts built from published abstracts. They are not medical advice.
