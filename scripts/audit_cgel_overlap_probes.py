"""Observe legacy and matrix findings on Cambridge overlap probes."""

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from cgel_passive_make_candidate import probe_passive_make
from parse_engine import NodeBuilder, analyze, parse_parse_string
from ruleset import collect

# These small development probes are not a gold corpus.
CASES = [
("modal form", "She can goes.", "(S (NP (PRP She)) (VP (MD can) (VP (VBZ goes))) (. .))"),
("modal to", "She can to go.", "(S (NP (PRP She)) (VP (MD can) (S (VP (TO to) (VP (VB go))))) (. .))"),
("modal control", "She can go.", "(S (NP (PRP She)) (VP (MD can) (VP (VB go))) (. .))"),
("ought control", "She ought to leave.", "(S (NP (PRP She)) (VP (MD ought) (S (VP (TO to) (VP (VB leave))))) (. .))"),
("active causative", "She made him to wait.", "(S (NP (PRP She)) (VP (VBD made) (NP (PRP him)) (S (VP (TO to) (VP (VB wait))))) (. .))"),
("active causative control", "She made him wait.", "(S (NP (PRP She)) (VP (VBD made) (NP (PRP him)) (S (VP (VB wait)))) (. .))"),
("passive causative", "We were made wait outside.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (VB wait) (ADVP (RB outside)))))) (. .))"),
("passive causative control", "We were made to wait outside.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (TO to) (VP (VB wait) (ADVP (RB outside))))))) (. .))"),
("enjoy action", "She enjoys to run.", "(S (NP (PRP She)) (VP (VBZ enjoys) (S (VP (TO to) (VP (VB run))))) (. .))"),
("enjoy noun control", "She enjoys the music.", "(S (NP (PRP She)) (VP (VBZ enjoys) (NP (DT the) (NN music))) (. .))"),
("modal coordination control", "She may or may not finish.", "(S (NP (PRP She)) (VP (MD may) (CC or) (MD may) (RB not) (VP (VB finish))) (. .))"),
]


# Freeze these expectations before running the configured parser.
MODAL_EVALUATION_CASES = [
    ("third-person form", "The courier might arrives before noon.", "The courier might arrive before noon."),
    ("third-person form", "Our guide will brings a spare lantern.", "Our guide will bring a spare lantern."),
    ("third-person form", "The committee should approves the request.", "The committee should approve the request."),
    ("extra to", "The caretaker must to lock the side gate.", "The caretaker must lock the side gate."),
    ("extra to", "A volunteer could to move the cabinet.", "A volunteer could move the cabinet."),
    ("extra to", "The hikers may to cross the bridge.", "The hikers may cross the bridge."),
    ("stress: negation", "The courier might not arrives before noon.", "The courier might not arrive before noon."),
    ("stress: inversion", "Could the courier arrives before noon?", "Could the courier arrive before noon?"),
    ("stress: intervening adjunct", "The courier might soon arrives.", "The courier might soon arrive."),
    ("control: plain", "The courier might arrive before noon.", None),
    ("control: plain ending in s", "The committee might focus on the budget.", None),
    ("control: plain ending in ss", "The cyclist can pass on the left.", None),
    ("control: perfect", "The courier might have arrived already.", None),
    ("control: passive", "The side gate must be locked.", None),
    ("control: noncentral modal", "The caretaker ought to lock the gate.", None),
    ("control: lexical need", "The guide needs to bring a spare lantern.", None),
    ("control: coordination", "The hikers may or may not cross the bridge.", None),
    ("control: lexical can", "The crew cans peaches in August.", None),
    ("control: infinitival purpose", "The caretaker will wait to lock the gate.", None),
    ("control: quotation", "The sign read, “You may cross the bridge.”", None),
]


