"""Compositional FINAL-D1 projection from Benepar structure and token evidence."""
from dataclasses import dataclass

from lemminflect import getLemma


CLAUSE = ("Ch2 pp. 29–30",)
NOUN = ("Ch7 pp. 141–144",)
NOMINAL = ("Ch7 pp. 165–168",)
LOCATIVE = ("Ch3 p. 57 [19]", "Ch4 pp. 74–75, 78")
ADVERBIAL = ("Ch5 pp. 87–93",)
AUXILIARY = ("Ch6 pp. 114–132",)
ELLIPSIS = ("Ch5 pp. 95–99",)
SUBORDINATE = ("Ch8 pp. 173–187",)
WH = ("Ch9 pp. 196–211",)
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
DETERMINERS = {
    **dict.fromkeys(("a", "an", "the"), "ART"),
    **dict.fromkeys(("this", "that", "these", "those"), "DEM"),
    **dict.fromkeys(("some", "any", "no", "each", "every", "either", "neither", "several", "enough"), "Q"),
}
DEGREE = {"very", "too", "rather", "quite", "so", "as", "more", "most", "less", "least", "somewhat", "how", "almost", "extremely", "fairly", "any"}
QA = {"many", "few", "much", "little", "more", "less", "fewer", "most", "least"}
PREDET = {"all", "both", "half", "double", "twice"}
PRONOUNS = {"everyone", "everybody", "everything", "anyone", "anybody", "anything",
            "someone", "somebody", "something", "nobody", "nothing", "none"}
SUBORDINATORS = {"if", "unless", "because", "although", "though", "while", "whereas", "when", "once", "as", "until", "before", "after", "since"}
TEMPORAL_P = {"after", "before", "until"}
TIME_NOUNS = {"today", "tomorrow", "yesterday", "tonight", "night", "week", "year", "day", "time", "moment"}
LOCATIVE_WORDS = {"here", "there", "upstairs", "downstairs", "outside", "inside"}
LOCATIVE_PREPOSITIONS = {"above", "across", "against", "along", "at", "behind", "below", "beside",
                        "between", "beyond", "by", "in", "inside", "near", "on", "outside", "under"}
INTENSIVE = {"be", "become", "seem", "appear", "look", "feel", "sound", "taste", "smell", "remain", "get", "grow", "prove"}
COMPLEX = {"call", "consider", "find", "keep", "make", "paint", "put", "render", "name", "elect", "turn", "get"}
DITRANSITIVE = {"give", "tell", "show", "send", "offer", "lend", "bring", "pay", "buy", "hand", "teach", "ask", "promise", "write", "read", "pass", "sell", "owe", "leave"}
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
TYPE_I = {"believe", "expect", "prefer", "want", "know", "hear", "watch", "like", "suppose", "consider", "imagine", "find", "see", "notice", "feel", "help"}
PASSIVE_TYPE_I = {"assume", "believe", "consider", "expect", "know", "report", "say", "suppose", "think"}
TYPE_II = {"persuade", "ask", "encourage", "force", "invite", "order", "tell", "teach", "promise", "advise", "require", "allow"}
SUBJECT_CONTROL = {"agree", "ask", "begin", "continue", "decide", "fail", "forget", "hope", "intend", "learn", "like", "love", "manage", "need", "offer", "plan", "prefer", "promise", "refuse", "remember", "start", "stop", "try", "want", "enjoy", "avoid", "afford"}
CONTROL_ADJECTIVES = {"anxious", "eager", "keen", "hesitant", "unwilling", "happy", "liable", "reluctant"}
RAISING_ADJECTIVES = {"likely", "unlikely"}
OBJECT_GAP_ADJECTIVES = {"easy", "hard", "difficult", "tough", "tiresome", "boring", "enjoyable", "disgusting", "delicious", "impossible", "worth"}
CLAUSAL_NOUNS = {"fact", "idea", "claim", "news", "belief", "rumour", "report", "decision", "question",
                 "possibility", "thought", "conclusion", "suggestion", "plan", "promise", "wish", "need"}


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
        leaf(child) and (child.get("punct") or child["surface"] in {"[", "]", "(", ")", ":", ";"}))]


