// Source-grounded retrieval practice, NOT independent review or published XP.
// Every item is tied to one actual instructional section. Nothing is padded by
// cloning a prompt or changing names in an already-missed question.
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
const segmenter = new Intl.Segmenter('en',{granularity:'sentence'});
const uiInstruction = /^(click|tap|select|choose|pick|try|trace|scroll|use the button|open the|look at the tree|find the button|inspect the|check your|your answer|read the brackets)/i;
function sentenceFacts(texts){
  const seen=new Set(),facts=[];
  for(const text of unique(texts))for(const {segment} of segmenter.segment(text)){
    const sentence=clean(segment);
    if(sentence.length<65||sentence.length>450||!/[.!?]$/.test(sentence)||uiInstruction.test(sentence)||/^(SNP|NP —|VPV|S″|S′)/.test(sentence))continue;
    // Complete a meaningful predicate rather than guessing a random missing
    // word. The task explicitly asks for this section's wording, not a claim
    // that every alternative is ungrammatical in every possible context.
    const boundary=/\b(?:is|are|means|marks|labels|contains|takes|take|uses|use|heads|head|describes|describe|expresses|requires|allows|can|does|do|has|have|gives|give|shows|show|lets|let|makes|make)\b/gi;
    const matches=[...sentence.matchAll(boundary)];
    const match=matches.find(m=>{
      if(m.index<10||m.index>sentence.length-24)return false;
      const prefix=sentence.slice(0,m.index);
      return (prefix.match(/“/g)||[]).length===(prefix.match(/”/g)||[]).length;
    });
    if(!match)continue;
    const split=match.index+match[0].length;
    const prefix=sentence.slice(0,split),answer=sentence.slice(split).trim();
    if(answer.length<18||answer.length>300||seen.has(sentence))continue;
    seen.add(sentence);facts.push({prefix,answer,sentence});
  }
  // A shared prefix with two different continuations would make a completion
  // ambiguous. Do not turn those source sentences into questions.
  return facts.filter(f=>facts.filter(other=>other.prefix===f.prefix).length===1);
}
function sectionQuestions(section){
  const questions=(practiceExamples[`${section.lesson_id}/${section.id}`]||[]).map(([prompt,answer,first,second,evidence],index)=>({
    family:`original-application-${index}`,kind:'rule_application',prompt,answer,others:[first,second],evidence,original:true,
  })),blocks=section.blocks||[];
  for(const [blockIndex,block] of blocks.entries()){
    if(block.type==='table'&&block.columns?.length>=2&&block.rows?.length>=2){
      const rows=block.rows.filter(r=>r.length===block.columns.length&&r.every(c=>typeof c==='string'));
      for(const [rowIndex,row] of rows.entries()){
        // Choose just one question per row, and include ALL other columns to
        // distinguish repeated labels (e.g. several NP rows with different heads).
        const target=[...block.columns.keys()].reverse().find(i=>unique(rows.map(r=>r[i])).length>=2);
        if(target===undefined)continue;
        const context=row.map((value,i)=>i===target?null:`${block.columns[i]}: “${clean(value)}”`).filter(Boolean).join('; ');
        if(rows.some((other,j)=>j!==rowIndex&&other.every((v,i)=>i===target||clean(v)===clean(row[i]))&&clean(other[target])!==clean(row[target])))continue;
        const answer=clean(row[target]),others=unique(rows.map(r=>r[target])).filter(v=>v!==answer).slice(0,2);
        questions.push({family:`table-${blockIndex}-${rowIndex}`,kind:'lesson_match',
          prompt:`In “${section.title}”, the table “${block.title||section.title}” pairs which ${block.columns[target].toLowerCase()} with ${context}?`,
          answer,others,evidence:`${context}; ${block.columns[target]}: ${answer}.`,
          examples:row.filter((value,i)=>/example|illustration|sentence|expression/i.test(block.columns[i]))});
      }
    }
    if(block.type==='examples'){
      const examples=(block.items||[]).filter(e=>e.text&&e.note);
      for(const [index,example] of examples.entries()){
        const answer=clean(example.note),others=unique(examples.map(e=>e.note)).filter(n=>n!==answer).slice(0,2);
        if(!others.length)continue;
        questions.push({family:`example-${blockIndex}-${index}`,kind:'lesson_match',
          prompt:`In “${section.title}”, which explanation is paired with “${clean(example.text)}”?`,
          answer,others,evidence:`The section pairs “${clean(example.text)}” with this explanation: ${answer}`,examples:[clean(example.text)]});
      }
    }
  }
  const texts=[
    ...(section.texts||[]),
    ...blocks.filter(b=>['paragraph','note'].includes(b.type)).map(b=>b.text).filter(Boolean),
  ];
  const facts=sentenceFacts(texts);
  for(const fact of facts){
    const others=unique(facts.filter(f=>f.sentence!==fact.sentence).map(f=>f.answer)).filter(a=>a!==fact.answer).slice(0,2);
    if(!others.length)continue;
    questions.push({family:`explanation-${hash(fact.sentence)}`,kind:'lesson_recall',
      prompt:`Complete this explanation from “${section.title}” using the wording in the lesson:\n“${fact.prefix} ____”`,
      answer:fact.answer,others,evidence:fact.sentence});
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
export function makeLessonPractice(curriculum,syntaxSource){
  const items=[],ids=new Set();
  for(const track of curriculum)for(const chapter of track.chapters)for(const topic of chapter.topics){
    const source=track.id==='syntax'
      ? syntaxSource?.sections?.find(s=>s.lesson_id===chapter.id&&s.subtopic_id===topic.id)
      : cambridgeChapterData[chapter.id]?.sections.find(s=>s.id===topic.id);
    if(!source)continue;
    if(track.id==='syntax'&&(source.lesson_version!==chapter.content_version||source.article_digest!==syntaxPracticeDigest(chapter.id)))continue;
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
      ||q.options.length<2||new Set(q.options.map(o=>o.text)).size!==q.options.length
      ||!q.options.some(o=>o.id===q.answer)||!q.rationale||!q.source_metadata?.excerpt
      ||q.lesson_reference!==`#lesson/${q.chapter_id}/${q.subtopic_id}`)throw Error('Invalid lesson practice content.');
    ids.add(q.item_id);prompts.add(promptKey);
  }
  return items;
}
