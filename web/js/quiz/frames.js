// ---------------------------------------------------------------------------
// Structural wrapper library for the Matrix Quiz.
//
// The quiz banks no longer hard-code two or three sentence frames per rule.
// Instead every rule supplies a minimal, well-formed *core clause* pair
// (a correct core and an incorrect core that differ only in the target form),
// and this module wraps that core in 40 structurally distinct sentences per
// difficulty tier. Two items therefore never share a sentence structure -- each
// wrapper produces a different tree shape (bare clause, trailing adjunct,
// fronted adjunct, coordination, subordination, reported/embedded clause, ...).
//
// A wrapper receives:
//   c.first -> the core clause exactly as given (used when the core must stay
//              sentence-initial, e.g. capitalization rules)
//   c.mid   -> the core clause with a lowered first letter (used when the core
//              is embedded after a comma, subordinator, or bridge verb)
//
// Each wrapper is { id, f, first }. `first: true` means the core clause is the
// very first thing in the sentence, so a lower-case-initial error survives.
// Rules that test capitalization use the dedicated CAP list.
//
// The wrapper scaffolds deliberately avoid constructions the constraint matrix
// treats as ambiguous (bare comma splices, sentential 'which', 'since' +
// present, negative polarity items) so a scaffold never introduces noise -- all
// signal must come from the rule's own core clause.
// ---------------------------------------------------------------------------

const PROPER_NAMES = new Set(['Tom', 'Anna', 'Bob', 'Sue', 'Ann', 'Ben', 'Sam',
  'Kim', 'Mia', 'Zoe', 'Amy', 'Roy', 'Dan', 'Leo', 'Max', 'Eve', 'Kay', 'Lee',
  'Ned', 'Rob', 'Ted', 'Val', 'Ian', 'Owen', 'Ivy', 'Noah', 'Eli', 'Uma', 'Zed']);

