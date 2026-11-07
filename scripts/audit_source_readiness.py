"""Report source approvals needed before publishing source-grounded lessons.

Read-only: extraction approval never becomes independent review by running this.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))
from cambridge_registry import load_runtime_registry
from explanations import load_registry, _eligible_source, _reviewed


def readiness():
    registry = load_runtime_registry()
    templates = load_registry()
    sources = {source['id']: source for source in templates.get('sources', []) if _eligible_source(source)}
    reviewed = [template for template in templates.get('templates', [])
                if _reviewed(template) and template.get('source_ids')
                and all(source_id in sources for source_id in template['source_ids'])]
    pending = []
    for path in sorted((ROOT / 'grammar/rules').glob('*.json')):
        data = json.loads(path.read_text())
        for rule in data if isinstance(data, list) else data.get('rules', []):
            unresolved = [mapping for mapping in rule.get('burton_roberts_mapping', [])
                          if mapping.get('relation') in {'unverified', 'conflict', 'incompatible'}]
            pending.append({'rule_id': rule.get('id'), 'rule_type': rule.get('rule_type'),
                            'record': str(path.relative_to(ROOT)),
                            'runtime_enabled': rule.get('id') in registry.get('active_rule_ids', []),
                            'unresolved_crosswalks': len(unresolved),
                            'exact_editions_present': bool(rule.get('sources')) and all(
                                source.get('edition') for source in rule.get('sources', []))})
    manifest_path = ROOT / 'sources/cambridge/source_manifest_2026-11-08.json'
    cambridge_basis = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    br_path = ROOT / 'sources/burton_roberts/source_manifest_2026-11-08.json'
    br_basis = json.loads(br_path.read_text()) if br_path.exists() else {}
    structural = [template for template in reviewed if template.get('channel') == 'structural'
                  and all(sources[ident]['book'] == 'B-R' for ident in template['source_ids'])]
    cambridge = [template for template in reviewed if template.get('channel') == 'grammatical'
                 and all(sources[ident]['book'] == 'Cambridge' for ident in template['source_ids'])]
    ready = bool(structural) and bool(cambridge) and bool(br_basis) and bool(cambridge_basis)
    return {'readiness_scope': 'Instructional source prerequisites for M4; not completion of lessons or runtime constraint coverage',
            'br_bibliographic_identity': {key: br_basis.get(key) for key in ['book', 'edition', 'copyright_year', 'isbn13']},
            'cambridge_bibliographic_identity': {key: cambridge_basis.get(key) for key in ['book', 'edition', 'isbn13', 'publisher_frontmatter_url']},
            'milestone_04_content_ready': ready,
            'runtime_constraint_coverage_ready': bool(registry.get('active_rules')),
            'reviewed_structural_template_count': len(structural),
            'reviewed_cambridge_template_count': len(cambridge),
            'runtime_enabled_rule_count': len(registry.get('active_rules', [])),
            'reviewed_template_count': len(reviewed),
            'source_rule_count': len(pending), 'rules': pending,
            'required_external_evidence': [] if ready else ['Verified bibliography and reviewed starter templates from both B-R and Cambridge are required.'],
            'publication_follow_up': [
                'Review each lesson, worked example and additional template before publishing it in M4.',
                'Enable grammaticality constraints only after source, scope, variety, exception and rule-specific test gates pass.',
                'No production Cambridge runtime constraint is currently enabled; teaching notes do not determine a full grammaticality verdict.',
            ]}



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-ready', action='store_true')
    args = parser.parse_args()
    result = readiness()
    print(json.dumps(result, indent=2))
    if args.require_ready and not result['milestone_04_content_ready']:
        raise SystemExit(1)
