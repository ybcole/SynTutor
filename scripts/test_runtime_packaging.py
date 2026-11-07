"""Verify the Docker COPY inputs can import and serve the shared evidence API.

This uses the declared local runtime file set, not a claimed Docker image build.
It requires the lightweight test dependencies, not NLP models.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='syntutor-runtime-package-') as directory:
    target = Path(directory)
    subprocess.run(['git', 'init', '-q', directory], check=True)
    (target / '.gitignore').write_bytes((ROOT / '.dockerignore').read_bytes())
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
    excluded = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin', '-z'],
                              input=paths, cwd=target, capture_output=True)
    if excluded.returncode not in (0, 1):
        raise RuntimeError(excluded.stderr.decode())
    ignored = set(excluded.stdout.decode().split('\0'))
    # Limit inputs to the actual COPY statements, so an accidental include-all
    # in the fixture cannot hide missing runtime files in the Dockerfile.
    copies = []
    for line in (ROOT / 'Dockerfile').read_text().splitlines():
        if line.startswith('COPY '):
            source, destination = line.split()[1:3]
            copies.append((source, destination))
    for source, destination in copies:
        original = ROOT / source
        names = [path for path in original.rglob('*') if path.is_file()] if original.is_dir() else [original]
        for path in names:
            relative = str(path.relative_to(ROOT))
            if relative in ignored:
                continue
            output = target / destination
            if original.is_dir():
                output /= path.relative_to(original)
            elif destination.endswith('/') or destination == './':
                output /= original.name
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, output)
    subprocess.run([sys.executable, '-c', '''
import sys
sys.path.insert(0, 'server')
from webapp import app
from explanations import load_registry
assert load_registry()['templates'], 'production source registry not packaged'
response = app.test_client().post('/api/explain', json={'tree': None})
assert response.status_code == 200
assert response.get_json()['status'] == 'ANALYSIS_UNRESOLVED'
print('PASS: Docker COPY/exclusion fixture imports backend and serves evidence API.')
'''], cwd=target, check=True)
