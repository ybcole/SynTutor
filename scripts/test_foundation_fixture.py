"""Temporary course variant for tests. The published course is never overwritten."""
import json
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1] / 'web/content/lessons/course.json'


def fixture_course():
    course = json.loads(COURSE.read_text())
    lesson = next(lesson for lesson in course['lessons'] if lesson['lesson_id'] == 'br-02')
    lesson['content_version'] = '2.0.0'
    assessment = {'required_sections': ['introduction', 'concepts', 'worked-example', 'application', 'recap']}
    for kind, count in [('opening', 5), ('closing', 6)]:
        assessment[kind] = [
            {
                'id': f'{kind}-{i}',
                'prompt': f'{kind.title()} fixture question {i + 1}',
                'options': [
                    {'id': 'a', 'text': 'Fixture option A', 'feedback': 'Explanation for option A.'},
                    {'id': 'b', 'text': 'Fixture option B', 'feedback': 'Explanation for option B.'},
                ],
                'answer': 'a',
                'source_ids': lesson['source_ids'],
                'outcome_ids': [o['id'] for o in lesson['outcomes']],
            }
            for i in range(count)
        ]
    lesson['revised_assessment'] = assessment
    return course


if __name__ == '__main__':
    print(json.dumps(fixture_course()))
