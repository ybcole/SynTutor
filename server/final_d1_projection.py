"""Compositional FINAL-D1 projection from Benepar structure and token evidence."""
from dataclasses import dataclass
from copy import deepcopy

if __package__:
    from .ruleset import PAST_ONLY, contracted_verb_class, passive_adjunct_parts
else:
    from ruleset import PAST_ONLY, contracted_verb_class, passive_adjunct_parts

CLAUSE = ("Ch2 pp. 29–30",)
NOUN = ("Ch7 pp. 141–144",)
NOMINAL = ("Ch7 pp. 165–168",)
PARTITIVE_PREDET = ("Ch7 pp. 145–146 [18]–[20]", "Ch7 p. 156 [74]–[75]")
LOCATIVE = ("Ch3 p. 57 [19]", "Ch4 pp. 74–75, 78")
DEICTIC_P = ("Ch3 pp. 56–57",)
ADVERBIAL = ("Ch5 pp. 87–93",)
AUXILIARY = ("Ch6 pp. 114–132",)
ELLIPSIS = ("Ch5 pp. 95–99",)
SUBORDINATE = ("Ch8 pp. 173–187",)
WH = ("Ch9 pp. 196–211",)
TOPIC = ("Ch6 pp. 128–132",)
NONFINITE = ("Ch10 pp. 224–243",)
COORD = ("Ch3 pp. 57–66",)
STORAGE_LABEL = {"S′": "S-bar", "S″": "S-dbar"}
FRAME_REFS = {
    "intrans": ("Ch4 pp. 71–72 [22]",), "trans": ("Ch4 pp. 70–71 [21]",),
    "ditrans": ("Ch4 pp. 72–75",), "intens": ("Ch4 pp. 74–76",),
    "complex": ("Ch4 pp. 76–77",), "prep": ("Ch4 pp. 77–79",),
}
NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
ADJ_TAGS = {"JJ", "JJR", "JJS"}
ADV_TAGS = {"RB", "RBR", "RBS"}
VERB_TAGS = {"VB", "VBP", "VBZ", "VBD", "VBG", "VBN", "MD"}
CENTRAL_MODALS = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
DETERMINERS = {
    **dict.fromkeys(("a", "an", "the"), "ART"),
    **dict.fromkeys(("this", "that", "these", "those"), "DEM"),
    **dict.fromkeys(("some", "any", "no", "each", "every", "either", "neither", "several", "enough"), "Q"),
}
POSSESSIVE_DETERMINERS = {
    "my", "your", "his", "her", "its", "our", "their", "whose", "thy", "one's",
}
DEGREE = {"very", "too", "rather", "quite", "so", "as", "more", "most", "less", "least", "somewhat", "how", "almost", "extremely", "fairly", "any"}
QA = {"many", "few", "much", "little", "more", "less", "fewer", "most", "least"}
PREDET = {"all", "both", "half", "double", "twice"}
PRONOUNS = {
    "everyone", "everybody", "everything", "anyone", "anybody", "anything",
    "someone", "somebody", "something", "nobody", "nothing", "none",
}
POSSESSIVE_PRONOUNS = {"mine", "yours", "his", "hers", "ours", "theirs"}
SUBORDINATORS = {"if", "unless", "because", "although", "though", "while", "whereas", "when", "once", "as", "until", "before", "after", "since", "than", "whether", "where", "whenever", "wherever", "so", "lest", "except"}
MULTIWORD_SUBORDINATORS = {
    ("so", "that"), ("in", "order", "that"), ("in", "order", "to"), ("in", "order"),
    ("even", "though"), ("even", "if"), ("now", "that"), ("except", "that"),
    ("as", "if"), ("as", "though"), ("as", "soon", "as"), ("as", "long", "as"),
    ("as", "far", "as"), ("provided", "that"), ("providing", "that"),
    ("given", "that"), ("seeing", "that"), ("such", "that"), ("in", "case"),
    ("rather", "than"), ("so", "as"), ("just", "as"), ("only", "if"),
    ("not", "only"), ("but", "also"), ("by", "the", "time"), ("for", "fear", "that"),
}
MULTIWORD_PREPOSITIONS = {
    ("such", "as"), ("due", "to"), ("prior", "to"), ("next", "to"), ("close", "to"),
    ("according", "to"), ("instead", "of"), ("because", "of"), ("out", "of"),
    ("apart", "from"), ("aside", "from"), ("rather", "than"), ("along", "with"),
    ("together", "with"), ("up", "to"), ("as", "for"), ("as", "to"),
    ("except", "for"), ("other", "than"), ("away", "from"), ("ahead", "of"),
    ("regardless", "of"), ("contrary", "to"), ("thanks", "to"), ("subject", "to"),
}
TEMPORAL_P = {"after", "before", "until"}
TIME_NOUNS = {"today", "tomorrow", "yesterday", "tonight", "night", "morning", "afternoon", "evening", "week", "month", "year", "day", "time", "moment", "hour", "minute", "second", "decade", "century"}
LOCATIVE_WORDS = {"here", "there", "upstairs", "downstairs", "outside", "inside"}
TEMPORAL_P_WORDS = {"now", "then"}
LOCATIVE_PREPOSITIONS = {"above", "across", "against", "along", "at", "behind", "below", "beside",
                        "between", "beyond", "by", "in", "inside", "near", "on", "outside", "under"}
INTENSIVE = {"be", "become", "seem", "appear", "look", "feel", "sound", "taste", "smell", "remain", "get", "grow", "prove", "stay", "turn"}
COMPLEX = {"call", "consider", "find", "keep", "make", "paint", "put", "place", "render", "name", "elect", "turn", "get", "drive", "leave", "hold", "declare", "deem"}
DITRANSITIVE = {"give", "tell", "show", "send", "offer", "lend", "bring", "pay", "buy", "hand", "teach", "ask", "promise", "write", "read", "pass", "sell", "owe", "leave", "remind", "inform", "warn", "assure", "convince", "persuade", "notify", "advise", "ensure"}
RECIPIENT_TO = {"give", "show", "send", "offer", "lend", "hand", "pass", "sell"}
SELECTED_PP = {
    "refer": {"to"}, "glance": {"at"}, "look": {"at", "for", "after"}, "listen": {"to"},
    "rely": {"on"}, "depend": {"on", "upon"}, "belong": {"to"}, "think": {"of", "about"},
    "talk": {"to", "about"}, "reply": {"to"}, "wait": {"for"}, "ask": {"for"},
    "deal": {"with"}, "agree": {"with", "to", "on"}, "result": {"in", "from"},
    "believe": {"in"}, "consist": {"of"}, "arrive": set(),
}
TIME_UNITS = {"second", "minute", "hour", "day", "week", "month", "year", "moment"}
KNOWN_INTRANS = {"arrive", "die", "disappear", "bark", "rain", "sneeze", "happen", "occur"}
REQUIRES_COMPLEMENT = {"demolish", "use", "dread", "inspect", "spot", "put", "make", "devour"}
TYPE_I = {"believe", "expect", "prefer", "want", "know", "hear", "watch", "like", "suppose", "consider", "imagine", "find", "see", "notice", "feel", "help", "declare", "prove", "allow", "cause", "enable", "let", "have", "need", "require", "wish"}
PASSIVE_TYPE_I = {"assume", "believe", "consider", "expect", "know", "report", "say", "suppose", "think", "declare", "find", "prove", "show", "understand", "allege", "claim"}
TYPE_II = {"persuade", "ask", "encourage", "force", "invite", "order", "tell", "teach", "promise", "advise", "require", "allow", "oblige", "entice", "convince", "remind", "warn", "permit", "enable", "cause", "help", "get", "lead", "urge", "command", "instruct", "compel"}
SUBJECT_CONTROL = {"agree", "ask", "begin", "continue", "decide", "fail", "forget", "hope", "intend", "learn", "like", "love", "manage", "need", "offer", "plan", "prefer", "promise", "refuse", "remember", "start", "stop", "try", "want", "enjoy", "avoid", "afford", "choose", "aim", "attempt", "tend", "seem", "appear", "happen", "mean", "wish", "desire", "seek", "strive", "prepare", "expect", "claim", "pretend", "hesitate", "dare", "ought", "use", "have", "go", "come"}
CONTROL_ADJECTIVES = {"anxious", "eager", "keen", "hesitant", "unwilling", "willing", "happy", "liable", "reluctant", "ready", "able", "unable", "glad", "proud", "afraid", "sorry", "pleased", "delighted", "prepared", "determined", "free", "quick", "slow", "careful", "ashamed", "content", "lucky", "fortunate", "welcome"}
RAISING_ADJECTIVES = {"likely", "unlikely", "sure", "certain", "bound", "apt", "supposed", "due", "set"}
OBJECT_GAP_ADJECTIVES = {"easy", "hard", "difficult", "tough", "tiresome", "boring", "enjoyable", "disgusting", "delicious", "impossible", "worth", "interesting", "pleasant", "unpleasant", "nice", "fun", "safe", "dangerous", "helpful", "useful", "simple", "awkward", "painful", "expensive", "cheap", "good", "bad", "great", "wonderful", "terrible", "fine"}
CLAUSAL_NOUNS = {
    "fact", "idea", "claim", "news", "belief", "rumour", "rumor", "report",
    "decision", "question", "possibility", "thought", "conclusion",
    "suggestion", "plan", "promise", "wish", "need",
    "evidence", "chance", "opportunity", "willingness", "ability", "inability",
    "attempt", "effort", "desire", "right", "duty", "way", "reason", "power",
    "freedom", "tendency", "failure", "refusal", "proof", "sign", "indication",
    "cause", "assumption", "argument", "feeling", "sense", "impression",
    "view", "opinion", "risk", "hope", "fear", "doubt", "notion", "concept",
    "theory", "hypothesis", "rule", "law", "principle", "condition",
    "requirement", "guarantee", "warning", "message", "statement",
    "observation", "finding", "discovery", "knowledge", "understanding",
    "goal", "aim", "purpose", "intention", "order", "request", "offer",
    "threat", "permission", "authority", "obligation", "responsibility",
}


class ProjectionUnavailable(ValueError):
    """A construction lacks an unambiguous projection rule."""


def branch(label, refs, *children, features=()):
    node = {"label": STORAGE_LABEL.get(label, label), "source_refs": list(refs), "children": list(children)}
    if features:
        node["features"] = list(features)
    return node


def tag(node):
    return node["type"]


def word(node):
    return node["surface"].lower().replace("’", "'")


def word_node(node):
    return {"word": node["surface"]}


def leaf(node):
    return not node.get("children") and "surface" in node


def kids(node):
    return [child for child in node.get("children", []) if not (
        leaf(child) and (
            child.get("punct")
            or child["surface"] in {"[", "]", "(", ")", ":", ";", ".", "?", "!", "\u2026", "..."}
            or (bool(child.get("surface")) and not any(
                ch.isalnum() or ch == "_" for ch in str(child.get("surface", ""))))
        ))]


def raw(label, children):
    return {"type": label, "children": children}


def leaves(node):
    return [node] if leaf(node) else [item for child in kids(node) for item in leaves(child)]


def lemma(node):
    if node.get("fused_aux_base"):
        return node["fused_aux_base"]
    term = word(node)
    if term in {"am", "is", "are", "was", "were", "been", "being", "'m", "'re", "'s"}:
        return "be"
    # Canonical tree validation imports this module without projecting verbs.
    from lemminflect import getLemma

    return next(iter(getLemma(term, upos="VERB", lemmatize_oov=False)), term)


def tense(node, mode):
    if mode == "untensed":
        return None
    if mode == "nonfinite":
        return "-tense"
    if tag(node) not in {"VBZ", "VBP", "VBD", "MD"}:
        raise ProjectionUnavailable("Finite clause has no identifiable tense carrier")
    base_w = node.get("fused_aux_base") or word(node)
    return "past" if tag(node) == "VBD" or base_w in {"could", "might", "should", "would", "'d"} else "pres"


@dataclass
class Gap:
    index: int
    kind: str
    used: bool = False

    def take(self):
        if self.used:
            raise ProjectionUnavailable("One dependency cannot fill multiple positions")
        self.used = True
        return {"gap": True, "index": self.index}


