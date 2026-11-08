"""Palette mirrors the existing approved validator; no new linguistic rules."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'server'))
from burton_roberts import _LABEL_INTRODUCED,_FEATURE_INTRODUCED
from tree_evaluation import evaluate_request
raw=(ROOT/'web/js/builder-inventory.js').read_text().split('export default ',1)[1].rstrip().removesuffix(';')
assert json.loads(raw)=={'labels':_LABEL_INTRODUCED,'features':_FEATURE_INTRODUCED}
course=json.loads((ROOT/'web/content/lessons/course.json').read_text())
count=0
for lesson in course['lessons']:
 tree=lesson['worked_example'].get('tree')
 if not tree or lesson['lesson_id']=='br-01':continue
 result=evaluate_request({'tree':tree,'target_lesson_id':lesson['lesson_id']})
 assert result['structure']['status']=='well_formed'
 assert result['target_comparison']['matched']
 assert result['grammaticality']['status']=='unresolved' # No production constraint silently enabled.
 count+=1
assert count==9
print('PASS: canonical validator/palette parity, nine reviewed construction targets, explicit unresolved grammaticality and unchanged source scope.')
