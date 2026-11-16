export function cambridgeDiff(chId, kind) {
  const num = chId === 'cgel-clauses' ? 2 : Number(String(chId).replace('cgel-ch', '')) || 1;
  if (num <= 6) return kind === 'grammar_correction' ? 'medium' : 'easy';
  if (num <= 13) return kind === 'fill_blank' ? 'easy' : kind === 'grammar_correction' ? 'hard' : 'medium';
  return kind === 'fill_blank' ? 'medium' : 'hard';
}

export function cBlank(chId, topic, idx, prompt, accepted, rationale) {
  return {
    item_id: `mixed:${chId}:${topic}:fill_blank:${idx}`,
    pool_id: `mixed:${chId}:${topic}:fill_blank`,
    content_version: '2.0.0',
    track_id: 'cambridge',
    chapter_id: chId,
    subtopic_id: topic,
    lesson_id: chId,
    concept_ids: [`${chId}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/${chId}/${topic}`,
    kind: 'fill_blank',
    difficulty: cambridgeDiff(chId, 'fill_blank'),
    prompt,
    accepted_answers: accepted,
    display_answer: accepted[0],
    rationale,
  };
}

export function cFix(chId, topic, idx, prompt, badSentence, accepted, rationale) {
  return {
    item_id: `mixed:${chId}:${topic}:grammar_correction:${idx}`,
    pool_id: `mixed:${chId}:${topic}:grammar_correction`,
    content_version: '2.0.0',
    track_id: 'cambridge',
    chapter_id: chId,
    subtopic_id: topic,
    lesson_id: chId,
    concept_ids: [`${chId}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/${chId}/${topic}`,
    kind: 'grammar_correction',
    difficulty: cambridgeDiff(chId, 'grammar_correction'),
    prompt,
    stimulus: { sentence: badSentence },
    accepted_answers: accepted,
    display_answer: accepted[0],
    rationale,
  };
}

export function cRecon(chId, topic, idx, tokens, accepted, rationale, prompt = 'Arrange the supplied words/constituents into a grammatical English sentence.') {
  return {
    item_id: `mixed:${chId}:${topic}:sentence_reconstruction:${idx}`,
    pool_id: `mixed:${chId}:${topic}:sentence_reconstruction`,
    content_version: '2.0.0',
    track_id: 'cambridge',
    chapter_id: chId,
    subtopic_id: topic,
    lesson_id: chId,
    concept_ids: [`${chId}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/${chId}/${topic}`,
    kind: 'sentence_reconstruction',
    difficulty: cambridgeDiff(chId, 'sentence_reconstruction'),
    prompt,
    tokens,
    accepted_answers: accepted,
    display_answer: accepted[0],
    rationale,
  };
}

import { extraCambridgeMixedItems } from './quiz-mixed-cambridge-extra.js';

export const baseCambridgeMixedItems = [
  // cgel-ch01: Preliminaries
  cBlank('cgel-ch01', 'prescriptive-descriptive', 1, 'A _____ grammar records the forms and patterns speakers actually use rather than issuing style rankings.', ['descriptive'], 'Descriptive grammar investigates actual usage systematically without prescribing taste judgements.'),
  cBlank('cgel-ch01', 'categories-functions', 2, 'In “The letter arrived too late”, Subject is a grammatical _____, while NP is a category.', ['function'], 'Cambridge separates syntactic functions (Subject, Object) from syntactic categories (NP, VP, AdjP).'),
  cBlank('cgel-ch01', 'morphology', 3, 'Adding -ed to “walk” creates an inflectional form of the same word, whereas adding -er creates a new lexeme by lexical word-_____.', ['formation'], 'Inflection yields forms of one lexeme; word-formation derives new lexemes.'),
  cBlank('cgel-ch01', 'truth-entailment', 4, 'If sentence A cannot be true without sentence B also being true, A _____ B.', ['entails'], 'Entailment is a logical truth relation between propositions, distinct from pragmatic implicature.'),
  cBlank('cgel-ch01', 'implicature-presupposition', 5, 'Unlike strict entailment, a conversational _____ such as “not all” from “some” can be cancelled in context.', ['implicature'], 'Implicatures arise from communicative expectations and are cancellable without contradiction.'),

  cFix('cgel-ch01', 'prescriptive-descriptive', 1, 'Correct the grammatical error in this sentence to match standard plural agreement with plural count nouns.', 'Fewer people was waiting outside than yesterday.', ['Fewer people were waiting outside than yesterday.'], 'Plural noun “people” requires plural finite verb agreement (“were”).'),
  cFix('cgel-ch01', 'disagreement', 2, 'Correct the subject pronoun case in this coordinated Standard English subject.', 'Me and Kim arrived before six.', ['Kim and I arrived before six.', 'I and Kim arrived before six.'], 'A coordinated pronoun functioning as clause Subject takes nominative “I” in formal Standard English.'),
  cFix('cgel-ch01', 'categories-functions', 3, 'Correct the verb inflection error in this past-time clause.', 'The package arrive too late for the meeting.', ['The package arrived too late for the meeting.'], 'Past-time reporting with a singular third-person subject requires finite preterite “arrived”.'),
  cFix('cgel-ch01', 'morphology', 4, 'Correct the irregular inflectional form of “write”.', 'She has already wrote two chapters.', ['She has already written two chapters.'], 'Perfect auxiliary “has” requires the past participle “written”, not preterite “wrote”.'),
  cFix('cgel-ch01', 'constituent-structure', 5, 'Correct the determiner agreement with this singular count noun.', 'These book belongs to the library.', ['This book belongs to the library.', 'These books belong to the library.'], 'Singular count noun “book” selects singular demonstrative “This” (or plural “These books belong”).'),

  cRecon('cgel-ch01', 'constituent-structure', 1, ['too late', 'arrived', 'letter', 'The'], ['The letter arrived too late'], 'Orders Subject constituent “The letter” before Predicate constituent “arrived too late”.'),
  cRecon('cgel-ch01', 'categories-functions', 2, ['reports', 'carefully', 'Kim', 'the', 'checked'], ['Kim checked the reports carefully', 'Kim carefully checked the reports'], 'Subject precedes transitive verb, object NP, and manner adverb.'),
  cRecon('cgel-ch01', 'speech-writing', 3, ['in both', 'appear', 'clause', 'the same', 'patterns'], ['the same clause patterns appear in both', 'in both the same clause patterns appear'], 'Places Subject NP “the same clause patterns” before VP.'),
  cRecon('cgel-ch01', 'prescriptive-descriptive', 4, ['to', 'who', 'did', 'you', 'talk'], ['who did you talk to'], 'Orders stranded-preposition interrogative naturally in English.'),
  cRecon('cgel-ch01', 'description-theory', 5, ['must', 'simpler', 'a', 'theory', 'grammar', 'make', 'description'], ['a theory must make grammar description simpler'], 'Places Subject NP before modal VP and predicative complement.'),

  // cgel-clauses: Syntactic overview
  cBlank('cgel-clauses', 'canonical-clauses', 1, 'A _____ clause is declarative, positive, active, unmarked in polarity and word order.', ['canonical'], 'Canonical clauses serve as the baseline against which non-canonical clauses are compared.'),
  cBlank('cgel-clauses', 'verb-head', 2, 'The head of the predicate VP that selects its subject and complements is the _____.', ['verb'], 'Every clause centres on its head verb and its selected complement pattern.'),
  cBlank('cgel-clauses', 'clause-type-force', 3, '“What a clever solution that is!” exemplifies the _____ clause type.', ['exclamative'], 'Exclamative clauses open with “what” + NP or “how” + AdjP/AdvP.'),
  cBlank('cgel-clauses', 'negation-polarity', 4, 'Words such as “any” and “ever” that require negative or non-affirmative licensing are _____ polarity items.', ['negative'], 'Negative polarity items (NPIs) are licensed inside negative/interrogative environments.'),
  cBlank('cgel-clauses', 'information-packaging', 5, 'Turning “Kim opened the gate” into “The gate was opened by Kim” alters information packaging using the _____ voice.', ['passive'], 'Passive voice realigns the active Object as passive Subject.'),

  cFix('cgel-clauses', 'verb-head', 1, 'Correct the agreement error on this third-person singular canonical clause.', 'Everyone in the room know the answer.', ['Everyone in the room knows the answer.'], 'Indefinite pronoun subject “Everyone” is third-person singular and takes “knows”.'),
  cFix('cgel-clauses', 'complements', 2, 'Correct the missing required locative complement of complex-transitive “put”.', 'She put quietly the file.', ['She quietly put the file away.', 'She put the file on the desk.', 'She put the file away.', 'She put the file in the drawer.'], '“put” obligatorily selects both an Object NP and a locative/directional PP/AdvP complement.'),
  cFix('cgel-clauses', 'negation-polarity', 3, 'Correct the unlicensed negative polarity item in this positive declarative clause.', 'She has any objections to the proposal.', ['She has no objections to the proposal.', 'She does not have any objections to the proposal.', "She doesn't have any objections to the proposal."], 'NPI “any” requires negative or interrogative licensing; use “no” or negate the verb.'),
  cFix('cgel-clauses', 'clause-type-force', 4, 'Correct the punctuation/auxiliary order in this closed interrogative.', 'Does she arrived on time?', ['Did she arrive on time?', 'Does she arrive on time?'], 'Auxiliary “did/does” carries tense, so the following lexical verb must appear in plain base form “arrive”.'),
  cFix('cgel-clauses', 'coordination-supplementation', 5, 'Correct the mismatched conjunction pair in this coordinated clause.', 'Neither Kim or Pat joined the committee.', ['Neither Kim nor Pat joined the committee.', 'Either Kim or Pat joined the committee.'], 'Negative correlative “Neither” pairs with “nor” (or “Either” with “or”).'),

  cRecon('cgel-clauses', 'canonical-clauses', 1, ['friendly', 'seems', 'quite', 'Jill'], ['Jill seems quite friendly'], 'Subject NP precedes copular verb “seems” and predicative AdjP.'),
  cRecon('cgel-clauses', 'subordinate-clauses', 2, ['seems', 'that', 'Kim', 'friendly', 'thinks', 'Jill'], ['Kim thinks that Jill seems friendly'], 'Matrix clause embeds finite content clause introduced by “that”.'),
  cRecon('cgel-clauses', 'information-packaging', 3, ['was', 'by', 'written', 'report', 'Pat', 'the'], ['the report was written by Pat'], 'Passive clause places derived Subject before “was written by Pat”.'),
  cRecon('cgel-clauses', 'nonfinite-catenative', 4, ['to', 'leave', 'early', 'decided', 'Sam'], ['Sam decided to leave early', 'Sam decided early to leave'], 'Catenative verb “decided” takes to-infinitival complement.'),
  cRecon('cgel-clauses', 'deixis-anaphora', 5, ['herself', 'blamed', 'the mistake', 'Pat', 'for'], ['Pat blamed herself for the mistake'], 'Reflexive object “herself” takes local clause Subject “Pat” as antecedent.'),

  // cgel-ch03: The verb
  cBlank('cgel-ch03', 'verb-forms', 1, 'Unlike ordinary lexical verbs, English “be” has _____ distinct inflectional forms.', ['eight', '8'], 'CGEL notes “be” has 8 distinct forms (be, am, is, are, was, were, being, been).'),
  cBlank('cgel-ch03', 'modal-auxiliaries', 2, 'Modal auxiliaries such as “must” and “can” lack third-person singular -s and have no _____ forms.', ['non-finite', 'participle', 'infinitival'], 'Core modals are defective: they have finite forms only and never appear as infinitives or participles.'),
  cBlank('cgel-ch03', 'perfect', 3, 'The English perfect combines auxiliary _____ with the past participle.', ['have'], 'Perfect aspect uses “have” + past participle.'),
  cBlank('cgel-ch03', 'progressive', 4, 'Progressive aspect pairs auxiliary “be” with the _____ participle (-ing form).', ['gerund', 'present', 'gerund-participle'], 'CGEL terms the -ing form in progressives the gerund-participle.'),
  cBlank('cgel-ch03', 'mood-modality', 5, 'In “I demand that he resign immediately”, “resign” illustrates the _____ subjunctive construction.', ['mandative'], 'Mandative clauses use the plain form regardless of third-person singular subject.'),

  cFix('cgel-ch03', 'modal-auxiliaries', 1, 'Correct the illegal double-modal / modal-infinitive error.', 'She will must finish the report tonight.', ['She will have to finish the report tonight.', 'She must finish the report tonight.'], 'Modals lack non-finite forms, so two modals cannot follow one another; replace the second with “have to” or keep one modal.'),
  cFix('cgel-ch03', 'verb-forms', 2, 'Correct the irregular past participle following perfect auxiliary “have”.', 'We have already drank all the water.', ['We have already drunk all the water.'], 'After perfect “have”, the past participle of “drink” is “drunk”, not preterite “drank”.'),
  cFix('cgel-ch03', 'auxiliary-chain', 3, 'Correct the auxiliary ordering error.', 'He is having waited for an hour.', ['He has been waiting for an hour.', 'He had been waiting for an hour.'], 'Perfect “have” precedes progressive “be” (PERF -> PROG -> Lexical Verb).'),
  cFix('cgel-ch03', 'tense-time', 4, 'Correct the non-finite form following modal auxiliary “might”.', 'They might leaves early tomorrow.', ['They might leave early tomorrow.'], 'Modal auxiliaries always select a plain bare-infinitival complement (“leave”), never an -s form.'),
  cFix('cgel-ch03', 'verb-phrase', 5, 'Correct the irregular past participle form of “swim”.', 'Before noon she had swam across the bay.', ['Before noon she had swum across the bay.'], 'The past participle of “swim” is “swum”, whereas “swam” is the preterite.'),

  cRecon('cgel-ch03', 'auxiliary-chain', 1, ['been', 'novel', 'must', 'have', 'writing', 'she', 'the'], ['she must have been writing the novel'], 'Follows strict auxiliary order: Modal -> Perfect -> Progressive -> Main verb.'),
  cRecon('cgel-ch03', 'future-time', 2, ['leaves', 'train', 'the', 'at', 'six', 'tomorrow'], ['the train leaves at six tomorrow', 'tomorrow the train leaves at six'], 'Scheduled futurate uses present tense with future time adjunct.'),
  cRecon('cgel-ch03', 'perfect', 3, ['never', 'visited', 'have', 'Kyoto', 'they'], ['they have never visited Kyoto'], 'Perfect “have” precedes adverbial “never” and past participle “visited”.'),
  cRecon('cgel-ch03', 'mood-modality', 4, ['were', 'if', 'here', 'she', 'help', 'would', 'she'], ['if she were here she would help'], 'Remote conditional uses irrealis “were” in protasis and modal “would” in apodosis.'),
  cRecon('cgel-ch03', 'verb-forms', 5, ['begun', 'already', 'concert', 'had', 'the'], ['the concert had already begun'], 'Perfect auxiliary precedes adverb and past participle “begun”.'),

  // cgel-ch04: The clause: complements
  cBlank('cgel-ch04', 'objects', 1, 'In “Pat gave Kim a key”, “Kim” functions as the _____ object.', ['indirect'], 'Ditransitive “give” takes indirect object “Kim” followed by direct object “a key”.'),
  cBlank('cgel-ch04', 'predicative-complements', 2, 'Unlike an object, a _____ complement cannot normally become the subject of a corresponding passive clause.', ['predicative'], 'In “Kim became doctor/happy”, “happy” is predicative complement and does not passivise.'),
  cBlank('cgel-ch04', 'copular-clauses', 3, 'Verbs like “be”, “seem”, and “become” that take predicative complements are called _____ verbs.', ['copular', 'linking'], 'Copular verbs link a subject (or object) to a predicative property/role.'),
  cBlank('cgel-ch04', 'particles-idioms', 4, 'When the object is an unstressed pronoun (“it”), a phrasal verb particle must come _____ the pronoun.', ['after', 'following'], '“She turned it off” is grammatical, whereas *“She turned off it” is ungrammatical.'),
  cBlank('cgel-ch04', 'semantic-roles', 5, 'In “The wind broke the branch”, “the wind” carries the semantic role of causer or force rather than volitional _____.', ['agent'], 'Agents act volitionally; inanimate causes serve as causer/force/instrument.'),

  cFix('cgel-ch04', 'particles-idioms', 1, 'Correct the position of the phrasal verb particle with this pronoun object.', 'She looked up it in the index.', ['She looked it up in the index.'], 'With an unstressed pronoun object “it”, particle “up” cannot precede the pronoun.'),
  cFix('cgel-ch04', 'copular-clauses', 2, 'Correct the erroneous adverb where a copular predicative adjective is required.', 'The soup tastes wonderfully tonight.', ['The soup tastes wonderful tonight.'], 'Copular “taste” selects a predicative AdjP complement (“wonderful”), not manner adverb “wonderfully”.'),
  cFix('cgel-ch04', 'prepositional-verbs', 3, 'Correct the missing specified preposition required by “depend”.', 'Our plans depend the weather.', ['Our plans depend on the weather.', 'Our plans depend upon the weather.'], 'Prepositional verb “depend” obligatorily selects a PP headed by “on/upon”.'),
  cFix('cgel-ch04', 'subject', 4, 'Correct the subject-verb agreement across the intervening PP modifier.', 'The list of new rules were posted yesterday.', ['The list of new rules was posted yesterday.'], 'The head of the Subject NP is singular “list”, requiring singular “was”.'),
  cFix('cgel-ch04', 'clause-patterns', 5, 'Correct the ungrammatical passive of an intransitive verb.', 'An accident was happened near the bridge.', ['An accident happened near the bridge.'], 'Intransitive “happen” has no object and cannot passivise.'),

  cRecon('cgel-ch04', 'clause-patterns', 1, ['appointed', 'chair', 'board', 'the', 'Mira'], ['the board appointed Mira chair'], 'Complex-transitive verb “appointed” takes Object NP + Object-Predicative NP.'),
  cRecon('cgel-ch04', 'objects', 2, ['the', 'sent', 'journal', 'she', 'a', 'manuscript'], ['she sent the journal a manuscript'], 'Ditransitive order places Indirect Object before Direct Object.'),
  cRecon('cgel-ch04', 'prepositional-verbs', 3, ['rely', 'his', 'always', 'can', 'friends', 'he', 'on'], ['he can always rely on his friends'], 'Modal + adverb precede prepositional verb “rely” + PP “on his friends”.'),
  cRecon('cgel-ch04', 'light-verbs', 4, ['a', 'took', 'quiet', 'walk', 'we', 'along', 'river', 'the'], ['we took a quiet walk along the river'], 'Light verb “took” combines with eventive noun complement “a quiet walk”.'),
  cRecon('cgel-ch04', 'predicative-complements', 5, ['painted', 'bright', 'door', 'the', 'green', 'they'], ['they painted the door bright green'], 'Resultative complex-transitive clause places AdjP “bright green” after direct object.'),

  // cgel-ch05: Nouns and noun phrases
  cBlank('cgel-ch05', 'number-countability', 1, 'Non-count nouns such as “information” and “furniture” take “much” or “little” rather than _____.', ['many', 'few'], '“many” and “few” require plural count nouns, whereas “much”/“little” combine with singular non-count nouns.'),
  cBlank('cgel-ch05', 'case', 2, 'A pronoun serving as complement to a preposition (“between you and _____”) takes accusative case.', ['me'], 'Prepositional complements require accusative “me” rather than nominative “I”.'),
  cBlank('cgel-ch05', 'genitives', 3, 'In “my sister’s coat”, “my sister’s” functions as _____ determiner inside the larger NP.', ['subject', 'determiner', 'possessive'], 'Genitive NPs fill the Determiner slot of the matrix noun phrase.'),
  cBlank('cgel-ch05', 'fused-heads', 4, 'In “Many arrived early”, determinative “Many” serves as a _____ head combining determiner and nominal head.', ['fused'], 'Fused-head constructions unite the determiner and head noun roles in one word.'),
  cBlank('cgel-ch05', 'subject-verb-agreement', 5, 'Collective nouns such as “committee” permit singular or plural agreement depending on unified body versus _____ reading.', ['individual', 'members', 'distributed'], 'British English often allows plural override when thinking of individual members.'),

  cFix('cgel-ch05', 'number-countability', 1, 'Correct the count/non-count noun error.', 'She gave me many helpful advices before the trip.', ['She gave me much helpful advice before the trip.', 'She gave me some helpful advice before the trip.', 'She gave me a lot of helpful advice before the trip.'], '“advice” is a non-count noun; it cannot pluralise to *“advices” or take “many”.'),
  cFix('cgel-ch05', 'case', 2, 'Correct the pronoun case error inside the prepositional phrase.', 'Wait between Pat and I after class.', ['Wait between Pat and me after class.'], 'As complement of preposition “between”, use accusative “me”.'),
  cFix('cgel-ch05', 'np-order', 3, 'Correct the determinative-modifier ordering inside this noun phrase.', 'All the students five signed the roster.', ['All five of the students signed the roster.', 'The five students all signed the roster.', 'All five students signed the roster.'], 'Cardinal numerals precede the head noun (after predeterminers/articles), never following the noun here.'),
  cFix('cgel-ch05', 'genitives', 4, 'Correct the possessive pronoun/determiner confusion.', 'The company changed it’s policy last spring.', ["The company changed its policy last spring."], 'The possessive determiner “its” has no apostrophe; “it’s” contracts “it is/has”.'),
  cFix('cgel-ch05', 'subject-verb-agreement', 5, 'Correct the number agreement error with “Each of the essays”.', 'Each of the essays were carefully graded.', ['Each of the essays was carefully graded.'], 'Fused-head Subject “Each” is grammatically singular, requiring “was”.'),

  cRecon('cgel-ch05', 'np-order', 1, ['three', 'first', 'the', 'chapters', 'unread', 'remained'], ['the first three chapters remained unread'], 'Determiner + ordinal + cardinal + head noun order in NP.'),
  cRecon('cgel-ch05', 'case', 2, ['shared', 'she', 'and', 'I', 'office', 'an'], ['she and I shared an office', 'I and she shared an office'], 'Coordinated Subject takes nominative pronouns before verb.'),
  cRecon('cgel-ch05', 'internal-dependents', 3, ['blue', 'large', 'wooden', 'a', 'box'], ['a large blue wooden box'], 'Pre-head modifiers follow size -> colour -> material -> head noun order.'),
  cRecon('cgel-ch05', 'quantification', 4, ['neither', 'of', 'the', 'answers', 'is', 'clear'], ['neither of the answers is clear'], 'Quantificational pronoun “neither” takes plural “of”-NP with singular verb.'),
  cRecon('cgel-ch05', 'genitives', 5, ['report', 'yesterday’s', 'surprised', 'everyone'], ['yesterday’s report surprised everyone'], 'Temporal genitive “yesterday’s” functions as determiner of “report”.'),

  // cgel-ch06: Adjectives and adverbs
  cBlank('cgel-ch06', 'restricted-adjectives', 1, 'Adjectives such as “asleep” and “afraid” are restricted to _____ position and cannot precede a noun.', ['predicative'], '“the child is asleep” is well-formed, whereas *“an asleep child” is ungrammatical.'),
  cBlank('cgel-ch06', 'restricted-adjectives', 2, 'Adjectives like “mere” and “utter” are restricted to _____ position inside an NP.', ['attributive'], '“a mere detail” is attributive-only; *“the detail is mere” is ungrammatical.'),
  cBlank('cgel-ch06', 'category-boundaries', 3, 'Unlike nouns, typical gradable adjectives accept modification by degree adverb _____.', ['very'], 'Modifiability by “very” / “too” distinguishes gradable adjectives/adverbs from nouns.'),
  cBlank('cgel-ch06', 'focusing-adverbs', 4, 'Adverbs like “only”, “even”, and “just” highlight one constituent in their _____ of focus.', ['scope'], 'The interpretation of focusing adverbs depends on which constituent they associate with.'),
  cBlank('cgel-ch06', 'adjp-complementation', 5, 'In “fond of music”, “of music” is a prepositional _____ licensed by the adjective “fond”.', ['complement'], 'Adjectives such as “fond”, “aware”, and “proud” license obligatory or characteristic PP complements.'),

  cFix('cgel-ch06', 'restricted-adjectives', 1, 'Correct the attributive misuse of predicative-only adjective “asleep”.', 'We tiptoed past the asleep baby.', ['We tiptoed past the sleeping baby.', 'We tiptoed past the baby who was asleep.'], '“asleep” is restricted to predicative position; replace it attributively with “sleeping” or use a relative clause.'),
  cFix('cgel-ch06', 'criterial-properties', 2, 'Correct the missing adverb form modifying a lexical verb.', 'She spoke very quiet during the ceremony.', ['She spoke very quietly during the ceremony.'], 'Manner modification of verb “spoke” requires adverb “quietly”, not adjective “quiet”.'),
  cFix('cgel-ch06', 'adverb-position', 3, 'Correct the misplaced focusing/degree modifier “very” before a finite verb.', 'He very enjoyed the concert.', ['He very much enjoyed the concert.', 'He enjoyed the concert very much.', 'He really enjoyed the concert.'], '“very” cannot directly modify finite verbs; use “very much” or “really”.'),
  cFix('cgel-ch06', 'adjp-complementation', 4, 'Correct the preposition selected by adjective “afraid”.', 'The hikers were afraid from the storm.', ['The hikers were afraid of the storm.'], '“afraid” governs prepositional complement headed by “of”, not “from”.'),
  cFix('cgel-ch06', 'adjp-modification', 5, 'Correct the adjective placement modifying an indefinite pronoun.', 'We saw strange something in the sky.', ['We saw something strange in the sky.'], 'Postpositive adjectives follow compound indefinite pronouns such as “something”.'),

  cRecon('cgel-ch06', 'adjp-modification', 1, ['interesting', 'found', 'something', 'they'], ['they found something interesting'], 'Adjective “interesting” follows indefinite pronoun “something”.'),
  cRecon('cgel-ch06', 'adverb-position', 2, ['clearly', 'explained', 'point', 'the', 'she'], ['she explained the point clearly', 'she clearly explained the point'], 'Manner adverb fits naturally at clause-end or pre-verbally.'),
  cRecon('cgel-ch06', 'restricted-adjectives', 3, ['remained', 'awake', 'children', 'the'], ['the children remained awake'], 'Predicative-only adjective “awake” follows copular verb “remained”.'),
  cRecon('cgel-ch06', 'focusing-adverbs', 4, ['read', 'only', 'two', 'Kim', 'chapters'], ['Kim read only two chapters', 'only Kim read two chapters'], 'Focusing adverb “only” precedes its focused constituent.'),
  cRecon('cgel-ch06', 'adjp-complementation', 5, ['result', 'the', 'with', 'pleased', 'very', 'was', 'Kim'], ['Kim was very pleased with the result'], 'Copula precedes degree-modified AdjP and its PP complement.'),

  // cgel-ch07: Prepositions and preposition phrases
  cBlank('cgel-ch07', 'pp-complementation', 1, 'Cambridge treats “because”, “before”, and “although” as _____ that take finite clause complements rather than conjunctions.', ['prepositions'], 'CGEL widens preposition category to include words taking clausal complements (formerly subordinating conjunctions).'),
  cBlank('cgel-ch07', 'stranding-order', 2, 'Leaving “in” at the end of “the town which he lives in” illustrates preposition _____.', ['stranding'], 'Preposition stranding separates the complement wh-phrase from the preposition.'),
  cBlank('cgel-ch07', 'stranding-order', 3, 'Moving “in” with its complement (“the town in which he lives”) is called _____ fronting.', ['pied-piping', 'pied piping'], 'Pied-piping fronts the entire PP to keep P and its complement adjacent.'),
  cBlank('cgel-ch07', 'grammaticised', 4, 'When “insist” requires “on” without spatial meaning, “on” functions as a _____ preposition.', ['grammaticised', 'grammaticized', 'specified'], 'Grammaticised uses select a specific preposition by lexical government rather than independent meaning.'),
  cBlank('cgel-ch07', 'pp-complementation', 5, 'Words like “upstairs” and “outdoors” are prepositions taking _____ overt complement.', ['no', 'zero'], 'CGEL classifies intransitive spatial words like “inside”/“upstairs” as complementless prepositions.'),

  cFix('cgel-ch07', 'pp-complementation', 1, 'Correct the pronoun case following preposition “for”.', 'This parcel is addressed to Sam and I.', ['This parcel is addressed to Sam and me.'], 'Complements of prepositions take accusative pronoun case (“me”).'),
  cFix('cgel-ch07', 'grammaticised', 2, 'Correct the wrongly selected preposition after “congratulate”.', 'They congratulated Mira for winning the prize.', ['They congratulated Mira on winning the prize.', 'They congratulated Mira upon winning the prize.'], '“congratulate” governs “on” (or “upon”), not “for”.'),
  cFix('cgel-ch07', 'stranding-order', 3, 'Correct the doubled preposition in this relative clause.', 'That is the house in which I grew up in.', ['That is the house in which I grew up.', 'That is the house which I grew up in.', 'That is the house that I grew up in.'], 'Use either pied-piping (“in which ...”) OR stranding (“which ... in”), never both simultaneously.'),
  cFix('cgel-ch07', 'category-contrasts', 4, 'Correct the confusion between preposition “despite” and “in spite of”.', 'Despite of the heavy rain, they walked home.', ['Despite the heavy rain, they walked home.', 'In spite of the heavy rain, they walked home.'], '“Despite” takes a direct NP complement without “of”; “in spite” takes “of”.'),
  cFix('cgel-ch07', 'pp-functions', 5, 'Correct the missing preposition required with “wait” before its NP target.', 'Wait the bus at the second stop.', ['Wait for the bus at the second stop.'], '“wait” in this sense takes prepositional complement “for the bus”.'),

  cRecon('cgel-ch07', 'stranding-order', 1, ['in', 'lives', 'house', 'which', 'the', 'she'], ['the house in which she lives', 'the house which she lives in'], 'Relative PP may pied-pipe (“in which”) or strand “in” at clause end.'),
  cRecon('cgel-ch07', 'pp-modification', 2, ['the', 'straight', 'road', 'down', 'ran', 'they'], ['they ran straight down the road'], 'Adv “straight” modifies preposition phrase “down the road”.'),
  cRecon('cgel-ch07', 'pp-complementation', 3, ['despite', 'finished', 'delay', 'early', 'the', 'she'], ['she finished early despite the delay', 'despite the delay she finished early'], 'Concessive PP sits comfortably at clause end or front.'),
  cRecon('cgel-ch07', 'space-time', 4, ['under', 'sat', 'shade', 'the', 'bridge', 'in', 'they', 'the'], ['they sat in the shade under the bridge', 'in the shade under the bridge they sat'], 'Locative PPs specify nested or sequential spatial locations.'),
  cRecon('cgel-ch07', 'grammaticised', 5, ['depends', 'timing', 'success', 'careful', 'on'], ['success depends on careful timing'], 'Verb “depends” selects PP complement headed by “on”.'),

  // cgel-ch08: The clause: adjuncts
  cBlank('cgel-ch08', 'conditionals-remote', 1, 'In “If he had left earlier, he would have caught the train”, the condition is _____ (counterfactual/remote) rather than open.', ['remote'], 'CGEL contrasts open conditionals (present/future real possibility) with remote conditionals (past backshifted modals).'),
  cBlank('cgel-ch08', 'concession', 2, 'Adverbs/prepositions like “although” and “even though” introduce adjuncts of _____.', ['concession'], 'Concessive adjuncts mark a contrast against an expected outcome.'),
  cBlank('cgel-ch08', 'domain-modality', 3, 'In “Financially, the plan is sound”, “Financially” acts as a _____ adjunct limiting the viewpoint.', ['domain'], 'Domain adjuncts specify the perspective/field within which the predicate holds.'),
  cBlank('cgel-ch08', 'evaluation-speech-connective', 4, 'An adverb like “Frankly” in “Frankly, I disagree” is a _____ -act adjunct commenting on the utterance itself.', ['speech'], 'Speech-act adjuncts qualify why or how the speaker makes the assertion.'),
  cBlank('cgel-ch08', 'manner-means-instrument', 5, 'In “She opened the crate with a crowbar”, “with a crowbar” indicates _____.', ['instrument'], '“with + tool NP” expresses instrument adjuncts, distinct from manner or accompaniment.'),

  cFix('cgel-ch08', 'conditionals-remote', 1, 'Correct the verb/modal mismatch in this remote counterfactual conditional.', 'If she would have known earlier, she would call you.', ['If she had known earlier, she would have called you.', 'If she had known earlier, she would call you.'], 'Remote conditional protasis (“if”-clause) takes past perfect “had known”, not modal “would have”.'),
  cFix('cgel-ch08', 'concession', 2, 'Correct the redundant coordinator “but” following concessive “Although”.', 'Although the road was icy, but he drove fast.', ['Although the road was icy, he drove fast.', 'The road was icy, but he drove fast.'], 'English does not pair subordinator “Although” with coordinator “but” in the same two-clause link.'),
  cFix('cgel-ch08', 'cause-result', 3, 'Correct the missing preposition after “because” before a noun phrase.', 'The match stopped because the heavy storm.', ['The match stopped because of the heavy storm.', 'The match stopped because the heavy storm arrived.'], '“because” takes a clausal complement; before an NP use “because of”.'),
  cFix('cgel-ch08', 'time-duration', 4, 'Correct the confusion between “during” (NP period) and “while” (clause).', 'I read two chapters during she was cooking.', ['I read two chapters while she was cooking.', 'I read two chapters during the evening.'], '“during” takes an NP, whereas finite clause “she was cooking” requires “while”.'),
  cFix('cgel-ch08', 'position', 5, 'Correct the ungrammatical adverb placement between transitive verb and short direct object.', 'He closed carefully the envelope.', ['He carefully closed the envelope.', 'He closed the envelope carefully.'], 'In English, manner adverbs normally precede the verb or follow its short object NP, not sitting between V and short object.'),

  cRecon('cgel-ch08', 'manner-means-instrument', 1, ['key', 'a', 'opened', 'with', 'she', 'the', 'door'], ['she opened the door with a key'], 'Object precedes instrument PP “with a key”.'),
  cRecon('cgel-ch08', 'conditionals-open', 2, ['rains', 'stay', 'inside', 'it', 'will', 'we', 'if'], ['if it rains we will stay inside', 'we will stay inside if it rains'], 'Open conditional protasis may precede or follow main clause.'),
  cRecon('cgel-ch08', 'evaluation-speech-connective', 3, ['luckily', 'arrived', 'bus', 'on', 'time', 'the'], ['luckily the bus arrived on time', 'the bus luckily arrived on time'], 'Evaluative adjunct “luckily” sits cleanly in initial or pre-VP position.'),
  cRecon('cgel-ch08', 'frequency-degree', 4, ['seldom', 'arrives', 'after', 'dark', 'Mira'], ['Mira seldom arrives after dark'], 'Pre-verbal frequency adverb precedes simple finite verb.'),
  cRecon('cgel-ch08', 'cause-result', 5, ['delayed', 'was', 'train', 'the', 'fog', 'because of'], ['the train was delayed because of fog', 'because of fog the train was delayed'], 'Causal PP “because of fog” appears initially or finally.'),

  // cgel-ch09: Negation
  cBlank('cgel-ch09', 'verbal-negation', 1, 'Standard verbal negation inserts “not” after the primary or modal _____, using “do” if none is present.', ['auxiliary'], 'Verbal negation attaches to/follows the tensed auxiliary.'),
  cBlank('cgel-ch09', 'nonverbal-negation', 2, 'In “No student complained”, negation is marked inside the NP rather than on the verb, called _____ negation.', ['non-verbal', 'nonverbal'], '“no/nothing/nobody/never” realize non-verbal negation on a dependent rather than verbal “not”.'),
  cBlank('cgel-ch09', 'npis', 3, 'Positive polarity item “already” normally shifts to negative polarity item _____ under negation.', ['yet'], '“Has she arrived yet?” / “She hasn’t arrived yet.” replaces PPI “already” with NPI “yet”.'),
  cBlank('cgel-ch09', 'approximate-affixal', 4, 'Words like “hardly” and “seldom” express _____ negation and still license NPIs like “any” and “ever”.', ['approximate'], 'Approximate negators convey near-zero quantity/frequency and trigger negative inversion & NPIs.'),
  cBlank('cgel-ch09', 'polarity-tests', 5, 'Confirming negation using a positive tag (“... doesn’t she?” vs “... does she?”) tests clause _____.', ['polarity'], 'Reversed-polarity tags flip positive after negative clauses and negative after positive clauses.'),

  cFix('cgel-ch09', 'verbal-negation', 1, 'Correct the missing dummy auxiliary “do” in this negated lexical verb clause.', 'She not finished the assignment on time.', ['She did not finish the assignment on time.', "She didn't finish the assignment on time."], 'Non-auxiliary finite lexical verbs require do-support (“did not finish”) for verbal negation.'),
  cFix('cgel-ch09', 'npis', 2, 'Correct the mismatched negative polarity item in this positive statement.', 'We found ever a better route through town.', ['We never found a better route through town.', 'We did not ever find a better route through town.', 'We have never found a better route through town.', 'We found a better route through town.'], 'NPI “ever” requires a negative/non-affirmative licensor such as “never” or verbal negation (or remove it).'),
  cFix('cgel-ch09', 'approximate-affixal', 3, 'Correct the polarity conflict between approximate negator “hardly” and “no”.', 'He could hardly see no landmarks in the mist.', ['He could hardly see any landmarks in the mist.', 'He could see no landmarks in the mist.'], 'Because “hardly” is already negative, pair it with NPI “any” rather than double negative “no” in Standard English.'),
  cFix('cgel-ch09', 'scope-focus', 4, 'Correct the missing subject-auxiliary inversion after fronted negative adverb “Never”.', 'Never I have seen such a clear diagram.', ['Never have I seen such a clear diagram.'], 'Fronting a negative constituent (“Never”, “Seldom”) triggers subject-auxiliary inversion.'),
  cFix('cgel-ch09', 'polarity-tests', 5, 'Correct the question tag polarity on this negative clause.', 'She hasn’t signed the form, hasn’t she?', ["She hasn't signed the form, has she?", 'She has signed the form, hasn’t she?'], 'Negative declarative takes an opposite-polarity positive question tag (“has she?”).'),

  cRecon('cgel-ch09', 'scope-focus', 1, ['seen', 'have', 'never', 'I', 'mistake', 'such a'], ['never have I seen such a mistake', 'I have never seen such a mistake'], 'Fronted “never” triggers inversion (“have I”); medial “never” follows auxiliary.'),
  cRecon('cgel-ch09', 'verbal-negation', 2, ['did', 'arrive', 'not', 'they', 'until', 'noon'], ['they did not arrive until noon'], 'Do-support auxiliary precedes “not” and plain infinitive “arrive”.'),
  cRecon('cgel-ch09', 'approximate-affixal', 3, ['said', 'anyone', 'hardly', 'word', 'a'], ['hardly anyone said a word'], 'Approximate negator “hardly” modifies indefinite “anyone” in Subject.'),
  cRecon('cgel-ch09', 'nonverbal-negation', 4, ['none', 'of', 'the', 'papers', 'remained'], ['none of the papers remained'], 'Non-verbal negative head “none” takes partitive PP before verb.'),
  cRecon('cgel-ch09', 'npis', 5, ['has', 'called', 'yet', 'nobody'], ['nobody has called yet'], 'Negative subject licenses NPI “yet” at end of clause.'),

  // cgel-ch10: Clause type and illocutionary force
  cBlank('cgel-ch10', 'kinds-questions', 1, 'A question inviting an open answer using a word like “who” or “where” is an _____ interrogative.', ['open'], 'Open interrogatives have an open set of answers, unlike polar closed interrogatives.'),
  cBlank('cgel-ch10', 'polar-alternative', 2, '“Would you like tea or coffee?” (requiring choosing one option rather than yes/no) is an _____ question.', ['alternative'], 'Alternative questions use “or” between specified candidate answers.'),
  cBlank('cgel-ch10', 'exclamatives', 3, 'Exclamative clauses begin either with “what” followed by an NP or “_____” followed by an AdjP/AdvP.', ['how'], '“What a nice day!” uses “what + NP”; “How fast she ran!” uses “how + AdjP/AdvP”.'),
  cBlank('cgel-ch10', 'imperatives-directives', 4, 'Positive imperatives normally lack an overt subject and take the verb in its _____ form.', ['plain', 'base'], 'Imperatives use the plain/base verb form (“Be quiet”, not *“Are quiet”).'),
  cBlank('cgel-ch10', 'indirect-speech-acts', 5, 'Using interrogative “Could you pass the salt?” to make a request is an _____ speech act.', ['indirect'], 'Clause type (interrogative) and illocutionary force (directive request) do not always coincide one-to-one.'),

  cFix('cgel-ch10', 'exclamatives', 1, 'Correct the subject-auxiliary inversion error in this exclamative clause.', 'How fast did she solve the puzzle!', ['How fast she solved the puzzle!'], 'Unlike wh-interrogatives, exclamatives retain non-inverted Subject + Verb order.'),
  cFix('cgel-ch10', 'declarative-interrogative', 2, 'Correct the missing subject-auxiliary inversion in this formal main open interrogative.', 'Where you did leave the keys?', ['Where did you leave the keys?'], 'Main wh-interrogatives invert auxiliary “did” before Subject “you”.'),
  cFix('cgel-ch10', 'imperatives-directives', 3, 'Correct the negative imperative form.', 'Not leave the door unlocked!', ["Do not leave the door unlocked!", "Don't leave the door unlocked!"], 'Negative imperatives obligatorily use “do not / don’t”, even with “be” (“Don’t be late”).'),
  cFix('cgel-ch10', 'exclamatives', 4, 'Correct the exclamative word choice (“what” vs “how”) before a singular count NP.', 'How a wonderful idea that is!', ['What a wonderful idea that is!'], 'NP exclamatives require “what” (“What a wonderful idea!”), while “how” modifies AdjP/AdvP (“How wonderful!”).'),
  cFix('cgel-ch10', 'tags-parentheticals', 5, 'Correct the pronoun/auxiliary in this imperative tag.', 'Open the window, don’t you?', ['Open the window, will you?', "Open the window, won't you?", 'Open the window, could you?', 'Open the window, can you?'], 'Directive imperatives typically take future/modal tags (“will you / won’t you”), not present “don’t you”.'),

  cRecon('cgel-ch10', 'exclamatives', 1, ['is', 'how', 'clear', 'this', 'explanation'], ['how clear this explanation is'], 'Exclamative fronts “how clear” before non-inverted Subject + copula.'),
  cRecon('cgel-ch10', 'polar-alternative', 2, ['prefer', 'tea', 'coffee', 'do', 'you', 'or'], ['do you prefer tea or coffee', 'do you prefer coffee or tea'], 'Closed/alternative question puts auxiliary “do” before Subject.'),
  cRecon('cgel-ch10', 'imperatives-directives', 3, ['be', 'don’t', 'late', 'tomorrow'], ["don't be late tomorrow"], 'Negative imperative uses “don’t” before plain “be”.'),
  cRecon('cgel-ch10', 'tags-parentheticals', 4, ['arrived', 'didn’t', 'early,', 'she', 'she'], ["she arrived early, didn't she"], 'Positive declarative takes opposite-polarity negative question tag.'),
  cRecon('cgel-ch10', 'indirect-speech-acts', 5, ['window', 'close', 'could', 'you', 'the'], ['could you close the window'], 'Modal interrogative politely conveys a directive request.'),

  // cgel-ch11: Content clauses and reported speech
  cBlank('cgel-ch11', 'that-omission', 1, 'Unlike object content clauses (“I know [that] she left”), a subject content clause before the verb requires overt _____.', ['that'], 'Clause-initial subject content clauses (“That she left surprised us”) cannot omit “that”.'),
  cBlank('cgel-ch11', 'interrogative-content', 2, 'A subordinate closed interrogative content clause is introduced by “whether” or _____.', ['if'], '“She asked whether/if he agreed” marks subordinate closed interrogatives.'),
  cBlank('cgel-ch11', 'mood-factivity', 3, 'Verbs like “insist” and “recommend” can govern a mandative content clause taking the _____ verb form.', ['plain', 'base', 'subjunctive'], 'Mandative content clauses take the plain verb form (“insist that she stay”).'),
  cBlank('cgel-ch11', 'functions-subject', 4, 'Moving a heavy subject content clause to the end with dummy “it” is called _____.', ['extraposition'], '“It is obvious that she knows” is the extraposed counterpart of “That she knows is obvious”.'),
  cBlank('cgel-ch11', 'reported-speech-indirect', 5, 'Shifting “I am ready” under past reporting verb “He said he was ready” is called _____.', ['backshift'], 'Indirect reported speech often shifts present to preterite under a past reporting verb.'),

  cFix('cgel-ch11', 'that-omission', 1, 'Correct the illegal omission of “that” at the beginning of a subject content clause.', 'She passed the exam surprised everyone.', ['That she passed the exam surprised everyone.', 'The fact that she passed the exam surprised everyone.', 'It surprised everyone that she passed the exam.'], 'A finite subject content clause in pre-verbal position requires subordinator “That”.'),
  cFix('cgel-ch11', 'interrogative-constructions', 2, 'Correct the improper subject-auxiliary inversion inside this subordinate interrogative.', 'I asked him where did he put the notebook.', ['I asked him where he put the notebook.', 'I asked him where he had put the notebook.'], 'Subordinate interrogative content clauses keep non-inverted declarative Subject + Verb order.'),
  cFix('cgel-ch11', 'interrogative-content', 3, 'Correct “if” vs “whether” inside a clause directly followed by “or not”.', 'She is uncertain if or not the train arrived.', ['She is uncertain whether or not the train arrived.', 'She is uncertain whether the train arrived or not.', 'She is uncertain if the train arrived or not.'], 'Before immediate “or not”, only “whether” (not *“if or not”) is grammatical.'),
  cFix('cgel-ch11', 'mood-factivity', 4, 'Correct the verb agreement inside this mandative content clause.', 'The rules require that every candidate submits two drafts.', ['The rules require that every candidate submit two drafts.', 'The rules require that every candidate should submit two drafts.'], 'Mandative complements take plain subjunctive “submit” (or “should submit”), not indicative *-s in formal mandatives.'),
  cFix('cgel-ch11', 'functions-complements', 5, 'Correct the missing preposition before a wh-interrogative vs illegal “that” directly after a preposition.', 'We talked about that he left early.', ['We talked about the fact that he left early.', 'We talked about his leaving early.'], 'Ordinary prepositions like “about” cannot take a finite declarative “that”-clause directly.'),

  cRecon('cgel-ch11', 'that-declaratives', 1, ['believed', 'that', 'everyone', 'correct', 'answer', 'the', 'was'], ['everyone believed that the answer was correct'], 'Matrix subject + verb precede finite “that” content clause.'),
  cRecon('cgel-ch11', 'functions-subject', 2, ['it', 'useful', 'notes', 'is', 'took', 'she', 'that'], ['it is useful that she took notes'], 'Extraposed structure uses dummy “it” + copula + AdjP + “that”-clause.'),
  cRecon('cgel-ch11', 'interrogative-constructions', 3, ['wonder', 'where', 'went', 'they', 'I'], ['I wonder where they went'], 'Embedded wh-interrogative keeps non-inverted Subject + Verb order.'),
  cRecon('cgel-ch11', 'reported-speech-indirect', 4, ['arrived', 'said', 'had', 'already', 'Kim', 'she'], ['Kim said she had already arrived', 'she said Kim had already arrived'], 'Indirect report embeds backshifted past-perfect content clause.'),
  cRecon('cgel-ch11', 'mood-factivity', 5, ['be', 'recommended', 'that', 'revised', 'they', 'plan', 'the'], ['they recommended that the plan be revised'], 'Mandative complement takes plain “be” before passive participle.'),

  // cgel-ch12: Relative constructions and unbounded dependencies
  cBlank('cgel-ch12', 'integrated-relatives', 1, 'A relative clause tightly integrated into an NP to identify its referent without commas is an _____ relative.', ['integrated'], 'CGEL distinguishes integrated (restrictive) relatives from supplementary (non-restrictive) ones.'),
  cBlank('cgel-ch12', 'supplementary-relatives', 2, 'Unlike integrated relatives, _____ (comma-separated) relatives cannot normally be introduced by “that”.', ['supplementary'], 'Supplementary relatives require wh-words (“who”, “which”) rather than “that”.'),
  cBlank('cgel-ch12', 'relativisation-gaps', 3, 'When a relative pronoun stands for a non-subject element, the clause contains a missing position or _____.', ['gap'], 'In “the letter which I read _”, the object of “read” is realized as a relativised gap.'),
  cBlank('cgel-ch12', 'fused-relatives', 4, 'In “What you said surprised me”, “What” combines antecedent and relative pronoun in a _____ relative.', ['fused'], 'Fused relatives (“what”, “whoever”) merge the NP head with the relativised element.'),
  cBlank('cgel-ch12', 'relative-phrases', 5, 'Use relative _____ for human antecedents and “which” for non-human antecedents in standard wh-relatives.', ['who', 'whom'], '“who/whom” selects personal/human antecedents while “which” selects non-personal antecedents.'),

  cFix('cgel-ch12', 'relativisation-gaps', 1, 'Correct the illegal resumptive pronoun inside this relative clause.', 'Here is the book that I borrowed it yesterday.', ['Here is the book that I borrowed yesterday.', 'Here is the book which I borrowed yesterday.', 'Here is the book I borrowed yesterday.'], 'The relativised object position inside a relative clause must remain a gap, never filled by resumptive “it”.'),
  cFix('cgel-ch12', 'supplementary-relatives', 2, 'Correct the invalid use of “that” in a supplementary non-restrictive relative clause.', 'Her brother, that lives in Oslo, called today.', ['Her brother, who lives in Oslo, called today.'], 'Supplementary relative clauses marked off by commas require “who/which”, not “that”.'),
  cFix('cgel-ch12', 'relative-phrases', 3, 'Correct the mismatched human/non-human relative pronoun.', 'The linguist which wrote this article retired.', ['The linguist who wrote this article retired.', 'The linguist that wrote this article retired.'], 'Human antecedent “The linguist” requires “who” (or integrated “that”), never “which”.'),
  cFix('cgel-ch12', 'fused-relatives', 4, 'Correct the erroneous “what” used as an ordinary relative pronoun with an overt head noun.', 'The essay what she submitted won a prize.', ['The essay that she submitted won a prize.', 'The essay which she submitted won a prize.', 'The essay she submitted won a prize.'], 'With an explicit antecedent noun (“The essay”), use “that/which” (or bare relative); “what” is fused-only.'),
  cFix('cgel-ch12', 'relative-position', 5, 'Correct the agreement error in the verb of a subject relative clause.', 'Students who finishes early may leave.', ['Students who finish early may leave.'], 'Plural antecedent “Students” determines plural verb “finish” inside the relative clause.'),

  cRecon('cgel-ch12', 'integrated-relatives', 1, ['yesterday', 'wrote', 'poem', 'that', 'I', 'the', 'memorised', 'she'], ['I memorised the poem that she wrote yesterday'], 'Integrated relative clause modifies “the poem” inside direct object NP.'),
  cRecon('cgel-ch12', 'supplementary-relatives', 2, ['in', 'built', 'which', 'was', '1920,', 'tower,', 'the', 'reopened'], ['the tower, which was built in 1920, reopened'], 'Supplementary relative sits inside paired commas after antecedent.'),
  cRecon('cgel-ch12', 'fused-relatives', 3, ['happened', 'everyone', 'what', 'surprised'], ['what happened surprised everyone'], 'Fused relative Subject “what happened” precedes main verb.'),
  cRecon('cgel-ch12', 'infinitival-relatives', 4, ['to', 'read', 'a', 'book', 'quietly', 'found', 'she'], ['she found a book to read quietly'], 'Infinitival relative “to read quietly” modifies NP “a book”.'),
  cRecon('cgel-ch12', 'unbounded-dependencies', 5, ['report', 'the', 'think', 'you', 'wrote', 'who', 'did'], ['who did you think wrote the report'], 'Long-distance wh-dependency extracts subject across “think”.'),

  // cgel-ch13: Comparative constructions
  cBlank('cgel-ch13', 'scalar-inequality', 1, 'Comparisons of inequality use inflectional -er/-est or analytic “more/most” together with preposition _____.', ['than'], 'Scalar inequality uses “than” (“taller than”, “more useful than”).'),
  cBlank('cgel-ch13', 'scalar-equality', 2, 'Scalar comparisons of equality pair “as ... _____” (e.g. “as tall as Kim”).', ['as'], 'Equality modifiers use correlative “as” + gradable word + comparative “as”-phrase.'),
  cBlank('cgel-ch13', 'scalar-non-scalar', 3, 'Unlike “taller”, “the same height as” expresses _____ comparison without degrees along a scale.', ['non-scalar'], 'Non-scalar comparison compares identity/likeness rather than relative degree.'),
  cBlank('cgel-ch13', 'set-comparison', 4, 'Comparing one member against a whole reference set uses a _____ grade (-est / most).', ['superlative'], 'Superlatives compare against an entire comparison set rather than a single standard.'),
  cBlank('cgel-ch13', 'as-like-unlike', 5, 'Unlike “like” + NP, preposition _____ introduces a role or capacity (“working as an editor”).', ['as'], '“as” marks role/capacity whereas “like” marks similarity.'),

  cFix('cgel-ch13', 'scalar-inequality', 1, 'Correct the double comparative inflection + analytic marking.', 'This explanation is more clearer than the first one.', ['This explanation is clearer than the first one.'], 'Never combine synthetic “-er” with analytic “more” on the same adjective.'),
  cFix('cgel-ch13', 'than-as-single', 2, 'Correct the mismatched comparative particle after “as”.', 'Her essay is just as thorough than yours.', ['Her essay is just as thorough as yours.'], 'Scalar equality “as ...” requires “as”, not “than”.'),
  cFix('cgel-ch13', 'set-comparison', 3, 'Correct the double superlative marking.', 'That was the most funniest story in the collection.', ['That was the funniest story in the collection.'], 'Do not combine analytic “most” with superlative inflection “-est”.'),
  cFix('cgel-ch13', 'governors-phrases', 4, 'Correct the comparative preposition error after “different”.', 'Your analysis is different than mine in two ways.', ['Your analysis is different from mine in two ways.', 'Your analysis is different to mine in two ways.'], '“different” does not govern scalar *“than” cleanly in traditional careful prose where “different from” (or British “to”) matches its non-scalar governor.'),
  cFix('cgel-ch13', 'comparative-clauses', 5, 'Correct the subject pronoun case in this formal comparative clause with “is”.', 'Kim is more experienced than me is.', ['Kim is more experienced than I am.', 'Kim is more experienced than me.'], 'When the comparative clause retains a finite auxiliary (“am”), its subject requires nominative “I” (“than I am”).'),

  cRecon('cgel-ch13', 'scalar-inequality', 1, ['longer', 'expected', 'than', 'was', 'chapter', 'we', 'the'], ['the chapter was longer than we expected'], 'Places comparative adjective + “than” comparative clause.'),
  cRecon('cgel-ch13', 'scalar-equality', 2, ['as', 'looks', 'as', 'calm', 'Kim', 'Pat'], ['Kim looks as calm as Pat', 'Pat looks as calm as Kim'], 'Correlative equality puts “as Adj as NP” after copular verb.'),
  cRecon('cgel-ch13', 'set-comparison', 3, ['all', 'of', 'the', 'most', 'rule', 'this', 'useful', 'is'], ['this is the most useful rule of all'], 'Superlative NP includes prepositional set complement “of all”.'),
  cRecon('cgel-ch13', 'non-scalar', 4, ['the', 'as', 'age', 'same', 'brother', 'his', 'is', 'Leo'], ['Leo is the same age as his brother'], 'Non-scalar identity uses “the same ... as ...”.'),
  cRecon('cgel-ch13', 'modification-correlative', 5, ['more', 'you', 'read,', 'the', 'more', 'notice', 'you', 'the'], ['the more you read, the more you notice'], 'Correlative comparative pairs two fronted “the + comparative” clauses.'),

  // cgel-ch14: Non-finite and verbless clauses
  cBlank('cgel-ch14', 'form-types', 1, 'Cambridge distinguishes four non-finite clause types: to-infinitival, bare infinitival, past-participial, and _____ -participial.', ['gerund'], 'Gerund-participials cover both traditional gerund and present participle -ing forms.'),
  cBlank('cgel-ch14', 'catenative-simple', 2, 'Verbs like “want”, “avoid”, and “seem” that take non-finite clausal complements in chains are _____ verbs.', ['catenative'], 'Catenative verbs form recursive chains of non-finite complements.'),
  cBlank('cgel-ch14', 'control-raising', 3, 'In “Kim seems to know”, “Kim” has no semantic role from “seem” and illustrates a _____ verb rather than control.', ['raising'], 'Raising verbs (“seem”, “appear”) raise the subordinate subject without assigning it a matrix semantic role.'),
  cBlank('cgel-ch14', 'hollow-clauses', 4, 'In “The book is easy to read _”, the missing object gap inside the infinitival makes it a _____ clause.', ['hollow'], 'Hollow to-infinitivals contain a non-subject gap bound by an antecedent like matrix Subject.'),
  cBlank('cgel-ch14', 'verbless-clauses', 5, '“With the work finished, they left” contains a _____ clause (“the work finished”) lacking any verb.', ['verbless'], 'Verbless clauses express predication without a finite or non-finite verb head.'),

  cFix('cgel-ch14', 'catenative-simple', 1, 'Correct the wrong non-finite complement type after “enjoy”.', 'They enjoy to walk along the shore.', ['They enjoy walking along the shore.'], 'Catenative “enjoy” selects a gerund-participial complement (“walking”), never a to-infinitival.'),
  cFix('cgel-ch14', 'catenative-complex', 2, 'Correct the bare vs to-infinitival error after passive “made”.', 'The coach made them to run another lap.', ['The coach made them run another lap.'], 'Active causative “make” takes a bare infinitival complement (“run”), without “to”.'),
  cFix('cgel-ch14', 'modifiers-supplements', 3, 'Correct the dangling subjectless participial modifier.', 'Walking into the gallery, the painting caught her eye.', ['Walking into the gallery, she noticed the painting.', 'As she walked into the gallery, the painting caught her eye.'], 'The understood subject of “Walking into the gallery” must match the matrix Subject (“she”, not “the painting”).'),
  cFix('cgel-ch14', 'catenative-analysis', 4, 'Correct the infinitival marker/verb inflection combination.', 'She decided to left before sunrise.', ['She decided to leave before sunrise.'], 'Infinitival marker “to” always takes a plain base verb form (“leave”), never preterite “left”.'),
  cFix('cgel-ch14', 'other-complements', 5, 'Correct the complement after “prevent ... from”.', 'Rain prevented us to finish the outdoor game.', ['Rain prevented us from finishing the outdoor game.', 'Rain prevented us finishing the outdoor game.'], '“prevent” selects “from” + gerund-participial (“finishing”), not to-infinitival.'),

  cRecon('cgel-ch14', 'catenative-simple', 1, ['avoided', 'mentioning', 'incident', 'the', 'Kim'], ['Kim avoided mentioning the incident'], 'Catenative “avoided” governs gerund-participial complement.'),
  cRecon('cgel-ch14', 'infinitival-structure', 2, ['it', 'to', 'leave', 'was', 'for', 'best', 'us'], ['it was best for us to leave'], '“for”-infinitival extraposed clause follows copular predicate.'),
  cRecon('cgel-ch14', 'hollow-clauses', 3, ['difficult', 'chapter', 'this', 'follow', 'to', 'is'], ['this chapter is difficult to follow'], 'Hollow to-infinitival modifies predicative adjective “difficult”.'),
  cRecon('cgel-ch14', 'control-raising', 4, ['seemed', 'understand', 'everyone', 'instructions', 'to', 'the'], ['everyone seemed to understand the instructions'], 'Raising verb “seemed” takes “to”-infinitival complement.'),
  cRecon('cgel-ch14', 'verbless-clauses', 5, ['quiet,', 'room', 'the', 'began', 'they', 'reading'], ['the room quiet, they began reading', 'they began reading, the room quiet'], 'Verbless absolute clause sets the background condition without an overt verb.'),

  // cgel-ch15: Coordination and supplementation
  cBlank('cgel-ch15', 'coordination-overview', 1, 'Words such as “and”, “or”, and “but” belong to the category of _____.', ['coordinators'], 'CGEL separates coordinators (“and/or/but”) from prepositions/subordinators.'),
  cBlank('cgel-ch15', 'both-either-neither', 2, 'Correlative determinative “both” pairs exclusively with coordinator _____.', ['and'], '“both X and Y” marks positive correlative coordination.'),
  cBlank('cgel-ch15', 'supplementation', 3, 'Unlike integrated dependents, parentheticals and non-restrictive appositives are loosely attached elements called _____.', ['supplements'], 'Supplements are interpolated or appended elements set off prosodically/by punctuation.'),
  cBlank('cgel-ch15', 'coordinate-structure', 4, 'Unlike asymmetric “try and see”, standard coordination of same-category units is _____.', ['symmetric'], 'Symmetric coordination allows order reversal without destroying grammaticality.'),
  cBlank('cgel-ch15', 'dislocation-parentheticals', 5, 'Repeating a pronoun inside the clause for a fronted NP (“That book, I read it”) is called left _____.', ['dislocation'], 'Dislocation places an NP outside the core clause linked to an internal resumptive pronoun.'),

  cFix('cgel-ch15', 'both-either-neither', 1, 'Correct the mismatched correlative coordinator pair.', 'Not only she revised the paper, she also checked every source.', ['Not only did she revise the paper, but she also checked every source.', 'She not only revised the paper, but also checked every source.'], 'Fronted “Not only” triggers auxiliary inversion (“did she revise”) and pairs with “but (also)”.'),
  cFix('cgel-ch15', 'layered-scope', 2, 'Correct the subject-verb agreement with “Neither ... nor”.', 'Neither the editor nor the authors was informed.', ['Neither the editor nor the authors were informed.'], 'With “or/nor” joining subjects of differing number, agreement follows the nearer coordinate (“authors were”).'),
  cFix('cgel-ch15', 'coordinate-structure', 3, 'Correct the non-parallel coordinated complements.', 'He likes swimming, hiking, and to cycle in summer.', ['He likes swimming, hiking, and cycling in summer.', 'He likes to swim, hike, and cycle in summer.'], 'Coordinated complements of “likes” should match structurally (three gerund-participials or three infinitives).'),
  cFix('cgel-ch15', 'supplement-forms', 4, 'Correct the comma splice between two independent declarative clauses without a coordinator or semicolon.', 'The train was late, we missed the opening talk.', ['The train was late, so we missed the opening talk.', 'The train was late; we missed the opening talk.', 'Because the train was late, we missed the opening talk.'], 'Two finite main clauses cannot join by comma alone without a coordinator or semicolon.'),
  cFix('cgel-ch15', 'both-either-neither', 5, 'Correct the mismatched “both ... or” correlative.', 'We need both clarity or accuracy in this report.', ['We need both clarity and accuracy in this report.', 'We need either clarity or accuracy in this report.'], '“both” pairs with “and”, while “either” pairs with “or”.'),

  cRecon('cgel-ch15', 'both-either-neither', 1, ['accurate', 'and', 'clear', 'both', 'argument', 'the', 'was'], ['the argument was both clear and accurate', 'the argument was both accurate and clear'], 'Correlative “both” + Adj + “and” + Adj inside predicative coordination.'),
  cRecon('cgel-ch15', 'clausal-subclausal', 2, ['left', 'stayed', 'Kim', 'but', 'Pat'], ['Kim stayed but Pat left', 'Pat stayed but Kim left'], 'Adversative coordinator “but” links two finite clauses.'),
  cRecon('cgel-ch15', 'supplement-forms', 3, ['visited', 'a', 'capital', 'we', 'Paris,', 'historic'], ['we visited Paris, a historic capital'], 'Appended NP supplement follows “Paris” as appositive.'),
  cRecon('cgel-ch15', 'dislocation-parentheticals', 4, ['it', 'really', 'enjoyed', 'lecture,', 'that', 'I'], ['that lecture, I really enjoyed it'], 'Left-dislocated NP sits before clause with resumptive pronoun “it”.'),
  cRecon('cgel-ch15', 'and-or', 5, ['call', 'or', 'write', 'can', 'us', 'you'], ['you can call or write us', 'you can write or call us'], 'Coordinator “or” joins two plain transitive verbs sharing object “us”.'),

  // cgel-ch16: Information packaging
  cBlank('cgel-ch16', 'existential', 1, 'In “There is a book on the desk”, “There” functions as dummy existential _____.', ['subject'], 'Existential “there” fills the grammatical Subject slot while displacing the notional subject after “be”.'),
  cBlank('cgel-ch16', 'clefts', 2, '“It was Kim who solved the puzzle” is an _____ -cleft highlighting “Kim”.', ['it'], 'An it-cleft splits a single proposition using “It + be + focus + relative clause”.'),
  cBlank('cgel-ch16', 'preposing', 3, 'Moving an object to clause-initial position (“This problem we already solved”) is called _____.', ['preposing'], 'Preposing places a complement before Subject to establish given-topic links.'),
  cBlank('cgel-ch16', 'inversion', 4, '“In the doorway stood a tall stranger” demonstrates Subject-Verb _____ after a fronted locative.', ['inversion'], 'Subject-dependent inversion places the Subject NP after the verb following a fronted locative.'),
  cBlank('cgel-ch16', 'passive-syntax', 5, 'In a long passive, the active subject appears inside an optional prepositional phrase headed by _____.', ['by'], 'The “by”-phrase expresses the internalised complement corresponding to active Subject.'),

  cFix('cgel-ch16', 'existential', 1, 'Correct the agreement mismatch with the post-verbal displaced subject.', 'There is several reasons for this delay.', ['There are several reasons for this delay.'], 'Finite “be” in existential clauses agrees in number with the plural displaced NP “several reasons”.'),
  cFix('cgel-ch16', 'extraposition', 2, 'Correct the missing anticipatory subject “It” in this extraposed sentence.', 'Is obvious that the data support our conclusion.', ['It is obvious that the data support our conclusion.', 'That the data support our conclusion is obvious.'], 'Extraposed finite clauses require dummy subject “It” in English.'),
  cFix('cgel-ch16', 'clefts', 3, 'Correct the agreement inside the relative clause of this cleft sentence.', 'It is the students who decides the schedule.', ['It is the students who decide the schedule.'], 'When plural “the students” is the foregrounded antecedent, the relative clause verb agrees with plural “decide”.'),
  cFix('cgel-ch16', 'passive-syntax', 4, 'Correct the missing passive auxiliary “be” in this passive sentence.', 'The manuscript reviewed by three linguists.', ['The manuscript was reviewed by three linguists.', 'The manuscript has been reviewed by three linguists.'], 'A passive clause requires passive auxiliary “be” (“was reviewed”) rather than a bare past participle.'),
  cFix('cgel-ch16', 'inversion', 5, 'Correct the subject-verb number agreement in this inverted locative clause.', 'On the shelf sits two heavy dictionaries.', ['On the shelf sit two heavy dictionaries.'], 'Despite preposed locative PP “On the shelf”, the verb agrees with plural postposed Subject “two heavy dictionaries”.'),

  cRecon('cgel-ch16', 'clefts', 1, ['that', 'started', 'was', 'Mira', 'the', 'it', 'project'], ['it was Mira that started the project'], 'It-cleft highlights focused constituent “Mira” before relative clause.'),
  cRecon('cgel-ch16', 'existential', 2, ['errors', 'in', 'three', 'draft', 'were', 'there', 'the'], ['there were three errors in the draft'], 'Existential “there” + plural “were” + displaced NP + locative PP.'),
  cRecon('cgel-ch16', 'extraposition', 3, ['remains', 'will', 'how', 'it', 'they', 'uncertain', 'succeed'], ['it remains uncertain how they will succeed'], 'Dummy “it” introduces predicate AdjP + extraposed interrogative clause.'),
  cRecon('cgel-ch16', 'preposing', 4, ['never', 'topic', 'that', 'discussed', 'we'], ['that topic we never discussed'], 'Preposed object NP precedes Subject + adverb + verb.'),
  cRecon('cgel-ch16', 'inversion', 5, ['a', 'lay', 'map', 'folded', 'on', 'table', 'the'], ['on the table lay a folded map'], 'Fronted locative PP triggers inversion of verb and Subject NP.'),

  // cgel-ch17: Deixis and anaphora
  cBlank('cgel-ch17', 'binding-domains', 1, 'A reflexive pronoun such as “himself” usually requires its antecedent within the same local _____.', ['clause'], 'Reflexive binding is bounded to its local clause (unlike ordinary non-reflexive “him”).'),
  cBlank('cgel-ch17', 'anaphora', 2, 'In “Before he arrived, Kim called”, “he” precedes its coreferential antecedent “Kim”, illustrating backward anaphora or _____.', ['cataphora'], 'When an anaphor precedes its antecedent in a subordinate clause, CGEL notes cataphoric reference.'),
  cBlank('cgel-ch17', 'reciprocals', 3, 'Reciprocal pronouns in English are “each other” and “_____ another”.', ['one'], 'Both “each other” and “one another” require plural or coordinated antecedents.'),
  cBlank('cgel-ch17', 'reduced-nps', 4, 'In “Take the green one”, “_____” acts as an anaphoric pro-nominal replacing a previously mentioned count noun.', ['one'], 'Pro-nominal “one” replaces a NOM head inside an NP.'),
  cBlank('cgel-ch17', 'reduced-vps', 5, 'In “Kim finished early, and Pat did too”, “did” strands an auxiliary via VP _____.', ['ellipsis'], 'Post-auxiliary ellipsis omits a recoverable VP predicate.'),

  cFix('cgel-ch17', 'reflexives', 1, 'Correct the reflexive pronoun usage when no local subject antecedent matches.', 'Pat and myself organized the workshop.', ['Pat and I organized the workshop.'], 'In a Subject coordination without a c-commanding antecedent, use nominative “I”, not reflexive *“myself”.'),
  cFix('cgel-ch17', 'reciprocals', 2, 'Correct the singular vs plural antecedent requirement of reciprocal “each other”.', 'Only Sam blamed each other for the delay.', ['Sam and Pat blamed each other for the delay.', 'Sam blamed himself for the delay.', 'Sam blamed himself for the delay.', 'Only Sam blamed himself for the delay.'], 'Reciprocal “each other” requires a plural/coordinated antecedent (or use reflexive “himself”).'),
  cFix('cgel-ch17', 'personal-pronouns', 3, 'Correct the pronoun-antecedent verb agreement error.', 'If a student submits late, they receives a penalty.', ['If a student submits late, they receive a penalty.', 'If a student submits late, he or she receives a penalty.'], 'Singular “they” takes plural verb agreement “receive”, never singular *“they receives”.'),
  cFix('cgel-ch17', 'demonstratives', 4, 'Correct the deictic demonstrative agreement error.', 'Those kind of mistakes are easy to prevent.', ['That kind of mistake is easy to prevent.', 'Those kinds of mistakes are easy to prevent.'], 'Plural demonstrative “Those” requires plural noun “kinds” (or singular “That kind”).'),
  cFix('cgel-ch17', 'reduced-nps', 5, 'Correct the improper omission of pro-nominal “one(s)” after a non-quantifier attributive adjective.', 'I prefer the small blue rather than the red.', ['I prefer the small blue one rather than the red one.'], 'Count-noun NPs with attributive adjectives normally require pro-nominal “one” when the noun is omitted.'),

  cRecon('cgel-ch17', 'binding-domains', 1, ['said', 'herself', 'praised', 'Kim', 'that', 'she'], ['Kim said that she praised herself'], 'Non-reflexive “she” links across clause boundary while reflexive “herself” binds locally.'),
  cRecon('cgel-ch17', 'reciprocals', 2, ['each other’s', 'read', 'critically', 'drafts', 'they'], ['they read each other’s drafts critically', 'they critically read each other’s drafts'], 'Genitive reciprocal “each other’s” determines “drafts”.'),
  cRecon('cgel-ch17', 'reduced-vps', 3, ['too', 'did', 'finished', 'on time', 'and', 'Ada', 'Sam'], ['Ada finished on time and Sam did too', 'Sam finished on time and Ada did too'], 'Auxiliary “did” replaces repeated VP before “too”.'),
  cRecon('cgel-ch17', 'temporal-deixis', 4, ['next week', 'by', 'will', 'depart', 'then', 'we', 'and', 'arrive'], ['we will depart next week and arrive by then'], 'Anaphoric temporal PP “by then” picks up “next week”.'),
  cRecon('cgel-ch17', 'reduced-nps', 5, ['older', 'kept', 'newer', 'gave', 'away', 'the', 'version', 'the', 'one', 'I', 'and'], ['I kept the newer version and gave the older one away', 'I kept the newer one and gave the older version away'], 'Pro-nominal “one” substitutes for previously introduced noun “version”.'),

  // cgel-ch18: Inflectional morphology and related matters
  cBlank('cgel-ch18', 'alternation-syncretism', 1, 'When two distinct inflectional forms of a lexeme share the same shape (like preterite and past participle “walked”), this identity is called _____.', ['syncretism'], 'Syncretism occurs when distinct grammatical cells share one morphological shape.'),
  cBlank('cgel-ch18', 'spelling-alternations', 2, 'Doubling the final consonant in “hop -> hopped” vs “hope -> hoped” preserves the _____ quality of the preceding vowel.', ['short', 'lax'], 'Consonant doubling marks a preceding short/checked vowel in English spelling.'),
  cBlank('cgel-ch18', 'noun-plurals', 3, 'Nouns like “sheep” and “deer” that show identical singular and plural shapes are _____ plurals.', ['zero'], 'Zero-inflection plurals have no overt plural suffix.'),
  cBlank('cgel-ch18', 'grade', 4, 'Synthetic inflectional comparison attaches -er and -est primarily to monosyllabic or disyllabic _____ bases.', ['adjective', 'adjectival'], 'Grade inflection attaches mainly to short adjectives and a few adverbs.'),
  cBlank('cgel-ch18', 'genitive', 5, 'Because “the Queen of England’s crown” attaches ’s to an entire NP rather than a single noun head, English genitive ’s behaves like a phrasal clitic or _____.', ['phrase-final', 'clitic', 'edge'], 'Group genitives attach ’s at the right edge of the whole NP.'),

  cFix('cgel-ch18', 'spelling-alternations', 1, 'Correct the consonant-doubling error in this past form of “plan”.', 'They planed the conference for October.', ['They planned the conference for October.'], 'Stress on the final CVC syllable of “plan” requires doubling “n” -> “planned” (“planed” is from “plane”).'),
  cFix('cgel-ch18', 'noun-plurals', 2, 'Correct the over-regularised plural inflection on “criterion”.', 'Three main criterias guided the committee.', ['Three main criteria guided the committee.'], '“criteria” is already the plural of “criterion”; adding *-s creates an erroneous double plural.'),
  cFix('cgel-ch18', 'genitive', 3, 'Correct the misplaced apostrophe on this regular plural possessive noun.', 'All the students’s essays were submitted.', ["All the students' essays were submitted."], 'Regular -s plural nouns form the genitive with an apostrophe alone (“students’”), without adding another s.'),
  cFix('cgel-ch18', 'verb-forms', 4, 'Correct the irregular past participle form of “lie” (recline).', 'The dog has laid by the fireplace all afternoon.', ['The dog has lain by the fireplace all afternoon.'], 'Intransitive “lie” (recline) takes preterite “lay” and past participle “lain”, whereas “laid” belongs to transitive “lay”.'),
  cFix('cgel-ch18', 'spelling-alternations', 5, 'Correct the y-to-i inflectional spelling error.', 'She tryed three methods before succeeding.', ['She tried three methods before succeeding.'], 'Final consonant + “y” changes “y” to “i” before “-ed” (“tried”).'),

  cRecon('cgel-ch18', 'noun-plurals', 1, ['remained', 'two', 'on', 'deer', 'hill', 'the'], ['two deer remained on the hill'], 'Zero-plural noun “deer” follows numeral without -s.'),
  cRecon('cgel-ch18', 'genitive', 2, ['office', 'the', 'door', 'director’s', 'open', 'stood'], ['the director’s office door stood open'], 'Genitive determiner “the director’s” modifies “office door”.'),
  cRecon('cgel-ch18', 'alternation-syncretism', 3, ['cut', 'paper', 'the', 'Kim', 'yesterday'], ['Kim cut the paper yesterday'], 'Syncretic verb “cut” serves as preterite form with “yesterday”.'),
  cRecon('cgel-ch18', 'grade', 4, ['heaviest', 'box', 'lifted', 'they', 'the'], ['they lifted the heaviest box'], 'Y-to-i alternation applies before superlative “-est”.'),
  cRecon('cgel-ch18', 'verb-forms', 5, ['already', 'forgotten', 'we', 'had', 'number', 'the'], ['we had already forgotten the number'], 'Consonant doubling applies in irregular participle “forgotten”.'),

  // cgel-ch19: Lexical word-formation
  cBlank('cgel-ch19', 'conversion', 1, 'Using a noun like “bottle” directly as a verb (“to bottle jam”) with no affix is called _____.', ['conversion'], 'Conversion assigns a base to a new lexical category without adding affixes.'),
  cBlank('cgel-ch19', 'compound-headedness', 2, 'In typical English endocentric compounds such as “blackbird” and “oak tree”, the _____ element is the semantic and syntactic head.', ['right', 'right-hand', 'final'], 'English compounds follow the Right-hand Head Rule in most endocentric cases.'),
  cBlank('cgel-ch19', 'minor-processes', 3, 'Combining parts of two words such as “smoke + fog -> smog” or “breakfast + lunch -> brunch” is lexical _____.', ['blending'], 'Blends fuse parts of two source lexemes into a single new word.'),
  cBlank('cgel-ch19', 'minor-processes', 4, 'Shortening “laboratory” to “lab” or “mathematics” to “math” is word _____.', ['clipping'], 'Clipping reduces a polysyllabic lexeme without changing its category or core meaning.'),
  cBlank('cgel-ch19', 'nominalisation', 5, 'Turning verb “arrive” into noun “arrival” or “decide” into “decision” is called _____.', ['nominalisation', 'nominalization'], 'Nominalisation derives nouns from verbs or adjectives via suffixation or conversion.'),

  cFix('cgel-ch19', 'negatives', 1, 'Correct the wrong negative prefix on “possible” / “relevant” -> here “possible”.', 'Solving every case by a fixed list is unpossible.', ['Solving every case by a fixed list is impossible.'], 'Latinate adjective “possible” takes assimilated negative prefix “im-”, not “un-”.'),
  cFix('cgel-ch19', 'compound-nouns', 2, 'Correct the plural inflection inside this right-headed compound noun.', 'We bought two books-shelf for the study.', ['We bought two bookshelves for the study.', 'We bought two book-shelves for the study.'], 'In right-headed compounds, plural inflection attaches to the right-hand head noun (“bookshelves”), not the left modifier.'),
  cFix('cgel-ch19', 'affixation', 3, 'Correct the malformed derived noun from adjective “curious”.', 'Her curiousity led to a new experiment.', ['Her curiosity led to a new experiment.'], 'Latinate “curious” drops “o” before nominal suffix “-ity” -> “curiosity”.'),
  cFix('cgel-ch19', 'negatives', 4, 'Correct the negative prefix error before “legal”.', 'Driving without a licence is inlegal.', ['Driving without a licence is illegal.'], 'Prefix “in-” assimilates to “il-” before lateral “l” (“illegal”).'),
  cFix('cgel-ch19', 'conversion', 5, 'Correct the missing verbal inflection when converted verb “email” is used in past time.', 'She email the revised draft to everyone yesterday.', ['She emailed the revised draft to everyone yesterday.'], 'Once converted into a verb, “email” takes normal verbal inflections (“emailed”).'),

  cRecon('cgel-ch19', 'compound-nouns', 1, ['rebuilt', 'the', 'greenhouse', 'storm', 'after', 'they', 'the'], ['they rebuilt the greenhouse after the storm', 'after the storm they rebuilt the greenhouse'], 'Compound noun “greenhouse” denotes a distinct glass structure.'),
  cRecon('cgel-ch19', 'nominalisation', 2, ['delayed', 'sudden', 'his', 'departure', 'proceedings', 'the'], ['his sudden departure delayed the proceedings'], 'Nominalised “departure” takes possessive determiner and adjective modifier.'),
  cRecon('cgel-ch19', 'compound-adjectives', 3, ['published', 'well-known', 'she', 'a', 'article'], ['she published a well-known article'], 'Compound adjective modifies following noun attributively.'),
  cRecon('cgel-ch19', 'conversion', 4, ['bottled', 'fresh', 'they', 'apple', 'juice'], ['they bottled fresh apple juice'], 'Converted verb “bottled” takes transitive direct object NP.'),
  cRecon('cgel-ch19', 'affixation', 5, ['remarkably', 'readable', 'was', 'chapter', 'the'], ['the chapter was remarkably readable'], 'Deverbal adjective “readable” takes adverbial degree modifier.'),

  // cgel-ch20: Punctuation
  cBlank('cgel-ch20', 'comma-uses', 1, 'Unlike integrated relatives, supplementary (non-restrictive) relative clauses are enclosed in _____.', ['commas', 'a comma'], 'Supplementary dependents are prosodically and orthographically separated by commas (or dashes/parentheses).'),
  cBlank('cgel-ch20', 'primary-terminals', 2, 'The three primary terminal marks closing sentences are the full stop (period), question mark, and _____ mark.', ['exclamation'], 'CGEL lists period, question mark, and exclamation mark as primary terminal indicators.'),
  cBlank('cgel-ch20', 'apostrophe-slash', 3, 'An _____ marks either letter omission in contractions (“don’t”) or genitive case on nouns (“Kim’s”).', ['apostrophe'], 'Apostrophes indicate genitives and contractions (not ordinary plural nouns).'),
  cBlank('cgel-ch20', 'secondary-boundaries', 4, 'A _____ can join two closely related independent main clauses without a coordinator.', ['semicolon'], 'Semicolons separate independent clauses without creating a comma splice.'),
  cBlank('cgel-ch20', 'parentheses-dash', 5, 'Paired commas, dashes, or _____ enclose parenthetical supplements in the middle of a clause.', ['parentheses', 'brackets'], 'Mid-clause supplements take symmetrical paired boundary marks on both sides.'),

  cFix('cgel-ch20', 'comma-uses', 1, 'Correct the missing closing comma around this mid-clause supplementary relative clause.', 'My sister, who lives in Toronto visits every autumn.', ['My sister, who lives in Toronto, visits every autumn.'], 'Paired supplementary modifiers inside a clause require both an opening and a closing comma.'),
  cFix('cgel-ch20', 'apostrophe-slash', 2, 'Correct the improper plural apostrophe.', 'Both linguistics textbook’s arrived on Monday.', ['Both linguistics textbooks arrived on Monday.'], 'Ordinary non-genitive plurals (“textbooks”) do not take an apostrophe.'),
  cFix('cgel-ch20', 'secondary-boundaries', 3, 'Correct the comma splice between two independent clauses.', 'The lab closed at five, everyone packed their notes.', ['The lab closed at five; everyone packed their notes.', 'The lab closed at five, and everyone packed their notes.', 'The lab closed at five, so everyone packed their notes.'], 'Joining two finite main clauses with only a comma is a comma splice; use a semicolon or add a coordinator.'),
  cFix('cgel-ch20', 'comma-uses', 4, 'Correct the punctuation separating Subject from Verb in a single clause.', 'The new syntax handbook on the upper shelf, is quite clear.', ['The new syntax handbook on the upper shelf is quite clear.'], 'Never place a single comma between a Subject NP and its finite predicate verb.'),
  cFix('cgel-ch20', 'primary-terminals', 5, 'Correct the terminal punctuation of this indirect reported question.', 'She asked where the seminar was being held?', ['She asked where the seminar was being held.'], 'An indirect declarative report containing an embedded interrogative closes with a period, not a question mark.'),

  cRecon('cgel-ch20', 'parentheses-dash', 1, ['however,', 'agreed', 'committee,', 'the', 'eventually'], ['the committee, however, eventually agreed'], 'Connective supplement takes boundary commas.'),
  cRecon('cgel-ch20', 'secondary-boundaries', 2, ['checked', 'sources:', 'three', 'primary,', 'we', 'and', 'secondary,', 'archival'], ['we checked three sources: primary, secondary, and archival'], 'Colon introduces enumerated appositive list.'),
  cRecon('cgel-ch20', 'quotation', 3, ['“The', 'data', 'clear.”', 'are', 'said,', 'she'], ['she said, “The data are clear.”', '“The data are clear,” she said.'], 'Quotation marks enclose direct reported utterance.'),
  cRecon('cgel-ch20', 'apostrophe-slash', 4, ['students’', 'reviewed', 'notes', 'the', 'tutor', 'the'], ["the tutor reviewed the students' notes"], 'Plural genitive apostrophe follows -s on “students’”.'),
  cRecon('cgel-ch20', 'comma-uses', 5, ['rained,', 'although', 'it', 'continued', 'match', 'the'], ['although it rained, the match continued', 'the match continued although it rained'], 'Preposed adverbial clause closes with a comma before the main clause.'),
];

export const cambridgeMixedItems = [
  ...baseCambridgeMixedItems,
  ...extraCambridgeMixedItems,
];
