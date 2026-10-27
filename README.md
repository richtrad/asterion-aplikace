# Asterion — pravidlové aplikace

Veřejná knihovna pravidlových aplikací s jedním výchozím a volitelným druhým čtecím panelem.
Vychází ze vzhledu elektronické edice modulů Asterionu. Tento projekt je samostatný;
neobsahuje soukromé modulové texty, diskuse ani interní rukopisy.

## Čtení a porovnávání

- Jeden nebo dva panely, v každém vlastní pravidla, dokument, stránka a posuv.
- 237 myšlenkových bytostí a pět dalších pilotních položek; hledání napříč moduly i podle názvů variant.
- Celé veřejné aplikace jako text nebo původní PDF; hledání uvnitř každého dokumentu.
- Prameny, varianty a otevřené rozpory u jednotlivých karet.
- Sdílení odkazu na modul, položku, systémy a režim čtení; tři vzhledy.
- Na mobilu jsou oba panely pod sebou.

Sada z 27. 10. 2026 obsahuje 29 veřejných PDF, 999 profilů (z toho 961 zdrojových bloků)
a 176 otevřených nálezů a rozdílů. Varianty, vydání, tabulky růstu pomocníčků a
společné bloky více bytostí zůstávají rozlišeny. Text je automatický výpis
s kontrolovanými hranicemi a ověřením vybraných stran, nikoli úplná mechanická
revize. Pole jsou výběrem údajů; pro hru platí také obecná pravidla původní aplikace.
JaD a D&D 2024 nejsou zaměňovány s DnD 5e v0.1, uvedeným uvnitř veřejného PDF
Času temna. Pracovní JaD a neveřejné historické podklady patří do místního Obsidianu.

Výchozí odkaz `#read` otevře jeden panel. `split=1` zapíná druhý panel a zachovává
starší sdílené odkazy. Volba „Všechny moduly“ hledá v celé veřejné sadě. Rozdíly
v emocích jsou podněty k rozhodnutí, nikoli automaticky potvrzené chyby. Jmenné
odchylky mají zvláštní varování a původní nadpis každého bloku je zachován.

## Původ obsahu

Jediným vstupem pro zveřejněné PDF je
[oficiální katalog Asterionu](https://asterionrpg.cz/index.php/aplikace-pravidel.html).
`public/data/catalogue.json` uvádí původní URL, SHA-256, rozsah a systém každého
dokumentu. Původní autorské údaje zůstávají v PDF. Veřejné zpřístupnění tímto
projektem nemění autorská práva ani neuděluje novou licenci k původním textům.

`scripts/collect_public.py` stáhne PDF odkazovaná katalogem a vytvoří čtecí data.
Vyžaduje Python 3 a PyMuPDF (`python -m pip install pymupdf`).
`scripts/export_registry.py` vytváří omezený veřejný výřez z místního redakčního
registru v sousedním projektu; registr není součástí tohoto repozitáře. Export
připustí pouze záznamy, jejichž všechny prameny odpovídají veřejným PDF podle
obsahového identifikátoru. Soukromé poznámky, cesty a nedoložené návrhy se neexportují.
Pro běžné spuštění není regenerace ani přístup k registru potřebný.

## Místní spuštění a kontrola

```sh
python -m http.server 8792 --bind 127.0.0.1 --directory public
node --check public/app.js
node --test tests/*.test.mjs
```

Otevřete `http://127.0.0.1:8792`. Stránka potřebuje HTTP server kvůli načítání JSON.
Neobsahuje framework, externí analytiku ani přihlašování. Původní PDF vykresluje
lokálně přibalená Mozilla PDF.js 6.4.299 (Apache-2.0); licence a verze jsou
v `public/vendor/pdfjs/`. Dokumenty se neposílají žádné externí službě.

## Nasazení

Cloudflare Pages, samostatný projekt `asterion-aplikace`, produkční větev `main`.
Nahrává se **pouze adresář `public`**. Nepoužívat kořen repozitáře.

```sh
wrangler pages deploy public --project-name asterion-aplikace --branch main
```

GitHub uchovává zdroje a historii. Nasazování je ruční Direct Upload;
samotný push do GitHubu web automaticky neaktualizuje. Tento projekt nemá
Overleaf remote a neprovádí synchronizaci žádného rukopisu.
