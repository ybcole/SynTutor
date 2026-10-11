"""SynTutor entity-classification lexicon (Stage 11 helper).

A small, deterministic, *optional-dependency* module that turns a noun lemma
(or pronoun surface) into one of the coarse entity classes used by the
selectional-restriction (R11.4) and subject–predicate compatibility (R11.6)
checks:

    'animate'   — a person or an animal (can be an agent / feel states)
    'living'    — a living organism that is not clearly an animate agent
                  (plants, fungi, bacteria, …)
    'inanimate' — a physical, man-made / material thing (artifact)
    'abstract'  — a concept, number, quality, state or the like
    None        — *unclassified*: no evidence establishes a class

Design rules
------------
* Explicit, high-confidence project lexicons (in :mod:`server.semantics`) are
  consulted first and always win.
* When the lemma is not covered there, WordNet (NLTK) is used as a local,
  offline fallback.  No network call is ever made at request time and no
  model is trained.
* WordNet is *optional*.  If NLTK or the corpus is unavailable the classifier
  degrades to the explicit lexicons and returns ``None`` — never a guessed
  class.  The application stays fully functional.
* Classifications are deterministic for fixed inputs, NLTK/WordNet versions
  and configuration: synsets are inspected in WordNet's fixed order and a
  lookup is cached in-process.

Polysemy policy
---------------
A lemma is classified only when a **strict majority** of its noun synsets
agree on one class.  This deliberately avoids trusting the first synset for a
polysemous word (``bat`` = animal vs. sports equipment; ``bank`` = slope vs.
financial institution) and preserves ``None`` as a legitimate, honest result.
"""

from __future__ import annotations

from collections import Counter

# ── WordNet resource handling ───────────────────────────────────────────────

_WORDNET_ERROR = None
_WORDNET = None


def _load_wordnet():
    """Import NLTK's WordNet lazily; return the corpus module or ``None``.

    The corpus is *not* downloaded here.  A missing corpus (or a missing NLTK
    install) disables the fallback and is reported by :func:`resource_status`.
    """
    global _WORDNET, _WORDNET_ERROR
    if _WORDNET is not None:
        return _WORDNET
    if _WORDNET_ERROR is not None:
        return None
    try:
        from nltk.corpus import wordnet as wn

        # Touch the corpus so a missing resource is detected eagerly and the
        # error is cached (no per-call retry / no request-time download).
        wn.synsets('dog', pos='n')
        _WORDNET = wn
        return wn
    except Exception as exc:  # noqa: BLE001 - any import/corpus failure
        _WORDNET_ERROR = exc
        return None


def resource_status():
    """``{'available': bool, 'detail': str}`` for diagnostics / documentation."""
    wn = _load_wordnet()
    if wn is None:
        return {'available': False, 'error': str(_WORDNET_ERROR)}
    return {'available': True,
            'synsets_dog': len(_WORDNET.synsets('dog', pos='n'))}


# ── WordNet hypernym classification ─────────────────────────────────────────

# Named WordNet synsets that anchor each coarse class.  These were verified
# against the shipped WordNet corpus (see ``scripts/audit_semantics.py``):
#   living_thing.n.01  "a living (or once living) entity"
#   animal.n.01        "a living organism characterized by voluntary movement"
#   person.n.01        "a human being"
#   artifact.n.01      "a man-made object taken as a whole"
#   abstraction.n.06   "a general concept formed by extracting common features …"
_ANIMATE_ROOTS = ('animal.n.01', 'person.n.01')
_LIVING_ROOT = 'living_thing.n.01'
_ARTIFACT_ROOT = 'artifact.n.01'
_ABSTRACT_ROOT = 'abstraction.n.06'

_CLASS_CACHE: dict[str, str | None] = {}


def _hypernym_names(synset) -> set[str]:
    names: set[str] = set()
    for path in synset.hypernym_paths():
        names.update(h.name() for h in path)
    return names


def _synset_class(synset) -> str | None:
    names = _hypernym_names(synset)
    if any(root in names for root in _ANIMATE_ROOTS):
        return 'animate'
    if _LIVING_ROOT in names:
        return 'living'
    if _ARTIFACT_ROOT in names:
        return 'inanimate'
    if _ABSTRACT_ROOT in names:
        return 'abstract'
    return None


def wordnet_class(lemma: str) -> str | None:
    """WordNet-only classification of a noun lemma (or ``None``).

    Requires a strict majority of the noun's synsets to agree; otherwise the
    word is treated as unclassified (polysemous / insufficient evidence).
    """
    lemma = (lemma or '').strip().lower()
    if not lemma:
        return None
    if lemma in _CLASS_CACHE:
        return _CLASS_CACHE[lemma]

    result: str | None = None
    wn = _load_wordnet()
    if wn is not None:
        synsets = wn.synsets(lemma, pos='n')
        votes = Counter(c for c in (_synset_class(s) for s in synsets) if c)
        total = len(synsets)
        if votes and total:
            # Deterministic tie-break by class name; only a strict majority wins.
            winner, count = max(sorted(votes.items()), key=lambda kv: kv[1])
            if count > total / 2:
                result = winner
    _CLASS_CACHE[lemma] = result
    return result


def reset_cache() -> None:
    """Clear the classification cache (used by tests)."""
    _CLASS_CACHE.clear()


# ── pronoun classification ──────────────────────────────────────────────────

# Conservative, feature-based pronoun classes.  A pronoun is *not* a free
# entity classifier: its referent is known only from context.  Only pronouns
# whose referent is a discourse participant or a known 3sg human are marked
# animate; genuinely ambiguous pronouns (it/they/them) stay unclassified so no
# finding is ever built on an unjustified assumption.
PRONOUN_ENTITY_CLASS: dict[str, str] = {
    # first/second person: speech-act participants are animate agents
    'i': 'animate',
    'we': 'animate',
    'you': 'animate',
    # third-person singular humans
    'he': 'animate',
    'she': 'animate',
    'him': 'animate',
    'her': 'animate',
    # 'it' may be animate or inanimate; 'they/them' may be either
    'it': None,
    'they': None,
    'them': None,
}


def pronoun_class(surface: str) -> str | None:
    return PRONOUN_ENTITY_CLASS.get((surface or '').strip().lower())


def resource_status_text() -> str:
    """One-line human-readable status for diagnostics / documentation."""
    if _load_wordnet() is not None:
        return 'WordNet available (NLTK) — WordNet fallback active'
    return ('WordNet unavailable — explicit lexicons only '
            '(install with: python3 -m nltk.downloader wordnet)')
