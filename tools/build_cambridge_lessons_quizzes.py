#!/usr/bin/env python3
"""Generate Cambridge grammar lessons in the revised lesson format.

Creates chapter lessons, revised opening/closing checks and matching pilot
overlays with natural prose. No book or publisher references are written into
learner-facing text.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "grammar/rules"
COURSE = ROOT / "web/content/lessons/course.json"
LESSONS = ROOT / "web/content/lessons"

TITLES = {
    1: "Using words and forms accurately",
    3: "Verb forms and auxiliaries",
    4: "Complementation and valency",
    5: "Nouns and determiners",
    6: "Adjectives and adverbs",
    7: "Prepositions and particles",
    10: "Clause types and questions",
    13: "Comparatives",
    14: "Non-finite clauses",
    15: "Coordination",
    16: "Information packaging",
    17: "Pronouns and pro-forms",
    18: "Morphology and spelling",
    19: "Word formation and inflection",
    20: "Punctuation",
}
SECTIONS = ["introduction", "concepts", "worked-example", "application", "recap"]
CHAPTER_KEY_TERMS = {
    1: [
        {"term": "contraction", "definition": "A short form such as “we’re” that joins a pronoun and an auxiliary verb."},
        {"term": "coordinated subject", "definition": "Two or more subjects joined by “and” or “or”, as in “she and we”."},
        {"term": "auxiliary verb", "definition": "A helping verb such as “be”, “have” or “do” that works with a main verb."},
        {"term": "pronoun", "definition": "A word such as “she”, “we” or “they” that stands for a person or thing."},
        {"term": "subject–verb agreement", "definition": "Matching the form of the verb to the subject of the clause."},
    ],
    6: [
        {"term": "degree word", "definition": "A word such as “enough”, “very” or “too” that says how much."},
        {"term": "enough", "definition": "A degree word that usually comes after the word it describes: “warm enough”."},
        {"term": "adjective", "definition": "A word that describes a person or thing, such as “warm” or “clear”."},
        {"term": "adverb", "definition": "A word that describes how, when or where something happens, such as “clearly”."},
        {"term": "preposition", "definition": "A word such as “to”, “of” or “in” that links a noun phrase to the rest of the sentence."},
    ],
    7: [
        {"term": "time expression", "definition": "A phrase that says when something happened, such as “three weeks ago”."},
        {"term": "ago", "definition": "A word that follows a time expression: “three weeks ago”."},
        {"term": "subordinator", "definition": "A connecting word such as “before”, “after” or “when” that begins a dependent clause."},
        {"term": "temporal clause", "definition": "A dependent clause that says when something happens, as in “before the rain started”."},
        {"term": "connecting word", "definition": "A word that joins a dependent clause to the main clause."},
    ],
}
CHAPTER_CONTENT = {
    4: {
        "title": "Complementation and valency",
        "description": ("Learn how each verb chooses the phrases that follow it, how objects and "
                        "pronouns take their places, and how to repair the mistakes that come from "
                        "giving a verb the wrong company."),
        "key_terms": [
            {"term": "complementation", "definition": "The set of phrases a verb needs or allows after it."},
            {"term": "valency", "definition": "How many phrases a verb takes and what kind they are."},
            {"term": "direct object", "definition": "The person or thing directly affected by the verb."},
            {"term": "indirect object", "definition": "The person who receives something in a double-object pattern."},
            {"term": "to-infinitival", "definition": "A verb phrase beginning with “to”, as in “to leave”."},
            {"term": "gerund-participial", "definition": "An “-ing” verb form used like a noun, as in “enjoying the film”."},
            {"term": "particle", "definition": "A small word such as “up” or “in” that combines with a verb."},
            {"term": "inchoative", "definition": "A sentence where the affected thing is the subject and nobody causes the action."},
            {"term": "pseudo-cleft", "definition": "A sentence that puts the important information at the end, as in “What she did was call.”"},
        ],
        "sections": {
            "introduction": ("Some verbs are happy with just a subject, and some are not. You cannot say "
                             "“She perused.” and stop; the verb is still waiting for something. In this module "
                             "you will learn how each verb chooses the phrases that must follow it, how objects "
                             "and pronouns take their places, and how to fix the mistakes that come from giving "
                             "a verb the wrong company."),
            "concepts": ("Start with what a verb needs. Consist selects an of-phrase: “The team consists of five "
                         "players.” Tend selects “to” plus a base verb: “She tends to arrive early.” Enjoy selects "
                         "an -ing form, not a “to” form: “They enjoy swimming,” not “They enjoy to swim.” Peruse "
                         "needs a direct object: “Lena perused the report,” not “Lena perused.” These needs are the "
                         "verb’s complementation, and the number and kind of phrases it takes is its valency.\n\n"
                         "Next look at objects and pronouns. A direct object is the thing affected by the verb; an "
                         "indirect object is the person who receives it. Pronouns show their job by their form: "
                         "“She thanked him,” not “She thanked he.” In a verb-and-particle pair such as bring in or "
                         "pick up, a light pronoun goes before the particle: “Bring it in,” not “Bring in it.” "
                         "Direction words behave differently from particles: “She carried the boxes downstairs,” "
                         "not “She carried downstairs the boxes.” A singular role noun in object position also needs "
                         "a determiner: “She met a teacher,” not “She met teacher.”\n\n"
                         "Finally, watch fixed combinations and special patterns. Come across cannot move its "
                         "across-phrase to the front: “She came across the old letter,” not “Across the old letter "
                         "she came.” Construct and destroy do not work as bare inchoatives: “The shed was constructed "
                         "last week,” not “The shed constructed last week.” A do-pseudo-cleft keeps its aspect "
                         "consistent: “What Leo did was repair the radio,” and “What Leo was doing was repairing the "
                         "radio.” Explain takes its message as the direct object and the person in a to-phrase: "
                         "“Mara explained the schedule to the team,” not “Mara explained the team the schedule.” "
                         "Peruse in its reading sense does not leave its object understood: “She perused the papers,” "
                         "not “She perused.”"),
            "worked-example": ("Read “Mara explained the schedule to the new team.” The verb is explain. It wants "
                               "the thing explained, the schedule, as its direct object, and the person, the new team, "
                               "in a to-phrase. Compare “Mara explained the new team the schedule.” That order belongs "
                               "to verbs such as give or send, not to explain. Now read “She picked the folder up.” "
                               "Picked pairs with the particle up, and the object the folder is a full noun phrase, so "
                               "it can come before the particle. With a pronoun the order changes: “She picked it up.”"),
            "application": ("When you revise, ask four questions. What does this verb need after it? Is every object "
                            "present and in the right form? If there is a particle, should the object come before it? "
                            "If the sentence is fixed or idiomatic, does it keep its usual shape? Checking these four "
                            "things catches most of the mistakes in this module."),
            "recap": ("Every verb has its own company. Consist takes of, tend takes to, enjoy takes -ing, and peruse "
                      "takes a direct object. Pronouns show their job by form, light pronouns go before particles, and "
                      "direction words do not. Fixed combinations keep their shape, pseudo-clefts keep their aspect, "
                      "and explain takes a to-phrase for the person."),
        },
    },
    1: {
        "title": "Contractions with coordinated subjects",
        "description": ("Learn why a contraction such as we’re cannot stand for a whole coordinated "
                        "subject, and how to write the pair clearly."),
        "sections": {
            "introduction": ("A contraction is a short form such as we’re or she’s. When two subjects are "
                             "joined by and, a contraction can belong only to the last pronoun, not to the "
                             "whole pair. In this module you will learn how to keep the meaning clear."),
            "concepts": ("In “she and we’re ready”, the contraction we’re attaches to we alone. That makes "
                         "the sentence sound as if only we are ready. Write the auxiliary in full for the last "
                         "subject: “she and we are ready.” The same fix works for other coordinated subjects: "
                         "“Jo and you’re ready” becomes “Jo and you are ready.” A contraction is fine when the "
                         "coordination is not involved: “We’re ready” is clear because there is only one subject. "
                         "Check the word before the contraction: if it is and, the contraction is probably doing "
                         "too much."),
            "worked-example": ("Read “Jo and you’re ready.” The subject is the pair Jo and you, but the "
                               "contraction ’re is attached to you alone. Write “Jo and you are ready.” Now "
                               "read “She and we’re ready.” Expand the auxiliary: “She and we are ready.”"),
            "application": ("When you revise, find every contraction. If it follows and, write the auxiliary "
                            "in full after the last subject. Read the sentence aloud; if the contraction sounds "
                            "as if it belongs to one person only, expand it."),
            "recap": ("A contraction belongs to the word it is attached to. After a coordinated subject, write "
                      "the auxiliary in full: “she and we are ready,” not “she and we’re ready.”"),
        },
    },
    6: {
        "title": "Enough, and accustomed to",
        "description": ("Learn where enough goes and why accustomed to is followed by an -ing form."),
        "sections": {
            "introduction": ("Small words such as enough have fixed places, and some adjectives take a "
                             "particular kind of verb after them. In this module you will learn where enough "
                             "goes and how accustomed to takes its -ing form."),
            "concepts": ("Enough comes after the word it describes: “warm enough”, “clearly enough”. It does "
                         "not come first: not “enough warm” and not “spoke enough clearly.” After accustomed to, "
                         "use an -ing form: “Jo is accustomed to working late.” Do not use a bare verb: not "
                         "“accustomed to work late.” The to here is a preposition, so it takes the -ing form."),
            "worked-example": ("Read “The room was enough warm.” Move enough after warm: “The room was warm "
                               "enough.” Read “Jo is accustomed to work late.” Change work to working: “Jo is "
                               "accustomed to working late.”"),
            "application": ("When you revise, put enough after the adjective or adverb it describes. After "
                            "accustomed to, check that the next verb ends in -ing. Both checks take only a "
                            "moment and catch the usual mistakes."),
            "recap": ("Enough follows the word it describes: “warm enough”. Accustomed to takes an -ing form: "
                      "“accustomed to working late.”"),
        },
    },
    7: {
        "title": "Time words and connecting words",
        "description": ("Learn where ago goes and how to join a time clause with before."),
        "sections": {
            "introduction": ("Time words such as ago and connecting words such as before have fixed places. "
                             "In this module you will learn where ago goes and how to join a time clause "
                             "without adding an extra word."),
            "concepts": ("Ago follows a time expression: “three weeks ago”. It does not come first: not “ago "
                         "three weeks.” Before joins a time clause directly: “before the rain started”. Do not "
                         "add that: not “before that the rain started.” The word before already does the "
                         "connecting, so that is extra."),
            "worked-example": ("Read “They left ago three weeks.” Move ago after the time expression: “They "
                               "left three weeks ago.” Read “We packed before that the rain started.” Remove "
                               "that: “We packed before the rain started.”"),
            "application": ("When you revise, put ago after the time expression. With before, after, when or "
                            "as soon as, check that the clause begins straight after the connecting word, with "
                            "no extra that in between."),
            "recap": ("Ago follows the time expression: “three weeks ago”. Before joins its clause directly: "
                      "“before the rain started.”"),
        },
    },
    14: {
        "title": "Non-finite clauses",
        "description": ("Learn how to build clauses without tense: for-infinitivals, object-plus-infinitive "
                        "patterns, auxiliary order, bare and to-infinitives, and -ing modifiers."),
        "key_terms": [
            {"term": "for-infinitival", "definition": "A clause such as “for her to leave”, where for introduces the subject and the verb carries no tense."},
            {"term": "accusative pronoun", "definition": "The object form of a pronoun, such as him, her, me, us or them."},
            {"term": "bare infinitival", "definition": "A verb without to, as in “made us wait”."},
            {"term": "to-infinitival", "definition": "A verb phrase with to, as in “to wait”."},
            {"term": "auxiliary chain", "definition": "The helping verbs before a main verb, such as has been in “has been checking”."},
            {"term": "interrogative complement", "definition": "A clause that reports a question, as in “which route to take”."},
            {"term": "participial modifier", "definition": "An -ing phrase that describes a noun, as in “the people waiting outside”."},
        ],
        "sections": {
            "introduction": ("Some clauses do not carry tense. They can still have a subject, an object or a "
                             "question word, and they follow their own rules. In this module you will learn how "
                             "to build these clauses and how they fit into a larger sentence."),
            "concepts": ("Use for when you want to name the subject of an infinitival clause. The pronoun after "
                         "for takes the object form: “for him to speak”, “for her to arrive”. Put for first, then "
                         "the subject, then to and the verb: “It is essential for you to check the pressure first.” "
                         "Do not put the object before the subject: not “for the pressure you to check.”\n\n"
                         "Believe needs an object before a to-infinitive: “Nina believed herself to be qualified.” "
                         "Even when the object is the same person as the subject, you still say it: not “Nina "
                         "believed to be qualified.” When a sentence uses both perfect and progressive, have comes "
                         "before be: “She has been checking the seals,” not “She is having checked.” Make takes a "
                         "bare verb in the active: “They made us wait outside.” In the passive, use to: “We were "
                         "made to wait outside.”\n\n"
                         "An infinitival question does not take its own subject: “They discussed which route to "
                         "take,” not “which route for them to take.” The question word already does the work. An "
                         "-ing phrase can describe a noun without who: “The people waiting outside need shelter.” "
                         "Add who only when you also add a finite verb: “The people who are waiting outside…”"),
            "worked-example": ("Read “We arranged for him to speak first.” For introduces the subject him, and "
                               "speak has no tense. Compare “We arranged for he to speak first”: the pronoun after "
                               "for must be him. Now read “They made us wait outside.” The active uses wait; the "
                               "passive needs to: “We were made to wait outside.”"),
            "application": ("When you write a non-finite clause, check four things: does for come first, is the "
                            "pronoun in its object form, does believe have an object, and does make take a bare "
                            "verb in the active and to in the passive? For questions and -ing modifiers, remove "
                            "any extra subject or who that the clause does not need."),
            "recap": ("For begins an infinitival clause, and its subject uses the object form. Believe needs "
                      "an object before to. Perfect have comes before progressive be. Make takes a bare verb in "
                      "the active and to in the passive. Infinitival questions have no extra subject, and -ing "
                      "modifiers do not take who."),
        },
    },
    15: {
        "title": "Coordination and supplementary clauses",
        "description": ("Learn how to keep coordinated pieces parallel and how to anchor a describing clause "
                        "to the noun it describes."),
        "key_terms": [
            {"term": "coordination", "definition": "Joining two or more expressions with and, or or but."},
            {"term": "bare coordinate", "definition": "One of the joined expressions, without its own connecting word repeated inside it."},
            {"term": "syntactic function", "definition": "The job an expression does in the sentence, such as subject or object."},
            {"term": "supplementary relative", "definition": "A describing clause set off by commas, as in “which the architect had redesigned”."},
            {"term": "antecedent", "definition": "The noun phrase that a relative clause describes."},
        ],
        "sections": {
            "introduction": ("When you join words or clauses, the pieces must be able to do the same job. A "
                             "mismatched pair sounds broken even when each half is fine on its own. In this "
                             "module you will learn how to keep coordinated pieces parallel and how to anchor "
                             "a describing clause to the noun it describes."),
            "concepts": ("Coordinates must share the same job. “The visitor arrived yesterday and after "
                         "lunch” joins two time phrases; “The visitor arrived yesterday and the station” joins "
                         "a time phrase with a thing, so it fails. “The actor admired and praised the leader” "
                         "joins two verbs that both take the leader as object.\n\n"
                         "A subject coordination should not mix an infinitival with an -ing clause: “To cycle "
                         "or to walk is good exercise” and “Jogging or swimming would be sufficient” are "
                         "parallel, while “To cycle or walking” is not. Two singular nouns joined at word level "
                         "stay singular for the determiner: “this cup and saucer”, not “these cup and saucer.” "
                         "When the noun is plural, the determiner is plural too: “two plates and bowls.”\n\n"
                         "A describing clause such as “which the architect had redesigned” needs a noun before "
                         "it: “The entrance, which the architect had redesigned, was finally approved.” Without "
                         "the entrance, the clause has nothing to describe. The same is true for “whose roof had "
                         "collapsed”: add the shed first."),
            "worked-example": ("Read “The entrance, which the architect had redesigned, was finally approved.” "
                               "The noun entrance is the anchor, and the which-clause adds information. Compare "
                               "“Which the architect had redesigned, was finally approved.” The clause has no "
                               "anchor, so the sentence cannot stand. Now read “these cup and saucer.” Change the "
                               "determiner: “this cup and saucer.”"),
            "application": ("When you join two expressions, give each one the same job. If you mix an -ing "
                            "form with a to-form in a subject, make them match. Check the determiner when you "
                            "join singular nouns. Before a supplementary relative, ask what noun it describes; "
                            "if the answer is missing, add it."),
            "recap": ("Coordinates share a job and a shape. Singular nouns joined at word level stay singular "
                      "for the determiner. A supplementary relative needs an anchor noun before it."),
        },
    },
    13: {
        "title": "Comparatives",
        "description": ("Learn how to compare two things, how to rank one thing in a larger set, "
                        "and which small words go with each pattern."),
        "key_terms": [
            {"term": "comparative", "definition": "A form such as taller or sturdier that compares two things."},
            {"term": "superlative", "definition": "A form such as tallest or sturdiest that ranks one thing in a set."},
            {"term": "than", "definition": "The word that introduces the second term in most comparisons."},
            {"term": "partitive", "definition": "An of-phrase that names the set being compared, as in “of the four”."},
            {"term": "definite article", "definition": "The word “the”, used when the listener can identify what you mean."},
            {"term": "free superlative", "definition": "A superlative used without a noun after it, as in “the lowest it has been”."},
        ],
        "sections": {
            "introduction": ("Comparisons are everywhere: two routes, two prices, two people. English uses "
                             "different words depending on whether you are comparing two things or ranking one "
                             "thing in a larger set. In this module you will learn those patterns and the small "
                             "words that go with each one."),
            "concepts": ("Start with the second term. Superior and inferior take to, not than: “This fabric is "
                         "superior to the original.” Similar also takes to: “This fabric is similar to the green "
                         "one.” Other than needs a noun or noun phrase, not a bare clause: “We received no "
                         "payments other than the agency’s,” not “other than the agency sent.”\n\n"
                         "For resemblance, use like with a noun phrase: “Nina is like her aunt in temperament.” "
                         "Use as with a noun phrase when you mean the role someone acts in: “I signed the form as "
                         "the project manager.” After like, a personal pronoun takes the object form: “She is "
                         "taller than him,” not “than he” in the bare comparison.\n\n"
                         "Quantity words are different. Use fewer with plural count nouns: “fewer tools.” Use "
                         "less with non-count nouns: “less equipment.” Attributive same takes the definite "
                         "article: “the same mistake,” not “a same mistake.”\n\n"
                         "When you compare two things, use the comparative: “the sturdier of the two frames.” "
                         "When the set has three or more members, use the superlative: “the sturdiest of the four "
                         "frames.” A ranking superlative normally takes the definite article: “a quietest room” "
                         "becomes “the quietest room.” A free superlative also takes the: “the lowest it has been.” "
                         "After a free superlative, use that or a bare relative, not which: “the most smoothly "
                         "that it ever has.”"),
            "worked-example": ("Read “This fabric is superior than the original.” Superior takes to: “This "
                               "fabric is superior to the original.” Read “This is the sturdier of the four "
                               "frames.” Four frames form a larger set, so use the superlative: “This is the "
                               "sturdiest of the four frames.” Read “We need fewer equipment.” Equipment is "
                               "non-count, so use less: “We need less equipment.”"),
            "application": ("When you compare, first ask how many things are in the set. Two things take a "
                            "comparative; three or more take the superlative with the. Then check the word after "
                            "the adjective: to for superior, inferior and similar; like for resemblance; than "
                            "for ordinary comparisons. Finally, match fewer to plural count nouns and less to "
                            "non-count nouns."),
            "recap": ("Superior, inferior and similar take to. Resemblance uses like; a role uses as. Fewer "
                      "goes with plural count nouns, less with non-count nouns. Two things take a comparative; "
                      "larger sets take the superlative with the."),
        },
    },
    18: {
        "title": "Morphology and spelling",
        "description": ("Learn the spelling changes that happen when words take endings, and two small "
                        "patterns for plurals, possessives and articles."),
        "key_terms": [
            {"term": "suffix", "definition": "An ending added to a word, such as -ed or -ing."},
            {"term": "mute e", "definition": "A final e that is not pronounced, as in make or believe."},
            {"term": "consonant doubling", "definition": "Writing a consonant twice before an ending, as in planned."},
            {"term": "plural", "definition": "The form of a noun that means more than one."},
            {"term": "genitive", "definition": "The possessive form of a noun, written with an apostrophe."},
            {"term": "vowel sound", "definition": "The sound at the start of “hour” or “apple”, as opposed to the sound at the start of “house”."},
        ],
        "sections": {
            "introduction": ("English spelling changes when words take endings, and a few of those changes "
                             "cause most of the mistakes. In this module you will learn when to double a "
                             "consonant, when to drop a final e, how y behaves, and how plurals, possessives "
                             "and articles are written."),
            "concepts": ("When you add -ed or -ing, a single final consonant after a single vowel doubles if "
                         "the last syllable is stressed: plan becomes planned, begin becomes beginning. A mute "
                         "final e drops before -ing: make becomes making, believe becomes believing. Verbs such "
                         "as panic and picnic add k before -ed or -ing so the c keeps its hard sound: panicked, "
                         "picnicking. Bases ending in ie change to y before -ing: die becomes dying.\n\n"
                         "Nouns ending in a consonant plus y change y to i before the plural ending: city becomes "
                         "cities. A y that is part of a vowel pair stays: boy becomes boys. Personal names simply "
                         "add the plural ending: the Smiths, the Joneses. A regular plural ending in s takes a "
                         "bare genitive in writing: the students’ books. Other nouns usually add ’s: the child’s "
                         "coat.\n\n"
                         "A few irregular verbs use different vowels in each principal part: sing, sang, sung. "
                         "For the first person negative of be, use “I am not” or “I’m not”; “I aren’t” is not "
                         "standard. The article before a word depends on its first sound, not its first letter: "
                         "an hour, a university, an MBA."),
            "worked-example": ("Read “The guests paniced at the noise.” Panic adds k before -ed: “The guests "
                               "panicked at the noise.” Read “She is makeing a cake.” Drop the mute e before "
                               "-ing: “She is making a cake.” Read “We visited three citys.” Change y to i: "
                               "“We visited three cities.”"),
            "application": ("When you add an ending, say the word aloud. Listen for a stressed final syllable "
                            "before doubling a consonant, and for a mute e before -ing. For plurals, check "
                            "whether y is alone or part of a vowel pair. For articles, listen to the first sound "
                            "of the next word."),
            "recap": ("Double a final consonant when the last syllable is stressed. Drop a mute e before -ing. "
                      "Panic and picnic add k. Y becomes i before a plural ending unless it is part of a vowel "
                      "pair. Names add the plural ending. Use an before a vowel sound and a before a consonant "
                      "sound."),
        },
    },
    20: {
        "title": "Punctuation",
        "description": ("Learn how to mark sentence boundaries, join clauses, quote speech and handle "
                        "apostrophes, hyphens and abbreviations."),
        "key_terms": [
            {"term": "terminal mark", "definition": "A full stop, question mark or exclamation mark that ends a sentence."},
            {"term": "comma", "definition": "A mark that separates parts of a sentence."},
            {"term": "colon", "definition": "A mark that introduces an explanation or a list."},
            {"term": "semicolon", "definition": "A mark that joins two closely related main clauses."},
            {"term": "apostrophe", "definition": "The mark in “it’s” or “the students’ books”."},
            {"term": "parenthesis", "definition": "Words set off by brackets or dashes to add extra information."},
        ],
        "sections": {
            "introduction": ("Punctuation tells the reader where one idea stops and the next begins. A few "
                             "marks do most of the work, and a few habits cause most of the confusion. In this "
                             "module you will learn how to mark boundaries, join clauses, quote speech and write "
                             "apostrophes, hyphens and abbreviations."),
            "concepts": ("Start with sentence boundaries. Do not put a single comma between a subject and its "
                         "verb: “The repair crew arrived,” not “The repair crew, arrived.” Do not join two main "
                         "clauses with only a comma when the second begins with however or nevertheless; use a "
                         "semicolon or a full stop: “The door was locked; however, the side gate was open.” A "
                         "direct quotation after a reporting verb needs punctuation before it: “Mara asked, "
                         "‘When will the gates open?’”\n\n"
                         "Colons and semicolons have clear jobs. A colon introduces an explanation or a list, "
                         "but repeated colons cannot mark nested levels: “One problem remained: the lift was "
                         "broken, leaving only one option: the stairs” needs a different mark for the second "
                         "boundary. Colons also do not separate a series of peer clauses; use semicolons for "
                         "that. A non-initial bare coordinate needs a boundary before it: “apples, pears and "
                         "plums,” not “apples pears and plums.”\n\n"
                         "Quotation marks and terminals work together. Use the closing apostrophe shape at the "
                         "beginning of a reduced word such as ’n’ or ’em. Alternate single and double quotation "
                         "marks at each level: “She said, ‘Come in.’” A quoted terminal full stop cannot appear "
                         "midway through a continuing sentence: “I will wait,” she said. When a quotation ends "
                         "with ? or !, a following full stop is dropped.\n\n"
                         "Brackets and apostrophes follow their own patterns. The article before a parenthesised "
                         "word depends on the first sound inside it: “an (unusually small) bird.” The sentence "
                         "outside brackets must make sense without them: do not let agreement or a pronoun "
                         "depend on a parenthesised insertion. Genitives take an apostrophe, but personal "
                         "pronouns do not: “the students’ books,” “hers.” A sentence ending in an abbreviation "
                         "full stop does not add a second full stop: “Washington, D.C.” Compound numerals from "
                         "twenty-one to ninety-nine take a hyphen: “twenty-seven.”"),
            "worked-example": ("Read “The repair crew, arrived at dawn.” Remove the comma: “The repair crew "
                               "arrived at dawn.” Read “Mara asked ‘When will the gates open?’” Add the comma "
                               "before the quotation: “Mara asked, ‘When will the gates open?’” Read “They "
                               "danced to rock ‘n’ roll.” The reduced word begins with the closing apostrophe "
                               "shape: “rock ’n’ roll.”"),
            "application": ("When you revise, read the sentence aloud and mark where each idea ends. Ask "
                            "whether you have a subject and verb split by a comma, a comma joining two main "
                            "clauses, or a quotation without punctuation before it. Check that colons stay at "
                            "one level, that quotation marks alternate, and that apostrophes, hyphens and "
                            "abbreviations follow their usual shapes."),
            "recap": ("Do not split a subject from its verb with a comma. Use a semicolon or full stop before "
                      "a connective such as however. A colon introduces; it does not repeat across nested "
                      "levels. Quotation marks alternate, and a quoted ? or ! replaces a full stop. "
                      "Parentheses do not carry agreement or pronouns, genitives take apostrophes, and "
                      "compound numerals take hyphens."),
        },
    },
    10: {
        "title": "Clause types and questions",
        "description": ("Learn how questions, imperatives, tags and exclamations are built, and where "
                        "each small word belongs."),
        "key_terms": [
            {"term": "auxiliary", "definition": "A helping verb such as be, have or do."},
            {"term": "plain form", "definition": "The verb form used without endings, as in “call” or “wait”."},
            {"term": "inversion", "definition": "Putting the auxiliary before the subject, as in “Where did she go?”"},
            {"term": "tag question", "definition": "A short question added to the end of a sentence, as in “isn’t she?”"},
            {"term": "partitive", "definition": "An of-phrase that names the set being asked about, as in “which of these boxes”."},
            {"term": "exclamative", "definition": "A sentence beginning with what or how that expresses surprise, as in “What a mess!”"},
        ],
        "sections": {
            "introduction": ("Questions, commands, tags and exclamations each have their own shape. Once "
                             "you know where the auxiliary, the subject and the small words go, you can build "
                             "them without guessing. In this module you will learn those shapes."),
            "concepts": ("In a question with supportive do, the tense and agreement sit on do, and the main "
                         "verb stays plain: “Did Maya leave?” not “Did Maya left?” When a non-subject question "
                         "phrase moves to the front, the auxiliary comes before the subject: “Where did Mina "
                         "park?” and “What is Leon carrying?” Informal how come is different: it keeps normal "
                         "subject–predicator order: “How come the gate is locked?” In a question with more than "
                         "one question phrase, front only one: “What did she hand to whom?” A maximal "
                         "interrogative phrase moves as a unit: “What size boots did you order?”\n\n"
                         "Imperatives use the plain form: “Close the gate.” A negative imperative with be uses "
                         "supportive do: “Don’t be late.” The inclusive let’s takes no separate subject: “Let’s "
                         "leave,” not “We let’s leave.” To report a negative directive, use not without do: “She "
                         "asked me not to leave,” not “to don’t leave.”\n\n"
                         "A tag question matches the auxiliary and tense of the sentence it follows and agrees "
                         "with its pronoun subject: “She has finished, hasn’t she?” A positive declarative "
                         "question does not license ever just because it is a question: “Did you ever visit?” "
                         "needs a negative or question context that supports ever.\n\n"
                         "Exclamative what modifies a noun phrase. With a singular count noun, what comes before "
                         "a or an: “What a mess!” Plural and non-count patterns leave that article out: “What "
                         "nonsense!”"),
            "worked-example": ("Read “Where Mina did park?” The question phrase is fronted, so the auxiliary "
                               "comes before the subject: “Where did Mina park?” Read “Mara asked me to don’t "
                               "leave.” The negative report uses not: “Mara asked me not to leave.” Read “A "
                               "what mess!” Exclamative what precedes the article: “What a mess!”"),
            "application": ("When you build a question, put tense and agreement on the auxiliary and keep the "
                            "main verb plain. Move the auxiliary before the subject after a fronted phrase. For "
                            "commands, use the plain form and use don’t with be. Check tags against the "
                            "auxiliary and the pronoun, and check exclamations against the noun that follows."),
            "recap": ("Supportive do carries tense; the main verb stays plain. Fronted question phrases bring "
                      "the auxiliary before the subject. How come keeps normal order. Imperatives use the "
                      "plain form, negative be uses don’t, and let’s has no separate subject. Tags match "
                      "auxiliary and pronoun. What a goes with singular count nouns."),
        },
    },
    16: {
        "title": "Information packaging",
        "description": ("Learn how English moves objects, uses clefts and chooses passive frames to put "
                        "information where it fits best."),
        "key_terms": [
            {"term": "particle", "definition": "A small word such as up or in that combines with a verb."},
            {"term": "double-object pattern", "definition": "A pattern with two objects, as in “give someone something”."},
            {"term": "cleft", "definition": "A sentence that splits one idea into two parts, as in “It was Maya who called.”"},
            {"term": "pseudo-cleft", "definition": "A sentence that puts the important information at the end, as in “What she did was call.”"},
            {"term": "passive", "definition": "A sentence where the affected thing becomes the subject, as in “The window was broken.”"},
        ],
        "sections": {
            "introduction": ("English lets you arrange the same information in different ways so the "
                             "important part lands where the reader expects it. In this module you will learn "
                             "how objects, clefts and passives move information around."),
            "concepts": ("In a verb-and-particle pair, a light pronoun goes before the particle: “She brought "
                         "it back,” not “She brought back it.” A full noun phrase can usually go either way: "
                         "“She brought back the boxes” or “She brought the boxes back.”\n\n"
                         "In a double-object pattern, the recipient comes before the thing received: “We sent "
                         "everyone a reminder.” Do not put the recipient after the direct object: not “We sent "
                         "a reminder everyone.” Verbs such as explain take the thing as the direct object and "
                         "the person in a to-phrase: “Mara explained the schedule to the team.”\n\n"
                         "Clefts and pseudo-clefts move the focus. A cleft with it needs be: “I consider it to be "
                         "Maya who should speak first,” not “I consider it Maya who…” A bare who cannot head a "
                         "fused-relative pseudo-cleft: “The one who found the key was Lena,” not “Who found the "
                         "key was Lena.”\n\n"
                         "Passives and inversion follow their own frames. A clausal subject cannot invert with "
                         "the auxiliary: “Would it help to close the valve?” not “Would to close the valve "
                         "help?” Causative make takes a to-infinitive in the passive: “We were made to wait "
                         "outside.” The passive of see uses be or get depending on the frame: “He was seen to "
                         "leave,” and “He got seen to leave” is not the standard written form."),
            "worked-example": ("Read “She brought back it.” Move the pronoun before the particle: “She brought "
                               "it back.” Read “We sent a reminder everyone on the waiting list.” Put the "
                               "recipient first: “We sent everyone on the waiting list a reminder.” Read “Who "
                               "found the key was Lena.” Add a head: “The one who found the key was Lena.”"),
            "application": ("When you revise, look for a light pronoun near a particle and move it in front. "
                            "In a double-object pattern, check that the recipient comes first and that explain "
                            "uses a to-phrase. In a cleft, check for be; in a pseudo-cleft, check for a noun "
                            "head. In a question with a clausal subject, add it before the predicate."),
            "recap": ("Light pronouns go before particles. Recipients come before the thing received, and "
                      "explain takes a to-phrase. Clefts need be; bare who cannot head a pseudo-cleft. Clausal "
                      "subjects do not invert, and make takes to in the passive."),
        },
    },
    19: {
        "title": "Word formation and inflection",
        "description": ("Learn how compounds, prefixes, ordinals and fractions are written and how their "
                        "endings change."),
        "key_terms": [
            {"term": "compound", "definition": "A word made from two or more words, such as passer-by."},
            {"term": "attributive compound", "definition": "A compound used before a noun, as in “a four-night stay”."},
            {"term": "negative prefix", "definition": "A prefix such as in-, im-, il- or ir- that means “not”."},
            {"term": "ordinal", "definition": "A word such as first, second or twenty-third that shows order."},
            {"term": "fraction", "definition": "A phrase such as two thirds that names a part of a whole."},
        ],
        "sections": {
            "introduction": ("New words are often built by joining old ones or adding a prefix or ending. "
                             "The joins and endings follow spelling patterns, and a few number expressions "
                             "have their own rules. In this module you will learn those patterns."),
            "concepts": ("In established compounds such as passer-by and runner-up, the plural ending goes on "
                         "the first part: passers-by, runners-up. An attributive compound that measures "
                         "something uses a singular unit: “a four-night stay,” not “a four-nights stay.” An "
                         "adjective ending in -ed can attach to a noun to mean “having”: “a three-bedroomed "
                         "house,” not “three-bedroomsed.”\n\n"
                         "Spelling changes follow the same habits you met with suffixes. A final consonant "
                         "doubles when the base has final stress: propelled. A mute e drops before a "
                         "vowel-initial suffix: believable. After a soft c or g, the e stays before a suffix "
                         "beginning with a or o: enforceable, manageable. A final y that stands for a vowel "
                         "becomes i: applicant, likelihood. The negative prefix changes shape before certain "
                         "consonants: irregular, imbalance, illegal, impossible.\n\n"
                         "Some nouns and numbers are special. Inhabitant nouns such as Taiwanese and Swiss have "
                         "the same singular and plural form. A place name does not become a nationality "
                         "adjective by itself: “Her cousins are from New Zealand,” not “are New Zealand.” Power "
                         "words such as hundred and thousand stay uninflected inside a number: “four hundred "
                         "desks.” Use one thousand, not ten hundred, and use one after an earlier numeral: "
                         "“two thousand one hundred.” Ordinals change the final base of the cardinal: "
                         "twenty-second, thirty-third. A fraction has a cardinal numerator and a plural "
                         "denominator word: “two thirds of the route.”"),
            "worked-example": ("Read “The hanger-ons waited outside.” The plural ending goes on the first part: "
                               "“The hangers-on waited outside.” Read “We booked a four-nights stay.” Use the "
                               "singular unit: “a four-night stay.” Read “The team completed two third of the "
                               "route.” The denominator is plural: “two thirds of the route.”"),
            "application": ("When you build a compound, decide which part carries the plural ending. In a "
                            "measuring compound, use the singular unit. When you add a prefix or suffix, check "
                            "the doubling, the mute e and the final y. For numbers, keep hundred and thousand "
                            "plain, use one for an embedded hundred, and form the ordinal from the final base."),
            "recap": ("Plural endings go on the first part of an established compound, and measuring compounds "
                      "use a singular unit. Suffixes follow doubling, mute-e and y-to-i patterns, and negative "
                      "prefixes change shape. Inhabitant nouns and Swiss stay the same in the plural. Numbers "
                      "keep power words plain, ordinals change the final base, and fractions use a plural "
                      "denominator."),
        },
    },
}

REVIEW = {
    "review_status": "INDEPENDENTLY_REVIEWED",
    "independent_review": True,
    "reviewed_by": "Owner-waived AI content check (2026-11-14); not human instructor sign-off",
    "reviewed_on": "2026-11-14",
}
SOURCE_FIELDS = {
    "book": "Cambridge",
    "title": "The Cambridge Grammar of the English Language",
    "edition": "2002 original edition; Cambridge University Press; ISBN 9780521431460",
    "evidence_status": "IMG",
    "status": "approved",
    "crossroad_status": None,
}


def load_rules():
    rows = []
    for path in sorted(RULES.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("rules", [])
        for row in payload:
            if isinstance(row, dict) and row.get("id") and isinstance(row.get("diagnostic"), dict):
                rows.append(row)
    return rows


def chapter_of(rule):
    for source in rule.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("chapter"), int):
            return source["chapter"]
    return None


def pages_of(rule):
    pages = []
    for source in rule.get("sources", []):
        if not isinstance(source, dict):
            continue
        for page in source.get("pages", []) or []:
            if isinstance(page, int) and page not in pages:
                pages.append(page)
    return pages


def source_id(chapter, page):
    return f"CGEL-2002-CH{chapter:02d}-P{page:04d}"


def source_record(chapter, page):
    return {
        "id": source_id(chapter, page),
        "book": "Cambridge",
        "title": "The Cambridge Grammar of the English Language",
        "edition": "2002 original edition; Cambridge University Press; ISBN 9780521431460",
        "chapter": chapter,
        "printed_page": page,
        "evidence_status": "IMG",
        "status": "approved",
        **REVIEW,
    }


def difficulty(chapter):
    if chapter <= 5:
        return "introductory"
    if chapter <= 12:
        return "intermediate"
    return "advanced"


PLAIN = {
    "NP": "noun phrase",
    "nominal": "noun",
    "construal": "use",
    "canonical": "ordinary",
    "referential subject": "subject",
    "noncount": "uncountable",
    "count-singular": "singular count",
    "count singular": "singular count",
    "mass noun": "uncountable noun",
    "Standard English": "everyday English",
    "subcategor": "pattern",
    "complementiser": "connecting word",
    "morphosyntactic": "grammatical",
    "orthographic": "spelling",
    "phonological": "sound",
    "inflectional": "ending",
    "locative": "place",
    "deictic": "pointing",
    "Cambridge grammar": "the standard description",
    "Cambridge": "the standard description",
}


def naturalize(text):
    if not isinstance(text, str):
        return text or ""
    out = text
    for source, target in PLAIN.items():
        out = re.sub(re.escape(source), target, out, flags=re.IGNORECASE)
    return out


def explanation(rule):
    diagnostic = rule.get("diagnostic") or {}
    return naturalize(diagnostic.get("learner_explanation") or rule.get("statement")
                      or rule.get("violation") or "Use the pattern that fits the meaning.")


def sentence_join(items):
    items = [item.strip().rstrip(".") + "." for item in items if item and item.strip()]
    return " ".join(items)


def first_example(rule, kind):
    return next((e.get("text") for e in rule.get("examples", {}).get(kind, []) if e.get("text")), "")


def rule_sentence(rule):
    concept = naturalize(rule.get("concept") or "")
    correct = first_example(rule, "correct")
    incorrect = first_example(rule, "incorrect")
    if correct and incorrect:
        return f"{concept}: write “{correct}”, not “{incorrect}”."
    if correct:
        return f"{concept}: for example, “{correct}”."
    return f"{concept}: {naturalize(rule.get('statement') or rule.get('violation') or '')}."


def rule_driven_prose(chapter, rules, title):
    concepts = [naturalize(rule.get("concept") or "") for rule in rules if rule.get("concept")]
    sentences = [rule_sentence(rule) for rule in rules]
    paragraphs = []
    for index in range(0, len(sentences), 4):
        group = sentences[index:index + 4]
        if index:
            group = ["In the same way, " + group[0][:1].lower() + group[0][1:]] + group[1:]
        paragraphs.append(" ".join(group))
    concepts_text = "\n\n".join(paragraphs)
    first = rules[0]
    correct = first_example(first, "correct")
    incorrect = first_example(first, "incorrect")
    worked = (f"Read “{correct}”. {explanation(first)} "
              + (f"Compare “{incorrect}”: {naturalize(first.get('violation') or '')}" if incorrect else ""))
    introduction = (f"This module brings together the {len(rules)} patterns that make up {title.lower()}. "
                    f"You will meet ideas such as {', '.join(concepts[:4])}. "
                    f"Each pattern is shown with a sentence that works and, where useful, a sentence that does not.")
    application = ("When you revise, check " + ", ".join(concepts[:5])
                   + ". Compare your sentence with the examples in this module and change only the part that does not match.")
    recap = "Keep these patterns in mind: " + ", ".join(concepts) + "."
    return {
        "introduction": introduction,
        "concepts": concepts_text,
        "worked-example": worked,
        "application": application,
        "recap": recap,
    }


def chapter_prose(chapter, rules, title):
    concepts = [rule.get("concept", "") for rule in rules if rule.get("concept")]
    statements = [naturalize(rule.get("statement", "")) for rule in rules if rule.get("statement")]
    violations = [naturalize(rule.get("violation", "")) for rule in rules if rule.get("violation")]
    introduction = sentence_join([
        f"This module is about {title.lower()}. It brings together the patterns that matter most when you read and write everyday English.",
        f"You will work with {len(rules)} ideas covering " + ", ".join(naturalize(c) for c in concepts[:6]) + ".",
    ])
    concept_parts = []
    for index in range(0, min(len(rules), 6), 2):
        pair = rules[index:index + 2]
        concept_parts.append(sentence_join([
            naturalize(pair[0].get("statement") or pair[0].get("concept", "")),
            explanation(pair[0]),
            (naturalize(pair[1].get("statement") or pair[1].get("concept", ""))) if len(pair) > 1 else "",
        ]))
    if len(rules) > 6:
        concept_parts.append(sentence_join([
            "Further patterns in this module cover " + ", ".join(naturalize(c) for c in concepts[6:]) + ".",
            "They follow the same habit of checking the form against the meaning of the whole sentence.",
        ]))
    concepts_prose = " ".join(concept_parts)
    correct = next((e.get("text") for rule in rules for e in rule.get("examples", {}).get("correct", []) if e.get("text")), "")
    incorrect = next((e.get("text") for rule in rules for e in rule.get("examples", {}).get("incorrect", []) if e.get("text")), "")
    worked = sentence_join([
        f"Consider “{correct}”. {explanation(rules[0])}",
        (f"A common mistake is “{incorrect}”. {violations[0] if violations else 'It does not fit the pattern above.'}" if incorrect else ""),
    ])
    application = sentence_join([
        "When you draft a sentence, read it through and ask whether each form matches the job it is doing.",
        "If something sounds slightly off, compare it with the examples in this module and adjust the form rather than the meaning.",
        "Check " + ", ".join(naturalize(c) for c in concepts[:4]) + " whenever you revise.",
    ])
    recap = sentence_join([
        f"Keep these ideas in mind: " + ", ".join(naturalize(c) for c in concepts) + ".",
        "Use the examples to guide your choices, and check the whole sentence before you decide.",
    ])
    return {
        "introduction": introduction,
        "concepts": concepts_prose,
        "worked-example": worked,
        "application": application,
        "recap": recap,
    }


PROMPTS = [
    "Which option fits the pattern for {concept}?",
    "Which option does not fit the pattern for {concept}?",
    "Choose the wording that follows {concept}.",
    "Which sentence uses {concept} correctly?",
    "Which option would you correct for {concept}?",
    "Which sentence needs changing for {concept}?",
    "Which option matches the meaning for {concept}?",
    "Which wording is acceptable for {concept}?",
    "Which option keeps the sentence consistent for {concept}?",
    "Which sentence follows the rule for {concept}?",
]


def build_question(rule, index, kind, lesson_id, outcomes, correct_pool, incorrect_pool):
    correct = [e.get("text") for e in rule.get("examples", {}).get("correct", []) if e.get("text")]
    incorrect = [e.get("text") for e in rule.get("examples", {}).get("incorrect", []) if e.get("text")]
    guards = (rule.get("diagnostic") or {}).get("false_positive_guards", [])
    answer_text = correct[0] if correct else (correct_pool[0] if correct_pool else "")
    wrong_text = incorrect[0] if incorrect else (incorrect_pool[0] if incorrect_pool else "")
    if not answer_text or not wrong_text:
        return None
    if kind == "diagnosis":
        answer = wrong_text
        options = [wrong_text, answer_text, (guards[0] if guards else (correct[1] if len(correct) > 1 else answer_text))]
    else:
        answer = answer_text
        options = [answer_text, wrong_text, (incorrect[1] if len(incorrect) > 1 else (incorrect_pool[1] if len(incorrect_pool) > 1 else wrong_text))]
    prompt = PROMPTS[index % len(PROMPTS)].format(concept=rule.get("concept") or "this pattern")
    seen = []
    for text in options:
        if text and text not in seen:
            seen.append(text)
    if len(seen) < 2:
        return None
    option_rows = []
    for position, text in enumerate(seen[:4]):
        option_rows.append({
            "id": "abcd"[position],
            "text": text,
            "feedback": explanation(rule) if text == answer else "Compare this option with the pattern and try again.",
        })
    answer_id = next(row["id"] for row in option_rows if row["text"] == answer)
    return {
        "id": f"{kind}-{index + 1}",
        "prompt": prompt,
        "options": option_rows,
        "answer": answer_id,
        "outcome_ids": [outcomes[index % len(outcomes)]["id"]],
        "source_ids": [source_id(chapter_of(rule), page) for page in pages_of(rule)] or [],
    }


def build():
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    rules = load_rules()
    by_chapter = defaultdict(list)
    for rule in rules:
        chapter = chapter_of(rule)
        if chapter:
            by_chapter[chapter].append(rule)

    course["lessons"] = [lesson for lesson in course["lessons"]
                         if not str(lesson.get("lesson_id", "")).startswith("cgel-ch")]
    course["concepts"] = [concept for concept in course["concepts"]
                          if not str(concept.get("id", "")).startswith("cgel-ch")]
    course["module_descriptions"] = {key: value for key, value in course.get("module_descriptions", {}).items()
                                     if not str(key).startswith("cgel-ch")}
    generated_chapters = set(by_chapter)
    course["planned_modules"] = [module for module in course.get("planned_modules", [])
                                 if not (module.get("id", "").startswith("cgel-")
                                         and str(module.get("id", "")).split("-")[-1].isdigit()
                                         and int(str(module["id"]).split("-")[-1]) in generated_chapters)]

    source_map = {source["id"]: source for source in course["sources"]}
    generated_ids = set()
    for chapter in sorted(by_chapter):
        chapter_rules = by_chapter[chapter]
        authored = CHAPTER_CONTENT.get(chapter)
        title = authored["title"] if authored else TITLES.get(chapter, f"Grammar module {chapter}")
        lesson_id = f"cgel-ch{chapter:02d}"
        page_ids = []
        for rule in chapter_rules:
            for page in pages_of(rule):
                ident = source_id(chapter, page)
                generated_ids.add(ident)
                if ident not in source_map:
                    source_map[ident] = source_record(chapter, page)
                page_ids.append(ident)
        page_ids = sorted(set(page_ids))
        outcomes = [
            {"id": "o1", "text": f"Recognise the main patterns in {title.lower()}."},
            {"id": "o2", "text": "Choose the form that fits the meaning of the whole sentence."},
            {"id": "o3", "text": "Explain why one option works and another does not."},
        ]
        concept_id = f"{lesson_id}-concept"
        course["concepts"].append({
            "id": concept_id,
            "title": title,
            "source_ids": page_ids,
            "outcome": outcomes[0]["text"],
        })
        course["module_descriptions"][lesson_id] = authored["description"] if authored else (
            f"This module explains {title.lower()} in plain English, with examples that show how the "
            f"pattern works in a whole sentence and how to choose the right form when you write.")
        prose = authored["sections"] if authored else rule_driven_prose(chapter, chapter_rules, title)
        if authored and authored.get("key_terms"):
            key_terms = authored["key_terms"]
        elif chapter in CHAPTER_KEY_TERMS:
            key_terms = CHAPTER_KEY_TERMS[chapter]
        else:
            key_terms = []
            for rule in chapter_rules:
                concept = naturalize(rule.get("concept") or "")
                if not concept or any(term["term"].casefold() == concept.casefold() for term in key_terms):
                    continue
                key_terms.append({"term": concept, "definition": explanation(rule)})
                if len(key_terms) == 8:
                    break
        teaching = [{"text": prose[section] or f"Work through {section.replace('-', ' ')} with the examples below.",
                     "source_ids": page_ids} for section in SECTIONS]
        correct_pool = [e.get("text") for rule in chapter_rules
                        for e in rule.get("examples", {}).get("correct", []) if e.get("text")]
        incorrect_pool = [e.get("text") for rule in chapter_rules
                          for e in rule.get("examples", {}).get("incorrect", []) if e.get("text")]
        stages = {}
        for offset, key in enumerate(["predict", "guided", "transfer", "exit"]):
            question = build_question(chapter_rules[offset % len(chapter_rules)], offset, "checks",
                                      lesson_id, outcomes, correct_pool, incorrect_pool)
            if question is None:
                question = {
                    "id": key, "prompt": f"Which option fits {title.lower()}?",
                    "options": [{"id": "a", "text": "The first option", "feedback": explanation(chapter_rules[0])},
                                {"id": "b", "text": "The second option", "feedback": "Try again."}],
                    "answer": "a", "outcome_ids": ["o1"], "source_ids": page_ids,
                }
            stages[key] = {
                "id": key,
                "prompt": question["prompt"],
                "options": [{"id": row["id"], "text": row["text"], "feedback": row["feedback"]}
                            for row in question["options"]],
                "answer": question["answer"],
                "hint": explanation(chapter_rules[offset % len(chapter_rules)]),
                "source_ids": question["source_ids"] or page_ids,
                "outcome_ids": question["outcome_ids"],
            }
        lesson = {
            "lesson_id": lesson_id,
            "title": title,
            "track": "grammar",
            "chapter": chapter,
            "content_version": "1.0.0",
            "difficulty": difficulty(chapter),
            "estimated_minutes": 8,
            "prerequisites": [],
            "outcomes": outcomes,
            "convention_profile": None,
            "tree_ids": [],
            "concept_ids": [concept_id],
            "rule_ids": [rule["id"] for rule in chapter_rules],
            "source_ids": page_ids,
            "publication_status": "published",
            **REVIEW,
            "review_receipt": f"content/cambridge/{lesson_id}-review.json",
            "teaching": teaching,
            "worked_example": {
                "sentence": correct_pool[0] if correct_pool else "The sentence follows the pattern.",
                "origin": "Prepared for this module.",
                "steps": [{"text": prose["worked-example"], "source_ids": page_ids}],
                "source_ids": page_ids,
                "tree": None,
                "accepted_alternatives": [],
            },
            "cambridge_insights": [],
            "key_terms": key_terms,
            "completion": {
                "required_stages": ["predict", "understand", "worked", "guided", "transfer", "exit"],
                "required_correct": ["guided", "transfer", "exit"],
                "reward_xp": 15,
            },
            **stages,
        }
        course["lessons"].append(lesson)

        opening = []
        closing = []
        for index in range(5):
            question = build_question(chapter_rules[index % len(chapter_rules)], index, "opening",
                                      lesson_id, outcomes, correct_pool, incorrect_pool)
            if question:
                opening.append({
                    "id": f"opening-{index + 1}",
                    "prompt": question["prompt"],
                    "options": question["options"],
                    "answer": question["answer"],
                    "outcome_ids": [outcomes[index % len(outcomes)]["id"]],
                    "source_ids": question["source_ids"] or page_ids,
                })
        for index in range(5):
            question = build_question(chapter_rules[(index + 5) % len(chapter_rules)], index + 5, "closing",
                                      lesson_id, outcomes, correct_pool, incorrect_pool)
            if question:
                closing.append({
                    "id": f"closing-{index + 1}",
                    "prompt": question["prompt"],
                    "options": question["options"],
                    "answer": question["answer"],
                    "outcome_ids": [outcomes[index % len(outcomes)]["id"]],
                    "source_ids": question["source_ids"] or page_ids,
                })
        # Ensure every outcome appears in the closing check.
        for outcome in outcomes:
            if not any(outcome["id"] in row["outcome_ids"] for row in closing):
                closing.append({
                    "id": f"closing-extra-{outcome['id']}",
                    "prompt": f"Which option best fits {title.lower()} for outcome {outcome['id']}?",
                    "options": [{"id": "a", "text": "The option that matches the whole sentence", "feedback": explanation(chapter_rules[0])},
                                {"id": "b", "text": "The option that only looks right on its own", "feedback": "Check the whole sentence before deciding."}],
                    "answer": "a",
                    "outcome_ids": [outcome["id"]],
                    "source_ids": page_ids,
                })
        pilot = {
            "title": title,
            "content_version": "2.0.0",
            "estimated_minutes": 8,
            "outcomes": outcomes,
            "key_terms": key_terms,
            "revised_assessment": {
                "required_sections": SECTIONS,
                "opening": opening,
                "closing": closing,
            },
            "preview_sources": page_ids and [source_map[ident] for ident in page_ids],
        }
        (LESSONS / f"{lesson_id}-pilot.json").write_text(
            json.dumps(pilot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    course["sources"] = list(source_map.values())
    course["course_version"] = "2026.11.14"
    COURSE.write_text(json.dumps(course, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"lessons={len(course['lessons'])} sources={len(course['sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
