"""Regression tests for Phase II & III H01/H02 reliability engineering improvements.

Covers expanded B-R verb frames, exceptive PPs, phrasal verbs with stranded
prepositions, whether-clause subjects, British English lexicon licensing,
number-transparent quantifiers, distributive coordination, supportive do-support,
auxiliary ordering, modal polarity, pronoun case, reflexives, determiners,
institutional articles, non-dative/IO-only complementation, active ECM,
prohibited passives, NPI licensing, punctuation, possessive it's, and determinism.
"""
import unittest

import analysis_api
import burton_roberts as br
import parse_engine


class H01ProjectionReliabilityTests(unittest.TestCase):
    def _assert_normalized(self, sentence):
        an = parse_engine.analyze(sentence)
        res = br.build_canonical_analysis(an)
        self.assertEqual(res["status"], "normalized", f"Failed to normalize: {sentence} -> {res.get('diagnostics')}")
        self.assertIsNotNone(res.get("tree"))

    def test_expanded_ditransitive_and_complex_frames(self):
        for sent in [
            "Maya feeds the sparrows breadcrumbs.",
            "We wished our guests a pleasant journey.",
            "The jury awarded Elena the first prize.",
            "The council nominated Clara spokesperson.",
            "The judges proclaimed the sculpture a masterpiece.",
        ]:
            with self.subTest(sentence=sent):
                self._assert_normalized(sent)

    def test_exceptive_pp_and_stranded_preposition_frames(self):
        for sent in [
            "I trust nobody but him.",
            "What did Sara turn up in?",
            "Which alley did the runner dash down into?",
            "Which envelope did Hannah put the receipt in?",
        ]:
            with self.subTest(sentence=sent):
                self._assert_normalized(sent)

    def test_whether_clause_subject_and_ambiguity_guard(self):
        self._assert_normalized("Whether Mark or Paul would be chosen was unclear.")
        # Deliberate Burton-Roberts 3rd-ed. 'since' guard must remain unresolved
        an = parse_engine.analyze("Since he left, everything changed.")
        res = br.build_canonical_analysis(an)
        self.assertEqual(res["status"], "unresolved")


class H02GrammarReliabilityTests(unittest.TestCase):
    def _analyze(self, sentence):
        return analysis_api.build_payload(sentence)["summary"]

    def test_grammatical_near_neighbors_have_zero_false_positives(self):
        for sent in [
            "The circus artistes rehearsed under the tent.",
            "Her favourite colour appeared in all the programmes.",
            "Every letter and every parcel was delivered before noon.",
            "A number of cyclists are waiting at the gate.",
            "The number of applicants has doubled this year.",
            "Heaps of sand was piled beside the wall.",
            "She is three years my senior.",
            "Do be patient while the system restarts.",
            "They don't have enough time for lunch.",
            "Nobody but her noticed the cracked tile.",
            "A further few volunteers joined the crew.",
            "The council has yet to announce the winner.",
            "The director, however, confirmed that the contract was valid.",
            "It's a quiet village near the coast.",
        ]:
            with self.subTest(sentence=sent):
                sm = self._analyze(sent)
                self.assertEqual(
                    sm["verdict"], "grammatical",
                    f"False positive on grammatical control: {sent} -> {sm.get('constraints_fired')}",
                )

    def test_ungrammatical_detection_and_valid_corrections(self):
        cases = [
            ("Did Thomas be reckless?", "Was Thomas reckless?"),
            ("They don't have departed yet.", "They haven't departed yet."),
            ("She used to can play the cello.", "She used to be able to play the cello."),
            ("He may must leave early.", "He may have to leave early."),
            ("You need stay until dusk.", "You need to stay until dusk."),
            ("The roof is been repaired.", "The roof is being repaired."),
            ("A number of trees has fallen across the road.", "A number of trees have fallen across the road."),
            ("The number of errors have increased.", "The number of errors has increased."),
            ("Every letter and every parcel were delivered on time.", "Every letter and every parcel was delivered on time."),
            ("Lots of luggage were stacked by the door.", "Lots of luggage was stacked by the door."),
            ("This committee are reviewing the budget.", "This committee is reviewing the budget."),
            ("She gained many knowledges during the trip.", "She gained much knowledge during the trip."),
            ("Both brothers are four years my seniors.", "Both brothers are four years my senior."),
            ("She picked a much more better route.", "She picked a much better route."),
            ("Us know I.", "We know me."),
            ("Did us miss the ferry?", "Did we miss the ferry?"),
            ("The pilot arrived early, didn't him?", "The pilot arrived early, didn't he?"),
            ("Nobody but she knew the password.", "Nobody but her knew the password."),
            ("She was beside her with excitement.", "She was beside herself with excitement."),
            ("I have no coins on myself.", "I have no coins on me."),
            ("Almost each visitor signed the guestbook.", "Almost every visitor signed the guestbook."),
            ("Her each remark drew applause.", "Her every remark drew applause."),
            ("The postcards cost two dollars every.", "The postcards cost two dollars each."),
            ("A further many parcels arrived today.", "A further few parcels arrived today."),
            ("She works at Ministry of Education.", "She works at the Ministry of Education."),
            ("She donated her old library five hundred dollars.", "She donated five hundred dollars to her old library."),
            ("The clerk spared the long queue for her.", "The clerk spared her the long queue."),
            ("They say him to be recovering.", "They say that he is recovering."),
            ("The parcels have arrived yet.", "The parcels have arrived already."),
            ("It was announced, that the ferry was delayed.", "It was announced that the ferry was delayed."),
            ("The technician restored it's original sheen.", "The technician restored its original sheen."),
            ("It's colour faded in the sun.", "Its colour faded in the sun."),
        ]
        for bad, expected in cases:
            with self.subTest(sentence=bad):
                sm = self._analyze(bad)
                self.assertEqual(sm["verdict"], "ungrammatical", f"Missed: {bad}")
                self.assertEqual(sm.get("corrected_sentence"), expected, f"Bad correction for: {bad}")

    def test_determinism_on_repeated_runs(self):
        sent = "Every letter and every parcel were delivered on time."
        r1 = analysis_api.build_payload(sent)
        r2 = analysis_api.build_payload(sent)
        self.assertEqual(r1["summary"]["verdict"], r2["summary"]["verdict"])
        self.assertEqual(r1["summary"]["corrected_sentence"], r2["summary"]["corrected_sentence"])
        self.assertEqual(r1["summary"]["constraints_fired"], r2["summary"]["constraints_fired"])


if __name__ == "__main__":
    unittest.main()
