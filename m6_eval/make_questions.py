import json
from pathlib import Path

Q = {
 "diabetes": [
  "What is the first-line drug treatment for type 2 diabetes?",
  "Do SGLT2 inhibitors reduce the risk of kidney problems in people with type 2 diabetes?",
  "What are the common side effects of metformin?",
  "Does exercise improve blood sugar control in type 2 diabetes?"],
 "hypertension": [
  "How is high blood pressure treated in older adults?",
  "Which classes of drugs are used to lower blood pressure?",
  "Does reducing salt intake lower blood pressure?",
  "What are the risks of lowering blood pressure too aggressively?"],
 "asthma": [
  "How do inhaled corticosteroids help in asthma?",
  "What is the role of biologic therapies in severe asthma?",
  "Are long-acting beta agonists safe for people with asthma?",
  "Can asthma symptoms be reduced by weight loss?"],
 "migraine": [
  "What drugs are used to prevent migraine attacks?",
  "Are CGRP antibodies effective for migraine prevention?",
  "How effective are triptans for acute migraine?",
  "Does acupuncture help with migraine?"],
 "antibiotic resistance": [
  "What causes bacteria to become resistant to antibiotics?",
  "How does antibiotic overuse contribute to resistance?",
  "What can hospitals do to reduce the spread of resistant bacteria?",
  "Are there alternatives to antibiotics for treating resistant infections?"],
 "depression": [
  "How effective are antidepressants for major depression?",
  "Is cognitive behavioural therapy effective for depression?",
  "What are the side effects of SSRIs?",
  "What treatment options exist when depression does not respond to the first antidepressant?"],
 "covid-19": [
  "What are the common symptoms of COVID-19?",
  "How long can COVID-19 symptoms persist after infection?",
  "Does COVID-19 vaccination reduce the risk of severe illness?",
  "What is long COVID?"],
 "heart failure": [
  "What drugs improve survival in heart failure with reduced ejection fraction?",
  "Do SGLT2 inhibitors help patients with heart failure?",
  "How does exercise training affect people with heart failure?",
  "What is the role of beta blockers in heart failure?"],
 "chronic kidney disease": [
  "How can the progression of chronic kidney disease be slowed?",
  "What are the complications of chronic kidney disease?",
  "Is a low-protein diet useful in chronic kidney disease?",
  "How is anaemia treated in people with chronic kidney disease?"],
 "vaccine safety": [
  "What are the common side effects of vaccines?",
  "Are serious adverse events after vaccination common?",
  "Is there evidence linking vaccines to autism?",
  "How is vaccine safety monitored after approval?"],
  "near-topic": ["What is the best treatment for acne?"],
}
OFF = [
  "How is a broken femur treated?",
  "How is acute appendicitis treated?",
  "What are the treatment options for glaucoma?",
  "How is a torn ACL treated?",
  "How are kidney stones treated?",
  "At what age should breast cancer screening begin?",
  "What is the treatment for hypothyroidism?"
]


rows = []
for topic, qs in Q.items():
    for q in qs:
        rows.append({"topic": topic, "question": q, "expect_abstain": False})
for q in OFF:
    rows.append({"topic": "off-topic", "question": q, "expect_abstain": True})
for i, r in enumerate(rows, 1):
    r["id"] = f"q{i:03d}"

Path("configs").mkdir(exist_ok=True)
with open("configs/questions.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps({k: r[k] for k in ("id", "topic", "question", "expect_abstain")}) + "\n")
print(len(rows), "questions written to configs/questions.jsonl")