const lowerFirst = (s) => {
  if (!s) return s;
  // Never de-capitalize the pronoun "I" (or "I'm"/"I've"/"I'd"/"I'll").
  if (/^I(['’]|\s|$)/.test(s)) return s;
  // Keep proper names capitalized even in the middle of a sentence.
  const lead = s.match(/^[A-Za-z]+/);
  if (lead && PROPER_NAMES.has(lead[0])) return s;
  return s.charAt(0).toLowerCase() + s.slice(1);
};

const wrap = (id, f, first = false) => ({ id, f, first });

// ---- Easy: single clause + light adjuncts / simple coordination -----------
export const EASY = [
  wrap('bare', (c) => `${c.first}.`, true),
  wrap('again', (c) => `${c.first} again.`, true),
  wrap('today', (c) => `${c.first} today.`, true),
  wrap('here', (c) => `${c.first} here.`, true),
  wrap('in-the-morning', (c) => `${c.first} in the morning.`, true),
  wrap('in-the-evening', (c) => `${c.first} in the evening.`, true),
  wrap('at-the-office', (c) => `${c.first} at the office.`, true),
  wrap('at-school', (c) => `${c.first} at school.`, true),
  wrap('near-the-river', (c) => `${c.first} near the river.`, true),
  wrap('by-the-window', (c) => `${c.first} by the window.`, true),
  wrap('on-the-bus', (c) => `${c.first} on the bus.`, true),
  wrap('with-her-friend', (c) => `${c.first} with her friend.`, true),
  wrap('for-the-team', (c) => `${c.first} for the team.`, true),
  wrap('during-the-break', (c) => `${c.first} during the break.`, true),
  wrap('after-work', (c) => `${c.first} after work.`, true),
  wrap('before-dinner', (c) => `${c.first} before dinner.`, true),
  wrap('in-the-garden', (c) => `${c.first} in the garden.`, true),
  wrap('under-the-tree', (c) => `${c.first} under the tree.`, true),
  wrap('on-the-farm', (c) => `${c.first} on the farm.`, true),
  wrap('at-the-station', (c) => `${c.first} at the station.`, true),
  wrap('front-again', (c) => `Again, ${c.mid}.`),
  wrap('front-today', (c) => `Today, ${c.mid}.`),
  wrap('front-morning', (c) => `In the morning, ${c.mid}.`),
  wrap('front-office', (c) => `At the office, ${c.mid}.`),
  wrap('front-river', (c) => `Near the river, ${c.mid}.`),
  wrap('front-break', (c) => `During the break, ${c.mid}.`),
  wrap('front-bus', (c) => `On the bus, ${c.mid}.`),
  wrap('front-garden', (c) => `In the garden, ${c.mid}.`),
  wrap('front-after', (c) => `After work, ${c.mid}.`),
  wrap('and-agree', (c) => `${c.first}, and I agree.`, true),
  wrap('but-disagreed', (c) => `${c.first}, but I disagreed.`, true),
  wrap('so-waited', (c) => `${c.first}, so we waited.`, true),
  wrap('yet-stayed', (c) => `${c.first}, yet we stayed.`, true),
  wrap('and-smiled', (c) => `${c.first}, and she smiled.`, true),
  wrap('because-fine', (c) => `${c.first} because the weather was fine.`, true),
  wrap('while-played', (c) => `${c.first} while the children played.`, true),
  wrap('although-late', (c) => `${c.first} although it was late.`, true),
  wrap('when-arrived', (c) => `When I arrived, ${c.mid}.`),
  wrap('after-meeting', (c) => `After the meeting, ${c.mid}.`),
  wrap('in-fact', (c) => `In fact, ${c.mid}.`),
];

// ---- Medium: fronted adverbials, reported / mental embedding ---------------
export const MEDIUM = [
  wrap('and-important', (c) => `${c.first}, and that is important.`, true),
  wrap('so-relieved', (c) => `${c.first}, so we were relieved.`, true),
  wrap('but-disagreed', (c) => `${c.first}, but I disagreed.`, true),
  wrap('yet-stayed', (c) => `${c.first}, yet we stayed.`, true),
  wrap('obviously', (c) => `Obviously, ${c.mid}.`),
  wrap('clearly', (c) => `Clearly, ${c.mid}.`),
  wrap('luckily', (c) => `Luckily, ${c.mid}.`),
  wrap('strangely', (c) => `Strangely, ${c.mid}.`),
  wrap('fortunately', (c) => `Fortunately, ${c.mid}.`),
  wrap('in-my-opinion', (c) => `In my opinion, ${c.mid}.`),
  wrap('to-my-surprise', (c) => `To my surprise, ${c.mid}.`),
  wrap('without-doubt', (c) => `Without any doubt, ${c.mid}.`),
  wrap('as-a-rule', (c) => `As a rule, ${c.mid}.`),
  wrap('in-general', (c) => `In general, ${c.mid}.`),
  wrap('on-the-whole', (c) => `On the whole, ${c.mid}.`),
  wrap('as-expected', (c) => `As expected, ${c.mid}.`),
  wrap('in-fact', (c) => `In fact, ${c.mid}.`),
  wrap('i-think-that', (c) => `I think that ${c.mid}.`),
  wrap('i-noticed-that', (c) => `I noticed that ${c.mid}.`),
  wrap('i-believe-that', (c) => `I believe that ${c.mid}.`),
  wrap('i-know-that', (c) => `I know that ${c.mid}.`),
  wrap('i-hope-that', (c) => `I hope that ${c.mid}.`),
  wrap('it-seems-that', (c) => `It seems that ${c.mid}.`),
  wrap('it-is-clear-that', (c) => `It is clear that ${c.mid}.`),
  wrap('it-is-obvious-that', (c) => `It is obvious that ${c.mid}.`),
  wrap('it-is-possible-that', (c) => `It is possible that ${c.mid}.`),
  wrap('everyone-agrees', (c) => `Everyone agrees that ${c.mid}.`),
  wrap('she-said-that', (c) => `She said that ${c.mid}.`),
  wrap('he-thinks-that', (c) => `He thinks that ${c.mid}.`),
  wrap('they-believe-that', (c) => `They believe that ${c.mid}.`),
  wrap('the-fact-is', (c) => `The fact is that ${c.mid}.`),
  wrap('it-appears-that', (c) => `It appears that ${c.mid}.`),
  wrap('we-all-knew', (c) => `We all knew that ${c.mid}.`),
  wrap('i-remember-that', (c) => `I remember that ${c.mid}.`),
  wrap('she-mentions-that', (c) => `She mentions that ${c.mid}.`),
  wrap('he-explained-that', (c) => `He explained that ${c.mid}.`),
  wrap('they-noticed-that', (c) => `They noticed that ${c.mid}.`),
  wrap('the-teacher-said', (c) => `The teacher said that ${c.mid}.`),
  wrap('my-friend-thinks', (c) => `My friend thinks that ${c.mid}.`),
  wrap('it-turns-out', (c) => `It turns out that ${c.mid}.`),
];

// ---- Hard: nested relatives, double embedding, heavy adjuncts -------------
export const HARD = [
  wrap('rel-who-heard', (c) => `${c.first}, and everyone who heard it agreed.`, true),
  wrap('rel-who-waited', (c) => `${c.first}, although the people who were waiting had left.`, true),
  wrap('rel-who-called', (c) => `${c.first}, because the manager who called earlier had insisted.`, true),
  wrap('rel-who-played', (c) => `${c.first}, while the children who were playing watched.`, true),
  wrap('rel-students-passed', (c) => `${c.first}, and the students who had studied passed easily.`, true),
  wrap('rel-staff-remained', (c) => `${c.first}, while the staff who remained were tired.`, true),
  wrap('rel-that-wrote', (c) => `${c.first}, and the report that she wrote was accurate.`, true),
  wrap('rel-that-discussed', (c) => `${c.first}, but the plan that we discussed was better.`, true),
  wrap('rel-that-arrived', (c) => `${c.first}, so the group that arrived celebrated.`, true),
  wrap('rel-who-trained', (c) => `${c.first}, yet the coach who trained them was proud.`, true),
  wrap('arrive-and-agree', (c) => `When I arrived, ${c.mid}, and everyone agreed.`),
  wrap('late-and-stayed', (c) => `Although it was late, ${c.mid}, and we stayed.`),
  wrap('rain-and-waited', (c) => `Because it was raining, ${c.mid}, and we waited inside.`),
  wrap('waited-and-passed', (c) => `While we waited, ${c.mid}, and the time passed.`),
  wrap('after-you-asked', (c) => `After you asked, ${c.mid}, and I answered.`),
  wrap('meeting-and-left', (c) => `After the meeting, ${c.mid}, and we left.`),
  wrap('break-and-notes', (c) => `Before the break, ${c.mid}, and she took notes.`),
  wrap('bell-and-arrived', (c) => `When the bell rang, ${c.mid}, and the class arrived.`),
  wrap('double-know', (c) => `I know that she thinks that ${c.mid}.`),
  wrap('double-agreed', (c) => `He said that everyone agreed that ${c.mid}.`),
  wrap('report-shows', (c) => `It seems that the report shows that ${c.mid}.`),
  wrap('teacher-noticed', (c) => `I believe that the teacher noticed that ${c.mid}.`),
  wrap('always-believed', (c) => `I have always believed that ${c.mid}.`),
  wrap('widely-known', (c) => `It is widely known that ${c.mid}.`),
  wrap('all-agreed', (c) => `We all agreed that ${c.mid}.`),
  wrap('clearly-showed', (c) => `The report clearly showed that ${c.mid}.`),
  wrap('scientists-believe', (c) => `Scientists believe that ${c.mid}.`),
  wrap('teacher-explained', (c) => `The teacher explained that ${c.mid}.`),
  wrap('friend-told', (c) => `My friend told me that ${c.mid}.`),
  wrap('important-note', (c) => `It is important to note that ${c.mid}.`),
  wrap('before-dawn', (c) => `In the quiet hours before dawn, ${c.mid}.`),
  wrap('office-station', (c) => `At the small office near the station, ${c.mid}.`),
  wrap('great-care', (c) => `With great care and patience, ${c.mid}.`),
  wrap('long-meeting', (c) => `After a long and difficult meeting, ${c.mid}.`),
  wrap('between-classes', (c) => `During the break between classes, ${c.mid}.`),
  wrap('bright-lights', (c) => `Under the bright lights of the stage, ${c.mid}.`),
  wrap('puzzled-everyone', (c) => `For reasons that puzzled everyone, ${c.mid}.`),
  wrap('whole-team', (c) => `To the surprise of the whole team, ${c.mid}.`),
  wrap('without-complaint', (c) => `Without a single word of complaint, ${c.mid}.`),
  wrap('long-before', (c) => `Long before the meeting started, ${c.mid}.`),
];

// ---- Capitalization-safe wrappers: the core clause must stay sentence-initial
export const CAP = [
  wrap('cap-bare', (c) => `${c.first}.`, true),
  wrap('cap-again', (c) => `${c.first} again.`, true),
  wrap('cap-today', (c) => `${c.first} today.`, true),
  wrap('cap-here', (c) => `${c.first} here.`, true),
  wrap('cap-in-the-morning', (c) => `${c.first} in the morning.`, true),
  wrap('cap-in-the-evening', (c) => `${c.first} in the evening.`, true),
  wrap('cap-at-the-office', (c) => `${c.first} at the office.`, true),
  wrap('cap-at-school', (c) => `${c.first} at school.`, true),
  wrap('cap-near-the-river', (c) => `${c.first} near the river.`, true),
  wrap('cap-by-the-window', (c) => `${c.first} by the window.`, true),
  wrap('cap-on-the-bus', (c) => `${c.first} on the bus.`, true),
  wrap('cap-with-her-friend', (c) => `${c.first} with her friend.`, true),
  wrap('cap-for-the-team', (c) => `${c.first} for the team.`, true),
  wrap('cap-during-the-break', (c) => `${c.first} during the break.`, true),
  wrap('cap-after-work', (c) => `${c.first} after work.`, true),
  wrap('cap-before-dinner', (c) => `${c.first} before dinner.`, true),
  wrap('cap-in-the-garden', (c) => `${c.first} in the garden.`, true),
  wrap('cap-under-the-tree', (c) => `${c.first} under the tree.`, true),
  wrap('cap-on-the-farm', (c) => `${c.first} on the farm.`, true),
  wrap('cap-at-the-station', (c) => `${c.first} at the station.`, true),
  wrap('cap-at-noon', (c) => `${c.first} at noon.`, true),
  wrap('cap-at-night', (c) => `${c.first} at night.`, true),
  wrap('cap-on-monday', (c) => `${c.first} on Monday.`, true),
  wrap('cap-in-the-kitchen', (c) => `${c.first} in the kitchen.`, true),
  wrap('cap-at-the-clinic', (c) => `${c.first} at the clinic.`, true),
  wrap('cap-near-the-gate', (c) => `${c.first} near the gate.`, true),
  wrap('cap-behind-the-house', (c) => `${c.first} behind the house.`, true),
  wrap('cap-around-the-corner', (c) => `${c.first} around the corner.`, true),
  wrap('cap-along-the-road', (c) => `${c.first} along the road.`, true),
  wrap('cap-and-agree', (c) => `${c.first}, and I agree.`, true),
  wrap('cap-but-disagreed', (c) => `${c.first}, but I disagreed.`, true),
  wrap('cap-so-waited', (c) => `${c.first}, so we waited.`, true),
  wrap('cap-yet-stayed', (c) => `${c.first}, yet we stayed.`, true),
  wrap('cap-and-smiled', (c) => `${c.first}, and she smiled.`, true),
  wrap('cap-because-fine', (c) => `${c.first} because the weather was fine.`, true),
  wrap('cap-while-played', (c) => `${c.first} while the children played.`, true),
  wrap('cap-although-late', (c) => `${c.first} although it was late.`, true),
  wrap('cap-unless-rain', (c) => `${c.first} unless it rains.`, true),
  wrap('cap-after-guests', (c) => `${c.first} after the guests arrived.`, true),
  wrap('cap-before-meeting', (c) => `${c.first} before the meeting ended.`, true),
];

export const WRAPPERS = { easy: EASY, medium: MEDIUM, hard: HARD };

const core = (s) => ({ first: s, mid: lowerFirst(s) });

// Wrap a single core pair across every wrapper in a tier. Returns one item per
// wrapper so every structure is distinct. `make(bad, good)` builds the item.
export function wrapCore(difficulty, badCore, goodCore, make) {
  const list = WRAPPERS[difficulty] || EASY;
  const b = core(badCore);
  const g = core(goodCore);
  return list.map((w) => make(w.f(b), w.f(g)));
}

// For rules whose error is at the very start of the clause (capitalization):
// only wrappers that keep the core sentence-initial preserve the error.
export function wrapCoreInitial(badCore, goodCore, make) {
  const b = core(badCore);
  const g = core(goodCore);
  return CAP.map((w) => make(w.f(b), w.f(g)));
}

// Resolve the i-th core pair from a rule's content source. A rule may pass a
// single pair, an array of pairs, or a generator (i) => pair. The generator form
// is what makes each item a *different scenario*: the rule composes a distinct
// subject/verb/object for every slot, so no two questions share a context.
const pairAt = (source, i) => {
  if (typeof source === 'function') return source(i);
  if (Array.isArray(source)) return source[i % source.length];
  return source;
};

// High-level helper used by the rule banks. Content (the scenario) comes from
// the rule, structure from the wrapper for this slot, so the 40 items differ in
// both the situation described and the shape of the sentence.
export function ruleItems(difficulty, source) {
  const list = WRAPPERS[difficulty] || EASY;
  return list.map((w, i) => {
    const p = pairAt(source, i);
    const b = core(p.bad);
    const g = core(p.good);
    return { bad: w.f(b), good: w.f(g), explanation: p.explanation };
  });
}

// Capitalization variant: the core stays sentence-initial in every wrapper so a
// missing capital is preserved.
export function ruleItemsInitial(source) {
  return CAP.map((w, i) => {
    const p = pairAt(source, i);
    const b = core(p.bad);
    const g = core(p.good);
    return { bad: w.f(b), good: w.f(g), explanation: p.explanation };
  });
}
