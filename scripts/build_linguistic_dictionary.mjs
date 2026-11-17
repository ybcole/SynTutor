import fs from 'node:fs';
const md=fs.readFileSync('docs/LINGUISTIC_DICTIONARY.md','utf8');
const entries=[];
const row=/^\| \*\*(.+?)\*\* \| (.+?) \| (.*?) \| (.*?) \|$/gm;
let m;
const unescape=s=>s.replace(/\\\|/g,'|').trim();
while((m=row.exec(md))){
 const term=unescape(m[1]);
 const definition=unescape(m[2]);
 const aliases=unescape(m[3]).split(',').map(s=>s.trim()).filter(Boolean);
 entries.push({term,definition,aliases});
}
if(entries.length<600) throw new Error(`Only parsed ${entries.length} dictionary entries`);
const body=entries.map(e=>`  ${JSON.stringify(e)},`).join('\n');
const out=`// Generated from docs/LINGUISTIC_DICTIONARY.md. Do not edit by hand.\nexport const linguisticDictionary = [\n${body}\n];\n`;
fs.writeFileSync('web/js/linguistic-dictionary.js',out);
console.log('wrote',entries.length,'entries');
