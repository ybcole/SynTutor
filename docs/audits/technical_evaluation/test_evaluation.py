import unittest
from run_technical_evaluation import _extract_spans, score_parseval_pair, aggregate_parseval, compute_binary_metrics

class EvaluationTests(unittest.TestCase):
    def test_reference_triangle_independent_of_parser_failure(self):
        gold = {'label':'NP','triangle':True,'words':['the','cat']}
        reference_flag = bool(_extract_spans(gold)[2])
        failed = {'normalized':False,'yield_match':False,'has_multiword_triangle':reference_flag}
        self.assertTrue(reference_flag)
        self.assertEqual([r for r in [failed] if not r['has_multiword_triangle']], [])

    def test_unresolved_retained_in_total_exact_match(self):
        ok = {'normalized':True,'yield_match':True,'gold_count':2,'pred_count':2,'labeled_match':2,'unlabeled_match':2,'exact_match':True}
        fail = {'normalized':False,'yield_match':False}
        result = aggregate_parseval([ok,fail])
        self.assertEqual(result['exact_rate_over_total'], .5)
        self.assertEqual(result['n_yield_aligned'], 1)

    def test_triangle_aware_does_not_remove_outer_attachment(self):
        gold = {'label':'S','children':[{'label':'NP','triangle':True,'words':['the','cat']},{'label':'VP','children':[{'word':'slept'}]}]}
        wrong = {'label':'S','children':[{'label':'VP','children':[{'word':'the'},{'word':'cat'}]},{'label':'NP','children':[{'word':'slept'}]}]}
        score = score_parseval_pair(gold,wrong,True)
        self.assertTrue(score['yield_match'])
        self.assertFalse(score['exact_match'])

if __name__ == '__main__':
    unittest.main()
