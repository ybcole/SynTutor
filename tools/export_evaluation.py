#!/usr/bin/env python3
"""Export approved rule examples into evaluation/*.json for the engine test suite.
Usage: python tools/export_evaluation.py
- grammatical_sentences.json : every 'correct' example of an APPROVED rule
- ungrammatical_sentences.json: 'incorrect' examples (constraint / variety_restricted rules only)
- minimal_pairs.json         : correct/incorrect examples sharing a pair_id within one rule
Bracketed annotations like [passive] and a leading '*' are stripped. 'contrast' examples are never exported.
"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def clean(t): return re.sub(r"\s*\[[^\]]*\]\s*$", "", t).lstrip("*").strip()
def unit(t): return "sentence" if t[-1:] in ".?!" else "phrase"
good, bad, pairs, seen = [], [], [], set()
for f in sorted((ROOT/"grammar"/"rules").glob("*.json")):
    for r in json.loads(f.read_text(encoding="utf-8")):
        if r["status"] != "APPROVED": continue
        meta = {"rule_id": r["id"], "domain": r["domain"], "rule_type": r["rule_type"],
                "source_pages": sorted({p for s in r["sources"] for p in s["pages"]})}
        byp = {}
        for kind, bucket in (("correct", good), ("incorrect", bad)):
            if kind == "incorrect" and r["rule_type"] not in ("constraint", "variety_restricted"): continue
            for e in r["examples"].get(kind, []):
                t = clean(e["text"]); key = (kind, t.lower())
                if key in seen: continue
                seen.add(key)
                rec = {"text": t, "unit": unit(t), "origin": e["origin"], **meta}
                if e.get("tests_exception"): rec["tests_exception"] = True
                bucket.append(rec)
                if e.get("pair_id"): byp.setdefault(e["pair_id"], {})[kind] = t
        for pid, d in byp.items():
            if "correct" in d and "incorrect" in d:
                pairs.append({"pair_id": f"{r['id']}:{pid}", "grammatical": d["correct"], "ungrammatical": d["incorrect"], **meta})
out = ROOT/"evaluation"; out.mkdir(exist_ok=True)
for name, data in (("grammatical_sentences", good), ("ungrammatical_sentences", bad), ("minimal_pairs", pairs)):
    (out/f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(f"grammatical {len(good)} | ungrammatical {len(bad)} | minimal pairs {len(pairs)}")
