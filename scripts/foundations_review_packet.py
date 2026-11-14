"""Print an internal answer and source review packet for the combined pilot."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    course = json.loads(subprocess.check_output(
        ['node', 'scripts/compose_foundations_preview.js'], cwd=ROOT))
    sources = {source['id']: source for source in course['sources']}
    print('# Syntax Foundations assessment review\n')
    print('Internal reviewer copy. Compare each item and its feedback with the cited edition.\n')
    for lesson in course['lessons']:
        assessment = lesson.get('revised_assessment')
        if not assessment:
            continue
        chapter = lesson['chapter']
        print(f"## Chapter {chapter} · {lesson['title']} · {lesson['content_version']}\n")
        review = f'docs/reports/syntax-foundations-chapter-{chapter}-pilot.md'
        print(f'Chapter walkthrough and source notes are in `{review}`.\n')
        for outcome in lesson['outcomes']:
            print(f"- **{outcome['id']}** {outcome['text']}")
        for kind in ('opening', 'closing'):
            print(f'\n### {kind.capitalize()} check\n')
            for question in assessment[kind]:
                pages = ', '.join(str(sources[id]['printed_page']) for id in question['source_ids'])
                outcomes = ', '.join(question['outcome_ids'])
                print(f"**{question['id']}** · Printed pp. {pages} · {outcomes}\n")
                print(f"{question['prompt']}\n")
                for option in question['options']:
                    marker = ' **Expected answer**' if option['id'] == question['answer'] else ''
                    print(f"- {option['id']}.{marker} {option['text']} — {option['feedback']}")
                print()


if __name__ == '__main__':
    main()
