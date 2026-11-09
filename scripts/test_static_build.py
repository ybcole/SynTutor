"""Build using tracked files after applying the Vercel upload exclusions."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
with tempfile.TemporaryDirectory(prefix='syntutor-static-build-') as directory:
    target = Path(directory)
    subprocess.run(['git', 'init', '-q', directory], check=True)
    (target / '.gitignore').write_bytes((ROOT / '.vercelignore').read_bytes())
    excluded = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin', '-z'],
                              input=paths, cwd=target, capture_output=True, check=False)
    if excluded.returncode not in (0, 1):
        raise RuntimeError(excluded.stderr.decode())
    ignored = set(excluded.stdout.decode().split('\0'))
    for name in paths.decode().split('\0'):
        if not name or name in ignored or name == '.gitignore':
            continue
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, path)
    subprocess.run(['npm', 'run', 'build'], cwd=target, check=True)
    assert (target / 'dist/index.html').is_file()
    public_html = (target / 'dist/index.html').read_text()
    assert 'Cambridge runtime grammaticality rules are not yet enabled.' in public_html
    assert 'Builder drafts stay on this device.' in public_html
    assert 'At least 15 characters' in public_html
    assert (target / 'dist/js/explanation-evidence.js').is_file()
    assert (target / 'dist/content/quizzes/bank.json').is_file()
    assert (target / 'dist/js/quizzes-ui.js').is_file()
    assert (target / 'dist/css/quizzes.css').is_file()
    assert (target / 'dist/js/builder-tools.js').is_file()
    assert (target / 'dist/js/builder-inventory.js').is_file()
    assert (target / 'dist/css/builder-tools.css').is_file()
    assert not (target / 'dist/server').exists()
    assert not (target / 'server/api.py').exists()
    print('PASS: Vercel-filtered static build; backend stays outside public output.')