ENJOY_EVALUATION_CASES = [
    ("direct", "The twins enjoy to swim before breakfast.", "The twins enjoy swimming before breakfast."),
    ("direct", "Mira enjoys to write short stories.", "Mira enjoys writing short stories."),
    ("direct", "Leo enjoyed to read on the porch.", "Leo enjoyed reading on the porch."),
    ("direct", "They are enjoying to learn a new language.", "They are enjoying learning a new language."),
    ("direct", "Nora enjoys to be alone on Sundays.", "Nora enjoys being alone on Sundays."),
    ("direct", "The children enjoy to play in the rain.", "The children enjoy playing in the rain."),
    ("stress: split infinitive", "Nora enjoys to quietly read at night.", "Nora enjoys quietly reading at night."),
    ("stress: coordination", "They enjoy to sing and dance.", "They enjoy singing and dancing."),
    ("control: nominal", "Nora enjoys the quiet.", None),
    ("control: purpose", "Leo enjoyed the break to clear his head.", None),
    ("control: gerund-participial", "Mira enjoys writing short stories.", None),
    ("control: overt lower subject", "They enjoy their children singing together.", None),
    ("control: embedded infinitive", "Nora enjoys learning to sail.", None),
    ("control: different verb", "The twins like to swim before breakfast.", None),
    ("control: independent clauses", "They enjoy the music, and I hope to dance.", None),
    ("control: quotation", "She wrote, “They enjoy to sing.”", None),
]


AUXILIARY_CASES = [
    ("modal stack", "The boat might could cross before noon.", "standard_english", ["COMP-031"]),
    ("modal stack", "The crew will can unload the truck.", "standard_english", ["COMP-031"]),
    ("modal stack", "The hikers may must turn back.", "standard_english", ["COMP-031"]),
    ("perfect have", "Did the courier have left already?", "standard_english", ["CLS-100"]),
    ("progressive be", "Does the engine be running now?", "standard_english", ["CLS-100"]),
    ("passive be", "Did the package be delivered yesterday?", "standard_english", ["CLS-100"]),
    ("copular be", "Does the assistant be available today?", "standard_english", ["CLS-100"]),
    ("copular be: fresh adjunct", "Did the clinic be open yesterday?", "standard_english", ["CLS-100"]),
    ("copular control", "Was the clinic open yesterday?", "standard_english", []),
    ("lexical question with adjunct", "Did the clinic open yesterday?", "standard_english", []),
    ("modal after do", "Did the mechanic can fix it?", "standard_english", ["CLS-100"]),
    ("lexical have", "Does the assistant have a spare key?", "standard_english", []),
    ("causative have", "Did the assistant have the door repaired?", "standard_english", []),
    ("lexical can", "The crew will can peaches tomorrow.", "standard_english", []),
    ("coordination", "The boat might or might not cross before noon.", "standard_english", []),
    ("negative imperative", "Do not be making noise in the hall.", "standard_english", []),
    ("emphatic imperative", "Do be careful on the stairs.", "standard_english", []),
    ("separate clauses", "The crew will wait until the driver can help.", "standard_english", []),
    ("lexical finite", "Did the driver parked near the library?", "standard_english", ["CLS-126"]),
    ("lexical finite", "Did the courier went home?", "standard_english", ["CLS-126"]),
    ("lexical finite", "Does the gardener trims the hedge?", "standard_english", ["CLS-126"]),
    ("invariant verb", "Did the chef cut the bread?", "standard_english", []),
    ("subject question", "Who trims the hedge?", "standard_english", []),
    ("lexical do", "Did the intern do the filing?", "standard_english", []),
    ("perfect form", "The courier has went home.", "standard_english", ["MORPH-026"]),
    ("perfect form", "The guests have already ate dinner.", "standard_english", ["MORPH-026"]),
    ("perfect form", "The pilot had took the wrong route.", "standard_english", ["MORPH-026"]),
    ("perfect form", "The volunteers have wrote a report.", "standard_english", ["MORPH-026"]),
    ("perfect control", "The courier has gone home.", "standard_english", []),
    ("regular perfect control", "The pilot had checked the route.", "standard_english", []),
    ("invariant perfect control", "The crew has cut the cable.", "standard_english", []),
    ("causative perfect control", "They have the technician check the cable.", "standard_english", []),
    ("possession control", "The volunteers have a report.", "standard_english", []),
    ("progressive chain", "The files were been reviewed by the auditors.", "standard_english", ["COMP-035"]),
    ("progressive chain", "The fence was been painted yesterday.", "standard_english", ["COMP-035"]),
    ("passive chain", "The photos were being took by the visitors.", "standard_english", ["COMP-036"]),
    ("passive chain", "The invitations are being wrote by hand.", "standard_english", ["COMP-036"]),
    ("progressive passive control", "The photos were being taken by the visitors.", "standard_english", []),
    ("copular control", "The visitors were being quiet.", "standard_english", []),
    ("simple progressive control", "The visitors were taking photos.", "standard_english", []),
    ("simple passive control", "The photos were taken yesterday.", "standard_english", []),
    ("ambiguous be", "The crew was paint.", "standard_english", []),
    ("unspecified variety", "The boat might could cross before noon.", None, []),
]


