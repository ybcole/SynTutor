// ---------------------------------------------------------------------------
// Hand-authored paragraph banks for the Matrix Quiz.
//
// Every rule's quiz now presents a short PARAGRAPH (one coherent idea) instead
// of a single sentence. Each paragraph has five sentences; one or two carry the
// rule's target error and the rest are already correct. The learner repairs the
// whole passage and it is graded sentence-by-sentence (see
// web/js/quiz/answer.js isParagraphQuizAnswerCorrect).
//
// A paragraph is built with the helpers below:
//   ok('A correct sentence.')                  -> already-correct sentence
//   p([[bad, good], ok('...'), ...], 'why')    -> one paragraph item
//
// `bad` is what the learner sees, `good` is the expected correction, and the
// per-paragraph `explanation` states what is wrong. Rules listed here override
// the single-sentence generators in ./sN.js (see ./index.js materializePool).
//
// To add a paragraph, append a p(...) entry to the rule's array, then run
// `npm run build:master`.

const ok = (sentence) => [sentence, sentence];

const p = (rows, explanation) => ({
  bad: rows.map((row) => row[0]).join(' '),
  good: rows.map((row) => row[1]).join(' '),
  sentences: rows.map(([bad, good]) => ({ bad, good })),
  explanation,
});

export const PARAGRAPHS = {
  // =========================================================================
  // Section 1 — Word forms
  // =========================================================================

  // 1.2 Irregular noun plurals
  '1.2': [
    p([
      ok('The village school held its spring fair on Saturday, and by mid-morning the whole playground was full.'),
      ['Several childs ran straight to the face-painting stall.', 'Several children ran straight to the face-painting stall.'],
      ok('Meanwhile, their parents bought cakes and lemonade from the volunteers.'),
      ['Two mans helped carry the heavy tables outside.', 'Two men helped carry the heavy tables outside.'],
      ok('By sunset, everyone had helped tidy the playground before heading home.'),
    ], 'The irregular plurals are "children" (not "childs") and "men" (not "mans").'),
    p([
      ok('My grandmother keeps a small farm near the coast, where she has lived for forty years.'),
      ['She keeps three gooses and a dozen chickens.', 'She keeps three geese and a dozen chickens.'],
      ok('Every morning, before breakfast, she collects the eggs they have laid.'),
      ['The two mouses in the barn always hide behind the grain sacks.', 'The two mice in the barn always hide behind the grain sacks.'],
      ok('Her grandchildren love visiting the animals each summer.'),
    ], 'The irregular plurals are "geese" (not "gooses") and "mice" (not "mouses").'),
    p([
      ok('The dentist greeted her young patient with a warm smile.'),
      ['"And how many tooths have you lost this year?" she asked.', '"And how many teeth have you lost this year?" she asked.'],
      ok('The boy thought for a moment and proudly counted them on his fingers.'),
      ['He then explained that his foots had grown two sizes since spring.', 'He then explained that his feet had grown two sizes since spring.'],
      ok('The dentist laughed, gave him a new brush, and sent him off with a sticker.'),
    ], 'The irregular plurals are "teeth" (not "tooths") and "feet" (not "foots").'),
    p([
      ok('The science class was studying a chapter about life in the sea.'),
      ['The teacher showed them photos of several unusual fishes from the deep ocean.', 'The teacher showed them photos of several unusual fish from the deep ocean.'],
      ok('One picture showed a whole shoal moving together like a single animal.'),
      ['Afterwards, the students wrote their favourite facts about the sheeps on the board.', 'Afterwards, the students wrote their favourite facts about the sheep on the board.'],
      ok('They finished the lesson with a short quiz.'),
    ], 'The plurals "fish" and "sheep" do not change form.'),
    p([
      ok('The newspaper office was unusually busy before the morning edition.'),
      ['Two womans were editing the front-page stories.', 'Two women were editing the front-page stories.'],
      ok('Meanwhile, a reporter checked the names in every headline.'),
      ['The editor asked the childs to wait quietly in the lobby.', 'The editor asked the children to wait quietly in the lobby.'],
      ok('The presses rolled exactly on time.'),
    ], 'The irregular plurals are "women" (not "womans") and "children" (not "childs").'),
  ],

  // 1.3 Possessive 's / s'
  '1.3': [
    p([
      ok('The football team gathered on the field after school.'),
      ['The boys coach blew the whistle twice.', "The boys' coach blew the whistle twice."],
      ok('At once, the players lined up in two neat rows.'),
      ['Each players jersey had a number on the back.', "Each player's jersey had a number on the back."],
      ok('They practiced passing until the sun went down.'),
    ], 'Plural owners take an apostrophe after the s ("boys\'"), and a single owner takes \'s ("player\'s").'),
    p([
      ok('My sister borrowed three books from the library.'),
      ok('She finished the first story in a single evening.'),
      ['The writers name was printed on the cover.', "The writer's name was printed on the cover."],
      ok('When she returned it, she left a kind note for the librarian.'),
      ['The libraries copy had a torn page.', "The library's copy had a torn page."],
    ], 'A single owner takes \'s: "writer\'s name", "library\'s copy".'),
    p([
      ok('The neighbours share a large garden that lies behind their houses.'),
      ['One afternoon, the childrens toys were scattered all across the lawn.', "One afternoon, the children's toys were scattered all across the lawn."],
      ok('Everyone helped gather them into two big boxes.'),
      ['Then their parents chairs were set out around a wooden table.', "Then their parents' chairs were set out around a wooden table."],
      ok('The families talked together until it grew dark.'),
    ], 'Irregular plurals add \'s ("children\'s"); regular plural owners add just an apostrophe ("parents\'").'),
    p([
      ok('Our dog loves chasing the ball in the park.'),
      ['The dogs tail wagged the whole way there.', "The dog's tail wagged the whole way there."],
      ok('Once we arrived, he barked happily at all the other animals.'),
      ['Two dogs owners waved to us from a nearby bench.', "Two dogs' owners waved to us from a nearby bench."],
      ok('We walked home just before it started to rain.'),
    ], 'One dog takes "dog\'s"; several dogs take "dogs\'".'),
    p([
      ok('The shop on the corner sells fresh bread every morning.'),
      ['Long before opening, the bakers oven filled the street with a warm smell.', "Long before opening, the baker's oven filled the street with a warm smell."],
      ok('By seven, customers were already queuing outside the door.'),
      ['The morning customers baskets were soon full.', "The morning customers' baskets were soon full."],
      ok('By nine, the shelves were nearly empty.'),
    ], 'A single baker is "baker\'s"; several customers are "customers\'".'),
  ],

  // 1.4 Verb endings (-s, -ed, -ing)
  '1.4': [
    p([
      ok('The runners had trained hard all autumn.'),
      ['Every morning she runing around the lake before school.', 'Every morning she runs around the lake before school.'],
      ok('Her coach timed each lap on a small silver watch.'),
      ['Yesterday she stoped only once to tie her shoe.', 'Yesterday she stopped only once to tie her shoe.'],
      ok('Now she hopes to enter the spring race.'),
    ], 'The third-person form is "runs", and the past tense of "stop" doubles the final consonant: "stopped".'),
    p([
      ok('The children stayed behind to help their teacher tidy the classroom.'),
      ['One boy writting the date on the board while the others worked.', 'One boy wrote the date on the board while the others worked.'],
      ok('A girl arranged the books neatly on the shelf.'),
      ['Together they carryed the chairs to the back wall.', 'Together they carried the chairs to the back wall.'],
      ok('By the time the bell rang, the room looked neat again.'),
    ], 'The past forms are "wrote" and "carried" (change y to i before -ed).'),
    p([
      ok('My aunt teaches music at the local school.'),
      ['Every Wednesday she watchs the choir rehearse after lessons.', 'Every Wednesday she watches the choir rehearse after lessons.'],
      ok('The singers often practise the same song for weeks on end.'),
      ['At home she studys each score carefully, marking every entry.', 'At home she studies each score carefully, marking every entry.'],
      ok('Her students always applaud at the end.'),
    ], 'Verbs ending in -ch or a consonant + y take -es: "watches", "studies".'),
    p([
      ok('The farmer rises before the sun each day.'),
      ['By first light he milking the cows while the dog waits.', 'By first light he milks the cows while the dog waits.'],
      ok('Soon afterwards, the hens scatter across the yard.'),
      ['Last week he fixxed the broken gate before breakfast.', 'Last week he fixed the broken gate before breakfast.'],
      ok('The farm was quiet again by lunchtime.'),
    ], 'The simple present is "milks"; the past tense is "fixed".'),
    p([
      ok('The class planned a trip to the coast for the end of term.'),
      ['They packing their bags the night before, hardly able to sleep.', 'They packed their bags the night before, hardly able to sleep.'],
      ok('The bus left the school gates at seven sharp.'),
      ['Everyone enjoyied the ride along the cliffs.', 'Everyone enjoyed the ride along the cliffs.'],
      ok('They promised to visit again next year.'),
    ], 'The past forms are "packed" and "enjoyed".'),
  ],

  // 1.5 Irregular past tense
  '1.5': [
    p([
      ok('My family visited a new city last weekend.'),
      ['On Saturday we goed to the old museum near the river.', 'On Saturday we went to the old museum near the river.'],
      ok('The building was full of ancient tools and strange maps.'),
      ['We taked dozens of photographs in the main hall.', 'We took dozens of photographs in the main hall.'],
      ok('The afternoon passed far too quickly.'),
    ], 'The past forms are "went" (not "goed") and "took" (not "taked").'),
    p([
      ok('Last summer I stayed with my grandparents by the lake.'),
      ['Every afternoon we eat ice cream together on the porch.', 'Every afternoon we ate ice cream together on the porch.'],
      ok('While we sat there, Grandpa told stories about his childhood.'),
      ['One evening he catched a huge fish right by the old jetty.', 'One evening he caught a huge fish right by the old jetty.'],
      ok('I still keep a photo of that day.'),
    ], 'The past forms are "ate" and "caught".'),
    p([
      ok('Anna received a bright red bicycle for her birthday.'),
      ['She rided it around the park all morning.', 'She rode it around the park all morning.'],
      ok('Her brother chased after her, struggling to keep up.'),
      ['Later they buyed matching helmets at the shop.', 'Later they bought matching helmets at the shop.'],
      ok('By evening, Anna could ride without wobbling.'),
    ], 'The past forms are "rode" and "bought".'),
    p([
      ok('The students prepared a play for the end of term.'),
      ['They writed the script together in class over several weeks.', 'They wrote the script together in class over several weeks.'],
      ok("With the teacher's help, they built a simple set for the stage."),
      ['On the opening night, the whole hall gived them a huge cheer.', 'On the opening night, the whole hall gave them a huge cheer.'],
      ok('Everyone agreed the show was a great success.'),
    ], 'The past forms are "wrote" and "gave".'),
    p([
      ok('Our neighbour keeps bees in his back garden.'),
      ['Last spring he bringed home a new hive from the market.', 'Last spring he brought home a new hive from the market.'],
      ok('The bees soon settled near the old apple tree.'),
      ['At first he thinked they would leave, but they stayed.', 'At first he thought they would leave, but they stayed.'],
      ok('Now the garden is full of busy workers.'),
    ], 'The past forms are "brought" and "thought".'),
  ],

  // 1.6 Irregular past participle
  '1.6': [
    p([
      ok('The travellers reached the mountain village just as night fell.'),
      ['They had went by bus and then on foot up the steep track.', 'They had gone by bus and then on foot up the steep track.'],
      ok('Inside the inn, a warm fire was already waiting.'),
      ['Someone had took their bags up to the rooms already.', 'Someone had taken their bags up to the rooms already.'],
      ok('They slept deeply after the long climb.'),
    ], 'After "had" the past participle is required: "gone" and "taken".'),
    p([
      ok('The library held a display of old wartime letters.'),
      ['A historian had wrote careful notes beside each one.', 'A historian had written careful notes beside each one.'],
      ok('Visitors read the stories with great interest.'),
      ['Many had saw the same letters online before.', 'Many had seen the same letters online before.'],
      ok('The display stayed open for a whole month.'),
    ], 'After "had" use "written" and "seen".'),
    p([
      ok('By noon, the whole kitchen smelled wonderful.'),
      ['The cooks had began preparing the feast at dawn.', 'The cooks had begun preparing the feast at dawn.'],
      ok('Long tables had been laid out across the hall.'),
      ['By the time we arrived, guests had already ate most of the bread.', 'By the time we arrived, guests had already eaten most of the bread.'],
      ok('The celebration lasted well into the night.'),
    ], 'After "had" use "begun" and "eaten".'),
    p([
      ok('The team had a difficult match on Saturday.'),
      ['By halftime they had went behind by two goals.', 'By halftime they had gone behind by two goals.'],
      ok('The captain called them together for a quiet talk.'),
      ['Soon after, a single goal had broke the deadlock.', 'Soon after, a single goal had broken the deadlock.'],
      ok('They won by the final whistle.'),
    ], 'After "had" use "gone" and "broken".'),
    p([
      ok('The gardener worked all through the spring.'),
      ['By April she had chose roses to climb the whole fence.', 'By April she had chosen roses to climb the whole fence.'],
      ok('As the warm weather came, the flowers opened one by one.'),
      ['Birds had flew over the wall to drink at the small pond.', 'Birds had flown over the wall to drink at the small pond.'],
      ok('Her garden won a prize at the fair.'),
    ], 'After "had" use "chosen" and "flown".'),
  ],

  // 1.7 Comparative / superlative formation
  '1.7': [
    p([
      ok('The class compared the model bridges they had built.'),
      ['Ben said his was more stronger than the rest.', 'Ben said his was stronger than the rest.'],
      ok('One by one, each group tested its model with small weights.'),
      ['In the end, Mia built the goodest arch in the room.', 'In the end, Mia built the best arch in the room.'],
      ok('The teacher praised every careful design.'),
    ], 'Use one comparative form only ("stronger" or "more strong"), and the irregular superlative of "good" is "best".'),
    p([
      ok('Three runners reached the final race of the day.'),
      ['Tom was the more fastest on the long straight.', 'Tom was the fastest on the long straight.'],
      ok('Anna, meanwhile, kept a steady pace just behind him.'),
      ['In the end, she was far more happier with her own time.', 'In the end, she was far happier with her own time.'],
      ok('Both agreed it had been a fair contest.'),
    ], 'Do not combine "more" with -er; use "fastest" and "happier".'),
    p([
      ok('The students measured two model towers side by side.'),
      ['At first the blue one looked more taller than the red one.', 'At first the blue one looked taller than the red one.'],
      ok('Carefully, they marked both heights on a chart.'),
      ['The red tower, however, had the baddest base of all.', 'The red tower, however, had the worst base of all.'],
      ok('So they rebuilt it with a wider stand.'),
    ], 'Use "taller" (not "more taller") and the irregular superlative "worst".'),
    p([
      ok('The shop sold fruit from farms in the surrounding valley.'),
      ['The owner boasted that these apples are gooder than the ones last week.', 'The owner boasted that these apples are better than the ones last week.'],
      ok('He arranged them in a tall pyramid near the window.'),
      ['The pears beside them had the most smallest labels.', 'The pears beside them had the smallest labels.'],
      ok('Everything was sold by the afternoon.'),
    ], 'The comparative of "good" is "better"; do not combine "most" with -est.'),
    p([
      ok('Two paths led up the hill behind the school.'),
      ['The left path was more easier to climb in dry weather.', 'The left path was easier to climb in dry weather.'],
      ok('Students preferred it especially after rain.'),
      ['The right path, though shorter, was the most steepest of the two.', 'The right path, though shorter, was the steepest of the two.'],
      ok('A wooden sign now marks both routes.'),
    ], 'Use "easier" and "steepest"; never double the degree word with -er/-est.'),
  ],

  // 1.8 Adverb formation
  '1.8': [
    p([
      ok('The choir spent the afternoon preparing for its winter concert.'),
      ['The singers practiced happyly for two whole hours.', 'The singers practiced happily for two whole hours.'],
      ok('Then the conductor raised her hands for silence.'),
      ['The soloist sang so good that everyone in the hall smiled.', 'The soloist sang so well that everyone in the hall smiled.'],
      ok('The audience clapped for a long time.'),
    ], 'The adverb of "happy" is "happily"; the adverb of "good" is "well".'),
    p([
      ok('The driver set off on a long trip overnight.'),
      ['Before leaving, he checked his mirrors careful.', 'Before leaving, he checked his mirrors carefully.'],
      ok('The roads were quiet after midnight.'),
      ['By dawn he arrived safe at the coast.', 'By dawn he arrived safely at the coast.'],
      ok('He was glad to finally rest.'),
    ], 'The adverbs are "carefully" and "safely".'),
    p([
      ok('The toddler was learning to walk on the soft grass.'),
      ['At first she moved slow across the lawn.', 'At first she moved slowly across the lawn.'],
      ok('Her mother knelt down and held out both hands.'),
      ["Soon, to everyone's delight, she could stand easy on her own.", "Soon, to everyone's delight, she could stand easily on her own."],
      ok('The whole family cheered.'),
    ], 'The adverbs are "slowly" and "easily".'),
    p([
      ok('The team worked together through a difficult project.'),
      ['They planned the schedule clever and shared the tasks fairly.', 'They planned the schedule cleverly and shared the tasks fairly.'],
      ok('Thanks to this, every task was finished before the deadline.'),
      ['At the end, the manager thanked them sincere for their effort.', 'At the end, the manager thanked them sincerely for their effort.'],
      ok('The project was praised by the whole company.'),
    ], 'The adverbs are "cleverly" and "sincerely".'),
    p([
      ok('An old clock hung in the quiet hallway.'),
      ['All night it ticked loud through the silent house.', 'All night it ticked loudly through the silent house.'],
      ok('Nobody had wound it in years.'),
      ['Then one morning it stopped sudden at seven.', 'Then one morning it stopped suddenly at seven.'],
      ok('So the family decided to have it repaired.'),
    ], 'The adverbs are "loudly" and "suddenly".'),
  ],

  // 1.9 Reflexive forms
  '1.9': [
    p([
      ok('The children were building a model castle in the yard.'),
      ['While gluing the towers, Tom cut hisself on a sharp edge.', 'While gluing the towers, Tom cut himself on a sharp edge.'],
      ok('His sister ran inside and fetched a plaster.'),
      ['After that, they reminded theirselves to be more careful.', 'After that, they reminded themselves to be more careful.'],
      ok('The castle was finished before dinner.'),
    ], 'The correct reflexives are "himself" and "themselves".'),
    p([
      ok('Our class wrote short stories for the school magazine.'),
      ['For once, I corrected my mistakes all by meself.', 'For once, I corrected my mistakes all by myself.'],
      ok('The teacher read two of the best stories aloud.'),
      ['We had divided the work fairly among ourself.', 'We had divided the work fairly among ourselves.'],
      ok('The magazine was printed on Friday.'),
    ], 'The correct reflexives are "myself" and "ourselves".'),
    p([
      ok('My grandmother lives alone in a small cottage.'),
      ['Even on her own, she looks after herselves very well.', 'Even on her own, she looks after herself very well.'],
      ok('She grows vegetables in the back garden.'),
      ['After retiring, she even taught hisself to paint.', 'After retiring, she even taught herself to paint.'],
      ok('Now her paintings hang in every room.'),
    ], 'The reflexive for "she" is "herself".'),
    p([
      ok('The players warmed up together before the match.'),
      ['Each of them stretched theirself near the goal.', 'Each of them stretched themselves near the goal.'],
      ok('Then the coach gathered them for a short, quiet talk.'),
      ['He told them to believe in hisself.', 'He told them to believe in themselves.'],
      ok('They went on to play their best game of the season.'),
    ], 'The reflexive matching "them" is "themselves".'),
    p([
      ok('We spent the whole weekend repairing the old boat.'),
      ['My brother and I sanded and painted it oursellves.', 'My brother and I sanded and painted it ourselves.'],
      ok('By Saturday, the fresh paint had dried in the sun.'),
      ok('"You should be proud of yourself too," my father said.'),
      ok('The boat was ready for the lake by Sunday.'),
    ], 'The correct reflexives are "ourselves" and "yourself".'),
  ],

  // 1.10 Homophones (its/it's, their/there/they're)
  '1.10': [
    p([
      ok('The puppy slept in a basket by the fire.'),
      ok('Now and then its tail twitched as it dreamed.'),
      ok('The children were careful not to wake it.'),
      ["They knew its time for a long rest.", "They knew it's time for a long rest."],
      ok('The little dog snored softly all evening.'),
    ], '"Its" shows possession; "it\'s" means "it is".'),
    p([
      ok('Two families met at the park on Sunday.'),
      ['They brought there own picnic baskets.', 'They brought their own picnic baskets.'],
      ok('While the children ran to the swings, the adults chose a bench.'),
      ["They said they're baskets would be safe beside them.", "They said their baskets would be safe beside them."],
      ok('Everyone stayed until the sun set.'),
    ], '"Their" shows possession; "they\'re" means "they are".'),
    p([
      ok('The students planned a trip to the science museum.'),
      ['They were excited about they\'re visit.', 'They were excited about their visit.'],
      ok('The bus left the school gate at eight.'),
      ["When they arrived, their were long queues at the entrance.", "When they arrived, there were long queues at the entrance."],
      ok('The exhibits were well worth the wait.'),
    ], 'Use "their" for possession and "there" for place or existence.'),
    p([
      ok('A new café opened near the station.'),
      ["From the street, it's windows were full of fresh bread.", "From the street, its windows were full of fresh bread."],
      ok('Office workers soon stopped in on their way to work.'),
      ["Many agreed that they're coffee was the best in town.", "Many agreed that their coffee was the best in town."],
      ok('The café was busy from morning to night.'),
    ], 'Possession uses "its" and "their"; "it\'s"/"they\'re" are contractions.'),
    p([
      ok('My cousin visits us every summer.'),
      ["She always says its too far to walk to the beach.", "She always says it's too far to walk to the beach."],
      ok('So we usually drive her there in the morning.'),
      ['She leaves her sandals their by the door.', 'She leaves her sandals there by the door.'],
      ok('We look forward to her visits.'),
    ], '"It\'s" = "it is"; "there" is the place.'),
  ],

  // 1.11 Contractions
  '1.11': [
    p([
      ok('The swimmers waited by the edge of the pool.'),
      ['"We dont want to start yet," they called out.', '"We don\'t want to start yet," they called out.'],
      ok('The coach checked the water temperature once more.'),
      ['"I cant hear you!" he shouted across the hall.', '"I can\'t hear you!" he shouted across the hall.'],
      ok('The whistle blew a moment later.'),
    ], 'Contractions need an apostrophe: "don\'t", "can\'t".'),
    p([
      ok('The library closes early on Fridays.'),
      ['The sign on the door says it wont open tomorrow.', "The sign on the door says it won't open tomorrow."],
      ok('Even so, students returned their books before lunch.'),
      ['"Im sorry for the short notice," said the librarian.', '"I\'m sorry for the short notice," said the librarian.'],
      ok('They thanked her and left quietly.'),
    ], 'Contractions need an apostrophe: "won\'t", "I\'m".'),
    p([
      ok('My friend moved to a new flat last month.'),
      ['She hasnt finished unpacking the kitchen yet.', "She hasn't finished unpacking the kitchen yet."],
      ok('Half-open boxes still fill the living room.'),
      ['"Ill call you when it\'s tidy," she promised.', '"I\'ll call you when it\'s tidy," she promised.'],
      ok('We plan to visit her on the weekend.'),
    ], 'Contractions need an apostrophe: "hasn\'t", "I\'ll".'),
    p([
      ok('The football match ended in a draw.'),
      ['The fans couldnt believe the final score.', "The fans couldn't believe the final score."],
      ok('In truth, both teams had played well.'),
      ['"Its a fair result," said the captain.', '"It\'s a fair result," said the captain.'],
      ok('They shook hands at the centre circle.'),
    ], 'Contractions need an apostrophe: "couldn\'t", "It\'s".'),
    p([
      ok('We planned a surprise meal for our father.'),
      ['He doesnt know about it yet, so please keep quiet.', "He doesn't know about it yet, so please keep quiet."],
      ok('My brother hid the cake in the garage.'),
      ['"Youre not going to believe this," he whispered.', '"You\'re not going to believe this," he whispered.'],
      ok('In the end, Dad was delighted with the whole evening.'),
    ], 'Contractions need an apostrophe: "doesn\'t", "You\'re".'),
  ],

  // 1.12 Spelling
  '1.12': [
    p([
      ok('The office handled hundreds of letters each week.'),
      ['Every morning they recieve a new bundle from the post.', 'Every morning they receive a new bundle from the post.'],
      ok('A clerk then sorts them all into two piles.'),
      ['Important ones are marked seperate from the rest.', 'Important ones are marked separate from the rest.'],
      ok('Nothing is filed before it is checked.'),
    ], 'The correct spellings are "receive" and "separate".'),
    p([
      ok('The teacher wrote the new words on the board.'),
      ['"Please definately bring your notebooks tomorrow," she said.', '"Please definitely bring your notebooks tomorrow," she said.'],
      ok('The class copied each word into their books carefully.'),
      ['She added that a short test will occured next Friday.', 'She added that a short test will occur next Friday.'],
      ok('The students promised to revise at home.'),
    ], 'The correct spellings are "definitely" and "occur".'),
    p([
      ok('My uncle sent a parcel from abroad.'),
      ['The adress on the label was hard to read.', 'The address on the label was hard to read.'],
      ok('Still, the postman delivered it the very next day.'),
      ['The package was sucessfully opened at dinner.', 'The package was successfully opened at dinner.'],
      ok('Everyone loved the small gifts inside.'),
    ], 'The correct spellings are "address" and "successfully".'),
    p([
      ok('The team planned a route across the hills.'),
      ['They studied the map until it was compleatly clear.', 'They studied the map until it was completely clear.'],
      ok('Each member packed a light bag for the walk.'),
      ['Then a sudden storm nearly ruined the whole embarassing trip.', 'Then a sudden storm nearly ruined the whole embarrassing trip.'],
      ok('Luckily, they reached the cabin safely before dark.'),
    ], 'The correct spellings are "completely" and "embarrassing".'),
    p([
      ok('The café has been open for a year.'),
      ['Its owner was worried about the buisness at first.', "Its owner was worried about the business at first."],
      ok('Soon, though, regular customers filled the small room.'),
      ['Today the coffee is famouse across the whole town.', 'Today the coffee is famous across the whole town.'],
      ok('A sign outside welcomes every visitor.'),
    ], 'The correct spellings are "business" and "famous".'),
  ],

  // 1.13 Numerals and measures
  '1.13': [
    p([
      ok('The charity organized a sponsored walk for the weekend.'),
      ['Three hundreds people joined the first group alone.', 'Three hundred people joined the first group alone.'],
      ok('They set off from the town square at nine sharp.'),
      ['Altogether, the route covered two thousands metres along the coast.', 'Altogether, the route covered two thousand metres along the coast.'],
      ok('A medic van followed the walkers the whole way.'),
    ], '"Hundred" and "thousand" stay singular after a number.'),
    p([
      ok('The bakery prepared for the harvest festival.'),
      ['Before dawn, the bakers made five dozens loaves.', 'Before dawn, the bakers made five dozen loaves.'],
      ok('They stacked them in crates near the door.'),
      ['By noon, a crowd of two hundreds customers had arrived.', 'By noon, a crowd of two hundred customers had arrived.'],
      ok('The stall sold out within an hour.'),
    ], '"Dozen" and "hundred" stay singular after a number.'),
    p([
      ok('The school raised money for new library books.'),
      ['In a single week, the pupils collected seven thousands coins.', 'In a single week, the pupils collected seven thousand coins.'],
      ok('Volunteers counted them in the assembly hall.'),
      ['In the end, the total came to four hundreds pounds.', 'In the end, the total came to four hundred pounds.'],
      ok('The library thanked everyone for their effort.'),
    ], '"Thousand" and "hundred" do not take -s after a number.'),
    p([
      ok('The runners trained for a long relay race.'),
      ['Between them, each team had to cover six thousands steps.', 'Between them, each team had to cover six thousand steps.'],
      ok('They practised on the track after school every day.'),
      ['One runner, however, missed three hundreds turns by mistake.', 'One runner, however, missed three hundred turns by mistake.'],
      ok('So the coach adjusted the plan for next week.'),
    ], '"Thousand" and "hundred" stay singular after a number.'),
    p([
      ok('The market attracted visitors from across the region.'),
      ['Across the centre, two thousands stalls filled the main street.', 'Across the centre, two thousand stalls filled the main street.'],
      ok('Near the old fountain, musicians played all afternoon.'),
      ['By evening, the organisers counted nine hundreds visitors.', 'By evening, the organisers counted nine hundred visitors.'],
      ok('Everyone agreed the day was a great success.'),
    ], '"Thousand" and "hundred" stay singular after a number.'),
  ],

  // =========================================================================
  // Section 2 — Agreement
  // =========================================================================

  // 2.1 Subject-verb, simple
  '2.1': [
    p([
      ok('The children settled into their seats as the lesson began.'),
      ['The teacher explain the new topic on the board.', 'The teacher explains the new topic on the board.'],
      ok('Everyone copied the examples into their notebooks.'),
      ['At the end, two students asks a question.', 'At the end, two students ask a question.'],
      ok('Then the bell rang for the morning break.'),
    ], 'A singular subject takes "explains"; a plural subject takes "ask".'),
    p([
      ok('The gardener works outside in every season.'),
      ['Early each morning she water the flowers.', 'Early each morning she waters the flowers.'],
      ok('Meanwhile, the roses grow along the whole fence.'),
      ['Two helpers trim the hedges every Friday.', 'Two helpers trim the hedges every Friday.'],
      ok('By the weekend, the garden always looks tidy.'),
    ], 'With "she" the verb is "waters"; a plural subject takes "trim".'),
    p([
      ok('My family is always busy on Sunday mornings.'),
      ['My mother bake fresh bread for breakfast.', 'My mother bakes fresh bread for breakfast.'],
      ok('Soon the whole kitchen fills with a warm smell.'),
      ['Meanwhile, my brothers helps her with the washing up.', 'Meanwhile, my brothers help her with the washing up.'],
      ok('We all eat together before noon.'),
    ], '"My mother" takes "bakes", and the plural "brothers" takes "help".'),
    p([
      ok('The manager checks the office every evening.'),
      ['He lock the doors and switch off the lights.', 'He locks the doors and switch off the lights.'],
      ok('The cleaners arrive early the next day.'),
      ['By then, the reports sits in a neat pile on the desk.', 'By then, the reports sit in a neat pile on the desk.'],
      ok('Nothing is left out of place.'),
    ], '"He" takes "locks", and the plural "reports" takes "sit".'),
    p([
      ok('A river runs quietly past the old mill.'),
      ['Under the wooden bridge, the water flow steadily.', 'Under the wooden bridge, the water flows steadily.'],
      ok('Willow trees line the far bank.'),
      ['On summer evenings, small boats sails past.', 'On summer evenings, small boats sail past.'],
      ok('The village is proud of its quiet river.'),
    ], '"Water" takes "flows", and the plural "boats" takes "sail".'),
  ],

  // 2.2 Subject-verb across intervening phrase
  '2.2': [
    p([
      ok('The workers carried new furniture into the room.'),
      ['The box of tools are too heavy to lift alone.', 'The box of tools is too heavy to lift alone.'],
      ok('So two people pushed it across the floor.'),
      ['The pile of chairs were stacked by the window.', 'The pile of chairs was stacked by the window.'],
      ok('By then, the room was ready for the meeting.'),
    ], 'The verb agrees with the head noun ("box", "pile"), not the nearby plural.'),
    p([
      ok('The school welcomed a group of new students.'),
      ['The teacher with the new pupils arrive early each day.', 'The teacher with the new pupils arrives early each day.'],
      ok('They gather near the main entrance.'),
      ['There, the head of the departments greet everyone at the gate.', 'There, the head of the departments greets everyone at the gate.'],
      ok('The first week passes quickly.'),
    ], 'The head noun is singular ("teacher", "head"), so the verb is singular.'),
    p([
      ok('A large crowd gathered for the town fair.'),
      ['The bag of apples are on the wooden table.', 'The bag of apples is on the wooden table.'],
      ok('Nearby, volunteers arranged the stalls along the street.'),
      ['The list of names were pinned to the board.', 'The list of names was pinned to the board.'],
      ok('By noon, the square was full of visitors.'),
    ], 'The subject is the singular "bag"/"list"; the plural phrase does not change the verb.'),
    p([
      ok('The boy in the blue jacket plays football well.'),
      ['The boy near the windows play every break.', 'The boy near the windows plays every break.'],
      ok('His friends cheer from the sideline.'),
      ['Meanwhile, the girl with the two dogs walk past the field.', 'Meanwhile, the girl with the two dogs walks past the field.'],
      ok('Practice ends before the sun sets.'),
    ], 'The head noun is singular ("boy", "girl"), so the verb is singular.'),
    p([
      ok('The museum opened a new gallery this spring.'),
      ['The collection of old coins were bought last year.', 'The collection of old coins was bought last year.'],
      ok('Visitors admire the shining displays.'),
      ['Across the main hall, the row of paintings hang.', 'Across the main hall, the row of paintings hangs.'],
      ok('The gallery soon became very popular.'),
    ], 'The head noun is singular ("collection", "row").'),
  ],

  // 2.3 Coordinated subjects (and / or / nor)
  '2.3': [
    p([
      ok('Two friends met at the corner café.'),
      ['Tom and Anna is planning a trip together.', 'Tom and Anna are planning a trip together.'],
      ok('They spread a map across the table.'),
      ['Tom or Anna have visited the coast before.', 'Tom or Anna has visited the coast before.'],
      ok('So they chose a route along the cliffs.'),
    ], '"And" makes the subject plural ("are"); with "or" the verb agrees with the nearer singular subject ("has").'),
    p([
      ok('The class chose a topic for the debate.'),
      ['The teacher and the students prepares questions together.', 'The teacher and the students prepare questions together.'],
      ok('Everyone then wrote a short opening speech.'),
      ['Neither the boys nor the girl know the answer.', 'Neither the boys nor the girl knows the answer.'],
      ok('Even so, the debate lasted a full hour.'),
    ], 'A joined subject is plural ("prepare"); with "neither...nor" the verb follows the nearer subject ("knows").'),
    p([
      ok('Our neighbours share a vegetable garden.'),
      ['My aunt and my uncle grows tomatoes there each summer.', 'My aunt and my uncle grow tomatoes there each summer.'],
      ok('The whole street enjoys the harvest.'),
      ['Either the carrots or the beans is ready to pick.', 'Either the carrots or the beans are ready to pick.'],
      ok('Any extra vegetables go to friends.'),
    ], 'A compound subject is plural ("grow"); with "either...or" the verb follows the nearer plural subject ("are").'),
    p([
      ok('The band rehearsed for the school concert.'),
      ['The singer and the drummer arrives first each time.', 'The singer and the drummer arrive first each time.'],
      ok('Together they set up their instruments near the stage.'),
      ['Neither the piano nor the guitars need tuning today.', 'Neither the piano nor the guitars need tuning today.'],
      ok('The rehearsal finished right on time.'),
    ], 'A compound subject takes a plural verb ("arrive"); "nor" follows the nearer plural ("need").'),
    p([
      ok('The project team met on Monday morning.'),
      ['The manager and the clerk was discussing the schedule.', 'The manager and the clerk were discussing the schedule.'],
      ok('They marked the deadlines on a chart.'),
      ['Either the designer or the writers has the final copy.', 'Either the designer or the writers have the final copy.'],
      ok('By the end, the team had agreed on a plan.'),
    ], 'A joined subject is plural ("were"); with "either...or" the verb follows the nearer plural ("have").'),
  ],

  // 2.4 Existential there
  '2.4': [
    p([
      ok('The hall filled quickly before the show.'),
      ['There is many reasons to arrive early.', 'There are many reasons to arrive early.'],
      ok('People queued beside the main doors.'),
      ['There was two long lines at the entrance.', 'There were two long lines at the entrance.'],
      ok('Even so, the performance began exactly on time.'),
    ], 'With a plural noun, use "there are" and "there were".'),
    p([
      ok('The kitchen prepared food for the whole school.'),
      ['There is several trays of sandwiches on the counter.', 'There are several trays of sandwiches on the counter.'],
      ok('Volunteers carried them to the dining room.'),
      ['There was a few cakes left for the second sitting.', 'There were a few cakes left for the second sitting.'],
      ok('Everyone found something they liked.'),
    ], 'The nouns "trays" and "cakes" are plural, so use "were" and "are".'),
    p([
      ok('The park was busy on Saturday afternoon.'),
      ['There is three football matches taking place.', 'There are three football matches taking place.'],
      ok('Near the fountain, children played happily.'),
      ['At the gate, there was dozens of bicycles.', 'At the gate, there were dozens of bicycles.'],
      ok('The day passed without a single complaint.'),
    ], 'Use "there are" with "matches" and "there were" with "bicycles".'),
    p([
      ok('The library added new books to its shelves.'),
      ['There is many readers in the study room.', 'There are many readers in the study room.'],
      ok('A volunteer helped at the front desk.'),
      ['There was only a few seats free near the window.', 'There were only a few seats free near the window.'],
      ok('The library closed at six as usual.'),
    ], 'The plural nouns require "there are" and "there were".'),
    p([
      ok('The market opened early on Sunday.'),
      ['There is hundreds of stalls along the street.', 'There are hundreds of stalls along the street.'],
      ok('Farmers sold fruit and vegetables.'),
      ['By the square, there was several musicians.', 'By the square, there were several musicians.'],
      ok('The market stayed busy all morning.'),
    ], 'With plural nouns, use "there are" and "there were".'),
  ],

  // 2.5 Collective and notional nouns
  '2.5': [
    p([
      ok('The local team prepared for the big final.'),
      ['The team are training on the field every evening.', 'The team is training on the field every evening.'],
      ok('Their supporters filled the stands.'),
      ['The crowd were very loud before kick-off.', 'The crowd was very loud before kick-off.'],
      ok('The match ended in a narrow win.'),
    ], 'A collective noun treated as one unit takes a singular verb ("is", "was").'),
    p([
      ok('A serious accident closed the main road.'),
      ['The police is investigating the cause.', 'The police are investigating the cause.'],
      ok('Witnesses gave statements to the officers.'),
      ['The public has been asked to stay away.', 'The public have been asked to stay away.'],
      ok('The road reopened the next morning.'),
    ], '"Police" and "public" are understood as plural and take plural verbs.'),
    p([
      ok('The family gathered for a special dinner.'),
      ['The family is arguing about where to sit.', 'The family are arguing about where to sit.'],
      ok('Grandmother placed the dishes on the table.'),
      ['Meanwhile, the government have announced a new plan.', 'Meanwhile, the government has announced a new plan.'],
      ok('The evening ended with old stories and laughter.'),
    ], 'When members act individually a collective may take "are"; as one body it takes "has".'),
    p([
      ok('The choir practised for the winter service.'),
      ['Tonight the choir are singing beautifully.', 'Tonight the choir is singing beautifully.'],
      ok('The audience listened in complete silence.'),
      ['Afterwards, the committee have reached a final decision.', 'Afterwards, the committee has reached a final decision.'],
      ok('The concert raised money for the hospital.'),
    ], 'A collective acting as one unit takes a singular verb ("is", "has").'),
    p([
      ok('The company opened a new branch in the city.'),
      ['The staff are unhappy about the new rules.', 'The staff is unhappy about the new rules.'],
      ok('Managers promised to review the schedule.'),
      ['In the meantime, the board have approved the yearly budget.', 'In the meantime, the board has approved the yearly budget.'],
      ok('The meeting ended on a positive note.'),
    ], 'Here each collective is treated as a single body, so it takes "is"/"has".'),
  ],

  // 2.6 Questions and inversion
  '2.6': [
    p([
      ok('The librarian tidied the shelves before closing.'),
      ['"Where is the new books about wildlife?" a reader asked.', '"Where are the new books about wildlife?" a reader asked.'],
      ok('She pointed to the far section at once.'),
      ['"Does the older students use the study room?" he added.', '"Do the older students use the study room?" he added.'],
      ok('The library closed at seven as usual.'),
    ], 'With a plural subject, use "Where are" and "Do".'),
    p([
      ok('The class prepared questions for the visiting author.'),
      ['"Why is the children waiting outside?" one asked.', '"Why are the children waiting outside?" one asked.'],
      ok('The teacher called them in one by one.'),
      ['"Does the teachers need more time?" another wondered.', '"Do the teachers need more time?" another wondered.'],
      ok('Everyone returned to their seats.'),
    ], 'Plural subjects take "are" and "Do".'),
    p([
      ok('The coach gathered the players after the match.'),
      ['"Where are the captain standing?" he asked.', '"Where is the captain standing?" he asked.'],
      ok('Then he pointed to the far corner.'),
      ['"Do the referee agree with the decision?" a player asked.', '"Does the referee agree with the decision?" a player asked.'],
      ok('The team shook hands and left.'),
    ], 'Singular subjects take "is" and "Does".'),
    p([
      ok('The shop opened early on Saturday.'),
      ['"Is the fresh cakes ready yet?" a customer asked.', '"Are the fresh cakes ready yet?" a customer asked.'],
      ok('The baker set them on the front shelf.'),
      ['"Are the price of bread going up?" she added.', '"Is the price of bread going up?" she added.'],
      ok('Customers quickly filled the small shop.'),
    ], 'Match the verb to the subject: "Are the cakes", "Is the price".'),
    p([
      ok('The hotel welcomed guests for the weekend.'),
      ['"Is the rooms ready for the visitors?" the porter asked.', '"Are the rooms ready for the visitors?" the porter asked.'],
      ok('Staff carried the bags to the top floor.'),
      ['"Do the manager work on Sundays?" a guest wondered.', '"Does the manager work on Sundays?" a guest wondered.'],
      ok('The guests thanked everyone warmly.'),
    ], 'Use "Are" with "rooms" and "Does" with the singular "manager".'),
  ],

  // 2.7 Relative clauses
  '2.7': [
    p([
      ok('The team celebrated after the final whistle.'),
      ['The boys who plays in the park are my neighbours.', 'The boys who play in the park are my neighbours.'],
      ok('They train together three times a week.'),
      ['The woman who sing at the concert lives nearby.', 'The woman who sings at the concert lives nearby.'],
      ok('Everyone clapped at the end.'),
    ], 'The verb in the relative clause agrees with its antecedent: "boys who play", "woman who sings".'),
    p([
      ok('The school hired a new music teacher.'),
      ['The students who learns quickly get extra work.', 'The students who learn quickly get extra work.'],
      ok('She sets weekly practice tasks for everyone.'),
      ['The girl who play the violin is very talented.', 'The girl who plays the violin is very talented.'],
      ok('The whole class enjoys the lessons.'),
    ], 'Use "who learn" with "students" and "who plays" with "girl".'),
    p([
      ok('A crowd gathered outside the old theatre.'),
      ['The actors who performs tonight are from the city.', 'The actors who perform tonight are from the city.'],
      ok('They rehearsed for several months.'),
      ['The director who choose the play is well known.', 'The director who chooses the play is well known.'],
      ok('The first show was a great success.'),
    ], 'Use "who perform" with "actors" and "who chooses" with "director".'),
    p([
      ok('The farmers sold their produce at the market.'),
      ['The customers who buys early get the best fruit.', 'The customers who buy early get the best fruit.'],
      ok('A queue formed before sunrise.'),
      ['The man who sell the honey is our neighbour.', 'The man who sells the honey is our neighbour.'],
      ok('The market closed by noon.'),
    ], 'Use "who buy" with "customers" and "who sells" with "man".'),
    p([
      ok('The volunteers cleaned the beach on Sunday.'),
      ['The helpers who arrives first collect the bags.', 'The helpers who arrive first collect the bags.'],
      ok('They worked until the tide came in.'),
      ['The child who find the most litter wins a prize.', 'The child who finds the most litter wins a prize.'],
      ok('The beach looked clean by the afternoon.'),
    ], 'Use "who arrive" with "helpers" and "who finds" with "child".'),
  ],

  // 2.8 Indefinite pronouns
  '2.8': [
    p([
      ok('The concert was sold out a week early.'),
      ['Everyone have a seat near the stage.', 'Everyone has a seat near the stage.'],
      ok('The band tuned their instruments backstage.'),
      ['Meanwhile, somebody forget their ticket at home.', 'Meanwhile, somebody forgot their ticket at home.'],
      ok('The show began right on time.'),
    ], 'Indefinite pronouns like "everyone" and "somebody" take singular verbs ("has", "forgot").'),
    p([
      ok('The club held its first meeting of the year.'),
      ['Everybody were excited about the new season.', 'Everybody was excited about the new season.'],
      ok('The coach explained the training plan.'),
      ['Even so, nobody know the final schedule yet.', 'Even so, nobody knows the final schedule yet.'],
      ok('They agreed to meet again next week.'),
    ], '"Everybody" and "nobody" take singular verbs ("was", "knows").'),
    p([
      ok('The kitchen prepared for the busy evening.'),
      ['Someone have left the oven on.', 'Someone has left the oven on.'],
      ok('The chef switched it off quickly.'),
      ['After all, nobody want to burn the roast.', 'After all, nobody wants to burn the roast.'],
      ok('The dinner service went smoothly.'),
    ], '"Someone" and "nobody" are singular here ("has", "wants").'),
    p([
      ok('The class discussed the new project.'),
      ['Anyone who finish early can help clean up.', 'Anyone who finishes early can help clean up.'],
      ok('They divided the tasks into small groups.'),
      ['Soon everyone in the group were ready to start.', 'Soon everyone in the group was ready to start.'],
      ok('The project was finished before the deadline.'),
    ], 'Use "finishes" and "was" with the singular indefinite subjects.'),
    p([
      ok('The travellers reached the mountain hut at dusk.'),
      ['Inside, someone have lit a fire in the hearth.', 'Inside, someone has lit a fire in the hearth.'],
      ok('They sat around it to keep warm.'),
      ['However, nobody were prepared for the cold night.', 'However, nobody was prepared for the cold night.'],
      ok('The morning brought clear skies and sunshine.'),
    ], '"Someone" and "nobody" take singular verbs ("has", "was").'),
  ],

  // 2.9 Quantified subjects
  '2.9': [
    p([
      ok('The class prepared for the final test.'),
      ['Each of the students are ready.', 'Each of the students is ready.'],
      ok('The teacher handed out the papers.'),
      ['Outside, a number of parents were waiting.', 'Outside, a number of parents were waiting.'],
      ok('The test lasted a full hour.'),
    ], '"Each of" takes a singular verb ("is"); "a number of" takes a plural verb ("were").'),
    p([
      ok('The council planned a new playground.'),
      ['Every one of the proposals need review.', 'Every one of the proposals needs review.'],
      ok('Residents shared their ideas at the meeting.'),
      ['In fact, a number of objections were raised.', 'In fact, a number of objections were raised.'],
      ok('The final plan was approved in the spring.'),
    ], '"Every one of" is singular ("needs"); "a number of" is plural ("were").'),
    p([
      ok('The team reviewed the season\'s results.'),
      ['Each of the players were tired after the match.', 'Each of the players was tired after the match.'],
      ok('The coach praised their effort.'),
      ['Notably, none of the goals were scored in the first half.', 'Notably, none of the goals were scored in the first half.'],
      ok('They looked forward to the next game.'),
    ], '"Each of" takes "was" here; "none of the goals" takes a plural verb.'),
    p([
      ok('The museum arranged a tour for the visitors.'),
      ['One of the paintings were damaged in the move.', 'One of the paintings was damaged in the move.'],
      ok('Restorers repaired it over several weeks.'),
      ['Meanwhile, each of the guides have a special badge.', 'Meanwhile, each of the guides has a special badge.'],
      ok('The tour reopened to the public soon after.'),
    ], '"One of" and "each of" take singular verbs ("was", "has").'),
    p([
      ok('The organisers prepared for the charity run.'),
      ['Each of the runners were given a number.', 'Each of the runners was given a number.'],
      ok('Volunteers handed out water along the route.'),
      ['However, neither of the winners were present at the start.', 'However, neither of the winners was present at the start.'],
      ok('The event raised money for the hospital.'),
    ], '"Each of" and "neither of" take singular verbs ("was").'),
  ],

  // 2.10 Determiner-noun number
  '2.10': [
    p([
      ok('The shop arranged its new displays.'),
      ['These book are on sale this week.', 'These books are on sale this week.'],
      ok('A small sign marks each discount.'),
      ['Meanwhile, this chairs came from the back room.', 'Meanwhile, this chair came from the back room.'],
      ok('Customers soon filled the small shop.'),
    ], '"These" needs a plural noun ("books"), and "this" needs a singular noun ("chair").'),
    p([
      ok('The teacher handed out the worksheets.'),
      ['"Can you move those box to the corner?" she asked.', '"Can you move those boxes to the corner?" she asked.'],
      ok('The class tidied the room quickly.'),
      ['This pencils are sharp enough already.', 'These pencils are sharp enough already.'],
      ok('Everyone sat down for the lesson.'),
    ], 'Use "those boxes" and "these pencils" to match plural nouns.'),
    p([
      ok('The museum displayed old photographs.'),
      ['That windows face the river.', 'Those windows face the river.'],
      ok('Visitors stopped to look at the view.'),
      ['These painting came from a private collection.', 'This painting came from a private collection.'],
      ok('The gallery was quiet all afternoon.'),
    ], 'Use "those windows" (plural) and "this painting" (singular).'),
    p([
      ok('The family packed for the long journey.'),
      ['These suitcase are far too heavy.', 'These suitcases are far too heavy.'],
      ok('They loaded them into the car.'),
      ['Luckily, that map show all the main roads.', 'Luckily, that map shows all the main roads.'],
      ok('They set off before sunrise.'),
    ], 'Use "these suitcases" (plural) and keep "that map" singular.'),
    p([
      ok('The restaurant prepared for a busy night.'),
      ['This tables need to be wiped.', 'These tables need to be wiped.'],
      ok('Staff arranged the cutlery carefully.'),
      ['Meanwhile, those dish is still on the shelf.', 'Meanwhile, that dish is still on the shelf.'],
      ok('The doors opened at six sharp.'),
    ], 'Use "these tables" (plural) and "that dish" (singular).'),
  ],

  // 2.11 Quantifier-noun
  '2.11': [
    p([
      ok('The shop stocked up before the weekend.'),
      ['There are less bottles of juice than before.', 'There are fewer bottles of juice than before.'],
      ok('Still, the shelves looked quite full.'),
      ['There is too much people in the aisle.', 'There are too many people in the aisle.'],
      ok('The staff restocked the drinks quickly.'),
    ], 'Use "fewer" with countable nouns and "many" (not "much") with plural count nouns.'),
    p([
      ok('The café was nearly out of supplies.'),
      ['We have less chairs than we need.', 'We have fewer chairs than we need.'],
      ok('So the owner borrowed some from next door.'),
      ['There is not many milk left in the fridge.', 'There is not much milk left in the fridge.'],
      ok('A delivery arrived before opening time.'),
    ], 'Countable "chairs" takes "fewer"; uncountable "milk" takes "much".'),
    p([
      ok('The gardener planned the spring planting.'),
      ['She has less seeds than last year.', 'She has fewer seeds than last year.'],
      ok('So she ordered more from the local shop.'),
      ['There is too many rain for the young plants.', 'There is too much rain for the young plants.'],
      ok('The garden soon turned bright green.'),
    ], 'Use "fewer seeds" (countable) and "too much rain" (uncountable).'),
    p([
      ok('The library reviewed its yearly budget.'),
      ['We bought less books this term.', 'We bought fewer books this term.'],
      ok('Luckily, donations helped fill the gaps.'),
      ['There are too much magazines on the low shelf.', 'There are too many magazines on the low shelf.'],
      ok('Readers enjoyed the new titles.'),
    ], 'Countable "books" and "magazines" take "fewer"/"many".'),
    p([
      ok('The team planned a long cycling trip.'),
      ['There are less riders than we expected.', 'There are fewer riders than we expected.'],
      ok('So they set off in two small groups.'),
      ['There is too many traffic on the coastal road.', 'There is too much traffic on the coastal road.'],
      ok('They reached the campsite by evening.'),
    ], 'Use "fewer riders" (countable) and "too much traffic" (uncountable).'),
  ],

  // 2.12 Pronoun-antecedent
  '2.12': [
    p([
      ok('The girls walked home together after school.'),
      ['The girls lost her bag on the way.', 'The girls lost their bag on the way.'],
      ok('They searched the whole street.'),
      ['A neighbour found it and returned it to their owner.', 'A neighbour found it and returned it to its owner.'],
      ok('The girls thanked her warmly.'),
    ], 'The plural "girls" needs "their"; the singular "it" (the bag) needs "its".'),
    p([
      ok('The students finished the group project.'),
      ['The teachers shared her own ideas with the class.', 'The teachers shared their own ideas with the class.'],
      ok('Afterwards, the teacher praised the whole class.'),
      ok('The class then presented the work to the school.'),
      ok('Everyone was proud of the result.'),
    ], 'The plural "teachers" needs "their", not "her".'),
    p([
      ok('The boy and his father fixed the bicycle.'),
      ['The boy thanked his father for their help.', 'The boy thanked his father for his help.'],
      ok('Together they tested the brakes in the garden.'),
      ['A neighbour lent them their tools.', 'A neighbour lent them his tools.'],
      ok('By evening, the bicycle was ready.'),
    ], 'The singular owner takes "his", not the plural "their".'),
    p([
      ok('The two cats slept on the warm windowsill.'),
      ['One cat opened their eyes slowly.', 'One cat opened its eyes slowly.'],
      ok('The other stretched and yawned.'),
      ok('Then both cats flicked their tails at the same time.'),
      ok('They soon fell asleep again.'),
    ], 'A singular cat takes "its", not "their".'),
    p([
      ok('The company opened a new office downtown.'),
      ['The company moved their headquarters last year.', 'The company moved its headquarters last year.'],
      ok('Staff settled in quickly.'),
      ok('Soon every employee received a new pass.'),
      ok('The office was running smoothly within a week.'),
    ], '"The company" is singular, so it takes "its", not "their".'),
  ],

  // 2.13 Correlatives
  '2.13': [
    p([
      ok('Two people offered to lead the group.'),
      ['Either Tom or Anna are going to speak first.', 'Either Tom or Anna is going to speak first.'],
      ok('They agreed on the order.'),
      ['However, neither the guide nor the drivers was ready.', 'However, neither the guide nor the drivers were ready.'],
      ok('So the group set off a little late.'),
    ], 'With "either/or" the verb follows the nearer singular subject; with "neither/nor" it follows the nearer plural.'),
    p([
      ok('The class chose two presenters for the event.'),
      ['Either the teacher or the students is leading the tour.', 'Either the teacher or the students are leading the tour.'],
      ok('They planned the route together.'),
      ['Unfortunately, neither the boys nor the girl know the way.', 'Unfortunately, neither the boys nor the girl knows the way.'],
      ok('A map solved the problem.'),
    ], 'The verb agrees with the nearer subject: "students are", "girl knows".'),
    p([
      ok('Two friends cooked dinner for the family.'),
      ['Neither rice nor pasta were needed that night.', 'Neither rice nor pasta was needed that night.'],
      ok('So they baked a simple pie instead.'),
      ['Either the pie or the salad are ready now.', 'Either the pie or the salad is ready now.'],
      ok('Everyone enjoyed the meal.'),
    ], 'With singular nearer subjects, use "was" and "is".'),
    p([
      ok('The team prepared for the quiz final.'),
      ['Either Sam or the twins is answering first.', 'Either Sam or the twins are answering first.'],
      ok('They practised every evening.'),
      ['Still, neither the captain nor the players was nervous.', 'Still, neither the captain nor the players were nervous.'],
      ok('They won by a single point.'),
    ], 'The verb follows the nearer subject: "twins are", "players were".'),
    p([
      ok('The committee planned the summer festival.'),
      ['Either the mayor or the councillors speaks at the opening.', 'Either the mayor or the councillors speak at the opening.'],
      ok('They printed a full programme.'),
      ['Even so, neither the band nor the singers were paid for the day.', 'Even so, neither the band nor the singers were paid for the day.'],
      ok('The festival was a great success.'),
    ], 'Use "speak" with the nearer plural "councillors" and "were" with the nearer plural "singers".'),
  ],

  // 2.14 Reflexive-antecedent
  '2.14': [
    p([
      ok('Anna prepared for the school concert.'),
      ['She taught himself to play the piano.', 'She taught herself to play the piano.'],
      ok('She practised every evening after dinner.'),
      ['Meanwhile, the boys amused hisself with a puzzle.', 'Meanwhile, the boys amused themselves with a puzzle.'],
      ok('The concert went better than expected.'),
    ], 'The reflexive must match its subject: "she...herself", "the boys...themselves".'),
    p([
      ok('The children played in the garden all afternoon.'),
      ['They built a fort all by theirselves.', 'They built a fort all by themselves.'],
      ok('They used old boxes and a blanket.'),
      ['Later, my sister cut herself on a sharp edge.', 'Later, my sister cut herself on a sharp edge.'],
      ok('Then they went inside for dinner.'),
    ], 'The correct reflexives are "themselves" and "herself".'),
    p([
      ok('We cleaned the whole house on Saturday.'),
      ['My brother and I painted the walls ourself.', 'My brother and I painted the walls ourselves.'],
      ok('Soon the rooms looked bright and new.'),
      ['"You should be proud of yourself," our mother said.', '"You should be proud of yourself," our mother said.'],
      ok('We celebrated with a takeaway dinner.'),
    ], 'Use "ourselves" with "my brother and I", and "yourself" with "you".'),
    p([
      ok('The old man lives alone in the village.'),
      ['He looks after hisself very well.', 'He looks after himself very well.'],
      ok('He cooks and cleans without help.'),
      ['So I reminded meself to visit him often.', 'So I reminded myself to visit him often.'],
      ok('He always welcomes a friendly visit.'),
    ], 'The correct reflexives are "himself" and "myself".'),
    p([
      ok('The choir warmed up before the evening show.'),
      ['Each singer introduced theirself to the group.', 'Each singer introduced themselves to the group.'],
      ok('They laughed and shared stories.'),
      ['Meanwhile, the conductor reminded hisself to stay calm.', 'Meanwhile, the conductor reminded himself to stay calm.'],
      ok('The performance was their best yet.'),
    ], 'Use "themselves" with "each singer" and "himself" with "the conductor".'),
  ],

  // =========================================================================
  // Section 3 — Articles and determiners
  // =========================================================================

  // 3.1 a/an choice
  '3.1': [
    p([
      ok('The family planned a trip to the countryside.'),
      ['They packed a apple and some sandwiches for the road.', 'They packed an apple and some sandwiches for the road.'],
      ok('The car left before the sun came up.'),
      ['Later, they stopped at a old farm to buy fresh eggs.', 'Later, they stopped at an old farm to buy fresh eggs.'],
      ok('The day was warm and clear.'),
    ], 'Use "an" before a vowel sound: "an apple", "an old farm".'),
    p([
      ok('The school held a science fair on Friday.'),
      ['Each pupil built a engine from a kit.', 'Each pupil built an engine from a kit.'],
      ok('Soon the hall filled with small working models.'),
      ['One group even made a machine that sorted coins.', 'One group even made a machine that sorted coins.'],
      ok('The judges chose three winners.'),
    ], 'Use "an" before the vowel sound in "engine".'),
    p([
      ok('The office hired a new assistant.'),
      ['She arrived with a umbrella and a heavy bag.', 'She arrived with an umbrella and a heavy bag.'],
      ok('The manager showed her to her desk.'),
      ['There she asked for a hour to read the notes.', 'There she asked for an hour to read the notes.'],
      ok('By lunch she felt at home.'),
    ], '"An umbrella" and "an hour" take "an" (note the silent h in "hour").'),
    p([
      ok('The gardener planted a small orchard.'),
      ['She chose a orange tree for the sunny corner.', 'She chose an orange tree for the sunny corner.'],
      ok('The soil there was rich and soft.'),
      ['Nearby, a older pear tree already grew.', 'Nearby, an older pear tree already grew.'],
      ok('The garden looked lovely in spring.'),
    ], 'Vowel sounds take "an": "an orange tree", "an older pear tree".'),
    p([
      ok('The café introduced a new menu.'),
      ['The chef added a egg dish and a fruit salad.', 'The chef added an egg dish and a fruit salad.'],
      ok('Customers liked the fresh ingredients.'),
      ['The café also offered a interesting soup of the day.', 'The café also offered an interesting soup of the day.'],
      ok('It soon became very popular.'),
    ], 'Use "an" before vowel sounds: "an egg dish", "an interesting soup".'),
  ],

  // 3.2 Missing article
  '3.2': [
    p([
      ok('A small boy walked along the beach.'),
      ['He found bottle lying in the sand.', 'He found a bottle lying in the sand.'],
      ok('Inside there was an old note.'),
      ['He carried it carefully to his mother.', 'He carried it carefully to his mother.'],
      ok('She said it was a message from years ago.'),
    ], 'A singular countable noun needs a determiner: "a bottle".'),
    p([
      ok('The village held its yearly festival.'),
      ['Crowd gathered near the old fountain.', 'A crowd gathered near the old fountain.'],
      ok('Musicians played on a small stage.'),
      ['They had built stage from wooden planks.', 'They had built a stage from wooden planks.'],
      ok('The festival lasted three days.'),
    ], 'Singular countable nouns need a determiner: "A crowd", "a stage".'),
    p([
      ok('My sister started a new job this month.'),
      ['She works in office near the station.', 'She works in an office near the station.'],
      ok('Her desk sits beside a tall window.'),
      ['She keeps plant on the sill to brighten it.', 'She keeps a plant on the sill to brighten it.'],
      ok('She enjoys the work very much.'),
    ], 'Singular countable nouns need a determiner: "an office", "a plant".'),
    p([
      ok('The kitchen smelled of fresh bread.'),
      ['Mother had baked loaf for the weekend.', 'Mother had baked a loaf for the weekend.'],
      ['She cut thick slice for each of us.', 'She cut a thick slice for each of us.'],
      ok('We ate it warm with butter.'),
      ok('The whole house felt cozy that morning.'),
    ], 'Singular countable nouns need a determiner: "a loaf", "a slice".'),
    p([
      ok('The students visited a nature reserve.'),
      ['They saw heron standing in the shallow water.', 'They saw a heron standing in the shallow water.'],
      ok('A guide explained the local wildlife.'),
      ['He pointed out nest high in the pine tree.', 'He pointed out a nest high in the pine tree.'],
      ok('The trip was both fun and useful.'),
    ], 'Singular countable nouns need a determiner: "a heron", "a nest".'),
  ],

  // 3.3 Unnecessary article
  '3.3': [
    p([
      ok('My brother plays several sports after school.'),
      ['He plays the basketball on Tuesdays.', 'He plays basketball on Tuesdays.'],
      ok('On Fridays he swims at the local pool.'),
      ['In winter he also plays the hockey.', 'In winter he also plays hockey.'],
      ok('He hopes to join the school team.'),
    ], 'Activities and sports take no article: "basketball", "hockey".'),
    p([
      ok('Our family eats dinner together each evening.'),
      ['We usually have the breakfast before seven.', 'We usually have breakfast before seven.'],
      ok('My father leaves for work at eight.'),
      ['He drinks the coffee on the way.', 'He drinks coffee on the way.'],
      ok('We meet again at dinner.'),
    ], 'Meals and drinks in general take no article: "breakfast", "coffee".'),
    p([
      ok('The children walk to school every morning.'),
      ['They go to the school together.', 'They go to school together.'],
      ok('Their mother watches from the gate.'),
      ['On Sundays they go to the church in the village.', 'On Sundays they go to church in the village.'],
      ok('They are always home by five.'),
    ], 'In these fixed phrases we say "go to school" and "go to church" without "the".'),
    p([
      ok('My grandmother is interested in languages.'),
      ['She studies the French every evening.', 'She studies French every evening.'],
      ok('She listens to short radio lessons.'),
      ['She also reads the history in her spare time.', 'She also reads history in her spare time.'],
      ok('She says learning never stops.'),
    ], 'Subjects and languages take no article: "French", "history".'),
    p([
      ok('The band traveled across the region last year.'),
      ['They performed in the cities and small towns alike.', 'They performed in cities and small towns alike.'],
      ok('Their music mixed folk and modern sounds.'),
      ['They hoped to bring the joy to every audience.', 'They hoped to bring joy to every audience.'],
      ok('Their tour ended in the capital.'),
    ], 'Generic plural nouns and abstract nouns take no article: "cities", "joy".'),
  ],

  // 3.4 Definite vs indefinite
  '3.4': [
    p([
      ok('A cat wandered into our garden yesterday.'),
      ['Cat sat under the hedge and watched us.', 'The cat sat under the hedge and watched us.'],
      ok('We had not seen it before.'),
      ['It seemed friendly, so we left the little bowl of milk.', 'It seemed friendly, so we left a little bowl of milk.'],
      ok('It drank the milk and then slipped away.'),
    ], 'Use "the" for a noun already mentioned, and "a" for first mention.'),
    p([
      ok('We visited a museum during the holidays.'),
      ['Museum had a whole room about ancient ships.', 'The museum had a whole room about ancient ships.'],
      ok('A guide told us about the explorers.'),
      ['She showed us old map of the coast.', 'She showed us an old map of the coast.'],
      ok('We stayed for several hours.'),
    ], '"The museum" was already introduced; "an old map" is new information.'),
    p([
      ok('A letter arrived for me this morning.'),
      ['Letter was from my old school friend.', 'The letter was from my old school friend.'],
      ok('She invited me to a reunion.'),
      ['She asked me to bring old photograph.', 'She asked me to bring an old photograph.'],
      ok('I replied straight away.'),
    ], 'Use "the letter" (specific, known) and "an old photograph" (first mention).'),
    p([
      ok('A dog followed us home from the park.'),
      ['Dog looked thin and hungry.', 'The dog looked thin and hungry.'],
      ok('We gave it some food and water.'),
      ['A neighbour recognised it as missing pet.', 'A neighbour recognised it as a missing pet.'],
      ok('Its owner came to collect it that evening.'),
    ], 'Use "the dog" on second mention and "a missing pet" for new information.'),
    p([
      ok('I bought a book about birds last week.'),
      ['Book has beautiful coloured pictures.', 'The book has beautiful coloured pictures.'],
      ok('It shows species from every continent.'),
      ['I plan to find bird guide for our own garden.', 'I plan to find a bird guide for our own garden.'],
      ok('Birdwatching has become my new hobby.'),
    ], '"The book" is already known; "a bird guide" is first mentioned.'),
  ],

  // 3.5 Stacked determiners
  '3.5': [
    p([
      ok('The children packed their bags for the trip.'),
      ['Each child found the my note in the lunch box.', 'Each child found my note in the lunch box.'],
      ok('The parents waved from the gate.'),
      ['The driver checked the his list twice.', 'The driver checked his list twice.'],
      ok('The bus left right on time.'),
    ], 'Only one central determiner is allowed: "my note", "his list".'),
    p([
      ok('The family tidied the house before the guests arrived.'),
      ['They cleared the our old boxes from the hall.', 'They cleared our old boxes from the hall.'],
      ok('Flowers were placed on the table.'),
      ['The mother arranged the her best plates.', 'The mother arranged her best plates.'],
      ok('Everything was ready by noon.'),
    ], 'Do not stack determiners: use "our boxes", "her plates".'),
    p([
      ok('The team prepared a surprise for the coach.'),
      ['They hid the their banner behind the door.', 'They hid their banner behind the door.'],
      ok('The players practised a short cheer.'),
      ['The captain checked the his watch.', 'The captain checked his watch.'],
      ok('The coach arrived a minute later.'),
    ], 'Use a single determiner: "their banner", "his watch".'),
    p([
      ok('The shop displayed new goods in the window.'),
      ['The owner moved the this shelf to the back.', 'The owner moved this shelf to the back.'],
      ok('She replaced it with a larger table.'),
      ['The assistant dusted the those jars carefully.', 'The assistant dusted those jars carefully.'],
      ok('The display looked bright and inviting.'),
    ], 'Only one determiner per noun phrase: "this shelf", "those jars".'),
    p([
      ok('We cleaned the attic on a rainy afternoon.'),
      ['We found the some old photographs in a box.', 'We found some old photographs in a box.'],
      ok('They showed the town many years ago.'),
      ['My father kept the his favourite one on the desk.', 'My father kept his favourite one on the desk.'],
      ok('We spent the rest of the day looking through them.'),
    ], 'Use one determiner: "some old photographs", "his favourite one".'),
  ],

  // 3.6 Determiner with no noun
  '3.6': [
    p([
      ok('Two friends swapped books after class.'),
      ['"This one is my," said Sam.', '"This one is mine," said Sam.'],
      ok('Anna held up a blue notebook.'),
      ['"And this is your," she replied with a smile.', '"And this is yours," she replied with a smile.'],
      ok('They promised to read both by Friday.'),
    ], 'A possessive determiner needs a noun; standing alone it becomes a pronoun: "mine", "yours".'),
    p([
      ok('The children sorted their toys into two boxes.'),
      ['"These are her and those are his," said the mother.', '"These are hers and those are his," said the mother.'],
      ok('Each box had a label on the side.'),
      ['"Remember, this box is our," she added.', '"Remember, this box is ours," she added.'],
      ok('The room was tidy within an hour.'),
    ], 'Use possessive pronouns "hers", "ours" when no noun follows.'),
    p([
      ok('Two neighbours compared their gardens.'),
      ['"My roses are lovely, but your are taller," said one.', '"My roses are lovely, but yours are taller," said one.'],
      ok('They walked along the fence together.'),
      ['"That bench is their," the other noted.', '"That bench is theirs," the other noted.'],
      ok('They agreed to share the space.'),
    ], 'Possessive pronouns replace the whole phrase: "yours", "theirs".'),
    p([
      ok('The students collected their projects.'),
      ['"Is this pen your?" asked Ben.', '"Is this pen yours?" asked Ben.'],
      ok('Mia shook her head.'),
      ['"Mine is over there; this one is her," she said.', '"Mine is over there; this one is hers," she said.'],
      ok('The owner soon claimed it.'),
    ], 'Use "yours" and "hers" when the noun is left out.'),
    p([
      ok('The family divided the old photographs.'),
      ['"These are our and those are their," said Mother.', '"These are ours and those are theirs," said Mother.'],
      ok('Each person received a small bundle.'),
      ['"Keep mine safe and I will keep your," she added.', '"Keep mine safe and I will keep yours," she added.'],
      ok('The photos were treasured by everyone.'),
    ], 'Without a following noun, use "ours", "theirs", "yours".'),
  ],

  // 3.7 some/any
  '3.7': [
    p([
      ok('We planned a picnic for the weekend.'),
      ['I will bring some fruit and some juice.', 'I will bring some fruit and some juice.'],
      ok('My sister offered to make sandwiches.'),
      ['"Do we have some napkins?" she asked.', '"Do we have any napkins?" she asked.'],
      ok('I checked the cupboard and found a pack.'),
    ], 'Use "some" in positive statements and "any" in questions.'),
    p([
      ok('The fridge was almost empty on Monday.'),
      ['We did not have some milk left.', 'We did not have any milk left.'],
      ok('I made a shopping list at once.'),
      ['I bought some bread and some cheese.', 'I bought some bread and some cheese.'],
      ok('The fridge looked much better by evening.'),
    ], 'Negatives take "any": "did not have any milk".'),
    p([
      ok('The children asked for a story before bed.'),
      ['"Are there some books about dragons?" they asked.', '"Are there any books about dragons?" they asked.'],
      ok('I found one on the top shelf.'),
      ['"There are some pictures on every page," I said.', '"There are some pictures on every page," I said.'],
      ok('They listened quietly to the whole tale.'),
    ], 'Use "any" in questions and "some" in positive statements.'),
    p([
      ok('The office was quiet on Friday afternoon.'),
      ['"Has some post arrived today?" asked the manager.', '"Has any post arrived today?" asked the manager.'],
      ok('The clerk checked the front desk.'),
      ['"There are some letters for you," she replied.', '"There are some letters for you," she replied.'],
      ok('The manager read them before leaving.'),
    ], 'Questions take "any"; positive statements take "some".'),
    p([
      ok('We were preparing for the visitors.'),
      ['"We do not have some chairs left," said my father.', '"We do not have any chairs left," said my father.'],
      ok('He fetched two from the garage.'),
      ['"Could you also bring some glasses?" asked my mother.', '"Could you also bring some glasses?" asked my mother.'],
      ok('Everything was ready in time.'),
    ], 'Negatives use "any"; requests and positives use "some".'),
  ],

  // 3.8 each/every/all/whole/other/another
  '3.8': [
    p([
      ok('The teacher handed out a worksheet to everyone.'),
      ['She asked each students to write their name at the top.', 'She asked each student to write their name at the top.'],
      ok('The class worked quietly for ten minutes.'),
      ['Another pupils finished early and helped the others.', 'Another pupil finished early and helped the others.'],
      ok('The lesson ended with a short discussion.'),
    ], '"Each" and "another" take singular nouns: "each student", "another pupil".'),
    p([
      ok('The family visited a large market on Sunday.'),
      ['Every stalls were full of colourful fruit.', 'Every stall was full of colourful fruit.'],
      ok('The children tasted a few samples.'),
      ['The whole family bought another bags of nuts.', 'The whole family bought another bag of nuts.'],
      ok('They carried everything home happily.'),
    ], '"Every stall" is singular; "another bag" is singular.'),
    p([
      ok('The class planned their end-of-year trip.'),
      ['Each options was discussed for a long time.', 'Each option was discussed for a long time.'],
      ok('The teacher wrote the ideas on the board.'),
      ['The whole class agreed on another places to visit.', 'The whole class agreed on another place to visit.'],
      ok('The trip was booked before the holiday.'),
    ], '"Each option" and "another place" are singular.'),
    p([
      ok('The gardener planted flowers along the path.'),
      ['She gave each plants plenty of water.', 'She gave each plant plenty of water.'],
      ok('The garden filled with colour.'),
      ['Other gardener helped her with the weeding.', 'Another gardener helped her with the weeding.'],
      ok('The path looked beautiful by summer.'),
    ], 'Use "each plant" (singular) and "another gardener" (singular).'),
    p([
      ok('The shop offered a discount that week.'),
      ['Every customers received a small gift.', 'Every customer received a small gift.'],
      ok('The staff wrapped each item carefully.'),
      ['They ordered another boxes to refill the shelves.', 'They ordered another box to refill the shelves.'],
      ok('The shop was busy all week.'),
    ], '"Every customer" and "another box" are singular.'),
  ],

  // =========================================================================
  // Section 4 — Nouns
  // =========================================================================

  // 4.1 Countable vs uncountable
  '4.1': [
    p([
      ok('The receptionist greeted the new visitor.'),
      ['She gave him several informations about the tour.', 'She gave him some information about the tour.'],
      ok('He read a leaflet in the waiting room.'),
      ['Then the guide offered a useful advice about timing.', 'Then the guide offered some useful advice about timing.'],
      ok('The tour started a few minutes later.'),
    ], '"Information" and "advice" are uncountable: no plural, no "a/an".'),
    p([
      ok('The teacher explained the new topic slowly.'),
      ['The students asked for more equipments for the lab.', 'The students asked for more equipment for the lab.'],
      ok('So the school ordered new tools for the class.'),
      ['They also needed a new furnitures for the room.', 'They also needed new furniture for the room.'],
      ok('The lab was ready by the next term.'),
    ], '"Equipment" and "furniture" are uncountable.'),
    p([
      ok('The doctor checked the young patient carefully.'),
      ['She wrote down a few advices for the parents.', 'She wrote down a few pieces of advice for the parents.'],
      ok('Then she explained how to use the medicine.'),
      ['She also requested more informations about his diet.', 'She also requested more information about his diet.'],
      ok('The parents thanked her and left.'),
    ], 'Uncountable nouns take "pieces of" and no plural -s: "advice", "information".'),
    p([
      ok('The office upgraded its computer systems.'),
      ['The manager bought new softwares for every team.', 'The manager bought new software for every team.'],
      ok('Technicians installed it over a weekend.'),
      ['They also ordered extra equipments for the lab.', 'They also ordered extra equipment for the lab.'],
      ok('The systems ran smoothly on Monday.'),
    ], '"Software" and "equipment" have no plural form.'),
    p([
      ok('The travellers packed for a long journey.'),
      ['They took a light luggage for the flight.', 'They took light luggage for the flight.'],
      ok('The airport was busy that morning.'),
      ['Each passenger needed a valid knowledges of the rules.', 'Each passenger needed good knowledge of the rules.'],
      ok('The flight left on time.'),
    ], '"Luggage" and "knowledge" are uncountable.'),
  ],

  // 4.2 Noun as modifier (number)
  '4.2': [
    p([
      ok('The company planned a new training programme.'),
      ['They designed a ten-years plan for the staff.', 'They designed a ten-year plan for the staff.'],
      ok('Managers explained each stage clearly.'),
      ['The programme included a two-hours workshop weekly.', 'The programme included a two-hour workshop weekly.'],
      ok('The first session began in March.'),
    ], 'A noun modifier stays singular: "ten-year plan", "two-hour workshop".'),
    p([
      ok('The council approved a new building project.'),
      ['They funded a five-miles road through the valley.', 'They funded a five-mile road through the valley.'],
      ok('Work was due to start in spring.'),
      ['It would shorten the twenty-minutes journey.', 'It would shorten the twenty-minute journey.'],
      ok('Residents welcomed the news.'),
    ], 'Modifiers stay singular even with a number: "five-mile", "twenty-minute".'),
    p([
      ok('The school opened a new sports section.'),
      ['They built a three-courts hall beside the field.', 'They built a three-court hall beside the field.'],
      ok('Students could play indoors in winter.'),
      ['The hall also hosted a six-teams tournament.', 'The hall also hosted a six-team tournament.'],
      ok('The first match drew a large crowd.'),
    ], 'Keep the modifier singular: "three-court", "six-team".'),
    p([
      ok('The company offered a special travel deal.'),
      ['It included a seven-days cruise for two.', 'It included a seven-day cruise for two.'],
      ok('The cabin looked out over the sea.'),
      ['Guests received a four-courses dinner each evening.', 'Guests received a four-course dinner each evening.'],
      ok('The trip sold out quickly.'),
    ], 'Modifiers stay singular: "seven-day cruise", "four-course dinner".'),
    p([
      ok('The hospital added a new recovery ward.'),
      ['It had a twelve-beds unit on the top floor.', 'It had a twelve-bed unit on the top floor.'],
      ok('Nurses could monitor every patient closely.'),
      ['A two-hours training was arranged for the staff.', 'A two-hour training was arranged for the staff.'],
      ok('The ward opened the following month.'),
    ], 'Use singular modifiers: "twelve-bed", "two-hour".'),
  ],

  // 4.3 Plural-only / singular -s nouns
  '4.3': [
    p([
      ok('The staff prepared the operating room.'),
      ['The nurse laid out a scissors and a tray.', 'The nurse laid out a pair of scissors and a tray.'],
      ok('The surgeon arrived a moment later.'),
      ['She asked for the new trouser from the cupboard.', 'She asked for the new pair of trousers from the cupboard.'],
      ok('The operation went smoothly.'),
    ], '"Scissors" and "trousers" are plural-only; count them with "a pair of".'),
    p([
      ok('The class listened to the morning announcements.'),
      ['The news about the trip were exciting.', 'The news about the trip was exciting.'],
      ok('Everyone wrote the details in their diary.'),
      ['The teacher said the new information were on the board.', 'The teacher said the new information was on the board.'],
      ok('The students left for lunch happily.'),
    ], '"News" and "information" end in -s but are singular in meaning.'),
    p([
      ok('The tailor measured the customer carefully.'),
      ['He needed a new scissors for the cloth.', 'He needed a new pair of scissors for the cloth.'],
      ok('The fabric was soft and strong.'),
      ['He soon finished the trouser for the fitting.', 'He soon finished the trousers for the fitting.'],
      ok('The customer was delighted with the result.'),
    ], 'Plural-only "scissors"/"trousers" need "a pair of" or a plural verb.'),
    p([
      ok('The trousers hung on the back of the door.'),
      ['They pair of trousers were still wet from the rain.', 'The pair of trousers was still wet from the rain.'],
      ok('The boy found his umbrella nearby.'),
      ['His glasses was on the table by the window.', 'His glasses were on the table by the window.'],
      ok('He put everything away before dinner.'),
    ], '"A pair of trousers" is singular; "glasses" is plural.'),
    p([
      ok('The shop stocked clothes for the new season.'),
      ['The manager ordered new trouser in three colours.', 'The manager ordered new trousers in three colours.'],
      ok('The window display looked bright.'),
      ['She also hung a new short in the window.', 'She also hung a new pair of shorts in the window.'],
      ok('The shop opened early the next morning.'),
    ], '"Trousers" and "shorts" are plural-only nouns.'),
  ],

  // =========================================================================
  // Section 5 — Pronouns
  // =========================================================================

  // 5.1 Case, simple
  '5.1': [
    p([
      ok('My neighbour needed help with the shopping.'),
      ['Me am always happy to help her.', 'I am always happy to help her.'],
      ok('So we walked to the market together.'),
      ['The heavy bags were a problem for she.', 'The heavy bags were a problem for her.'],
      ok('In the end, we shared the load on the way home.'),
    ], 'Subjects take "I"; after a preposition the object form "her" is used.'),
    p([
      ok('A new singer joined the choir.'),
      ['Her has a lovely voice.', 'She has a lovely voice.'],
      ok('The group practised twice a week.'),
      ['After the show, the choir director praised we.', 'After the show, the choir director praised us.'],
      ok('They performed at the winter concert.'),
    ], 'Use the subject form "She" and the object form "us".'),
    p([
      ok('A parcel arrived for the family.'),
      ['It was addressed to we by mistake.', 'It was addressed to us by mistake.'],
      ok('So my father called the delivery office.'),
      ['Them promised to send a new label.', 'They promised to send a new label.'],
      ok('The parcel arrived correctly the next day.'),
    ], 'Use the object "us" and the subject "They".'),
    p([
      ok('The students waited outside the hall.'),
      ['Them were talking about the exam.', 'They were talking about the exam.'],
      ok('Then the teacher opened the doors at nine.'),
      ['She wished good luck to we all.', 'She wished good luck to us all.'],
      ok('The exam began a few minutes later.'),
    ], 'Use the subject "They" and the object "us".'),
    p([
      ok('My cousin sent a postcard from abroad.'),
      ['Him wrote about the long train journey.', 'He wrote about the long train journey.'],
      ok('The views from the window were amazing.'),
      ['The card arrived for I just before the holiday.', 'The card arrived for me just before the holiday.'],
      ok('So I pinned it above my desk.'),
    ], 'Use the subject "He" and the object "me".'),
  ],

  // 5.2 Case in coordination and comparison
  '5.2': [
    p([
      ok('My brother and I planned a cycling trip.'),
      ['Me and him packed the bags the night before.', 'He and I packed the bags the night before.'],
      ok('We left at dawn on Saturday.'),
      ['The route took my brother and I along the coast.', 'The route took my brother and me along the coast.'],
      ok('We were home by dusk.'),
    ], 'As subject use "He and I"; as object use "my brother and me".'),
    p([
      ok('The teacher handed out the prize certificates.'),
      ['She gave one to Anna and I.', 'She gave one to Anna and me.'],
      ok('The class clapped for both winners.'),
      ['Me and Sam were surprised by the applause.', 'Sam and I were surprised by the applause.'],
      ok('The ceremony ended with a short speech.'),
    ], 'After a preposition use "Anna and me"; as subject use "Sam and I".'),
    p([
      ok('The club organised a weekend hike.'),
      ['They invited my sister and I to join.', 'They invited my sister and me to join.'],
      ok('We met the group at the car park.'),
      ['Me and my sister brought extra water.', 'My sister and I brought extra water.'],
      ok('The hike was longer than expected.'),
    ], 'Use "my sister and me" as object and "My sister and I" as subject.'),
    p([
      ok('Two families shared a holiday cottage.'),
      ['The owners welcomed my parents and I warmly.', 'The owners welcomed my parents and me warmly.'],
      ok('We unpacked the car together.'),
      ['Me and my brother took the small room.', 'My brother and I took the small room.'],
      ok('The week passed far too quickly.'),
    ], 'Use the object "my parents and me" and the subject "My brother and I".'),
    p([
      ok('The company moved two staff to a new branch.'),
      ['The manager thanked Priya and I for our help.', 'The manager thanked Priya and me for our help.'],
      ok('We trained the new team that week.'),
      ['Me and Priya enjoyed the challenge.', 'Priya and I enjoyed the challenge.'],
      ok('The new branch opened on Monday.'),
    ], 'Use "Priya and me" as object and "Priya and I" as subject.'),
  ],

  // 5.3 Ambiguous reference
  '5.3': [
    p([
      ok('The classroom was ready for the first lesson.'),
      ['When they arrived, the room was full.', 'When the pupils arrived, the room was full.'],
      ok('The teacher greeted everyone at the door.'),
      ['He asked it to find a seat quickly.', 'He asked each pupil to find a seat quickly.'],
      ok('The lesson began right on time.'),
    ], 'The pronouns "they" and "it" have no antecedent; name the referent instead.'),
    p([
      ok('The bus was late that morning.'),
      ['When it finally came, we climbed aboard.', 'When the bus finally came, we climbed aboard.'],
      ok('The driver apologised for the delay.'),
      ['They said the traffic had been heavy.', 'The driver said the traffic had been heavy.'],
      ok('We still reached school in time.'),
    ], 'Replace the unclear pronoun with its noun: "the bus", "the driver".'),
    p([
      ok('The new café opened on the corner.'),
      ['They say the coffee is excellent, so we visited it.', 'People say the coffee is excellent, so we visited the café.'],
      ok('The queue stretched out of the door.'),
      ['It served us quickly all the same.', 'The staff served us quickly all the same.'],
      ok('We will certainly go again.'),
    ], 'The pronouns "They" and "It" are unclear; name the referents.'),
    p([
      ok('A parcel was left at the front desk.'),
      ['They want it collected before noon.', 'The receptionist wants the parcel collected before noon.'],
      ok('My colleague checked the label.'),
      ['She said it belonged to a new tenant.', 'She said the parcel belonged to a new tenant.'],
      ok('It was delivered to the right flat.'),
    ], 'Name the referents for the unclear "They" and "it".'),
    p([
      ok('The garden needed a lot of work in spring.'),
      ['They told us it would take a whole weekend.', 'The gardeners told us the work would take a whole weekend.'],
      ok('We cleared the beds on Saturday.'),
      ['It looked much better by Sunday.', 'The garden looked much better by Sunday.'],
      ok('We planted new flowers along the path.'),
    ], 'Replace the unclear pronouns with the nouns they refer to.'),
  ],

  // 5.4 Relative pronoun choice
  '5.4': [
    p([
      ok('A woman moved into the house next door.'),
      ['The woman which lives there is a doctor.', 'The woman who lives there is a doctor.'],
      ok('She greeted us over the garden fence.'),
      ['Her car, which she parks outside, is very small.', 'Her car, which she parks outside, is very small.'],
      ok('We soon became good neighbours.'),
    ], 'Use "who" for people and "which" for things.'),
    p([
      ok('The team bought new equipment for the gym.'),
      ['The machine who arrived yesterday is very modern.', 'The machine which arrived yesterday is very modern.'],
      ok('The coach tested it at once.'),
      ['The players who use it train every morning.', 'The players who use it train every morning.'],
      ok('The gym has been busy ever since.'),
    ], 'Use "which" for objects and "who" for people.'),
    p([
      ok('The library opened a new reading room.'),
      ['The books who fill the shelves are all new.', 'The books which fill the shelves are all new.'],
      ok('A librarian helps visitors find titles.'),
      ['The reader which asked for help was very pleased.', 'The reader who asked for help was very pleased.'],
      ok('The room was quiet all afternoon.'),
    ], 'Use "which" for books and "who" for the reader.'),
    p([
      ok('A new bakery opened near the station.'),
      ['The baker which owns it starts before dawn.', 'The baker who owns it starts before dawn.'],
      ok('The bread is popular with commuters.'),
      ['The oven, which is very old, still works well.', 'The oven, which is very old, still works well.'],
      ok('The shop sells out most mornings.'),
    ], 'Use "who" for the baker and "which" for the oven.'),
    p([
      ok('A film crew visited our town last month.'),
      ['The director which chose the location loved the square.', 'The director who chose the location loved the square.'],
      ok('They filmed for three days.'),
      ['The streets who appeared in the film looked lovely.', 'The streets which appeared in the film looked lovely.'],
      ok('Everyone enjoyed watching the crew at work.'),
    ], 'Use "who" for people and "which" for places and things.'),
  ],

  // 5.5 Dummy it/there
  '5.5': [
    p([
      ok('The clouds grew dark before lunchtime.'),
      ['Was raining hard by the afternoon.', 'It was raining hard by the afternoon.'],
      ok('We hurried home along the main road.'),
      ['Was a large puddle at the corner.', 'There was a large puddle at the corner.'],
      ok('We were glad to reach the house.'),
    ], 'English needs a dummy subject: "It was raining", "There was a puddle".'),
    p([
      ok('The hall filled up before the show.'),
      ['Was a long queue at the entrance.', 'There was a long queue at the entrance.'],
      ok('Staff showed everyone to their seats.'),
      ['Is exciting to watch a live performance.', 'It is exciting to watch a live performance.'],
      ok('The show began right on time.'),
    ], 'Use "There was" for existence and "It is" as a dummy subject.'),
    p([
      ok('The morning was cold and grey.'),
      ['Was snowing when we woke up.', 'It was snowing when we woke up.'],
      ok('The children ran to the window.'),
      ['Is difficult to walk in deep snow.', 'It is difficult to walk in deep snow.'],
      ok('They spent the day indoors by the fire.'),
    ], 'Use "It was snowing" and "It is difficult", not a bare verb.'),
    p([
      ok('The library was quiet that evening.'),
      ['Is a study room on the second floor.', 'There is a study room on the second floor.'],
      ok('Students read at the long tables.'),
      ['Was easy to concentrate in the silence.', 'It was easy to concentrate in the silence.'],
      ok('The library closed at eight.'),
    ], 'Use "There is" for existence and "It was easy" as a dummy subject.'),
    p([
      ok('The town held its summer market.'),
      ['Were many stalls along the high street.', 'There were many stalls along the high street.'],
      ok('Visitors tasted food from around the world.'),
      ['Is wonderful to see the town so busy.', 'It is wonderful to see the town so busy.'],
      ok('The market ran for a whole week.'),
    ], 'Use "There were" for existence and "It is wonderful" as a dummy subject.'),
  ],

  // 5.6 Possessive pronoun vs determiner
  '5.6': [
    p([
      ok('Two classmates swapped notes after the lesson.'),
      ['"Is this pen your?" asked Ben.', '"Is this pen yours?" asked Ben.'],
      ok('Mia searched her bag for a moment.'),
      ['"No, mine pen is blue," she said.', '"No, my pen is blue," she said.'],
      ok('The owner soon claimed it.'),
    ], 'Use the pronoun "yours" alone, and the determiner "my" before a noun.'),
    p([
      ok('The family sorted their belongings.'),
      ['"That box is my," said the boy.', '"That box is mine," said the boy.'],
      ok('His sister lifted a smaller one.'),
      ['"And these books are her," she added.', '"And these books are hers," she added.'],
      ok('They carried everything to the new flat.'),
    ], 'Standalone possessives are "mine"/"hers", not "my"/"her".'),
    p([
      ok('Two neighbours compared their tools.'),
      ['"This hammer is your, I think," said one.', '"This hammer is yours, I think," said one.'],
      ok('The other checked the handle.'),
      ['"No, it is my hammer," he replied.', '"No, it is my hammer," he replied.'],
      ok('They laughed and shared the work.'),
    ], 'Use "yours" alone and "my hammer" with a noun.'),
    p([
      ok('The students packed for the trip.'),
      ['"Is this suitcase our?" asked the group.', '"Is this suitcase ours?" asked the group.'],
      ok('The teacher checked the label.'),
      ['"Yes, and that map is our too," she said.', '"Yes, and that map is ours too," she said.'],
      ok('They loaded the bus quickly.'),
    ], 'Standalone possessives are "ours", not "our".'),
    p([
      ok('The children cleaned the classroom.'),
      ['"These pencils are their," said the monitor.', '"These pencils are theirs," said the monitor.'],
      ok('She put them in the correct box.'),
      ['"And this board is their as well," she added.', '"And this board is theirs as well," she added.'],
      ok('The room was spotless by home time.'),
    ], 'Use the possessive pronoun "theirs", not the determiner "their".'),
  ],

  // 5.7 Reflexive vs ordinary pronoun
  '5.7': [
    p([
      ok('The whole class helped decorate the hall.'),
      ['Myself painted the big banner.', 'I painted the big banner.'],
      ok('Others arranged the chairs and tables.'),
      ['He and myself hung the balloons.', 'He and I hung the balloons.'],
      ok('The hall looked wonderful for the party.'),
    ], 'A reflexive cannot be the subject; use "I" for the subject.'),
    p([
      ok('The project needed careful planning.'),
      ['Themselves finished the report on time.', 'They finished the report on time.'],
      ok('The manager praised the whole team.'),
      ['Herself checked every figure twice.', 'She checked every figure twice.'],
      ok('The report was submitted before the deadline.'),
    ], 'Use ordinary subject pronouns "They" and "She", not reflexives.'),
    p([
      ok('The family prepared the evening meal.'),
      ['Ourselves cooked the main course.', 'We cooked the main course.'],
      ok('The children set the table.'),
      ['Himself washed the vegetables.', 'He washed the vegetables.'],
      ok('The dinner was ready by six.'),
    ], 'Use the subject pronouns "We" and "He".'),
    p([
      ok('The choir prepared a new song.'),
      ['Herself sang the opening line.', 'She sang the opening line.'],
      ok('The others joined in the chorus.'),
      ['Ourselves practised the harmony twice.', 'We practised the harmony twice.'],
      ok('The song sounded beautiful.'),
    ], 'Reflexives cannot be subjects; use "She" and "We".'),
    p([
      ok('The workers finished the repairs quickly.'),
      ['Themselves fixed the broken fence.', 'They fixed the broken fence.'],
      ok('The owner inspected the work.'),
      ['Myself thanked them for their effort.', 'I thanked them for their effort.'],
      ok('The fence looked as good as new.'),
    ], 'Use ordinary subject pronouns "They" and "I".'),
  ],

  // =========================================================================
  // Section 6 — Verbs
  // =========================================================================

  // 6.1 Auxiliary + verb form
  '6.1': [
    p([
      ok('The children prepared for sports day.'),
      ['Mia can runs faster than anyone in her class.', 'Mia can run faster than anyone in her class.'],
      ok('She trains every morning before school.'),
      ['So the coach has chose her for the relay team.', 'So the coach has chosen her for the relay team.'],
      ok('Sports day is next Friday.'),
    ], 'After a modal use the base form ("can run"); after "has" use the past participle ("has chosen").'),
    p([
      ok('The teacher marked the weekend homework.'),
      ['Some pupils have wrote long answers.', 'Some pupils have written long answers.'],
      ok('The class discussed the tricky questions.'),
      ['They could not understands the last one.', 'They could not understand the last one.'],
      ok('So the teacher explained it again.'),
    ], 'After "have" use "written"; after "could" use the base form "understand".'),
    p([
      ok('The family planned a trip to the hills.'),
      ['They will drove to the cabin early.', 'They will drive to the cabin early.'],
      ok('The weather was clear and bright.'),
      ['They have took the same route before.', 'They have taken the same route before.'],
      ok('In the end, they arrived before lunchtime.'),
    ], 'After "will" use "drive"; after "have" use "taken".'),
    p([
      ok('The singer rehearsed with the band.'),
      ['She may sings the new song tonight.', 'She may sing the new song tonight.'],
      ok('The band has practised for weeks.'),
      ['They have wrote two new pieces.', 'They have written two new pieces.'],
      ok('In fact, the concert sold out quickly.'),
    ], 'After "may" use "sing"; after "have" use "written".'),
    p([
      ok('The kitchen prepared for the dinner rush.'),
      ['The chef must washes the vegetables first.', 'The chef must wash the vegetables first.'],
      ok('The staff have set the tables neatly.'),
      ['They have went through the whole menu twice.', 'They have gone through the whole menu twice.'],
      ok('Then the doors opened at six.'),
    ], 'After "must" use "wash"; after "have" use "gone".'),
  ],

  // 6.2 Finite main verb
  '6.2': [
    p([
      ok('The pupils lined up outside the gate.'),
      ['Every morning she going to school by bus.', 'Every morning she goes to school by bus.'],
      ok('Her friends wait at the same stop.'),
      ['They running to class when the bell rings.', 'They run to class when the bell rings.'],
      ok('Then the teacher greets them at the door.'),
    ], 'A main clause needs a finite verb: "she goes", "they run".'),
    p([
      ok('The players warmed up before the match.'),
      ['The captain standing near the centre.', 'The captain stands near the centre.'],
      ok('He shouts advice to his team.'),
      ['They listening carefully to every word.', 'They listen carefully to every word.'],
      ok('Soon after, the match began.'),
    ], 'Use finite verbs "stands" and "listen", not bare -ing forms.'),
    p([
      ok('The train left the station on time.'),
      ['The passengers waiting on the cold platform.', 'The passengers wait on the cold platform.'],
      ok('A porter helps with the heavy cases.'),
      ['The doors opening with a soft hiss.', 'The doors open with a soft hiss.'],
      ok('The journey was quiet and smooth.'),
    ], 'Finite verbs "wait" and "open" are needed; -ing forms cannot stand alone.'),
    p([
      ok('The family gathered for the evening meal.'),
      ['My mother baking a large pie.', 'My mother bakes a large pie.'],
      ok('My father lays the table.'),
      ['My brothers carrying the plates inside.', 'My brothers carry the plates inside.'],
      ok('Then we all sat down together.'),
    ], 'Use "bakes" and "carry", not bare -ing forms.'),
    p([
      ok('The gardener worked through the afternoon.'),
      ['She planting rows of vegetables.', 'She plants rows of vegetables.'],
      ok('The watering can stands by the tap.'),
      ['Birds singing in the apple tree.', 'Birds sing in the apple tree.'],
      ok('The garden looked peaceful in the sun.'),
    ], 'Finite verbs are "plants" and "sing".'),
  ],

  // 6.3 Missing verb / copula
  '6.3': [
    p([
      ok('The children came home from school.'),
      ['My sister very happy with her test result.', 'My sister is very happy with her test result.'],
      ok('She showed the paper to our parents.'),
      ['The soup too hot to eat straight away.', 'The soup is too hot to eat straight away.'],
      ok('So we waited a few minutes before dinner.'),
    ], 'English clauses need a verb: "is very happy", "is too hot".'),
    p([
      ok('The waiting room filled with patients.'),
      ['The doctor ready to see the next person.', 'The doctor is ready to see the next person.'],
      ok('A nurse called the first name.'),
      ['The seats outside quite comfortable.', 'The seats outside are quite comfortable.'],
      ok('Everyone was seen quickly that morning.'),
    ], 'Add the copula: "is ready", "are comfortable".'),
    p([
      ok('The team travelled to the away match.'),
      ['The changing rooms very small at that ground.', 'The changing rooms are very small at that ground.'],
      ok('The players changed quickly.'),
      ['The pitch wet from the morning rain.', 'The pitch was wet from the morning rain.'],
      ok('Still, the match went ahead anyway.'),
    ], 'Add "are very small" and "was wet".'),
    p([
      ok('The shop opened early on Saturday.'),
      ['The shelves full of fresh produce.', 'The shelves were full of fresh produce.'],
      ok('Customers filled their baskets.'),
      ['The prices very fair for the quality.', 'The prices were very fair for the quality.'],
      ok('The shop sold out by noon.'),
    ], 'Add the verb "were" to each clause.'),
    p([
      ok('The library closed for the holidays.'),
      ['The room silent except for the clock.', 'The room was silent except for the clock.'],
      ok('A single lamp lit the corner.'),
      ['The books dusty after so many months.', 'The books were dusty after so many months.'],
      ok('The staff returned in the new year.'),
    ], 'Add "was silent" and "were dusty".'),
  ],

  // 6.4 Passive formation
  '6.4': [
    p([
      ok('The town planned a new bridge over the river.'),
      ['The old bridge build many years ago.', 'The old bridge was built many years ago.'],
      ok('Engineers inspected it every year.'),
      ['A new design choose by the council last month.', 'A new design was chosen by the council last month.'],
      ok('Work will begin in the spring.'),
    ], 'A passive needs "be + past participle": "was built", "was chosen".'),
    p([
      ok('The school arranged a music competition.'),
      ['Three prizes gave to the best singers.', 'Three prizes were given to the best singers.'],
      ok('The audience cheered loudly.'),
      ['The final song write by a student.', 'The final song was written by a student.'],
      ok('Everyone left with a smile.'),
    ], 'Use "were given" and "was written".'),
    p([
      ok('The bakery prepared for the morning rush.'),
      ['The bread bake fresh every day.', 'The bread is baked fresh every day.'],
      ok('The smell reached the whole street.'),
      ['The first loaves sell before seven.', 'The first loaves are sold before seven.'],
      ok('The shop closes at noon on Sundays.'),
    ], 'Use "is baked" and "are sold".'),
    p([
      ok('The committee reviewed the new rules.'),
      ['The rules approve at last week\'s meeting.', 'The rules were approved at last week\'s meeting.'],
      ok('Staff received a written summary.'),
      ['The changes announce to everyone by email.', 'The changes were announced to everyone by email.'],
      ok('The new rules start in June.'),
    ], 'Use "were approved" and "were announced".'),
    p([
      ok('The workers restored the old station.'),
      ['The roof repair after the winter storms.', 'The roof was repaired after the winter storms.'],
      ['New windows fitted on the upper floor.', 'New windows were fitted on the upper floor.'],
      ok('The station reopened in the summer.'),
      ok('The whole town was proud of the result.'),
    ], 'Use "was repaired" and "were fitted".'),
  ],

  // 6.5 Intransitive passive
  '6.5': [
    p([
      ok('A strange noise woke the whole street.'),
      ['The accident was happened near the corner.', 'The accident happened near the corner.'],
      ok('Neighbours rushed outside at once.'),
      ['Nothing serious was occurred that night.', 'Nothing serious occurred that night.'],
      ok('Everyone returned to their homes.'),
    ], 'Intransitive verbs like "happen" and "occur" have no passive form.'),
    p([
      ok('The guests arrived late in the evening.'),
      ['A delay was occurred at the airport.', 'A delay occurred at the airport.'],
      ok('The hosts kept the dinner warm.'),
      ['The flight was departed two hours late.', 'The flight departed two hours late.'],
      ok('The family welcomed them warmly.'),
    ], '"Occur" and "depart" are intransitive; do not use them in the passive.'),
    p([
      ok('The festival brought visitors to the town.'),
      ['The main concert was lasted three hours.', 'The main concert lasted three hours.'],
      ok('Musicians played on two stages.'),
      ['A large crowd was appeared by the river.', 'A large crowd appeared by the river.'],
      ok('The festival ended without trouble.'),
    ], '"Last" and "appear" are intransitive and take no passive.'),
    p([
      ok('The hikers set off before sunrise.'),
      ['Their guide was risen with the sun.', 'Their guide rose with the sun.'],
      ok('They followed a path through the pine woods.'),
      ['They were returned before dark.', 'They returned before dark.'],
      ok('The trip was tiring but enjoyable.'),
    ], '"Rise" and "return" are intransitive here; use the active forms.'),
    p([
      ok('The children waited for the school bus.'),
      ['The bus was arrived early that day.', 'The bus arrived early that day.'],
      ok('They climbed aboard quickly.'),
      ['Two late pupils was appeared at the corner.', 'Two late pupils appeared at the corner.'],
      ok('The bus left on time after all.'),
    ], '"Arrive" and "appear" are intransitive; do not use the passive.'),
  ],

  // 6.6 Stative verbs in progressive
  '6.6': [
    p([
      ok('The students discussed the homework together.'),
      ['I am knowing the answer to the first question.', 'I know the answer to the first question.'],
      ok('My friend looked at the second one.'),
      ['She is believing it is too hard.', 'She believes it is too hard.'],
      ok('In the end, we finished the whole exercise by dinner.'),
    ], 'Stative verbs like "know" and "believe" are not used in the progressive.'),
    p([
      ok('The family settled in the new house.'),
      ['We are wanting a larger garden.', 'We want a larger garden.'],
      ok('The neighbours are very friendly.'),
      ['They are seeming happy to help us.', 'They seem happy to help us.'],
      ok('We have settled in well.'),
    ], 'Use "want" and "seem", not "are wanting"/"are seeming".'),
    p([
      ok('The customers admired the new display.'),
      ['I am preferring the blue scarf.', 'I prefer the blue scarf.'],
      ok('My sister likes the red one better.'),
      ['She is understanding the price too well.', 'She understands the price too well.'],
      ok('We bought both in the end.'),
    ], 'Stative verbs "prefer" and "understand" stay in the simple present.'),
    p([
      ok('The travellers reached the mountain village.'),
      ['We are hearing the church bells already.', 'We hear the church bells already.'],
      ok('The air smells of pine and wood smoke.'),
      ['I am seeing the whole valley from here.', 'I see the whole valley from here.'],
      ok('The view was worth the long climb.'),
    ], 'Verbs of perception like "hear" and "see" are stative here.'),
    p([
      ok('The team reviewed the match on video.'),
      ['The coach is doubting the referee\'s decision.', 'The coach doubts the referee\'s decision.'],
      ok('The players watched the replay closely.'),
      ['They are remembering the last goal clearly.', 'They remember the last goal clearly.'],
      ok('They agreed to train harder.'),
    ], 'Use "doubts" and "remember", not the progressive forms.'),
  ],

  // 6.7 Tense consistency
  '6.7': [
    p([
      ok('My aunt told us a story from her childhood.'),
      ['She said she will visit the old town every summer.', 'She said she would visit the old town every summer.'],
      ok('We listened with great interest.'),
      ['She explained that she is only ten at the time.', 'She explained that she was only ten at the time.'],
      ok('The story made us all laugh.'),
    ], 'In reported speech after a past verb, shift to the past: "would visit", "was only ten".'),
    p([
      ok('The manager described the new plan to the team.'),
      ['He said the changes will start next month.', 'He said the changes would start next month.'],
      ok('He explained the reason for each decision.'),
      ['He added that the budget increases by ten per cent.', 'He added that the budget would increase by ten per cent.'],
      ok('The team asked a few questions afterwards.'),
    ], 'Keep the tense consistent with the past reporting verb: "would start", "would increase".'),
    p([
      ok('The pupil described her weekend to the class.'),
      ['She said she goes to the lake with her family.', 'She said she went to the lake with her family.'],
      ok('She showed a photo of the boat.'),
      ['She explained that the water was cold in the morning.', 'She explained that the water was cold in the morning.'],
      ok('Everyone wanted to visit the lake too.'),
    ], 'After a past reporting verb, use "went", not "goes".'),
    p([
      ok('The guide described the history of the castle.'),
      ['He said the castle is built in the fifteenth century.', 'He said the castle was built in the fifteenth century.'],
      ok('We walked around the old walls.'),
      ['He explained that the tower burns down long ago.', 'He explained that the tower had burned down long ago.'],
      ok('The visit ended before the rain came.'),
    ], 'Shift to past or past perfect after the past reporting verb.'),
    p([
      ok('The twins told their parents about the trip.'),
      ['They said the journey takes five hours.', 'They said the journey took five hours.'],
      ok('They described the mountain views.'),
      ['They said they will go again next year.', 'They said they would go again next year.'],
      ok('Their parents were happy to hear it.'),
    ], 'Use "took" and "would go" to match the past reporting verbs.'),
  ],

  // 6.8 Transitivity
  '6.8': [
    p([
      ok('The team met to plan the new project.'),
      ['They discussed about the schedule for an hour.', 'They discussed the schedule for an hour.'],
      ok('Everyone wrote down the key dates.'),
      ['The manager then explained about the budget.', 'The manager then explained the budget.'],
      ok('The meeting ended on time.'),
    ], '"Discuss" and "explain" take a direct object, with no "about".'),
    p([
      ok('The guests arrived at the hotel.'),
      ['They entered into the large lobby together.', 'They entered the large lobby together.'],
      ok('A porter carried the bags upstairs.'),
      ['They reached at their rooms by four.', 'They reached their rooms by four.'],
      ok('Dinner was served in the evening.'),
    ], '"Enter" and "reach" take a direct object, with no preposition.'),
    p([
      ok('The class answered the difficult questions.'),
      ['One pupil replied the final question.', 'One pupil answered the final question.'],
      ok('The teacher praised the clear explanations.'),
      ['Another pupil responded the challenge.', 'Another pupil responded to the challenge.'],
      ok('The lesson ended with a short break.'),
    ], '"Reply" and "respond" need "to"; "answer" takes a direct object.'),
    p([
      ok('The neighbours discussed the noisy road.'),
      ['They complained the traffic to the council.', 'They complained about the traffic to the council.'],
      ok('A meeting was arranged for the following week.'),
      ['The council explained the new plan.', 'The council explained the new plan.'],
      ok('A speed limit was introduced soon after.'),
    ], '"Complain" needs "about"; "explain" takes a direct object.'),
    p([
      ok('The workers finished the repairs early.'),
      ['They mentioned about the broken pipe.', 'They mentioned the broken pipe.'],
      ok('The owner inspected the whole room.'),
      ['She entered the empty flat carefully.', 'She entered the empty flat carefully.'],
      ok('The flat was ready for a new tenant.'),
    ], '"Mention" and "enter" take direct objects without "about"/"into".'),
  ],

  // 6.9 Gerund vs infinitive
  '6.9': [
    p([
      ok('My sister enjoys her swimming lessons.'),
      ['She enjoys to swim in the sea in summer.', 'She enjoys swimming in the sea in summer.'],
      ok('She practices at the pool every week.'),
      ['She has decided to join the local club.', 'She has decided to join the local club.'],
      ok('Her teacher says she is improving fast.'),
    ], '"Enjoy" takes a gerund ("swimming"); "decide" takes an infinitive ("to join").'),
    p([
      ok('The family plans its holidays carefully.'),
      ['They hope visiting the coast this year.', 'They hope to visit the coast this year.'],
      ok('The children are excited about the trip.'),
      ['They look forward to swim in the sea.', 'They look forward to swimming in the sea.'],
      ok('The hotel was booked in March.'),
    ], '"Hope" takes an infinitive; after a preposition use the gerund "swimming".'),
    p([
      ok('Ben has started a new hobby.'),
      ['He has begun to collects old stamps.', 'He has begun to collect old stamps.'],
      ok('He keeps them in a neat album.'),
      ['He also enjoys to read about history.', 'He also enjoys reading about history.'],
      ok('His collection is growing quickly.'),
    ], '"Begin" takes an infinitive ("to collect"); "enjoy" takes a gerund ("reading").'),
    p([
      ok('The couple planned their new kitchen.'),
      ['They wanted choosing the tiles themselves.', 'They wanted to choose the tiles themselves.'],
      ok('They visited several shops.'),
      ['They finished to paint the walls on Sunday.', 'They finished painting the walls on Sunday.'],
      ok('The kitchen looked lovely in the end.'),
    ], '"Want" takes an infinitive; "finish" takes a gerund.'),
    p([
      ok('The students prepared for the exam.'),
      ['They avoided to study the hardest topic.', 'They avoided studying the hardest topic.'],
      ok('The teacher set extra practice questions.'),
      ['Everyone agreed working together more often.', 'Everyone agreed to work together more often.'],
      ok('Their results improved a great deal.'),
    ], '"Avoid" takes a gerund; "agree" takes an infinitive.'),
  ],

  // 6.10 to + base form
  '6.10': [
    p([
      ok('The children wanted to help in the garden.'),
      ['They tried to goes outside before the rain.', 'They tried to go outside before the rain.'],
      ok('The dark clouds gathered quickly.'),
      ['They hoped to finishes before dinner.', 'They hoped to finish before dinner.'],
      ok('They managed to tidy the whole shed.'),
    ], 'After "to" use the base form: "to go", "to finish".'),
    p([
      ok('My cousin plans to travel this summer.'),
      ['She wants to sees the northern lights.', 'She wants to see the northern lights.'],
      ok('She has saved money for the trip.'),
      ['She hopes to travels with two friends.', 'She hopes to travel with two friends.'],
      ok('They booked the tickets in spring.'),
    ], 'Use the base form after "to": "to see", "to travel".'),
    p([
      ok('The team needs to improve its defence.'),
      ['The coach asked them to trains harder.', 'The coach asked them to train harder.'],
      ok('They agreed to meet on Saturday.'),
      ['They promised to arrives early.', 'They promised to arrive early.'],
      ok('The next match is on Friday.'),
    ], 'Use "to train" and "to arrive".'),
    p([
      ok('The school decided to build a new hall.'),
      ['The head teacher wanted to opens it in autumn.', 'The head teacher wanted to open it in autumn.'],
      ok('The builders started the work in June.'),
      ['They hoped to completes it before the term began.', 'They hoped to complete it before the term began.'],
      ok('The hall opened right on time.'),
    ], 'Use the base form "to open" and "to complete".'),
    p([
      ok('My neighbour offered to water our plants.'),
      ['She promised to takes care of them daily.', 'She promised to take care of them daily.'],
      ok('We gave her a spare key.'),
      ['She was happy to helps us out.', 'She was happy to help us out.'],
      ok('The plants looked healthy when we returned.'),
    ], 'Use "to take" and "to help" after "to".'),
  ],

  // 6.11 Phrasal verbs
  '6.11': [
    p([
      ok('The bin was full of old newspapers.'),
      ['Please take out it before the truck arrives.', 'Please take it out before the truck arrives.'],
      ok('The truck comes on Thursday mornings.'),
      ['I will pick up them from the corner later.', 'I will pick them up from the corner later.'],
      ok('After that, the street is always tidy.'),
    ], 'A pronoun object goes between the verb and its particle: "take it out", "pick them up".'),
    p([
      ok('The room looked dark in the evening.'),
      ['Could you turn on it for me?', 'Could you turn it on for me?'],
      ok('The lamp stands by the armchair.'),
      ['Please switch off them before bed.', 'Please switch them off before bed.'],
      ok('We saved electricity that month.'),
    ], 'Use "turn it on" and "switch them off".'),
    p([
      ok('My sister left her coat at school.'),
      ['She will look for it tomorrow.', 'She will look for it tomorrow.'],
      ok('She asked the office for help.'),
      ['They promised to sort out it quickly.', 'They promised to sort it out quickly.'],
      ok('Eventually, the coat was found the next day.'),
    ], 'The pronoun goes before the particle: "sort it out".'),
    p([
      ok('The guests arrived after dinner.'),
      ['We had to put up it in the spare room.', 'We had to put it up in the spare room.'],
      ok('The room was small but tidy.'),
      ['They helped us take down it in the morning.', 'They helped us take it down in the morning.'],
      ok('By noon, everything was back in place.'),
    ], 'Use "put it up" and "take it down".'),
    p([
      ok('The class collected old toys for charity.'),
      ['They wanted to give away them to the shelter.', 'They wanted to give them away to the shelter.'],
      ok('A van arrived to collect the boxes.'),
      ['Volunteers helped load up them carefully.', 'Volunteers helped load them up carefully.'],
      ok('Afterwards, the shelter thanked the school warmly.'),
    ], 'Use "give them away" and "load them up".'),
  ],

  // 6.12 Modals and semi-modals
  '6.12': [
    p([
      ok('The pupils prepared for the school trip.'),
      ['Everyone must to bring a packed lunch.', 'Everyone must bring a packed lunch.'],
      ok('The bus leaves at eight sharp.'),
      ['The children can to wear casual clothes.', 'The children can wear casual clothes.'],
      ok('The trip lasts the whole day.'),
    ], 'Modals take the base form with no "to": "must bring", "can wear".'),
    p([
      ok('The office introduced a new system.'),
      ['Staff should to read the guide carefully.', 'Staff should read the guide carefully.'],
      ok('Training sessions start next week.'),
      ['You may to book a session online.', 'You may book a session online.'],
      ok('The system goes live in April.'),
    ], 'Use "should read" and "may book" without "to".'),
    p([
      ok('The guests arrived for the weekend.'),
      ['They might to stay until Monday.', 'They might stay until Monday.'],
      ok('We prepared the spare room.'),
      ['They could to arrive earlier than planned.', 'They could arrive earlier than planned.'],
      ok('Either way, we were ready.'),
    ], 'Use "might stay" and "could arrive".'),
    p([
      ok('The garden needed some attention.'),
      ['We must to cut the grass this weekend.', 'We must cut the grass this weekend.'],
      ok('The hedge has grown very tall.'),
      ['I can to help you on Saturday.', 'I can help you on Saturday.'],
      ok('By Sunday evening, the garden looked neat.'),
    ], 'Use "must cut" and "can help".'),
    p([
      ok('The travellers reached the border crossing.'),
      ['They should to show their passports.', 'They should show their passports.'],
      ok('A queue formed at the checkpoint.'),
      ['They might to wait for an hour.', 'They might wait for an hour.'],
      ok('The crossing took less time than expected.'),
    ], 'Use "should show" and "might wait".'),
  ],

  // 6.13 Question formation
  '6.13': [
    p([
      ok('The pupils finished the exercise early.'),
      ['Where you are going after school?', 'Where are you going after school?'],
      ok('Some of them go to the library.'),
      ['What she does read in the evenings?', 'What does she read in the evenings?'],
      ok('Then the bell rang for the end of the day.'),
    ], 'In questions, invert subject and auxiliary: "are you going", "does she read".'),
    p([
      ok('The family planned a holiday abroad.'),
      ['When they will leave for the airport?', 'When will they leave for the airport?'],
      ok('The flight is early in the morning.'),
      ['Where you have put the tickets?', 'Where have you put the tickets?'],
      ok('Everything was ready on time.'),
    ], 'Use "will they leave" and "have you put" in questions.'),
    p([
      ok('The chef prepared the evening menu.'),
      ['How you make the soup so quickly?', 'How do you make the soup so quickly?'],
      ok('The recipe is a family secret.'),
      ['Why she uses fresh herbs every time?', 'Why does she use fresh herbs every time?'],
      ok('The dinner was delicious.'),
    ], 'Questions need "do/does": "do you make", "does she use".'),
    p([
      ok('The team travelled to the away match.'),
      ['When the coach will announce the line-up?', 'When will the coach announce the line-up?'],
      ok('The players waited in the changing room.'),
      ['Who you saw at the stadium yesterday?', 'Who did you see at the stadium yesterday?'],
      ok('The match began at three.'),
    ], 'Use "will the coach announce" and "did you see".'),
    p([
      ok('The students organised a charity run.'),
      ['Where they will start the race?', 'Where will they start the race?'],
      ok('The route goes through the park.'),
      ['How long it will take to finish?', 'How long will it take to finish?'],
      ok('In the end, the event raised a lot of money.'),
    ], 'Invert the auxiliary: "will they start", "will it take".'),
  ],

  // 6.14 Negation
  '6.14': [
    p([
      ok('My brother saved his pocket money carefully.'),
      ['He does not have no money left now.', 'He does not have any money left now.'],
      ok('He spent it on a new bicycle.'),
      ['He does not want nothing else for his birthday.', 'He does not want anything else for his birthday.'],
      ok('He rides it every day.'),
    ], 'Standard English uses one negative: "not... any".'),
    p([
      ok('The team played an away match on Sunday.'),
      ['They did not score no goals in the first half.', 'They did not score any goals in the first half.'],
      ok('The coach gave them a firm talk.'),
      ['They did not lose no confidence.', 'They did not lose any confidence.'],
      ok('In the end, they won the second half easily.'),
    ], 'Use "any" after "not", not a second negative.'),
    p([
      ok('The children tidied the classroom after school.'),
      ['Nobody did not help with the chairs.', 'Nobody helped with the chairs.'],
      ok('They stacked them by the wall.'),
      ['They did not leave nothing on the floor.', 'They did not leave anything on the floor.'],
      ok('The room was spotless in an hour.'),
    ], '"Nobody" is already negative; do not add "did not".'),
    p([
      ok('The shop stayed open late on Friday.'),
      ['There were not no customers all evening.', 'There were no customers all evening.'],
      ok('The owner read a book behind the counter.'),
      ['She did not serve nobody after nine.', 'She did not serve anyone after nine.'],
      ok('She closed the shop at ten.'),
    ], 'Use "no" or "not... any", never both.'),
    p([
      ok('The travellers set off early in the morning.'),
      ['They did not have no maps for the route.', 'They did not have any maps for the route.'],
      ok('They followed the road signs instead.'),
      ['They did not meet nobody on the way.', 'They did not meet anybody on the way.'],
      ok('By noon, they reached the coast.'),
    ], 'After "not", use "any"/"anybody".'),
  ],

  // 6.15 Imperatives
  '6.15': [
    p([
      ok('The children were getting ready for bed.'),
      ['"Don\'t goes upstairs yet," said their mother.', '"Don\'t go upstairs yet," said their mother.'],
      ok('She wanted them to brush their teeth first.'),
      ['"Washes your hands too," she added.', '"Wash your hands too," she added.'],
      ok('They were in bed by eight.'),
    ], 'Imperatives use the base form: "don\'t go", "wash".'),
    p([
      ok('The coach gathered the players on the field.'),
      ['"Listens carefully to the plan," he said.', '"Listen carefully to the plan," he said.'],
      ok('He pointed to the far goal.'),
      ['"Don\'t loses your positions," he warned.', '"Don\'t lose your positions," he warned.'],
      ok('The team played well that day.'),
    ], 'Use the base forms "listen" and "don\'t lose".'),
    p([
      ok('The teacher handed out the test papers.'),
      ['"Please writes your name at the top," she said.', '"Please write your name at the top," she said.'],
      ok('The class began at once.'),
      ['"Don\'t talks during the test," she added.', '"Don\'t talk during the test," she added.'],
      ok('Everyone worked quietly.'),
    ], 'Imperatives use "write" and "don\'t talk".'),
    p([
      ok('The hikers reached a steep path.'),
      ['"Takes small steps here," said the guide.', '"Take small steps here," said the guide.'],
      ok('The rocks were wet from the rain.'),
      ['"Don\'t rushes," he warned the group.', '"Don\'t rush," he warned the group.'],
      ok('They reached the top safely.'),
    ], 'Use the base forms "take" and "don\'t rush".'),
    p([
      ok('The chef was preparing the soup.'),
      ['"Tastes it before serving," she told the helper.', '"Taste it before serving," she told the helper.'],
      ok('The helper added a little salt.'),
      ['"Don\'t forgets the pepper," the chef added.', '"Don\'t forget the pepper," the chef added.'],
      ok('The soup was perfect.'),
    ], 'Imperatives use "taste" and "don\'t forget".'),
  ],

  // 6.16 Conditionals
  '6.16': [
    p([
      ok('The garden needs a lot of water in summer.'),
      ['If I will water the plants daily, they will survive.', 'If I water the plants daily, they will survive.'],
      ok('The forecast promises a hot week.'),
      ['If it will rain tomorrow, I will stay indoors.', 'If it rains tomorrow, I will stay indoors.'],
      ok('The flowers should be fine either way.'),
    ], 'In real conditionals, use the present tense in the if-clause, not "will".'),
    p([
      ok('The team needs to win the next match.'),
      ['If they will play well, they will reach the final.', 'If they play well, they will reach the final.'],
      ok('The coach is confident about the squad.'),
      ['If the captain will return, the team will be stronger.', 'If the captain returns, the team will be stronger.'],
      ok('The final is on Saturday.'),
    ], 'Use "if they play" and "if the captain returns" (present tense).'),
    p([
      ok('The family plans a trip to the mountains.'),
      ['If the weather will be good, we will drive up on Friday.', 'If the weather is good, we will drive up on Friday.'],
      ok('The cabin is already booked.'),
      ['If we will leave early, we will avoid the traffic.', 'If we leave early, we will avoid the traffic.'],
      ok('The journey should take four hours.'),
    ], 'Use the present tense in the if-clause: "is", "leave".'),
    p([
      ok('The students are revising for the exam.'),
      ['If she will study hard, she will pass easily.', 'If she studies hard, she will pass easily.'],
      ok('The teacher gave them a study plan.'),
      ['If they will follow it, they will do well.', 'If they follow it, they will do well.'],
      ok('The exam is next Tuesday.'),
    ], 'Use "studies" and "follow" in the if-clause, not "will".'),
    p([
      ok('The business hopes to grow this year.'),
      ['If the sales will increase, they will hire more staff.', 'If the sales increase, they will hire more staff.'],
      ok('The manager prepared a budget.'),
      ['If they will open a new branch, they will need more space.', 'If they open a new branch, they will need more space.'],
      ok('The plan goes to the board in June.'),
    ], 'Use present-tense verbs in the if-clause: "increase", "open".'),
  ],

  // 6.17 Subjunctive and wish
  '6.17': [
    p([
      ok('The weather was cold during the holiday.'),
      ['I wish I was somewhere warm.', 'I wish I were somewhere warm.'],
      ok('The heating was broken all week.'),
      ['If I was you, I would complain to the hotel.', 'If I were you, I would complain to the hotel.'],
      ok('We made the best of a difficult week.'),
    ], 'In "wish" and hypotheticals, use "were" for all subjects.'),
    p([
      ok('My friend is studying medicine.'),
      ['She wishes she was already a doctor.', 'She wishes she were already a doctor.'],
      ok('The course takes several years.'),
      ['If she was allowed, she would start work tomorrow.', 'If she were allowed, she would start work tomorrow.'],
      ok('She works very hard in the meantime.'),
    ], 'Use "were" in "wish" and in the hypothetical clause.'),
    p([
      ok('The team missed the final by one point.'),
      ['The coach wishes he was still in the competition.', 'The coach wishes he were still in the competition.'],
      ok('The players trained hard all season.'),
      ['If he was able, he would replay the last minute.', 'If he were able, he would replay the last minute.'],
      ok('They plan to try again next year.'),
    ], 'Use the subjunctive "were" after "wish" and "if".'),
    p([
      ok('The old house is full of character.'),
      ['I wish it was a little warmer inside.', 'I wish it were a little warmer inside.'],
      ok('The rooms are spacious and bright.'),
      ['If it was cheaper, we would buy it at once.', 'If it were cheaper, we would buy it at once.'],
      ok('For now, we simply enjoy visiting.'),
    ], 'Hypotheticals take "were": "I wish it were", "if it were".'),
    p([
      ok('The exam results arrive next week.'),
      ['She wishes she was less nervous about them.', 'She wishes she were less nervous about them.'],
      ok('She has prepared for months.'),
      ['If she was calmer, she would sleep better.', 'If she were calmer, she would sleep better.'],
      ok('Her friends keep her cheerful.'),
    ], 'Use "were" after "wish" and in the hypothetical if-clause.'),
  ],

  // 6.18 Reported speech
  '6.18': [
    p([
      ok('My sister called me from the station.'),
      ['She said me the train was delayed.', 'She told me the train was delayed.'],
      ok('I offered to wait for her.'),
      ['She said she would arrive by six.', 'She said she would arrive by six.'],
      ok('We met at the café nearby.'),
    ], 'Use "tell + person" and "say + clause" (no "me" after "said" here).'),
    p([
      ok('The teacher spoke to the class.'),
      ['She told that the test would be on Friday.', 'She said that the test would be on Friday.'],
      ok('The pupils wrote the date down.'),
      ['She also told us to revise the first chapter.', 'She also told us to revise the first chapter.'],
      ok('The test was fair and short.'),
    ], '"Say" introduces a clause; "tell" needs a person object.'),
    p([
      ok('My colleague updated me about the meeting.'),
      ['He said me the project was on track.', 'He told me the project was on track.'],
      ok('We reviewed the schedule together.'),
      ['He explained that the deadline had moved.', 'He explained that the deadline had moved.'],
      ok('The new deadline suits everyone.'),
    ], 'Use "told me" rather than "said me".'),
    p([
      ok('The guide welcomed us to the museum.'),
      ['She said us the tour would last an hour.', 'She told us the tour would last an hour.'],
      ok('We followed her through the main hall.'),
      ['She explained that photography was not allowed.', 'She explained that photography was not allowed.'],
      ok('The tour ended by the gift shop.'),
    ], 'Use "told us" (person object) for reported information.'),
    p([
      ok('My neighbour asked about the parcel.'),
      ['He told that it had arrived this morning.', 'He said that it had arrived this morning.'],
      ok('I thanked him for letting me know.'),
      ['He also told me he had signed for it.', 'He also told me he had signed for it.'],
      ok('I collected it after lunch.'),
    ], '"Said that..." for a clause; "told me (that)..." with a person.'),
  ],

  // 6.19 Causatives and perception verbs
  '6.19': [
    p([
      ok('The sad film moved the whole audience.'),
      ['It made me to cry at the end.', 'It made me cry at the end.'],
      ok('My friend passed me a tissue.'),
      ['The ending let us to think about our own lives.', 'The ending let us think about our own lives.'],
      ok('We talked about it all the way home.'),
    ], '"Make" and "let" take a bare infinitive: "made me cry", "let us think".'),
    p([
      ok('The teacher wanted the room tidy.'),
      ['She had the desks to move to the back.', 'She had the desks moved to the back.'],
      ok('Two pupils helped at once.'),
      ['She made them to work quietly.', 'She made them work quietly.'],
      ok('The room was ready in ten minutes.'),
    ], 'Use "had the desks moved" (causative) and "made them work" (bare infinitive).'),
    p([
      ok('My parents arranged a repair for the car.'),
      ['They had it to fix at the local garage.', 'They had it fixed at the local garage.'],
      ok('The mechanic replaced the brakes.'),
      ['He let us to watch the repair.', 'He let us watch the repair.'],
      ok('The car ran smoothly afterwards.'),
    ], 'Use "had it fixed" and "let us watch".'),
    p([
      ok('The gardener tidied the whole yard.'),
      ['She had the old tree to cut down.', 'She had the old tree cut down.'],
      ok('The yard looked much brighter.'),
      ['She watched the birds to return to the feeder.', 'She watched the birds return to the feeder.'],
      ok('The garden became her favourite place.'),
    ], 'Use "had the tree cut down" and "watched the birds return".'),
    p([
      ok('The manager improved the office.'),
      ['She had the walls to paint a bright colour.', 'She had the walls painted a bright colour.'],
      ok('The staff chose the shade themselves.'),
      ['She let them to decorate their own desks.', 'She let them decorate their own desks.'],
      ok('The office felt much more welcoming.'),
    ], 'Use "had the walls painted" and "let them decorate".'),
  ],

  // 6.20 Verb + clause patterns
  '6.20': [
    p([
      ok('The committee discussed the new proposal.'),
      ['They suggested him to apply for the grant.', 'They suggested that he apply for the grant.'],
      ok('He prepared the documents carefully.'),
      ['The chair explained him the next steps.', 'The chair explained the next steps to him.'],
      ok('The application was sent on time.'),
    ], '"Suggest" takes a that-clause, and "explain" takes "to + person".'),
    p([
      ok('The doctor reviewed the patient\'s notes.'),
      ['She recommended him to rest for a week.', 'She recommended that he rest for a week.'],
      ok('She wrote a short summary.'),
      ['She described him the treatment in detail.', 'She described the treatment to him in detail.'],
      ok('The patient left feeling reassured.'),
    ], 'Use "recommend that he rest" and "describe ... to him".'),
    p([
      ok('The teacher helped the new pupil.'),
      ['She explained him the homework rules.', 'She explained the homework rules to him.'],
      ok('He wrote everything in his book.'),
      ['She suggested him to join the reading club.', 'She suggested that he join the reading club.'],
      ok('He joined the club the same week.'),
    ], 'Use "explained ... to him" and "suggested that he join".'),
    p([
      ok('The manager trained the new staff.'),
      ['She proposed them a new schedule.', 'She proposed a new schedule to them.'],
      ok('They discussed it in a short meeting.'),
      ['She recommended them to arrive early.', 'She recommended that they arrive early.'],
      ok('The schedule worked well.'),
    ], 'Use "propose ... to them" and "recommend that they arrive".'),
    p([
      ok('The guide helped the visitors.'),
      ['She described them the route clearly.', 'She described the route to them clearly.'],
      ok('They marked it on their maps.'),
      ['She suggested them to start before noon.', 'She suggested that they start before noon.'],
      ok('The walk was lovely in the morning light.'),
    ], 'Use "described ... to them" and "suggested that they start".'),
  ],

  // =========================================================================
  // Section 7 — Adjectives and Adverbs
  // =========================================================================

  // 7.1 Adjective order
  '7.1': [
    p([
      ok('My uncle collects vintage cars.'),
      ['He keeps a red small sports car in the garage.', 'He keeps a small red sports car in the garage.'],
      ok('He polishes it every weekend.'),
      ['Beside it stands a wooden old chest.', 'Beside it stands an old wooden chest.'],
      ok('The garage smells of oil and polish.'),
    ], 'Order: size before colour, age before material ("a small red car", "an old wooden chest").'),
    p([
      ok('The couple furnished their first flat.'),
      ['They bought a round modern glass table.', 'They bought a modern round glass table.'],
      ok('The chairs came from a market.'),
      ['On the wall hangs a beautiful French landscape.', 'On the wall hangs a beautiful French landscape.'],
      ok('The flat felt warm and inviting.'),
    ], 'Order: opinion, then origin, then noun; and shape before material ("round glass").'),
    p([
      ok('The family visited a country market.'),
      ['A farmer sold us some sweet green apples.', 'A farmer sold us some sweet green apples.'],
      ok('We filled two large bags.'),
      ['My mother chose a long striped red scarf.', 'My mother chose a long red striped scarf.'],
      ok('We carried everything home happily.'),
    ], 'Colour comes before the type/pattern word: "long red striped scarf".'),
    p([
      ok('My grandparents moved to a coastal village.'),
      ['They live in a stone old cottage near the harbour.', 'They live in an old stone cottage near the harbour.'],
      ok('The garden runs down to the water.'),
      ['A friendly black Labrador greets every visitor.', 'A friendly black Labrador greets every visitor.'],
      ok('We visit them every summer.'),
    ], 'Age before material: "an old stone cottage".'),
    p([
      ok('The team designed a new building.'),
      ['The architect proposed a tall glass modern tower.', 'The architect proposed a tall modern glass tower.'],
      ok('The council approved the plan.'),
      ['Workers cleared a large empty grey site.', 'Workers cleared a large grey empty site.'],
      ok('The building opened three years later.'),
    ], 'Order: size, shape, age ("a large grey empty site") and size, age, material ("tall modern glass tower").'),
  ],

  // 7.2 Comparatives
  '7.2': [
    p([
      ok('The two sisters both love running.'),
      ['Anna is more taller than her sister.', 'Anna is taller than her sister.'],
      ok('She trains three times a week.'),
      ['Her times are getting more better every month.', 'Her times are getting better every month.'],
      ok('The coach expects a strong season.'),
    ], 'Use only one comparative marker: "taller", "better" (never "more taller").'),
    p([
      ok('The city has two main bridges.'),
      ['The new bridge is more wider than the old one.', 'The new bridge is wider than the old one.'],
      ok('It carries traffic in both directions.'),
      ['The old bridge is more narrower.', 'The old bridge is narrower.'],
      ok('Both bridges are busy at rush hour.'),
    ], 'Use "wider" and "narrower", not "more wider"/"more narrower".'),
    p([
      ok('We compared two hotels for our holiday.'),
      ['The seaside hotel was more cheaper.', 'The seaside hotel was cheaper.'],
      ok('It was also much nearer the beach.'),
      ['The city hotel looked more nicer in the photos.', 'The city hotel looked nicer in the photos.'],
      ok('We chose the seaside hotel in the end.'),
    ], 'Use "cheaper" and "nicer" as single comparatives.'),
    p([
      ok('My brother and I both play chess.'),
      ['He is more cleverer than me at the game.', 'He is cleverer than me at the game.'],
      ok('He practises against the computer.'),
      ['His openings are more stronger now.', 'His openings are stronger now.'],
      ok('I am slowly catching up.'),
    ], 'Use "cleverer" and "stronger", not double comparatives.'),
    p([
      ok('The town built two new pools.'),
      ['The outdoor pool is more bigger.', 'The outdoor pool is bigger.'],
      ok('It opens only in summer.'),
      ['The indoor pool is more busier in winter.', 'The indoor pool is busier in winter.'],
      ok('Both pools are popular with families.'),
    ], 'Use "bigger" and "busier" as single comparatives.'),
  ],

  // 7.3 Superlatives
  '7.3': [
    p([
      ok('The class studied mountains around the world.'),
      ['Everest is the most highest mountain on Earth.', 'Everest is the highest mountain on Earth.'],
      ok('Many climbers dream of reaching it.'),
      ['It is also the most famousest peak in the world.', 'It is also the most famous peak in the world.'],
      ok('The subject fascinated everyone.'),
    ], 'Use one superlative marker: "the highest", "the most famous".'),
    p([
      ok('The library holds thousands of books.'),
      ['This is the most oldest one in the collection.', 'This is the oldest one in the collection.'],
      ok('It was printed two hundred years ago.'),
      ['It is the most rarest book here.', 'It is the rarest book here.'],
      ok('Visitors come to see it every week.'),
    ], 'Use "the oldest" and "the rarest" (no "most" with -est).'),
    p([
      ok('We watched a documentary about oceans.'),
      ['The Pacific is the most deepest ocean.', 'The Pacific is the deepest ocean.'],
      ok('It covers a huge area of the planet.'),
      ['It is also the most largest by far.', 'It is also the largest by far.'],
      ok('The film was full of surprises.'),
    ], 'Use "the deepest" and "the largest" as single superlatives.'),
    p([
      ok('The bakery is famous in our town.'),
      ['Customers say it makes the most best bread.', 'Customers say it makes the best bread.'],
      ok('The baker starts work at four.'),
      ['She uses the most freshest flour.', 'She uses the freshest flour.'],
      ok('There is always a queue by eight.'),
    ], 'Use "the best" and "the freshest".'),
    p([
      ok('The team reviewed its season.'),
      ['That was the most worst match of the year.', 'That was the worst match of the year.'],
      ok('They lost by four goals.'),
      ['It was also the most unluckiest day.', 'It was also the unluckiest day.'],
      ok('They improved in every game after that.'),
    ], 'Use "the worst" and "the unluckiest".'),
  ],

  // 7.4 as...as / so...as
  '7.4': [
    p([
      ok('The twins went to the same school.'),
      ['Tom is as tall than his brother.', 'Tom is as tall as his brother.'],
      ok('People often confuse them.'),
      ['They are not so different than they look.', 'They are not so different as they look.'],
      ok('Their teachers tell them apart easily.'),
    ], 'Use "as ... as" in comparisons of equality, and "not so ... as" in the negative.'),
    p([
      ok('The two cafés sit on the same street.'),
      ['The new café is not as busy than the old one.', 'The new café is not as busy as the old one.'],
      ok('It opened just last month.'),
      ['Its coffee is as good than the other\'s.', 'Its coffee is as good as the other\'s.'],
      ok('More customers discover it each week.'),
    ], 'Use "as busy as" and "as good as".'),
    p([
      ok('The siblings both play the piano.'),
      ['Maya practises as often than her brother.', 'Maya practises as often as her brother.'],
      ok('They perform at the same concert.'),
      ['Her playing is not so confident than his yet.', 'Her playing is not so confident as his yet.'],
      ok('They support each other well.'),
    ], 'Use "as often as" and "not so ... as".'),
    p([
      ok('The hikers compared two routes.'),
      ['The north path is not as steep than the south one.', 'The north path is not as steep as the south one.'],
      ok('But it is twice as long.'),
      ['Both views are as beautiful than any painting.', 'Both views are as beautiful as any painting.'],
      ok('They chose the shorter route.'),
    ], 'Use "as steep as" and "as beautiful as".'),
    p([
      ok('The competition featured two strong teams.'),
      ['The visitors were as quick than the home side.', 'The visitors were as quick as the home side.'],
      ok('The match stayed level for an hour.'),
      ['The home players were not so tired than the visitors.', 'The home players were not so tired as the visitors.'],
      ok('The home team scored late on.'),
    ], 'Use "as quick as" and "not so ... as".'),
  ],

  // 7.5 Adverb form
  '7.5': [
    p([
      ok('The choir performed at the school concert.'),
      ['The soloist sang beautiful.', 'The soloist sang beautifully.'],
      ok('The audience clapped for a long time.'),
      ['The pianist played the final piece very good.', 'The pianist played the final piece very well.'],
      ok('Everyone left in high spirits.'),
    ], 'Modify a verb with an adverb: "sang beautifully", "played ... well".'),
    p([
      ok('The driver took the mountain road carefully.'),
      ['He always drives very careful.', 'He always drives very carefully.'],
      ok('The road winds through the hills.'),
      ['He checks his mirrors regular.', 'He checks his mirrors regularly.'],
      ok('They reached the coast safely.'),
    ], 'Use the adverbs "carefully" and "regularly".'),
    p([
      ok('The pupil answered the questions quickly.'),
      ['She writes very neat.', 'She writes very neatly.'],
      ok('The teacher praised her work.'),
      ['She also listens very attentive.', 'She also listens very attentively.'],
      ok('Her marks improved all year.'),
    ], 'Use "neatly" and "attentively" to modify the verbs.'),
    p([
      ok('The team prepared for the final.'),
      ['They trained very hard and played brilliant.', 'They trained very hard and played brilliantly.'],
      ok('The crowd cheered throughout.'),
      ['The captain spoke calm to the players.', 'The captain spoke calmly to the players.'],
      ok('They lifted the trophy at last.'),
    ], 'Use "brilliantly" and "calmly".'),
    p([
      ok('The chef prepared the evening meal.'),
      ['She chopped the vegetables quick and precise.', 'She chopped the vegetables quickly and precisely.'],
      ok('The sauce simmered on the stove.'),
      ['She tasted it careful before serving.', 'She tasted it carefully before serving.'],
      ok('The guests enjoyed every course.'),
    ], 'Use "quickly", "precisely", and "carefully".'),
  ],

  // 7.6 Adverb position
  '7.6': [
    p([
      ok('My colleague answered the phone.'),
      ['She speaks always politely to customers.', 'She always speaks politely to customers.'],
      ok('She has worked here for years.'),
      ['She drinks never coffee after noon.', 'She never drinks coffee after noon.'],
      ok('Her cheerful manner is well known.'),
    ], 'Frequency adverbs go before the main verb: "always speaks", "never drinks".'),
    p([
      ok('The bus arrives at the same time.'),
      ['It is usually busy in the morning.', 'It is usually busy in the morning.'],
      ok('Many commuters take it daily.'),
      ['They have often to stand in the aisle.', 'They often have to stand in the aisle.'],
      ok('The journey takes forty minutes.'),
    ], 'Place "usually" after "is" and "often" before "have".'),
    p([
      ok('The twins finish their homework early.'),
      ['They do always their chores first.', 'They always do their chores first.'],
      ok('Their parents are very proud.'),
      ['They are never late for dinner.', 'They are never late for dinner.'],
      ok('The family eats together each evening.'),
    ], 'Frequency adverbs go between the subject and verb, after "be": "always do", "are never".'),
    p([
      ok('The gardener tends the flower beds.'),
      ['She checks often the roses for pests.', 'She often checks the roses for pests.'],
      ok('The roses bloom twice a year.'),
      ['She waters the plants rarely in autumn.', 'She rarely waters the plants in autumn.'],
      ok('The garden wins prizes each summer.'),
    ], 'Place the adverb before the main verb: "often checks", "rarely waters".'),
    p([
      ok('The staff open the shop at nine.'),
      ['They always are friendly to customers.', 'They are always friendly to customers.'],
      ok('The manager greets everyone warmly.'),
      ['He never has missed a day of work.', 'He has never missed a day of work.'],
      ok('The shop has a loyal following.'),
    ], 'After "be" and "have" place the adverb: "are always", "has never".'),
  ],

  // 7.7 Comparison with than / parallelism
  '7.7': [
    p([
      ok('We compared the weather of two seasons.'),
      ['This summer is hotter than last summer.', 'This summer is hotter than last summer was.'],
      ok('The gardens need more water than before.'),
      ['The evenings are warmer than in May.', 'The evenings are warmer than they were in May.'],
      ok('We spend much more time outdoors now.'),
    ], 'Compare like with like: "than last summer was", "than they were in May".'),
    p([
      ok('My friends enjoy different hobbies.'),
      ['Swimming is more fun than to run.', 'Swimming is more fun than running.'],
      ok('Both keep you fit.'),
      ['Reading is quieter than to watch television.', 'Reading is quieter than watching television.'],
      ok('Everyone has their own favourite.'),
    ], 'Keep the two compared items parallel: gerund with gerund.'),
    p([
      ok('The two routes differ in difficulty.'),
      ['Cycling is faster than to walk.', 'Cycling is faster than walking.'],
      ok('The cycle path is smooth and flat.'),
      ['Walking is safer than to ride on the main road.', 'Walking is safer than riding on the main road.'],
      ok('We chose the cycle path anyway.'),
    ], 'Use parallel gerunds after "than".'),
    p([
      ok('The town compared its two parks.'),
      ['The riverside park is greener than the square.', 'The riverside park is greener than the square is.'],
      ok('It also has a larger playground.'),
      ['The play area is busier than last year.', 'The play area is busier than it was last year.'],
      ok('Families visit it all summer.'),
    ], 'Compare clause with clause: "than the square is", "than it was last year".'),
    p([
      ok('Two students discussed their subjects.'),
      ['History is more interesting than to study maths.', 'History is more interesting than studying maths.'],
      ok('Both require plenty of reading.'),
      ['Essays are easier than to sit exams for some people.', 'Essays are easier than sitting exams for some people.'],
      ok('They each chose their favourite.'),
    ], 'Keep the comparison parallel: "studying maths", "sitting exams".'),
  ],

  // =========================================================================
  // Section 8 — Prepositions
  // =========================================================================

  // 8.1 Prepositions of time and place
  '8.1': [
    p([
      ok('My cousin was born in a small hospital.'),
      ['She was born in a cold Monday morning.', 'She was born on a cold Monday morning.'],
      ok('The family celebrated for days.'),
      ['They gather every year at that same day.', 'They gather every year on that same day.'],
      ok('The story is retold at every birthday.'),
    ], 'Use "on" with days and dates: "on a Monday morning", "on that day".'),
    p([
      ok('We start school early each day.'),
      ['Lessons begin at the morning.', 'Lessons begin in the morning.'],
      ok('The first break comes at ten.'),
      ['The hall is quiet at the afternoon.', 'The hall is quiet in the afternoon.'],
      ok('Clubs run after lessons end.'),
    ], 'Use "in" with parts of the day: "in the morning", "in the afternoon".'),
    p([
      ok('My parents first met at university.'),
      ['They met at the year 1998.', 'They met in the year 1998.'],
      ok('They married two years later.'),
      ['The wedding was at a warm June day.', 'The wedding was on a warm June day.'],
      ok('They still celebrate every year.'),
    ], 'Use "in" with years and "on" with days.'),
    p([
      ok('The train stops at several towns.'),
      ['We arrived to the station early.', 'We arrived at the station early.'],
      ok('The platform was busy.'),
      ['We waited in the platform for the train.', 'We waited on the platform for the train.'],
      ok('The train left on time.'),
    ], 'Use "arrive at" and, for a raised surface, "on the platform".'),
    p([
      ok('The picture shows an old street.'),
      ['A lamp stands in the corner of the room.', 'A lamp stands in the corner of the room.'],
      ok('A rug lies in the middle of the floor.'),
      ['Some keys hang at the wall.', 'Some keys hang on the wall.'],
      ok('The street looks quiet and still.'),
    ], 'Use "on the wall" for a surface, "in the corner" for an enclosed space.'),
  ],

  // 8.2 Other preposition choices
  '8.2': [
    p([
      ok('My aunt married young.'),
      ['She is married with a teacher.', 'She is married to a teacher.'],
      ok('They live in the next town.'),
      ['She has been married to him for ten years.', 'She has been married to him for ten years.'],
      ok('They are a happy couple.'),
    ], 'Use "married to" for people.'),
    p([
      ok('The success of the plan is unsure.'),
      ['Everything depends of the weather.', 'Everything depends on the weather.'],
      ok('We will decide on Friday.'),
      ['Our plans depend of the forecast.', 'Our plans depend on the forecast.'],
      ok('We hope for a clear day.'),
    ], 'Use "depend on", never "depend of".'),
    p([
      ok('The doctor gave clear advice.'),
      ['This medicine is good to a headache.', 'This medicine is good for a headache.'],
      ok('Take it twice a day.'),
      ['It is also useful to a sore throat.', 'It is also useful for a sore throat.'],
      ok('The chemist explained the dose.'),
    ], 'Use "good for" and "useful for" a purpose or condition.'),
    p([
      ok('The town is proud of its bridge.'),
      ['The bridge is made by steel and stone.', 'The bridge is made of steel and stone.'],
      ok('It was built by local workers.'),
      ['The design was made of a young engineer.', 'The design was made by a young engineer.'],
      ok('The bridge still stands today.'),
    ], 'Use "made of" for material and "made by" for the maker.'),
    p([
      ok('The teacher thanked the class.'),
      ['She was very pleased of their work.', 'She was very pleased with their work.'],
      ok('The results were excellent.'),
      ['She was proud of their effort.', 'She was proud of their effort.'],
      ok('The class felt encouraged.'),
    ], 'Use "pleased with" and "proud of".'),
  ],

  // 8.3 Prepositional phrases and fixed expressions
  '8.3': [
    p([
      ok('The guests reached the hotel late.'),
      ['They arrived to the city after midnight.', 'They arrived in the city after midnight.'],
      ok('A taxi waited at the entrance.'),
      ['It took them straight at the hotel.', 'It took them straight to the hotel.'],
      ok('They were asleep within an hour.'),
    ], 'Use "arrive in" a city and "to" for a destination with "take".'),
    p([
      ok('My brother loves music.'),
      ['He listens music every evening.', 'He listens to music every evening.'],
      ok('He plays the guitar too.'),
      ['He listens to the radio at breakfast.', 'He listens to the radio at breakfast.'],
      ok('He dreams of joining a band.'),
    ], 'Use "listen to" with an object.'),
    p([
      ok('The students prepared for the test.'),
      ['They were waiting the results nervously.', 'They were waiting for the results nervously.'],
      ok('The teacher marked the papers quickly.'),
      ['They asked the teacher about their marks.', 'They asked the teacher about their marks.'],
      ok('The results were good.'),
    ], 'Use "wait for" with an object.'),
    p([
      ok('The family moved to a new town.'),
      ['They had to look after of the garden.', 'They had to look after the garden.'],
      ok('The house came with a large lawn.'),
      ['They also took care of the old trees.', 'They also took care of the old trees.'],
      ok('The garden soon looked lovely.'),
    ], '"Look after" and "take care of" take objects without extra prepositions.'),
    p([
      ok('The manager reviewed the report.'),
      ['She was responsible of the whole team.', 'She was responsible for the whole team.'],
      ok('She trained the new staff.'),
      ['She was also in charge for the schedule.', 'She was also in charge of the schedule.'],
      ok('The team met every Monday.'),
    ], 'Use "responsible for" and "in charge of".'),
  ],

  // 8.4 Stranded prepositions
  '8.4': [
    p([
      ok('I met an old friend last week.'),
      ['She is the person I spoke.', 'She is the person I spoke to.'],
      ok('We talked for a long time.'),
      ['She mentioned the job she applied.', 'She mentioned the job she applied for.'],
      ok('I promised to stay in touch.'),
    ], 'Keep the preposition with its verb: "spoke to", "applied for".'),
    p([
      ok('The house was built long ago.'),
      ['It is the house I live.', 'It is the house I live in.'],
      ok('The rooms are small but warm.'),
      ['The garden is what I like most about it.', 'The garden is what I like most about it.'],
      ok('I hope to stay for years.'),
    ], 'Use "the house I live in".'),
    p([
      ok('The teacher gave us a task.'),
      ['She is the teacher we were talking.', 'She is the teacher we were talking about.'],
      ok('We had to write a short essay.'),
      ['The topic is one we are all interested.', 'The topic is one we are all interested in.'],
      ok('We handed the essays in on Friday.'),
    ], 'Keep "talking about" and "interested in".'),
    p([
      ok('The shop sells old records.'),
      ['It is the shop my father bought his first guitar.', 'It is the shop my father bought his first guitar from.'],
      ok('He still visits it sometimes.'),
      ['The owner is a man he knows well.', 'The owner is a man he knows well.'],
      ok('They always talk about music.'),
    ], 'Use "the shop ... bought his first guitar from".'),
    p([
      ok('The team needed a new coach.'),
      ['They hired the man everyone had heard.', 'They hired the man everyone had heard of.'],
      ok('He had a strong record.'),
      ['He was the person they had been looking.', 'He was the person they had been looking for.'],
      ok('The team improved under him.'),
    ], 'Keep "heard of" and "looking for".'),
  ],

  // 8.5 Prepositions with adjectives and verbs
  '8.5': [
    p([
      ok('My sister is a talented pupil.'),
      ['She is very good in maths.', 'She is very good at maths.'],
      ok('She solves problems quickly.'),
      ['She is also interested on science.', 'She is also interested in science.'],
      ok('She hopes to study engineering.'),
    ], 'Use "good at" and "interested in".'),
    p([
      ok('The team was well prepared.'),
      ['They were confident of winning the final.', 'They were confident of winning the final.'],
      ok('The coach trusted the players.'),
      ['They were capable for a strong performance.', 'They were capable of a strong performance.'],
      ok('The match went to extra time.'),
    ], 'Use "capable of" and "confident of".'),
    p([
      ok('The town became very popular.'),
      ['Visitors are fond for its old market.', 'Visitors are fond of its old market.'],
      ok('The market sells local food.'),
      ['People are proud for the market\'s history.', 'People are proud of the market\'s history.'],
      ok('It has stood there for centuries.'),
    ], 'Use "fond of" and "proud of".'),
    p([
      ok('The pupil borrowed a book.'),
      ['She was grateful of the help.', 'She was grateful for the help.'],
      ok('The librarian found it quickly.'),
      ['The book was full with pictures.', 'The book was full of pictures.'],
      ok('She read it in two days.'),
    ], 'Use "grateful for" and "full of".'),
    p([
      ok('The workers finished the job.'),
      ['They were proud for the finished bridge.', 'They were proud of the finished bridge.'],
      ok('The bridge crosses a wide river.'),
      ['It is famous with its long span.', 'It is famous for its long span.'],
      ok('Tourists photograph it every day.'),
    ], 'Use "proud of" and "famous for".'),
  ],

  // 8.6 Prepositions of movement and direction
  '8.6': [
    p([
      ok('The children walked to the park.'),
      ['They ran in the playground happily.', 'They ran into the playground happily.'],
      ok('The gate stood wide open.'),
      ['They climbed on the climbing frame.', 'They climbed onto the climbing frame.'],
      ok('They played until it grew dark.'),
    ], 'Use "into" for entering and "onto" for a surface.'),
    p([
      ok('The family set off on holiday.'),
      ['They drove in the tunnel towards the coast.', 'They drove through the tunnel towards the coast.'],
      ok('The road curved along the cliffs.'),
      ['They walked on the beach at sunset.', 'They walked onto the beach at sunset.'],
      ok('It was a peaceful evening.'),
    ], 'Use "through" for passing within, and "onto" for a surface.'),
    p([
      ok('The train crossed the valley.'),
      ['It went in a long tunnel.', 'It went through a long tunnel.'],
      ok('The view opened up on the far side.'),
      ['The track ran over a wide river.', 'The track ran over a wide river.'],
      ok('The journey took two hours.'),
    ], 'Use "through" for going within an enclosed space.'),
    p([
      ok('The hikers left the village early.'),
      ['They climbed on the steep hill.', 'They climbed up the steep hill.'],
      ok('The path was rocky and narrow.'),
      ['They walked along a ridge and down the other side.', 'They walked along a ridge and down the other side.'],
      ok('They reached the valley by noon.'),
    ], 'Use "up" and "down" for vertical movement.'),
    p([
      ok('The swallows returned in spring.'),
      ['They flew in the open window.', 'They flew through the open window.'],
      ok('They nested under the roof.'),
      ['In autumn they flew away to warmer lands.', 'In autumn they flew away to warmer lands.'],
      ok('They return to the same nest each year.'),
    ], 'Use "through" for entering an opening, and "away" for departure.'),
  ],

  // =========================================================================
  // Section 9 — Sentence structure
  // =========================================================================

  // 9.1 Subject-verb agreement (basic)
  '9.1': [
    p([
      ok('The school holds a fair every summer.'),
      ['The children plays games on the field.', 'The children play games on the field.'],
      ok('Parents watch from the shade.'),
      ['Our dog bark at every visitor.', 'Our dog barks at every visitor.'],
      ok('The fair lasts the whole afternoon.'),
    ], 'A singular subject takes "barks"; a plural subject takes "play".'),
    p([
      ok('The café opens early each day.'),
      ['The waiters serves breakfast from seven.', 'The waiters serve breakfast from seven.'],
      ok('The tables fill quickly.'),
      ['A young chef cook the eggs.', 'A young chef cooks the eggs.'],
      ok('The smell draws people inside.'),
    ], 'Use "serve" with a plural subject and "cooks" with a singular one.'),
    p([
      ok('The library lends books for free.'),
      ['The shelves holds thousands of titles.', 'The shelves hold thousands of titles.'],
      ok('Readers browse in the quiet room.'),
      ['A single lamp light the reading desk.', 'A single lamp lights the reading desk.'],
      ok('The library closes at six.'),
    ], 'Agreement: "shelves hold" but "lamp lights".'),
    p([
      ok('The team trains twice a week.'),
      ['The players runs around the track.', 'The players run around the track.'],
      ok('The coach blows the whistle.'),
      ['A new member join every month.', 'A new member joins every month.'],
      ok('The team improves each season.'),
    ], 'Use "players run" and "member joins".'),
    p([
      ok('The garden blooms in late spring.'),
      ['The roses opens before the tulips.', 'The roses open before the tulips.'],
      ok('Bees visit the flowers daily.'),
      ['A robin sings from the fence.', 'A robin sings from the fence.'],
      ok('The whole garden feels alive.'),
    ], 'Use "roses open" with the plural subject.'),
  ],

  // 9.2 Agreement with intervening phrases
  '9.2': [
    p([
      ok('The kitchen was busy that morning.'),
      ['The box of apples are on the table.', 'The box of apples is on the table.'],
      ok('The recipe card sits beside it.'),
      ['A bowl of onions wait to be chopped.', 'A bowl of onions waits to be chopped.'],
      ok('The cook works quickly.'),
    ], 'The verb agrees with the head noun ("box", "bowl"), not the phrase after "of".'),
    p([
      ok('The office prepared for the audit.'),
      ['The manager, along with the staff, are ready.', 'The manager, along with the staff, is ready.'],
      ok('The files are neatly arranged.'),
      ['A folder of receipts sit on the desk.', 'A folder of receipts sits on the desk.'],
      ok('Everything is in order.'),
    ], 'Ignore the interrupting phrase: "the manager ... is", "a folder ... sits".'),
    p([
      ok('The choir gave a fine performance.'),
      ['The group of singers were in good voice.', 'The group of singers was in good voice.'],
      ok('The audience applauded warmly.'),
      ['A pair of soloists shine in the second half.', 'A pair of soloists shines in the second half.'],
      ok('The concert ended on a high note.'),
    ], 'The subject is "group"/"pair", so use "was" and "shines".'),
    p([
      ok('The team travelled by coach.'),
      ['The captain, as well as the players, were cheerful.', 'The captain, as well as the players, was cheerful.'],
      ok('They sang songs for the whole trip.'),
      ['A crowd of fans wait at the stadium.', 'A crowd of fans waits at the stadium.'],
      ok('The match began in bright sunshine.'),
    ], 'Use the head noun: "the captain ... was", "a crowd ... waits".'),
    p([
      ok('The museum opened a new wing.'),
      ['The collection of paintings draw large crowds.', 'The collection of paintings draws large crowds.'],
      ok('Visitors queue at the entrance.'),
      ['The curator, together with the team, are delighted.', 'The curator, together with the team, is delighted.'],
      ok('The new wing is a great success.'),
    ], 'Agreement follows "collection" and "curator": "draws", "is".'),
  ],

  // 9.3 Agreement with compound and collective subjects
  '9.3': [
    p([
      ok('The class planned a group project.'),
      ['Both the teacher and the pupils was excited.', 'Both the teacher and the pupils were excited.'],
      ok('They divided the work fairly.'),
      ['The news about the topic are surprising.', 'The news about the topic is surprising.'],
      ok('The project took two weeks.'),
    ], 'A compound subject takes "were"; "news" is singular, so "is".'),
    p([
      ok('The family runs a small farm.'),
      ['The family are gathering the harvest today.', 'The family is gathering the harvest today.'],
      ok('Everyone works from dawn.'),
      ['Neither the dogs nor the cat were inside.', 'Neither the dogs nor the cat was inside.'],
      ok('The farm is always busy.'),
    ], 'Treat "family" as one unit here: "is gathering"; with "nor", the nearer subject controls: "cat was".'),
    p([
      ok('The club meets on Thursdays.'),
      ['Either the coach or the players is responsible.', 'Either the coach or the players are responsible.'],
      ok('They review the rules each week.'),
      ['Mathematics are my favourite subject.', 'Mathematics is my favourite subject.'],
      ok('The club has many members.'),
    ], 'With "either... or", the nearer subject controls: "players are"; "mathematics" is singular.'),
    p([
      ok('The company opened a new branch.'),
      ['Both the manager and the staff has moved.', 'Both the manager and the staff have moved.'],
      ok('The building is bright and modern.'),
      ['The team has finished their training.', 'The team has finished its training.'],
      ok('The branch opens next week.'),
    ], 'Use "have moved" for the compound subject and "its" for the collective noun.'),
    p([
      ok('The village prepares for the festival.'),
      ['The committee have made its decision.', 'The committee has made its decision.'],
      ok('Decorations appear on every street.'),
      ['Neither the mayor nor the villagers was absent.', 'Neither the mayor nor the villagers were absent.'],
      ok('The festival lasts three days.'),
    ], 'Use "committee has" and, with "nor", match the nearer subject "villagers were".'),
  ],

  // 9.4 Pronoun-antecedent agreement
  '9.4': [
    p([
      ok('The company updated its website.'),
      ['The company has changed their logo.', 'The company has changed its logo.'],
      ok('Customers noticed the new look at once.'),
      ['Each department printed their own leaflets.', 'Each department printed its own leaflets.'],
      ok('The new brand looks modern.'),
    ], 'A singular noun like "company" or "each department" takes "its".'),
    p([
      ok('The dog guarded the gate.'),
      ['Every dog wagged their tail.', 'Every dog wagged its tail.'],
      ok('The postman arrived at noon.'),
      ['Someone left their bag by the door.', 'Someone left his bag by the door.'],
      ok('The gate stayed closed.'),
    ], 'Singular antecedents ("every dog", "someone") take singular pronouns.'),
    p([
      ok('The students finished the project.'),
      ['Each pupil chose their topic carefully.', 'Each pupil chose a topic carefully.'],
      ok('They presented the work on Friday.'),
      ['Neither girl had brought their notes.', 'Neither girl had brought her notes.'],
      ok('The teacher praised the effort.'),
    ], '"Each" and "neither" are singular: "her notes".'),
    p([
      ok('The choir prepared for the concert.'),
      ['Every singer tuned their voice.', 'Every singer tuned his voice.'],
      ok('The hall filled with sound.'),
      ['The audience clapped their hands.', 'The audience clapped their hands.'],
      ok('The concert was a triumph.'),
    ], 'With "every singer" use a singular possessive; "the audience" may take "their".'),
    p([
      ok('The business grew very quickly.'),
      ['The firm rewarded their best staff.', 'The firm rewarded its best staff.'],
      ok('Morale improved at once.'),
      ['Each team shared their ideas.', 'Each team shared its ideas.'],
      ok('The company opened a second office.'),
    ], 'Use "its" with the singular "firm" and "each team".'),
  ],

  // 9.5 Run-on sentences and comma splices
  '9.5': [
    p([
      ok('The sky turned grey by noon.'),
      ['It was raining, we stayed inside.', 'It was raining, so we stayed inside.'],
      ok('We played board games all afternoon.'),
      ['The rain stopped, we went outside at once.', 'The rain stopped, and we went outside at once.'],
      ok('The evening was calm and clear.'),
    ], 'Join two clauses with a conjunction: "so", "and".'),
    p([
      ok('My brother studies every evening.'),
      ['He works hard he wants good marks.', 'He works hard because he wants good marks.'],
      ok('His effort shows in his results.'),
      ['The exam is near, he revises daily.', 'The exam is near, so he revises daily.'],
      ok('He feels ready for it.'),
    ], 'A comma splice needs a conjunction: "because", "so".'),
    p([
      ok('The team gathered for the match.'),
      ['They warmed up, the coach gave a talk.', 'They warmed up, and the coach gave a talk.'],
      ok('The whistle blew at three.'),
      ['The play was quick, it was exciting too.', 'The play was quick, and it was exciting too.'],
      ok('The team won by two goals.'),
    ], 'Use "and" to join the clauses instead of a bare comma.'),
    p([
      ok('The hikers set out at dawn.'),
      ['The path was steep, they kept climbing.', 'The path was steep, but they kept climbing.'],
      ok('The view from the top was stunning.'),
      ['They rested a while, they ate their lunch.', 'They rested a while and ate their lunch.'],
      ok('They were home by dusk.'),
    ], 'Use "but" or drop the second subject: "rested and ate".'),
    p([
      ok('The village held its summer fair.'),
      ['The stalls opened, a band played on the green.', 'The stalls opened, and a band played on the green.'],
      ok('Children queued for ice cream.'),
      ['It grew dark, the lanterns were lit.', 'When it grew dark, the lanterns were lit.'],
      ok('The fair ended with fireworks.'),
    ], 'Join the clauses with "and" or a subordinator like "when".'),
  ],

  // 9.6 Sentence fragments
  '9.6': [
    p([
      ok('We waited at the bus stop.'),
      ['Because the bus was late.', 'Because the bus was late, we arrived tired.'],
      ok('The journey took an hour.'),
      ['Although the roads were clear.', 'Although the roads were clear, the trip felt long.'],
      ok('We were glad to reach home.'),
    ], 'A subordinate clause needs a main clause: "Because ... we ...".'),
    p([
      ok('The class prepared for the trip.'),
      ['Which was arranged by the teacher.', 'The trip, which was arranged by the teacher, took place on Friday.'],
      ok('Everyone brought a packed lunch.'),
      ['Even though it was raining heavily.', 'Even though it was raining heavily, we set off on time.'],
      ok('The day was a great success.'),
    ], 'Fragments beginning with "which" or "even though" must join a main clause.'),
    p([
      ok('The puppy explored the garden.'),
      ['Running through the flower beds.', 'It ran through the flower beds.'],
      ok('Its paws were covered in mud.'),
      ['Barking at the birds in the trees.', 'It barked at the birds in the trees.'],
      ok('The garden was a mess afterwards.'),
    ], 'A bare -ing phrase is a fragment; give it a subject and a verb.'),
    p([
      ok('The shop closed at six.'),
      ['The one on the corner.', 'The one on the corner closed early.'],
      ok('A note hung on the door.'),
      ['A quiet little place with old shelves.', 'It was a quiet little place with old shelves.'],
      ok('We agreed to return tomorrow.'),
    ], 'A noun phrase alone is a fragment; add a verb.'),
    p([
      ok('The team lost the final.'),
      ['Despite playing very well.', 'Despite playing very well, they lost the final.'],
      ok('They shook hands with the winners.'),
      ['And promised to return next year.', 'They promised to return next year.'],
      ok('The season ended with pride.'),
    ], 'Attach the phrase to a main clause: "Despite ... they lost".'),
  ],

  // 9.7 Dangling modifiers
  '9.7': [
    p([
      ok('I walked home through the park.'),
      ['Walking home, the rain started.', 'Walking home, I felt the rain start.'],
      ok('I hurried along the path.'),
      ['Having no umbrella, my coat got soaked.', 'Having no umbrella, I got my coat soaked.'],
      ok('I was glad to reach the door.'),
    ], 'The opening phrase must describe the subject: "walking home, I ...".'),
    p([
      ok('The chef prepared the evening meal.'),
      ['Cooked slowly, the chef tasted the sauce.', 'Cooked slowly, the sauce tasted rich.'],
      ok('The guests arrived at eight.'),
      ['Being very hungry, the soup smelled wonderful.', 'Being very hungry, we thought the soup smelled wonderful.'],
      ok('Everyone enjoyed the dinner.'),
    ], 'The modifier must describe the right subject: "the sauce tasted rich".'),
    p([
      ok('The team trained on the field.'),
      ['After training hard, the match was won.', 'After training hard, the team won the match.'],
      ok('The fans cheered them loudly.'),
      ['Exhausted but happy, the trophy was lifted.', 'Exhausted but happy, the players lifted the trophy.'],
      ok('It was a proud day for the club.'),
    ], 'Tie the phrase to the doer: "the team won", "the players lifted".'),
    p([
      ok('The students wrote their essays.'),
      ['Having finished the essay, the printer jammed.', 'Having finished the essay, the pupils printed it.'],
      ok('They handed the work in on time.'),
      ['Writing quickly, some mistakes were made.', 'Writing quickly, they made some mistakes.'],
      ok('The teacher marked the essays fairly.'),
    ], 'The -ing phrase describes the pupils, not the printer or mistakes.'),
    p([
      ok('The scientists studied the ice.'),
      ['Having collected the samples, the results were analysed.', 'Having collected the samples, the scientists analysed the results.'],
      ok('The findings were published in June.'),
      ['Working late, the report was finished.', 'Working late, the team finished the report.'],
      ok('The study made the news.'),
    ], 'The opening phrase must share its subject with the main clause.'),
  ],

  // 9.8 Misplaced modifiers
  '9.8': [
    p([
      ok('The host welcomed everyone warmly.'),
      ['She served sandwiches to the guests on paper plates.', 'She served sandwiches on paper plates to the guests.'],
      ok('The food was fresh and tasty.'),
      ['She poured tea into the cups with a smile.', 'With a smile, she poured tea into the cups.'],
      ok('The party went on all evening.'),
    ], 'Place the modifier next to what it describes: "on paper plates" belongs with "sandwiches".'),
    p([
      ok('The gardener tidied the whole yard.'),
      ['She cut the hedge that was overgrown with sharp shears.', 'With sharp shears, she cut the overgrown hedge.'],
      ok('The lawn looked neat afterwards.'),
      ['She planted roses in the corner that smelled lovely.', 'She planted lovely roses in the corner that smelled nice.'],
      ok('The garden won a prize.'),
    ], 'Keep the modifier close to the word it modifies.'),
    p([
      ok('The teacher praised the class.'),
      ['She returned the essays to the pupils with red ink.', 'She returned the essays with red ink to the pupils.'],
      ok('The marks were very good.'),
      ['She gave a talk about grammar at the front that was useful.', 'At the front, she gave a useful talk about grammar.'],
      ok('The lesson ended with a smile.'),
    ], 'Put the modifying phrase next to the noun it belongs to.'),
    p([
      ok('The mechanic repaired the car.'),
      ['He replaced the brake pads that were worn on the van.', 'He replaced the worn brake pads on the van.'],
      ok('The van ran smoothly afterwards.'),
      ['He found a problem with the engine inside the garage.', 'Inside the garage, he found a problem with the engine.'],
      ok('The owner was pleased.'),
    ], 'Place "worn" before "brake pads" and the location phrase at the start.'),
    p([
      ok('The choir sang at the concert.'),
      ['They performed the songs that were new beautifully.', 'They performed the new songs beautifully.'],
      ok('The audience listened in silence.'),
      ['The conductor raised his arms at the front with great energy.', 'The conductor raised his arms with great energy.'],
      ok('The concert ended to loud applause.'),
    ], 'Keep descriptive words next to the nouns they modify.'),
  ],

  // 9.9 Parallel structure
  '9.9': [
    p([
      ok('She has many hobbies.'),
      ['She likes swimming, running and to ride a bike.', 'She likes swimming, running and riding a bike.'],
      ok('She spends her weekends outdoors.'),
      ['Her goals are to stay fit, to have fun and making friends.', 'Her goals are to stay fit, to have fun and to make friends.'],
      ok('She is always cheerful.'),
    ], 'Keep items in a list in the same form: all gerunds or all infinitives.'),
    p([
      ok('The job requires several skills.'),
      ['It needs patience, care and being reliable.', 'It needs patience, care and reliability.'],
      ok('The employer explained the role.'),
      ['The duties are answering calls, filing papers and to greet guests.', 'The duties are answering calls, filing papers and greeting guests.'],
      ok('Many people applied for it.'),
    ], 'Keep list items parallel: nouns with nouns, gerunds with gerunds.'),
    p([
      ok('The town built a new leisure centre.'),
      ['The centre offers swimming, fitness and to join classes.', 'The centre offers swimming, fitness and classes.'],
      ok('The opening drew large crowds.'),
      ['Members can train, relax or taking a sauna.', 'Members can train, relax or take a sauna.'],
      ok('The centre is open daily.'),
    ], 'Keep the coordinated items in the same grammatical form.'),
    p([
      ok('The pupils wrote a report on the trip.'),
      ['The trip was long, tiring but we enjoyed it.', 'The trip was long and tiring but enjoyable.'],
      ok('They described the mountain views.'),
      ['They saw rivers, forests and some was climbing.', 'They saw rivers, forests and mountains.'],
      ok('The report earned high marks.'),
    ], 'Make coordinated adjectives and nouns consistent in form.'),
    p([
      ok('The manager explained the plan.'),
      ['The plan is simple, clear and it can be done.', 'The plan is simple, clear and practical.'],
      ok('The staff agreed with it.'),
      ['They will plan, prepare and are going to start soon.', 'They will plan, prepare and start soon.'],
      ok('The work begins on Monday.'),
    ], 'Keep coordinated verbs and adjectives parallel.'),
  ],

  // 9.10 Faulty coordination
  '9.10': [
    p([
      ok('The race was long and hard.'),
      ['He was tired, and he finished the race.', 'He was tired, but he finished the race.'],
      ok('The crowd cheered him home.'),
      ['The course was tough, and the runners enjoyed it.', 'The course was tough, but the runners enjoyed it.'],
      ok('He was proud of his time.'),
    ], 'Use "but" for contrast, "and" for addition.'),
    p([
      ok('The café serves light meals.'),
      ['The food was cheap, and the service was excellent.', 'The food was cheap, and the service was excellent.'],
      ok('It fills up at lunchtime.'),
      ['The queue was long, and the wait was short.', 'The queue was long, but the wait was short.'],
      ok('We will go back soon.'),
    ], 'Choose the conjunction that matches the meaning.'),
    p([
      ok('The team prepared carefully.'),
      ['They practised hard, and they lost the match.', 'They practised hard, but they lost the match.'],
      ok('The coach praised their effort.'),
      ['The defeat was painful, and it taught them a lot.', 'The defeat was painful, but it taught them a lot.'],
      ok('They trained harder the next week.'),
    ], 'Use "but" to signal contrast.'),
    p([
      ok('The book was very long.'),
      ['It was heavy, and it was easy to read.', 'It was heavy, but it was easy to read.'],
      ok('I finished it in a week.'),
      ['The story was simple, and the ending surprised me.', 'The story was simple, but the ending surprised me.'],
      ok('I lent it to a friend.'),
    ], 'Contrast needs "but", not "and".'),
    p([
      ok('The journey took most of the day.'),
      ['The road was busy, and we arrived on time.', 'The road was busy, but we arrived on time.'],
      ok('We found a place to park.'),
      ['The weather was poor, and the trip was enjoyable.', 'The weather was poor, but the trip was enjoyable.'],
      ok('We would do it again.'),
    ], 'Use "but" when the second clause contrasts with the first.'),
  ],

  // 9.11 Faulty subordination
  '9.11': [
    p([
      ok('She was very tired.'),
      ['Although it was late, but she kept working.', 'Although it was late, she kept working.'],
      ok('She wanted to finish the report.'),
      ['Because she was busy, so she missed dinner.', 'Because she was busy, she missed dinner.'],
      ok('She went to bed at midnight.'),
    ], 'Do not pair "although ... but" or "because ... so".'),
    p([
      ok('The children were excited.'),
      ['Since it was raining, so they stayed inside.', 'Since it was raining, they stayed inside.'],
      ok('They built a den with cushions.'),
      ['Even though they were indoors, but they had fun.', 'Even though they were indoors, they had fun.'],
      ok('The afternoon passed quickly.'),
    ], 'Use one subordinator only: "since ... they", "even though ... they".'),
    p([
      ok('The bus was crowded.'),
      ['Although the seats were full, but we stood near the door.', 'Although the seats were full, we stood near the door.'],
      ok('The journey was short.'),
      ['Because the traffic was light, so we arrived early.', 'Because the traffic was light, we arrived early.'],
      ok('We caught the next bus home.'),
    ], 'Avoid the double connector "although ... but" and "because ... so".'),
    p([
      ok('The exam was difficult.'),
      ['Even though she had studied, but she felt nervous.', 'Even though she had studied, she felt nervous.'],
      ok('She read each question twice.'),
      ['As the clock ticked, so she worked faster.', 'As the clock ticked, she worked faster.'],
      ok('She passed with a good mark.'),
    ], 'Use a single subordinating conjunction.'),
    p([
      ok('The garden was overgrown.'),
      ['Although nobody had time, but the neighbours helped.', 'Although nobody had time, the neighbours helped.'],
      ok('They cleared it in a weekend.'),
      ['Since the weather was fine, so they worked outside.', 'Since the weather was fine, they worked outside.'],
      ok('The garden looked lovely again.'),
    ], 'Drop the extra "but"/"so" after a subordinator.'),
  ],

  // 9.12 Relative clause errors
  '9.12': [
    p([
      ok('The man called the police.'),
      ['The man who he called was very helpful.', 'The man who called was very helpful.'],
      ok('The officer arrived quickly.'),
      ['The book which I read it was thrilling.', 'The book which I read was thrilling.'],
      ok('I recommend it to everyone.'),
    ], 'A relative pronoun already replaces the object; do not repeat it.'),
    p([
      ok('The teacher marked the tests.'),
      ['The pupil whom she praised him was pleased.', 'The pupil whom she praised was pleased.'],
      ok('The class worked quietly.'),
      ['The film that we watched it last night was long.', 'The film that we watched last night was long.'],
      ok('We discussed it this morning.'),
    ], 'Do not add an extra pronoun after the relative clause.'),
    p([
      ok('The house stood on a hill.'),
      ['The family who they live there are friendly.', 'The family who live there are friendly.'],
      ok('They invited us for tea.'),
      ['The garden that surrounds it is beautiful.', 'The garden that surrounds it is beautiful.'],
      ok('We walked up the hill slowly.'),
    ], 'Use the relative pronoun once: "who live there".'),
    p([
      ok('The shop sells fresh bread.'),
      ['The baker which owns it starts before dawn.', 'The baker who owns it starts before dawn.'],
      ok('The loaves sell out early.'),
      ['The queue that forms it reaches the corner.', 'The queue that forms reaches the corner.'],
      ok('Customers come from far away.'),
    ], 'Use "who" for people and drop the repeated pronoun.'),
    p([
      ok('The town has an old bridge.'),
      ['The tourists who they visit it love the view.', 'The tourists who visit love the view.'],
      ok('The bridge crosses a wide river.'),
      ['The café which it stands nearby is popular.', 'The café which stands nearby is popular.'],
      ok('We took many photos.'),
    ], 'Do not repeat the subject inside the relative clause.'),
  ],

  // 9.13 Word order
  '9.13': [
    p([
      ok('The shop opens at nine.'),
      ['Always she arrives late.', 'She always arrives late.'],
      ok('The manager has noticed.'),
      ['Never she has been on time.', 'She has never been on time.'],
      ok('The manager decided to talk to her.'),
    ], 'Frequency adverbs go before the main verb: "always arrives", "never been".'),
    p([
      ok('The train left the platform.'),
      ['Rarely the train is late.', 'The train is rarely late.'],
      ok('Commuters rely on it.'),
      ['Seldom it stops at this station.', 'It seldom stops at this station.'],
      ok('The service is reliable.'),
    ], 'Place "rarely" and "seldom" after the subject (or before the verb).'),
    p([
      ok('The choir practised for weeks.'),
      ['Beautifully they sang the final song.', 'They sang the final song beautifully.'],
      ok('The audience clapped loudly.'),
      ['Yesterday we went to the concert.', 'Yesterday we went to the concert.'],
      ok('It was a memorable evening.'),
    ], 'Adverbs of manner follow the verb; sentence adverbs may start the clause.'),
    p([
      ok('The team scored early.'),
      ['Quickly they finished the match.', 'They finished the match quickly.'],
      ok('The crowd went wild.'),
      ['Slowly the players left the field.', 'The players left the field slowly.'],
      ok('It was a great win.'),
    ], 'Keep manner adverbs after the verb or object.'),
    p([
      ok('The pupils finished the test.'),
      ['Carefully she read each question.', 'She read each question carefully.'],
      ok('The clock ticked loudly.'),
      ['Nervously some pupils checked the time.', 'Some pupils nervously checked the time.'],
      ok('The bell rang at last.'),
    ], 'Place the adverb with the verb it modifies.'),
  ],

  // 9.14 There is / there are
  '9.14': [
    p([
      ok('There are many shops on this street.'),
      ['There is many reasons to visit the town.', 'There are many reasons to visit the town.'],
      ok('The market is always busy.'),
      ['There was two cakes left on the plate.', 'There were two cakes left on the plate.'],
      ok('We bought one straight away.'),
    ], 'Use "there are/were" with plural nouns, "there is/was" with singular.'),
    p([
      ok('There is a park near the river.'),
      ['There are a new bridge over the water.', 'There is a new bridge over the water.'],
      ok('It opened last spring.'),
      ['There were a crowd gathered to watch.', 'There was a crowd gathered to watch.'],
      ok('The ceremony was short and cheerful.'),
    ], 'Use "there is/was" for singular nouns like "bridge" and "crowd".'),
    p([
      ok('There are three schools in the village.'),
      ['There is several clubs after school.', 'There are several clubs after school.'],
      ok('The children enjoy them all.'),
      ['There was many parents at the meeting.', 'There were many parents at the meeting.'],
      ok('The meeting lasted an hour.'),
    ], 'Plural subjects need "there are/were".'),
    p([
      ok('There is a lot to see in the city.'),
      ['There are a museum beside the station.', 'There is a museum beside the station.'],
      ok('It holds a famous collection.'),
      ['There were an exhibition last month.', 'There was an exhibition last month.'],
      ok('It attracted many visitors.'),
    ], 'Match "there is/was" to the singular nouns "museum" and "exhibition".'),
    p([
      ok('There is plenty of food in the fridge.'),
      ['There are a bottle of milk on the shelf.', 'There is a bottle of milk on the shelf.'],
      ok('We will not go hungry.'),
      ['There was several apples in the bowl.', 'There were several apples in the bowl.'],
      ok('The kitchen is well stocked.'),
    ], 'Use "there is" for "a bottle" and "there were" for "several apples".'),
  ],

  // 9.15 Question tags
  '9.15': [
    p([
      ok('You are coming to the party.'),
      ['You are coming, isn\'t it?', 'You are coming, aren\'t you?'],
      ok('It starts at eight.'),
      ['She can swim well, doesn\'t she?', 'She can swim well, can\'t she?'],
      ok('We will meet at the door.'),
    ], 'Match the tag to the auxiliary: "aren\'t you?", "can\'t she?".'),
    p([
      ok('The film was very long.'),
      ['It was boring, isn\'t it?', 'It was boring, wasn\'t it?'],
      ok('We left before the end.'),
      ['They had left already, didn\'t they?', 'They had left already, hadn\'t they?'],
      ok('We caught the last bus.'),
    ], 'Keep the tag tense the same as the main clause: "wasn\'t it?", "hadn\'t they?".'),
    p([
      ok('The team played well.'),
      ['They won the match, did they?', 'They won the match, didn\'t they?'],
      ok('The crowd cheered loudly.'),
      ['They will play again, will they?', 'They will play again, won\'t they?'],
      ok('The final is next week.'),
    ], 'A positive statement takes a negative tag.'),
    p([
      ok('The café is always busy.'),
      ['You don\'t like coffee, don\'t you?', 'You don\'t like coffee, do you?'],
      ok('They serve excellent tea.'),
      ['She isn\'t coming, isn\'t she?', 'She isn\'t coming, is she?'],
      ok('We will wait a little longer.'),
    ], 'A negative statement takes a positive tag.'),
    p([
      ok('The children have finished their homework.'),
      ['They have eaten, have they?', 'They have eaten, haven\'t they?'],
      ok('They can go out to play.'),
      ['You will join us, will you?', 'You will join us, won\'t you?'],
      ok('The evening is still young.'),
    ], 'Match the auxiliary in the tag to the one in the statement.'),
  ],

  // =========================================================================
  // Section 10 — Punctuation
  // =========================================================================

  // 10.1 End punctuation and sentence boundaries
  '10.1': [
    p([
      ok('The visitors arrived at the museum.'),
      ['Where are you going', 'Where are you going?'],
      ok('The guard pointed to the main hall.'),
      ['What time does it close', 'What time does it close?'],
      ok('The doors shut at six.'),
    ], 'A direct question ends with a question mark.'),
    p([
      ok('She looked out of the window.'),
      ['The rain had stopped', 'The rain had stopped.'],
      ok('A rainbow stretched across the sky.'),
      ['How beautiful it was', 'How beautiful it was!'],
      ok('She called her brother to see.'),
    ], 'Every sentence needs end punctuation: a full stop or an exclamation mark.'),
    p([
      ok('The pupils lined up for the bus.'),
      ['did you bring your lunch', 'Did you bring your lunch?'],
      ok('The teacher checked the list.'),
      ['the bus is late again', 'The bus is late again.'],
      ok('It finally arrived at nine.'),
    ], 'Sentences start with a capital letter and end with a full stop or question mark.'),
    p([
      ok('The recipe looked simple enough.'),
      ['What could go wrong', 'What could go wrong?'],
      ok('He gathered all the ingredients.'),
      ['the oven was still cold', 'The oven was still cold.'],
      ok('He turned it on and waited.'),
    ], 'Add a capital at the start and a question mark for questions.'),
    p([
      ok('The hikers reached the summit.'),
      ['how far is the village', 'How far is the village?'],
      ok('They checked their map.'),
      ['it is still five miles away', 'It is still five miles away.'],
      ok('They set off down the path.'),
    ], 'Use a capital letter and the correct end mark.'),
  ],

  // 10.2 Commas in lists
  '10.2': [
    p([
      ok('We went shopping for the party.'),
      ['We bought apples oranges and pears.', 'We bought apples, oranges and pears.'],
      ok('The bags were heavy.'),
      ['We also needed plates cups and napkins.', 'We also needed plates, cups and napkins.'],
      ok('The car was full by the time we left.'),
    ], 'Separate items in a list with commas.'),
    p([
      ok('The team packed for the trip.'),
      ['They took boots gloves and hats.', 'They took boots, gloves and hats.'],
      ok('The forecast promised cold weather.'),
      ['They added snacks water and a map.', 'They added snacks, water and a map.'],
      ok('Their rucksacks were ready.'),
    ], 'Use commas between the items of a list.'),
    p([
      ok('The garden needed several jobs done.'),
      ['She mowed trimmed and watered the lawn.', 'She mowed, trimmed and watered the lawn.'],
      ok('The flower beds looked neat.'),
      ['She planted roses tulips and daisies.', 'She planted roses, tulips and daisies.'],
      ok('The garden was lovely by evening.'),
    ], 'Separate the listed verbs and nouns with commas.'),
    p([
      ok('The class prepared a display.'),
      ['They painted drew and printed their work.', 'They painted, drew and printed their work.'],
      ok('The wall looked colourful.'),
      ['They added photos posters and charts.', 'They added photos, posters and charts.'],
      ok('The display won a school prize.'),
    ], 'Use commas to separate items in a list.'),
    p([
      ok('The kitchen smelled wonderful.'),
      ['She chopped onions garlic and carrots.', 'She chopped onions, garlic and carrots.'],
      ok('The soup simmered on the stove.'),
      ['She added salt pepper and herbs.', 'She added salt, pepper and herbs.'],
      ok('Dinner was ready by six.'),
    ], 'Commas separate the listed ingredients.'),
  ],

  // 10.3 Commas after introductory phrases
  '10.3': [
    p([
      ok('The family set off early.'),
      ['After the long journey we were tired.', 'After the long journey, we were tired.'],
      ok('The hotel was warm and welcoming.'),
      ['In the morning we explored the town.', 'In the morning, we explored the town.'],
      ok('The holiday began well.'),
    ], 'Use a comma after an introductory phrase.'),
    p([
      ok('The pupils worked quietly.'),
      ['When the bell rang they packed away.', 'When the bell rang, they packed away.'],
      ok('The teacher dismissed the class.'),
      ['Before lunch they finished the exercise.', 'Before lunch, they finished the exercise.'],
      ok('The afternoon lesson began at one.'),
    ], 'A comma follows an introductory clause.'),
    p([
      ok('The train pulled out of the station.'),
      ['As the sun rose the mist cleared.', 'As the sun rose, the mist cleared.'],
      ok('The countryside looked fresh.'),
      ['Along the river we saw herons.', 'Along the river, we saw herons.'],
      ok('The journey passed pleasantly.'),
    ], 'Set off the opening clause with a comma.'),
    p([
      ok('The choir gathered on the stage.'),
      ['After a short break they sang again.', 'After a short break, they sang again.'],
      ok('The audience listened in silence.'),
      ['In the second half the tempo quickened.', 'In the second half, the tempo quickened.'],
      ok('The concert ended to applause.'),
    ], 'Use a comma after the introductory phrase.'),
    p([
      ok('The gardener started early.'),
      ['Before the rain came she finished planting.', 'Before the rain came, she finished planting.'],
      ok('The soil was soft and dark.'),
      ['By noon the whole bed was done.', 'By noon, the whole bed was done.'],
      ok('The garden looked full of promise.'),
    ], 'Introductory phrases are followed by a comma.'),
  ],

  // 10.4 Commas with non-restrictive clauses
  '10.4': [
    p([
      ok('My father works at the hospital.'),
      ['My father who is a doctor loves golf.', 'My father, who is a doctor, loves golf.'],
      ok('He plays every Sunday.'),
      ['His friend who works with him joins too.', 'His friend, who works with him, joins too.'],
      ok('They enjoy the fresh air.'),
    ], 'A non-restrictive relative clause (extra information) is set off with commas.'),
    p([
      ok('The town has an old castle.'),
      ['The castle which is on a hill attracts tourists.', 'The castle, which is on a hill, attracts tourists.'],
      ok('It was built centuries ago.'),
      ['The tower which is the tallest part offers a view.', 'The tower, which is the tallest part, offers a view.'],
      ok('Visitors climb it on sunny days.'),
    ], 'Set off the non-essential clause with commas.'),
    p([
      ok('Our neighbour owns a small boat.'),
      ['His boat which he keeps at the harbour needs repairs.', 'His boat, which he keeps at the harbour, needs repairs.'],
      ok('He sails it most weekends.'),
      ['His son who is ten loves the sea.', 'His son, who is ten, loves the sea.'],
      ok('They often sail together.'),
    ], 'Extra information is separated by commas.'),
    p([
      ok('The café on the corner is popular.'),
      ['The owner who moved here last year serves great cakes.', 'The owner, who moved here last year, serves great cakes.'],
      ok('The queue is often long.'),
      ['The tables which are outside fill up first.', 'The tables, which are outside, fill up first.'],
      ok('It is worth the wait.'),
    ], 'A non-defining clause goes between commas.'),
    p([
      ok('The book became a bestseller.'),
      ['The author who lives in this city wrote it quickly.', 'The author, who lives in this city, wrote it quickly.'],
      ok('She gave a talk at the library.'),
      ['The sequel which she is writing comes out next year.', 'The sequel, which she is writing, comes out next year.'],
      ok('Fans are eagerly waiting.'),
    ], 'Set off the extra information with commas.'),
  ],

  // 10.5 Possessive apostrophes
  '10.5': [
    p([
      ok('The dog ran across the field.'),
      ['The dogs bone was buried in the garden.', 'The dog\'s bone was buried in the garden.'],
      ok('He dug it up again at once.'),
      ['The childrens toys lay scattered on the grass.', 'The children\'s toys lay scattered on the grass.'],
      ok('The garden was a cheerful mess.'),
    ], 'Use an apostrophe for possession: "the dog\'s bone", "the children\'s toys".'),
    p([
      ok('The pupils handed in their work.'),
      ['The teachers desk was covered in papers.', 'The teacher\'s desk was covered in papers.'],
      ok('She marked the books at home.'),
      ['The pupils answers were mostly correct.', 'The pupils\' answers were mostly correct.'],
      ok('The class did very well.'),
    ], 'Singular "teacher\'s" and plural "pupils\'" both take an apostrophe.'),
    p([
      ok('My sister borrowed my bike.'),
      ['My sisters helmet was left at home.', 'My sister\'s helmet was left at home.'],
      ok('She had to walk back for it.'),
      ['The boys bags were by the door.', 'The boys\' bags were by the door.'],
      ok('They set off later than planned.'),
    ], 'Use "sister\'s" for one owner and "boys\'" for many.'),
    p([
      ok('The team celebrated the win.'),
      ['The captains speech was short and cheerful.', 'The captain\'s speech was short and cheerful.'],
      ok('The players cheered loudly.'),
      ['The womens match was played first.', 'The women\'s match was played first.'],
      ok('Both teams played well.'),
    ], 'Note the apostrophe in "captain\'s" and the irregular "women\'s".'),
    p([
      ok('The company held its annual picnic.'),
      ['The firms staff gathered in the park.', 'The firm\'s staff gathered in the park.'],
      ok('There were games for everyone.'),
      ['The managers speech ended the day.', 'The manager\'s speech ended the day.'],
      ok('Everyone went home happy.'),
    ], 'Use "firm\'s" and "manager\'s" for possession.'),
  ],

  // 10.6 Apostrophes in contractions and its/it's
  '10.6': [
    p([
      ok('The cat slept on the sofa.'),
      ['The cat licked it\'s paw.', 'The cat licked its paw.'],
      ok('It looked very content.'),
      ['Its raining outside now.', 'It\'s raining outside now.'],
      ok('The cat moved to a warmer spot.'),
    ], '"Its" shows possession; "it\'s" means "it is".'),
    p([
      ok('The robot needed a new battery.'),
      ['The machine lost it\'s power.', 'The machine lost its power.'],
      ok('The technician opened the panel.'),
      ['Its going to take an hour to fix.', 'It\'s going to take an hour to fix.'],
      ok('The robot was soon working again.'),
    ], 'Use "its" for possession and "it\'s" for "it is".'),
    p([
      ok('The tree lost all of its leaves.'),
      ['The old oak shed it\'s leaves early.', 'The old oak shed its leaves early.'],
      ok('The branches stood bare.'),
      ['Its a sign that winter is coming.', 'It\'s a sign that winter is coming.'],
      ok('The garden will sleep until spring.'),
    ], '"Its leaves" (possession) versus "It\'s a sign" (it is).'),
    p([
      ok('The school has a new hall.'),
      ['The building had it\'s roof repaired.', 'The building had its roof repaired.'],
      ok('The work took three months.'),
      ['Its much brighter inside now.', 'It\'s much brighter inside now.'],
      ok('The pupils love the new space.'),
    ], 'Use "its roof" for possession and "It\'s" for "it is".'),
    p([
      ok('The puppy chased its own tail.'),
      ['The puppy wagged it\'s tail happily.', 'The puppy wagged its tail happily.'],
      ok('It ran around the garden.'),
      ['Its tired now after all that play.', 'It\'s tired now after all that play.'],
      ok('It curled up for a nap.'),
    ], '"Its tail" (possession) and "It\'s tired" (it is).'),
  ],

  // 10.7 Capitalisation
  '10.7': [
    p([
      ok('The family planned a trip abroad.'),
      ['we visited paris in july.', 'We visited Paris in July.'],
      ok('The city was warm and busy.'),
      ['my sister loved the eiffel tower.', 'My sister loved the Eiffel Tower.'],
      ok('We took hundreds of photos.'),
    ], 'Capitalise the first word, names of places, and months.'),
    p([
      ok('The pupils studied world geography.'),
      ['they learned about the river nile.', 'They learned about the River Nile.'],
      ok('The lesson was fascinating.'),
      ['on monday they studied the alps.', 'On Monday they studied the Alps.'],
      ok('The class asked many questions.'),
    ], 'Capitalise proper nouns, days and specific place names.'),
    p([
      ok('The choir practised a new song.'),
      ['they sang a piece by mozart.', 'They sang a piece by Mozart.'],
      ok('The concert was in december.'),
      ['the choir travelled to london for it.', 'The choir travelled to London for it.'],
      ok('The performance was beautiful.'),
    ], 'Capitalise names of people, months and cities.'),
    p([
      ok('The book club met on friday.'),
      ['they discussed a novel by dickens.', 'They discussed a novel by Dickens.'],
      ok('Everyone had read the first chapter.'),
      ['the next meeting is in october.', 'The next meeting is in October.'],
      ok('They chose a new title to read.'),
    ], 'Capitalise the sentence start, author names and months.'),
    p([
      ok('The tourists crossed the border.'),
      ['they arrived in italy on tuesday.', 'They arrived in Italy on Tuesday.'],
      ok('The weather was perfect for sightseeing.'),
      ['they visited rome and florence.', 'They visited Rome and Florence.'],
      ok('The holiday was unforgettable.'),
    ], 'Capitalise countries, cities and days of the week.'),
  ],

  // 10.8 Quotation marks and dialogue
  '10.8': [
    p([
      ok('The teacher entered the room.'),
      ['"Where are you going" he asked.', '"Where are you going?" he asked.'],
      ok('The pupils pointed to the door.'),
      ['"The bus is leaving now" she said.', '"The bus is leaving now," she said.'],
      ok('Everyone hurried outside.'),
    ], 'Place punctuation inside the quotation marks.'),
    p([
      ok('The coach gathered the players.'),
      ['"Listen carefully" he said.', '"Listen carefully," he said.'],
      ok('The team fell silent.'),
      ['"We will win today" he added.', '"We will win today," he added.'],
      ok('They ran onto the pitch.'),
    ], 'A comma separates speech from the reporting clause.'),
    p([
      ok('The chef greeted the guests.'),
      ['"Dinner is ready" she announced.', '"Dinner is ready," she announced.'],
      ok('The table was beautifully set.'),
      ['"Please take your seats" she added.', '"Please take your seats," she added.'],
      ok('The meal was delicious.'),
    ], 'Put a comma inside the closing quotation mark.'),
    p([
      ok('The librarian helped a reader.'),
      ['"The book is over there" she said.', '"The book is over there," she said.'],
      ok('The reader found it quickly.'),
      ['"It sounds wonderful" he replied.', '"It sounds wonderful," he replied.'],
      ok('He borrowed it at once.'),
    ], 'Set off the spoken words with punctuation inside the quotes.'),
    p([
      ok('The guide met the group.'),
      ['"Follow me please" she said.', '"Follow me, please," she said.'],
      ok('The path led through the woods.'),
      ['"Watch your step here" she warned.', '"Watch your step here," she warned.'],
      ok('They reached the waterfall safely.'),
    ], 'Punctuate the quotation before the reporting clause.'),
  ],

  // 10.9 Semicolons and colons
  '10.9': [
    p([
      ok('The team had a busy week.'),
      ['It was late, however, we continued.', 'It was late; however, we continued.'],
      ok('The work had to be finished.'),
      ['We finished the report, then we went home.', 'We finished the report; then we went home.'],
      ok('Everyone was exhausted but pleased.'),
    ], 'Use a semicolon before a conjunctive adverb or to join related clauses.'),
    p([
      ok('She loves outdoor sports.'),
      ['I have three hobbies swimming, running and reading.', 'I have three hobbies: swimming, running and reading.'],
      ok('Each one keeps her active.'),
      ['She has one aim to run a marathon.', 'She has one aim: to run a marathon.'],
      ok('She trains every morning.'),
    ], 'A colon introduces a list or an explanation.'),
    p([
      ok('The trip required careful planning.'),
      ['We needed three things, tickets, maps and sunscreen.', 'We needed three things: tickets, maps and sunscreen.'],
      ok('The list was pinned to the wall.'),
      ['We packed for everything the weather was uncertain.', 'We packed for everything: the weather was uncertain.'],
      ok('In the end we used everything.'),
    ], 'Use a colon before a list and a semicolon between related clauses.'),
    p([
      ok('The recipe had a short list of ingredients.'),
      ['We needed two things flour and butter.', 'We needed two things: flour and butter.'],
      ok('The rest were already in the cupboard.'),
      ['The dough was ready, we shaped it at once.', 'The dough was ready; we shaped it at once.'],
      ok('The biscuits smelled wonderful.'),
    ], 'A colon introduces the list; a semicolon joins the clauses.'),
    p([
      ok('The manager called a meeting.'),
      ['There was one clear reason the budget.', 'There was one clear reason: the budget.'],
      ok('The team discussed it openly.'),
      ['The figures were clear, we had to save more.', 'The figures were clear; we had to save more.'],
      ok('Everyone agreed on a plan.'),
    ], 'Use a colon for a single explanation and a semicolon for related clauses.'),
  ],

  // 10.10 Hyphens and compound modifiers
  '10.10': [
    p([
      ok('The library held a book signing.'),
      ['A well known author came to speak.', 'A well-known author came to speak.'],
      ok('The room was full of readers.'),
      ['The event lasted for two hours.', 'The event lasted for two hours.'],
      ok('Everyone left with a signed copy.'),
    ], 'Hyphenate a compound modifier before a noun: "well-known author".'),
    p([
      ok('The family adopted a rescue dog.'),
      ['It was a three year old puppy.', 'It was a three-year-old puppy.'],
      ok('The children loved it at once.'),
      ['They built a long lasting friendship.', 'They built a long-lasting friendship.'],
      ok('The dog settled in quickly.'),
    ], 'Hyphenate compound modifiers: "three-year-old", "long-lasting".'),
    p([
      ok('The company launched a new product.'),
      ['It was a state of the art device.', 'It was a state-of-the-art device.'],
      ok('Reviews were very positive.'),
      ['It was a much needed upgrade.', 'It was a much-needed upgrade.'],
      ok('Sales rose sharply.'),
    ], 'Use hyphens in multi-word modifiers: "state-of-the-art", "much-needed".'),
    p([
      ok('The town held a food festival.'),
      ['A family run bakery won first prize.', 'A family-run bakery won first prize.'],
      ok('The judges tasted many entries.'),
      ['The award went to a hand made cake.', 'The award went to a hand-made cake.'],
      ok('The festival was a great success.'),
    ], 'Hyphenate "family-run" and "hand-made" before nouns.'),
    p([
      ok('The school opened a new lab.'),
      ['It was a well equipped science room.', 'It was a well-equipped science room.'],
      ok('The pupils began experiments at once.'),
      ['They used a brand new microscope.', 'They used a brand-new microscope.'],
      ok('The lab quickly became their favourite room.'),
    ], 'Hyphenate compound modifiers: "well-equipped", "brand-new".'),
  ],

  // =========================================================================
  // Section 11 — Meaning and usage
  // =========================================================================

  // 11.1 their / there / they're
  '11.1': [
    p([
      ok('The pupils packed for the school trip.'),
      ['Their going to the museum by coach.', 'They\'re going to the museum by coach.'],
      ok('The coach leaves at nine.'),
      ['The children left there bags by the door.', 'The children left their bags by the door.'],
      ok('The teacher checked the list.'),
    ], '"They\'re" means "they are"; "their" shows possession.'),
    p([
      ok('My cousins moved to a new town.'),
      ['Their house is near the park.', 'Their house is near the park.'],
      ok('They like the neighbourhood.'),
      ['There coming to visit us next month.', 'They\'re coming to visit us next month.'],
      ok('We will meet them at the station.'),
    ], 'Use "They\'re" for "they are" and "their" for possession.'),
    p([
      ok('The students finished the project.'),
      ['There results were excellent.', 'Their results were excellent.'],
      ok('The teacher praised the whole class.'),
      ['Their going to celebrate on Friday.', 'They\'re going to celebrate on Friday.'],
      ok('The party is at the café.'),
    ], '"Their results" (possession) and "They\'re going" (they are).'),
    p([
      ok('The birds built a nest in the tree.'),
      ['There nest is high in the branches.', 'Their nest is high in the branches.'],
      ok('They return to it each spring.'),
      ['Their singing every morning.', 'They\'re singing every morning.'],
      ok('The garden is full of birdsong.'),
    ], 'Use "their nest" (possession) and "They\'re singing" (they are).'),
    p([
      ok('The players trained hard all week.'),
      ['Their ready for the big match.', 'They\'re ready for the big match.'],
      ok('The coach is confident.'),
      ['There fans will fill the stadium.', 'Their fans will fill the stadium.'],
      ok('The atmosphere will be electric.'),
    ], '"They\'re ready" (they are) and "Their fans" (possession).'),
  ],

  // 11.2 to / too / two
  '11.2': [
    p([
      ok('I planned an early start.'),
      ['I wanted too go before sunrise.', 'I wanted to go before sunrise.'],
      ok('The roads would be quiet.'),
      ['There were to many delays.', 'There were too many delays.'],
      ok('I left later than planned.'),
    ], 'Use "to" for the infinitive and "too" for "excessively".'),
    p([
      ok('The café was very busy.'),
      ['It was to crowded to sit inside.', 'It was too crowded to sit inside.'],
      ok('We looked for a table outside.'),
      ['We decided too wait a little.', 'We decided to wait a little.'],
      ok('A table soon became free.'),
    ], '"Too crowded" (excessive) and "to wait" (infinitive).'),
    p([
      ok('My brother bought a new guitar.'),
      ['He wants too learn quickly.', 'He wants to learn quickly.'],
      ok('He practises every day.'),
      ['The strings were to tight.', 'The strings were too tight.'],
      ok('He tuned them and tried again.'),
    ], 'Use "to learn" (infinitive) and "too tight" (excessive).'),
    p([
      ok('The soup needed more seasoning.'),
      ['It was to salty for me.', 'It was too salty for me.'],
      ok('My sister added some water.'),
      ['She asked me too taste it.', 'She asked me to taste it.'],
      ok('It was much better.'),
    ], '"Too salty" (excessive) and "to taste" (infinitive).'),
    p([
      ok('The walk took longer than expected.'),
      ['The path was to steep for us.', 'The path was too steep for us.'],
      ok('We rested halfway up.'),
      ['We decided too turn back.', 'We decided to turn back.'],
      ok('The view was still lovely.'),
    ], 'Use "too steep" (excessive) and "to turn" (infinitive).'),
  ],

  // 11.3 then / than and other confusions
  '11.3': [
    p([
      ok('My sister is very tall.'),
      ['She is taller then me.', 'She is taller than me.'],
      ok('She plays basketball at school.'),
      ['We finished dinner, than we went out.', 'We finished dinner, then we went out.'],
      ok('It was a pleasant evening.'),
    ], 'Use "than" for comparisons and "then" for time/sequence.'),
    p([
      ok('The new phone is expensive.'),
      ['It costs more then the old one.', 'It costs more than the old one.'],
      ok('The old one still works well.'),
      ['We compared them, than we decided.', 'We compared them, then we decided.'],
      ok('We kept the old phone.'),
    ], '"More than" for comparison; "then" for sequence.'),
    p([
      ok('The two teams are evenly matched.'),
      ['The home side is faster then the visitors.', 'The home side is faster than the visitors.'],
      ok('The visitors are stronger.'),
      ['They scored, than the visitors replied.', 'They scored, then the visitors replied.'],
      ok('The match ended in a draw.'),
    ], 'Use "than" to compare and "then" for what happens next.'),
    p([
      ok('The recipe was simple.'),
      ['It was easier then I expected.', 'It was easier than I expected.'],
      ok('I finished the meal quickly.'),
      ['I cleaned up, than I relaxed.', 'I cleaned up, then I relaxed.'],
      ok('It was a good evening.'),
    ], '"Easier than" compares; "then" marks the next action.'),
    p([
      ok('The train was very crowded.'),
      ['It was busier then usual.', 'It was busier than usual.'],
      ok('I found a seat near the window.'),
      ['I read my book, than I dozed off.', 'I read my book, then I dozed off.'],
      ok('The journey passed quickly.'),
    ], 'Use "than" for comparison and "then" for sequence.'),
  ],

  // 11.4 borrow / lend, lie / lay
  '11.4': [
    p([
      ok('My pen had run out of ink.'),
      ['Can you borrow me a pen?', 'Can you lend me a pen?'],
      ok('My friend handed me one.'),
      ['I promised to give it back, than I forgot.', 'I promised to give it back, then I forgot.'],
      ok('I returned it the next day.'),
    ], '"Lend" gives and "borrow" receives; the sequence word is "then".'),
    p([
      ok('The dog looked tired after its walk.'),
      ['It wanted to lay down on the rug.', 'It wanted to lie down on the rug.'],
      ok('It curled up by the fire.'),
      ['Please lay the blanket over it.', 'Please lay the blanket over it.'],
      ok('It was soon fast asleep.'),
    ], 'People and animals "lie down"; you "lay" something else down.'),
    p([
      ok('I felt unwell after lunch.'),
      ['I decided to lay down for an hour.', 'I decided to lie down for an hour.'],
      ok('The room was quiet and cool.'),
      ['I laid my book on the table first.', 'I laid my book on the table first.'],
      ok('I felt much better afterwards.'),
    ], 'Use "lie down" for yourself and "laid" for placing an object.'),
    p([
      ok('The cat found a sunny spot.'),
      ['It likes to lay in the window.', 'It likes to lie in the window.'],
      ok('It sleeps there every afternoon.'),
      ['She laid a cushion on the sill for it.', 'She laid a cushion on the sill for it.'],
      ok('The cat was very comfortable.'),
    ], '"Lie" is intransitive; "lay" needs an object.'),
    p([
      ok('The hikers were exhausted.'),
      ['They wanted to lay down on the grass.', 'They wanted to lie down on the grass.'],
      ok('They rested for a while.'),
      ['They laid their packs beside them.', 'They laid their packs beside them.'],
      ok('They set off again refreshed.'),
    ], 'Use "lie down" for resting and "laid" for putting things down.'),
  ],

  // 11.5 Redundancy and wordiness
  '11.5': [
    p([
      ok('The committee reviewed the plan.'),
      ['The final outcome was a clear success.', 'The outcome was a clear success.'],
      ok('The whole team celebrated.'),
      ['They discussed the past history of the project.', 'They discussed the history of the project.'],
      ok('Everyone felt proud of the work.'),
    ], 'Avoid redundant pairs: "outcome" and "history" already imply finality and the past.'),
    p([
      ok('The report summarised the findings.'),
      ['It described the basic fundamentals of the method.', 'It described the fundamentals of the method.'],
      ok('The method was clearly explained.'),
      ['The results were a added bonus.', 'The results were a bonus.'],
      ok('The report was well received.'),
    ], '"Fundamentals" and "bonus" do not need "basic" or "added".'),
    p([
      ok('The garden was in a poor state.'),
      ['The weeds were tall and overgrown.', 'The weeds were overgrown.'],
      ok('We decided to tidy it up.'),
      ['We made a plan together to cooperate jointly.', 'We made a plan to work together.'],
      ok('The garden looked lovely by autumn.'),
    ], 'Cut redundant words: "overgrown" already means tall, and "together" covers "jointly".'),
    p([
      ok('The meeting was short.'),
      ['We returned back to the office afterwards.', 'We returned to the office afterwards.'],
      ok('The afternoon was productive.'),
      ['We each wrote our own personal notes.', 'We each wrote our personal notes.'],
      ok('The project moved forward.'),
    ], '"Returned" needs no "back"; "own" and "personal" are redundant.'),
    p([
      ok('The travellers packed light.'),
      ['They met together at the entrance.', 'They met at the entrance.'],
      ok('The bus was already waiting.'),
      ['They shared the same identical map.', 'They shared an identical map.'],
      ok('The trip began on time.'),
    ], 'Remove redundant words: "met" implies together; "same" and "identical" overlap.'),
  ],

  // 11.6 Idioms and collocations
  '11.6': [
    p([
      ok('The pupil prepared his homework.'),
      ['He done a mistake in the first sum.', 'He made a mistake in the first sum.'],
      ok('The teacher marked it clearly.'),
      ['He decided to make it again.', 'He decided to do it again.'],
      ok('He got the right answer in the end.'),
    ], 'We "make a mistake" and "do a task again".'),
    p([
      ok('The family went on holiday.'),
      ['They took a photo of the harbour.', 'They took a photo of the harbour.'],
      ok('The weather was beautiful.'),
      ['They made some photos of the sunset.', 'They took some photos of the sunset.'],
      ok('They framed the best one.'),
    ], 'The collocation is "take a photo", not "make a photo".'),
    p([
      ok('The students revised for the test.'),
      ['They did a lot of progress.', 'They made a lot of progress.'],
      ok('Their confidence grew.'),
      ['They took a decision to study together.', 'They made a decision to study together.'],
      ok('The whole class passed.'),
    ], 'We "make progress" and "make a decision".'),
    p([
      ok('The neighbours were friendly.'),
      ['They made us a warm welcome.', 'They gave us a warm welcome.'],
      ok('They invited us for dinner.'),
      ['They took a lot of effort with the meal.', 'They put a lot of effort into the meal.'],
      ok('It was a lovely evening.'),
    ], 'We "give a welcome" and "put effort into" something.'),
    p([
      ok('The team played an away match.'),
      ['They make an excellent performance.', 'They gave an excellent performance.'],
      ok('The fans cheered them on.'),
      ['They took a good impression on the coach.', 'They made a good impression on the coach.'],
      ok('The coach praised them afterwards.'),
    ], 'We "give a performance" and "make an impression".'),
  ],

  // 11.7 Register and word choice
  '11.7': [
    p([
      ok('The scientist presented the findings.'),
      ['The results were really awesome.', 'The results were excellent.'],
      ok('The committee reviewed the data.'),
      ['The method was kinda unusual.', 'The method was somewhat unusual.'],
      ok('The report was accepted.'),
    ], 'In formal writing, choose "excellent" and "somewhat" over informal words.'),
    p([
      ok('The manager wrote to the client.'),
      ['The delay was a big mess.', 'The delay was a serious problem.'],
      ok('She promised a full investigation.'),
      ['The client was pretty annoyed.', 'The client was rather annoyed.'],
      ok('The matter was resolved quickly.'),
    ], 'Replace informal expressions with formal equivalents.'),
    p([
      ok('The pupils wrote a report on the trip.'),
      ['The mountain was totally massive.', 'The mountain was very large.'],
      ok('They described the long climb.'),
      ['The view from the top was super cool.', 'The view from the top was impressive.'],
      ok('The trip was educational and fun.'),
    ], 'Use formal description in a written report: "very large", "impressive".'),
    p([
      ok('The council reviewed the proposal.'),
      ['The plan was a bit of a disaster.', 'The plan was unsuccessful.'],
      ok('A new committee was formed.'),
      ['The old system was pretty useless.', 'The old system was ineffective.'],
      ok('The new plan was approved.'),
    ], 'Choose formal wording: "unsuccessful", "ineffective".'),
    p([
      ok('The doctor spoke to the patient.'),
      ['The treatment was kinda painful.', 'The treatment was quite painful.'],
      ok('The patient asked several questions.'),
      ['The recovery was a total breeze.', 'The recovery was straightforward.'],
      ok('The patient was soon discharged.'),
    ], 'Use formal vocabulary: "quite painful", "straightforward".'),
  ],

  // 11.8 fewer/less, amount/number
  '11.8': [
    p([
      ok('The festival attracted many visitors.'),
      ['There were less people than last year.', 'There were fewer people than last year.'],
      ok('The organisers were disappointed.'),
      ['There was a smaller amount of visitors.', 'There was a smaller number of visitors.'],
      ok('They hoped for a better turnout next time.'),
    ], 'Use "fewer" and "number" with countable nouns.'),
    p([
      ok('The library kept careful records.'),
      ['They bought fewer new books this term.', 'They bought fewer new books this term.'],
      ok('The budget was tight.'),
      ['The number of visitors was less than expected.', 'The number of visitors was lower than expected.'],
      ok('They relied on donated books.'),
    ], 'With countable nouns use "fewer" and "lower number".'),
    p([
      ok('The shop sold fresh produce.'),
      ['There was less apples in the crate.', 'There were fewer apples in the crate.'],
      ok('The farmer delivered a new batch.'),
      ['The number of crates was smaller than usual.', 'The number of crates was smaller than usual.'],
      ok('The shop soon restocked.'),
    ], 'Countable items take "fewer"; "number" fits countable nouns.'),
    p([
      ok('The class compared two surveys.'),
      ['The first had less participants.', 'The first had fewer participants.'],
      ok('The second was more detailed.'),
      ['It also had a larger amount of questions.', 'It also had a larger number of questions.'],
      ok('The class preferred the second one.'),
    ], '"Fewer participants" and "number of questions" for countable nouns.'),
    p([
      ok('The town measured its traffic.'),
      ['There were less cars on the road today.', 'There were fewer cars on the road today.'],
      ok('The new bypass helped.'),
      ['The amount of vehicles dropped sharply.', 'The number of vehicles dropped sharply.'],
      ok('The air was cleaner as a result.'),
    ], 'Use "fewer cars" and "number of vehicles" for countable nouns.'),
  ],
};
