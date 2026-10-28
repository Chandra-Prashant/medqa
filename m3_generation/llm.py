import os, json, hashlib, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["LLM_API_KEY"], base_url=os.environ["LLM_BASE_URL"])
MODEL = os.environ["LLM_MODEL"]
CACHE = Path("data/llm_cache"); CACHE.mkdir(parents=True, exist_ok=True)

def clean(t):
    return (t.replace("\u2011", "-").replace("\u2010", "-").replace("\u2013", "-")
             .replace("\u202f", " ").replace("\u00a0", " ").replace("\u2009", " "))

def chat(messages, temperature=0.0, max_tokens=2500, model=None, effort=None):
    model = model or MODEL
    parts = [model, messages, temperature, max_tokens] + ([effort] if effort else [])
    key = hashlib.sha256(json.dumps(parts).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if f.exists():
        return clean(json.loads(f.read_text())["text"])
    extra = {"reasoning_effort": effort} if effort else {}
    for attempt in range(5):
        try:
            r = client.chat.completions.create(model=model, messages=messages,
                                               temperature=temperature, max_tokens=max_tokens, **extra)
            text = clean((r.choices[0].message.content or "").strip())
            if not text:
                raise ValueError("empty answer (reasoning may have used all tokens)")
            f.write_text(json.dumps({"text": text}))
            return text
        except Exception as e:
            wait = 5 * 2 ** attempt
            print("LLM error:", e, "| retrying in", wait, "s")
            time.sleep(wait)
    raise RuntimeError("LLM call failed after retries")