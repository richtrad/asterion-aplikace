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
  if p['entity_id'] not in module and p.get('import_batch')!='bestiary-20261027':continue
  if p['coverage']=='not_found_in_audited_sources':continue
  rr=p['source_refs']
  if not rr or not all(r['source_id'] in docs for r in rr):continue
  out={k:p.get(k) for k in ['id','entity_id','system_id','edition','application_version','variant','coverage','values','summary','text','application_kind','identity_status','is_complete_statblock','proposed_values','alternatives','design_notes','rules_refs','derived_from_profile_ids','authorship']}
  out['source_refs']=[ref(r) for r in rr];out['state']=('Nový návrh · neověřeno hrou' if p['coverage']=='new_proposal' else 'Textový blok veřejné aplikace' if p.get('text') else 'Výběr údajů z veřejné aplikace');pp.append(out)
  module.setdefault(p['entity_id'],[])
  for m in p.get('modules',[]):
   if m not in module[p['entity_id']]:module[p['entity_id']].append(m)
 ee=[{'id':e['id'],'label':e['label'],'kind':e['kind'],'modules':module[e['id']],
      'aliases':sorted({p['variant'] for p in pp if p['entity_id']==e['id'] and p.get('text')})} for e in entities if e['id'] in module]
 dd=[]
 for d in decisions:
  if not any(e in module for e in d['entity_ids']):continue
  if not d.get('source_refs') or not all(r['source_id'] in docs for r in d['source_refs']):continue
  dd.append({k:d.get(k) for k in ['id','entity_ids','title','description','proposal','recommendation','type','status','profile_ids']}|{'source_refs':[ref(r) for r in d['source_refs']]})
 huama16=next(p for p in pp if p['id']=='bytost.huama.drd_16.zakladni')
 huamadh=next(p for p in pp if p['entity_id']=='bytost.huama' and p['system_id']=='dh')
 dd.append({'id':'public.huama-emoce','entity_ids':['bytost.huama'],'title':'Huama: strach × rozhořčení','description':'Veřejná aplikace DrD 1.6 uvádí vyvolávací emoci strach, veřejná aplikace Dračí hlídky rozhořčení. Jde o rozdíl v popisu téže bytosti, nikoli o převod číselné stupnice.','recommendation':'Obě znění zachovat u jejich systémů. Bez autorského rozhodnutí žádné z nich nepovýšit na společné pravidlo světa.','type':'source_conflict','status':'open','source_refs':huama16['source_refs']+huamadh['source_refs']})
 # Mixed private/public editorial dossiers cannot be published as a whole.
 # Build a separate public finding solely from the already-allowed profiles.
 for e in ee:
  for status,kind,label,description in [
    ('provisional_name_correspondence','identity_to_review','odlišné názvy','Společná srovnávací karta obsahuje jmenné odchylky. Totožnost je pracovní a vyžaduje potvrzení; hodnoty a původní názvy zůstávají oddělené.'),
    ('shared_block','shared_source_block','společný blok','Pramen uvádí několik bytostí ve společném bloku. Lomítka a odlišné podmínky se nesmějí bez výkladu pramene přidělit každé bytosti stejně.')]:
   matched=[p for p in pp if p['entity_id']==e['id'] and p.get('identity_status')==status]
   if not matched or any(d['type']==kind and e['id'] in d['entity_ids'] for d in dd):continue
   refs=[]
   for p in [p for p in pp if p['entity_id']==e['id'] and p.get('text')]:
    for r in p['source_refs']:
     if r not in refs:refs.append(r)
   dd.append({'id':'public.'+e['id']+'.'+kind,'entity_ids':[e['id']],'title':e['label']+': '+label,
       'description':description+' Názvy v dotčených veřejných blocích: '+', '.join(sorted({p['variant'] for p in matched}))+'.',
       'recommendation':'Ponechat zdrojové varianty; opravu nebo sjednocení provést až po redakčním rozhodnutí.',
       'type':kind,'status':'open','source_refs':refs})
 sy=[{'id':s['id'],'label':s['label']} for s in read(reg/'systems.json')]
 review=None
 if (reg/'conversion_review.json').exists():
  rr=read(reg/'conversion_review.json');ids={p['id'] for p in pp}
  review={'date':rr['date'],'rules_refs':rr['rules_refs'],'system_contracts':rr['system_contracts'],
          'dependency_rules':rr['dependency_rules'],'cases':[]}
  for c in rr['public_cases']:
   o={k:c[k] for k in ['entity_id','label','gaps','gap_options','identity_flags','scope']}
   o['source_refs']=[ref(r) for r in c['source_refs']]
   o['new_profile_ids']=[i for i in c['new_profile_ids'] if i in ids]
   o['coverage']={s:[i for i in ii if i in ids] for s,ii in c['coverage'].items()}
   o['features']=[{k:f[k] for k in ['id','label','options','status']}|{'source_refs':[ref(r) for r in f['source_refs']],'profile_ids':[i for i in f['profile_ids'] if i in ids]} for f in c['features']]
   review['cases'].append(o)
  review['counts']={'publicEntities':len(review['cases']),
    'newProposals':sum(p['coverage']=='new_proposal' for p in pp),
    'playtestBlocks':sum(p.get('application_kind')=='editorial_statblock' for p in pp),
    'compatibilityDrafts':sum(p.get('application_kind')=='compatibility_draft' for p in pp)}
 data={'updated':'2026-10-27','entities':ee,'profiles':pp,'decisions':dd,'systems':sy,
       'review':review,
       'scope':'Veřejné aplikace a oddělené nové redakční návrhy. Původní znění se nepřepisuje. Návrhy ani podklady k převodu nejsou schválením či herním testem. Soukromé rukopisy a starší soukromé návrhy nejsou součástí veřejného exportu.',
       'counts':{'thoughtBeings':sum(e['kind']=='bytost' for e in ee),'sourceBlocks':sum(bool(p.get('text')) and p['coverage']!='new_proposal' for p in pp), 'proposalBlocks':sum(p['coverage']=='new_proposal' for p in pp)}}
 (ROOT/'public/data/rules.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
 report={'publicProfiles':len(pp),'entities':len(ee),'publicFindings':len(dd),'allowedSourceIds':sorted(docs),'privateRegistryIncluded':False}
 (ROOT/'qa/export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
