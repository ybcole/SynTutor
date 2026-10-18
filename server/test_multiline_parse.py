"""Regression check for Benepar parsing of newline-delimited text."""

from parse_engine import analyze
from matrix import evaluate


def main():
    lines = [
        'The garden club opened its greenhouse.',
        'Students carried several boxs near the wall.',
        'They watered the beds before lunch.',
        'The flowers looked healthy by afternoon.',
    ]
    for separator in ('\n', '\r\n'):
        text = separator.join(lines)
        analysis = analyze(text, sentence_index=1)
        assert analysis['sentence_count'] == 4
        assert analysis['sentence'] == lines[1]
        for sentence in analysis['sentences']:
            assert text[sentence['start']:sentence['end']] == sentence['text']
        summary = evaluate(analysis['root'], text=analysis['sentence'])['summary']
        assert summary['verdict'] == 'ungrammatical'
    print('Multiline parser regression passed (LF/CRLF paragraphs, offsets, and second-sentence error).')


if __name__ == '__main__':
    main()
