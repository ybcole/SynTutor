const keyTerms = {
  'br-01': [
    ['Constituent', 'A word or group of words that acts as a unit within a larger expression.'],
    ['Hierarchy', 'The arrangement of smaller units inside larger ones. In a syntax tree, branches show which units belong together.'],
    ['Replacement test', 'A way to check whether words form a unit by replacing them with a suitable expression, such as a pronoun, and checking that the rest of the sentence still fits.'],
    ['Structural ambiguity', 'Two or more possible readings that come from grouping or attaching the same words differently.'],
  ],
  'br-02': [
    ['Subject', 'A grammatical function within a clause. In a typical English statement, the subject comes before the verb and controls agreement where the verb shows it.'],
    ['Predicate', 'The part of a clause that says what the subject does, what happens to it, or what state it is in.'],
    ['Category', 'The kind of word or phrase something is, such as a noun phrase (NP) or a verb phrase (VP).'],
    ['Function', 'The grammatical role a word or phrase has within a larger structure, such as subject or object.'],
  ],
  'br-03': [
    ['Head', 'The central word of a phrase, which determines the phrase’s grammatical category.'],
    ['Adjective phrase (AP)', 'A phrase headed by an adjective. It can consist of the adjective alone or include words that modify or complete it.'],
    ['Degree word (DEG)', 'A word such as “very” or “quite” that indicates the degree to which a quality applies.'],
  ],
  'br-04': [
    ['Transitive verb (V [trans])', 'A verb used with a direct object. Transitivity describes how the verb is used in a particular construction.'],
    ['Direct object', 'A verb complement that typically follows the verb in an active English clause. It often identifies the person or thing affected by the action.'],
    ['Sister nodes', 'Nodes that share the same immediate parent in a tree.'],
  ],
  'br-05': [
    ['Complement', 'A phrase or clause that fills a role licensed by its head. A direct object is one kind of verb complement.'],
    ['Adjunct', 'A modifier that adds information such as time, place, or manner to a phrase or clause.'],
    ['Inner and outer VP', 'Two levels of verb phrase structure. The inner VP sits inside the outer VP, which also covers material attached at the higher level.'],
  ],
  'br-06': [
    ['Progressive auxiliary (PROG)', 'A form of “be” used with a verb in its -ing form to present a situation as ongoing.'],
    ['Lexical VP', 'A verb phrase headed by the main verb, together with any complements of that verb.'],
    ['VP complement', 'A verb phrase that serves as the complement of a head, such as an auxiliary.'],
    ['Tense', 'A grammatical feature, such as present or past, that helps locate a situation in time.'],
  ],
  'br-07': [
    ['Determiner (DET)', 'A word or expression that helps identify or quantify what a noun phrase refers to. DET labels its position in the tree.'],
    ['Demonstrative (DEM)', 'A word such as “this”, “that”, “these”, or “those” that points out a referent.'],
    ['Nominal (NOM)', 'The part of a noun phrase built around the head noun. In Burton-Roberts trees, NOM forms a layer between NP and N and can contain noun modifiers.'],
    ['Head noun (N)', 'The noun that heads the nominal and gives the noun phrase its basic reference.'],
  ],
  'br-08': [
    ['Embedded clause', 'A clause that forms part of a larger phrase or clause.'],
    ['Complementiser (C)', 'A word such as “that” or “whether” that introduces a subordinate clause. C labels its position in the tree.'],
    ['S and S′', 'In Burton-Roberts trees, S labels the clause with its subject and predicate. S′, read “S-bar”, is the higher layer that groups C with S.'],
  ],
  'br-09': [
    ['Fronting', 'Placing a word or phrase near the beginning of a clause, earlier than its usual position.'],
    ['C1', 'The lower front position in the Burton-Roberts question tree. A fronted tensed auxiliary occupies C1 in a main-clause question.'],
    ['C2', 'The higher front position in the Burton-Roberts question tree. A fronted wh-expression such as “what” occupies C2.'],
    ['Gap', 'A position with no spoken word or phrase. In a tree with fronting, a gap marks the position associated with the fronted expression.'],
  ],
  'br-10': [
    ['Infinitival “to”', 'The marker “to” that precedes a base-form verb in a to-infinitive. Burton-Roberts analyses it as an untensed auxiliary.'],
    ['Non-finite', 'A term for verb forms and clauses that carry no tense of their own. Infinitives and participles are non-finite verb forms.'],
    ['Stem form', 'The base form of a verb, such as “go”, “write”, or “inspect”.'],
    ['Lexical VP', 'A verb phrase headed by the main verb, together with any complements of that verb.'],
  ],
  'br-11': [
    ['Grammar', 'A system of patterns that describes how words and groups combine to form larger expressions.'],
    ['Combination rule', 'An instruction that specifies which units can combine and how the resulting structure is grouped.'],
    ['Recursion', 'A pattern in which a rule can apply again within or to the structure it produces, allowing further layers.'],
  ],
  'cgel-clauses': [
    ['Written sentence', 'A unit of written text, usually marked by an initial capital letter and sentence-ending punctuation.'],
    ['Clause', 'A grammatical unit organised around a predicate. A typical clause has a subject and a predicate.'],
    ['Embedded clause', 'A clause that forms part of a larger phrase or clause.'],
  ],
};

export function addLessonKeyTerms(body, el, lessonId) {
  const terms = keyTerms[lessonId];
  if (!terms) return;
  const section = el('section', undefined, 'lesson-key-terms');
  section.append(el('h3', 'Key terms'));
  const list = el('dl');
  for (const [term, definition] of terms) {
    const entry = el('div');
    entry.append(el('dt', term), el('dd', definition));
    list.append(entry);
  }
  section.append(list);
  body.append(section);
}
