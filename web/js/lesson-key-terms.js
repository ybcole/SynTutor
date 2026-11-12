const keyTerms = {
  'br-01': [
    ['Constituent', 'A word or group of words that acts as one unit in a sentence.', '“The quiet garden” forms a unit inside “near the quiet garden”.'],
    ['Hierarchy', 'The arrangement of smaller units inside larger ones.', 'The garden group sits inside the whole place phrase.'],
    ['Replacement test', 'A way to check a group by substituting one suitable expression for it.', '“It” replaces “the quiet garden” in “We met near it”.'],
    ['Structural ambiguity', 'Two possible meanings that come from grouping the same words differently.', '“With a telescope” can describe how I watched or identify which hikers I watched.'],
  ],
  'br-02': [
    ['Subject', 'The group the predicate says something about in the simple statements studied here.', '“The robins” is the subject in “The robins sing”.'],
    ['Predicate', 'The group that says something about the subject.', '“Are singing softly” is the whole predicate in the longer robins example.'],
    ['Category', 'The kind of group a phrase is.', 'Noun phrase (NP) and verb phrase (VP) are categories.'],
    ['Function', 'The job a phrase does in a larger structure.', '“The robins” is an NP in both examples. It serves as subject in “The robins sing” and as object in “Maya watched the robins”.'],
  ],
  'br-03': [
    ['Head', 'The word that gives a phrase its basic grammatical character.', '“Cheerful” is the head of “very cheerful”.'],
    ['Adjective phrase (AP)', 'A phrase headed by an adjective (A).', 'Both “cheerful” and “very cheerful” can form an AP.'],
    ['Degree word (DEG)', 'A word that indicates the strength or degree of a description.', '“Very” tells us how cheerful the children seemed.'],
  ],
  'br-04': [
    ['Transitive verb (V [trans])', 'In the pattern here, a verb used with a direct object.', '“Inspected” takes the object “the bridge”.'],
    ['Direct object', 'A complement of the verb that identifies what or whom the action concerns in these examples.', 'Ask what Nora inspected. “The bridge” is the complete answer and the object NP.'],
    ['Sister nodes', 'Nodes that share an immediate parent in a tree.', 'V and the direct-object NP are sisters under VP.'],
  ],
  'br-05': [
    ['Complement', 'A group that fills a role in the grammatical pattern of a head.', 'The object “the bridge” is the complement of “inspected”.'],
    ['Adjunct', 'A group that adds information such as time or place to a larger group.', '“In June” adds the time of the inspection.'],
    ['Inner and outer VP', 'Two verb phrases, with one contained in the other.', '“Inspected the bridge” is the inner VP. The outer VP adds “in June”.'],
  ],
  'br-06': [
    ['Progressive auxiliary (PROG)', 'A form of “be” used with an -ing verb to present an activity as in progress.', '“Is” is the progressive auxiliary in “Nora is inspecting the bridge”.'],
    ['Lexical VP', 'The verb phrase headed by the main verb in this analysis.', '“Inspecting the bridge” groups the main verb and its object.'],
    ['VP complement', 'A verb phrase that fills the complement role of another head.', 'The whole lexical VP is the complement of “is”.'],
    ['Tense', 'A grammatical feature of a verb form, such as present or past.', 'The tense feature [pres] belongs to PROG in “is inspecting”.'],
  ],
  'br-07': [
    ['Determiner (DET)', 'The position for a word that helps identify or specify what a noun phrase refers to.', 'DET is one of the two immediate branches under NP.'],
    ['Demonstrative (DEM)', 'A word such as “this” or “those” that points out which thing or group is meant.', '“Those” is a DEM inside DET.'],
    ['Nominal (NOM)', 'The level of noun phrase structure that contains the head noun and any modifiers in this analysis.', 'NOM contains only “lanterns” in the worked example.'],
    ['Head noun (N)', 'The noun that supplies the basic kind of thing named by the phrase.', '“Lanterns” is the head noun of “those lanterns”.'],
  ],
  'br-08': [
    ['Embedded clause', 'A clause that appears inside a larger grammatical structure.', '“Nora is inspecting the bridge” has its own subject and predicate inside Leo’s report.'],
    ['Complementiser (C)', 'A word that introduces a subordinate clause in the pattern taught here.', '“That” introduces the reported content and appears under C.'],
    ['S and S′', 'S marks the inner subject–predicate structure. S′ groups C with that inner S in this pattern.', 'S begins at “Nora”. S′ begins at “that”.'],
  ],
  'br-09': [
    ['Fronting', 'Placing a word or phrase earlier than its corresponding position in the statement.', '“What” appears at the start of the question, while the corresponding object follows “inspecting” in the statement.'],
    ['C1', 'The front position used by the tensed auxiliary in these questions.', '“Is” occupies C1 in “What is Nora inspecting?”'],
    ['C2', 'The higher front position for the wh-expression in this analysis.', '“What” occupies C2.'],
    ['Gap', 'An unspoken position in the tree that shows where a fronted item belongs in the corresponding statement.', 'One gap is under PROG for “is”. The other is under the object NP for “what”.'],
  ],
  'br-10': [
    ['Infinitival “to”', 'The form of “to” used with the base form of a verb. In this analysis it is an untensed auxiliary.', '“To” in “to inspect the bridge” carries the feature [-tense].'],
    ['Non-finite', 'A verb form or phrase that has no tense of its own in the pattern taught here.', '“To inspect the bridge” stays the same after “plans” or “planned”.'],
    ['Stem form', 'The base form of a verb, without endings such as -s, -ed, or -ing.', '“Inspect” is the stem after infinitival “to”.'],
    ['Lexical VP', 'The phrase headed by the main verb.', '“Inspect the bridge” is the lexical VP that follows “to”.'],
  ],
  'br-11': [
    ['Grammar', 'A system of rules that describes how expressions can be built and grouped.', 'The toy grammar has basic sentences and a rule for joining them.'],
    ['Combination rule', 'An instruction for building a larger expression from eligible inputs.', 'The rule joins two complete sentences with “and”.'],
    ['Recursion', 'Using the output of a rule as an input to that same rule.', 'A sentence made by joining “Iris rests” and “Leo waits” can be joined with another sentence.'],
  ],
  'cgel-clauses': [
    ['Written sentence', 'A complete unit of written text, usually marked by an initial capital and final punctuation.', '“Nora reports that the robins sing.” is one written sentence.'],
    ['Clause', 'A grammatical unit that typically contains a subject and predicate.', '“The robins sing” has a subject and predicate.'],
    ['Embedded clause', 'A clause that forms part of a larger grammatical structure.', 'The robins’ singing is reported inside the larger clause about Nora.'],
  ],
};

export function addLessonKeyTerms(body, el, lessonId) {
  const terms = keyTerms[lessonId];
  if (!terms) return;
  const section = el('section', undefined, 'lesson-key-terms');
  section.append(el('h3', 'Key terms'));
  const list = el('dl');
  for (const [term, definition, example] of terms) {
    const description = el('dd');
    const use = el('p');
    use.append(el('strong', 'In this chapter'), ' ', example);
    description.append(el('p', definition), use);
    const entry = el('div');
    entry.append(el('dt', term), description);
    list.append(entry);
  }
  section.append(list);
  body.append(section);
}
