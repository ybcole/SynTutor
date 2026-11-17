import fs from 'node:fs';
import { foundationsGlossary } from '../web/js/foundations-glossary.js';
import { lessonKeyTerms } from '../web/js/lesson-key-terms.js';
const course=JSON.parse(fs.readFileSync(new URL('../web/content/lessons/course.json',import.meta.url),'utf8'));
const md=fs.readFileSync(new URL('../docs/LINGUISTIC_DICTIONARY.md',import.meta.url),'utf8');
const known=new Set();
const row=/^\| \*\*(.+?)\*\* \| (.+?) \| (.*?) \| (.*?) \|$/gm;let m;
while((m=row.exec(md))){
 known.add(m[1].replace(/\\\|/g,'|').trim().toLowerCase());
 for(const a of m[3].replace(/\\\|/g,'|').split(',')) if(a.trim()) known.add(a.trim().toLowerCase());
}
const missing=new Set();
for(const [chapter,section,entries] of foundationsGlossary){for(const [title,,aliases] of entries){ if(!known.has(title.toLowerCase())) missing.add(title); for(const a of (aliases||'').split('|')) if(a.trim()&&!known.has(a.trim().toLowerCase())) missing.add(a.trim()); }}
for(const entries of Object.values(lessonKeyTerms)) for(const [title] of entries) if(!known.has(title.toLowerCase())) missing.add(title);
for(const l of course.lessons) for(const kt of (l.key_terms||[])) if(!known.has(kt.term.toLowerCase())) missing.add(kt.term);
if(missing.size){console.error('Missing dictionary entries/aliases:',[...missing].sort().join(', '));process.exit(1);}
console.log(`PASS: all ${known.size} names/aliases in the runtime lesson dictionaries are covered by docs/LINGUISTIC_DICTIONARY.md`);