def evaluate_auxiliaries(probe):
    rows = []
    for group, sentence, variety, expected in AUXILIARY_CASES:
        analysis = analyze(sentence)
        result = probe(sentence, analysis["root"], variety=variety)
        for candidate in result["candidates"]:
            if edit := candidate["edit_hint"]:
                start, end = edit["char_span"]
                corrected = sentence[:start] + edit["replacement"] + sentence[end:]
                recheck = probe(corrected, analyze(corrected)["root"], variety=variety)
                candidate["reparse_observation"] = {
                    "sentence": corrected, "candidate_count": len(recheck["candidates"]),
                    "status": recheck["status"],
                }
        rows.append({
            "group": group, "sentence": sentence, "variety": variety,
            "parse": analysis["parse_string"], "expected_rule_ids": expected, "probe": result,
        })
    return rows


ARTICLE_CASES = [
    ("An university opened nearby.", "A university opened nearby."),
    ("We waited a hour.", "We waited an hour."),
    ("She bought a unusual book.", "She bought an unusual book."),
    ("She bought a (old) book.", "She bought an (old) book."),
    ("They saw an (small) owl.", "They saw a (small) owl."),
    ("A university opened nearby.", None),
    ("She bought an unusual book.", None),
    ("She bought an (old) book.", None),
    ("They saw a (small) owl.", None),
    ("She grew a herb.", None),
    ("They saw a UFO.", None),
]


def evaluate_articles(probe):
    for sentence, expected in ARTICLE_CASES:
        analysis = analyze(sentence)
        result = probe(sentence, analysis["root"], variety="standard_english")
        for candidate in result["candidates"]:
            edit = candidate["edit_hint"]
            start, end = edit["char_span"]
            repaired = sentence[:start] + edit["replacement"] + sentence[end:]
            recheck = probe(repaired, analyze(repaired)["root"], variety="standard_english")
            candidate["reparse_observation"] = {
                "sentence": repaired, "candidate_count": len(recheck["candidates"]),
                "status": recheck["status"],
            }
        yield {"sentence": sentence, "expected_repair": expected,
               "parse": analysis["parse_string"], "probe": result}


def evaluate_cases(cases, probe, governor_label, governor_key):
    rows = []
    for group, sentence, expected in cases:
        observation = observe_candidate(analyze(sentence), probe, governor_label, governor_key)
        candidates = observation["probe"]["candidates"]
        exact_reparse = len(candidates) == 1 and (
            candidates[0].get("reparse_observation", {}).get("sentence") == expected
            and candidates[0].get("reparse_observation", {}).get("candidate_count") == 0
            and candidates[0].get("reparse_observation", {}).get("candidate_status") != "not_evaluated"
        )
        rows.append({
            "group": group,
            "sentence": sentence,
            "expected_repair": expected,
            "exact_reparse": exact_reparse,
            **observation,
        })
    return rows


