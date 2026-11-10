#!/usr/bin/env python3
"""Fail-closed chapter bulk approval; never auto-enables runtime grammar rules."""
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def checked(*cmd):
    p=subprocess.run([sys.executable,*cmd],cwd=ROOT,capture_output=True,text=True)
    if p.returncode:raise RuntimeError("Gate failed: "+" ".join(cmd)+"\n"+(p.stdout+p.stderr)[-3000:])
def belongs(rule,ch):
    return any(s.get("chapter")==ch and "cambridge" in str(s.get("book","")).lower() for s in rule.get("sources",[]))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--chapter",required=True,type=int)
    p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    if not 1<=a.chapter<=20:p.error("chapter must be 1..20")
    files={path:json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT/"grammar/rules").glob("*.json"))}
    candidates=[r for rs in files.values() for r in rs if r.get("status")=="NEEDS_REVIEW" and belongs(r,a.chapter)]
    if not candidates:
        print(json.dumps({"chapter":a.chapter,"eligible":0,"approved":0}));return 0
    ids={r["id"] for r in candidates}
    audit=ROOT/f"sources/cambridge/chapter_{a.chapter:02d}/source_exception_self_check.json"
    if not audit.is_file():raise RuntimeError("No source-page and exception self-check")
    data=json.loads(audit.read_text(encoding="utf-8"))
    if (data.get("chapter")!=a.chapter or data.get("result")!="pass" or data.get("source_pages_reviewed") is not True
        or data.get("exceptions_reviewed") is not True or not ids.issubset(set(data.get("checked_rule_ids",[])))):
        raise RuntimeError("Source-page/exception self-check does not cover candidates")
    for r in candidates:
        if r["rule_type"]=="constraint":
            d=r.get("diagnostic")
            if not isinstance(d,dict) or d.get("detector") in {None,"spec_only"}:
                raise RuntimeError(f"{r['id']} missing implemented or justified none_possible detector")
    checked("tools/migrate_diagnostics.py","--check")
    checked("tools/ledger.py","check","--chapter",str(a.chapter))
    checked("tools/validate_cgel_rules.py","--chapter",str(a.chapter),"--require-diagnostics")
    checked("scripts/audit_xai_pre.py","--require-contracts")
    if not (ROOT/"evaluation/cgel_coverage_corpus.json").is_file() or not (ROOT/"scripts/evaluate_cgel_coverage.py").is_file():
        raise RuntimeError("Phase C coverage corpus and evaluator are not present")
    checked("scripts/evaluate_cgel_coverage.py","--require-passing")
    checked("scripts/basic_errors.py")
    checked("-m","unittest","discover","-s","server","-p","test_*.py")
    if not a.apply:
        print(json.dumps({"chapter":a.chapter,"eligible":len(candidates),"gates":"passed","mode":"dry-run"}));return 0
    date=datetime.now(timezone.utc).date().isoformat()
    for path,records in files.items():
        modified=False
        for r in records:
            if r["id"] in ids and r["status"]=="NEEDS_REVIEW":
                r.update(status="APPROVED",approved_by="owner_bulk",approved_on=date);modified=True
        if modified:
            temp=path.with_suffix(".tmp")
            temp.write_text(json.dumps(records,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            temp.replace(path)
    print(json.dumps({"chapter":a.chapter,"approved":len(candidates),"approved_by":"owner_bulk","approved_on":date,"runtime_enabled":False}))
    return 0
if __name__=="__main__":
    try:sys.exit(main())
    except (OSError,ValueError,RuntimeError) as e:
        print("APPROVAL BLOCKED: "+str(e),file=sys.stderr)
        sys.exit(1)
