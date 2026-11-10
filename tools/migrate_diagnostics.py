#!/usr/bin/env python3
"""Idempotent backwards-compatible migration of grammar rules to diagnostic:null."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(write=False):
    total=missing=0
    for path in sorted((ROOT/"grammar/rules").glob("*.json")):
        rules=json.loads(path.read_text(encoding="utf-8"));changed=False
        for rule in rules:
            total+=1
            if "diagnostic" not in rule:
                missing+=1
                if write:rule["diagnostic"]=None;changed=True
        if changed:path.write_text(json.dumps(rules,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return total,missing
if __name__=="__main__":
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    opt=p.parse_args();total,missing=run(opt.write)
    print(f"Rules: {total}; missing diagnostic fields: {missing}")
    if opt.check and missing:raise SystemExit(1)
