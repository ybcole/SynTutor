"""Hybrid detection channel: a CoLA-fine-tuned acceptability classifier.

SynTutor's verdict is now two-phase:

1. **Detection** (this module): a trained RoBERTa acceptability model decides
   whether the sentence is acceptable English. Broad coverage without a rule
   per error.
2. **Explanation** (the rule matrix / licensing layer): deterministic
   constraints say *why* a sentence is wrong and stay the explainable core.

A sentence is grammatical *only if both channels accept it*.  When the matrix
stays clean but the model rejects the input, the rules cannot explain the
rejection, so the verdict degrades to ``unverified`` and the model's reasoning
is surfaced instead of a fabricated rule explanation.

The detector is optional: if it cannot be loaded (no network, missing weights,
OOM, torch unavailable) ``classify`` returns ``None`` and the payload falls
back to the rules-only verdict, exactly like the licensing layer degrades.
"""

import os

_MODEL_ID = os.environ.get(
    'SYNTUTOR_DETECTOR_MODEL', 'textattack/roberta-base-CoLA')
_FLAG_TOLERANCE = float(os.environ.get('SYNTUTOR_DETECTOR_FLAG_TOL', '0.5'))

_PIPELINE = None
_LOAD_ERROR = None
_LOAD_ERROR_REPORTED = False

_ACCEPTABLE_LABELS = {'acceptable', 'LABEL_1'}


def load_detector():
    """Load the pipeline once, CPU-only, and cache it (never crash the app)."""
    global _PIPELINE, _LOAD_ERROR, _LOAD_ERROR_REPORTED
    if _PIPELINE is not None:
        return _PIPELINE
    if _LOAD_ERROR is not None:
        if not _LOAD_ERROR_REPORTED:
            import sys
            sys.stderr.write(f'[syntutor] detector unavailable: {_LOAD_ERROR}\n')
            _LOAD_ERROR_REPORTED = True
        return None
    try:
        import torch  # noqa: F401  (ensures torch import order)
        from transformers import pipeline
        _PIPELINE = pipeline(
            'text-classification',
            model=_MODEL_ID,
            device=-1,  # CPU-only on the ZeroGPU Space
            truncation=True,
            max_length=512,
        )
    except Exception as exc:  # noqa: BLE001 - degraded mode is by design
        _LOAD_ERROR = exc
        return None
    return _PIPELINE


def classify(text):
    """Classify one sentence. Returns a dict, or None if the detector is out.

    The returned dict never carries a parse error: a missing/inert detector is
    indistinguishable from "no detection channel" at the caller.
    """
    pipe = load_detector()
    if pipe is None:
        return None
    try:
        out = pipe(text)[0]
        label = out['label']
        score = float(out['score'])
        acceptable = label in _ACCEPTABLE_LABELS
        acceptable_prob = score if acceptable else 1.0 - score
        return {
            'available': True,
            'model': _MODEL_ID,
            'label': 'acceptable' if acceptable else 'unacceptable',
            'acceptable': acceptable,
            'acceptable_prob': round(acceptable_prob, 4),
            'confidence': round(max(score, 1.0 - score), 4),
            'explanation': (f"Acceptability model ({_MODEL_ID}) rates the sentence "
                            f"{'acceptable' if acceptable else 'unacceptable'} "
                            f"(p(acceptable)={acceptable_prob:.2f})."),
        }
    except Exception:  # noqa: BLE001 - inert by design
        return None


def combine(summary, det):
    """Merge the rules verdict with the detection channel (never mutates)."""
    if det is None:
        return summary
    merged = dict(summary)
    merged['detector'] = det
    merged['flagged'] = False
    if merged.get('verdict') == 'ungrammatical':
        # The matrix explains the rejection; report the model's view alongside.
        merged['flagged'] = True
        merged['detector_note'] = det['explanation']
        return merged
    if not det['acceptable']:
        # Rules clean/unverified but the model says no - rules can't explain it.
        merged['flagged'] = True
        merged['verdict'] = 'unverified'
        merged['detector_note'] = (
            f"{det['explanation']} The rule matrix found no violation, so the "
            'deterministic rules cannot explain this rejection; the sentence is '
            'kept UNVERIFIED (not condemned) rather than labeled ungrammatical '
            'without a rule-level reason.')
    else:
        merged['detector_note'] = det['explanation']
        if merged.get('verdict') == 'grammatical':
            merged['verdict'] = 'grammatical'
    return merged