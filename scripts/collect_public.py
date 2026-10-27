"""Acquire only PDFs linked by the official public applications catalogue."""
from pathlib import Path
import json,sys,re,hashlib,urllib.request,urllib.parse,concurrent.futures
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent
try:
 import fitz
except ImportError:
 sys.path.insert(0,str(BASE/'asterion-tri-moduly-web/tmp/fa-deps'))
 import fitz
CATALOG='https://asterionrpg.cz/index.php/aplikace-pravidel.html'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Asterion application reader source verification'})
 with urllib.request.urlopen(req,timeout=60) as r:return r.read()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.base=CATALOG
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='base' and d.get('href'):self.base=urllib.parse.urljoin(CATALOG,d['href'])
  if t=='a' and d.get('href'):
   url=urllib.parse.urljoin(self.base,d['href']);parts=urllib.parse.urlsplit(url)
   self.links.append(urllib.parse.urlunsplit((parts.scheme,parts.netloc,urllib.parse.quote(urllib.parse.unquote(parts.path),safe='/+'),parts.query,parts.fragment)))
MODULES=[('ct','Čas temna','Základní pravidla světa, Hlavní modul a Dálavy'),('ns','Nemrtví a světlonoši','Smrt, nemrtví a jejich protivníci'),('pp','Písky proroctví','Mar’Nub, pouštní elfové a Nunmejci'),('vtb','Vzestup temných bohů','Božstva, kněží a zázraky'),('hzm','Z hlubin zelené a modré','Moře, ostrovy a vodní svět'),('zp','Zlatá pavučina','Obchod, zločin a městské prostředí'),('old','Obloha z listí a drahokamů','Džungle, skřítci a elfové'),('fa','Falešná apokalypsa','Magie, školy a pomocníci'),('zzs','Za závojem stínů','Stínový svět, druidi a rituály'),('ko','Stíny jihu','Jižní Tara a její obyvatelé'),('sz','Sedmý živel','Nekromancie a nemrtví'),('svv','Sarindarské výsostné vody','Sarindar a dobrodružství')]
def classify(url):
 name=urllib.parse.unquote(urllib.parse.urlsplit(url).path.split('/')[-1]);lo=name.lower()
 if 'aplikace_dh' in lo or ('dh' in lo and ('hr' in lo or 'vypr' in lo)):return 'dh-all','dh',('Hráči' if 'hr' in lo else 'Vypravěč')
 if lo=='aplikace.pdf':return 'ct','dnd5e_2014','DnD 5e v0.1'
 if 'drdii' in lo or 'drd_ii' in lo or 'drd ii' in lo:
  return ('ct' if 'temna' in lo or 'cas' in lo or lo.startswith('ct') else 'sz'),'drd_ii',('Černobílá sazba' if 'bw' in lo or 'ernob' in lo else 'Barevná sazba')
 for mid,_,_ in MODULES:
  if lo.startswith(mid+'_drd'):return mid,('drd_plus' if '+' in lo else 'drd_16'),'Aplikace pravidel'
 if 'ko_drd' in lo:return 'ko','drd_16','Aplikace pravidel'
 if 'stiny' in lo or 'stíny' in lo:return 'ko',('drd_plus' if '+' in lo else 'drd_16'),'Aplikace pravidel'
 if 'sz_' in lo:return 'sz','drd_ii' if 'drdii' in lo else 'drd_16','Aplikace pravidel'
 if 'svv' in lo or '/svv/' in url.lower():return 'svv','drd_16','Dobrodružství' if 'dobro' in lo or lo.startswith('2') else 'Hlavní aplikace'
 return None
def main():
 html=get(CATALOG).decode('utf-8');p=Links();p.feed(html)
 urls=sorted(set(u for u in p.links if urllib.parse.urlsplit(u).path.lower().endswith('.pdf')))
 qa=ROOT/'qa';qa.mkdir(exist_ok=True);(qa/'catalogue.html').write_text(html,'utf-8')
 records=[];errors=[]
 def job(url):
  data=get(url);assert data.startswith(b'%PDF'),url
  h=hashlib.sha256(data).hexdigest();sid=h[:16];file=ROOT/'public/pdf'/(sid+'.pdf');file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
  doc=fitz.open(stream=data,filetype='pdf');intro=' '.join(doc[0].get_text().split())
  cls=classify(url)
  if not cls:return {'unclassified':url,'intro':intro[:500],'id':sid}
  module,system,variant=cls
  # Internal title has priority over the website's DnD aka JaD shelf label.
  if 'DrD+' in intro or 'doupěte Plus' in intro:system='drd_plus'
  pages=[{'page':i+1,'text':pg.get_text(),'blocks':[b[4].strip() for b in pg.get_text('blocks') if b[6]==0 and b[4].strip()]} for i,pg in enumerate(doc)]
  write(ROOT/'public/data/documents'/(sid+'.json'),{'id':sid,'pages':pages})
  heads=[{'page':i+1,'label':'Bestiář'} for i,pg in enumerate(pages) if i>3 and re.search(r'(?im)^\s*Besti[aá]ř\s*$',pg['text'])]
  return {'id':sid,'module':module,'system':system,'variant':variant,'url':url,'sha256':h,'pages':len(doc),'bytes':len(data),'intro':intro[:650],'pdf':'pdf/'+sid+'.pdf','data':'data/documents/'+sid+'.json','bestiaryPage':heads[0]['page'] if heads else None}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  futures={pool.submit(job,u):u for u in urls}
  for f in concurrent.futures.as_completed(futures):
   try:records.append(f.result())
   except Exception as exc:errors.append({'url':futures[f],'error':str(exc)})
 write(ROOT/'qa/public_sources.json',{'catalogue':CATALOG,'checked':'2026-10-27','documents':sorted(records,key=lambda x:x['id']),'errors':errors})
 write(ROOT/'public/data/catalogue.json',{'updated':'2026-10-27','sourceUrl':CATALOG,'modules':[{'id':m,'title':t,'description':d} for m,t,d in MODULES]+[{'id':'dh-all','title':'Asterion v Dračí hlídce','description':'Souhrnné příručky pro hráče a vypravěče'}],'documents':[r for r in records if 'unclassified' not in r],'unavailable':errors})
 print(json.dumps({'downloaded':len(records),'errors':errors,'unclassified':[r for r in records if 'unclassified' in r]},ensure_ascii=False))
if __name__=='__main__':main()