def summarize_matrix(evaluation):
    summary = evaluation["summary"]
    node_errors = []
    attached_errors = []
    for node_id, detail in evaluation["details"].items():
        if detail["status"] == "error":
            node_errors.append({
                "node_id": node_id,
                "rule_id": detail.get("rule_id"),
                "constraint": detail.get("constraint"),
                "surface": detail.get("surface"),
                "suggested_fix": (detail.get("remediation") or {}).get("suggested_fix"),
            })
        for finding in detail.get("findings", []):
            if finding["status"] == "error":
                attached_errors.append({
                    "attached_to": node_id,
                    "node_id": finding.get("node_id"),
                    "rule_id": finding.get("rule_id"),
                    "constraint": finding.get("constraint"),
                })
    return {
        "verdict": summary["verdict"],
        "checker_errors": summary["checker_errors"],
        "node_errors": node_errors,
        "attached_errors": attached_errors,
    }


def observe_candidate(analysis, candidate_probe, governor_label, governor_key):
    from burton_roberts import build_canonical_analysis
    from xai_facts import build_fact_graph

    sentence = analysis["sentence"]
    probe = candidate_probe(sentence, analysis["root"], variety="standard_english")
    canonical = build_canonical_analysis(analysis)
    report = {"parse": analysis["parse_string"], "probe": probe,
              "canonical_status": canonical["status"],
              "canonical_reason_codes": [row["code"] for row in canonical["reasons"]]}
    if not probe["candidates"]:
        return report
    graph = build_fact_graph(canonical) if canonical["status"] == "normalized" else {}
    by_id = {node["node_id"]: node for node in graph.get("nodes", []) if graph["status"] == "observed"}
    by_span = {tuple(token["char_span"]): token for token in graph.get("token_index", [])
               if graph["status"] == "observed"}
    for candidate in probe["candidates"]:
        relation = candidate["relation"]
        labels = {"governor": {governor_label}, "dependent": {"V", "AUX"}}
        nodes = {}
        for role, expected in labels.items():
            token = by_span.get(tuple(relation[f"{role}_char_span"]))
            if token and not token["opaque"]:
                node = next((by_id[node_id] for node_id in token["node_ids_innermost_first"]
                             if by_id[node_id]["label"] in expected), None)
                if node:
                    nodes[role] = node
        if len(nodes) == 2:
            common = set(nodes["governor"]["ancestor_ids"]) & set(nodes["dependent"]["ancestor_ids"])
            vp = next((node_id for node_id in nodes["governor"]["ancestor_ids"]
                       if node_id in common and by_id[node_id]["label"] == "VP"), None)
            if vp:
                candidate["canonical_observation"] = {
                    governor_key: nodes["governor"]["node_id"],
                    "dependent_node_id": nodes["dependent"]["node_id"],
                    "shared_vp_node_id": vp,
                }
        hint = candidate.get("edit_hint")
        if hint:
            start, end = hint["char_span"]
            corrected = sentence[:start] + hint["replacement"] + sentence[end:]
            reparsed = analyze(corrected)
            recheck = candidate_probe(corrected, reparsed["root"], variety="standard_english")
            candidate["reparse_observation"] = {
                "sentence": corrected,
                "candidate_count": len(recheck["candidates"]),
                "candidate_status": recheck["status"],
            }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true",
                        help="Use hand-authored trees instead of the configured parser")
    parser.add_argument("--matrix", action="store_true",
                        help="Also observe matrix verdicts, node errors, and attached findings")
    parser.add_argument("--passive-candidate", action="store_true",
                        help="Also observe the inactive passive causative candidate")
    parser.add_argument("--modal-candidate", action="store_true",
                        help="Observe parser-backed central modal candidates and canonical node alignment")
    parser.add_argument("--modal-evaluation", action="store_true",
                        help="Run the separate modal evaluation on configured parser output")
    parser.add_argument("--enjoy-evaluation", action="store_true",
                        help="Evaluate the inactive enjoy action-complement probe")
    parser.add_argument("--auxiliary-evaluation", action="store_true",
                        help="Measure modal stacking and inverted supportive do on configured parser output")
    parser.add_argument("--article-evaluation", action="store_true",
                        help="Measure the inactive article onset probe")
    args = parser.parse_args()
    if args.article_evaluation:
        if any(value for name, value in vars(args).items() if name != "article_evaluation"):
            parser.error("--article-evaluation runs separately on configured parser output")
        from cgel_article_parser_probe import probe_article_parser

        print(json.dumps({"input": "configured_parser",
                          "article_evaluation": list(evaluate_articles(probe_article_parser))}, indent=2))
        return
    if args.auxiliary_evaluation:
        if any((args.fixtures, args.matrix, args.passive_candidate, args.modal_candidate,
                args.modal_evaluation, args.enjoy_evaluation)):
            parser.error("--auxiliary-evaluation runs separately on configured parser output")
        from cgel_modal_parser_probe import probe_modal_parser

        print(json.dumps({"input": "configured_parser",
                          "auxiliary_evaluation": evaluate_auxiliaries(probe_modal_parser)}, indent=2))
        return
    if args.enjoy_evaluation:
        if args.fixtures or args.matrix or args.passive_candidate or args.modal_candidate or args.modal_evaluation:
            parser.error("--enjoy-evaluation runs separately on configured parser output")
        from cgel_enjoy_parser_probe import probe_enjoy_parser

        print(json.dumps({"input": "configured_parser",
                          "enjoy_evaluation": evaluate_cases(ENJOY_EVALUATION_CASES, probe_enjoy_parser, "V", "governor_node_id")}, indent=2))
        return
    if args.modal_evaluation:
        if args.fixtures or args.matrix or args.passive_candidate or args.modal_candidate:
            parser.error("--modal-evaluation runs separately on configured parser output")
        from cgel_modal_parser_probe import probe_modal_parser

        print(json.dumps({"input": "configured_parser",
                          "modal_evaluation": evaluate_cases(MODAL_EVALUATION_CASES, probe_modal_parser, "MOD", "modal_node_id")}, indent=2))
        return
    if args.modal_candidate and args.fixtures:
        parser.error("--modal-candidate requires configured parser output")
    if args.modal_candidate:
        from cgel_modal_parser_probe import probe_modal_parser
    if args.matrix:
        from matrix import evaluate
    observations = []
    for label, sentence, fixture in CASES:
        if args.fixtures:
            leaf_count = len(re.findall(r"\([^()]+\)", fixture))
            tree = NodeBuilder().build(parse_parse_string(fixture), leaf_count=leaf_count)
        else:
            analysis = analyze(sentence)
            tree = analysis["root"]
        errors = [
            {key: finding.get(key) for key in ("rule_id", "constraint", "node_id")}
            for finding in collect(sentence, tree)
            if finding["status"] == "error"
        ]
        observation = {"probe": label, "sentence": sentence, "errors": errors}
        if args.matrix:
            observation["matrix"] = summarize_matrix(evaluate(tree, text=sentence))
        if args.passive_candidate:
            probe = probe_passive_make(sentence, tree, variety="standard_english")
            observation["passive_make_candidate"] = probe
            if label == "passive causative":
                observation["passive_make_parse"] = fixture if args.fixtures else analysis["parse_string"]
            if not args.fixtures:
                for candidate in probe["candidates"]:
                    edit = candidate["edit_hint"]
                    start, end = edit["char_span"]
                    corrected = sentence[:start] + edit["replacement"] + sentence[end:]
                    corrected_tree = analyze(corrected)["root"]
                    recheck = probe_passive_make(corrected, corrected_tree, variety="standard_english")
                    candidate["reparse_observation"] = {
                        "sentence": corrected,
                        "candidate_count": len(recheck["candidates"]),
                        "candidate_status": recheck["status"],
                    }
                    if args.matrix:
                        candidate["reparse_observation"]["matrix_verdict"] = evaluate(
                            corrected_tree, text=corrected)["summary"]["verdict"]
        if args.modal_candidate:
            observation["modal_candidate"] = observe_candidate(analysis, probe_modal_parser, "MOD", "modal_node_id")
        observations.append(observation)
    print(json.dumps({
        "input": "hand_authored_trees" if args.fixtures else "configured_parser",
        "checker": "ruleset.collect",
        "matrix_included": args.matrix,
        "observations": observations,
    }, indent=2))


if __name__ == "__main__":
    main()
