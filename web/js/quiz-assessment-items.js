// Versioned formal questions. Project-approved for publication; independent human review is false.
import {isRelevantAssessmentQuestion} from './quiz-scope.js';
import {formatTablePrompt} from './quiz-lesson-practice.js';
import {syntaxApprovedAdditions} from './quiz-approved-syntax.js';
import {cambridgeApprovedAdditions} from './quiz-approved-cambridge.js';

const APPROVAL = {
  publication_status: 'published',
  review_status: 'PROJECT_APPROVED',
  independent_review: false,
  approved_by: 'project-owner',
  approved_on: '2026-11-16',
};

export function makeAssessmentItems(lessonItems, curriculum = null) {
  const items=lessonItems.flatMap(q=>{
    let prompt=q.prompt,options=q.options.map(o=>({...o})),answer=q.answer,kind=q.kind;
    if(kind==='lesson_recall'){
      // Incomplete-sentence verb-splitting is retired; exclude safely.
      return [];
    }else if(kind==='lesson_match'){
      const legacyTable=/^In “[^”]+”, the table “([^”]+)” pairs which (.+?) with (.+)\?$/.exec(prompt);
      const example=/^In “[^”]+”, which explanation is paired with “(.+)”\?$/.exec(prompt);
      if(legacyTable)prompt=formatTablePrompt(legacyTable[1],legacyTable[2],legacyTable[3]);
      else if(example)prompt=`Which grammatical analysis correctly describes “${example[1]}”?`;
      else if(!/^In “[^”]+”, (?:given|select the) /i.test(prompt))return [];
      kind='analysis';
    }
    return [{...q,item_id:q.item_id.replace(/^lesson-practice:/,'lesson-assessment:')+':formal-1',
      content_version:'lesson-assessment-1.0.0',...APPROVAL,
      kind,prompt,options,answer,assessment_format:'independent',
      source_metadata:{...q.source_metadata,assessment_derivation:'application_or_analysis'},
    }];
  });
  const additions=[
    ['br-01','application','In “The reporter interviewed the actor on the balcony”, what does attachment of “on the balcony” inside the object NP specify?','Which actor is being identified','The tense of interviewed','The main-clause subject','Within the object NP, the PP modifies actor. Attachment to the interviewing phrase instead relates the location to the event.'],
    ['br-01','application','Two analyses keep all the same words in the same order but attach a PP to different constituents. What can differ?','The interpretation of which constituent the PP modifies','Necessarily the spelling of the words','Necessarily the number of verbs','Constituent grouping and attachment can change interpretation without changing the surface word sequence.'],
    ['cgel-ch06','modifier-style','An editor finds a long sequence of -ly adverbs awkward. Does that observation alone establish that the sequence is ungrammatical?','No; grammatical structure and stylistic effectiveness are distinct','Yes; every awkward sequence violates grammar','Yes; adverbs cannot modify other adverbs','A grammatical modifier sequence may still be difficult to process or ineffective in its context.'],
    ['cgel-ch06','modifier-style','What should an analyst establish before deciding the scope of a modifier?','Which head or construction the modifier is attached to','Only whether the word ends in -ly','Only the number of syllables in the word','Modifier interpretation depends on structural attachment and scope, not just its category label or spelling.'],
    ['br-07','application','In “Someone beside the fountain waved”, what does “beside the fountain” modify on the NP-internal reading?','The referent of someone','The tense of waved','The manner of waving','The PP narrows the reference of the indefinite pronoun inside the subject NP; it does not describe how the waving occurred.'],
    ['br-07','application','Which phrase follows the position of an adjective modifying an indefinite pronoun taught in this lesson?','something fragile','fragile something','fragile very something','An adjective modifying an indefinite pronoun such as something follows it: something fragile. This differs from ordinary pre-nominal modification, as in a fragile vase.'],
  ];
  const pushAuthored=(chapter,topic,keyId,prompt,correct,first,second,rationale)=>{
    const basis=lessonItems.find(q=>q.chapter_id===chapter&&q.subtopic_id===topic)
      ||lessonItems.find(q=>q.chapter_id===chapter);
    const trackId=basis?.track_id||(chapter.startsWith('br-')?'syntax':'cambridge');
    const chapterMeta=curriculum?.find(t=>t.id===trackId)?.chapters.find(c=>c.id===chapter);
    const outcomes=basis?.outcome_ids||chapterMeta?.outcomes?.map(o=>o.id)||[];
    const sourceMeta=basis?.source_metadata||{
      kind:'syntutor_lesson_section',
      artifact:trackId==='syntax'?'content/quizzes/syntax-practice-source.json':'js/cambridge-chapter-data.js',
    };
    items.push({...(basis||{}),item_id:`lesson-assessment:${chapter}:${topic}:${keyId}:formal-1`,
      pool_id:`lesson-practice:${chapter}:${topic}`,track_id:trackId,chapter_id:chapter,
      subtopic_id:topic,lesson_id:chapter,concept_ids:[`${chapter}:${topic}`],outcome_ids:outcomes,
      lesson_reference:`#lesson/${chapter}/${topic}`,
      content_version:'lesson-assessment-1.0.0',...APPROVAL,assessment_format:'independent',
      kind:'rule_application',prompt,answer:'a',rationale,
      options:[correct,first,second].map((text,i)=>({id:String.fromCharCode(97+i),text,rationale:i===0?rationale:`Incorrect. ${rationale}`})),
      source_metadata:{...sourceMeta,section_id:topic,excerpt:rationale,derivation:'original_application'},
      practice_family:`${chapter}:${topic}:${keyId}`,practice_example_ids:[],
    });
  };
  for(const [index,[chapter,topic,prompt,correct,first,second,rationale]] of additions.entries()){
    pushAuthored(chapter,topic,`application-${index}`,prompt,correct,first,second,rationale);
  }
  for(const [topicKey,tuples] of [...Object.entries(syntaxApprovedAdditions),...Object.entries(cambridgeApprovedAdditions)]){
    const [chapter,topic]=topicKey.split('/');
    for(const [index,[prompt,correct,first,second,rationale]] of tuples.entries()){
      pushAuthored(chapter,topic,`approved-${index}`,prompt,correct,first,second,rationale);
    }
  }
  return items.filter(isRelevantAssessmentQuestion);
}
export function validateAssessmentItems(items,curriculum){
  const ids=new Set(),prompts=new Set();
  for(const q of items){
    const chapter=curriculum.find(t=>t.id===q.track_id)?.chapters.find(c=>c.id===q.chapter_id);
    const promptKey=`${q.chapter_id}/${q.subtopic_id}/${q.prompt}`;
    if(!chapter?.topics.some(t=>t.id===q.subtopic_id)||ids.has(q.item_id)||prompts.has(promptKey)
      ||!isRelevantAssessmentQuestion(q)
      ||q.lesson_id!==q.chapter_id||q.lesson_reference!==`#lesson/${q.chapter_id}/${q.subtopic_id}`
      ||q.source_metadata?.section_id!==q.subtopic_id
      ||q.assessment_format!=='independent'||q.publication_status!=='published'
      ||q.review_status!=='PROJECT_APPROVED'||q.independent_review!==false||!q.approved_by
      ||!['analysis','rule_application'].includes(q.kind)
      ||q.options.length<3||!q.options.some(o=>o.id===q.answer)||new Set(q.options.map(o=>o.text)).size!==q.options.length
      ||q.options.some(o=>/^[,;:.!?]/.test(o.text.trim()))
      ||!q.options.every(o=>o.rationale)
      ||/\bwhich (what|how|why|when|where|whether)\b/i.test(q.prompt)
      ||/Given\s*:/i.test(q.prompt)
      ||/____/.test(q.prompt)
      ||/using the wording in the lesson|which explanation is paired with|the table “[^”]+” pairs/i.test(q.prompt))
      throw Error('Invalid formal assessment item.');
    ids.add(q.item_id);prompts.add(promptKey);
  }
  return items;
}
