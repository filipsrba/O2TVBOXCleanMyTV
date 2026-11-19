---
name: o2-tv-safe-launcher
description: "Diagnostikuj O2/ZTE Android TV box přes ADB a nastav samostatný launcher CleanYourTV se zachováním Oneplay a plánem návratu. Použij pro pomalý operátorský launcher, tlačítko Domů, probouzení nebo chyby streamů na těchto boxech; kompatibilitu vždy ověř podle modelu a firmware."
---

# O2 TV: bezpečný launcher

Pomoz uživateli získat samostatnou nabídku aplikací na operátorském Android TV
boxu. Pracuj na jeho skutečném zařízení, v rozsahu schváleném v této konverzaci.
Výchozí režim je čtecí diagnostika. Tento skill není automatický debloat.

## Kritická vlastnost O2/ZTE

U ověřeného O2TV_B866V2 s Androidem 12 obsahuje firmware kontrolu původního
systémového launcheru s větví vedoucí k továrnímu resetu. **Pro dosažení cíle
nevypínej ani neodinstalovávej `cz.o2.o2tv`, jeho HOME komponentu, ControlDevice
ani související služby ZTE.** Zachování ikony Oneplay nestačí; jeho balíček
i systémová HOME aktivita musí zůstat povolené.

Před změnami čti [ověřený profil a důkazy](references/device-profile.md).
Stejné marketingové jméno, jiné Android API nebo jiný firmware není ověřená
kompatibilita. U odlišného profilu pokračuj diagnostikou, změnový postup nejprve
posuď proti skutečnému zařízení. Neslibuj nulové riziko ani obnovu po resetu.

## Rozsah a souhlas

- IP/ADB identifikátor vždy převezmi od aktuálního uživatele nebo z jeho již
  autorizovaného spojení. V každém příkazu používej explicitní `adb -s SERIAL`.
  Nevynucuj spojení s prvním nalezeným zařízením a neprohledávej celou síť.
- Autorizace ADB a ruční instalace aplikace nejsou souhlas s přístupností,
  změnou Domů, probouzením nebo odebíráním aplikací. Souhlas, který již pokrývá
  konkrétní kroky a návrat, respektuj; neopakuj tutéž žádost.
- Novou změnu předlož konkrétně: dotčený balíček/nastavení, potřebné oprávnění,
  kontrola funkčnosti a návrat. Potvrzení funkčního testu není další žádost
  o souhlas s již schváleným krokem.
- Nepoužívej root, firmware flash, `pm clear`, factory/test menu nebo plošnou
  obnovu nastavení. Nespouštěj projektový instalační/debloat skript jako celek.
- Na neznámém firmware nezobecňuj výsledky jednoho boxu. Při odmítnuté instalaci
  ochranu neobcházej. Při problému se zastav a proveď schválený úzký návrat.

## Postup podle požadavku

### 1. Připojení, diagnostika a záloha

Ověř ADB z oficiálních Platform Tools, spojení autorizované uživatelem, přesný
model, build fingerprint, Android API, ABI a aktuální HOME. Na TV musí uživatel
sám potvrdit případnou výzvu k ladění. Nikdy nesnižuj zabezpečení ADB kvůli spojení.

Zaznamenej RAM, CPU, dostupné /data, teplotu, aplikace, verze, povolené komponenty,
HOME, preferred activities, přístupnost a oprávnění. Nezaměňuj obsazenou RAM
s nedostatkem RAM ani plnou read-only systémovou partition s plným /data.
Odliš start procesu, první vykreslení, načtení obsahu a první přehrané video.

Pro čtecí snímek použij [scripts/collect_android_tv.py](scripts/collect_android_tv.py):

```text
python scripts/collect_android_tv.py --adb C:\Android\platform-tools\adb.exe --serial ADRESA_BOXU:5555 --out C:\TV-backup\snimek-001 --profile baseline
```

