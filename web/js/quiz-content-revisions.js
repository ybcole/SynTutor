// Keep original item identities/keys available for historical attempts. Only new
// selection uses these separately identified corrections; never rewrite a key.
const phrase=(label,children,extra={})=>({label,children,...extra});
const word=text=>({word:text});
const gap=index=>({gap:true,index});
function whRevision({subject,verb,embedded=false,outer='Lila',wh='What'}) {
 return original=>{
  const whWords=wh.split(' ');
  const front=phrase('C2',whWords.length===1?[word(wh)]:[phrase('NP',[
   phrase('DET',[phrase('Q',[word(whWords[0])])]),phrase('NOM',[phrase('N',[word(whWords[1])])])])],{index:1});
  const lowerVP=phrase('VP',[phrase('V',[word(verb)]),phrase('NP',[gap(1)])]);
  const clause=phrase('S',[phrase('NP',[phrase('name',[word(subject)])]),
   embedded?lowerVP:phrase('VP',[phrase('PROG',[gap(2)]),lowerVP])]);
  const whClause=phrase('S-dbar',[front,phrase('S-bar',[
   embedded?{empty:true,label:'C1'}:phrase('C1',[word('is')],{index:2}),clause])]);
  const root=embedded?phrase('S',[phrase('NP',[phrase('name',[word(outer)])]),phrase('VP',[phrase('V',[word('asked')]),whClause])]):whClause;
  const words=embedded?[outer,'asked',...whWords,subject,verb]:[...whWords,'is',subject,verb];
  const sentence=words.join(' ');
  let offset=0;
  const tokens=words.map((text,index)=>{const start=offset;offset+=text.length+1;return {index,text,char_span:[start,offset-1]};});
  const envelope=root=>({...original.expected_tree,sentence,tokens,root,movement:[],accepted_alternatives:[]});
  const summary=embedded?'C2 holds the wh-expression, C1 is empty, and the object gap stays inside VP.':'C2 holds the wh-expression, C1 holds the fronted auxiliary, and indexed gaps mark their original positions.';
  return {
   prompt:`${original.kind==='syntax_correction'?'Repair':'Build'} the ${embedded?'embedded':'main'} wh-clause in “${sentence}”. Use C2 for the wh-expression and C1 for ${embedded?'the unfilled lower position':'the fronted progressive auxiliary'}; include the corresponding indexed gap${embedded?'':'s'}.`,
   expected_tree:envelope(root),accepted_trees:[],expected_summary:summary,display_answer:summary,rationale:summary,
   ...(original.kind==='syntax_correction'?{stimulus:{sentence},seed_tree:envelope(phrase('S',words.map(word)))}:{seed_tokens:sentence}),
  };
 };
}
const corrections = {
 'mixed:br-09:worked-example:syntax_correction:1':whRevision({subject:'Omar',verb:'sketching'}),
 'mixed:br-09:concepts:syntax_correction:3':whRevision({subject:'Ada',verb:'reading'}),
 'mixed:br-09:worked-example:syntax_correction:5':whRevision({subject:'Hana',verb:'playing',wh:'Which tune'}),
 'mixed:br-09:worked-example:tree_builder:1':whRevision({subject:'Lila',verb:'photographing'}),
 'mixed:br-09:concepts:tree_builder:2':whRevision({subject:'Noor',verb:'repairing'}),
 'mixed:br-09:worked-example:tree_builder:4':whRevision({subject:'Ivo',verb:'restoring'}),
 'mixed:br-09:embedded-interrogatives:syntax_correction:2':whRevision({subject:'Omar',verb:'repaired',wh:'what',embedded:true}),
 'mixed:br-09:embedded-interrogatives:tree_builder:3':whRevision({subject:'Noor',verb:'painted',outer:'Ivo',wh:'what',embedded:true}),
 'mixed:br-09:concepts:fill_blank:1':{
  prompt:'In “What is Hana drawing?”, “what” occupies the higher front position and “is” the lower one. The label of the higher position is _____.',
  accepted_answers:['C2'],
  rationale:'The lesson places the wh-expression in C2 under S-dbar and the fronted auxiliary in C1 under S-bar.',
 },
 'mixed:br-09:embedded-interrogatives:fill_blank:3':{
  prompt:'Compare “What is Hana drawing?” with “I asked what Hana is drawing”. The embedded question retains subject–auxiliary order instead of applying _____.',
  accepted_answers:['inversion','subject-auxiliary inversion','subject–auxiliary inversion'],
  rationale:'Main wh-questions front the auxiliary to C1. Embedded wh-interrogatives leave C1 unfilled and keep the auxiliary after the subject; the wh-expression still occupies C2.',
 },
 'mixed:br-04:worked-example:syntax_correction:1': {
  prompt:'Repair the verb category in “Mira thanked Sam”. Represent thanked as a transitive V and retain Sam as its object inside the VP.',
  subtopic_id:'concepts',
  concept_ids:['br-04:concepts'],
  lesson_reference:'#lesson/br-04/concepts',
 },
 'mixed:cgel-ch07:pp-complementation:grammar_correction:1': {
  prompt:'Replace only the pronoun “I” with the object-case form required after the preposition “to”; preserve the remaining wording.',
  stimulus:{sentence:'The invitation was sent to Priya and I.'},
  accepted_answers:['The invitation was sent to Priya and me.'],
  rationale:'The coordinated NP is the complement of to. In the formal Standard English pattern requested here, the pronoun takes object case me.',
 },
 'mixed:cgel-ch13:scalar-inequality:grammar_correction:1': {
  prompt:'Replace only “more clearer” with a comparative form of “clear”, preserving the comparison and all other wording.',
  stimulus:{sentence:'This diagram is more clearer than the earlier sketch.'},
  accepted_answers:['This diagram is clearer than the earlier sketch.','This diagram is more clear than the earlier sketch.'],
  rationale:'Clearer and more clear each mark the comparison once. Combining more with clearer marks it twice in the intended standard construction. The analytic alternative more clear is also grammatical.',
 },
 'mixed:cgel-ch14:verbless-clauses:sentence_reconstruction:5': {
  prompt:'Begin with a verbless absolute describing the studio, then state what the artists did. Use every token and retain its punctuation.',
  tokens:['silent,','studio','the','began','the artists','sketching'],
  accepted_answers:['the studio silent, the artists began sketching'],
  rationale:'The studio silent is a verbless absolute: the studio is its subject and silent its predicative complement. The fixed comma closes that initial clause; it cannot move after sketching.',
 },
 'mixed:cgel-ch14:form-types:sentence_reconstruction:11': {
  prompt:'Arrange the tokens with “they” as subject and a bare infinitival complement after “helped us”. Use every supplied token without adding “to”.',
  tokens:['the equipment','helped us','carry','they'],
  accepted_answers:['they helped us carry the equipment'],
  rationale:'Help can license a bare infinitival complement. The fixed tokens contain no to, so a to-infinitival alternative cannot be constructed with this input.',
 },
 'mixed:cgel-ch15:layered-scope:sentence_reconstruction:11': {
  prompt:'A meal always includes rice plus a choice of beans or lentils. Place “either” immediately before the two alternatives to make their scope explicit.',
  tokens:['lentils','rice','and','either','beans','or'],
  accepted_answers:['rice and either beans or lentils','rice and either lentils or beans'],
  rationale:'Rice is the first coordinate; either beans or lentils is the second. Either makes the choice inside that second coordinate explicit, so rice accompanies either alternative.',
 },
 'mixed:cgel-ch20:quotation:sentence_reconstruction:3': {
  prompt:'Put the reporting clause first, followed by the direct quotation. Preserve the supplied punctuation and use every token.',
  tokens:['“The','ready.”','are','said,','he','maps'],
  accepted_answers:['he said, “The maps are ready.”'],
  rationale:'The comma introduces the quotation after the reporting clause. A quotation-first order would require different punctuation, which the fixed tokens do not supply. This item uses one consistent quotation convention.',
 },
 'mixed:cgel-ch01:truth-entailment:fill_blank:4': {
  prompt:'A report states “Ari shattered the vase”. Even with no further context, “The vase broke” must be true. The first proposition _____ the second.',
  accepted_answers:['entails'],
  rationale:'Shattering the vase guarantees that it broke. This is a truth-conditional entailment, rather than a defeasible inference about what usually happens. The item applies the relation to an event instead of reciting its definition.',
 },
 'mixed:cgel-ch01:truth-entailment:sentence_reconstruction:11': {
  prompt:'Three of five sculptures survived intact. Reconstruct the conclusion this guarantees, with negation taking scope over “all”; do not assert that none was damaged.',
  tokens:['damaged','were','all','not','the sculptures'],
  accepted_answers:['not all the sculptures were damaged'],
  rationale:'At least three escaped damage, so damage did not affect the entire set. Not all negates the universal claim; it does not claim that every sculpture escaped damage. The original word-order-only task did not require an inference.',
 },
 'mixed:cgel-ch03:situations-aspect:fill_blank:11': {
  prompt:'Compare “Nora repaired one bicycle” with “Nora repaired bicycles”. Only the first predicate specifies an inherent endpoint; it is therefore _____.',
  accepted_answers:['telic'],
  rationale:'Repairing one bicycle has an inherent completion point; repairing bicycles has no specified endpoint. Telicity concerns that endpoint, whereas perfective viewpoint presents a situation as a whole.',
 },
 'mixed:cgel-ch05:pronouns:grammar_correction:12': {
  prompt:'Replace only the incorrect genitive form before “car”; preserve the rest of the sentence.',
  stimulus:{sentence:'Her keys worked, but hers car stayed locked.'},
  accepted_answers:['Her keys worked, but her car stayed locked.'],
  rationale:'Her is the dependent genitive used before the overt noun car. Hers is independent and cannot fill that position.',
 },
 'mixed:cgel-ch20:comma-uses:sentence_reconstruction:5': {
  prompt:'Arrange every token into a sentence beginning with “Although”; retain the comma closing the initial subordinate clause.',
  tokens:['continued','although','the','match','it','rained,'],
  accepted_answers:['although it rained, the match continued'],
  rationale:'The comma marks the end of the initial subordinate clause. Moving that clause to the end would require changing punctuation, which these fixed tokens do not allow.',
 },
 'mixed:cgel-ch01:defining-concepts:fill_blank:11': {
  prompt:'In “They pocketed the receipt”, pocketed takes a past-tense ending and an object despite referring to a container-related action. Its category is _____.',
  accepted_answers:['verb','a verb'],
  rationale:'The tense ending and object provide grammatical evidence for verb status. A meaning associated with a container does not establish noun status.',
 },
 'mixed:cgel-ch01:defining-concepts:sentence_reconstruction:12': {
  prompt:'Arrange the tokens so that the converted verb “pocketed” heads the predicate and “the receipt” is its object.',
  tokens:['the receipt','pocketed','they'],
  accepted_answers:['they pocketed the receipt'],
  rationale:'Pocketed functions as a finite transitive verb, with they as subject and the receipt as object. The construction tests category by distribution with an example not demonstrated in the lesson.',
 },
};
export const revisedMixedIds=Object.freeze(Object.keys(corrections));
export function applyMixedRevisions(items, trackId='cambridge') {
 const ids=revisedMixedIds.filter(id=>trackId==='syntax'?id.startsWith('mixed:br-'):id.startsWith('mixed:cgel-'));
 const originals=items.map(q=>ids.includes(q.item_id)?{...q,retired_from_selection:true}:q);
 const revised=items.filter(q=>ids.includes(q.item_id)).map(q=>{
  const correction=corrections[q.item_id];
  const edit=typeof correction==='function'?correction(q):correction;
  return {...q,...edit,item_id:q.item_id+':revision-2',content_version:'2.0.1',
   replaces_item_id:q.item_id,display_answer:edit.accepted_answers?.[0]||edit.display_answer||q.display_answer,
   practice_family:q.practice_family||q.item_id};
 });
 if(revised.length!==ids.length)throw Error('Missing original mixed item for a content correction.');
 return [...originals,...revised];
}
