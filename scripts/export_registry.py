"""Export a public-only projection. Never ship the private registry or its paths."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 cat=read(ROOT/'public/data/catalogue.json');docs={d['id']:d for d in cat['documents']}
 reg=BASE/'08_pravidlove_aplikace/registry';entities=read(reg/'entities.json');profiles=read(reg/'profiles.json');decisions=read(reg/'decisions.json')
 module={'bytost.huama':['ct'],'bytost.draskara':['pp'],'bytost.epyra':['ct'],'bytost.temny-vlk':['ns'],'rod.poustni-elf':['pp'],'rod.nunmejec':['pp'],'material.lintir':['ct'],'predmet.albirejska-koruna':['ct'],'pravidlo.magicky-pomocnik':['fa','zzs','vtb']}
 def ref(r):return {k:r[k] for k in ['source_id','pdf_pages','printed_pages','section'] if k in r}
 pp=[]
 for p in profiles:
  if p['entity_id'] not in module or p['coverage']=='not_found_in_audited_sources':continue
  rr=p['source_refs']
  if not rr or not all(r['source_id'] in docs for r in rr):continue
  out={k:p.get(k) for k in ['id','entity_id','system_id','edition','application_version','variant','coverage','values','summary','is_complete_statblock']}
  out['source_refs']=[ref(r) for r in rr];out['state']='Pracovní přepis veřejné aplikace';pp.append(out)
 ee=[{'id':e['id'],'label':e['label'],'kind':e['kind'],'modules':module[e['id']]} for e in entities if e['id'] in module]
 dd=[]
 for d in decisions:
  if not any(e in module for e in d['entity_ids']):continue
  if not d.get('source_refs') or not all(r['source_id'] in docs for r in d['source_refs']):continue
  dd.append({k:d.get(k) for k in ['id','entity_ids','title','description','recommendation','type','status']}|{'source_refs':[ref(r) for r in d['source_refs']]})
 huama16=next(p for p in pp if p['id']=='bytost.huama.drd_16.zakladni')
 huamadh=next(p for p in pp if p['entity_id']=='bytost.huama' and p['system_id']=='dh')
 dd.append({'id':'public.huama-emoce','entity_ids':['bytost.huama'],'title':'Huama: strach × rozhořčení','description':'Veřejná aplikace DrD 1.6 uvádí vyvolávací emoci strach, veřejná aplikace Dračí hlídky rozhořčení. Jde o rozdíl v popisu téže bytosti, nikoli o převod číselné stupnice.','recommendation':'Obě znění zachovat u jejich systémů. Bez autorského rozhodnutí žádné z nich nepovýšit na společné pravidlo světa.','type':'source_conflict','status':'open','source_refs':huama16['source_refs']+huamadh['source_refs']})
 sy=[{'id':s['id'],'label':s['label']} for s in read(reg/'systems.json')]
 data={'updated':'2026-10-27','entities':ee,'profiles':pp,'decisions':dd,'systems':sy,'scope':'Srovnávací pilot devíti položek; celé veřejné aplikace jsou v čtečce dokumentů. Soukromé návrhy nejsou součástí veřejného exportu.'}
 (ROOT/'public/data/rules.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
 report={'publicProfiles':len(pp),'entities':len(ee),'publicFindings':len(dd),'allowedSourceIds':sorted(docs),'privateRegistryIncluded':False}
 (ROOT/'qa/export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
