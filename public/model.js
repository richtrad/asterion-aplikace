export const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('cs');
export const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function parseState(hash,cat,rules){
 const [route,q='']=hash.replace(/^#/,'').split('?');const p=new URLSearchParams(q);
 const module=cat.modules.some(m=>m.id===p.get('module'))?p.get('module'):'ct';
 const available=entitiesFor(rules,module);
 const entity=available.some(e=>e.id===p.get('entity'))?p.get('entity'):(available[0]?.id||'');
 const system=(key,fallback)=>rules.systems.some(s=>s.id===p.get(key))?p.get(key):fallback;
 const view=p.get('view')==='document'?'document':'cards';
 return {route:['read','sources'].includes(route)?route:'home',module,entity,left:system('left','drd_16'),right:system('right','dh'),split:p.get('split')!=='0',view};
}
export function stateHash(s){const p=new URLSearchParams();for(const k of ['module','entity','left','right','view'])p.set(k,s[k]);p.set('split',s.split?'1':'0');return '#read?'+p}
export function entitiesFor(rules,module,query='',kind='all'){return rules.entities.filter(e=>(module==='dh-all'||e.modules.includes(module))&&(kind==='all'||e.kind===kind)&&norm(e.label).includes(norm(query)))}
export function profilesFor(rules,entity,system){return rules.profiles.filter(p=>p.entity_id===entity&&p.system_id===system)}
export function documentsFor(cat,module,system){return cat.documents.filter(d=>d.system===system&&(d.module===module||d.module==='dh-all'||module==='dh-all'||(module==='ns'&&d.module==='sz'&&system==='drd_ii')))}
export function pageNumber(value,total){return Math.max(1,Math.min(total,Math.trunc(Number(value))||1))}
