#!/usr/bin/env python3
import json
import re
import os

ROOT = '/Users/angelo/Downloads/SynTutor'
MD = os.path.join(ROOT, 'docs', 'ALL_EXPLANATIONS_EXHAUSTIVE.md')
OUT = os.path.join(ROOT, 'web/content/exhaustive_rules.json')

with open(MD, encoding='utf-8') as f:
    content = f.read()

rules = {}
# Match rule blocks
pattern = r'### Rule (\d+\.\d+): ([^\n]+)\n\n\*\*Tree-Structure Explanation:\*\* (.+?)\n\n\*\*Usage Template:\*\* (.+?)(?=\n---|\n## |\Z)'
for m in re.finditer(pattern, content, re.S):
    rid = m.group(1)
    name = m.group(2).strip()
    expl = m.group(3).strip()
    tmpl = m.group(4).strip()
    # clean
    expl = re.sub(r'\n+', ' ', expl)
    tmpl = re.sub(r'\n+', ' ', tmpl)
    rules[rid] = {'name': name, 'explanation': expl, 'template': tmpl}

# Also get category
cat = None
for line in content.splitlines():
    if line.startswith('## ') and re.match(r'## \d+\.', line):
        cat = line.strip()
        continue
    if line.startswith('### Rule '):
        m = re.match(r'### Rule (\d+\.\d+):', line)
        if m and m.group(1) in rules:
            rules[m.group(1)]['category'] = cat

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rules, f, indent=2)

print(f'Saved {len(rules)} rules')
