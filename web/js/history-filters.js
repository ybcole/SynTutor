// Rolling elapsed-time windows in UTC milliseconds; never mutate source rows.
export function historyTimestamp(row) {
 const value=row.created_at;
 if(typeof value!=='string'||!value.trim())return NaN;
 // Timestamp strings without a zone are interpreted explicitly as UTC.
 return Date.parse(/(?:Z|[+-]\d\d:\d\d)$/i.test(value)?value:value+'Z');
}
export function filterHistory(entries, range='all', now=Date.now()) {
 const days={day:1,week:7,month:30}[range];
 return entries.filter(row=>{
  const time=historyTimestamp(row);
  return !days||(Number.isFinite(time)&&time<=now&&time>=now-days*86400000);
 }).sort((a,b)=>(Number.isFinite(historyTimestamp(b))?historyTimestamp(b):-Infinity)-(Number.isFinite(historyTimestamp(a))?historyTimestamp(a):-Infinity));
}
