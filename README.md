# Asterion — pravidlové aplikace

Veřejná knihovna pravidlových aplikací s dvojicí nezávislých čtecích panelů.
Vychází ze vzhledu elektronické edice modulů Asterionu. Tento projekt je samostatný;
neobsahuje soukromé modulové texty, diskuse ani interní rukopisy.

## Čtení a porovnávání

- Jeden nebo dva panely, v každém vlastní pravidla, dokument, stránka a posuv.
- Společný výběr položky pro přímé srovnání devíti položek pilotu.
- Celé veřejné aplikace jako text nebo původní PDF; hledání uvnitř každého dokumentu.
- Prameny, varianty a otevřené rozpory u jednotlivých karet.
- Sdílení odkazu na modul, položku, systémy a režim čtení; tři vzhledy.
- Na mobilu jsou oba panely pod sebou.

Sada z 27. 10. 2026 obsahuje 29 veřejných PDF, 38 pracovních pravidlových profilů
a 7 nálezů k řešení. Srovnávací karty nejsou kompletní statbloky. Dostupnost karty
se liší od dostupnosti celého dokumentu. JaD a D&D 2024 nejsou zaměňovány s DnD 5e
v0.1, které je uvedeno uvnitř veřejného PDF Času temna.

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
Neobsahuje framework, externí analytiku ani přihlašování.

## Nasazení

Cloudflare Pages, samostatný projekt `asterion-aplikace`, produkční větev `main`.
Nahrává se **pouze adresář `public`**. Nepoužívat kořen repozitáře.

```sh
wrangler pages deploy public --project-name asterion-aplikace --branch main
```

GitHub uchovává zdroje a historii. Nasazování je ruční Direct Upload;
samotný push do GitHubu web automaticky neaktualizuje. Tento projekt nemá
Overleaf remote a neprovádí synchronizaci žádného rukopisu.
