// Keep original item identities/keys available for historical attempts. Only new
// selection uses these separately identified corrections; never rewrite a key.
const corrections = {
 'mixed:cgel-ch20:functions:grammar_correction:12': {
  prompt:'Correct only the final punctuation of this direct question. Use a question mark, with no additional terminal mark.',
  accepted_answers:['Did anyone check the final totals?'],
  punctuation_sensitive:true,
  rationale:'A direct interrogative here ends in a question mark. An extra full stop after that question mark is not part of the required correction.',
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
export function applyMixedRevisions(items) {
 const originals=items.map(q=>corrections[q.item_id]?{...q,retired_from_selection:true}:q);
 const revised=items.filter(q=>corrections[q.item_id]).map(q=>{
  const edit=corrections[q.item_id];
  return {...q,...edit,item_id:q.item_id+':revision-2',content_version:'2.0.1',
   replaces_item_id:q.item_id,display_answer:edit.accepted_answers[0],
   practice_family:q.practice_family||q.item_id};
 });
 if(revised.length!==revisedMixedIds.length)throw Error('Missing original mixed item for a content correction.');
 return [...originals,...revised];
}
