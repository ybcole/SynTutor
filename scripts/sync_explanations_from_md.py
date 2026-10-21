#!/usr/bin/env python3
import json
import re
import os

ROOT = '/Users/angelo/Downloads/SynTutor'
MD = os.path.join(ROOT, 'docs', 'ALL_EXPLANATIONS_EXHAUSTIVE.md')
TREE_SHEET = os.path.join(ROOT, 'web/content/tree_sheet.json')

# Parse rules from MD
with open(MD, encoding='utf-8') as f:
    content = f.read()

rules = {}
# Match "### Rule X.Y: Name" followed by explanation and template
pattern = r'### Rule (\d+\.\d+): ([^\n]+)\n\n\*\*Tree-Structure Explanation:\*\* ([^\n]+(?:\n(?!\*\*|\#|---)[^\n]+)*)\n\n\*\*Usage Template:\*\* ([^\n]+(?:\n(?!\*\*|\#|---)[^\n]+)*)'
for m in re.finditer(pattern, content, re.S):
    rid = m.group(1)
    name = m.group(2).strip()
    expl = m.group(3).strip().replace('\n', ' ')
    tmpl = m.group(4).strip().replace('\n', ' ')
    rules[rid] = {'name': name, 'explanation': expl, 'template': tmpl}

print(f'Parsed {len(rules)} rules')

# Update tree_sheet.json
ts = json.load(open(TREE_SHEET))
st4 = [s for s in ts['stages'] if s['id']==4][0]
updated = 0
for it in st4['items']:
    if it.get('rule') in rules:
        r = rules[it['rule']]
        # Update concept with tree explanation
        it['concept'] = r['explanation']
        # Also update name if needed
        updated += 1

ts['exhaustive_explanations'] = rules
ts['synced_from'] = MD

with open(TREE_SHEET, 'w', encoding='utf-8') as f:
    json.dump(ts, f, indent=2)

print(f'Updated {updated} items in tree_sheet')