def raw(label, children):
    return {"type": label, "children": children}


def leaves(node):
    return [node] if leaf(node) else [item for child in kids(node) for item in leaves(child)]


def lemma(node):
    term = word(node)
    if term in {"am", "is", "are", "was", "were", "been", "being", "'m", "'re", "'s"}:
        return "be"
    return next(iter(getLemma(term, upos="VERB", lemmatize_oov=False)), term)


def tense(node, mode):
    if mode == "untensed":
        return None
    if mode == "nonfinite":
        return "-tense"
    if tag(node) not in {"VBZ", "VBP", "VBD", "MD"}:
        raise ProjectionUnavailable("Finite clause has no identifiable tense carrier")
    return "past" if tag(node) == "VBD" or word(node) in {"could", "might", "should", "would", "'d"} else "pres"


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
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def dependency(self, node):
        start = node.get("span", [None])[0]
        return self.tokens.get(start, {}).get("dep")

    def gap(self, kind):
        self.index += 1
        return Gap(self.index, kind)

    def coordinate(self, nodes, convert):
        links = [i for i, node in enumerate(nodes) if tag(node) == "CC" and leaf(node)]
        if len(links) != 1:
            return None
        i = links[0]
        if not i or i == len(nodes) - 1:
            raise ProjectionUnavailable("Incomplete coordination")
        return convert(nodes[:i]), word_node(nodes[i]), convert(nodes[i + 1:])

    def phrase(self, node):
        label = tag(node)
        if label == "NP":
            raw_children = node.get("children", [])
            nonrestrictive = {id(child) for preceding, child in zip(raw_children, raw_children[1:])
                              if preceding.get("surface") == "," and tag(child) == "SBAR"}
            return self.np(kids(node), nonrestrictive)
        if label == "PP":
            return self.pp(kids(node))
        if label in {"ADJP", "ADVP"}:
            parts = kids(node)
            if label == "ADVP" and len(parts) == 1 and leaf(parts[0]):
                if word(parts[0]) in LOCATIVE_WORDS:
                    return branch("PP", LOCATIVE, branch("P", LOCATIVE, word_node(parts[0])))
                if tag(parts[0]) in {"IN", "RP"}:
                    return self.pp(parts)
            return self.modifier(parts, adjective=label == "ADJP")
        if label in {"S", "SQ", "SBARQ", "SBAR", "SINV"}:
            return self.clause(node)
        if leaf(node) and label in ADV_TAGS:
            return self.modifier([node])
        raise ProjectionUnavailable(f"Unsupported {label} phrase")

    def modifier(self, nodes, adjective=False, quantifying=False):
        category = "AP" if adjective else "AdvP"
        refs = ("Ch3 pp. 55–56",)
        coordination = self.coordinate(nodes, lambda part: self.modifier(part, adjective, quantifying))
        if coordination:
            return branch(category, COORD, *coordination)
        if len(nodes) == 1 and tag(nodes[0]) == ("ADJP" if adjective else "ADVP"):
            return self.phrase(nodes[0])
        head_tags = ADJ_TAGS | ({"CD", "DT", "NN", "RB"} if quantifying else set()) if adjective else ADV_TAGS | {"NN"}
        head = next((i for i in range(len(nodes) - 1, -1, -1)
                     if leaf(nodes[i]) and tag(nodes[i]) in head_tags), None)
        if head is None:
            raise ProjectionUnavailable(f"{category} has no identifiable head")
        before = [branch("DEG", refs, word_node(n)) if leaf(n) and word(n) in DEGREE else self.phrase(n) for n in nodes[:head]]
        after = [self.phrase(n) for n in nodes[head + 1:]]
        if after and not adjective:
            raise ProjectionUnavailable("Unsupported complement of AdvP")
        return branch(category, refs, *before,
                      branch("QA" if quantifying else "A" if adjective else "Adv", refs, word_node(nodes[head])), *after)

    def pp(self, nodes, gap=None):
        if len(nodes) > 1 and leaf(nodes[0]) and word(nodes[0]) == "not":
            return branch("PP", ADVERBIAL, word_node(nodes[0]), self.pp(nodes[1:], gap))
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
        elif len(tail) == 1:
            tail = [self.phrase(tail[0])]
        elif tail:
            raise ProjectionUnavailable("PP has multiple unclassified dependents")
        return branch("PP", ("Ch3 pp. 56–59",), head, *tail)

    def np(self, nodes, nonrestrictive=()):
        if not nodes:
            raise ProjectionUnavailable("Empty overt noun phrase")
        if len(nodes) > 1 and leaf(nodes[0]) and tag(nodes[0]) in ADV_TAGS and word(nodes[0]) in {"only", "almost", "even", "just"}:
            result = branch("NP", NOUN, self.modifier([nodes[0]]), self.np(nodes[1:], nonrestrictive))
            result["notes"] = ["The focusing adverb modifies the following NP."]
            return result
        coordination = self.coordinate(nodes, lambda part: self.np(part, nonrestrictive))
        if coordination:
            return branch("NP", COORD, *coordination)
        if len(nodes) == 1 and tag(nodes[0]) == "NP":
            return self.phrase(nodes[0])
        if tag(nodes[0]) == "SBAR" and len(nodes) == 1:
            return branch("NP", SUBORDINATE, self.clause(nodes[0]))
        if len(nodes) == 1 and leaf(nodes[0]) and (tag(nodes[0]) in {"PRP", "EX"} or word(nodes[0]) in PRONOUNS):
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
            if inside and leaf(inside[0]) and word(inside[0]) in PREDET:
                return branch("NP", NOUN, branch("PRE-DET", NOUN, word_node(inside[0])),
                              self.np([raw("NP", inside[1:]), *nodes[1:]], nonrestrictive))
            base = self.phrase(nodes[0])
            if len(nodes) == 2 and id(nodes[1]) in nonrestrictive:
                return branch("NP", WH, base, self.relative(nodes[1]))
            if base["children"][0]["label"] == "DET":
                det, nominal = base["children"]
                modifiers = nodes[1:]
                head_word = word(leaves(nodes[0])[-1])
            elif base["children"][0]["label"] == "pronoun" and len(nodes) == 2 and tag(nodes[1]) in {"PP", "ADJP"}:
                return branch("NP", ("Ch7 pp. 155–157",), base["children"][0], self.phrase(nodes[1]))
            else:
                raise ProjectionUnavailable("Unsupported modifier of a name or pronoun")
        else:
            det = branch("DET", ("Ch7 p. 143 [10]",))
            start = 0
            first = nodes[0]
            if leaf(first) and (tag(first) == "PRP$" or word(first) in DETERMINERS):
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
                             and tag(nodes[i - 1]) == "JJR"))), None)
            if head is None:
                if len(nodes) == 1 and leaf(nodes[0]) and tag(nodes[0]) == "CD":
                    return branch("NP", NOUN, det, branch("NOM", NOMINAL, self.modifier(nodes, adjective=True, quantifying=True)))
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
                elif tag(mod) == "ADJP":
                    phrase = self.phrase(mod)
                elif tag(mod) == "QP":
                    phrase = self.modifier(kids(mod), adjective=True, quantifying=True)
                else:
                    phrase = self.modifier([mod], adjective=True, quantifying=word(mod) in QA or tag(mod) == "CD")
                nominal = branch("NOM", NOMINAL, phrase, nominal)
        for mod in modifiers:
            if tag(mod) == "SBAR":
                if self.noun_complement(head_word, mod):
                    phrase = self.clause(mod)
                    if len(nominal["children"]) == 1 and nominal["children"][0].get("label") == "N":
                        nominal = branch("NOM", NOMINAL, nominal["children"][0], phrase)
                        continue
                    raise ProjectionUnavailable("Noun complement has ambiguous attachment")
                phrase = self.relative(mod)
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
            elif tag(mod) in {"PP", "ADJP"}:
                phrase = self.phrase(mod)
            elif leaf(mod) and tag(mod) in ADJ_TAGS:
                phrase = self.modifier([mod], adjective=True)
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
            or (tag(node) == "PP" and word(dependents[0]) == "of"
                and noun in {"number", "group", "bunch", "part", "rest", "kind", "type", "amount", "pair", "picture", "photo", "member"}))

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
        return self.phrase(node)

    def attach(self, tree, label, leading=(), trailing=()):
        for node in reversed(leading):
            tree = branch(label, ADVERBIAL, self.adjunct(node), tree)
        for node in trailing:
            tree = branch(label, ADVERBIAL, tree, self.adjunct(node))
        return tree

    def auxiliary(self, head, tail):
        if tag(head) == "MD" or (word(head) in {"need", "dare"} and len(tail) == 1
                                  and tag(tail[0]) == "VP" and kids(tail[0]) and tag(kids(tail[0])[0]) == "VB"):
            return "MOD"
        if tag(head) == "TO":
            return "AUX"
        if len(tail) != 1 or tag(tail[0]) != "VP":
            return None
        first = kids(tail[0])
        if not first:
            return None
        base = lemma(head)
        next_tag = tag(first[0])
        if (base == "have" or word(head) in {"'ve", "'s", "'d"}) and next_tag == "VBN":
            return "PASS" if word(head) == "'s" and self.dependency(first[0]) == "ROOT" and self.dependency(head) == "auxpass" else "PERF"
        if base == "be" and next_tag in {"VBN", "VBG"}:
            return "PASS" if next_tag == "VBN" else "PROG"
        if base == "do" and next_tag in {"VB", "VBP"}:
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
        # An auxiliary can be followed by adverbials before its VP complement.
        auxiliary_tail = [node for node in tail if tag(node) not in {"ADVP"}]
        aux = self.auxiliary(head, auxiliary_tail)
        head_words = [fronted.take() if fronted else word_node(head)]
        if negation:
            head_words.append(word_node(negation))
        if aux:
            if len(auxiliary_tail) != 1 or tag(auxiliary_tail[0]) != "VP":
                raise ProjectionUnavailable("Auxiliary has no overt VP complement")
            target = auxiliary_tail[0]
            position = tail.index(target)
            aux_tense = "-tense" if aux == "AUX" else tense(head, mode)
            lexical_passive = passive
            if aux == "PASS":
                if passive is not None or subject is None:
                    raise ProjectionUnavailable("Passive has no unambiguous promoted subject")
                lexical_passive = self.link_subject(subject)
                lexical_passive.kind = "object"
            complement = self.vp(kids(target), "untensed", subject, incoming, lexical_passive)
            complement = self.attach(complement, "VP", tail[:position], tail[position + 1:])
            return branch("VP", AUXILIARY, branch(aux, AUXILIARY, *head_words,
                          features=(aux_tense,) if aux_tense else ()), complement)

        base = lemma(head)
        feature = tense(head, mode)
        features = (feature,) if feature else ()
        if negation and base != "be" and not (base == "have" and mode == "finite"):
            raise ProjectionUnavailable("Negation attached directly to a non-auxiliary lexical verb")
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
            if len(small) == 1 and tag(small[0]) in {"ADJP", "NP", "PP"} and base in INTENSIVE:
                tail[:1] = small
            elif len(small) == 2 and tag(small[0]) == "NP" and tag(small[1]) in {"ADJP", "NP", "PP"} and base in COMPLEX:
                tail[:1] = small

        if tail and tag(tail[0]) == "S" and self.is_nonfinite(tail[0]) and base in SUBJECT_CONTROL | TYPE_I:
            lower = tail.pop(0)
            overt = len(kids(lower)) == 2
            if overt and base not in TYPE_I or not overt and base not in SUBJECT_CONTROL:
                raise ProjectionUnavailable("Non-finite complement has no supported control analysis")
            clause = self.nonfinite(lower, None if overt else subject)
            v = branch("V(I)" if overt else "V", NONFINITE, *head_words, features=features)
            return self.attach(branch("VP", NONFINITE, v, clause), "VP", trailing=tail)
        if len(tail) >= 2 and tag(tail[0]) == "NP" and tag(tail[1]) == "S" and self.is_nonfinite(tail[1]) and base in TYPE_II:
            obj = self.phrase(tail[0])
            lower = self.nonfinite(tail[1], subject if base == "promise" else obj)
            v = branch("V(II)", NONFINITE, *head_words, features=features)
            return self.attach(branch("VP", NONFINITE, v, obj, lower), "VP", trailing=tail[2:])

        complement = []
        particle = None
        if tail and tag(tail[0]) == "PRT":
            particle = tail.pop(0)
        if incoming and not passive and tail and tag(tail[0]) == "SBAR" and not self.is_adverbial(tail[0]):
            parts = kids(tail[0])
            if parts and not tag(parts[0]).startswith("WH"):
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
                if not tail or tag(tail[0]) != "PP" or len(kids(tail[0])) != 1:
                    raise ProjectionUnavailable("Wh-phrase has no unique stranded preposition")
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
            else:
                if base in KNOWN_INTRANS or (tail and tag(tail[0]) == "NP" and not self.is_time_np(tail[0])):
                    raise ProjectionUnavailable("Object gap conflicts with the verb frame or an overt object")
                frame = "trans"
                complement.append(branch("NP", AUXILIARY if passive else WH, incoming.take()))
        elif base in INTENSIVE and tail and self.is_predicative(base, tail[0]):
            frame = "intens"
            complement.append(self.predicative(tail.pop(0), subject))
        elif (base in {"give", "send", "lend", "hand", "pass", "sell", "offer", "show", "write"}
              and len(tail) >= 2 and tag(tail[0]) == "PP" and kids(tail[0])
              and word(kids(tail[0])[0]) == "to" and tag(tail[1]) == "NP" and not self.is_time_np(tail[1])):
            frame = "ditrans"
            complement.extend(self.phrase(n) for n in tail[:2])
            tail = tail[2:]
        elif tail and tag(tail[0]) == "NP" and not self.is_time_np(tail[0]):
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
                elif base in COMPLEX and (label in {"NP", "ADJP"} or base == "put"):
                    frame = "complex"
                if frame != "trans":
                    complement.append(self.phrase(tail.pop(0)))
            if base == "put" and frame == "trans" and particle is None and not any(tag(node) == "PRT" for node in tail):
                raise ProjectionUnavailable("Put has no overt or licensed covert object-predicative")
        elif tail and tag(tail[0]) == "PP" and self.selected_pp(base, tail[0]):
            frame = "prep"
            complement.append(self.phrase(tail.pop(0)))
        elif tail and tag(tail[0]) == "SBAR" and not self.is_adverbial(tail[0]):
            frame = "intens" if base == "be" else "trans"
            clause = self.clause(tail.pop(0))
            complement.append(clause if frame == "intens" else branch("NP", SUBORDINATE, clause))
        else:
            if base in REQUIRES_COMPLEMENT | {"be"} and particle is None:
                raise ProjectionUnavailable(f"{base} has no overt or licensed covert complement")
            frame = "intrans"
        refs = FRAME_REFS[frame]
        if base == "sleep":
            refs += ("Ch5 p. 104 [1e]",)
        v_refs = (*refs, "Ch6 p. 113 [8]–[9]") if feature else refs
        suffix = ("phrasal",) if particle is not None or tail and tag(tail[0]) == "PRT" else ()
        if particle is not None:
            head_words.extend(word_node(n) for n in leaves(particle))
        elif tail and tag(tail[0]) == "PRT":
            complement.append(branch("Prt", ("Ch5 pp. 93–95",), *(word_node(n) for n in leaves(tail.pop(0)))))
        v = branch("V", v_refs, *head_words, features=(frame, *suffix, *features))
        for extra in tail:
            label = tag(extra)
            if label not in {"ADVP", "PP", "SBAR", "NP", "S"} or (label == "NP" and not self.is_time_np(extra)) or (label == "SBAR" and not self.is_adverbial(extra)) or (label == "S" and not self.is_nonfinite(extra)):
                raise ProjectionUnavailable(f"Unclassified VP dependent {label}")
        return self.attach(branch("VP", refs, v, *complement), "VP", trailing=tail)

    def is_time_np(self, node):
        words = leaves(node)
        return bool(words) and (self.dependency(node) == "npadvmod"
            or (word(words[-1]).rstrip("s") in TIME_NOUNS and
                (len(words) == 1 or word(words[0]) in {"all", "every", "last", "next", "this", "that"})))

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
        return len(parts) == 2 and (
            (leaf(parts[0]) and word(parts[0]) in SUBORDINATORS)
            or (tag(parts[0]) in {"WHNP", "WHADVP"} and leaves(parts[0])
                and word(leaves(parts[0])[0]) in {"whatever", "whoever", "whenever", "wherever", "however"}))

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
            if parts and tag(parts[0]).startswith("WH"):
                return self.wh_clause(parts)
            if not parts or tag(parts[-1]) != "S" or len(parts) > 2:
                raise ProjectionUnavailable("Unsupported subordinate clause wrapper")
            if len(parts) == 2 and (not leaf(parts[0]) or word(parts[0]) not in SUBORDINATORS | {"that", "whether", "for"}):
                raise ProjectionUnavailable("Unrecognized complementiser")
            if len(parts) == 2 and word(parts[0]) in TEMPORAL_P:
                return branch("PP", SUBORDINATE, branch("P", SUBORDINATE, word_node(parts[0])), self.clause(parts[-1], incoming))
            carrier = branch("C1", SUBORDINATE, *(word_node(n) for n in parts[:-1]))
            body = self.nonfinite(parts[-1], wrap=False) if len(parts) == 2 and word(parts[0]) == "for" and self.is_nonfinite(parts[-1]) else self.clause(parts[-1], incoming)
            return branch("S′", SUBORDINATE, carrier, body)
        if label != "S":
            raise ProjectionUnavailable(f"Unsupported clause structure {label}")
        raw_children = node.get("children", [])
        if (len(parts) == 2 and all(tag(n) in {"S", "SQ", "SBARQ", "SINV"} for n in parts)
                and len(raw_children) >= 3 and raw_children[1].get("surface") in {":", ";"}
                and incoming is None):
            result = branch("S", COORD, *(self.clause(n) for n in parts))
            result["notes"] = ["The punctuation joins two independently projected clauses and remains in the submitted text."]
            return result
        if incoming is None:
            elliptical = self.coordinated_ellipsis(parts)
            if elliptical:
                return elliptical
        coordination = self.coordinate(parts, lambda nodes: self.clause(nodes[0] if len(nodes) == 1 else raw("S", nodes)))
        if coordination:
            if incoming:
                raise ProjectionUnavailable("Unresolved movement across coordinated clauses")
            return branch("S", COORD, *coordination)
        if len(parts) == 1 and tag(parts[0]) == "S":
            return self.clause(parts[0], incoming)
        if len(parts) == 1 and tag(parts[0]) == "VP" and incoming is None:
            vp_parts = kids(parts[0])
            if vp_parts and leaf(vp_parts[0]) and tag(vp_parts[0]) == "VB" and lemma(vp_parts[0]) == word(vp_parts[0]):
                imperative = ("Ch3 p. 66; Ch10 pp. 224–225",)
                subject = branch("NP", imperative, {"gap": True})
                return branch("S", imperative, subject, self.vp(vp_parts, "untensed", subject))
        before = []
        while len(parts) > 1 and tag(parts[0]) in {"PP", "ADVP", "SBAR"} and not (
                tag(parts[0]) == "SBAR" and not self.is_adverbial(parts[0])):
            before.append(parts.pop(0))
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
        if len(parts) != 1 or tag(parts[0]) != "VP":
            raise ProjectionUnavailable("Clause has no single identifiable predicate")
        predicate_parts = kids(parts[0])
        # Expletive subject and a delayed that-clause in the documented extraposition frame.
        delayed = None
        if (len(predicate_parts) >= 2 and leaf(predicate_parts[0]) and lemma(predicate_parts[0]) in {"be", "seem", "appear", "happen"}
                and tag(predicate_parts[-1]) == "SBAR" and not self.is_adverbial(predicate_parts[-1])
                and subject.get("children", [{}])[0].get("label") == "pronoun"
                and subject["children"][0]["children"][0]["word"].lower() == "it"
                and (lemma(predicate_parts[0]) != "be" or len(predicate_parts) >= 3)):
            delayed = self.clause(predicate_parts.pop())
        vp = self.vp(predicate_parts, "finite", subject, incoming if incoming and not incoming.used else None)
        vp = self.attach(vp, "VP", early)
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
        if len(parts) == 1 and tag(parts[0]) == "VP" and self.is_aux_inversion(kids(parts[0])):
            parts = kids(parts[0])
        if len(parts) < 2 or not leaf(parts[0]):
            raise ProjectionUnavailable("Unsupported inversion or question tag")
        head, *tail = parts
        negative = tail.pop(0) if tail and leaf(tail[0]) and word(tail[0]) in {"not", "n't"} else None
        if not tail or tag(tail[0]) != "NP":
            raise ProjectionUnavailable("Inversion has no identifiable subject NP")
        raw_subject = tail.pop(0)
        if tag(head) not in {"MD", "VBZ", "VBP", "VBD"} or (
                self.auxiliary(head, [node for node in tail if tag(node) != "ADVP"]) is None
                and lemma(head) not in {"be", "have"}):
            raise ProjectionUnavailable("No licensed auxiliary or auxiliary-behaving verb in C1")
        subject = self.phrase(raw_subject)
        link = self.gap("fronted verb")
        carrier = branch("C1", AUXILIARY, word_node(head), *([word_node(negative)] if negative else []))
        carrier["index"] = link.index
        vp = self.vp([head, *tail], "finite", subject, incoming, fronted=link)
        return branch("S′", AUXILIARY, carrier, branch("S", CLAUSE, subject, vp))

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
            return "pp" if word(leaves(wh)[0]) == "where" else "adverbial"
        if label != "WHNP":
            raise ProjectionUnavailable(f"Unsupported {label} dependency")
        parts = kids(body)
        if tag(body) == "S" and len(parts) == 1 and tag(parts[0]) == "VP":
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
        fronted = branch("C2", WH, *([{"word": words[0]}] if len(words) == 1 else [{"triangle": True, "words": words}]))
        fronted["index"] = link.index
        if tag(body) == "SQ":
            lower = self.question(kids(body), link)
        elif not relative and link.kind == "subject" and len(kids(body)) == 1:
            vp = kids(kids(body)[0])
            if vp and leaf(vp[0]) and (
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
        if parts and tag(parts[0]).startswith("WH"):
            return self.wh_clause(parts, relative=True)
        if len(parts) == 2 and leaf(parts[0]) and word(parts[0]) == "that" and tag(parts[1]) == "S":
            return self.wh_clause([raw("WHNP", [parts[0]]), parts[1]], relative=True)
        if len(parts) != 1 or tag(parts[0]) != "S":
            raise ProjectionUnavailable("Unsupported relative clause")
        # A zero relative with an overt subject can introduce an object gap.
        link = self.gap("object")
        body = self.clause(parts[0], link)
        if not link.used:
            raise ProjectionUnavailable("Relative clause has no uniquely identified object gap")
        operator = branch("C2", WH, {"gap": True, "index": link.index})
        return branch("S″", WH, operator, branch("S′", WH, branch("C1", WH), body))
