# Občasné chyby přehrávání

Nejprve zjisti, zda (a) skončí video s hlášením a aplikace běží dál,
(b) aplikace zmizí do launcheru, nebo (c) zamrzne/restartuje se box.
Ptej se na aplikaci, přesný text/kód, čas, jeden/více titulů a jednu/více služeb.
Uživatelovo „internet funguje“ respektuj, ale rozliš běžnou konektivitu,
krátké výpadky a cestu k serveru konkrétní služby.

Když aplikace běží dál, samotný ApplicationExitInfo obvykle chybu přehrávače
nevysvětlí. Hledej časově odpovídající MediaCodec/ExoPlayer/Crypto/MediaDrm chyby,
licenční odpovědi, stav HDMI/HDCP, dostupnost dekodéru, paměť a teplotu.
Výpadek napříč aplikacemi je důvod zkoumat společné vrstvy; není sám o sobě
důkazem závady DRM, RAM nebo internetu.

Použij čtecí sběrač s `--profile streaming --app BALÍČEK_APLIKACE` ideálně
ihned při chybě a před restartem. `--app` lze opakovat; bez této volby se
čtou výpisy Disney+ a HBO. Zkontroluj všechny položky `failures` v metadata,
nejen návratový kód. `required_reads_complete` popisuje nezbytná čtení daného
profilu; `all_requested_reads_complete` zahrnuje i volitelná rozhraní.
Ani kompletní sběr sám nepotvrzuje bezpečnost následných změn.
Záznam z období normálního fungování nepředstavuj jako diagnózu
události staré několik dnů. Některé služby a sysfs soubory firmware nepovolí
číst; `Permission denied` nebo neexistující dumpsys služba není závada zařízení.
Na referenčním firmware se služba jmenuje `drm.drmManager`, nikoli `media.drm`.

Vodítka pro interpretaci:

- `importance=400`, `TRIM EMPTY` a `TOO MANY EMPTY PROCS` v historii
  neaktivních procesů nejsou důkazem přerušení právě sledovaného videa.
  Také záznam `LOW_MEMORY` vztahuj ke konkrétnímu procesu a času chyby.
- Paměť, teplota a čítače Ethernetu v pořádku po restartu nevylučují
  dřívější problém. Aktuální HAL teplotu nepleť s dřívější cached teplotou.
- Pokud chyba není zachycena, lze s uživatelem dohodnout čtecí sběr při
  příštím výskytu před restartem, bez trvalého sledování nebo automatických oprav.

Bez důkazu neměň DNS, MTU, rozlišení, HDCP, DRM, firmware nebo data aplikací.
Nezapínej trvalý sběr logů bez odpovídajícího požadavku. Zvol cílený další
test až podle kódu chyby a časově odpovídajících záznamů. Zachovej původní
problém jako nevyřešený, pokud se ho nepodařilo reprodukovat nebo doložit.

Oficiální zdroje pro interpretaci (ověř podle konkrétní chyby):

- https://developer.android.com/reference/android/media/MediaCodec.CodecException
- https://developer.android.com/reference/android/media/MediaCodec.CryptoException
- https://developer.android.com/reference/android/app/ApplicationExitInfo
- https://help.disneyplus.com/article/disneyplus-en-il-streaming-issues
