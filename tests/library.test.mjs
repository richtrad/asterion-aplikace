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
 assert.equal(rules.entities.length,9);assert.equal(rules.profiles.length,38);
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
