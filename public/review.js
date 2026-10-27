import {escape as h} from './model.js';

// All input comes from the public-only projection, never the private registry.
export function conversionHtml(rules,entity,system,sourceLinks){
 const review=rules.review,c=review?.cases.find(c=>c.entity_id===entity);
 if(!c)return '';
 const gap=c.gap_options.find(g=>g.system_id===system);
 const proposal=rules.profiles.some(p=>p.entity_id===entity&&p.system_id===system&&p.coverage==='new_proposal');
 return `<details class="conversion-review"><summary>Vazby a možnosti převodu${gap?' · pramenná mezera':''}</summary>
 <p>${gap?(proposal?'Původní aplikace chybí; níže je samostatně označený nový návrh.':'Úplná aplikace ještě není hotová. Toto jsou podklady a varianty k rozhodnutí, nikoli hratelný blok.'):'Původní varianty zůstávají oddělené; společný název schopnosti neznamená shodný účinek.'}</p>
 <p>${h(review.system_contracts[system]||'')}</p>
 ${c.identity_flags.length?'<p class="proposal-warning">Pozor na sdílené bloky, vyšší varianty a pracovní přiřazení názvů. Schopnosti různých variant se nesčítají.</p>':''}
 <h4>Možnosti pro doložené názvy schopností</h4><p class="muted">Stavební prvky k posouzení. Neudělují bytosti nové schopnosti; před použitím zvolte konkrétní výchozí variantu.</p>
 ${c.features.map(f=>`<details class="feature-choice"><summary>${h(f.label)}</summary>${f.options.map(t=>`<p>${h(t)}</p>`).join('')}<p>${sourceLinks(f)}</p></details>`).join('')||'<p>Jmenný průzkum neurčil společnou sadu. Ověřte konkrétní výchozí bloky.</p>'}
 ${gap?`<h4>Dosud nerozhodnuto</h4><ul>${gap.unresolved.map(x=>`<li>${h(x)}</li>`).join('')}</ul>`:''}
 <details><summary>Společné zásady převodu</summary>${review.dependency_rules.map(r=>`<h4>${h(r.title)}</h4><p>${h(r.rule)}</p>`).join('')}</details>
 <details><summary>Pravidlové reference</summary>${review.rules_refs.map(r=>`<p><a href="${h(r.url)}" target="_blank" rel="noopener">${h(r.title)} ↗</a></p>`).join('')}</details></details>`;
}

export function proposalHtml(p){
 if(p.coverage!=='new_proposal')return '';
 const incomplete=p.application_kind==='compatibility_draft';
 return `<div class="proposal-warning"><strong>${incomplete?'Kompatibilní návrh — dosud neúplně zkontrolovaný':'Nový testovací blok — neověřeno hrou'}</strong><p>${h(p.design_notes||'')}</p><p>Čísla a omezení jsou návrhová volba. Předlohy nejsou dokladem schválení těchto změn.</p></div>
 <details class="proposal-options"><summary>Varianty A/B k posouzení</summary>${(p.alternatives||[]).map(t=>`<p>${h(t)}</p>`).join('')}
 <label>Pracovní volba pro tento návrh <select data-review="${h(p.id)}" aria-label="Pracovní volba ${h(p.variant)}"><option value="">Nerozhodnuto</option><option value="A">A — pro další test</option><option value="B">B — pro další test</option><option value="revise">Přepracovat</option></select></label><p class="muted" data-review-status>Volba se ukládá jen v tomto prohlížeči. Nemění aplikaci, Obsidian ani stav schválení.</p></details>`;
}

export function bindReviewChoices(root){
 for(const select of root.querySelectorAll('[data-review]')){
  const key='asterion-proposal-choice:'+select.dataset.review;
  try{const v=localStorage.getItem(key);if(['A','B','revise'].includes(v))select.value=v}catch{}
  select.onchange=()=>{const status=select.parentElement.nextElementSibling;try{
   if(select.value)localStorage.setItem(key,select.value);else localStorage.removeItem(key);
   status.textContent='Uloženo pouze v tomto prohlížeči; profil ani jeho schválení se nemění.';
  }catch{status.textContent='Prohlížeč nepovolil uložení. Volba platí jen do obnovení stránky.'}};
 }
}
