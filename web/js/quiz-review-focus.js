import {topicPerformance} from './quiz-v2.js';
export function reviewFocus(bank,curriculum,attempts,trackId){
 const perf=topicPerformance(bank,curriculum,attempts,trackId);
 const track=curriculum.find(t=>t.id===trackId);
 const topics=[...perf.topics.entries()].filter(([,s])=>s.incorrect>0).map(([key,s])=>{
  const [chapterId,topicId]=key.split('/');
  const topic=track?.chapters.find(c=>c.id===chapterId)?.topics.find(t=>t.id===topicId);
  return topic?{title:topic.title,...s}:null;
 }).filter(Boolean).sort((a,b)=>b.weakness-a.weakness||b.incorrect-a.incorrect);
 if(!topics.length)return 'Complete a quiz to build your review focus. Only submitted answers are used; there are no recorded mistakes to review yet.';
 const selected=topics.slice(0,2);
 const names=selected.map(t=>t.title).join(' and ');
 const repeated=selected.some(t=>t.incorrect>=2);
 return `Focus on ${names}. ${repeated?'Repeated missed answers make these useful areas to revisit.':'A missed answer points to each of these topics; more practice will give a clearer picture.'}`;
}