V příkladu nahraď cestu, `ADRESA_BOXU` i cílový adresář skutečnými hodnotami;
pro názvy s mezerami použij uvozovky. Při potřebě zálohy instalačních souborů
přidej `--copy-apk cz.o2.o2tv --copy-apk com.gathin.tvhome`; druhý balíček jen
pokud už existuje. `--zip` vytvoří a ověří lokální archiv. Nový výstupní adresář
je povinný. Skript se nepřipojuje k neautorizovaným zařízením, nic na TV nemění
a nemá žádný režim instalace, resetu nebo vzdáleného odesílání.

Záloha dostupné konfigurace a APK **není obraz flash**. Nezajišťuje obnovu
přihlášení, soukromých dat aplikací, párovacích tajemství ani DRM klíčů.
Ověřený hash není funkční test obnovy. Snímky mohou obsahovat osobní
identifikátory, citlivé URL a tokeny vypsané do logů: uchovej je lokálně
a nesdílej je jako součást tohoto skillu.

### 2. Samostatné ruční spuštění launcheru

Čti [instalaci, kontroly a návrat](references/install-and-rollback.md).
Zkontroluj konkrétní zdrojový commit CleanYourTV a výsledné APK. Nejprve
nainstaluj pouze základní launcher, bez doplňků a bez grantů, a spusť jej
explicitně jako aplikaci. Původní HOME nech beze změny. Potvrď vykreslení,
skutečný ovladač a shodu nastavení před/po.

### 3. Domů, potom probouzení

Pouze ve schváleném rozsahu nastav nejprve `home_long_press_home=true`
a povol jen `com.gathin.tvhome/.HomeKeyService`. Probouzení zůstává vypnuté.
Ověř fyzický krátký/dlouhý Domů, Oneplay z ikony včetně přehrávání, Zpět,
Menu/Nastavení a podržení hlasitosti. ADB simulace nenahrazuje tento test.

Teprve po úspěchu zapni `power_on_home_always=true`. Ověř několik probuzení,
včetně návratu z Oneplay a jiné aplikace, a sleduj výsledek 30–60 sekund.
U restartu eviduj přesnou variantu APK: restart před poslední aktualizací
není důkazem chování poslední verze. Restart prováděj v dohodnutém rozsahu.

`stock_home_redirect` musí zůstat prázdné: Oneplay má stejnou aktivitu pro
HOME i otevření z ikony. Trvalé přesměrování by mohlo znemožnit jeho použití.
Nepovoluj `WRITE_SECURE_SETTINGS`, polohu, notification listener, InputKeyService
ani ServiceRepair. Stávající cizí služby přístupnosti vždy zachovej.

Výsledkem může být jiná viditelná domovská obrazovka. **Neslibuj, že firmware
přestane spouštět proces Oneplay na pozadí.** Pokud probouzení přebije pozdější
start Oneplay nebo přestanou fungovat tlačítka, vrať schválené změny; nerozšiřuj
automaticky oprávnění ani zásahy do operátorských služeb.

### 4. Občasné chyby streamu

Čti [diagnostiku přehrávání](references/streaming-diagnostics.md). Rozliš chybu
videa při stále otevřené aplikaci od pádu procesu či restartu boxu. Záznamy
sbírej ideálně při chybě před restartem pomocí `--profile streaming`.
Přehrávací chybu neřeš automatickým debloatem nebo mazáním dat.

## Uzavření práce

Uveď přesné změny, zachované systémové komponenty, ověřené testy a jejich limity,
umístění zálohy a konkrétní návrat. Neoznačuj čekající test za hotový. Odděl
uživatelské potvrzení od vlastního měření. Další použití či ukončení síťového
ADB dohodni podle potřeb diagnostiky a dosavadního souhlasu; neměň oprávnění
navíc. Tento skill nesmí zveřejnit uživatelovy záznamy, APK, klíče ani hlášení.
