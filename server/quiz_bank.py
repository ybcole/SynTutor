"""Repository-owned quiz feedback, not an XP authority or parser judgement."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_quiz_bank():
    return json.loads((ROOT/'web/content/quizzes/bank.json').read_text())

def explain_quiz_request(data):
    if set(data)-{'quiz_item_id','quiz_item_version','answer_id'}:
        raise ValueError('Only quiz item ID/version and answer ID are accepted')
    ident,version=data.get('quiz_item_id'),data.get('quiz_item_version')
    if not isinstance(ident,str) or not ident or len(ident)>160 or not isinstance(version,str) or len(version)>30:
        raise ValueError('A bounded quiz item ID and version are required')
    bank=load_quiz_bank()
    matches=[q for q in bank.get('items',[]) if q.get('item_id')==ident and q.get('content_version')==version]
    if len(matches)!=1:raise ValueError('Unknown quiz item version')
    from explanations import explain_quiz_response
    return explain_quiz_response(matches[0],data.get('answer_id'),bank.get('sources',[]))
