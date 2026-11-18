// Source-grounded retrieval practice, NOT independent review or published XP.
// Every item is tied to one actual instructional section. Nothing is padded by
// cloning a prompt, verb-splitting incomplete sentences, or keeping leaky distractors.
import {cambridgeChapterData} from './cambridge-chapter-data.js?v=2026.11.16c';
import {practiceExamples} from './quiz-practice-examples.js';
import {pilotArticles} from './lesson-curriculum.js';

const clean = text => String(text).replace(/\*/g,'').replace(/\s+/g,' ').trim();
const hash = text => {
  let n=2166136261;
  for(const char of text){n^=char.charCodeAt(0);n=Math.imul(n,16777619);}
  return (n>>>0).toString(16).padStart(8,'0');
};
export const syntaxPracticeDigest = id => {
  const article=pilotArticles[id];
  return article?hash(JSON.stringify({teach:String(article.teach),sections:article.sections,keyTerms:article.keyTerms,description:article.description})):null;
};
const unique = values => [...new Set(values.map(clean).filter(Boolean))];
const wordsOf = text => [...new Set(clean(text).toLowerCase().replace(/[^a-z0-9’'\s-]/g,' ').split(/\s+/).filter(w=>w.length>=2))];

// Grammatical metalanguage and closed-class scaffolding words allowed across options.
const grammarMeta = new Set([
  'the','a','an','and','or','but','not','no','nor','of','in','on','at','to','by','for','from','with','as','into','onto','than','that','this','these','those',
  'is','are','was','were','be','been','being','has','have','had','do','does','did','can','could','may','might','must','shall','should','will','would',
  'it','its','he','she','they','them','his','her','their','you','your','we','our','who','whom','whose','which','what','where','when','why','how',
  'one','two','only','both','all','each','some','any','more','most','same','other','own','such','very',
  'clause','clauses','sentence','sentences','phrase','phrases','word','words','noun','nouns','verb','verbs','adjective','adjectives','adverb','adverbs',
  'preposition','prepositions','determiner','determiners','pronoun','pronouns','auxiliary','auxiliaries','complement','complements','object','objects',
  'subject','subjects','adjunct','adjuncts','modifier','modifiers','head','heads','predicate','predicative','gap','finite','non-finite','infinitival',
  'bare','relative','content','comparative','declarative','interrogative','imperative','exclamative','active','passive','positive','negative','singular',
  'plural','tense','present','past','preterite','participle','form','forms','function','category','use','uses','meaning','direct','indirect','core',
  'non-core','simple','complex','open','closed','main','subordinate','matrix','embedded','fronted','preposed','postposed','extraposed','dummy',
  'marked','marker','coordination','coordinated','appositive','supplement','nominal','genitive','accusative','nominative','plain','modal','perfect',
  'progressive','aspect','modality','mood','negation','polarity','deictic','anaphoric','reflexive','reciprocal','quantifier','numeral','compound',
  'suffix','prefix','base','stem','regular','irregular','standard','informal','formal','style','register','speech','writing','spoken','written',
  'stress','intonation','punctuation','comma','commas','apostrophe','slash','hyphen','spelling','example','pattern','construction','role','position',
  'structure','order','reading','sense','scope','reference','referent','antecedent','licensor','elided','ellipsis','omitted','optional','obligatory',
]);

// Comparison-matrix columns that compare parallel slots rather than naming a distinct classification target.
const matrixTargetBlacklist = /^(take|want|hit|auxiliary|lexical verb|direct object|indirect object|predicative complement|object|canonical|non-canonical|positive clause|negative clause|positive context|negative context|equality|inequality|first member|second member|first type|second type)$/i;

export function formatTablePrompt(title, columnName, context) {
  const col = clean(columnName);
  const lower = col.toLowerCase().replace(/\bnp\b/g, 'NP');
  if (/^what changes$/i.test(col)) return `In “${title}”, given ${context}, what changes?`;
  if (/^what it shows$/i.test(col)) return `In “${title}”, given ${context}, what does this example show?`;
  if (/^what happens$/i.test(col)) return `In “${title}”, given ${context}, what happens?`;
  if (/^what it does$/i.test(col)) return `In “${title}”, given ${context}, what does this construction do?`;
  if (/^why included$/i.test(col)) return `In “${title}”, given ${context}, why is it included?`;
  if (/^anchored to$/i.test(col)) return `In “${title}”, given ${context}, what is it anchored to?`;
  if (/^temporal$/i.test(col)) return `In “${title}”, given ${context}, which temporal value applies?`;
  if (/^tensed$/i.test(col)) return `In “${title}”, given ${context}, which tensed-verb pattern applies?`;
  return `In “${title}”, select the ${lower} matching ${context}.`;
}

function validExampleChoices(example, examples, blockLex) {
  if (example.mark && example.mark !== 'ok') return null;
  const ownText = clean(example.text).toLowerCase();
  const ownWords = new Set(wordsOf(example.text).filter(w => !grammarMeta.has(w)));
  const ans = clean(example.note);
  const ansWords = wordsOf(ans).filter(w => !grammarMeta.has(w));
  const selfLeak = ansWords.some(w =>
    ownWords.has(w) && examples.some(o => clean(o.note) !== ans && !clean(o.text).toLowerCase().includes(w))
  );
  if (selfLeak) return null;

  const others = [];
  for (const other of examples) {
    const otherNote = clean(other.note);
    if (!otherNote || otherNote === ans || others.includes(otherNote)) continue;
    const otherTextLower = clean(other.text).toLowerCase();
    const otherWords = wordsOf(otherNote).filter(w => !grammarMeta.has(w));
    const foreign = otherWords.some(w => (blockLex.has(w) || otherTextLower.includes(w)) && !ownWords.has(w) && !ownText.includes(w));
    if (foreign) continue;
    const foreignCitation = [...String(other.note).matchAll(/\*([^*]+)\*|“([^”]+)”/g)].some(m => {
      const phrase = clean(m[1] || m[2]).toLowerCase();
      return phrase && !ownText.includes(phrase) && otherTextLower.includes(phrase);
    });
    if (foreignCitation) continue;
    const initCap = /^([A-Z][a-z’'-]+)\s+(?:is|are|marks|shows|takes|follows|precedes|refers|means|acts|functions|serves|heads)\b/.exec(otherNote);
    if (initCap) {
      const tok = initCap[1].toLowerCase();
      if (!grammarMeta.has(tok) && wordsOf(other.text).includes(tok) && !wordsOf(example.text).includes(tok)) continue;
    }
    const initPhrase = /^([A-Z][a-z’'-]+\s+[a-z’'-]+)\s+(?:is|are|marks|shows|takes|follows|precedes|refers|means|acts|functions|serves|heads)\b/.exec(otherNote);
    if (initPhrase) {
      const phrase = initPhrase[1].toLowerCase();
      if (otherTextLower.includes(phrase) && !ownText.includes(phrase)) continue;
    }
    others.push(otherNote);
  }
  return others.length >= 2 ? others.slice(0, 2) : null;
}

function sectionQuestions(section){
  const questions=(practiceExamples[`${section.lesson_id}/${section.id}`]||[]).map(([prompt,answer,first,second,evidence],index)=>({
    family:`original-application-${index}`,kind:'rule_application',prompt,answer,others:[first,second],evidence,original:true,
  })),blocks=section.blocks||[];
  for(const [blockIndex,block] of blocks.entries()){
    if(block.type==='table'&&block.columns?.length>=2&&block.rows?.length>=3){
      if(block.columns.some(c=>!clean(c)))continue;
      const rows=block.rows.filter(r=>r.length===block.columns.length&&r.every(c=>typeof c==='string'&&clean(c)));
      const target=[...block.columns.keys()].reverse().find(i=>!matrixTargetBlacklist.test(clean(block.columns[i]))&&unique(rows.map(r=>r[i])).length>=3);
      if(target===undefined)continue;
      for(const [rowIndex,row] of rows.entries()){
        const answer=clean(row[target]);
        if(/^examples?$/i.test(clean(block.columns[target]))&&/^[A-Z][a-z’'-]+$/.test(answer))continue;
        const ctxCells=row.filter((_,i)=>i!==target).map(clean);
        if(ctxCells.some(c=>c.toLowerCase()===answer.toLowerCase()))continue;
        if(rows.some((other,j)=>j!==rowIndex&&other.every((v,i)=>i===target||clean(v)===clean(row[i]))&&clean(other[target])!==answer))continue;
        const ctxWords=new Set(ctxCells.flatMap(c=>wordsOf(c)).filter(w=>!grammarMeta.has(w)));
        const ctxLower=ctxCells.join(' ').toLowerCase();
        const ansWords=wordsOf(answer).filter(w=>!grammarMeta.has(w));
        const validOthers=[];
        for(const otherRow of rows){
          const d=clean(otherRow[target]);
          if(!d||d===answer||validOthers.includes(d))continue;
          const dWords=wordsOf(d).filter(w=>!grammarMeta.has(w));
          const oCtxCells=otherRow.filter((_,i)=>i!==target).map(clean);
          const oCtxWords=new Set(oCtxCells.flatMap(c=>wordsOf(c)).filter(w=>!grammarMeta.has(w)));
          const oCtxLower=oCtxCells.join(' ').toLowerCase();
          if(dWords.some(w=>(oCtxWords.has(w)||oCtxLower.includes(w))&&!ctxWords.has(w)&&!ctxLower.includes(w)))continue;
          validOthers.push(d);
        }
        const others=validOthers.slice(0,2);
        if(others.length<2)continue;
        if(ansWords.some(w=>(ctxWords.has(w)||ctxLower.includes(w))&&others.some(d=>!wordsOf(d).includes(w))))continue;
        const context=row.map((value,i)=>i===target?null:`${block.columns[i]}: “${clean(value)}”`).filter(Boolean).join('; ');
        questions.push({family:`table-${blockIndex}-${rowIndex}`,kind:'lesson_match',
          prompt:formatTablePrompt(block.title||section.title,block.columns[target],context),
          answer,others,evidence:`${context}; ${block.columns[target]}: ${answer}.`,
          examples:row.filter((value,i)=>/example|illustration|sentence|expression/i.test(block.columns[i]))});
      }
    }
    if(block.type==='examples'){
      const examples=(block.items||[]).filter(e=>e.text&&e.note);
      const blockLex=new Set(examples.flatMap(e=>wordsOf(e.text)).filter(w=>!grammarMeta.has(w)));
      for(const [index,example] of examples.entries()){
        const others=validExampleChoices(example,examples,blockLex);
        if(!others)continue;
        const answer=clean(example.note);
        questions.push({family:`example-${blockIndex}-${index}`,kind:'lesson_match',
          prompt:`In “${section.title}”, which explanation is paired with “${clean(example.text)}”?`,
          answer,others,evidence:`The section pairs “${clean(example.text)}” with this explanation: ${answer}`,examples:[clean(example.text)]});
      }
    }
  }
  // A real application section with little expository prose: distinct original
  // inputs test recursive coordination, not five rewordings of one question.
  if(section.lesson_id==='br-11'&&section.id==='apply-the-rule'){
    const examples=[
      ['Rae sings.','Vic reads.','Rae sings and Vic reads.'],
      ['The kettle boiled.','The lights flickered.','The kettle boiled and the lights flickered.'],
      ['Inez waited.','The bus arrived.','Inez waited and the bus arrived.'],
      ['The dog barked.','The gate opened.','The dog barked and the gate opened.'],
      ['Mina drew a map.','Jo checked the route.','Mina drew a map and Jo checked the route.'],
      ['The rain stopped.','The children went outside.','The rain stopped and the children went outside.'],
    ];
    for(const [index,[first,second,answer]] of examples.entries())questions.push({
      family:`coordination-${index}`,kind:'rule_application',original:true,
      prompt:`Apply the sentence-coordination rule to these two complete inputs: “${first}” and “${second}”. Which result preserves both clauses?`,
      answer,others:[`${first.slice(0,-1)} and.`,`${first.slice(0,-1)} and ${second.split(' ')[0]}.`],
      evidence:`Both ${first.slice(0,-1)} and ${second.slice(0,-1)} are complete clauses. Joining them with “and” gives ${answer} The complete result can be coordinated with a further complete clause.`,
    });
  }
  // A maximum prevents a long section from dominating personalized practice.
  return questions.slice(0,12);
}

export function findStaleSyntaxSources(curriculum, syntaxSource) {
  const stale = [];
  const syntaxTrack = curriculum.find(t => t.id === 'syntax');
  if (!syntaxTrack) return stale;
  for (const chapter of syntaxTrack.chapters) {
    const expectedDigest = syntaxPracticeDigest(chapter.id);
    for (const topic of chapter.topics) {
      const source = syntaxSource?.sections?.find(s => s.lesson_id === chapter.id && s.subtopic_id === topic.id);
      if (!source) stale.push({ chapter_id: chapter.id, subtopic_id: topic.id, reason: 'missing_section' });
      else if (source.lesson_version !== chapter.content_version) stale.push({ chapter_id: chapter.id, subtopic_id: topic.id, reason: 'version_mismatch' });
      else if (source.article_digest !== expectedDigest) stale.push({ chapter_id: chapter.id, subtopic_id: topic.id, reason: 'digest_mismatch' });
    }
  }
  return stale;
}

export function validateSyntaxPracticeSource(curriculum, syntaxSource) {
  const stale = findStaleSyntaxSources(curriculum, syntaxSource);
  if (!stale.length) return syntaxSource;
  const chapters = [...new Set(stale.map(s => s.chapter_id))].join(', ');
  throw Error(`Stale syntax practice source for ${chapters}: lesson version or article digest changed. Run scripts/build_quiz_practice.js to regenerate.`);
}

export function makeLessonPractice(curriculum, syntaxSource, options = {}){
  const items=[],ids=new Set(),staleTopics=syntaxSource?findStaleSyntaxSources(curriculum,syntaxSource):[];
  const staleSet=new Set(staleTopics.map(s=>`${s.chapter_id}/${s.subtopic_id}`));
  if(staleTopics.length){
    if(typeof options.onStale==='function')options.onStale(staleTopics);
    else if(options.allowStale!==true)validateSyntaxPracticeSource(curriculum,syntaxSource);
  }
  if(!syntaxSource&&options.allowMissingSyntax!==true&&typeof options.onStale!=='function'){
    throw Error('Syntax practice source is unavailable.');
  }
  for(const track of curriculum)for(const chapter of track.chapters)for(const topic of chapter.topics){
    if(track.id==='syntax'&&(!syntaxSource||staleSet.has(`${chapter.id}/${topic.id}`)))continue;
    const source=track.id==='syntax'
      ? syntaxSource?.sections?.find(s=>s.lesson_id===chapter.id&&s.subtopic_id===topic.id)
      : cambridgeChapterData[chapter.id]?.sections.find(s=>s.id===topic.id);
    if(!source)continue;
    const section={...source,lesson_id:chapter.id,id:topic.id,title:topic.title};
    const markedExamples=(section.blocks||[]).flatMap(b=>[...String(b.text||'').matchAll(/\*([^*]+)\*/g)].map(m=>clean(m[1])))
      .filter(text=>text.includes(' '));
    const titles=new Set([section.title,...(section.blocks||[]).map(b=>b.title).filter(Boolean)]);
    for(const question of sectionQuestions(section)){
      const options=[question.answer,...question.others].map((text,i)=>({
        id:String.fromCharCode(97+i),text,
        rationale:i===0?question.evidence:`This is not the completion or pairing recorded for this prompt. The lesson states: ${question.evidence}`,
      }));
      const digest=hash(JSON.stringify([question.prompt,options,question.evidence]));
      const item_id=`lesson-practice:${chapter.id}:${topic.id}:${question.family}:${digest}`;
      if(ids.has(item_id))throw Error('Duplicate lesson practice question.');
      ids.add(item_id);
      items.push({item_id,pool_id:`lesson-practice:${chapter.id}:${topic.id}`,content_version:'lesson-practice-1.0.0',
        track_id:track.id,chapter_id:chapter.id,subtopic_id:topic.id,lesson_id:chapter.id,
        concept_ids:[`${chapter.id}:${topic.id}`],outcome_ids:chapter.outcomes?.map(o=>o.id)||[],
        lesson_reference:`#lesson/${chapter.id}/${topic.id}`,
        source_metadata:{kind:'syntutor_lesson_section',section_id:topic.id,
          artifact:track.id==='syntax'?'content/quizzes/syntax-practice-source.json':'js/cambridge-chapter-data.js',
          excerpt:question.evidence,derivation:question.original?'original_application':'lesson_retrieval',content_digest:digest},
        publication_status:'practice',review_status:'UNREVIEWED',independent_review:false,
        kind:question.kind,prompt:question.prompt,options,answer:'a',rationale:question.evidence,
        practice_family:`${chapter.id}:${topic.id}:${question.family}`,
        practice_example_ids:unique([
          ...(question.examples||[]),
          ...(question.kind==='lesson_match'?[]:[...`${question.prompt} ${question.evidence}`.matchAll(/“([^”]+)”/g)].map(m=>m[1]).filter(t=>t.includes(' ')&&!titles.has(t))),
          ...markedExamples.filter(text=>question.evidence.includes(text)),
        ]).map(text=>`${track.id}:${hash(clean(text).toLowerCase().replace(/[.!?]+$/,''))}`),
      });
    }
  }
  return items;
}
export function validateLessonPractice(items,curriculum){
  const ids=new Set(),prompts=new Set();
  for(const q of items){
    const chapter=curriculum.find(t=>t.id===q.track_id)?.chapters.find(c=>c.id===q.chapter_id);
    const promptKey=`${q.chapter_id}/${q.subtopic_id}/${q.prompt}`;
    if(!chapter?.topics.some(t=>t.id===q.subtopic_id)||ids.has(q.item_id)||prompts.has(promptKey)
      ||q.review_status!=='UNREVIEWED'||q.independent_review!==false||q.publication_status!=='practice'
      ||q.options.length<3||new Set(q.options.map(o=>o.text)).size!==q.options.length
      ||q.options.some(o=>/^[,;:.!?]/.test(o.text.trim()))
      ||!q.options.some(o=>o.id===q.answer)||!q.rationale||!q.source_metadata?.excerpt
      ||q.lesson_reference!==`#lesson/${q.chapter_id}/${q.subtopic_id}`)throw Error('Invalid lesson practice content.');
    ids.add(q.item_id);prompts.add(promptKey);
  }
  return items;
}
