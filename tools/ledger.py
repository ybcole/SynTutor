#!/usr/bin/env python3
"""Track CGEL printed-page coverage. Strict check refuses unprocessed pages."""
import argparse,json,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"grammar/coverage/cgel_ledger.json"
MANIFEST=ROOT/"sources/cambridge/source_manifest_2026-11-08.json"
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def ranges(manifest):
    files=manifest["files"]
    return {f["chapter"]:(f["printed_start"],files[i+1]["printed_start"]-1 if i+1<len(files) else 1764) for i,f in enumerate(files)}
def check(data,manifest,chapter=None,allow_unprocessed=False):
    errs=[];bounds=ranges(manifest);rows=data.get("pages",[])
    limit=max(end for _,end in bounds.values())
    if len(rows)!=limit or data.get("printed_end")!=limit or data.get("printed_start")!=1:
        errs.append("Invalid page inventory")
    for i,row in enumerate(rows):
        p=i+1;ch=next((c for c,(a,b) in bounds.items() if a<=p<=b),None)
        if not isinstance(row,dict):
            errs.append(f"Page {p} not object");continue
        if row.get("page")!=p or row.get("chapter")!=ch:errs.append(f"Page {p} number/chapter mismatch")
        status=row.get("status")
        if status not in {"unprocessed","extracted","skipped_with_reason","absent_from_source"}:
            errs.append(f"Page {p} invalid status")
        if status in {"skipped_with_reason","absent_from_source"} and not str(row.get("reason") or "").strip():
            errs.append(f"Page {p} missing skip reason")
        if status=="extracted" and not str(row.get("evidence") or "").strip():
            errs.append(f"Page {p} missing extraction evidence")
        if status=="unprocessed" and not allow_unprocessed and (chapter is None or ch==chapter):
            errs.append(f"Page {p} unprocessed")
    for path in sorted((ROOT/"grammar/rules").glob("*.json")):
        for rule in load(path):
            for src in rule.get("sources",[]):
                if "cambridge" not in str(src.get("book","")).lower():continue
                ch=src.get("chapter")
                if ch not in bounds:errs.append(f"{rule['id']} unknown chapter {ch}");continue
                for p in src.get("pages",[]):
                    if not isinstance(p,int) or not bounds[ch][0]<=p<=bounds[ch][1]:
                        errs.append(f"{rule['id']} page {p} outside chapter {ch}")
                    elif p<=len(rows) and rows[p-1].get("status") in {"absent_from_source","skipped_with_reason"}:
                        errs.append(f"{rule['id']} cites textless/unavailable page {p}")
    return errs
def summary(data,chapter=None):
    rows=[r for r in data["pages"] if chapter is None or r["chapter"]==chapter]
    c=Counter(r["status"] for r in rows)
    return {"chapter":chapter,"pages":len(rows),"extracted":c["extracted"],"unprocessed":c["unprocessed"],"skipped_with_reason":c["skipped_with_reason"],"absent_from_source":c["absent_from_source"],"extracted_percent":round(100*c["extracted"]/max(1,len(rows)),2)}
def number_set(spec):
    out=set()
    for group in spec.split(","):
        bits=group.strip().split("-")
        if len(bits)==1:out.add(int(bits[0]))
        elif len(bits)==2:
            a,b=map(int,bits)
            if a>b:raise ValueError("reversed range")
            out.update(range(a,b+1))
        else:raise ValueError("invalid range")
    if not out or min(out)<1:raise ValueError("invalid pages")
    return sorted(out)
def main():
    a=argparse.ArgumentParser();subs=a.add_subparsers(dest="op",required=True)
    for op in ["report","check","mark"]:
        sp=subs.add_parser(op);sp.add_argument("--chapter",type=int,required=op=="mark")
        if op=="check":sp.add_argument("--allow-unprocessed",action="store_true",help="Phase A integrity only, not full-coverage certification")
        if op=="mark":
            sp.add_argument("--pages",required=True);sp.add_argument("--status",choices=["extracted","skipped_with_reason"],required=True)
            sp.add_argument("--reason");sp.add_argument("--evidence");sp.add_argument("--override-source",action="store_true")
    args=a.parse_args();data=load(LEDGER);manifest=load(MANIFEST);bounds=ranges(manifest)
    ch=args.chapter
    if ch is not None and ch not in bounds:a.error("unknown chapter")
    if args.op=="mark":
        try:pages=number_set(args.pages)
        except ValueError as e:a.error(str(e))
        first,last=bounds[ch]
        if any(p<first or p>last for p in pages):a.error("pages outside chapter")
        if args.status=="skipped_with_reason" and not str(args.reason or "").strip():a.error("--reason required")
        if args.status=="extracted":
            if not args.evidence:a.error("--evidence required")
            target=(ROOT/args.evidence).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():a.error("--evidence must exist in repo")
        if not args.override_source and any(data["pages"][p-1]["status"] in {"skipped_with_reason","absent_from_source"} for p in pages):
            a.error("source exceptions need --override-source after independent verification")
        for p in pages:
            data["pages"][p-1].update(status=args.status,
               reason=args.reason if args.status=="skipped_with_reason" else None,
               evidence=args.evidence if args.status=="extracted" else None)
        LEDGER.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"marked":pages,**summary(data,ch)}));return 0
    errors=check(data,manifest,ch,allow_unprocessed=args.op=="report" or getattr(args,"allow_unprocessed",False))
    print(json.dumps({**summary(data,ch),"errors":len(errors),"examples":errors[:12],
       "coverage_certified":args.op=="check" and not getattr(args,"allow_unprocessed",False) and not errors},indent=2))
    return int(bool(errors)) if args.op=="check" else 0
if __name__=="__main__":sys.exit(main())
