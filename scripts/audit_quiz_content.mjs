// Screening evidence, NOT an educational-quality approval. See the audit report.
import fs from 'node:fs';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {cambridgeChapterData} from '../web/js/cambridge-chapter-data.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {questionMetadata} from '../web/js/quiz-v2.js';
import {syntaxMixedItems} from '../web/js/quiz-mixed-syntax.js';
import {cambridgeMixedItems} from '../web/js/quiz-mixed-cambridge.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../web'+p,import.meta.url)));
const curriculum=quizCurriculum(await loadActiveCourse(async p=>({ok:true,json:()=>read(p)})));
const source=read('/content/quizzes/syntax-practice-source.json');
const formal=makeAssessmentItems(makeLessonPractice(curriculum,source),curriculum);
const immutable=read('/content/quizzes/bank.json').items;
const mixed=[...syntaxMixedItems,...cambridgeMixedItems];
const normalize=t=>String(t).toLowerCase().replace(/[^\p{L}\p{N}\s]/gu,' ').replace(/\s+/g,' ').trim();
const overlaps=[];
for(const q of [...immutable,...formal,...mixed]){
 const meta=questionMetadata(q,curriculum);if(!meta)continue;
 const section=meta.track_id==='syntax'
  ?source.sections.find(s=>s.lesson_id===meta.chapter_id&&s.subtopic_id===meta.subtopic_id)
  :cambridgeChapterData[meta.chapter_id]?.sections.find(s=>s.id===meta.subtopic_id);
 const lessonText=normalize(JSON.stringify(section||{}));
 const fragments=[...String(q.prompt).matchAll(/“([^”]+)”/g)].map(m=>m[1]);
 if(q.stimulus?.sentence)fragments.push(q.stimulus.sentence);
 if(q.kind==='sentence_reconstruction')fragments.push(...q.accepted_answers);
 const repeated=fragments.filter(f=>normalize(f).split(' ').length>=4&&lessonText.includes(normalize(f)));
 if(repeated.length)overlaps.push({item_id:q.item_id,retired:!!q.retired_from_selection,repeated,lesson:`${meta.chapter_id}/${meta.subtopic_id}`});
}
const formats={};
for(const track of curriculum)for(const chapter of track.chapters){
 formats[chapter.id]=[...new Set(mixed.filter(q=>q.chapter_id===chapter.id&&!q.retired_from_selection).map(q=>q.kind))];
}
const report={scope:'Automated overlap candidates and format inventory; manual findings are documented separately. Overlap is not by itself a defect.',
 counts:{immutable:immutable.length,formal:formal.length,mixed:mixed.length,retired:mixed.filter(q=>q.retired_from_selection).length,overlapCandidates:overlaps.length,activeOverlapCandidates:overlaps.filter(q=>!q.retired).length},formats,overlaps};
console.log(JSON.stringify(report.counts,null,2));
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
