"""Install model data into the Vercel function's build directory."""

from pathlib import Path

import benepar
from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[1] / 'vercel_models'

# Match the models used by detector.py and corrector.py.
MODELS = (
    ('textattack/roberta-base-CoLA', '3ccf3a400f2fa75ff257eac171047603ffbe84f1',
     'pytorch_model.bin'),
    ('distilbert-base-uncased', '12040accade4e8a0f71eabdb258fecc2e7e948be',
     'model.safetensors'),
)


def main():
    nltk_dir = ROOT / 'nltk'
    nltk_dir.mkdir(parents=True, exist_ok=True)
    benepar.download('benepar_en3', download_dir=str(nltk_dir), raise_on_error=True)
    (nltk_dir / 'models/benepar_en3.zip').unlink(missing_ok=True)

    for repo, revision, weights in MODELS:
        # Transformers' offline lookup needs the model's main ref as well as
        # the snapshot. Store resolved files so deployment doesn't rely on symlinks.
        cache_name = f"models--{repo.replace('/', '--')}"
        cache_dir = ROOT / 'hub' / cache_name
        snapshot_download(
            repo,
            revision=revision,
            local_dir=cache_dir / 'snapshots' / revision,
            allow_patterns=['*.json', '*.txt', weights],
        )
        refs = cache_dir / 'refs'
        refs.mkdir(parents=True, exist_ok=True)
        (refs / 'main').write_text(revision, encoding='utf-8')


if __name__ == '__main__':
    main()
