"""Check the structural schema and source anchors for the combined local candidate."""
import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / 'web/content/lessons'
course = json.loads(subprocess.check_output(
    ['node', 'scripts/compose_foundations_preview.js'], cwd=ROOT))
Draft202012Validator(json.loads((LESSONS / 'course.schema.json').read_text())).validate(course)
published = json.loads((LESSONS / 'course.json').read_text())
sources = {source['id']: source for source in course['sources']}
assert len(sources) == len(course['sources'])
manifest = json.loads((ROOT / 'sources/burton_roberts/source_manifest_2026-11-08.json').read_text())
by_chapter = {entry['chapter']: entry for entry in manifest['files']}

assert course['tracks'] == published['tracks']
assert course['planned_modules'] == published['planned_modules']
assert [lesson for lesson in course['lessons'] if lesson['track'] != 'foundations'] == [
    lesson for lesson in published['lessons'] if lesson['track'] != 'foundations']
revised = [lesson for lesson in course['lessons'] if lesson.get('revised_assessment')]
assert [lesson['lesson_id'] for lesson in revised] == [f'br-{n:02}' for n in range(1, 12)]
for lesson in revised:
    assert lesson['content_version'] == '2.0.0'
    for kind in ('opening', 'closing'):
        questions = lesson['revised_assessment'][kind]
        assert len(questions) == 5, (lesson['lesson_id'], kind)
        for question in questions:
            for id in question['source_ids']:
                source = sources[id]
                chapter = lesson['chapter']
                pages = by_chapter[chapter]
                assert source['book'] == 'B-R' and source['chapter'] == chapter, question['id']
                assert pages['printed_start'] <= source['printed_page'] <= pages['printed_end'], id

print('PASS: combined course schema, 110 assessment items and in-chapter anchors, and unchanged Cambridge catalog.')
