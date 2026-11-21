"""Cross-component NLP reliability & architecture-preservation regression suite.

Covers Phases A, 2, 3, 4, 5, 6, 7, and 10:
  - Scenario A: Correct grammatical sentences & negative controls (no FPs / false repairs)
  - Scenario B: Verified grammatical errors (rule-backed verdict + valid correction + grounding)
  - Scenario C: Proper-noun preservation & anti-corruption safeguards
  - Scenario D: Independent interrogatives vs. subordinate clauses in learner XAI
  - Scenario E: Burton-Roberts canonical tree normalization & fallback separation
  - Scenario F: Multiple simultaneous errors & non-conflicting repair
  - Scenario G: Public API contract & architecture-preservation verification gate
"""
from __future__ import annotations

import copy
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import api  # noqa: E402
import burton_roberts as br  # noqa: E402
import parse_engine  # noqa: E402
from learner_explanations import compose_learner_explanation  # noqa: E402


REQUIRED_PAYLOAD_KEYS = {
    "meta", "parse", "tree", "candidate_tree", "br_analysis",
    "explanation_evidence", "authority", "canonical_binding",
    "unified_findings", "canonical_evaluation", "cambridge_runtime",
    "cambridge_evaluation", "xai4_partial_evaluation", "xai5_localization",
    "xai6_naturalization", "xai7_unified", "learner_explanation",
    "nodes", "node_details", "summary", "explainers",
}


class NlpReliabilityRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parse_engine.load_models()

    # --- Scenario A: Grammatical sentences & documented false-positive fixes ---
    def test_documented_grammatical_sentences_not_rejected(self):
        grammatical_cases = [
            "I saw him before he left.",
            "Three eggs is plenty.",
            "In twenty years there will be fewer cars in use than there are today.",
            "Sally hasn't cleaned these white oxen.",
            "The mushroom went bad.",
            "The hidden offspring aren't confident.",
            "Tracy passed these art galleries.",
            "However, all of them are limited.",
            "An alumnus doubts every sweater flattens.",
            "So I think we would not be alive if our ancestors did not develop sciences and technologies.",
            "Just searching the internet, we can find out what we want.",
        ]
        for sentence in grammatical_cases:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(
                    payload["summary"]["verdict"], "grammatical",
                    f"False rejection on {sentence!r}: constraints={payload['summary'].get('constraints_fired')}",
                )
                self.assertIsNone(payload["summary"].get("corrected_sentence"))

    def test_it_cleft_reflexive_not_condemned_by_rules(self):
        payload = api.build_payload("It's himself who Robert discusses.")
        self.assertNotIn("C-REFLEXIVE-ANTECEDENT", payload["summary"].get("constraints_fired", []))
        self.assertNotEqual(payload["summary"]["verdict"], "ungrammatical")
        self.assertIsNone(payload["summary"].get("corrected_sentence"))

    # --- Scenario B: Verified grammatical errors + valid repairs + grounding ---
    def test_verified_errors_produce_rule_backed_verdicts_and_valid_repairs(self):
        cases = [
            ("The hid bicycles weren't exposed.", "C-VERB-FORM", "The hidden bicycles weren't exposed."),
            ("The wore skirts aren't important.", "C-VERB-FORM", "The worn skirts aren't important."),
            ("The knew adult was exposed.", "C-VERB-FORM", "The known adult was exposed."),
            ("Teresa hidden every senator.", "C-VERB-FORM", "Teresa hid every senator."),
            ("She gave the book to he.", "C-PREP-PRON-CASE", "She gave the book to him."),
            ("There is two books on the table.", "C-EXISTENTIAL", "There are two books on the table."),
            ("This is a real possibility for the fucture.", "C-SPELLING", "This is a real possibility for the future."),
        ]
        for sentence, expected_constraint, expected_correction in cases:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected_constraint, payload["summary"]["constraints_fired"])
                self.assertEqual(payload["summary"].get("corrected_sentence"), expected_correction)
                # Cross-component display-status truth gating: zero green 'valid' badges
                for detail in payload["node_details"].values():
                    if isinstance(detail, dict):
                        self.assertNotEqual(detail.get("display_status"), "valid")

    def test_gendered_common_noun_reflexive_mismatch_caught(self):
        payload = api.build_payload("The mother praised himself.")
        self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
        self.assertIn("C-REFLEXIVE-ANTECEDENT", payload["summary"]["constraints_fired"])

    # --- Scenario C: Proper-noun preservation ---
    def test_proper_noun_naomi_never_corrupted(self):
        sentence = "A cousin of a lot of dancers anticipates Naomi to aggravate Angela."
        payload = api.build_payload(sentence)
        self.assertNotIn("C-NOUN-FORM", payload["summary"].get("constraints_fired", []))
        corr = payload["summary"].get("corrected_sentence") or ""
        self.assertNotIn("Naomuses", corr)
        self.assertNotIn("Naomus", corr)

    # --- Scenario D: Independent interrogative XAI prose (Defect F4) ---
    def test_independent_questions_not_labeled_subordinate_clauses(self):
        for sentence, expected_phrase in [
            ("What did Jon buy?", "independent wh-question"),
            ("Did Jon buy the book?", "independent yes/no question"),
        ]:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "grammatical")
                fg = payload["explanation_evidence"]["fact_graph"]
                root_prose = compose_learner_explanation(fg, node_id=fg["nodes"][0]["node_id"])["text"]
                self.assertNotIn("subordinate clause", root_prose.lower())
                self.assertIn(expected_phrase, root_prose.lower())

    # --- Scenario E: Burton-Roberts standalone phrase normalization & fallback honesty ---
    def test_standalone_phrase_normalization_without_lookup(self):
        prof = br.convention_profile()
        for phrase in ("beside a stream", "their rather dubious jokes", "called the boss up"):
            with self.subTest(phrase=phrase):
                res = br.normalize_benepar_candidate(parse_engine.analyze(phrase), prof)
                self.assertEqual(res["status"], "normalized")
                self.assertIsInstance(res.get("tree"), dict)

    def test_hyphenated_phrase_does_not_crash_normalizer(self):
        prof = br.convention_profile()
        res = br.normalize_benepar_candidate(parse_engine.analyze("second-hand car salesmen"), prof)
        self.assertIn(res["status"], {"normalized", "unresolved"})

    def test_canonical_projection_never_mutates_benepar_candidate_tree(self):
        for sentence in (
            "It's himself who Robert discusses.",
            "It is obvious that she left early.",
        ):
            with self.subTest(sentence=sentence):
                an = parse_engine.analyze(sentence)
                before = copy.deepcopy(an["root"])
                br.build_canonical_analysis(an)
                self.assertEqual(an["root"], before)

    # --- Scenario F: Multiple simultaneous errors ---
    def test_multiple_simultaneous_errors_separated_and_repaired(self):
        payload = api.build_payload("She go to school with he.")
        self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
        cns = set(payload["summary"]["constraints_fired"])
        self.assertIn("C-SUBJECT-AGREEMENT", cns)
        self.assertIn("C-PREP-PRON-CASE", cns)
        self.assertEqual(payload["summary"].get("corrected_sentence"), "She goes to school with him.")

    # --- Scenario G: Architecture preservation & public API contract gate ---
    def test_public_api_contract_and_authority_boundaries_preserved(self):
        payload = api.build_payload("The researchers have been examining the evidence.")
        self.assertTrue(REQUIRED_PAYLOAD_KEYS.issubset(payload.keys()))
        self.assertEqual(payload["meta"]["parser"], "benepar_en3")
        self.assertEqual(payload["meta"]["spacy"], "en_core_web_md")
        self.assertEqual(payload["meta"]["acceptability_signal_role"], "advisory_only")
        self.assertFalse(payload["meta"]["acceptability_signal_can_create_rule_violation"])
        self.assertEqual(payload["br_analysis"]["status"], "normalized")
        self.assertEqual(payload["canonical_evaluation"]["structure"]["status"], "well_formed")

    # --- Scenario H: Cycle 3 false-repair elimination & precision guards ---
    def test_cycle3_false_repairs_and_grammatical_constructions_preserved(self):
        grammatical = [
            "Dawn's ex-husband wasn't going to one rough grocery store and Becca wasn't going to many.",
            "What they did is reduce the amount of gas consumed.",
            "If we consider an idea within the process of defining reality, it becomes clear.",
            "Candice skated around these oases.",
            "Who could Joel and this fish hurt?",
            "What are Rose and a picture scaring?",
            "What have Brian and Galileo escaped from?",
            "Who haven't Edward's plumbers that had listened to Tonya's daughters questioned?",
            "Every actress's piano teachers skate around five messy college campuses and Carolyn's dentists skate around four.",
            "The teenager does tour at most nine restaurants.",
            "There are very successful politicians that have never tried something new.",
            "Finally, fish farming relates to long-term wastefulness, which can pollute the sea.",
            "Think about and create a fire escape plan.",
            "Larry's oncologists aren't helped by Spain.",
            "On the other hand each academic field needs experts in order to progress.",
        ]
        for sentence in grammatical:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertNotEqual(
                    payload["summary"]["verdict"], "ungrammatical",
                    f"False rejection on {sentence!r}: constraints={payload['summary'].get('constraints_fired')}",
                )
                self.assertIsNone(payload["summary"].get("corrected_sentence"))

    def test_cycle3_negative_controls_still_caught(self):
        for sentence, expected in [
            ("She is go to school.", "C-AUX-FORM"),
            ("There are to many books on the desk.", "C-TO_TOO"),
            ("She bought five book yesterday.", "C-QUANT-PLURAL"),
            ("The car red stopped suddenly.", "C-MOD-POS"),
        ]:
            with self.subTest(sentence=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected, payload["summary"]["constraints_fired"])

    # --- Scenario I: Cycle 4 canonical B-R normalization on complex learner prose ---
    def test_cycle4_complex_learner_constructions_normalize_canonically(self):
        prof = br.convention_profile()
        sentences = [
            "And young people spend more time on their lifestyles.",
            "This will prove the speeding offense so that the police can easily catch them.",
            "Finally, fish farming relates to long-term wastefulness, which can pollute the sea.",
            "Dawn's ex-husband wasn't going to one rough grocery store and Becca wasn't going to many.",
            "I would like to initiate whatever I do in order to get more out of my trip.",
            "second-hand car salesmen",
            "Andy has been on court for five hours now.",
            "What are Rose and a picture scaring?",
        ]
        for sentence in sentences:
            with self.subTest(sentence=sentence):
                res = br.normalize_benepar_candidate(parse_engine.analyze(sentence), prof)
                self.assertEqual(res["status"], "normalized", f"Failed to normalize {sentence!r}: {res.get('reasons')}")
                self.assertTrue(res["validation"]["valid"])

    # --- Scenario J: Cycle 5 syntactic rules (minimal pairs + negative controls) ---
    def test_cycle5_syntactic_rules_catch_errors_without_overgeneralizing(self):
        ungrammatical = [
            ("Those banks had really ever lied.", "C-NPI-LICENSING"),
            ("Even Grace ever reveals Janice.", "C-NPI-LICENSING"),
            ("The doctor that has not referenced Diane might ever move.", "C-NPI-LICENSING"),
            ("Many people who only George likes ever clashed.", "C-NPI-LICENSING"),
            ("Emily is thinking that Samuel will love herself.", "C-REFLEXIVE-ANTECEDENT"),
            ("It's herself who wasn't firing Judy.", "C-REFLEXIVE-ANTECEDENT"),
            ("Steven doesn't think about himself listened to Theresa.", "C-REFLEXIVE-SUBJECT"),
            ("Larry's oncologists aren't struggled by Spain.", "C-INTRANSITIVE-PASSIVE"),
            ("Alan existed that dress.", "C-INTRANSITIVE-OBJECT"),
            ("Tara's contractors drive to.", "C-STRANDED-PREP"),
            ("There was every rug disappearing.", "C-EXISTENTIAL-DEFINITENESS"),
            ("There is willing to be a cat existing.", "C-RAISING-CONTROL"),
            ("William has obliged there to be no guests getting fired.", "C-RAISING-CONTROL"),
            ("Becca wasn't going to many rough.", "C-ELLIPSIS-HEAD"),
            ("Mark discovers what Randolf remembered most analyses.", "C-FILLED-GAP"),
            ("Whose did you see car?", "C-LEFT-BRANCH-ISLAND"),
            ("What is Rose scaring and a picture?", "C-COORD-ISLAND"),
            ("Carrie is pleasant to explore some public park.", "C-TOUGH-COMPLEMENT"),
        ]
        for sentence, expected in ungrammatical:
            with self.subTest(ungrammatical=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected, payload["summary"]["constraints_fired"])

        grammatical_controls = [
            "Have you ever seen this film?",
            "Only teachers ever attend those meetings.",
            "This is the best novel I have ever read.",
            "Emily is thinking that Samuel will love himself.",
            "He was laughed at by everyone.",
            "She slept three hours.",
            "There is every reason to hope.",
            "There is likely to be rain tomorrow.",
            "William has declared there to be no guests getting fired.",
            "Mark discovers what Randolf remembered.",
            "Whose car did you see?",
            "Whose is this?",
            "It is pleasant to explore some public park.",
            "Carrie is pleasant to talk to.",
        ]
        for sentence in grammatical_controls:
            with self.subTest(grammatical_control=sentence):
                payload = api.build_payload(sentence)
                self.assertNotEqual(
                    payload["summary"]["verdict"], "ungrammatical",
                    f"Overgeneralization on {sentence!r}: {payload['summary'].get('constraints_fired')}",
                )

    # --- Scenario K: Cycle 6 XAI explanation accuracy (relative pronouns, C1, PASS/PERF) ---
    def test_cycle6_learner_explanations_accurate_on_relatives_and_auxiliaries(self):
        # Relative pronoun in C2 must NOT be called a 'question'
        rel_payload = api.build_payload("The book which she read was interesting.")
        fg = rel_payload["explanation_evidence"]["fact_graph"]
        which_node = next(n for n in fg["nodes"] if n.get("kind") == "word" and n.get("surface") == "which")
        which_prose = compose_learner_explanation(fg, node_id=which_node["node_id"])["text"].lower()
        self.assertIn("relative pronoun", which_prose)
        self.assertNotIn("front of the question", which_prose)

        # Subordinate C1 clause fragment must NOT be called an 'independent yes/no question'
        sub_payload = api.build_payload("Although she left early.")
        sub_fg = sub_payload["explanation_evidence"]["fact_graph"]
        if sub_fg and sub_fg.get("nodes"):
            root_prose = compose_learner_explanation(sub_fg, node_id=sub_fg["nodes"][0]["node_id"])["text"].lower()
            self.assertNotIn("independent yes/no question", root_prose)

        # Passive & perfect auxiliaries accurately named even with irregular participles
        aux_payload = api.build_payload("The window has been broken by the storm.")
        aux_fg = aux_payload["explanation_evidence"]["fact_graph"]
        has_node = next(n for n in aux_fg["nodes"] if n.get("kind") == "word" and n.get("surface") == "has")
        been_node = next(n for n in aux_fg["nodes"] if n.get("kind") == "word" and n.get("surface") == "been")
        self.assertIn("perfect auxiliary", compose_learner_explanation(aux_fg, node_id=has_node["node_id"])["text"].lower())
        self.assertIn("passive auxiliary", compose_learner_explanation(aux_fg, node_id=been_node["node_id"])["text"].lower())

    # --- Scenario L: Cycle 7 Priority 1 invalid-correction elimination ---
    def test_cycle7_priority1_invalid_corrections_eliminated(self):
        # 1. C-ADJ-ADV: comparative flat adverbs & 'other than' preserved; true flat adverbs caught
        for grammatical in (
            "And they can make a product and sell it cheaper than most countries.",
            "He runs faster than his brother.",
            "Please speak louder so everyone can hear.",
            "She aimed higher than before.",
            "Thus, the environmental issue will encourage more people to consider ways to commute other than driving a car.",
        ):
            with self.subTest(grammatical_adv=grammatical):
                payload = api.build_payload(grammatical)
                self.assertNotIn("C-ADJ-ADV", payload["summary"].get("constraints_fired", []))
                self.assertEqual(payload["summary"]["verdict"], "grammatical")
                self.assertIsNone(payload["summary"].get("corrected_sentence"))

        bad_adv = api.build_payload("He runs quick.")
        self.assertEqual(bad_adv["summary"]["verdict"], "ungrammatical")
        self.assertIn("C-ADJ-ADV", bad_adv["summary"]["constraints_fired"])
        self.assertEqual(bad_adv["summary"].get("corrected_sentence"), "He runs quickly.")

        # 2. C-ARTICLE: article placed before prenominal modifiers; mass nouns exempt
        for sentence, expected_corr in (
            ("She bought red car.", "She bought a red car."),
            ("She bought very tall man.", "She bought a very tall man."),
            (
                "A friend of Pamela hasn't attacked one person and Ann hasn't attacked more unsure person.",
                "A friend of Pamela hasn't attacked one person and Ann hasn't attacked a more unsure person.",
            ),
        ):
            with self.subTest(article_placement=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn("C-ARTICLE", payload["summary"]["constraints_fired"])
                self.assertEqual(payload["summary"].get("corrected_sentence"), expected_corr)
                self.assertNotIn("unsure a person", expected_corr)
                self.assertNotIn("tall a man", expected_corr)

        for mass_ok in (
            "We read on many subjects so we get ample exposure.",
            "Modern society debates capitalism and journalism.",
        ):
            with self.subTest(mass_noun_ok=mass_ok):
                payload = api.build_payload(mass_ok)
                self.assertNotIn("C-ARTICLE", payload["summary"].get("constraints_fired", []))
                self.assertEqual(payload["summary"]["verdict"], "grammatical")

        # 3. C-QUANT-PLURAL vs C-ELLIPSIS-HEAD: adjectives in ellipsis never pluralized
        for ellipsis_bad in (
            "Jerry was cleaning few public parks and some grandson of Ann was cleaning many gray.",
            "Bill's associate fires a lot of popular adults and Galileo fires a few old.",
        ):
            with self.subTest(ellipsis_bad=ellipsis_bad):
                payload = api.build_payload(ellipsis_bad)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn("C-ELLIPSIS-HEAD", payload["summary"]["constraints_fired"])
                self.assertNotIn("C-QUANT-PLURAL", payload["summary"]["constraints_fired"])
                corr = payload["summary"].get("corrected_sentence") or ""
                self.assertNotIn("grays", corr.lower())
                self.assertNotIn("olds", corr.lower())

        # Genuine quantifier-plural errors still caught and repaired
        for quant_bad, expected_corr in (
            ("She bought five book yesterday.", "She bought five books yesterday."),
            ("He ate three orange.", "He ate three oranges."),
        ):
            with self.subTest(quant_bad=quant_bad):
                payload = api.build_payload(quant_bad)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn("C-QUANT-PLURAL", payload["summary"]["constraints_fired"])
                self.assertEqual(payload["summary"].get("corrected_sentence"), expected_corr)

    # --- Scenario M: Cycle 7 Priority 2 syntactic recall with strict controls ---
    def test_cycle7_priority2_syntactic_rules_and_controls(self):
        ungrammatical = [
            ("Who can't Douglas realize who had investigated?", "C-WH-ISLAND"),
            ("What could Jessica sell these spotlights before noticing?", "C-ADJUNCT-ISLAND"),
            ("Who might Rose flee from this customer before returning to?", "C-ADJUNCT-ISLAND"),
            ("Who wouldn't Katherine forget all mothers of Florence who disturbed?", "C-COMPLEX-NP-ISLAND"),
            ("Who couldn't Carmen observe nephews of Victoria that did conceal?", "C-COMPLEX-NP-ISLAND"),
            ("What could that legislature bother and Janice?", "C-COORD-ISLAND"),
            ("What is Aaron lifting mountains and that woman insulting?", "C-COORD-ISLAND"),
            ("Which has Thomas disliked waiters?", "C-LEFT-BRANCH-ISLAND"),
            ("Veronica investigated who students might remember Julie.", "C-FILLED-GAP"),
            ("The Lutherans know what some fungi were alarming that association.", "C-FILLED-GAP"),
            ("Most teachers question what some actresses that Melissa boasted about walk through a closet.", "C-FILLED-GAP"),
            ("That shawl reveals.", "C-MISSING-OBJECT"),
            ("Sarah should forget that some waiter dislikes.", "C-MISSING-OBJECT"),
            ("George forgets that some car has looked like.", "C-STRANDED-PREP"),
            ("Some drivers are apt to listen to.", "C-STRANDED-PREP"),
            ("There are most rugs embarrassing Galileo.", "C-EXISTENTIAL-DEFINITENESS"),
            ("Gregory is pushing there to be a movie irritating Douglas.", "C-RAISING-CONTROL"),
            ("Ronald asked it to be not so pleasant that those actors hide away.", "C-RAISING-CONTROL"),
            ("There didn't bother to be more than three commentaries confusing Frank.", "C-RAISING-CONTROL"),
            ("This doctor's cousins aren't interesting to question Kirsten.", "C-TOUGH-COMPLEMENT"),
            ("All actors appeared Tonya's brothers.", "C-INTRANSITIVE-OBJECT"),
            ("Mitchell's grandfathers are concurred.", "C-INTRANSITIVE-PASSIVE"),
            ("Kristen hasn't worked with itself.", "C-REFLEXIVE-ANTECEDENT"),
            ("A lot of girls had bothered himself.", "C-REFLEXIVE-ANTECEDENT"),
            ("Lori wasn't hiring that delighted men.", "C-DETERMINER-AGREEMENT"),
        ]
        for sentence, expected in ungrammatical:
            with self.subTest(ungrammatical=sentence):
                payload = api.build_payload(sentence)
                self.assertEqual(payload["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected, payload["summary"]["constraints_fired"])
                # Truth gating: zero green 'valid' badges
                for detail in payload["node_details"].values():
                    if isinstance(detail, dict):
                        self.assertNotEqual(detail.get("display_status"), "valid")

        grammatical_controls = [
            "Who can't Douglas realize he had investigated?",
            "Who knows what she bought?",
            "What did Jessica file before reading?",
            "Who wouldn't all mothers of Florence who disturbed Katherine forget?",
            "Which did Thomas dislike?",
            "The Lutherans know that some fungi were alarming that association.",
            "Most patients investigate most patients that Sonia was insulting.",
            "It's itself that that pork would stun.",
            "A lot of mothers of Steve observe.",
            "A lot of girls had bothered themselves.",
            "I myself like to participate in these kinds of activities.",
            "The last thing they have to study is disease, which means they will be safe.",
            "Fourth, they have a great chance to prepare for their future life.",
            "They make very high profits year after year and the numbers also increase year after year.",
            "There turned out to be more than three college campuses falling.",
            "The cashiers should notice a lot of cafes that Roger will drop by that resemble all prints.",
            "Jane can discover whose dogs?",
        ]
        for sentence in grammatical_controls:
            with self.subTest(grammatical_control=sentence):
                payload = api.build_payload(sentence)
                self.assertNotEqual(
                    payload["summary"]["verdict"], "ungrammatical",
                    f"False positive on {sentence!r}: constraints={payload['summary'].get('constraints_fired')}",
                )

    # --- Scenario N: Cycle 7 Priority 3 canonical B-R trees on learner writing ---
    def test_cycle7_priority3_learner_trees_and_honest_fragments(self):
        prof = br.convention_profile()
        recoverable = [
            "And they can make a product and sell it cheaper than most countries.",
            "In a market economy, the price must reflect the cost of the product and the consumer's willingness to buy the product.",
            "Fourth, they have a great chance to prepare for their future life.",
            "There are editors to review the new information.",
            "This is the cheapest way for people to take a trip.",
            "For example, they can play football whenever they want, but the elders cannot.",
            "However, are these things good to all people?",
            "Once you get success why would you not get it next time?",
            "I myself like to participate in these kinds of activities.",
            "Students can focus on only a few subjects they are interested in and they will become experts in those areas.",
            "But most of the time it is important because most students are not heard.",
            "Thus, even today, sex is considered as the least important topic in many parts of India.",
            "Many Scientists obtained clear results of investigations after the facts were on the table, but before they could even begin to theorize about them.",
            "You will face huge difficulties in life if you don't know at least something from every subject.",
        ]
        for sentence in recoverable:
            with self.subTest(recoverable=sentence):
                res = br.normalize_benepar_candidate(parse_engine.analyze(sentence), prof)
                self.assertEqual(res["status"], "normalized", f"Failed on {sentence!r}: {res.get('reasons')}")
                self.assertTrue(res["validation"]["valid"])

        # Legitimate unsupported fragments / malformed L2 inputs stay honest working_tree fallbacks
        for fragment in (
            "4:they have a big chance to prepare for their future life",
            "Which caused her situation to be worse.",
        ):
            with self.subTest(honest_fragment=fragment):
                res = br.normalize_benepar_candidate(parse_engine.analyze(fragment), prof)
                self.assertNotEqual(res["status"], "normalized")
                self.assertTrue(bool(res.get("working_tree")))

    # --- Scenario O: Cycle 7 Priority 6 XAI prose on VP ellipsis & new rules ---
    def test_cycle7_priority6_xai_vp_ellipsis_and_new_rule_grounding(self):
        vp_ellip_payload = api.build_payload("For example, they can play football whenever they want, but the elders cannot.")
        self.assertEqual(vp_ellip_payload["br_analysis"]["status"], "normalized")
        fg = vp_ellip_payload["explanation_evidence"]["fact_graph"]
        elided_nodes = [n for n in fg["nodes"] if n.get("kind") in {"empty", "elided_terminal"} and n.get("label") == "E"]
        self.assertTrue(elided_nodes, "Expected elided VP terminal E in canonical fact graph")
        prose = compose_learner_explanation(fg, node_id=elided_nodes[0]["node_id"])["text"].lower()
        self.assertIn("verb-phrase", prose)
        self.assertIn("ellipsis", prose)

        # New rule explanations are grounded and contain zero internal rule codes
        for sent in (
            "Who can't Douglas realize who had investigated?",
            "What could Jessica sell these spotlights before noticing?",
            "That shawl reveals.",
        ):
            p = api.build_payload(sent)
            errs = [d for d in p["node_details"].values() if isinstance(d, dict) and d.get("status") == "error"]
            self.assertTrue(errs)
            for d in errs:
                txt = (d.get("text") or "").strip()
                self.assertTrue(txt)
                self.assertNotIn("C-", txt)

    # --- Scenario P: Cycle 8 Priority 3 correction safety & meaning preservation ---
    def test_cycle8_correction_safety_and_meaning_preservation(self):
        # 1. Contraction polarity preservation: 'dont' -> "don't", NEVER 'do'
        p_dont = api.build_payload("You will face huge difficulties in life if you dont know at least something from every subject.")
        self.assertEqual(p_dont["summary"]["verdict"], "ungrammatical")
        self.assertIn("C-CONTRACTION", p_dont["summary"]["constraints_fired"])
        corr_dont = p_dont["summary"].get("corrected_sentence")
        self.assertIsNotNone(corr_dont)
        self.assertIn("don't", corr_dont.lower())
        self.assertNotIn("if you do know", corr_dont.lower())

        p_doesnt = api.build_payload("She doesnt like cold weather.")
        self.assertEqual(p_doesnt["summary"].get("corrected_sentence"), "She doesn't like cold weather.")

        # 2. Structural island violations NEVER emit prose-scraped Frankenstein edits
        for island_sent in (
            "What could Jessica sell these spotlights before noticing?",
            "Whose had Irene messed up rug?",
            "Who can't Douglas realize who had investigated?",
            "Who wouldn't Katherine forget all mothers of Florence who disturbed?",
        ):
            with self.subTest(island_no_garbage=island_sent):
                p = api.build_payload(island_sent)
                self.assertEqual(p["summary"]["verdict"], "ungrammatical")
                self.assertIsNone(
                    p["summary"].get("corrected_sentence"),
                    f"Unexpected non-local correction on {island_sent!r}: {p['summary'].get('corrected_sentence')!r}",
                )

        # 3. Plural count quantifier + singular countable noun pluralizes the noun
        #    rather than changing 'a few' -> 'a little' (which distorts meaning).
        p_few = api.build_payload("Renee helps one girlfriend and Roger helps a few ill girlfriend.")
        self.assertEqual(p_few["summary"]["verdict"], "ungrammatical")
        self.assertEqual(
            p_few["summary"].get("corrected_sentence"),
            "Renee helps one girlfriend and Roger helps a few ill girlfriends.",
        )

        # 4. Plural-subject predicative nominal preserves plural agreement ('become experts')
        #    while singular-subject keeps singular ('is an expert').
        p_pl = api.build_payload("Students can focus on only a few subjects they are intwerested in and they will become an experts in those areas.")
        self.assertEqual(
            p_pl["summary"].get("corrected_sentence"),
            "Students can focus on only a few subjects they are interested in and they will become experts in those areas.",
        )
        p_sg = api.build_payload("She is an experts in her field.")
        self.assertEqual(p_sg["summary"].get("corrected_sentence"), "She is an expert in her field.")

    # --- Scenario Q: Cycle 8 Priority 2 generalized grammar detection & controls ---
    def test_cycle8_grammar_detection_generalization_and_controls(self):
        grammatical_controls = [
            "What mountains is Aaron lifting and that woman insulting?",
            "Examples: If people who were good did something wrong, they could develop into criminals.",
            "Not only this, but without a clear understanding of what is being taught, the student would not be able to perform well.",
            "My best time was 55 seconds in 400 meters.",
            "We will finish the project in 5 minutes.",
            "She returned in 10 days.",
            "Thus, even today, sex is considered as the least important topic in many parts of India.",
            "Each actor has revealed at most four shawls.",
            "No man has revealed more than five forks.",
            "I know what a great teacher she is.",
            "She came home early.",
            "They came a long way.",
            "She became more unsure after the meeting.",
            "He returned more confident from the trip.",
            "The elders spoke clearly about the traditions.",
        ]
        for sentence in grammatical_controls:
            with self.subTest(grammatical_control=sentence):
                p = api.build_payload(sentence)
                self.assertNotEqual(
                    p["summary"]["verdict"], "ungrammatical",
                    f"False positive on {sentence!r}: {p['summary'].get('constraints_fired')}",
                )

        ungrammatical = [
            ("No man has revealed at least five forks.", "C-SUPERLATIVE-QUANT"),
            ("No actor has revealed at most four shawls.", "C-SUPERLATIVE-QUANT"),
            ("No person would bring at most three gates.", "C-SUPERLATIVE-QUANT"),
            ("Some turtles come here Kimberley.", "C-INTRANSITIVE-OBJECT"),
            ("A friend of Pamela hasn't attacked one unemployed person and Ann hasn't attacked more unsure.", "C-ELLIPSIS-HEAD"),
            ("The cashiers should notice what a lot of cafes that Roger will drop by resemble all prints.", "C-FILLED-GAP"),
            ("Also they have more responsibilities than young person.", "C-ARTICLE"),
            ("As the cities were smallers, there was less traffic.", "C-LEXICON-MALFORMED"),
            ("They can play football whenever they want, but the olders cannot.", "C-LEXICON-MALFORMED"),
            ("The meeting starts in 3:30.", "C-TIME-PLACE-PREP"),
        ]
        for sentence, expected in ungrammatical:
            with self.subTest(ungrammatical=sentence):
                p = api.build_payload(sentence)
                self.assertEqual(p["summary"]["verdict"], "ungrammatical")
                self.assertIn(expected, p["summary"]["constraints_fired"])

    # --- Scenario R: Cycle 8 Priority 4 recoverable B-R trees vs honest fallbacks ---
    def test_cycle8_recoverable_br_trees_and_honest_fallbacks(self):
        prof = br.convention_profile()
        for sent in (
            "If there are specialized doctors, the doctor has done the operation very often before, so he is really talented in his job.",
            "Many Scientists obtained clear results of investigations after the facts were on the table before they could even begin to theorise about them.",
            "However, are these things all good to people?",
            "As the cities were smaller, there was less violence, noise, traffic, etc.",
            "Fourth, they have a great chance to prepare for their future life.",
        ):
            with self.subTest(recoverable_br=sent):
                res = br.normalize_benepar_candidate(parse_engine.analyze(sent), prof)
                self.assertEqual(res["status"], "normalized", f"Failed on {sent!r}: {res.get('reasons')}")
                self.assertTrue(res["validation"]["valid"])

        # Ungrammatical duplicate determiner / typo fragments must NOT be fabricated into canonical trees
        for raw_bad in (
            "Most of the the things I hear are not true.",
            "Which caused her situation to be worse.",
        ):
            with self.subTest(honest_fallback=raw_bad):
                res = br.normalize_benepar_candidate(parse_engine.analyze(raw_bad), prof)
                self.assertNotEqual(res["status"], "normalized")
                self.assertTrue(bool(res.get("working_tree")))

    # --- Scenario S: Cycle 8 Priority 5 end-to-end XAI chain on Cycles 5-8 rules ---
    def test_cycle8_end_to_end_xai_consistency_new_rules(self):
        cases = [
            "No man has revealed at least five forks.",
            "A friend of Pamela hasn't attacked one unemployed person and Ann hasn't attacked more unsure.",
            "Some turtles come here Kimberley.",
            "You will face huge difficulties in life if you dont know at least something from every subject.",
            "The cashiers should notice what a lot of cafes that Roger will drop by resemble all prints.",
        ]
        for sent in cases:
            with self.subTest(xai_chain=sent):
                p = api.build_payload(sent)
                self.assertEqual(p["summary"]["verdict"], "ungrammatical")
                errs = [d for d in p["node_details"].values() if isinstance(d, dict) and d.get("status") == "error"]
                self.assertTrue(errs)
                for d in p["node_details"].values():
                    if isinstance(d, dict):
                        self.assertNotEqual(d.get("display_status"), "valid")
                for e in errs:
                    txt = (e.get("text") or "").strip()
                    self.assertTrue(txt)
                    self.assertNotIn("C-", txt)
                if p["br_analysis"].get("status") == "normalized":
                    fg = p["explanation_evidence"]["fact_graph"]
                    self.assertTrue(fg.get("nodes"))
                    for n in fg["nodes"][:8]:
                        prose = (compose_learner_explanation(fg, node_id=n["node_id"]).get("text") or "").strip()
                        self.assertTrue(prose)


if __name__ == "__main__":
    unittest.main()
