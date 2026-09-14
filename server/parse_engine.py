"""SynTutor Stage 4 engine: spaCy tokenization/POS + benepar constituency parsing.

Extracts the top-ranked phrase-structure tree directly from benepar's
``span._.parse_string`` (the deterministic parse-string rendering of the
selected tree) and rebuilds it as a serializable node graph.
"""

import re
import warnings

warnings.filterwarnings('ignore')

PARSER_BUNDLE = 'en_core_web_md'
PARSER_MODEL = 'benepar_en3'

_nlp = None
_load_error = None


def load_models():
    """Load the spaCy pipeline with the benepar constituency parser (cached)."""
    global _nlp, _load_error
    if _nlp is not None:
        return _nlp
    if _load_error is not None:
        raise _load_error
    try:
        import spacy
        import benepar  # noqa: F401  (registered component required)
        nlp = spacy.load(PARSER_BUNDLE)
        nlp.add_pipe('benepar', config={'model': PARSER_MODEL})
        _nlp = nlp
        return _nlp
    except Exception as exc:  # pragma: no cover - depends on local model install
        _load_error = exc
        raise exc


class ParseFailure(Exception):
    pass


def parse_parse_string(tree_text):
    """Parse a benepar parse string into a nested list tree.

    Returns ('(S ', ...) list structure:
        ('S', [('NP', [('DT', 'The'), ('JJ', 'clever'), ('NN', 'boy')]),
               ('VP', [('VBZ', 'reads'), ('NP', [('DT', 'a'), ('NN', 'book')])]),
               ('.', '.')])
    """
    tokens = re.findall(r'\(|\)|[^\s()]+', tree_text)
    pos = 0

    def parse():
        nonlocal pos
        if tokens[pos] != '(':
            raise ParseFailure(f'bad parse string at token {pos}')
        pos += 1
        label = tokens[pos]
        pos += 1
        children = []
        while pos < len(tokens) and tokens[pos] != ')':
            if tokens[pos] == '(':
                children.append(parse())
            else:
                word = tokens[pos]
                pos += 1
                children.append((label, word))
                label = None
        pos += 1
        if label is None:
            return children[0] if len(children) == 1 else ('', children)
        return (label, children)

    root = parse()
    if pos != len(tokens):
        raise ParseFailure(f'trailing content at parse token {pos}')
    return root


class NodeBuilder:
    """Turns a tagged list tree into deterministic JSON node objects.

    Node shape:
        {id, type, span:[start,end), surface, children?, pos?, punct?}
    Leaves carry their Penn POS tag as ``type``/``pos``; internal nodes carry
    the phrase label as ``type``. ``span`` is given in token coordinates.
    """

    def __init__(self):
        self._counter = 0
        self._token_i = 0
        self.nodes = {}

    def _next_id(self):
        node_id = f'n{self._counter}'
        self._counter += 1
        return node_id

    @staticmethod
    def _is_punct(pos):
        return pos in ('.', ',', ':', ';', '?', '!', '``', "''", '-RRB-', '-LRB-')

    def build(self, tagged, leaf_count):
        """Build the node graph; returns the root node. ``leaf_count`` is the
        number of tokens in the target sentence (used for the span check)."""
        self._token_i = 0
        root = self._build_node(tagged, is_root=True)
        if self._token_i != leaf_count:
            raise ParseFailure(
                f'span alignment mismatch: tree leaves={self._token_i} tokens={leaf_count}'
            )
        return root

    def _build_node(self, tagged, is_root=False):
        node_id = self._next_id()
        label, payload = tagged
        if isinstance(payload, str):
            start = self._token_i
            self._token_i += 1
            node = {
                'id': node_id,
                'type': label,
                'pos': label,
                'span': [start, start + 1],
                'surface': payload,
                'punct': self._is_punct(label),
            }
            self.nodes[node_id] = node
            return node
        children = [self._build_node(p) for p in payload]
        start = children[0]['span'][0]
        end = children[-1]['span'][1]
        surface = ' '.join(w for c in children for w in [self._leaf_text(c)])
        node = {
            'id': node_id,
            'type': label or ('ROOT' if is_root else 'PHRASE'),
            'span': [start, end],
            'surface': surface,
            'children': children,
        }
        self.nodes[node_id] = node
        return node

    @staticmethod
    def _leaf_text(node):
        if 'children' not in node:
            return node['surface']
        return node['surface']


def token_metadata(nlp, doc, target):
    """Serialize spaCy token metadata for the analysis-sentence span."""
    out = []
    for tok in target:
        out.append({
            'i': tok.i - target.start,
            't': tok.text,
            'pos': tok.pos_,
            'tag': tok.tag_,
            'dep': tok.dep_,
            'head': tok.head.text,
        })
    return out


def analyze(text, sentence_index=0):
    """Full deterministic parse of ``text``, targeting one sentence.

    ``sentence_index`` selects which spaCy sentence (0-based) to parse; it is
    clamped to the detected sentence range. Returns the target sentence, its
    token metadata, the benepar parse string, the rebuilt node graph (root +
    id map), and the full sentence segmentation with character offsets
    (start/end) valid against the exact ``text`` string passed in.
    """
    nlp = load_models()
    doc = nlp(text)
    sents = [s for s in doc.sents]
    if not sents:
        raise ParseFailure('no sentences detected')
    idx = min(max(sentence_index, 0), len(sents) - 1)
    target = sents[idx]
    parse_string = target._.parse_string
    tagged = parse_parse_string(parse_string)
    builder = NodeBuilder()
    root = builder.build(tagged, leaf_count=len(target))
    meta = token_metadata(nlp, doc, target)
    return {
        'sentence': target.text,
        'sentence_index': idx,
        'sentence_count': len(sents),
        'sentences': [{'ordinal': i + 1, 'start': s.start_char, 'end': s.end_char,
                       'text': s.text} for i, s in enumerate(sents)],
        'tokens': meta,
        'parse_string': parse_string,
        'root': root,
        'nodes': builder.nodes,
    }