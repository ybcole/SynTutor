#!/usr/bin/env python3
"""Validate the Cambridge JSON schema and all rules; optionally demand chapter diagnostics."""
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.ledger import LEDGER,MANIFEST,load,ranges
def validate(chapter=None,require_diagnostics=False):
    schema=load(ROOT/"grammar/schema.json");Draft202012Validator.check_schema(schema)
    v=Draft202012Validator(schema);bounds=ranges(load(MANIFEST))
    status={row["page"]:row["status"] for row in load(LEDGER)["pages"]}
    ids=set();errors=[];count=0
    for path in sorted((ROOT/"grammar/rules").glob("*.json")):
        for rule in load(path):
            count+=1;rid=rule.get("id","UNKNOWN")
            if rid in ids:errors.append(f"{rid}: duplicate ID")
            ids.add(rid)
            for err in v.iter_errors(rule):errors.append(f"{rid} {err.json_path}: {err.message}")
            target=False
            for src in rule.get("sources",[]):
                if "cambridge" not in str(src.get("book","")).lower():continue
                ch=src.get("chapter");target |= ch==chapter
                if ch not in bounds:errors.append(f"{rid}: unknown chapter {ch}");continue
                for p in src.get("pages",[]):
                    if not isinstance(p,int) or not bounds[ch][0]<=p<=bounds[ch][1]:
                        errors.append(f"{rid}: page {p} outside chapter")
                    elif status.get(p) in {"skipped_with_reason","absent_from_source"}:
                        errors.append(f"{rid}: textless/unavailable cited page {p}")
            if require_diagnostics and (chapter is None or target) and rule.get("rule_type")=="constraint":
                d=rule.get("diagnostic")
                if not isinstance(d,dict):errors.append(f"{rid}: missing diagnostic")
                else:
                    if d.get("detector")=="spec_only":errors.append(f"{rid}: detector still spec_only")
                    if not d.get("false_positive_guards"):errors.append(f"{rid}: no negative guards")
                    for pair in d.get("minimal_pairs",[]):
                        ps=pair.split("|||")
                        if len(ps)!=2 or not all(x.strip() for x in ps):errors.append(f"{rid}: bad minimal pair")
    return count,errors
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--chapter",type=int)
    p.add_argument("--require-diagnostics",action="store_true")
    opt=p.parse_args()
    try:count,errs=validate(opt.chapter,opt.require_diagnostics)
    except Exception as e:print(f"Validator failed: {e}",file=sys.stderr);sys.exit(1)
    print(json.dumps({"rules":count,"errors":len(errs),"samples":errs[:30]},indent=2))
    if errs:sys.exit(1)