class Projection:
    WORKING_LEAF_LABEL = {
        "MD": "MOD", "TO": "C1", "DT": "DET", "PDT": "DET", "PRP$": "DET",
        "NN": "N", "NNS": "N", "NNP": "N", "NNPS": "N",
        "JJ": "A", "JJR": "A", "JJS": "A",
        "RB": "Adv", "RBR": "Adv", "RBS": "Adv",
        "IN": "P", "PRP": "pronoun", "WP": "pronoun", "EX": "pronoun",
        "CD": "Q", "POS": "POSS",
    }
    WORKING_BRANCH_LABEL = {
        "SQ": "S", "SBARQ": "S", "SINV": "S", "FRAG": "S", "SBAR": "S-bar",
        "NML": "NOM", "NX": "NOM", "WHNP": "NP", "WHADVP": "AdvP",
        "WHPP": "PP", "ADJP": "AP", "ADVP": "AdvP", "PRN": "PP",
        "ROOT": "S", "TOP": "S",
    }

    def working_leaf(self, part):
        if part.get('negative_contraction'):
            result = word_node(part)
            result['notes'] = ['Spelling of a negative contraction is unresolved.']
            return result
        if part.get('contraction_auxiliary') and word(part) in {'do', 'does', 'did'}:
            result = branch('TENSE', (), word_node(part),
                            features=('past' if word(part) == 'did' else 'pres',))
            result['notes'] = ['Auxiliary category supported by token evidence. Grouping remains provisional.']
            return result
        if word(part) in {"'s", "'d"} and tag(part) in VERB_TAGS:
            result = branch('AUX', (), word_node(part))
            result['notes'] = ['The full form of the contracted auxiliary remains uncertain.']
            return result
        if tag(part) == "CC":
            # Coordinators are overt terminals in B-R phrase markers rather
            # than a phrase category of their own.
            return word_node(part)
        if part.get("uncertain_token") or (
            tag(part) in {"DT", "PDT", "PRP$"}
            and word(part) not in (set(DETERMINERS) | POSSESSIVE_DETERMINERS | PREDET)
        ):
            return {
                "triangle": True,
                "words": [part["surface"]],
                "notes": ["Lexical category and spelling of this token remain uncertain."],
            }
        label = self.WORKING_LEAF_LABEL.get(tag(part))
        if tag(part) in VERB_TAGS - {"MD"}:
            child = branch("V", (), word_node(part))
            child["notes"] = ["Verb category only. Frame and tense analysis remain unresolved."]
            return child
        if label:
            if label == "MOD":
                # A modal is a branch with an overt word, not a triangle, so the
                # FINAL-D1 display features can be attached. The form is not
                # established in a provisional tree; mark the default explicitly.
                child = branch("MOD", (), word_node(part), features=("pres",))
                child["notes"] = ["Modal category and provisional present form. "
                                  "The main-verb analysis remains unresolved."]
                return child
            return {"triangle": True, "label": label, "words": [part["surface"]],
                    "notes": ["Category label only. Internal analysis remains unresolved."]}
        return {"triangle": True, "words": [part["surface"]],
                "notes": ["The syntactic role of this word remains unresolved."]}

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.allow_object_gap = 0

    def working_tree(self, node, subject=None):
        """Retain projectable constituents, with explicit local uncertainty."""
        saved_index = self.index
        try:
            if tag(node) in {"ROOT", "TOP", "S", "SQ", "SINV", "SBAR", "SBARQ"}:
                return self.clause(node)
            if tag(node) == "VP" and subject is not None and not subject.get("triangle"):
                trial_subject = deepcopy(subject)
                result = self.vp(kids(node), "finite", trial_subject)
                subject.update(trial_subject)
                return result
            return self.phrase(node)
        except ProjectionUnavailable as exc:
            self.index = saved_index
            reason = str(exc)
        parts = kids(node)
        if tag(node) in {"ROOT", "TOP"} and len(parts) == 1:
            return self.working_tree(parts[0])
        # Never collapse a whole clause into one triangle. Keep the observed
        # constituent order, label known categories, and make the uncertainty
        # local to the span that could not be projected.
        label = self.WORKING_BRANCH_LABEL.get(tag(node), tag(node))
        if parts and label in {"S", "S-bar", "VP", "NP", "NOM", "PP", "AP", "AdvP"}:
            children = []
            for part in parts:
                if leaf(part):
                    child = self.working_leaf(part)
                else:
                    child = self.working_tree(part, subject)
                if tag(node) == "S" and tag(part) == "NP" and not children:
                    subject = child
                children.append(child)
            result = branch(label, (), *children)
            result["notes"] = ["Provisional constituent grouping. " + reason]
            return result
        if tag(node) in {"S", "VP"} and parts:
            children = []
            for part in parts:
                if leaf(part):
                    child = self.working_leaf(part)
                else:
                    child = self.working_tree(part, subject)
                children.append(child)
            result = branch(tag(node), (), *children)
            result["notes"] = ["Provisional constituent grouping. " + reason]
            return result
        result = {"triangle": True, "words": [n["surface"] for n in leaves(node)],
                  "notes": ["Unresolved internal analysis. " + reason]}
        # These identify the candidate phrase category only, not its internals.
        category = {"NP": "NP", "PP": "PP", "ADJP": "AP", "ADVP": "AdvP",
                    "SBAR": "S-bar", "SQ": "S", "SBARQ": "S"}.get(tag(node))
        if category:
            result["label"] = category
        return result

    def dependency(self, node):
        start = node.get("span", [None])[0]
        return self.tokens.get(start, {}).get("dep")

    def gap(self, kind):
        self.index += 1
        return Gap(self.index, kind)

    def coordinate(self, nodes, convert):
        links = [i for i, node in enumerate(nodes) if tag(node) == "CC" and leaf(node)]
        if not links:
            return None
        # Leading discourse coordinator ("And ...", "But ...") is handled by
        # clause()/phrase() callers rather than treated as incomplete binary coordination.
        if links[0] == 0:
            if len(links) == 1:
                return None
            links = links[1:]
        if len(links) == 1:
            i = links[0]
            if not i or i == len(nodes) - 1:
                raise ProjectionUnavailable("Incomplete coordination")
            return convert(nodes[:i]), word_node(nodes[i]), convert(nodes[i + 1:])
        # Multi-way coordination ("A and B and C")
        if any(links[k] + 1 >= links[k + 1] for k in range(len(links) - 1)) or links[-1] == len(nodes) - 1:
            raise ProjectionUnavailable("Incomplete coordination")
        out = []
        prev = 0
        for idx in links:
            out.append(convert(nodes[prev:idx]))
            out.append(word_node(nodes[idx]))
            prev = idx + 1
        out.append(convert(nodes[prev:]))
        return tuple(out)

    def phrase(self, node):
        label = tag(node)
        if label == "NP":
            raw_children = node.get("children", [])
            nonrestrictive = {id(child) for preceding, child in zip(raw_children, raw_children[1:])
                              if preceding.get("surface") == "," and tag(child) == "SBAR"}
            return self.np(kids(node), nonrestrictive)
        if label == "PP":
            return self.pp(kids(node))
        if label == "UCP":
            # Coordinated prepositions sharing one NP complement ('up and down the staircase', Ch3 [41a]).
            parts = kids(node)
            if (len(parts) == 4 and leaf(parts[0]) and tag(parts[0]) in {"IN", "RP", "RB"}
                    and leaf(parts[1]) and tag(parts[1]) == "CC"
                    and leaf(parts[2]) and tag(parts[2]) in {"IN", "RP", "RB"}
                    and tag(parts[3]) == "NP"):
                coord_p = branch(
                    "P", COORD,
                    branch("P", COORD, word_node(parts[0])),
                    word_node(parts[1]),
                    branch("P", COORD, word_node(parts[2])),
                )
                return branch("PP", COORD, coord_p, self.phrase(parts[3]))
        if label in {"ADJP", "ADVP"}:
            parts = kids(node)
            if (label == "ADJP" and len(parts) == 1 and leaf(parts[0])
                    and tag(parts[0]) in {"VBN", "VBG"}):
                # A participial predicate ("was surprised", "was missing") is
                # an AP whose head is a participle, not an adjective with no
                # identifiable head.
                participle = branch(
                    "PartP", ("Ch7 pp. 147–148, 158",),
                    branch("V-part", ("Ch7 p. 158",), word_node(parts[0])))
                return branch("AP", ("Ch7 p. 147",), participle)
            # Participial ADJP with modifiers/complements ("so-called",
            # "not based on experience", "disappointed by our evening").
            if (label == "ADJP" and parts
                    and any(leaf(p) and tag(p) in {"VBN", "VBG"} for p in parts)
                    and not any(leaf(p) and tag(p) in ADJ_TAGS for p in parts)):
                p_idx = next(i for i in range(len(parts) - 1, -1, -1)
                             if leaf(parts[i]) and tag(parts[i]) in {"VBN", "VBG"})
                before = [
                    branch("DEG", ("Ch3 pp. 55–56",), word_node(n))
                    if leaf(n) and word(n) in DEGREE
                    else (branch("AdvP", ADVERBIAL, word_node(n)) if leaf(n) and word(n) == "not"
                          else self.phrase(n))
                    for n in parts[:p_idx]
                ]
                after = [self.phrase(n) for n in parts[p_idx + 1:]]
                participle = branch(
                    "PartP", ("Ch7 pp. 147–148, 158",),
                    branch("V-part", ("Ch7 p. 158",), word_node(parts[p_idx])))
                return branch("AP", ("Ch7 p. 147",), *before, participle, *after)
            # ADVP wrapping "as soon as <S>", "cheaper than <NP>", or "very often before"
            if (label == "ADVP" and len(parts) == 2 and tag(parts[0]) == "ADVP"
                    and tag(parts[1]) in {"SBAR", "PP"}):
                base = self.phrase(parts[0])
                second = self.clause(parts[1]) if tag(parts[1]) == "SBAR" else self.phrase(parts[1])
                out_lbl = "AP" if base.get("label") == "AP" else "AdvP"
                return branch(out_lbl, ADVERBIAL, *base["children"], second)
            if label == "ADVP" and len(parts) == 1 and leaf(parts[0]):
                if word(parts[0]) in LOCATIVE_WORDS | TEMPORAL_P_WORDS:
                    refs = LOCATIVE if word(parts[0]) in LOCATIVE_WORDS else DEICTIC_P
                    return branch("PP", refs, branch("P", refs, word_node(parts[0])))
                if tag(parts[0]) in {"IN", "RP"}:
                    return self.pp(parts)
            # Benepar sometimes tags an adjective (or degree adverb + adjective)
            # as ADVP. Project the phrase as AP; the matrix still reports the
            # adjective/adverb choice independently.
            if label == "ADVP" and parts and leaf(parts[-1]) and tag(parts[-1]) in ADJ_TAGS:
                return self.modifier(parts, adjective=True)
            return self.modifier(parts, adjective=label == "ADJP")
        if label == "NML":
            return self.nml_phrase(node)
        if label in {"S", "SQ", "SBARQ", "SBAR", "SINV"}:
            return self.clause(node)
        if leaf(node) and label in ADV_TAGS:
            return self.modifier([node])
        if leaf(node) and label in ADJ_TAGS:
            return self.modifier([node], adjective=True)
        if leaf(node) and label in NOUN_TAGS:
            return branch("N", NOUN, word_node(node))
        if leaf(node) and label == "CD":
            return self.modifier([node], adjective=True, quantifying=True)
        raise ProjectionUnavailable(f"Unsupported {label} phrase")

    def nml_phrase(self, node):
        """Project a Penn Treebank v3 NML compound premodifier ('long-term',
        'second-hand', 'World Cup', '2006') into a schema-valid B-R N/NOM/AP."""
        parts = kids(node)
        if not parts:
            raise ProjectionUnavailable("Empty NML constituent")
        # Single fused hyphenated adjective NML ('second-hand', 'long-term')
        if len(parts) == 1 and leaf(parts[0]) and tag(parts[0]) in ADJ_TAGS:
            return self.modifier(parts, adjective=True)
        # All-noun or proper-noun NML ('World Cup', 'car park')
        if all(leaf(p) and tag(p) in NOUN_TAGS for p in parts):
            nouns = [branch("N", NOUN, word_node(p)) for p in parts]
            return nouns[0] if len(nouns) == 1 else branch("N", NOUN, *nouns)
        # All-numeral NML ('2006' split as '2 0 0 6')
        if all(leaf(p) and tag(p) == "CD" for p in parts):
            return branch("AP", NOUN, *(branch("QA", NOUN, word_node(p)) for p in parts))
        # Modifier + noun compound NML ('long-term', 'second-hand', 'high-speed')
        if leaf(parts[-1]) and tag(parts[-1]) in NOUN_TAGS:
            head_n = branch("N", NOUN, word_node(parts[-1]))
            mods = []
            for p in parts[:-1]:
                if leaf(p) and tag(p) in ADJ_TAGS:
                    mods.append(self.modifier([p], adjective=True))
                elif leaf(p) and tag(p) == "CD":
                    mods.append(self.modifier([p], adjective=True, quantifying=True))
                elif leaf(p) and tag(p) in NOUN_TAGS:
                    mods.append(branch("N", NOUN, word_node(p)))
                elif leaf(p) and tag(p) in ADV_TAGS:
                    mods.append(self.modifier([p]))
                elif leaf(p) and tag(p) in {"VBN", "VBG"}:
                    mods.append(branch("PartP", ("Ch7 pp. 147–148, 158",),
                                       branch("V-part", ("Ch7 p. 158",), word_node(p))))
                else:
                    mods.append(self.phrase(p))
            return branch("NOM", NOMINAL, *mods, head_n)
        # Fallback: try projecting as NP if it has a valid nominal structure
        return self.np(parts)

    def modifier(self, nodes, adjective=False, quantifying=False):
        category = "AP" if adjective else "AdvP"
        refs = ("Ch3 pp. 55–56",)
        if len(nodes) > 1 and leaf(nodes[0]) and tag(nodes[0]) == "CC" and word(nodes[0]) in {"either", "neither", "both"}:
            coordination = self.coordinate(nodes[1:], lambda part: self.modifier(part, adjective, quantifying))
            if coordination:
                return branch(category, COORD, word_node(nodes[0]), *coordination)
        coordination = self.coordinate(nodes, lambda part: self.modifier(part, adjective, quantifying))
        if coordination:
            return branch(category, COORD, *coordination)
        if len(nodes) == 1 and tag(nodes[0]) == ("ADJP" if adjective else "ADVP"):
            return self.phrase(nodes[0])
        if (adjective and nodes and tag(nodes[0]) == "ADJP"
                and all(tag(node) in {"SBAR", "PP"} for node in nodes[1:])):
            base = self.phrase(nodes[0])
            return branch(category, refs, *base["children"],
                          *(self.clause(node) if tag(node) == "SBAR" else self.phrase(node)
                            for node in nodes[1:]))
        # Complex quantifier phrases like "at least as many", "more than seven",
        # "at most nine": build a clean quantifying AP from leaves/phrases.
        if quantifying and len(nodes) >= 2:
            q_head = next((i for i in range(len(nodes) - 1, -1, -1)
                           if leaf(nodes[i]) and (tag(nodes[i]) in ADJ_TAGS | {"CD", "DT", "RB"} or word(nodes[i]) in QA)), None)
            if q_head is not None:
                before = [
                    branch("DEG", refs, word_node(n)) if leaf(n)
                    else self.phrase(n)
                    for n in nodes[:q_head]
                ]
                after = [self.phrase(n) for n in nodes[q_head + 1:]]
                return branch("AP", refs, *before, branch("QA", refs, word_node(nodes[q_head])), *after)
        if (adjective and len(nodes) == 2 and leaf(nodes[0])
                and tag(nodes[0]) == "DT" and word(nodes[0]) in {"all", "both"}
                and tag(nodes[1]) == "ADJP"):
            base = self.phrase(nodes[1])
            return branch(category, refs, branch("DEG", refs, word_node(nodes[0])), *base["children"])
        if (not adjective and len(nodes) == 2 and tag(nodes[0]) == "ADVP"
                and tag(nodes[1]) in {"ADVP", "PP"}):
            return branch(category, refs, self.phrase(nodes[0]), self.phrase(nodes[1]))
        if (not adjective and len(nodes) == 2 and leaf(nodes[0])
                and word(nodes[0]) == "other" and tag(nodes[1]) == "PP"):
            return branch(category, refs, branch("Adv", refs, word_node(nodes[0])), self.phrase(nodes[1]))
        head_tags = ADJ_TAGS | ({"CD", "DT", "NN", "RB"} if quantifying else set()) if adjective else ADV_TAGS | {"LS", "NN", "NNS", "NNP", "NNPS", "IN", "DT"}
        head = next((i for i in range(len(nodes) - 1, -1, -1)
                     if leaf(nodes[i]) and tag(nodes[i]) in head_tags), None)
        if head is None:
            raise ProjectionUnavailable(f"{category} has no identifiable head")
        before = [
            branch("DEG", refs, word_node(n)) if leaf(n) and (
                word(n) in DEGREE or (tag(n) == "DT" and word(n) in {"all", "both", "any", "no", "that", "this"})
            )
            else (branch("AdvP", refs, word_node(n)) if leaf(n) and word(n) == "not"
                  else self.phrase(n))
            for n in nodes[:head]
        ]
        after = [self.phrase(n) for n in nodes[head + 1:]]
        if after and not adjective:
            if len(after) == 1 and tag(nodes[head + 1]) in {"PP", "SBAR"}:
                return branch(category, refs, *before, branch("Adv", refs, word_node(nodes[head])), *after)
            raise ProjectionUnavailable("Unsupported complement of AdvP")
        return branch(category, refs, *before,
                      branch("QA" if quantifying else "A" if adjective else "Adv", refs, word_node(nodes[head])), *after)

    def pp(self, nodes, gap=None):
        coordination = (self.coordinate(nodes, lambda part: self.pp(kids(part[0])) if len(part) == 1 and tag(part[0]) == "PP" else self.pp(part))
                        if gap is None else None)
        if coordination:
            return branch("PP", COORD, *coordination)
        if len(nodes) == 2 and tag(nodes[0]) == "PP" and tag(nodes[1]) in {"ADVP", "PP"} and gap is None:
            return branch("PP", ADVERBIAL, self.phrase(nodes[0]), self.phrase(nodes[1]))
        if len(nodes) > 1 and leaf(nodes[0]) and word(nodes[0]) == "not":
            return branch("PP", ADVERBIAL, word_node(nodes[0]), self.pp(nodes[1:], gap))
        if len(nodes) > 1 and tag(nodes[0]) == "ADVP" and len(nodes) >= 2 and leaf(nodes[1]) and tag(nodes[1]) in {"IN", "TO"}:
            return branch("PP", ADVERBIAL, self.phrase(nodes[0]), self.pp(nodes[1:], gap))
        # Multi-word prepositions ("such as", "due to", "instead of", "because of", ...)
        # Also handle Benepar CONJP wrappers like (PP (CONJP (RB instead) (IN of)) (S ...)).
        if len(nodes) >= 2 and tag(nodes[0]) == "CONJP":
            conjp_lvs = leaves(nodes[0])
            conjp_pair = tuple(word(n) for n in conjp_lvs)
            if conjp_pair in MULTIWORD_PREPOSITIONS or conjp_pair in {
                ("instead", "of"), ("rather", "than"), ("other", "than"),
                ("as", "well", "as"), ("apart", "from"), ("along", "with"),
                ("except", "for"), ("because", "of"), ("due", "to"),
            }:
                head = branch("P", ("Ch3 pp. 56–59",), *(word_node(n) for n in conjp_lvs))
                tail = nodes[1:]
                if gap is not None:
                    if tail:
                        raise ProjectionUnavailable("Preposition already has an overt complement")
                    tail = [branch("NP", WH, gap.take())]
                elif len(tail) == 1 and tag(tail[0]) == "S" and self.is_nonfinite(tail[0]):
                    tail = [self.nonfinite(tail[0], wrap=False)]
                elif len(tail) == 1 and tag(tail[0]) == "S":
                    tail = [self.clause(tail[0])]
                elif len(tail) == 1:
                    tail = [self.phrase(tail[0])]
                elif tail:
                    raise ProjectionUnavailable("PP has multiple unclassified dependents")
                return branch("PP", ("Ch3 pp. 56–59",), head, *tail)
        if (len(nodes) >= 2 and leaf(nodes[0]) and leaf(nodes[1])
                and (word(nodes[0]), word(nodes[1])) in MULTIWORD_PREPOSITIONS):
            head = branch("P", ("Ch3 pp. 56–59",), word_node(nodes[0]), word_node(nodes[1]))
            tail = nodes[2:]
            if gap is not None:
                if tail:
                    raise ProjectionUnavailable("Preposition already has an overt complement")
                tail = [branch("NP", WH, gap.take())]
            elif len(tail) == 1 and tag(tail[0]) == "S" and self.is_nonfinite(tail[0]):
                tail = [self.nonfinite(tail[0], wrap=False)]
            elif len(tail) == 1 and tag(tail[0]) == "S":
                tail = [self.clause(tail[0])]
            elif len(tail) == 1:
                tail = [self.phrase(tail[0])]
            elif tail:
                raise ProjectionUnavailable("PP has multiple unclassified dependents")
            return branch("PP", ("Ch3 pp. 56–59",), head, *tail)
        if not nodes or not leaf(nodes[0]) or tag(nodes[0]) not in {"IN", "TO", "RP", "RB", "VBG"}:
            raise ProjectionUnavailable("PP has no identifiable preposition")
        head = branch("P", ("Ch3 pp. 56–59",), word_node(nodes[0]))
        tail = nodes[1:]
        if gap is not None:
            if tail:
                raise ProjectionUnavailable("Preposition already has an overt complement")
            tail = [branch("NP", WH, gap.take())]
        elif len(tail) == 1 and tag(tail[0]) == "S" and self.is_nonfinite(tail[0]):
            tail = [self.nonfinite(tail[0], wrap=False)]
        elif len(tail) == 1 and tag(tail[0]) == "S":
            tail = [self.clause(tail[0])]
        elif len(tail) == 1:
            tail = [self.phrase(tail[0])]
        elif len(tail) == 2 and tag(tail[0]) in {"IN", "TO", "RB"} and leaf(tail[0]):
            # Compound preposition ("out of X", "up to X", "away from X", "due to X")
            head = branch("P", ("Ch3 pp. 56–59",), word_node(nodes[0]), word_node(tail[0]))
            tail = [self.phrase(tail[1])]
        elif tail:
            raise ProjectionUnavailable("PP has multiple unclassified dependents")
        return branch("PP", ("Ch3 pp. 56–59",), head, *tail)

    def np(self, nodes, nonrestrictive=()):
        if not nodes:
            raise ProjectionUnavailable("Empty overt noun phrase")
        focus = next((i for i in range(len(nodes) - 1)
                      if leaf(nodes[i]) and word(nodes[i]) == "not"
                      and leaf(nodes[i + 1]) and word(nodes[i + 1]) == "even"), None)
        if focus is not None:
            target = self.np(nodes[focus + 2:], nonrestrictive)
            adv = branch("AdvP", ADVERBIAL, word_node(nodes[focus]), word_node(nodes[focus + 1]))
            if focus == 0:
                return branch("NP", ADVERBIAL, adv, target)
            return branch("NP", ADVERBIAL, self.np(nodes[:focus], nonrestrictive), adv, target)
        if len(nodes) > 1 and leaf(nodes[0]) and tag(nodes[0]) in ADV_TAGS and word(nodes[0]) in {"only", "almost", "even", "just", "not", "nearly", "especially", "particularly", "mainly", "mostly", "merely", "simply", "about", "around", "over", "under"}:
            result = branch("NP", NOUN, self.modifier([nodes[0]]), self.np(nodes[1:], nonrestrictive))
            result["notes"] = ["The focusing adverb modifies the following NP."]
            return result
        if len(nodes) == 3 and tag(nodes[1]) == "CC" and any(tag(p) == "PP" for p in (nodes[0], nodes[2])):
            left = self.temporal_pp(nodes[0])
            right = self.temporal_pp(nodes[2])
            if left is not None and right is not None:
                return branch("PP", COORD, left, word_node(nodes[1]), right)
        if (len(nodes) > 3 and leaf(nodes[0]) and tag(nodes[0]) == "CC"
                and word(nodes[0]) in {"either", "neither"}):
            # Correlative subject: CC + NP + CC + NP. The leading either/
            # neither is part of the coordination, but it precedes the first
            # conjunct, so the normal NP CC NP coordinator cannot start here.
            coordination = self.coordinate(
                nodes[1:], lambda part: self.np(part, nonrestrictive))
            if coordination:
                return branch("NP", COORD, word_node(nodes[0]), *coordination)
        if len(nodes) >= 3 and tag(nodes[0]) == "CONJP":
            # Correlative coordination ("Not only the teacher but also the
            # students"). The CONJP material is overt coordinator wording and
            # stays as words rather than an unlabelled triangle.
            children = []
            for part in nodes:
                if tag(part) == "CONJP":
                    children.extend(word_node(lf) for lf in leaves(part) if leaf(lf))
                elif tag(part) == "NP":
                    children.append(self.np(kids(part), nonrestrictive))
                else:
                    children.append(self.phrase(part))
            if len(children) >= 2:
                return branch("NP", COORD, *children)
        coordination = self.coordinate(nodes, lambda part: self.np(part, nonrestrictive))
        if coordination:
            return branch("NP", COORD, *coordination)
        if len(nodes) == 1 and tag(nodes[0]) == "NP":
            return self.phrase(nodes[0])
        if (len(nodes) == 2 and tag(nodes[0]) == "NP" and tag(nodes[1]) == "SBAR"):
            inside = kids(nodes[0])
            if len(inside) == 1 and leaf(inside[0]) and tag(inside[0]) in ADJ_TAGS:
                ap = branch("AP", ("Ch7 p. 147",), branch("A", ("Ch7 p. 147",), word_node(inside[0])))
                return branch("NP", NOUN, ap, self.clause(nodes[1]))
            sbar_parts = kids(nodes[1])
            if (sbar_parts and leaf(sbar_parts[0])
                    and word(sbar_parts[0]) in {"than", "as"}):
                # Comparative as/than clauses are complements, not relatives.
                return branch("NP", NOUN, self.phrase(nodes[0]), self.clause(nodes[1]))
            # Restrictive relative clauses (B-R Ch9 [39], [53a], [59]) and noun-complement
            # clauses (B-R Ch9 [38], [53b]) on DET+NOM NPs attach inside NOM via lines 748-932.
            # Only non-restrictive relatives, names, pronouns, or complex inner NPs without
            # a DET+NOM split attach at NP level here.
            is_name_or_pron = (
                (len(inside) == 1 and leaf(inside[0])
                 and (tag(inside[0]) in {"PRP", "EX", "NNP", "NNPS"}
                      or word(inside[0]) in PRONOUNS | POSSESSIVE_PRONOUNS))
                or all(leaf(n) and tag(n) in {"NNP", "NNPS"} for n in inside)
            )
            if id(nodes[1]) in nonrestrictive or is_name_or_pron:
                head_word = word(leaves(nodes[0])[-1])
                if self.noun_complement(head_word, nodes[1]):
                    return branch("NP", NOUN, self.phrase(nodes[0]), self.clause(nodes[1]))
                return branch("NP", WH, self.phrase(nodes[0]), self.relative(nodes[1]))
        if (len(nodes) == 2 and tag(nodes[0]) == "NP" and tag(nodes[1]) == "NP"
                and kids(nodes[1]) and tag(kids(nodes[1])[0]) == "CONJP"):
            conjunction = kids(nodes[1])[0]
            first = kids(conjunction)
            if (first and leaf(first[0]) and word(first[0]) == "not"
                    and len(first) >= 2 and leaf(first[1]) and word(first[1]) == "even"):
                adverb = branch("AdvP", ADVERBIAL, *(word_node(node) for node in first))
                return branch("NP", ADVERBIAL, self.phrase(nodes[0]), adverb,
                              self.np(kids(nodes[1])[1:]))
        if len(nodes) == 2 and tag(nodes[1]) == "PRN":
            inner = next((child for child in kids(nodes[1]) if tag(child) == "S"), None)
            if inner is not None:
                return branch("NP", ADVERBIAL, self.phrase(nodes[0]), self.clause(inner))
        # Benepar may group a pre-determiner as its own NP before the of-PP.
        # The book keeps it as PRE-DET and represents the omitted head as E.
        if len(nodes) == 2 and tag(nodes[1]) == "PP" and kids(nodes[1]) and word(kids(nodes[1])[0]) == "of":
            first = kids(nodes[0]) if tag(nodes[0]) == "NP" else [nodes[0]]
            if len(first) == 1 and leaf(first[0]) and word(first[0]) in {"all", "both", "half"}:
                return branch("NP", PARTITIVE_PREDET,
                              branch("PRE-DET", PARTITIVE_PREDET, word_node(first[0])),
                              branch("NP", PARTITIVE_PREDET,
                                     branch("DET", PARTITIVE_PREDET),
                                     branch("NOM", PARTITIVE_PREDET,
                                            branch("N", PARTITIVE_PREDET, {"elided": True, "symbol": "E"}),
                                            self.phrase(nodes[1]))))
        if tag(nodes[0]) == "SBAR" and len(nodes) == 1:
            return branch("NP", SUBORDINATE, self.clause(nodes[0]))
        if len(nodes) == 1 and leaf(nodes[0]) and (
                tag(nodes[0]) in {"PRP", "EX", "WP"} or word(nodes[0]) in PRONOUNS
                or word(nodes[0]) in POSSESSIVE_PRONOUNS):
            return branch("NP", NOUN, branch("pronoun", NOUN, word_node(nodes[0])))
        if len(nodes) == 1 and leaf(nodes[0]) and word(nodes[0]) in {"this", "that", "these", "those"}:
            return branch("NP", ("Ch7 pp. 155–157",), branch("DET", NOUN, branch("DEM", NOUN, word_node(nodes[0]))),
                          branch("NOM", NOMINAL, branch("N", NOUN, {"elided": True, "symbol": "E"})))
        if all(leaf(n) and tag(n) in {"NNP", "NNPS"} for n in nodes):
            return branch("NP", NOUN, branch("name", NOUN, *(word_node(n) for n in nodes)))
        if leaf(nodes[-1]) and tag(nodes[-1]) == "POS" and len(nodes) > 1:
            poss = branch("POSS", NOUN, self.np(nodes[:-1]), word_node(nodes[-1]))
            return branch("NP", NOUN, branch("DET", NOUN, poss),
                          branch("NOM", NOMINAL, branch("N", NOUN, {"elided": True, "symbol": "E"})))
        if leaf(nodes[0]) and word(nodes[0]) in PREDET and len(nodes) > 1:
            return branch("NP", NOUN, branch("PRE-DET", NOUN, word_node(nodes[0])), self.np(nodes[1:]))

        if tag(nodes[0]) == "NP" and not (kids(nodes[0]) and tag(kids(nodes[0])[-1]) == "POS"):
            inside = kids(nodes[0])
            if len(inside) > 1 and leaf(inside[0]) and word(inside[0]) in PREDET:
                return branch("NP", NOUN, branch("PRE-DET", NOUN, word_node(inside[0])),
                              self.np([raw("NP", inside[1:]), *nodes[1:]], nonrestrictive))
            # Benepar wraps PRE-DET inside a possessive NP shell:
            # (NP (NP (DT all) (NP Gulbenkian 's)) (NNS contributions)) -> hoist PRE-DET (Ch7 [ex1-e]).
            if (len(inside) >= 2 and tag(inside[0]) == "NP"
                    and kids(inside[0]) and leaf(kids(inside[0])[0])
                    and word(kids(inside[0])[0]) in PREDET
                    and len(kids(inside[0])) == 2 and tag(kids(inside[0])[1]) == "NP"
                    and kids(kids(inside[0])[1]) and tag(kids(kids(inside[0])[1])[-1]) == "POS"):
                predet_leaf = kids(inside[0])[0]
                poss_np = kids(inside[0])[1]
                return branch("NP", NOUN, branch("PRE-DET", NOUN, word_node(predet_leaf)),
                              self.np([raw("NP", [poss_np, *inside[1:]]), *nodes[1:]], nonrestrictive))
            # B-R Ch. 7 Appendix D1: when Benepar wraps a simple premodified NP
            # inside an outer NP before an 'of'-PP complement
            # ((NP (NP that tall student) (PP of maths) (PP in the hat))),
            # flatten so the 'of'-PP complement attaches to N inside NOM before
            # outer premodifiers ('tall') and adjunct PPs ('in the hat').
            if (len(nodes) >= 2 and tag(nodes[1]) == "PP"
                    and kids(nodes[1]) and leaf(kids(nodes[1])[0])
                    and word(kids(nodes[1])[0]) == "of"
                    and inside and not any(tag(c) in {"PP", "SBAR", "S", "VP", "NP"} for c in inside)
                    and any(leaf(c) and tag(c) in NOUN_TAGS for c in inside)):
                return self.np([*inside, *nodes[1:]], nonrestrictive)
            base = self.phrase(nodes[0])
            if len(nodes) == 2 and id(nodes[1]) in nonrestrictive:
                return branch("NP", WH, base, self.relative(nodes[1]))
            if base["children"][0]["label"] == "DET":
                det, nominal = base["children"]
                modifiers = nodes[1:]
                head_word = word(leaves(nodes[0])[-1])
            elif (base["children"][0]["label"] == "AdvP" and len(base["children"]) == 2
                  and base["children"][1].get("label") == "NP"
                  and base["children"][1]["children"][0].get("label") == "DET"):
                # Focusing adverb inside inner NP ("Even a lot of lamps")
                focus_adv = base["children"][0]
                inner_np = self.np([raw("NP", kids(nodes[0])[1:]), *nodes[1:]], nonrestrictive)
                result = branch("NP", NOUN, focus_adv, inner_np)
                result["notes"] = ["The focusing adverb modifies the following NP."]
                return result
            elif base["children"][0]["label"] == "pronoun" and len(nodes) == 2 and tag(nodes[1]) in {"PP", "ADJP"}:
                return branch("NP", ("Ch7 pp. 155–157",), base["children"][0], self.phrase(nodes[1]))
            elif (base["children"][0]["label"] == "pronoun" and len(nodes) == 2 and tag(nodes[1]) == "NP"
                  and len(leaves(nodes[1])) == 1
                  and word(leaves(nodes[1])[0]) in {"myself", "yourself", "himself", "herself", "itself", "ourselves", "yourselves", "themselves"}):
                # Emphatic appositive reflexive ('I myself', 'she herself')
                return branch("NP", ("Ch7 pp. 155–157",), base, self.phrase(nodes[1]))
            elif base["children"][0]["label"] == "name" and len(nodes) == 2 and id(nodes[1]) in nonrestrictive:
                return branch("NP", WH, base, self.relative(nodes[1]))
            else:
                raise ProjectionUnavailable("Unsupported modifier of a name or pronoun")
        else:
            det = branch("DET", ("Ch7 p. 143 [10]",))
            start = 0
            first = nodes[0]
            if any(lf.get("uncertain_token") for n in nodes for lf in leaves(n)):
                raise ProjectionUnavailable("Lexical category cannot be verified for an orthographically uncertain token")
            if leaf(first) and tag(first) in {"PRP$", "DT", "PDT"} and word(first) not in (
                POSSESSIVE_DETERMINERS | set(DETERMINERS) | PREDET
            ):
                raise ProjectionUnavailable("Determiner or possessive category cannot be verified for this token")
            if leaf(first) and ((tag(first) == "PRP$" and word(first) in POSSESSIVE_DETERMINERS) or word(first) in DETERMINERS):
                label = "POSS" if tag(first) == "PRP$" else DETERMINERS[word(first)]
                det = branch("DET", NOUN, branch(label, NOUN, word_node(first)))
                start = 1
            elif tag(first) == "NP" and kids(first) and tag(kids(first)[-1]) == "POS":
                possessive = kids(first)
                det = branch("DET", NOUN, branch("POSS", NOUN, self.np(possessive[:-1]), word_node(possessive[-1])))
                start = 1
            stop = next((i for i in range(start, len(nodes)) if tag(nodes[i]) in {"PP", "SBAR", "S", "VP"}), len(nodes))
            # Benepar sometimes tags nominal one as a cardinal after a
            # comparative adjective. Keep ordinary number uses in QA.
            head = next((i for i in range(stop - 1, start - 1, -1)
                         if leaf(nodes[i]) and (tag(nodes[i]) in NOUN_TAGS or (
                             start and i > start and tag(nodes[i]) == "CD" and word(nodes[i]) == "one"
                             and tag(nodes[i - 1]) in (ADJ_TAGS | {"DT"})))), None)
            if head is None:
                if len(nodes) == 1 and leaf(nodes[0]) and tag(nodes[0]) == "CD":
                    return branch("NP", NOUN, det, branch("NOM", NOMINAL, self.modifier(nodes, adjective=True, quantifying=True)))
                # Elided-head quantifier NP (Ch7 ellipsis convention: "going to
                # many", "loved few", "discovered more", "at least as many"):
                # project the quantifying AP over an explicit empty N(E).
                if (start == 0 and stop >= 1
                        and (
                            (stop == 1 and leaf(nodes[0]) and (word(nodes[0]) in QA or tag(nodes[0]) == "CD"))
                            or (stop == 1 and tag(nodes[0]) == "QP")
                            or (stop == 1 and tag(nodes[0]) == "ADJP"
                                and any(word(lf) in QA or tag(lf) == "CD" for lf in leaves(nodes[0])))
                            or (all(leaf(n) and (word(n) in QA | DEGREE or tag(n) in {"CD", "RB", "IN", "JJS", "JJR"}) for n in nodes[:stop])
                                and any(word(n) in QA or tag(n) == "CD" for n in nodes[:stop]))
                        )):
                    q_nodes = kids(nodes[0]) if (stop == 1 and tag(nodes[0]) in {"QP", "ADJP"}) else nodes[:stop]
                    q_ap = self.modifier(q_nodes, adjective=True, quantifying=True)
                    nominal = branch("NOM", NOMINAL, q_ap,
                                     branch("NOM", NOMINAL, branch("N", NOUN, {"elided": True, "symbol": "E"})))
                    for mod in nodes[stop:]:
                        nominal = branch("NOM", NOMINAL, nominal, self.phrase(mod))
                    return branch("NP", NOUN, det, nominal)
                if start and stop - start <= 1:
                    nominal = branch("NOM", NOMINAL, branch("N", NOUN, {"elided": True, "symbol": "E"}))
                    if start < stop:
                        mod = nodes[start]
                        nominal = branch("NOM", NOMINAL, self.modifier([mod], adjective=True,
                                         quantifying=tag(mod) == "CD" or word(mod) in QA), nominal)
                    for mod in nodes[stop:]:
                        nominal = branch("NOM", NOMINAL, nominal, self.phrase(mod))
                    return branch("NP", NOUN, det, nominal)
                if len(nodes) == 1 and leaf(nodes[0]) and word(nodes[0]) in {"plenty", "several"}:
                    if word(nodes[0]) == "several":
                        return self.np([dict(nodes[0], type="DT")])
                    return branch("NP", NOUN, det, branch("NOM", NOMINAL, branch("N", NOUN, word_node(nodes[0]))))
                raise ProjectionUnavailable("NP has no identifiable noun head")
            head_word = word(nodes[head])
            noun_start = head
            while noun_start > start and leaf(nodes[noun_start - 1]) and tag(nodes[noun_start - 1]) in NOUN_TAGS:
                noun_start -= 1
            pro_nominal = head_word in {"one", "ones"} and (start > 0 or head_word == "ones") and noun_start == head
            if pro_nominal:
                noun = word_node(nodes[head])
            else:
                nouns = [branch("N", NOUN, word_node(n)) for n in nodes[noun_start:head + 1]]
                noun = nouns[0] if len(nouns) == 1 else branch("N", NOUN, *nouns)
            nominal = branch("NOM", NOMINAL, noun)
            modifiers = nodes[head + 1:]
            # Complements of nouns precede any outer premodification in the hierarchy.
            if not pro_nominal and modifiers and self.noun_complement(head_word, modifiers[0]):
                selected = modifiers[0]
                if tag(selected) == "S":
                    controller = det if det["children"] and det["children"][0]["label"] == "POSS" else None
                    complement = self.nonfinite(selected, controller)
                else:
                    complement = self.phrase(selected)
                nominal = branch("NOM", NOMINAL, noun, complement)
                modifiers = modifiers[1:]
            for mod in reversed(nodes[start:noun_start]):
                if leaf(mod) and tag(mod) == "VBG":
                    phrase = branch("PartP", ("Ch7 pp. 147–148, 158",), branch("V-part", ("Ch7 p. 158",), word_node(mod)))
                elif leaf(mod) and tag(mod) == "VBN":
                    # A past-participial premodifier ("the revised report") is a
                    # reduced relative, not an adjective phrase with no head.
                    phrase = branch("PartP", ("Ch7 pp. 147–148, 158",), branch("V-part", ("Ch7 p. 158",), word_node(mod)))
                elif tag(mod) == "ADJP":
                    phrase = self.phrase(mod)
                elif tag(mod) == "ADVP":
                    phrase = self.phrase(mod)
                elif tag(mod) == "NML":
                    phrase = self.nml_phrase(mod)
                elif tag(mod) == "QP":
                    phrase = self.modifier(kids(mod), adjective=True, quantifying=True)
                else:
                    phrase = self.modifier([mod], adjective=True, quantifying=word(mod) in QA or tag(mod) == "CD")
                nominal = branch("NOM", NOMINAL, phrase, nominal)
        for mod in modifiers:
            if tag(mod) == "SBAR":
                sbar_parts = kids(mod)
                if (sbar_parts and leaf(sbar_parts[0])
                        and word(sbar_parts[0]) in {"than", "as"}):
                    phrase = self.clause(mod)
                elif self.noun_complement(head_word, mod):
                    phrase = self.clause(mod)
                    if len(nominal["children"]) == 1 and nominal["children"][0].get("label") == "N":
                        nominal = branch("NOM", NOMINAL, nominal["children"][0], phrase)
                        continue
                    raise ProjectionUnavailable("Noun complement has ambiguous attachment")
                else:
                    try:
                        phrase = self.relative(mod)
                    except ProjectionUnavailable:
                        # B-R Ch9 [53b]: a finite 'that'-clause modifying a noun
                        # whose embedded clause is structurally complete (no gap)
                        # is a noun-complement clause (S-bar -> C1(that) + S),
                        # not a relative clause with a missing object gap.
                        if (len(sbar_parts) == 2 and leaf(sbar_parts[0])
                                and word(sbar_parts[0]) == "that" and tag(sbar_parts[1]) == "S"):
                            phrase = self.clause(mod)
                            if len(nominal["children"]) == 1 and nominal["children"][0].get("label") == "N":
                                nominal = branch("NOM", NOMINAL, nominal["children"][0], phrase)
                                continue
                        else:
                            raise
                if id(mod) in nonrestrictive:
                    return branch("NP", WH, branch("NP", NOUN, det, nominal), phrase)
            elif tag(mod) == "VP" and kids(mod) and tag(kids(mod)[0]) in {"VBG", "VBN"}:
                link = self.gap("subject")
                subject = branch("NP", NONFINITE, link.take())
                passive = Gap(link.index, "object") if tag(kids(mod)[0]) == "VBN" else None
                predicate = self.vp(kids(mod), "nonfinite", subject, passive=passive)
                operator = branch("C2", NONFINITE, {"gap": True, "index": link.index})
                phrase = branch("S″", NONFINITE, operator, branch("S′", NONFINITE,
                                branch("C1", NONFINITE), branch("S", NONFINITE, subject, predicate)))
            elif tag(mod) == "PP" and self.noun_complement(head_word, mod) and len(nominal["children"]) == 1 and nominal["children"][0].get("label") == "N":
                nominal = branch("NOM", NOMINAL, nominal["children"][0], self.phrase(mod))
                continue
            elif tag(mod) == "S" and self.is_nonfinite(mod):
                phrase = self.nonfinite(mod)
            elif tag(mod) in {"PP", "ADJP", "ADVP"}:
                phrase = self.phrase(mod)
            elif tag(mod) == "NP" and self.is_time_np(mod):
                phrase = self.phrase(mod)
            elif leaf(mod) and tag(mod) in ADJ_TAGS:
                phrase = self.modifier([mod], adjective=True)
            elif leaf(mod) and tag(mod) in ADV_TAGS:
                phrase = self.modifier([mod])
            elif leaf(mod) and tag(mod) == "FW" and word(mod).rstrip(".") == "etc":
                phrase = branch("AdvP", ADVERBIAL, branch("Adv", ADVERBIAL, word_node(mod)))
            else:
                raise ProjectionUnavailable(f"Unsupported nominal dependent {tag(mod)}")
            nominal = branch("NOM", NOMINAL, nominal, phrase)
        return branch("NP", NOUN, det, nominal)

    def noun_complement(self, noun, node):
        dependents = kids(node)
        return bool(dependents) and (
            (tag(node) == "S" and self.is_nonfinite(node) and noun in CLAUSAL_NOUNS)
            or
            (tag(node) == "SBAR" and word(dependents[0]) in {"that", "whether"}
             and tag(dependents[0]) in {"IN", "DT"}
             and noun in CLAUSAL_NOUNS)
            or (tag(node) == "PP" and leaf(dependents[0]) and word(dependents[0]) == "of"
                and noun not in PRONOUNS))

    def is_nonfinite(self, node):
        components = kids(node)
        if components and tag(components[-1]) == "S" and len(components) == 2:
            return self.is_nonfinite(components[-1])
        if not components or tag(components[-1]) != "VP":
            return False
        vp = kids(components[-1])
        return bool(vp) and tag(vp[0]) in {"TO", "VB", "VBG", "VBN"}

    def nonfinite(self, node, controller=None, wrap=True, incoming=None):
        parts = kids(node)
        if len(parts) == 2 and tag(parts[-1]) == "S" and len(kids(parts[-1])) == 1:
            parts[-1] = kids(parts[-1])[0]
        if not parts or tag(parts[-1]) != "VP" or len(parts) > 2:
            raise ProjectionUnavailable("Unsupported non-finite clause shape")
        if len(parts) == 2:
            subject = self.phrase(parts[0])
        elif controller is not None:
            link = self.link_subject(controller)
            subject = branch("NP", NONFINITE, link.take())
        else:
            subject = branch("NP", NONFINITE, {"gap": True})
        predicate = self.vp(kids(parts[-1]), "nonfinite", subject, incoming)
        core = branch("S", NONFINITE, subject, predicate)
        return branch("S′", NONFINITE, branch("C1", NONFINITE), core) if wrap else core

    def passive_adjunct(self, parts, controller):
        refs = ('Ch10 p. 246, Discussion 5 [55b]',)
        link = self.link_subject(controller)
        subject = branch('NP', refs, link.take())
        predicate = self.vp(parts, 'nonfinite', subject, passive=Gap(link.index, 'object'))
        return branch('S′', refs, branch('C1', refs), branch('S', refs, subject, predicate))

    def link_subject(self, controller):
        index = controller.get("index")
        if index is None:
            index = next((child["index"] for child in controller["children"]
                          if child.get("gap") and "index" in child), None)
        if index is None:
            index = self.gap("subject").index
            controller["index"] = index
        return Gap(index, "subject")

    def adjunct(self, node):
        if tag(node) == "S" and self.is_nonfinite(node):
            return self.nonfinite(node)
        if tag(node) == "NP" and self.is_time_np(node):
            return self.phrase(node)
        return self.phrase(node)

    def attach(self, tree, label, leading=(), trailing=()):
        for node in reversed(leading):
            tree = branch(label, ADVERBIAL, self.adjunct(node), tree)
        for node in trailing:
            tree = branch(label, ADVERBIAL, tree, self.adjunct(node))
        return tree

    def auxiliary(self, head, tail):
        surface = word(head)
        if (surface in {"'s", "'d"} and len(tail) == 1
                and tag(tail[0]) == 'VP' and kids(tail[0]) and leaf(kids(tail[0])[0])
                and tag(kids(tail[0])[0]) in VERB_TAGS):
            verb = kids(tail[0])[0]
            start = verb.get('span', [None])[0]
            dependents = [node for node in leaves(tail[0]) if start is not None and node.get('fhead') == start]
            kind = contracted_verb_class(head, verb, dependents)
            if kind == 'have':
                return 'PERF'
            if kind == 'modal':
                return 'MOD'
            if kind == 'be':
                return 'PROG' if tag(verb) == 'VBG' else 'PASS'
            raise ProjectionUnavailable('The contracted auxiliary has no uniquely supported verb-form analysis')
        if tag(head) == "MD" or (word(head) in {"need", "dare"} and len(tail) == 1
                                  and tag(tail[0]) == "VP" and kids(tail[0]) and tag(kids(tail[0])[0]) == "VB"):
            return "MOD"
        if tag(head) == "TO":
            return "AUX"
        if len(tail) != 1 or tag(tail[0]) != "VP":
            return None
        # Peel through Benepar's nested VP-adjunction or coordinated-VP wrappers
        # ((VP (VP (VBN observed)) (ADVP at all)) or (VP (VP (VBN accepted)) (CC and) (ADVP quickly) (VP (VBN published))))
        # to inspect the lexical/auxiliary head verb selected by this auxiliary.
        probe = tail[0]
        head_leaf = None
        while tag(probe) == "VP":
            p_kids = kids(probe)
            if not p_kids:
                break
            if leaf(p_kids[0]):
                head_leaf = p_kids[0]
                break
            if tag(p_kids[0]) == "VP":
                probe = p_kids[0]
                continue
            break
        if head_leaf is None:
            return None
        base = lemma(head)
        next_tag = tag(head_leaf)
        if (base == "have" or surface == "'ve") and next_tag in VERB_TAGS:
            if next_tag != 'VBN' or word(head_leaf) in PAST_ONLY:
                raise ProjectionUnavailable('Perfect have requires a past participle')
            return 'PERF'
        if base == "be" and next_tag in VERB_TAGS:
            if next_tag not in {'VBG', 'VBN'} or word(head_leaf) in PAST_ONLY:
                raise ProjectionUnavailable('The VP form does not support a progressive or passive analysis')
            return "PASS" if next_tag == "VBN" else "PROG"
        if base == "do" and next_tag in VERB_TAGS:
            return "TENSE"
        return None

    def predicative(self, node, subject=None):
        children = kids(node)
        if tag(node) == "ADJP":
            if len(children) == 1 and tag(children[0]) == "ADJP":
                return self.predicative(children[0], subject)
            coordinated = self.coordinate(children, lambda part: self.predicative(raw("ADJP", part), subject))
            if coordinated:
                return branch("AP", COORD, *coordinated)
            if len(children) == 2 and leaf(children[0]) and tag(children[0]) in ADJ_TAGS:
                lower = children[1]
                if tag(lower) == "SBAR" and len(kids(lower)) == 1:
                    lower = kids(lower)[0]
                if tag(lower) == "S" and self.is_nonfinite(lower):
                    adjective = word(children[0])
                    if adjective in CONTROL_ADJECTIVES | RAISING_ADJECTIVES and subject is not None:
                        clause = self.nonfinite(lower, subject)
                    elif adjective in OBJECT_GAP_ADJECTIVES and subject is not None:
                        kind = "preposition" if any(tag(n) == "PP" and len(kids(n)) == 1 for n in self.phrase_nodes(lower)) else "object"
                        gap = self.gap(kind)
                        subject["index"] = gap.index
                        clause = self.nonfinite(lower, incoming=gap)
                        if not gap.used:
                            raise ProjectionUnavailable("Adjective complement has no identifiable gap")
                    else:
                        raise ProjectionUnavailable("Adjective complement has no supported dependency analysis")
                    return branch("AP", NONFINITE, branch("A", ("Ch3 p. 55",), word_node(children[0])), clause)
        if tag(node) == "ADVP" and len(children) == 1 and word(children[0]) == "so":
            result = branch("AP", ("Ch3 pp. 55–56",), word_node(children[0]))
            result["notes"] = ["Predicative so stands for an adjectival property."]
            return result
        if tag(node) == "ADVP" and len(kids(node)) == 1 and word(kids(node)[0]) in {"here", "there", "in", "out", "up", "down", "away", "home"}:
            return branch("PP", ("Ch3 pp. 56–59",), branch("P", ("Ch3 pp. 56–59",), word_node(kids(node)[0])))
        return self.phrase(node)

    @staticmethod
    def modal_marked_vp(head, target):
        """Retain an observed extra infinitival marker in a central-modal VP."""
        if tag(head) != "MD" or word(head) not in CENTRAL_MODALS or tag(target) != "S":
            return target
        clause = kids(target)
        if len(clause) != 1 or tag(clause[0]) != "VP":
            return target
        parts = kids(clause[0])
        if len(parts) != 2 or tag(parts[0]) != "TO" or word(parts[0]) != "to" or tag(parts[1]) != "VP":
            return target
        lower = kids(parts[1])
        if not lower or tag(lower[0]) != "VB" or any(tag(node) in {"CC", "CONJP"} for node in lower[1:]):
            return target
        return clause[0]

    @staticmethod
    def bare_causative_complement(tail):
        """Identify an overt bare VP without assigning a role to a marked infinitival."""
        if len(tail) == 2:
            agent = kids(tail[1])
            if (tag(tail[1]) != "PP" or len(agent) != 2
                    or tag(agent[0]) != "IN" or word(agent[0]) != "by" or tag(agent[1]) != "NP"):
                return None
        elif len(tail) != 1:
            return None
        lower = tail[0]
        if tag(lower) == "S":
            parts = kids(lower)
            if len(parts) != 1:
                return None
            lower = parts[0]
        if tag(lower) != "VP":
            return None
        parts = kids(lower)
        if not parts or tag(parts[0]) != "VB" or any(tag(part) in {"CC", "CONJP"} for part in parts[1:]):
            return None
        return raw("S", [lower])

    def peel_finite_vp_adjunct(self, nodes):
        """Separate a witnessed postposed clause from a simple auxiliary chain."""
        if len(nodes) < 2 or not leaf(nodes[0]):
            return nodes, None
        head, last = nodes[0], nodes[-1]
        parts = kids(last)
        if (tag(last) == "SBAR" and len(parts) == 2 and leaf(parts[0])
                and word(parts[0]) in {"because", "if", "unless", "although"}
                and tag(parts[1]) == "S" and not self.is_nonfinite(parts[1])):
            mark, body = parts
            if self.dependency(mark) == "mark" and any(
                    self.dependency(verb) == "advcl"
                    and verb["span"][0] == mark.get("fhead")
                    and verb.get("fhead") == head.get("span", [None])[0]
                    for verb in leaves(body)):
                return nodes[:-1], last
        # A selected clausal complement, coordination or negative scope is a
        # boundary. Follow only an auxiliary's single nested VP.
        if len(nodes) == 2 and tag(last) == "VP" and self.auxiliary(head, [last]):
            inner, adjunct = self.peel_finite_vp_adjunct(parts)
            if adjunct is not None:
                return [head, {**last, "children": inner}], adjunct
        return nodes, None

    def vp(self, nodes, mode, subject, incoming=None, passive=None, fronted=None):
        if not nodes:
            raise ProjectionUnavailable("Missing verb phrase")
        if len(nodes) > 3 and tag(nodes[1]) == "CC" and all(leaf(nodes[i]) and tag(nodes[i]) in VERB_TAGS for i in (0, 2)):
            if incoming or passive or fronted or tag(nodes[0]) != tag(nodes[2]):
                raise ProjectionUnavailable("Unresolved dependency on coordinated verb heads")
            right = self.vp(nodes[2:], mode, subject)
            lexical = right["children"][0]
            if lexical["label"] != "V" or lexical.get("features", [None])[0] != "trans" or lemma(nodes[0]) in KNOWN_INTRANS | INTENSIVE:
                raise ProjectionUnavailable("Coordinated heads have no shared licensed complement frame")
            left = branch("V", COORD, word_node(nodes[0]), features=lexical["features"])
            right["children"][0] = branch("V", COORD, left, word_node(nodes[1]), lexical,
                                          features=lexical["features"])
            return right
        if (len(nodes) >= 3
                and sum(1 for node in nodes if tag(node) == "VP") >= 2
                and all(tag(node) in {"VP", ",", "CC", "ADVP"} for node in nodes)):
            # Coordinated predicates sharing one subject: "went to the market,
            # bought some fruit, and returned home" or "was accepted and quickly
            # published".
            children = []
            idx = 0
            vp_count = 0
            while idx < len(nodes):
                part = nodes[idx]
                if tag(part) == "ADVP" and idx + 1 < len(nodes) and tag(nodes[idx + 1]) == "VP":
                    conj_passive = (
                        Gap(passive.index, passive.kind) if (passive is not None and vp_count > 0) else passive
                    )
                    vp_tree = self.vp(kids(nodes[idx + 1]), mode, subject, incoming, conj_passive, fronted)
                    children.append(self.attach(vp_tree, "VP", leading=[part]))
                    vp_count += 1
                    idx += 2
                elif tag(part) == "VP":
                    conj_passive = (
                        Gap(passive.index, passive.kind) if (passive is not None and vp_count > 0) else passive
                    )
                    children.append(self.vp(kids(part), mode, subject, incoming, conj_passive, fronted))
                    vp_count += 1
                    idx += 1
                elif leaf(part):
                    children.append(word_node(part))
                    idx += 1
                else:
                    children.append(self.phrase(part))
                    idx += 1
            return branch("VP", COORD, *children)
        coordination = self.coordinate(nodes, lambda part: self.vp(part, mode, subject))
        if coordination:
            if incoming or passive or fronted:
                raise ProjectionUnavailable("Movement across a coordinated VP")
            return branch("VP", COORD, *coordination)
        if tag(nodes[0]) == "VP":
            return self.attach(self.vp(kids(nodes[0]), mode, subject, incoming, passive, fronted), "VP", trailing=nodes[1:])
        head, *tail = nodes
        if not leaf(head) or tag(head) not in VERB_TAGS | {"TO"}:
            raise ProjectionUnavailable(f"VP has no identifiable verb ({tag(head)})")
        negation = None
        if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"}:
            negation = tail.pop(0)
        # An auxiliary can be followed by adverbials or floating quantifiers
        # ('we are all taking...', 'they have both finished') before its VP complement.
        auxiliary_tail = [
            node for node in tail
            if tag(node) != "ADVP"
            and not (leaf(node) and tag(node) == "DT" and word(node) in {"all", "both", "each"})
        ]
        aux = self.auxiliary(head, auxiliary_tail)
        # Modal/auxiliary VP-ellipsis ('the elders cannot.', 'she did not.', 'he will.'):
        # project VP -> MOD/TENSE/PERF/PROG + VP(E) per B-R Ch. 5 pp. 95-99.
        if (not auxiliary_tail and not tail and incoming is None and passive is None
                and (tag(head) == "MD" or (negation is not None and lemma(head) in {"do", "have", "be"}))):
            ellip_label = (
                "MOD" if tag(head) == "MD"
                else "TENSE" if lemma(head) == "do"
                else "PERF" if lemma(head) == "have"
                else "PROG"
            )
            ellip_tense = tense(head, mode)
            head_words = [fronted.take() if fronted else word_node(head)]
            if negation:
                head_words.append(word_node(negation))
            return branch(
                "VP", (*AUXILIARY, *ELLIPSIS),
                branch(ellip_label, AUXILIARY, *head_words,
                       features=(ellip_tense,) if ellip_tense else ()),
                branch("VP", ELLIPSIS, {"elided": True, "symbol": "E"}),
            )
        head_words = [fronted.take() if fronted else word_node(head)]
        if negation:
            head_words.append(word_node(negation))
        if aux:
            if len(auxiliary_tail) != 1:
                raise ProjectionUnavailable("Auxiliary has no overt VP complement")
            target = auxiliary_tail[0]
            position = tail.index(target)
            complement_vp = self.modal_marked_vp(head, target) if len(tail) == 1 and not negation else target
            if tag(complement_vp) != "VP":
                raise ProjectionUnavailable("Auxiliary has no overt VP complement")
            aux_tense = "-tense" if aux == "AUX" else tense(head, mode)
            lexical_passive = passive
            if aux == "PASS":
                if passive is not None or subject is None:
                    raise ProjectionUnavailable("Passive has no unambiguous promoted subject")
                lexical_passive = self.link_subject(subject)
                lexical_passive.kind = "object"
            lower = kids(complement_vp)
            high_adjunct = None
            if mode == "finite" and not (negation or fronted or incoming or tail[position + 1:]):
                lower, high_adjunct = self.peel_finite_vp_adjunct(lower)
            complement = self.vp(lower, "untensed", subject, incoming, lexical_passive)
            before_aux = [
                branch("AP", NOUN, branch("QA", NOUN, word_node(n)))
                if (leaf(n) and tag(n) == "DT" and word(n) in {"all", "both", "each"})
                else self.adjunct(n)
                for n in tail[:position]
            ]
            for pre_node in reversed(before_aux):
                complement = branch("VP", ADVERBIAL, pre_node, complement)
            complement = self.attach(complement, "VP", (), tail[position + 1:])
            predicate = branch("VP", AUXILIARY, branch(aux, AUXILIARY, *head_words,
                               features=(aux_tense,) if aux_tense else ()), complement)
            # B–R Chapter 8 p. 186 places the clause beside the tensed VP.
            return self.attach(predicate, "VP", trailing=[high_adjunct]) if high_adjunct else predicate

        base = lemma(head)
        feature = tense(head, mode)
        features = (feature,) if feature else ()
        if negation and base != "be" and not (base == "have" and mode == "finite"):
            raise ProjectionUnavailable("Negation attached directly to a non-auxiliary lexical verb")
        if passive and not incoming and base == "make" and tag(head) == "VBN":
            lower = self.bare_causative_complement(tail)
            if lower is not None:
                # Preserve the actual bare form. This is structural evidence for
                # the candidate, and carries no Cambridge verdict or repair.
                refs = ("Ch6 pp. 125–127", "Ch10 pp. 226, 238–240")
                complement = self.nonfinite(lower, subject)
                predicate = branch("VP", refs, branch("V", refs, *head_words),
                                   branch("NP", refs, passive.take()), complement)
                return self.attach(predicate, "VP", trailing=tail[1:])
        if passive and not incoming and base in PASSIVE_TYPE_I and tail and tag(tail[0]) == "S":
            lower = kids(tail[0])
            if len(lower) == 1 and tag(lower[0]) == "VP" and kids(lower[0]) and tag(kids(lower[0])[0]) == "TO":
                refs = ("Ch10 p. 226 [8], pp. 239–242",)
                clause = self.nonfinite(tail[0], subject)
                return self.attach(branch("VP", refs, branch("V(I)", refs, *head_words), clause),
                                   "VP", trailing=tail[1:])
        if passive is not None:
            if incoming is not None and incoming.kind in {"adverbial", "pp"}:
                vp = self.vp(nodes, mode, subject, passive=passive)
                return branch("VP", ADVERBIAL, vp, branch("PP" if incoming.kind == "pp" else "AdvP", WH, incoming.take()))
            if incoming is not None and incoming is not passive:
                raise ProjectionUnavailable("Overlapping dependencies inside passive VP")
            incoming = passive

        if tail and tag(tail[0]) == "S" and not self.is_nonfinite(tail[0]):
            small = kids(tail[0])
            if len(small) == 1 and tag(small[0]) in {"ADJP", "NP", "PP"} and (base in INTENSIVE or base in COMPLEX or passive is not None):
                tail[:1] = small
            elif len(small) == 2 and tag(small[0]) == "NP" and tag(small[1]) in {"ADJP", "NP", "PP"} and base in COMPLEX:
                tail[:1] = small

        if tail and tag(tail[0]) == "S" and self.is_nonfinite(tail[0]) and base in SUBJECT_CONTROL | TYPE_I:
            lower = tail.pop(0)
            overt = len(kids(lower)) == 2
            if overt and base not in TYPE_I or not overt and base not in SUBJECT_CONTROL:
                raise ProjectionUnavailable("Non-finite complement has no supported control analysis")
            clause = self.nonfinite(lower, None if overt else subject, incoming=incoming)
            v = branch("V(I)" if overt else "V", NONFINITE, *head_words, features=features)
            return self.attach(branch("VP", NONFINITE, v, clause), "VP", trailing=tail)
        if len(tail) >= 2 and tag(tail[0]) == "NP" and tag(tail[1]) == "S" and self.is_nonfinite(tail[1]) and base in TYPE_II:
            obj = self.phrase(tail[0])
            lower = self.nonfinite(tail[1], subject if base == "promise" else obj)
            v = branch("V(II)", NONFINITE, *head_words, features=features)
            return self.attach(branch("VP", NONFINITE, v, obj, lower), "VP", trailing=tail[2:])

        # Benepar occasionally parses an echo wh-in-situ object + PP
        # ('taking (SBAR (WHNP what) (PP to Athens))', B-R Ch9 [11a]) as an SBAR.
        # Unpack it into the in-situ wh-NP object plus its following PP.
        if (len(tail) >= 1 and tag(tail[0]) == "SBAR" and not self.is_adverbial(tail[0])
                and len(kids(tail[0])) == 2 and tag(kids(tail[0])[0]) == "WHNP"
                and tag(kids(tail[0])[1]) in {"PP", "ADVP"}):
            sb_wh, sb_pp = kids(tail[0])
            tail[:1] = [raw("NP", kids(sb_wh)), sb_pp]

        complement = []
        particle = None
        if tail and tag(tail[0]) == "PRT":
            particle = tail.pop(0)
        # Preserve intervening medial ADVP between lexical verb and its complement
        # ("notes merely that...", "prefers strongly to...", "believes firmly that...").
        medial_advps = []
        while (len(tail) >= 2 and tag(tail[0]) == "ADVP"
               and not (base in INTENSIVE and self.is_predicative(base, tail[0]))
               and tag(tail[1]) in {"SBAR", "NP", "PP", "S", "ADJP"}):
            medial_advps.append(tail.pop(0))
        if incoming and not passive and tail and tag(tail[0]) == "SBAR" and not self.is_adverbial(tail[0]):
            parts = kids(tail[0])
            first_leaves = leaves(parts[0]) if parts else []
            complementizer_like = bool(parts) and (
                not tag(parts[0]).startswith("WH")
                or (tag(parts[0]) in {"WHNP", "WHADVP"} and first_leaves
                    and word(first_leaves[0]) == "that"))
            if complementizer_like:
                clause = self.clause(tail.pop(0), incoming)
                v = branch("V", FRAME_REFS["trans"], *head_words, features=("trans", *features))
                return self.attach(branch("VP", FRAME_REFS["trans"], v, branch("NP", SUBORDINATE, clause)),
                                   "VP", trailing=tail)
        if incoming is not None and incoming.kind in {"object", "predicative", "adverbial", "preposition", "pp"}:
            if incoming.kind == "pp" and base == "put" and tail and tag(tail[0]) == "NP":
                frame = "complex"
                complement.extend([self.phrase(tail.pop(0)), branch("PP", WH, incoming.take())])
            elif incoming.kind == "predicative" or (base in INTENSIVE and incoming.kind == "object" and passive is None):
                if tail and tag(tail[0]) in {"NP", "ADJP"}:
                    raise ProjectionUnavailable("Predicative gap conflicts with an overt complement")
                frame = "intens"
                complement.append(branch("AP" if incoming.kind == "predicative" else "NP", WH, incoming.take()))
            elif incoming.kind == "preposition":
                # Predicative AP with stranded preposition ('subjects they are
                # interested in', 'things we are proud of', 'people she is fond of').
                if (base in INTENSIVE and tail and tag(tail[0]) == "ADJP"
                        and any(tag(c) == "PP" and len(kids(c)) == 1 for c in kids(tail[0]))):
                    adjp_parts = kids(tail.pop(0))
                    pp_idx = next(i for i, c in enumerate(adjp_parts) if tag(c) == "PP" and len(kids(c)) == 1)
                    ap_prefix = [
                        branch("DEG", ("Ch3 pp. 55–56",), word_node(c))
                        if leaf(c) and word(c) in DEGREE
                        else (branch("A", ("Ch3 p. 55",), word_node(c))
                              if leaf(c) and tag(c) in ADJ_TAGS
                              else (branch("PartP", ("Ch7 pp. 147–148, 158",),
                                           branch("V-part", ("Ch7 p. 158",), word_node(c)))
                                    if leaf(c) and tag(c) in {"VBN", "VBG"}
                                    else self.phrase(c)))
                        for c in adjp_parts[:pp_idx]
                    ]
                    stranded_pp = self.pp(kids(adjp_parts[pp_idx]), incoming)
                    ap_suffix = [self.phrase(c) for c in adjp_parts[pp_idx + 1:]]
                    frame = "intens"
                    complement.append(branch("AP", WH, *ap_prefix, stranded_pp, *ap_suffix))
                elif (base in RECIPIENT_TO and len(tail) >= 2
                      and tag(tail[0]) == "NP" and not self.is_time_np(tail[0])
                      and tag(tail[1]) == "PP" and len(kids(tail[1])) == 1
                      and word(kids(tail[1])[0]) == "to"
                      and sum(tag(node) == "PP" and len(kids(node)) == 1 for node in tail) == 1):
                    # Ch9 [1b(ii)] strands the recipient preposition and keeps
                    # the direct object and the recipient PP in the ditransitive VP.
                    frame = "ditrans"
                    complement.append(self.phrase(tail.pop(0)))
                    complement.append(self.pp(kids(tail.pop(0)), incoming))
                elif not tail or tag(tail[0]) != "PP" or len(kids(tail[0])) != 1:
                    raise ProjectionUnavailable("Wh-phrase has no unique stranded preposition")
                else:
                    prep = tail.pop(0)
                    frame = "prep" if word(kids(prep)[0]) in SELECTED_PP.get(base, ()) else "intrans"
                    stranded = self.pp(kids(prep), incoming)
                    if frame == "prep":
                        complement.append(stranded)
                    else:
                        v = branch("V", FRAME_REFS[frame], *head_words, features=(frame, *features))
                        vp = branch("VP", ADVERBIAL, branch("VP", FRAME_REFS[frame], v), stranded)
                        return self.attach(vp, "VP", trailing=tail)
            elif incoming.kind in {"adverbial", "pp"}:
                if base in INTENSIVE and not tail:
                    frame = "intens"
                    complement.append(branch("PP", WH, incoming.take()))
                else:
                    if fronted:
                        raise ProjectionUnavailable("Unresolved adjunct with a fronted lexical verb")
                    v = self.vp(nodes, mode, subject)
                    return branch("VP", ADVERBIAL, v, branch("PP" if incoming.kind == "pp" else "AdvP", WH, incoming.take()))
            elif tail and tag(tail[0]) == "NP" and base in DITRANSITIVE:
                frame = "ditrans"
                obj = self.phrase(tail.pop(0))
                complement.extend([branch("NP", WH, incoming.take()), obj] if passive else [obj, branch("NP", WH, incoming.take())])
            elif passive is not None and base in COMPLEX and tail and tag(tail[0]) in {"ADJP", "NP", "PP"}:
                # Passive of a complex-transitive verb ('Otto was driven • mad by the noise', B-R Ch6 [81]).
                frame = "complex"
                complement.extend([branch("NP", AUXILIARY, incoming.take()), self.phrase(tail.pop(0))])
            else:
                if base in KNOWN_INTRANS or (tail and tag(tail[0]) == "NP" and not self.is_time_np(tail[0])):
                    raise ProjectionUnavailable("Object gap conflicts with the verb frame or an overt object")
                frame = "trans"
                complement.append(branch("NP", AUXILIARY if passive else WH, incoming.take()))
        elif (base in INTENSIVE and len(tail) >= 2 and tag(tail[0]) == "ADVP"
              and tag(tail[1]) == "VP" and len(kids(tail[1])) == 1
              and tag(kids(tail[1])[0]) == "JJ"):
            # Benepar may split "be + adverb + participial adjective" into
            # ADVP + VP(JJ). The B-R convention treats the adjective as the
            # predicative AP head with the adverb inside AP.
            adverb = tail.pop(0)
            adjective = kids(tail.pop(0))[0]
            ap = branch("AP", ADVERBIAL,
                        branch("AdvP", ADVERBIAL, *(word_node(n) for n in leaves(adverb))),
                        branch("A", ADVERBIAL, word_node(adjective)))
            frame = "intens"
            complement.append(ap)
        elif (base in TYPE_I and len(tail) == 1 and tag(tail[0]) == "S"):
            small = kids(tail[0])
            if (len(small) == 3 and tag(small[0]) == "NP"
                    and tag(small[1]) in {"ADJP", "NP", "PP"}
                    and tag(small[2]) == "SBAR"):
                frame = "complex"
                complement.extend([self.phrase(small[0]), self.phrase(small[1]),
                                   self.clause(small[2])])
                tail.pop(0)
            else:
                raise ProjectionUnavailable("Unsupported complex object frame")
        elif base in INTENSIVE and tail and self.is_predicative(base, tail[0]):
            frame = "intens"
            complement.append(self.predicative(tail.pop(0), subject))
        elif tail and tag(tail[0]) == "ADJP" and (
                base in INTENSIVE or base in {"do", "make", "take", "have", "give", "find"}):
            # Preserve the observed adjectival dependent ("did good") without
            # endorsing it. The adjective/adverb rule reports the error.
            frame = "intens" if base in INTENSIVE else "complex"
            complement.append(self.predicative(tail.pop(0), subject))
        elif (base in {"give", "send", "lend", "hand", "pass", "sell", "offer", "show", "write"}
              and len(tail) >= 2 and tag(tail[0]) == "PP" and kids(tail[0])
              and word(kids(tail[0])[0]) == "to" and tag(tail[1]) == "NP" and not self.is_time_np(tail[1])):
            frame = "ditrans"
            complement.extend(self.phrase(n) for n in tail[:2])
            tail = tail[2:]
        elif (tail and tag(tail[0]) == "NP" and not self.is_time_np(tail[0])
              and not self.is_temporal_coordination(tail[0])):
            if base in KNOWN_INTRANS:
                raise ProjectionUnavailable(f"{base} has an overt object without a licensed object frame")
            frame = "trans"
            complement.append(self.phrase(tail.pop(0)))
            if tail and tag(tail[0]) == "SBAR" and base in DITRANSITIVE and not self.is_adverbial(tail[0]):
                frame = "ditrans"
                complement.append(branch("NP", SUBORDINATE, self.clause(tail.pop(0))))
            if tail and frame == "trans" and tag(tail[0]) in {"NP", "ADJP", "PP"}:
                second = tail[0]
                label = tag(second)
                if base == "find" and label == "NP":
                    raise ProjectionUnavailable("Two noun phrases after find can have ditransitive or object-predicative readings")
                if label == "NP" and base in DITRANSITIVE or (label == "PP" and base in DITRANSITIVE and word(kids(second)[0]) in {"to", "for"}):
                    frame = "ditrans"
                elif base in COMPLEX and (label in {"NP", "ADJP"} or base in {"put", "place"}):
                    frame = "complex"
                if frame != "trans":
                    complement.append(self.phrase(tail.pop(0)))
            if base in {"put", "place"} and frame == "trans" and particle is None and not any(tag(node) == "PRT" for node in tail):
                raise ProjectionUnavailable(f"{base} has no overt or licensed covert object-predicative")
        elif tail and tag(tail[0]) == "PP" and self.selected_pp(base, tail[0]):
            frame = "prep"
            complement.append(self.phrase(tail.pop(0)))
        elif tail and tag(tail[0]) == "SBAR" and not self.is_adverbial(tail[0]):
            frame = "intens" if base == "be" else "trans"
            clause = self.clause(tail.pop(0))
            complement.append(clause if frame == "intens" else branch("NP", SUBORDINATE, clause))
        else:
            if base == "be" and particle is None:
                frame = "intens"
                complement.append(branch("AP", ("Ch8 p. 189",),
                                         branch("A", ("Ch8 p. 189",),
                                                {"elided": True, "symbol": "E"})))
            elif base in REQUIRES_COMPLEMENT and particle is None and self.allow_object_gap:
                frame = "trans"
                complement.append(branch("NP", WH, self.gap("object").take()))
            elif base in REQUIRES_COMPLEMENT and particle is None:
                raise ProjectionUnavailable(f"{base} has no overt or licensed covert complement")
            else:
                frame = "intrans"
        refs = FRAME_REFS[frame]
        if base == "sleep":
            refs += ("Ch5 p. 104 [1e]",)
        v_refs = (*refs, *(("Ch4 p. 85 ex. 1(14)",) if base == "place" and frame == "complex" else ()),
                  *(("Ch6 p. 113 [8]–[9]",) if feature else ()))
        suffix = ("phrasal",) if particle is not None or tail and tag(tail[0]) == "PRT" else ()
        if particle is not None:
            head_words.extend(word_node(n) for n in leaves(particle))
        elif tail and tag(tail[0]) == "PRT":
            complement.append(branch("Prt", ("Ch5 pp. 93–95",), *(word_node(n) for n in leaves(tail.pop(0)))))
        v = branch("V", v_refs, *head_words, features=(frame, *suffix, *features))
        participial = {}
        for extra in tail:
            label = tag(extra)
            parts = passive_adjunct_parts(extra, head) if subject is not None else None
            if parts:
                participial[id(extra)] = parts
                continue
            if (label == "SBAR" and not self.is_adverbial(extra)
                    and passive is not None and base in PASSIVE_TYPE_I):
                continue
            if (label == "VP" and kids(extra) and tag(kids(extra)[0]) in {"VBG", "VBN"}
                    and base == "be"):
                continue
            if (label == "S" and not self.is_nonfinite(extra)
                    and len(kids(extra)) == 1 and tag(kids(extra)[0]) == "ADJP"):
                continue
            if label not in {"ADVP", "PP", "SBAR", "NP", "S"} or (label == "NP" and not self.is_time_np(extra)
                and not self.is_temporal_coordination(extra)) or (label == "SBAR" and not self.is_adverbial(extra)) or (label == "S" and not self.is_nonfinite(extra)):
                raise ProjectionUnavailable(f"Unclassified VP dependent {label}")
        # Project trailing participial VP, small-clause S(ADJP), or stacked
        # adverbial SBAR(PP/SBAR + SBAR) cleanly as sequential VP adjuncts.
        normalized_tail = []
        for extra in tail:
            if id(extra) in participial:
                normalized_tail.append(extra)
            elif tag(extra) == "S" and not self.is_nonfinite(extra) and len(kids(extra)) == 1 and tag(kids(extra)[0]) == "ADJP":
                normalized_tail.append(kids(extra)[0])
            elif tag(extra) == "VP" and kids(extra) and tag(kids(extra)[0]) in {"VBG", "VBN"} and base == "be":
                normalized_tail.append(raw("S", [extra]))
            elif (tag(extra) == "SBAR" and len(kids(extra)) >= 2
                  and all(tag(p) in {"PP", "SBAR"} for p in kids(extra))):
                normalized_tail.extend(kids(extra))
            else:
                normalized_tail.append(extra)
        predicate = branch('VP', refs, v, *(self.adjunct(a) for a in medial_advps), *complement)
        for extra in normalized_tail:
            dependent = (self.passive_adjunct(participial[id(extra)], subject)
                         if id(extra) in participial else self.adjunct(extra))
            predicate = branch('VP', ADVERBIAL, predicate, dependent)
        return predicate

    def temporal_pp(self, node):
        if tag(node) == "PP":
            return self.phrase(node)
        if tag(node) == "NP" and self.is_time_np(node):
            refs = ("Ch5 pp. 100–102",)
            return branch("PP", refs,
                          branch("P", refs, {"elided": True, "symbol": "E"}),
                          self.phrase(node))
        return None

    def is_temporal_coordination(self, node):
        if tag(node) != "NP":
            return False
        parts = kids(node)
        return (len(parts) == 3 and tag(parts[1]) == "CC"
                and any(tag(p) == "PP" for p in (parts[0], parts[2]))
                and self.temporal_pp(parts[0]) is not None
                and self.temporal_pp(parts[2]) is not None)

    def is_time_np(self, node):
        words = leaves(node)
        if not words:
            return False
        if self.dependency(node) == "npadvmod":
            return True
        last_w = word(words[-1]).rstrip("s")
        if last_w in TIME_NOUNS:
            if len(words) == 1:
                return True
            if word(words[0]) in {"all", "every", "last", "next", "this", "that", "even", "most", "some", "each", "one"}:
                return True
        return False

    def is_predicative(self, base, node):
        label = tag(node)
        if label == "NP":
            # Get a book has an object, unlike the adjective in get angry.
            return base != "get"
        if label == "ADVP":
            words = leaves(node)
            if len(words) == 1 and word(words[0]) == "so":
                return base in {"be", "remain", "seem", "appear"}
            return bool(words and word(words[-1]) in LOCATIVE_WORDS | {"in", "out", "up", "down", "away", "home"})
        return label in {"ADJP", "PP"}

    def selected_pp(self, base, node):
        parts = kids(node)
        if not parts:
            return False
        head = word(parts[0])
        if head == "for" and len(parts) > 1:
            complement = leaves(parts[1])
            if complement and word(complement[-1]).rstrip("s") in TIME_UNITS:
                return False
        return head in SELECTED_PP.get(base, ())

    def is_adverbial(self, node):
        parts = kids(node)
        if len(parts) < 2:
            return False
        # Coordinated adverbial SBARs ('after ..., but before ...')
        if (len(parts) >= 3 and tag(parts[0]) == "SBAR"
                and any(leaf(p) and tag(p) == "CC" for p in parts)
                and all(tag(p) == "SBAR" or (leaf(p) and tag(p) == "CC") for p in parts)
                and all(self.is_adverbial(p) for p in parts if tag(p) == "SBAR")):
            return True
        # Stacked consecutive adverbial clauses wrapped under one SBAR
        # ('after the facts were on the table before they could ...')
        if (len(parts) >= 2 and all(tag(p) in {"PP", "SBAR"} for p in parts)
                and all(self.is_adverbial(p) for p in parts if tag(p) == "SBAR")):
            return True
        if len(parts) == 2 and leaf(parts[0]) and word(parts[0]) in SUBORDINATORS:
            return True
        # Multi-word subordinators: "so that", "in order that", "even though",
        # "even if", "now that", "except that", "as if", "as though", etc.
        if len(parts) >= 3 and tag(parts[-1]) == "S":
            lead_words = tuple(word(lf) for p in parts[:-1] for lf in leaves(p))
            if lead_words in MULTIWORD_SUBORDINATORS:
                return True
        # Benepar wraps a subordinating wh-word as WHNP/WHADVP. "when",
        # "where", "while", "because" and similar clauses are adjuncts, not
        # complement clauses, even though the wh-phrase is not a bare leaf.
        if len(parts) == 2 and tag(parts[0]) in {"WHNP", "WHADVP", "WHPP"}:
            heads = leaves(parts[0])
            if heads and word(heads[0]) in SUBORDINATORS:
                return True
            if heads and word(heads[0]) in {"whatever", "whoever", "whenever",
                                             "wherever", "however", "where"}:
                return True
        return False

    def extract_delayed_sbar(self, node):
        """Find a trailing non-adverbial SBAR inside a nested VP without mutating input."""
        children = list(node.get("children", []))
        if children and tag(children[-1]) == "SBAR" and not self.is_adverbial(children[-1]):
            found = children.pop()
            return {**node, "children": children}, found
        for idx in range(len(children) - 1, -1, -1):
            if tag(children[idx]) == "VP":
                updated_child, found = self.extract_delayed_sbar(children[idx])
                if found is not None:
                    children[idx] = updated_child
                    return {**node, "children": children}, found
        return node, None

    def clause(self, node, incoming=None):
        label, parts = tag(node), kids(node)
        if label in {"ROOT", "TOP"} and len(parts) == 1:
            return self.clause(parts[0], incoming)
        if label in {"S", "SQ"} and incoming is None and self.is_question_tag(node):
            return self.tag_question(parts)
        if label == "SQ":
            return self.question(parts, incoming)
        if label == "SINV" and incoming is None:
            return self.locative_inversion(parts)
        if label in {"SBAR", "SBARQ"}:
            # Leading adverbial before SBARQ ('Once you get success why would you...')
            if (label == "SBARQ" and len(parts) >= 3
                    and tag(parts[0]) in {"SBAR", "PP", "ADVP"}
                    and not (tag(parts[0]) == "SBAR" and not self.is_adverbial(parts[0]))
                    and tag(parts[1]).startswith("WH")):
                lead_adv = parts[0]
                return self.attach(self.clause(raw("SBARQ", parts[1:]), incoming), "S", [lead_adv])
            # Coordinated subordinate clauses ('after ..., but before ...')
            if (label == "SBAR" and len(parts) >= 3
                    and any(leaf(p) and tag(p) == "CC" for p in parts)
                    and all(tag(p) == "SBAR" or (leaf(p) and tag(p) == "CC") for p in parts)):
                coord_sbar = self.coordinate(parts, lambda sub: self.clause(sub[0] if len(sub) == 1 else raw("SBAR", sub), incoming))
                if coord_sbar:
                    return branch("S′", COORD, *coord_sbar)
            if parts and tag(parts[0]).startswith("WH"):
                heads = leaves(parts[0])
                # Benepar wraps the complementiser "that" as WHNP(WDT that).
                # It is a C1 marker, not a relative wh-phrase.
                if (len(parts) == 2 and heads and word(heads[0]) == "that"
                        and tag(parts[1]) == "S"):
                    carrier = branch("C1", SUBORDINATE, word_node(heads[0]))
                    body_node = parts[1]
                    if (incoming is None and kids(body_node)
                            and all(tag(part) == "VP" for part in kids(body_node))):
                        body = self.clause(body_node, self.gap("subject"))
                    else:
                        body = self.clause(body_node, incoming)
                    return branch("S′", SUBORDINATE, carrier, body)
                return self.wh_clause(parts)
            if not parts or tag(parts[-1]) != "S":
                raise ProjectionUnavailable("Unsupported subordinate clause wrapper")
            # Multi-word subordinators ("so that", "even though", "in order that", ...)
            if len(parts) > 2:
                lead_leaves = [lf for p in parts[:-1] for lf in leaves(p)]
                lead_words = tuple(word(lf) for lf in lead_leaves)
                if lead_words not in MULTIWORD_SUBORDINATORS:
                    raise ProjectionUnavailable("Unsupported subordinate clause wrapper")
                carrier = branch("C1", SUBORDINATE, *(word_node(lf) for lf in lead_leaves))
                body_node = parts[-1]
                body = (self.nonfinite(body_node, wrap=False)
                        if self.is_nonfinite(body_node)
                        else self.clause(body_node, incoming))
                return branch("S′", SUBORDINATE, carrier, body)
            if len(parts) == 2 and (not leaf(parts[0]) or word(parts[0]) not in SUBORDINATORS | {"that", "whether", "for"}):
                raise ProjectionUnavailable("Unrecognized complementiser")
            if len(parts) == 2 and word(parts[0]) == "since":
                # Ch8 pp.185-186 and the 3rd-edition preface distinguish
                # temporal preposition 'since' from causal complementiser
                # 'since'. Benepar's SBAR alone cannot decide which.
                raise ProjectionUnavailable("Since requires temporal-P versus causal-C disambiguation under the B-R third edition")
            if len(parts) == 2 and word(parts[0]) in TEMPORAL_P:
                return branch("PP", SUBORDINATE, branch("P", SUBORDINATE, word_node(parts[0])), self.clause(parts[-1], incoming))
            carrier = branch("C1", SUBORDINATE, *(word_node(n) for n in parts[:-1]))
            if len(parts) == 2 and word(parts[0]) in {"as", "than"}:
                self.allow_object_gap += 1
                try:
                    body = self.clause(parts[-1], incoming)
                finally:
                    self.allow_object_gap -= 1
            else:
                body_node = parts[-1]
                if (incoming is None and tag(body_node) == "S" and kids(body_node)
                        and all(tag(part) == "VP" for part in kids(body_node))):
                    # A subordinate clause whose subject is a relative/ECM gap
                    # still has a structural subject position. Keep the gap
                    # explicit rather than refusing the whole sentence.
                    body = self.clause(body_node, self.gap("subject"))
                else:
                    body = (self.nonfinite(body_node, wrap=False)
                            if len(parts) == 2 and word(parts[0]) == "for"
                            and self.is_nonfinite(body_node)
                            else self.clause(body_node, incoming))
            return branch("S′", SUBORDINATE, carrier, body)
        if label == "WHADVP" and len(parts) == 2 and tag(parts[0]) == "WHADVP" and tag(parts[1]) == "SQ":
            # Benepar occasionally labels a short root SBARQ ('How are you') as WHADVP(WHADVP, SQ).
            return self.wh_clause(parts)
        if label != "S":
            raise ProjectionUnavailable(f"Unsupported clause structure {label}")
        raw_children = node.get("children", [])
        if (len(parts) == 2 and all(tag(n) in {"S", "SQ", "SBARQ", "SINV"} for n in parts)
                and len(raw_children) >= 3 and raw_children[1].get("surface") in {":", ";"}
                and incoming is None):
            result = branch("S", COORD, *(self.clause(n) for n in parts))
            result["notes"] = ["The punctuation joins two independently projected clauses and remains in the submitted text."]
            return result
        # Discourse-initial coordinator ("And young people...", "But in another way...",
        # or Benepar-tagged "(IN So) (NP ...) (VP ...)")
        if (len(parts) >= 2 and leaf(parts[0])
                and (tag(parts[0]) == "CC"
                     or (tag(parts[0]) == "IN" and word(parts[0]) in {"so", "yet", "nor", "for"}))):
            return branch("S", COORD, word_node(parts[0]), self.clause(raw("S", parts[1:]), incoming))
        if incoming is None:
            elliptical = self.coordinated_ellipsis(parts)
            if elliptical:
                return elliptical
        coordination = self.coordinate(parts, lambda nodes: self.clause(nodes[0] if len(nodes) == 1 else raw("S", nodes)))
        if coordination is None and incoming is None:
            # Benepar often tags clausal coordinator 'so' as IN between two S
            # clauses ('If ..., the doctor has done ..., so he is talented').
            so_links = [
                i for i, n in enumerate(parts)
                if 0 < i < len(parts) - 1 and leaf(n) and tag(n) == "IN"
                and word(n) == "so" and tag(parts[i + 1]) in {"S", "SQ", "SBARQ", "SINV"}
                and any(tag(p) in {"S", "SQ", "SBARQ", "SINV"} for p in parts[:i])
            ]
            if len(so_links) == 1:
                si = so_links[0]
                left_nodes = parts[:si]
                right_nodes = parts[si + 1:]
                left_c = self.clause(left_nodes[0] if len(left_nodes) == 1 else raw("S", left_nodes))
                right_c = self.clause(right_nodes[0] if len(right_nodes) == 1 else raw("S", right_nodes))
                return branch("S", COORD, left_c, word_node(parts[si]), right_c)
        if coordination:
            if incoming:
                raise ProjectionUnavailable("Unresolved movement across coordinated clauses")
            return branch("S", COORD, *coordination)
        if len(parts) == 1 and tag(parts[0]) == "S":
            return self.clause(parts[0], incoming)
        # Benepar wraps a zero-that embedded clause + trailing adverbial SBAR under S:
        # (S (SBAR (S ...)) (SBAR (IN because) (S ...))) (e.g. B-R Ch8 ex. 2b).
        if (len(parts) >= 2 and tag(parts[0]) == "SBAR" and not self.is_adverbial(parts[0])
                and len(kids(parts[0])) == 1 and tag(kids(parts[0])[0]) == "S"
                and all(tag(p) == "SBAR" and self.is_adverbial(p) for p in parts[1:])):
            return self.attach(self.clause(kids(parts[0])[0], incoming), "S", trailing=parts[1:])
        if (incoming is None and len(parts) == 2 and tag(parts[0]) == "NP"
                and tag(parts[1]) == "SBAR"):
            return branch("S", TOPIC, self.phrase(parts[0]), self.clause(parts[1]))
        if len(parts) == 1 and tag(parts[0]) == "VP" and incoming is None:
            vp_parts = kids(parts[0])
            if vp_parts and leaf(vp_parts[0]) and tag(vp_parts[0]) == "VB" and lemma(vp_parts[0]) == word(vp_parts[0]):
                imperative = ("Ch3 p. 66; Ch10 pp. 224–225",)
                subject = branch("NP", imperative, {"gap": True})
                return branch("S", imperative, subject, self.vp(vp_parts, "untensed", subject))
            if self.is_nonfinite(node):
                return self.nonfinite(node)
        before = []
        while len(parts) > 1 and (
                (tag(parts[0]) in {"PP", "ADVP", "SBAR"} and not (
                    tag(parts[0]) == "SBAR" and not self.is_adverbial(parts[0])))
                or (len(parts) >= 3 and tag(parts[0]) == "NP" and self.is_time_np(parts[0])
                    and tag(parts[1]) in {"NP", "S", "SBAR", "PP", "ADVP"})):
            before.append(parts.pop(0))
        # Leading adverbials before a wrapped inner clause ("Then when we went...,
        # (S she could...)" or "However, (S ... and ...)").
        if len(parts) == 1 and tag(parts[0]) in {"S", "SQ", "SBARQ", "SINV"}:
            return self.attach(self.clause(parts[0], incoming), "S", before)
        # Locative/existential inversion parsed as S -> ADVP(Here/There) VP(be) NP
        if (len(parts) == 2 and before and tag(parts[0]) == "VP" and tag(parts[1]) == "NP"
                and len(kids(parts[0])) == 1 and leaf(kids(parts[0])[0])
                and lemma(kids(parts[0])[0]) == "be" and tag(before[-1]) in {"ADVP", "PP"}):
            loc = before.pop()
            inv = self.locative_inversion([loc, kids(parts[0])[0], parts[1]])
            return self.attach(inv, "S", before)
        if len(parts) == 1 and tag(parts[0]) == "VP" and incoming and incoming.kind == "subject":
            subject = branch("NP", WH, incoming.take())
        elif len(parts) >= 2 and tag(parts[0]) in {"NP", "SBAR", "S"}:
            first = parts.pop(0)
            if tag(first) == "S" and self.is_nonfinite(first):
                subject = branch("NP", NONFINITE, self.nonfinite(first))
            elif tag(first) == "SBAR":
                subject = branch("NP", SUBORDINATE, self.clause(first))
            else:
                subject = self.phrase(first)
        else:
            raise ProjectionUnavailable("Clause has no overt or licensed covert subject")
        early = []
        while len(parts) > 1 and tag(parts[0]) == "ADVP":
            early.append(parts.pop(0))
        outer_delayed = None
        if (len(parts) == 2 and tag(parts[0]) == "VP" and tag(parts[1]) == "SBAR"
                and not self.is_adverbial(parts[1])
                and subject.get("children", [{}])[0].get("label") == "pronoun"
                and subject["children"][0]["children"][0]["word"].lower() == "it"):
            outer_delayed = self.clause(parts.pop())
        if len(parts) != 1 or tag(parts[0]) != "VP":
            if (len(parts) == 1 and leaf(parts[0])
                    and tag(parts[0]) in VERB_TAGS):
                # Benepar can place a finite verb directly under S when the
                # verb has no dependents. Restore the VP projection layer.
                parts[0] = raw("VP", [parts[0]])
            else:
                raise ProjectionUnavailable("Clause has no single identifiable predicate")
        predicate_parts = kids(parts[0])
        # Expletive 'it' + Benepar flat extraposition without overt 'that':
        # (VP (VP is n't my fault) (NP Max) (VP crushed your monocle)) (B-R Ch8 Disc. 2).
        if (outer_delayed is None
                and len(predicate_parts) == 3
                and tag(predicate_parts[0]) == "VP"
                and tag(predicate_parts[1]) == "NP"
                and tag(predicate_parts[2]) == "VP"
                and subject.get("children", [{}])[0].get("label") == "pronoun"
                and subject["children"][0]["children"][0]["word"].lower() == "it"):
            outer_delayed = branch("S′", SUBORDINATE, branch("C1", SUBORDINATE),
                                   self.clause(raw("S", predicate_parts[1:])))
            predicate_parts = kids(predicate_parts[0])
        if (outer_delayed is None
                and subject.get("children", [{}])[0].get("label") == "pronoun"
                and subject["children"][0]["children"][0]["word"].lower() == "it"):
            cleaned_vp, found = self.extract_delayed_sbar(parts[0])
            if found is not None:
                parts[0] = cleaned_vp
                predicate_parts = kids(parts[0])
                outer_delayed = self.clause(found)
        # Expletive subject and a delayed that-clause in the documented extraposition frame.
        delayed = None
        if (len(predicate_parts) >= 2 and leaf(predicate_parts[0]) and lemma(predicate_parts[0]) in {"be", "seem", "appear", "happen"}
                and tag(predicate_parts[-1]) == "SBAR" and not self.is_adverbial(predicate_parts[-1])
                and subject.get("children", [{}])[0].get("label") == "pronoun"
                and subject["children"][0]["children"][0]["word"].lower() == "it"
                and (lemma(predicate_parts[0]) != "be" or len(predicate_parts) >= 3)):
            delayed = self.clause(predicate_parts.pop())
        predicate_head = next((leaf for leaf in leaves(predicate_parts[0])
                               if tag(leaf) in VERB_TAGS), None)
        if predicate_head is not None and tag(predicate_head) in {"VBG", "VBN", "TO"}:
            mode = "nonfinite"
        elif predicate_head is not None and tag(predicate_head) == "VB" and lemma(predicate_head) == word(predicate_head):
            mode = "untensed"
        else:
            mode = "finite"
        vp = self.vp(predicate_parts, mode, subject, incoming if incoming and not incoming.used else None)
        vp = self.attach(vp, "VP", early)
        delayed = delayed or outer_delayed
        core = branch("S", SUBORDINATE if delayed else CLAUSE, subject, vp, *([delayed] if delayed else []))
        return self.attach(core, "S", before)

    def locative_inversion(self, parts):
        if len(parts) == 3 and tag(parts[1]) == "VP" and len(kids(parts[1])) == 1:
            parts = [parts[0], kids(parts[1])[0], parts[2]]
        if len(parts) == 3:
            location, verb, raw_subject = parts
            loc_words = leaves(location)
            is_locative = bool(loc_words) and (
                (tag(location) == "PP" and word(loc_words[0]) in LOCATIVE_PREPOSITIONS)
                or (tag(location) == "ADVP" and len(loc_words) == 1 and word(loc_words[0]) in LOCATIVE_WORDS))
            if (is_locative and leaf(verb) and lemma(verb) == "be" and tag(verb) in {"VBD", "VBP", "VBZ"}
                    and tag(raw_subject) == "NP" and self.dependency(loc_words[0]) != "expl"):
                subject = self.phrase(raw_subject)
                fronted = self.phrase(location)
                link = self.gap("pp")
                fronted["index"] = link.index
                predicate = self.vp([verb], "finite", subject, link)
                # An application of the PP predicative frame to surface inversion.
                # The subject remains a daughter of S and the lexical be remains in VP.
                result = branch("S", LOCATIVE, fronted, branch("S", CLAUSE, predicate, subject))
                result["notes"] = ["SynTutor applies the locative predicative frame to declarative inversion."]
                return result
        raise ProjectionUnavailable("Unsupported declarative inversion")

    def is_question_tag(self, node):
        parts = node.get("children", [])
        return (len(parts) in {5, 6} and tag(parts[0]) == "S"
                and parts[1].get("surface") == "," and parts[-1].get("surface") == "?"
                and tag(parts[-2]) == "NP" and len(kids(parts[-2])) == 1
                and tag(kids(parts[-2])[0]) in {"PRP", "EX"}
                and (len(parts) == 5 or parts[3].get("surface") in {"n't", "not"}))

    def finite_predicate_head(self, node):
        for child in node.get("children", ()):
            if set(child.get("features", ())) & {"pres", "past"}:
                return child, node
            if child.get("label") in {"S", "VP"}:
                result = self.finite_predicate_head(child)
                if result:
                    return result
        return None

    def tag_question(self, parts):
        main = self.clause(parts[0])
        head, *negative, raw_subject = parts[1:]
        tag_clause = self.inverted_ellipsis(main, head, negative, raw_subject)
        result = branch("S", (*AUXILIARY, *ELLIPSIS), main, tag_clause)
        result["notes"] = ["SynTutor applies the auxiliary-fronting and ellipsis conventions to the question tag."]
        return result

    def coordinated_ellipsis(self, parts):
        if len(parts) < 3 or tag(parts[-1]) != "SINV":
            return None
        inversion = kids(parts[-1])
        coordinator_at = len(parts) - 2
        if leaf(parts[coordinator_at]) and word(parts[coordinator_at]) == "nor":
            marker = parts[coordinator_at]
            coordinator_at -= 1
        elif (len(inversion) == 3 and tag(inversion[0]) == "ADVP"
              and len(kids(inversion[0])) == 1 and word(kids(inversion[0])[0]) in {"so", "nor", "neither"}):
            marker = kids(inversion.pop(0))[0]
        else:
            return None
        coordinator = parts[coordinator_at]
        if (coordinator_at < 1 or not leaf(coordinator) or tag(coordinator) != "CC"
                or word(coordinator) not in {"and", "but"} or len(inversion) != 2
                or tag(inversion[0]) != "VP" or len(kids(inversion[0])) != 1 or tag(inversion[1]) != "NP"):
            return None
        left = self.clause(raw("S", parts[:coordinator_at]))
        right = self.inverted_ellipsis(left, kids(inversion[0])[0], (), inversion[1])
        adv = branch("AdvP", ADVERBIAL, branch("Adv", ADVERBIAL, word_node(marker)))
        result = branch("S", COORD, left, word_node(coordinator), branch("S", ADVERBIAL, adv, right))
        result["notes"] = ["SynTutor applies the auxiliary-fronting and ellipsis conventions to the coordinated clause."]
        return result

    def inverted_ellipsis(self, main, head, negative, raw_subject):
        finite = self.finite_predicate_head(main)
        if not finite or not leaf(head) or tag(head) not in {"MD", "VBD", "VBP", "VBZ"}:
            raise ProjectionUnavailable("Inverted ellipsis has no identifiable finite carrier")
        antecedent, antecedent_vp = finite
        base = lemma(head)
        label = antecedent["label"]
        features = (tense(head, "finite"),)
        omitted = {"elided": True, "symbol": "E"}
        complement = branch("VP", ELLIPSIS, omitted)
        if tag(head) == "MD":
            label = "MOD"
        elif base == "do" and label in {"V", "TENSE"}:
            label = "TENSE"
        elif base == "be" and label == "V" and ("intens" in antecedent["features"]
              and lemma({"surface": antecedent["children"][0].get("word", "")}) == "be"):
            features = ("intens", *features)
            complement = branch(antecedent_vp["children"][1]["label"], ELLIPSIS, omitted)
        elif (base, label) not in {("have", "PERF"), ("be", "PROG"), ("be", "PASS")}:
            raise ProjectionUnavailable("Inverted ellipsis has no licensed antecedent predicate")
        link = self.gap("fronted verb")
        carrier = branch("C1", AUXILIARY, word_node(head), *(word_node(n) for n in negative))
        carrier["index"] = link.index
        vp = branch("VP", (*AUXILIARY, *ELLIPSIS), branch(label, AUXILIARY, link.take(), features=features), complement)
        return branch("S′", AUXILIARY, carrier, branch("S", CLAUSE, self.phrase(raw_subject), vp))

    def question(self, parts, incoming=None):
        before = []
        while len(parts) > 2 and tag(parts[0]) in {"ADVP", "PP", "SBAR"} and not (
                tag(parts[0]) == "SBAR" and not self.is_adverbial(parts[0])):
            before.append(parts[0])
            parts = parts[1:]
        if len(parts) == 1 and tag(parts[0]) == "VP" and self.is_aux_inversion(kids(parts[0])):
            parts = kids(parts[0])
        if len(parts) < 2 or not leaf(parts[0]):
            raise ProjectionUnavailable("Unsupported inversion or question tag")
        head, *tail = parts
        negative = tail.pop(0) if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"} else None
        if not tail or tag(tail[0]) != "NP":
            raise ProjectionUnavailable("Inversion has no identifiable subject NP")
        raw_subject = tail.pop(0)
        # Benepar occasionally wraps a trailing participial VP inside the subject
        # NP of an inverted question: (SQ (VBP are) (NP (NP Rose and a picture)
        # (VP (VBG scaring)))). Detach the trailing VP back into tail when tail
        # has no VP of its own.
        if (not tail and len(kids(raw_subject)) == 2
                and tag(kids(raw_subject)[0]) == "NP"
                and tag(kids(raw_subject)[1]) == "VP"):
            subj_parts = kids(raw_subject)
            raw_subject = subj_parts[0]
            tail = [subj_parts[1]]
        if tag(head) not in {"MD", "VBZ", "VBP", "VBD"} or (
                self.auxiliary(head, [node for node in tail if tag(node) != "ADVP"]) is None
                and lemma(head) not in {"be", "have"}):
            raise ProjectionUnavailable("No licensed auxiliary or auxiliary-behaving verb in C1")
        subject = self.phrase(raw_subject)
        delayed = None
        if tail and tag(tail[-1]) == "SBAR" and not self.is_adverbial(tail[-1]):
            delayed = self.clause(tail.pop())
        link = self.gap("fronted verb")
        carrier = branch("C1", AUXILIARY, word_node(head), *([word_node(negative)] if negative else []))
        carrier["index"] = link.index
        vp = self.vp([head, *tail], "finite", subject, incoming, fronted=link)
        core = branch("S′", AUXILIARY, carrier,
                      branch("S", CLAUSE, subject, vp, *([delayed] if delayed else [])))
        return self.attach(core, "S", before) if before else core

    def is_aux_inversion(self, parts):
        if not parts or not leaf(parts[0]) or tag(parts[0]) not in {"MD", "VBZ", "VBP", "VBD"}:
            return False
        head, *tail = parts
        if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"}:
            tail.pop(0)
        return bool(tail and tag(tail[0]) == "NP" and (
            lemma(head) in {"be", "have"}
            or self.auxiliary(head, [node for node in tail[1:] if tag(node) != "ADVP"])))

    def wh_gap(self, wh, body):
        label = tag(wh)
        if label == "WHADJP":
            return "predicative"
        if label == "WHPP":
            return "pp"
        if label == "WHADVP":
            wh_word = word(leaves(wh)[0])
            if wh_word == "how" and tag(body) == "SQ":
                sq_parts = kids(body)
                if (sq_parts and leaf(sq_parts[0]) and lemma(sq_parts[0]) == "be"
                        and not any(tag(n) == "VP" for n in sq_parts[1:])):
                    return "predicative"
            return "pp" if wh_word in {"where", "when"} else "adverbial"
        if label != "WHNP":
            raise ProjectionUnavailable(f"Unsupported {label} dependency")
        parts = kids(body)
        if tag(body) == "S" and len(parts) == 1 and tag(parts[0]) == "VP" and not self.is_nonfinite(body):
            return "subject"
        if tag(body) == "SQ":
            tail = parts[1:] if parts and leaf(parts[0]) else parts
            if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"}:
                tail = tail[1:]
            if parts and leaf(parts[0]) and tail and tag(tail[0]) == "VP":
                return "subject"
            if (not any(tag(node) == "VP" for node in tail)
                    and any(tag(node) == "NP" for node in tail)):
                return "predicative"
        # In "Who did ... say that submitted ..." and "... believe has
        # submitted ...", the wh-word fills the subject gap of a nested
        # subjectless clause, not an object position of the higher verb.
        for descendant in self.phrase_nodes(body):
            if tag(descendant) != "SBAR":
                continue
            inner = kids(descendant)
            if (inner and tag(inner[-1]) == "S" and kids(inner[-1])
                    and all(tag(part) == "VP" for part in kids(inner[-1]))):
                return "subject"
        if any(tag(node) == "PP" and len(kids(node)) == 1 for node in self.phrase_nodes(body)):
            return "preposition"
        return "object"

    def phrase_nodes(self, node):
        yield node
        for child in kids(node):
            yield from self.phrase_nodes(child)

    def wh_clause(self, parts, relative=False):
        if len(parts) != 2 or tag(parts[1]) not in {"S", "SQ"}:
            raise ProjectionUnavailable("Unsupported wh clause")
        wh, body = parts
        link = self.gap(self.wh_gap(wh, body))
        words = [n["surface"] for n in leaves(wh)]
        if len(words) == 1:
            fronted = branch("C2", WH, {"word": words[0]})
        else:
            lead = str(words[0]).lower()
            fronted_label = "PP" if lead in {
                "to", "for", "in", "on", "at", "by", "with", "from", "of",
                "about", "into", "over", "under", "between", "among",
                "against", "without", "after", "before", "during", "through",
                "across", "behind", "beside", "near", "as", "than",
            } else "NP"
            fronted = branch("C2", WH, {"triangle": True, "label": fronted_label,
                                        "words": words})
        fronted["index"] = link.index
        if tag(body) == "SQ":
            sq_parts = kids(body)
            if (not relative and link.kind == "subject" and sq_parts and leaf(sq_parts[0])
                    and (lemma(sq_parts[0]) == "be"
                         or self.auxiliary(sq_parts[0], [n for n in sq_parts[1:] if tag(n) != "ADVP" and not (leaf(n) and word(n) in {"not", "n't"})]))):
                head, *tail = sq_parts
                negative = tail.pop(0) if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"} else None
                subject = branch("NP", WH, link.take())
                carrier_link = self.gap("fronted verb")
                carrier = branch("C1", WH, word_node(head), *([word_node(negative)] if negative else []))
                carrier["index"] = carrier_link.index
                lower = branch("S′", WH, carrier,
                               branch("S", WH, subject, self.vp([head, *tail], "finite", subject, fronted=carrier_link)))
            else:
                lower = self.question(sq_parts, link)
        elif tag(body) == "S" and self.is_nonfinite(body):
            # Non-finite wh-clause ('how many guests to expect', B-R Ch10 [37]):
            # 'to' stays as AUX[-tense] inside VP and NEVER inverts into C1.
            lower = branch("S′", NONFINITE, branch("C1", NONFINITE),
                           self.nonfinite(body, wrap=False, incoming=link))
        elif not relative and link.kind == "subject" and len(kids(body)) == 1:
            vp = kids(kids(body)[0])
            if vp and leaf(vp[0]) and tag(vp[0]) != "TO" and (
                lemma(vp[0]) == "be" or self.auxiliary(vp[0], [n for n in vp[1:] if tag(n) != "ADVP"])
            ):
                head, *tail = vp
                negative = tail.pop(0) if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"} else None
                subject = branch("NP", WH, link.take())
                carrier_link = self.gap("fronted verb")
                carrier = branch("C1", WH, word_node(head), *([word_node(negative)] if negative else []))
                carrier["index"] = carrier_link.index
                lower = branch("S′", WH, carrier, branch("S", WH, subject, self.vp([head, *tail], "finite", subject, fronted=carrier_link)))
            else:
                lower = branch("S′", WH, branch("C1", WH), self.clause(body, link))
        else:
            lower = branch("S′", WH, branch("C1", WH), self.clause(body, link))
        if not link.used:
            raise ProjectionUnavailable("Wh-phrase has no uniquely identified gap")
        return branch("S″", WH, fronted, lower)

    def relative(self, node):
        parts = kids(node)
        if (len(parts) == 2 and tag(parts[0]) == "WHNP" and leaves(parts[0])
                and word(leaves(parts[0])[0]) == "that" and tag(parts[1]) == "S"):
            # B-R Ch9 [53a]: in a gapped 'that'-relative clause, 'that' occupies
            # C2 with an empty C1 in S-bar (S-dbar -> C2(that) + S-bar(C1[], S)).
            return self.wh_clause(parts, relative=True)
        if parts and tag(parts[0]).startswith("WH"):
            return self.wh_clause(parts, relative=True)
        if len(parts) == 2 and leaf(parts[0]) and word(parts[0]) == "that" and tag(parts[1]) == "S":
            return self.wh_clause([raw("WHNP", [parts[0]]), parts[1]], relative=True)
        if len(parts) == 2 and leaf(parts[0]) and word(parts[0]) == "for" and tag(parts[1]) == "S" and self.is_nonfinite(parts[1]):
            # Non-finite for-to modifier ('the cheapest way for people to take a trip')
            return branch("S′", NONFINITE, branch("C1", NONFINITE, word_node(parts[0])), self.nonfinite(parts[1], wrap=False))
        if len(parts) != 1 or tag(parts[0]) != "S":
            raise ProjectionUnavailable("Unsupported relative clause")
        # Non-finite infinitival modifier ('editors to review the new information')
        if self.is_nonfinite(parts[0]):
            return self.nonfinite(parts[0])
        # A zero relative with an overt subject can introduce an object or
        # stranded-preposition gap ('the subjects they are interested in').
        gap_kind = ("preposition"
                    if any(tag(n) == "PP" and len(kids(n)) == 1 for n in self.phrase_nodes(parts[0]))
                    else "object")
        link = self.gap(gap_kind)
        body = self.clause(parts[0], link)
        if not link.used:
            raise ProjectionUnavailable("Relative clause has no uniquely identified object gap")
        operator = branch("C2", WH, {"gap": True, "index": link.index})
        operator["index"] = link.index
        return branch("S″", WH, operator, branch("S′", WH, branch("C1", WH), body))
