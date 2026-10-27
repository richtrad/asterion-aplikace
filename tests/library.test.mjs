import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {parseState,stateHash,entitiesFor,documentsFor,profilesFor,pageNumber,norm,escape} from '../public/model.js';
const root=new URL('../public/',import.meta.url);
const json=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const cat=json('data/catalogue.json'),rules=json('data/rules.json');
test('share link preserves independent systems and two-panel mode',()=>{
 const s={module:'pp',entity:'rod.nunmejec',left:'drd_plus',right:'dh',view:'document',split:false};
 assert.deepEqual(parseState(stateHash(s),cat,rules),{route:'read',...s});
});

test('one panel is the default; comparison is explicit and shareable',()=>{
 assert.equal(parseState('#read',cat,rules).split,false);
 assert.equal(parseState('#read?split=1',cat,rules).split,true);
 assert.equal(parseState('#read?split=0',cat,rules).split,false);
 const s=parseState('#read?module=all&entity=bytost.minva&split=1',cat,rules);
 assert.equal(s.module,'all');assert.equal(s.entity,'bytost.minva');
 assert.equal(parseState(stateHash(s),cat,rules).split,true);
});
test('invalid route values and foreign-module entity cannot select unrelated cards',()=>{
 const s=parseState('#read?module=pp&entity=bytost.huama&left=unknown',cat,rules);
 assert.equal(s.left,'drd_16');assert(entitiesFor(rules,'pp').some(e=>e.id===s.entity));
 assert.equal(parseState('#read?module=unknown',cat,rules).module,'ct');
});
test('Czech search, type filter and document alternatives',()=>{
 assert.equal(entitiesFor(rules,'ns','temny','bytost')[0].id,'bytost.temny-vlk');
 assert.equal(entitiesFor(rules,'ct','Huama','rod').length,0);
 assert(documentsFor(cat,'ns','drd_ii').every(d=>d.module==='sz'));
 assert.equal(documentsFor(cat,'ct','dh').length,2);
 assert.equal(documentsFor(cat,'ct','jad').length,0);
 assert.equal(profilesFor(rules,'bytost.huama','dnd5e_2024').length,0);
});
test('page input is bounded and rendered source text cannot inject markup',()=>{
 assert.equal(pageNumber(-10,100),1);assert.equal(pageNumber(999,100),100);
 assert.equal(pageNumber('garbage',100),1);assert.equal(pageNumber('3.8',100),3);
 assert.equal(norm('Myšlenkové BYTOSTI'),'myslenkove bytosti');
 assert.equal(escape('<script>"&'),'&lt;script&gt;&quot;&amp;');
});
test('every public PDF matches official-source digest and extracted page count',()=>{
 assert.equal(cat.documents.length,29);assert.equal(cat.unavailable.length,0);
 assert.equal(new Set(cat.documents.map(d=>d.id)).size,cat.documents.length);
 for(const d of cat.documents){
  assert.equal(new URL(d.url).hostname,'asterionrpg.cz');
  const pdf=readFileSync(new URL(d.pdf,root));
  assert.equal(createHash('sha256').update(pdf).digest('hex'),d.sha256);
  assert.equal(pdf.length,d.bytes);
  const text=json(d.data);assert.equal(text.id,d.id);assert.equal(text.pages.length,d.pages);
  text.pages.forEach((p,i)=>assert.equal(p.page,i+1));
 }
});
test('all public cards and findings cite only downloaded public PDFs and valid pages',()=>{
 assert(rules.entities.length>200);assert(rules.profiles.length>900);
 assert.equal(rules.counts.thoughtBeings,rules.entities.filter(e=>e.kind==='bytost').length);
 assert.equal(rules.counts.sourceBlocks,rules.profiles.filter(p=>p.text).length);
 for(const p of [...rules.profiles,...rules.decisions]){
  assert(p.source_refs.length);
  for(const r of p.source_refs){
   const d=cat.documents.find(d=>d.id===r.source_id);assert(d);
   for(const n of r.pdf_pages||[])assert(n>=1&&n<=d.pages,`${p.id}: ${n}`);
   assert(!('path' in r));assert(!('extract_path' in r));
  }
 }
 const data=JSON.stringify(rules);
 assert(!/C:\\\\Users|docs\.google\.com|discord\.com|raw_snapshot|snapshot_path|source_path/i.test(data));
 assert.equal(readdirSync(new URL('pdf/',root)).length,cat.documents.length);
});

test('variants, shared blocks, aliases and gaps survive the export',()=>{
 assert(entitiesFor(rules,'all','kvilice').some(e=>e.id==='bytost.bansi'));
 assert(entitiesFor(rules,'all','dvouhlavec').some(e=>e.id==='bytost.mnohohlavy-obr'));
 const minva=profilesFor(rules,'bytost.minva','drd_16').find(p=>p.text);
 assert(minva.text.includes('Minva / Ralva'));assert.equal(minva.values,null);
 assert.equal(profilesFor(rules,'bytost.huama','dnd5e_2014').filter(p=>p.text).length,2);
 assert.equal(profilesFor(rules,'bytost.huama','jad').length,0);
 assert.equal(profilesFor(rules,'bytost.vanga','drd_16').filter(p=>p.text).length,2);
 assert(!rules.entities.some(e=>e.label==='Draci'||/^\d+$/.test(e.label)));
 assert(rules.decisions.some(d=>d.type==='identity_to_review'));
 assert(rules.decisions.some(d=>d.entity_ids.includes('bytost.epyra')&&d.description.includes('touha')));
});
