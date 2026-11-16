"""Acceptance stress test for the syntax generator.

50 varied grammatical sentences and 36 known-bad sentences are run through the
real parser + rule matrix.  The script reports:

* acceptance: every valid sentence should be ``grammatical``
* false positives: no invalid sentence should be ``grammatical``
* B-R coverage: canonical status and triangulated nodes
* explanation coverage: every visible tree node has a non-empty explanation

Run from the repository root:
    python server/stress_syntax_generator.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload

VALID = [
    "The cat sleeps.",
    "The dogs bark loudly.",
    "She is reading a book.",
    "They have finished their homework.",
    "The children were playing in the garden.",
    "He will visit his grandmother tomorrow.",
    "We can solve this problem together.",
    "The teacher gave the students a test.",
    "My brother bought a new bicycle.",
    "The girl with the red hat is my sister.",
    "The man who lives next door works at the hospital.",
    "I think that the plan will succeed.",
    "She said that she was tired.",
    "The book was written by a famous author.",
    "The window was broken during the storm.",
    "If it rains, we will stay inside.",
    "Unless you hurry, you will miss the train.",
    "Although he was tired, he finished the work.",
    "The more you practice, the better you become.",
    "Running every morning keeps him healthy.",
    "To learn a language requires patience.",
    "She enjoys listening to classical music.",
    "He promised to help us.",
    "There is a small park near the station.",
    "There are many reasons to celebrate.",
    "What did you buy at the market?",
    "Where are the keys?",
    "Why is she laughing?",
    "Never have I seen such a beautiful sunset.",
    "Please close the door.",
    "Do not touch the paintings.",
    "The tall boy in the blue jacket plays basketball.",
    "Her younger sister studies medicine.",
    "The city where I grew up has changed.",
    "The news surprised everyone.",
    "Mathematics is difficult but rewarding.",
    "Neither the manager nor the employees were informed.",
    "Either the twins or their mother is coming.",
    "The committee has reached a decision.",
    "The police are investigating the case.",
    "He has been working here for five years.",
    "By next year, she will have completed her degree.",
    "The letter should have arrived yesterday.",
    "You must not smoke in this building.",
    "The children made their parents proud.",
    "We found the room empty.",
    "She considers him a friend.",
    "The project, which began in January, is almost finished.",
    "He asked whether I wanted coffee.",
    "The students were given extra time.",
]

INVALID = [
    "The boys are walks.",
    "The boys is walking.",
    "She are happy.",
    "They walks to school.",
    "He have a car.",
    "The dog bark loudly.",
    "I seen him yesterday.",
    "She has went home.",
    "They was late.",
    "The children is playing.",
    "He can goes.",
    "She must to go.",
    "I am agree.",
    "He don't like coffee.",
    "The peoples are here.",
    "A apple is on the table.",
    "These book are new.",
    "He gave to me a book.",
    "I look forward to see you.",
    "Listen music every day.",
    "She said me the truth.",
    "The man which lives here.",
    "Me and him went home.",
    "There is many problems.",
    "The house was build in 1990.",
    "She very happy.",
    "Because I was late.",
    "He runs quick.",
    "The car red is mine.",
    "I have less books than you.",
    "The boy which won the race.",
    "She can sings well.",
    "It was happened yesterday.",
    "I am knowing the answer.",
    "The team are playing good.",
    "Him is my friend.",
]


def report(text, payload):
    summary = payload.get('summary', {})
    analysis = payload.get('br_analysis', {})
    root = (analysis.get('tree') or {}).get('root')

    def triangles(node):
        if not node:
            return 0
        return (1 if node.get('triangle') else 0) + sum(
            triangles(child) for child in node.get('children', []))

    tree_nodes = []

    def walk(node):
        if not node:
            return
        tree_nodes.append(node['id'])
        for child in node.get('children', []):
            walk(child)

    walk(payload.get('tree'))
    details = payload.get('node_details') or {}
    missing = [node_id for node_id in tree_nodes if node_id not in details]
    empty = [node_id for node_id, detail in details.items()
             if not (detail.get('text') or detail.get('explanation'))]
    return {
        'text': text,
        'verdict': summary.get('verdict'),
        'analysis': analysis.get('status'),
        'triangles': triangles(root) if root else None,
        'nodes': len(tree_nodes),
        'missing_explanations': missing,
        'empty_explanations': empty,
        'generic_fallbacks': sum(
            1 for detail in details.values()
            if detail.get('status') in ('unlisted', 'unverified')
            or detail.get('constraint') == 'C-UNLISTED'),
    }


def main():
    valid = [report(text, build_payload(text)) for text in VALID]
    invalid = [report(text, build_payload(text)) for text in INVALID]

    valid_rejected = [item for item in valid if item['verdict'] != 'grammatical']
    false_positives = [item for item in invalid if item['verdict'] == 'grammatical']
    unresolved = [item for item in valid if item['analysis'] not in ('normalized', 'gold')]
    triangles = [item for item in valid if item['triangles']]
    uncovered = [item for item in valid
                 if item['missing_explanations'] or item['empty_explanations']]

    print(f"valid sentences: {len(valid)}")
    print(f"  accepted: {len(valid) - len(valid_rejected)}/{len(valid)}")
    print(f"  canonical trees resolved: {len(valid) - len(unresolved)}/{len(valid)}")
    print(f"  triangles in resolved trees: {len(triangles)}")
    print(f"  nodes missing an explanation: {len(uncovered)} sentences")
    print("  generic C-UNLISTED explanations: "
          f"{sum(item['generic_fallbacks'] for item in valid)}")
    print("invalid sentences:")
    print(f"  rejected: {len(invalid) - len(false_positives)}/{len(invalid)}")
    print(f"  false positives: {len(false_positives)}")

    for item in valid_rejected:
        print(f"  REJECTED {item['text']} -> {item['verdict']}")
    for item in unresolved:
        print(f"  UNRESOLVED {item['text']} -> {item['analysis']}")
    for item in false_positives:
        print(f"  FALSE POSITIVE {item['text']}")
    for item in uncovered:
        print(f"  UNCOVERED {item['text']} -> {item['missing_explanations']} "
              f"{item['empty_explanations']}")


if __name__ == '__main__':
    main()
