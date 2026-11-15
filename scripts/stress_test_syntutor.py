"""Stress-test SynTutor on complex sentences and record every observable issue.

Run from the repository root:

    .venv/Scripts/python.exe scripts/stress_test_syntutor.py \
        --output artifacts/syntutor-stress-report.json

The harness is read-only: it calls the same ``build_payload`` the browser uses
and inspects the returned trees, findings, explanation coverage and correction
delta. It never promotes a diagnostic to a grammar verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from api import build_payload  # noqa: E402


CASES = [
    # --- Simple and layered declaratives -------------------------------------
    ("simple-declarative", "The clever boy reads a book."),
    ("copular", "The committee is ready for the review."),
    ("pp-stacking", "The list of items are on the table beside the folder reviews."),
    ("locative-pp", "The keys are on the table beside the folder."),
    ("partitive", "Several of the students have finished the assignment."),
    ("temporal-adjunct", "The team met before the deadline on Friday."),
    # --- Verb frames and auxiliaries ----------------------------------------
    ("progressive", "The researchers have been examining the evidence."),
    ("passive", "The report was submitted by the administrator before the deadline."),
    ("modal-to", "The researchers might to have been examining the evidence when the committee unexpectedly arrived."),
    ("modal-bare", "The researchers might have been examining the evidence."),
    ("ditransitive", "The teacher gave the students a homework and they does it good."),
    ("complex-object", "We found it odd that the committee arrived early."),
    # --- Nominals and relative clauses --------------------------------------
    ("subject-relative", "The professor who the students from several departments believe have submitted the report."),
    ("object-relative", "The report that the administrator submitted before the deadline was accepted."),
    ("reduced-relative", "The students working in the library missed the announcement."),
    ("possessive", "The author's latest book about the region is difficult to find."),
    # --- Clauses and questions ----------------------------------------------
    ("wh-question", "Who did the administrator say that submitted the application before the deadline?"),
    ("embedded-whether", "I wonder whether the committee will accept the revised report."),
    ("embedded-that", "The committee said that the report had been submitted before the deadline."),
    ("comparative", "The new building is taller than the old one."),
    ("subjunctive", "It is vital that he submit the report before Friday."),
    ("conditional", "If the committee arrives early, the review can begin."),
    ("coordination", "The dogs is running and the cat are sleeping."),
    ("topicalization", "This book I gave to Mara last week."),
    ("parenthetical", "My aunt, who lives in Paris, is visiting next month."),
    # --- Ungrammatical multi-error cases ------------------------------------
    ("det-agreement", "These child are tired."),
    ("subject-agreement", "The boy go to school."),
    ("aux-chain", "She don't likes apples."),
    ("perfect-form", "He have went to the store yesterday."),
    ("pronoun-case", "Me and him is going."),
    ("simple-past-form", "I seen him yesterday and he don't care."),
    ("noun-form", "The childs are play in the park."),
    ("article-agreement", "A apple are on the table."),
    ("uncountable", "The teacher gave the students a homework."),
    ("adj-adverb", "The students did good on the exam."),
    ("agreement-relative-scope", "I and he saw the three thieves stealing the car whom was parked on the wrong side."),
    ("number-of-relative-scope", "The number of students who were late surprised me."),
    ("correlative-relative-scope", "Neither the teacher nor I saw the man who was late."),
    ("relative-pronoun-inanimate", "The car whom was parked outside belongs to me."),
    ("relative-pronoun-human", "The man which saw me was late."),
    # --- Long, nested stress sentences --------------------------------------
    ("nested-relative", "The professor who the students believe has submitted the report that the committee requested yesterday was praised."),
    ("long-coordination", "The administrator and the committee reviewed the applications that arrived late and decided that the process should continue."),
    ("nested-question", "Could the administrator explain why the students who submitted the application were not notified?"),
    ("gerund-subject", "Examining the evidence carefully is important for the committee."),
    ("preposition-stranding", "The report that the administrator referred to was submitted late."),
    # --- Coordination --------------------------------------------------------
    ("coord-np-agree", "The teacher and the students were waiting in the hall."),
    ("coord-vp", "She sings and dances every weekend."),
    ("coord-ap", "He is tired but happy."),
    ("coord-three-vp", "They went to the market, bought some fruit, and returned home."),
    ("correlative-either", "Either the manager or the assistant will sign the document."),
    ("correlative-neither", "Neither the students nor the teacher was ready."),
    ("correlative-both", "Both the committee and the staff approved the plan."),
    ("correlative-notonly", "Not only the teacher but also the students were surprised."),
    ("coord-yet", "The book is long, yet it is easy to read."),
    ("coord-pp-or", "We can meet on Monday or on Tuesday."),
    # --- Adverbial / subordinate clauses ------------------------------------
    ("adv-because", "Because the road was closed, we took a different route."),
    ("adv-although", "Although she was tired, she finished the report."),
    ("adv-while", "While the committee was meeting, the phone rang."),
    ("adv-after", "After the students left, the teacher locked the door."),
    ("adv-since", "Since the weather was bad, the trip was cancelled."),
    ("adv-unless", "Unless you hurry, you will miss the train."),
    ("adv-before", "He left before the meeting ended."),
    ("adv-because-final", "The project succeeded because everyone cooperated."),
    ("adv-when-front", "When the bell rang, the children ran outside."),
    ("conditional-if", "If it rains tomorrow, we will stay indoors."),
    # --- Relative clauses ----------------------------------------------------
    ("rel-whose", "The woman whose car was stolen called the police."),
    ("rel-that-object", "The house that Jack built still stands."),
    ("rel-subject", "The students who passed the exam celebrated."),
    ("rel-object-which", "The book which I borrowed from the library is overdue."),
    ("rel-pied-piping", "The man to whom she spoke was her former teacher."),
    ("rel-where", "The city where I grew up has changed."),
    ("rel-why", "The reason why he left remains unclear."),
    ("rel-nonrestrictive", "Her brother, who lives in Canada, is visiting."),
    ("rel-nonrestrictive-which", "The report, which was published yesterday, caused a stir."),
    ("rel-anyone", "Anyone who wants to join should sign up."),
    # --- Wh questions and embedded questions --------------------------------
    ("wh-what", "What did the committee decide?"),
    ("wh-which", "Which book did you choose?"),
    ("wh-where", "Where did they go after the meeting?"),
    ("wh-why", "Why did the manager cancel the appointment?"),
    ("wh-how", "How did the students solve the problem?"),
    ("wh-who-pp", "Who among the candidates is best qualified?"),
    ("yesno-did", "Did the administrator submit the report on time?"),
    ("yesno-has", "Has the committee reviewed the application?"),
    ("yesno-could", "Could you explain why the system failed?"),
    ("embedded-wh-indirect", "I wonder who called last night."),
    # --- Comparatives --------------------------------------------------------
    ("comp-as-as", "She is as tall as her brother."),
    ("comp-more-than", "This exam is easier than the previous one."),
    ("comp-the-more", "The more you practice, the better you become."),
    ("comp-less-than", "He earns less than his colleague."),
    ("comp-superlative", "The second proposal is the most practical."),
    ("comp-the-same-as", "This is the same book as the one I read."),
    ("comp-more-noun", "She has more experience than the other candidates."),
    ("comp-far-worse", "The situation is far worse than we expected."),
    # --- Passives ------------------------------------------------------------
    ("passive-by", "The proposal was approved by the board."),
    ("passive-storm", "The window was broken during the storm."),
    ("passive-ditransitive", "The students were given extra time."),
    ("passive-progressive", "The report is being reviewed by the committee."),
    ("passive-perfect", "The letter has been sent to all members."),
    ("passive-truncated", "Mistakes were made during the process."),
    ("passive-built", "The house was built in 1920."),
    ("passive-modal", "The problem can be solved easily."),
    # --- Modals, tense and aspect -------------------------------------------
    ("modal-perfect", "She must have forgotten the appointment."),
    ("modal-progressive", "They might be waiting outside."),
    ("future-perfect", "The committee will have finished by noon."),
    ("modal-perfect-progressive", "He could have been studying all night."),
    ("should-have", "You should have called before arriving."),
    ("modal-negation", "The train may not arrive on time."),
    ("conditional-perfect", "We would have helped if you had asked."),
    ("future-perfect-by", "By next year, she will have completed the degree."),
    ("past-perfect", "They had already left when we arrived."),
    ("present-perfect-progressive", "I have been working here for five years."),
    # --- Non-finite, control and raising ------------------------------------
    ("inf-want-to", "She wants to learn a new language."),
    ("inf-decide-to", "They decided to postpone the meeting."),
    ("raising-seem", "He seems to be enjoying the course."),
    ("raising-believed", "The report is believed to be accurate."),
    ("ecm-expect", "I expect her to finish the task."),
    ("control-persuade", "The manager persuaded the team to work overtime."),
    ("gerund-subject2", "Walking in the park is relaxing."),
    ("participial-perfect", "Having finished the report, she went home."),
    ("perception-passive", "The children were seen playing in the yard."),
    ("bare-infinitive", "We heard the door close."),
    # --- Clefts, inversion, ellipsis ----------------------------------------
    ("it-cleft", "It was the administrator who approved the request."),
    ("wh-cleft", "What she needs is a longer holiday."),
    ("negative-inversion", "Never have I seen such a storm."),
    ("only-inversion", "Only after the meeting did she realize the mistake."),
    ("locative-inversion", "Here comes the bus."),
    ("so-inversion", "So tired was he that he fell asleep."),
    ("gapping", "They reviewed the first draft and we the second."),
    ("vp-ellipsis", "She can play the piano and he can too."),
    # --- Fronting, extraposition, appositives -------------------------------
    ("topicalization2", "This problem, we can solve together."),
    ("extraposition-that", "It is important that everyone attends the briefing."),
    ("extraposition-seem", "It seems that the committee has changed its mind."),
    ("appositive", "The plan, a bold one, was approved."),
    ("parenthetical-dash", "Her idea — to rebuild the bridge — was expensive."),
    # --- Agreement -----------------------------------------------------------
    ("agree-list", "The list of items is on the table."),
    ("agree-each", "Each of the students has a laptop."),
    ("agree-neither", "Neither of the answers is correct."),
    ("agree-collective", "The committee are divided on the issue."),
    ("agree-existential-are", "There are several reasons for the delay."),
    ("agree-existential-is", "There is a book and two pens on the desk."),
    ("agree-number-of", "The number of applicants has increased."),
    ("agree-a-number-of", "A number of students are absent today."),
    # --- Articles, determiners and quantifiers ------------------------------
    ("det-an-honest", "An honest answer is always appreciated."),
    ("det-a-university", "She bought a university guide and an umbrella."),
    ("quant-little", "There is little water left in the bottle."),
    ("quant-few", "Few students attended the optional lecture."),
    ("quant-much", "We have much work to do before Friday."),
    ("quant-many", "Many people prefer to travel by train."),
    ("quant-both", "Both proposals have merit."),
    ("quant-all", "All the evidence points to one conclusion."),
    # --- Pronouns and prepositions ------------------------------------------
    ("pron-between", "Between you and me, the plan seems risky."),
    ("pron-double-object", "She gave the book to him and me."),
    ("pron-coord-object", "The decision was made by the committee and me."),
    ("pron-coord-subject", "My brother and I went to the market."),
    ("pron-object", "The teacher spoke to us about the project."),
    ("poss-mine-yours", "That book is mine; this one is yours."),
    ("prep-pied-piping", "The report to which she referred was missing."),
    ("prep-stranding-who", "Who did you give the keys to?"),
    # --- Additional ungrammatical probes ------------------------------------
    ("err-list-agree", "The list of items are on the table."),
    ("err-do-not", "She don't like apples."),
    ("err-go", "He go to school every day."),
    ("err-childs", "The childs are playing outside."),
    ("err-seen", "I seen the movie last night."),
    ("err-they-was", "They was late for the meeting."),
    ("err-information", "The information are useful."),
    ("err-a-apples", "A apples are on the table."),
    ("err-can-sings", "He can sings very well."),
    ("err-has-went", "She has went to the store."),
    ("err-which-person", "The man which called was polite."),
    ("err-neither-are", "Neither of the boys are ready."),
    ("err-each-have", "Each of the students have a book."),
    ("err-there-is-many", "There is many reasons for the delay."),
    ("err-number-are", "The number of students are increasing."),
    # --- Long, deeply nested sentences --------------------------------------
    ("deep-relative-1", "The committee that reviewed the proposal which the administrator submitted yesterday approved it."),
    ("deep-conditional", "If the students who missed the deadline explain their situation, the professor may accept the late work."),
    ("deep-relative-2", "The report that she wrote after interviewing the witnesses was praised by the committee that had commissioned it."),
    ("deep-wh", "What the administrator said about the proposal that the committee rejected surprised everyone who attended the meeting."),
    ("deep-concession", "Although the researchers who examined the evidence disagreed, the committee decided that the funding should continue."),
    ("deep-relative-3", "The book that the teacher recommended to the students who were preparing for the exam was out of print."),
    ("deep-wh-2", "Who did the manager say would replace the assistant who resigned last month?"),
    ("deep-passive-relative", "The proposal that the committee discussed at length during the meeting was finally approved."),
    ("deep-temporal", "When the alarm rang, the students who were in the laboratory left the building immediately."),
    ("deep-cleft", "It was the assistant who the manager believed had submitted the report before the deadline."),
]


def _walk(node):
    yield node
    for child in node.get("children") or []:
        yield from _walk(child)


def _error_details(payload):
    return {key: detail for key, detail in (payload.get("node_details") or {}).items()
            if isinstance(detail, dict) and detail.get("status") == "error"}


def _token_indices_for_detail(detail):
    indices = set()
    remediation = detail.get("remediation") or {}
    rows = []
    if isinstance(remediation.get("edit"), dict):
        rows.append(remediation["edit"])
    for row in remediation.get("edits") or []:
        rows.append(row.get("edit") if isinstance(row.get("edit"), dict) else row)
    for edit in rows:
        start, end = edit.get("start"), edit.get("end")
        if isinstance(start, int) and isinstance(end, int):
            indices.update(range(start, end))
    binding = detail.get("canonical_binding") or {}
    for span in binding.get("token_spans") or []:
        if isinstance(span, list) and len(span) == 2:
            indices.update(range(span[0], span[1]))
    if not indices and isinstance(detail.get("span"), list) and len(detail["span"]) == 2:
        indices.update(range(detail["span"][0], detail["span"][1]))
    return indices


def _smallest_for_span(root, span):
    if not (isinstance(span, list) and len(span) == 2):
        return None
    start, end = span
    if not (isinstance(start, int) and isinstance(end, int) and end > start):
        return None
    hits = []
    for node in _walk(root):
        node_span = node.get("token_span")
        if not (isinstance(node_span, list) and len(node_span) == 2):
            continue
        if node_span[0] <= start and end <= node_span[1]:
            hits.append(node)
    if not hits:
        return None
    return min(hits, key=lambda node: (
        0 if not node.get("children") else 1,
        (node.get("token_span") or [0, 0])[1] - (node.get("token_span") or [0, 0])[0],
    ))


def _bound_in_tree(root, detail):
    for span in (detail.get("canonical_binding") or {}).get("token_spans") or []:
        if _smallest_for_span(root, span) is not None:
            return True
    if _smallest_for_span(root, detail.get("span")) is not None:
        return True
    return False


def inspect(case_id, sentence):
    try:
        payload = build_payload(sentence)
    except Exception as exc:  # noqa: BLE001 - a crash is itself an issue
        return {
            "case": case_id, "sentence": sentence, "fatal": True,
            "error": f"{type(exc).__name__}: {exc}", "issues": ["FATAL_PARSE"],
        }
    analysis = payload.get("br_analysis") or {}
    envelope = analysis.get("tree") or analysis.get("working_tree") or {}
    root = envelope.get("root") or {}
    nodes = list(_walk(root)) if root else []
    triangles = [node for node in nodes if node.get("triangle")]
    unlabelled_triangles = [node for node in triangles if not node.get("label")]
    details = _error_details(payload)
    bound_details = set()
    unbound = []
    for key, detail in details.items():
        if detail.get("canonical_node_ids") or detail.get("canonical_node_id"):
            bound_details.add(key)
            continue
        if analysis.get("status") == "unresolved" and root and _bound_in_tree(root, detail):
            bound_details.add(key)
            continue
        unbound.append(key)
    bound_spans = set()
    for key in bound_details:
        bound_spans.update(_token_indices_for_detail(details[key]))
    red_spans = set()
    for detail in details.values():
        red_spans.update(_token_indices_for_detail(detail))
    unbound_red = sorted(red_spans - bound_spans)
    correction = (payload.get("summary") or {}).get("correction") or {}
    impact = correction.get("impact") or {}
    issues = []
    if analysis.get("status") not in {"normalized", "unresolved", "rejected"}:
        issues.append("UNKNOWN_BR_STATUS")
    if not envelope:
        issues.append("NO_TREE")
    if analysis.get("status") == "normalized" and not analysis.get("display_labels"):
        issues.append("NO_DISPLAY_LABELS")
    if analysis.get("status") == "unresolved" and not analysis.get("working_tree"):
        issues.append("UNRESOLVED_WITHOUT_WORKING_TREE")
    if analysis.get("status") == "unresolved" and analysis.get("working_tree") and not analysis.get("working_display_labels"):
        issues.append("WORKING_TREE_WITHOUT_DISPLAY_LABELS")
    if root.get("triangle") and len((root.get("words") or [])) > 4:
        issues.append("WHOLE_SENTENCE_TRIANGLE")
    if unlabelled_triangles:
        issues.append("UNLABELLED_TRIANGLE")
    if unbound:
        issues.append("ERROR_WITHOUT_EXPLANATION_NODE")
    if unbound_red:
        issues.append("RED_WORD_WITHOUT_BOUND_DETAIL")
    actionable_edit = any(
        (detail.get("remediation") or {}).get("edit")
        or (detail.get("remediation") or {}).get("edits")
        for detail in details.values())
    # A whole-sentence correction can legitimately be withheld when the
    # detector rejects the repaired candidate (for example, when another
    # independent issue remains). Flag only when no local executable fix
    # exists at all.
    if (payload.get("summary", {}).get("verdict") == "ungrammatical"
            and not correction and not actionable_edit):
        issues.append("NO_CORRECTION_FOR_UNGRAMMATICAL")
    if impact.get("introduced_count"):
        issues.append("CORRECTION_INTRODUCES_ERRORS")
    if impact and not impact.get("whole_sentence_clean") and impact.get("remaining_count"):
        issues.append("CORRECTION_LEAVES_ERRORS")
    return {
        "case": case_id,
        "sentence": sentence,
        "fatal": False,
        "verdict": (payload.get("summary") or {}).get("verdict"),
        "br_status": analysis.get("status"),
        "br_reasons": [row.get("detail") for row in analysis.get("reasons") or []],
        "has_tree": bool(analysis.get("tree")),
        "has_working_tree": bool(analysis.get("working_tree")),
        "display_labels": bool(analysis.get("display_labels")
                               or analysis.get("working_display_labels")),
        "node_count": len(nodes),
        "triangle_count": len(triangles),
        "unlabelled_triangle_count": len(unlabelled_triangles),
        "error_detail_count": len(details),
        "actionable_edit": actionable_edit,
        "unbound_error_details": unbound,
        "red_tokens": sorted(red_spans),
        "unbound_red_tokens": unbound_red,
        "correction": correction.get("corrected_sentence"),
        "correction_edits": len(correction.get("edits") or []),
        "impact": {
            "resolved": impact.get("resolved_count"),
            "remaining": impact.get("remaining_count"),
            "introduced": impact.get("introduced_count"),
            "whole_sentence_clean": impact.get("whole_sentence_clean"),
        } if impact else None,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/syntutor-stress-report.json")
    args = parser.parse_args()
    results = []
    for index, (case_id, sentence) in enumerate(CASES, 1):
        print(f"[{index}/{len(CASES)}] {case_id}: {sentence[:72]}", flush=True)
        results.append(inspect(case_id, sentence))
    summary = {
        "total": len(results),
        "fatal": sum(row["fatal"] for row in results),
        "normalized": sum(row.get("br_status") == "normalized" for row in results),
        "unresolved": sum(row.get("br_status") == "unresolved" for row in results),
        "with_display_labels": sum(bool(row.get("display_labels")) for row in results),
        "unlabelled_triangles": sum(row.get("unlabelled_triangle_count", 0) for row in results),
        "whole_sentence_triangles": sum("WHOLE_SENTENCE_TRIANGLE" in row.get("issues", [])
                                        for row in results),
        "red_tokens_without_bound_detail": sum(len(row.get("unbound_red_tokens") or [])
                                               for row in results),
        "corrections_with_cascade": sum("CORRECTION_INTRODUCES_ERRORS" in row.get("issues", [])
                                        for row in results),
        "cases_with_issues": sum(bool(row.get("issues")) for row in results),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"summary": summary, "results": results},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
