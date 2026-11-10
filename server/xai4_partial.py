"""XAI-4 typed, narrow English morphology observations; NOT a grammar oracle.

The four XAI-PRE Cambridge source claims await human review. The public
evaluator must never expose a candidate VIOLATED as a verified diagnosis.
Raw tokens remain distinct from canonical B-R node IDs.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = "xai4-partial-1.0.0"
TOKEN_RE = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)
HAVE = {"have", "has", "had"}
BE = {"am", "is", "are", "was", "were", "be", "been", "being"}
MODAL = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
SKIP = {"already", "just", "never", "not", "often", "always", "recently", "still"}
PAST = {"went", "ate", "saw", "wrote", "drove", "sang", "spoke", "took",
        "gave", "broke", "drank", "was", "were", "did", "swam", "flew"}
PARTICIPLE = {"gone", "eaten", "seen", "written", "driven", "sung", "spoken",
              "taken", "given", "broken", "drunk", "been", "done", "swum",
              "flown", "made", "read", "paid", "bought", "known", "left"}
PLAIN = {"go", "eat", "see", "write", "drive", "sing", "speak", "take",
         "give", "break", "drink", "be", "do", "have", "run", "swim",
         "fly", "make", "read", "know", "discuss", "walk", "talk", "work",
         "play", "study", "sleep", "laugh"}
FINITE = {"goes", "eats", "sees", "writes", "drives", "sings", "speaks",
          "takes", "gives", "breaks", "drinks", "does", "has", "is",
          "runs", "flies", "makes", "knows", "discusses", "plays", "studies"}
FAMILIES = {"perfect_auxiliary_participle", "modal_plain_form",
            "progressive_auxiliary_gerund_participle", "present_perfect_time_adjunct"}


def tokenize(text):
    return [{"id": "t" + str(i), "index": i, "text": m.group(),
             "lower": m.group().casefold().replace("’", "'"),
             "char_span": [m.start(), m.end()]}
            for i, m in enumerate(TOKEN_RE.finditer(text))]


def next_word(tokens, i):
    j = i + 1
    while j < len(tokens) and tokens[j]["lower"] in SKIP:
        j += 1
    return j if j < len(tokens) and tokens[j]["lower"].isalpha() else None


def observation(tokens, i, j, signal):
    start, end = min(i, j), max(i, j)
    return {"signal": signal, "governor_token_id": tokens[i]["id"],
            "target_token_id": tokens[j]["id"],
            "affected_token_ids": [t["id"] for t in tokens[start:end+1]],
            "token_span": [start, end+1],
            "char_span": [tokens[start]["char_span"][0], tokens[end]["char_span"][1]],
            "observed_tokens": [t["text"] for t in tokens[start:end+1]],
            "evidence_kind": "raw_token_context_only"}


def inspect(family, tokens):
    """Internal candidate signal; never directly rendered as a grammar verdict."""
    if family not in FAMILIES:
        return []
    rows = []
    for i, token in enumerate(tokens):
        word = token["lower"]
        if family == "perfect_auxiliary_participle":
            if word not in HAVE and not word.endswith("'ve") and not word.endswith("'d"):
                continue
        elif family == "modal_plain_form":
            if word not in MODAL:
                continue
        elif family == "progressive_auxiliary_gerund_participle":
            if word not in BE:
                continue
        elif family == "present_perfect_time_adjunct":
            if word not in {"have", "has"} and not word.endswith("'ve"):
                continue
        j = next_word(tokens, i)
        if j is None:
            continue
        after = tokens[j]["lower"]
        if family == "perfect_auxiliary_participle":
            if word.endswith("'d"):
                signal = "AMBIGUOUS"
            elif after in PAST:
                signal = "VIOLATED"
            elif after in PARTICIPLE or (after.endswith("ed") and len(after)>3):
                signal = "SATISFIED"
            elif after in PLAIN or after in FINITE:
                signal = "AMBIGUOUS" if after == "have" else "VIOLATED"
            else:
                continue  # "had breakfast": lexical have, not assumed auxiliary
        elif family == "modal_plain_form":
            if after in PLAIN:
                signal = "SATISFIED"
            elif after in FINITE or after in PAST or after in PARTICIPLE:
                signal = "VIOLATED"
            else:
                continue  # a can opener, a May date, unknown word
        elif family == "progressive_auxiliary_gerund_participle":
            if after.endswith("ing") and len(after)>4:
                signal = "SATISFIED"
            elif after in PLAIN or after in FINITE or after in PAST:
                signal = "VIOLATED"
            elif after in PARTICIPLE or after.endswith("ed"):
                signal = "AMBIGUOUS"  # passive/copular be, not progressive
            else:
                continue  # she is happy: copular, not progressive
        else:
            if not (after in PARTICIPLE or after.endswith("ed")):
                continue
            for k in range(j+1, min(len(tokens),j+18)):
                if tokens[k]["lower"] == "yesterday":
                    rows.append(observation(tokens, i, k, "AMBIGUOUS"))
            continue
        rows.append(observation(tokens, i, j, signal))
    return rows


def load_manifest(root=None):
    root = root or ROOT
    manifest = json.loads((root/"grammar/xai4_candidates.json").read_text())
    audit = json.loads((root/"grammar/xai_pre/source_audit.json").read_text())
    rows = manifest.get("rules")
    if (manifest.get("schema_version") != "xai4-candidates-1.0.0"
            or manifest.get("language_policy") != "ENGLISH_ONLY"
            or audit.get("schema_version") != "xai-pre-source-audit-1.0"
            or not isinstance(rows, list) or len(rows) > 16
            or len({r.get("id") for r in rows if isinstance(r, dict)}) != len(rows)):
        raise ValueError("Invalid XAI-4 source manifest")
    return manifest, audit
