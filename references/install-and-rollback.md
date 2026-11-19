# Instalace, aktivace a návrat

Čti až pro přípravu konkrétních schválených změn. Přímé příkazy musí mít
aktuální explicitní ADB serial; níže uvedené shell fragmenty jsou jednotlivé
kroky, nikoli skript k hromadnému spuštění. Před aplikací přečti aktuální stav.

## Příprava a záloha

Ulož přesnou přítomnost i hodnotu změněných klíčů, seznam povolených služeb,
HOME, preferred activities, stavy balíčků/komponent a APK původního launcheru.
`enabled=0` znamená výchozí stav, ne zakázanou aplikaci. `settings get` vrací
`null` i pro některé nejasné situace; pro rozdíl chybějící klíč / prázdný klíč
použij `settings list`. Zálohu ověř hashi a čitelností archivu, neslibuj data aplikací.

Před každým krokem ověř:

- Správné zařízení a stejný firmware; ADB je dostupné.
- `cz.o2.o2tv/.MainActivity` je stále systémové HOME.
- Oneplay, jeho HOME komponenta a `com.control.device` jsou zapnuté; žádné
  další původní balíčky se oproti snímku nezměnily.
- Instalační APK má očekávanou identitu, hash a podpis. Při aktualizaci musí
  být podepsané stejným místním klíčem jako nainstalovaná varianta.
- Nejsou přehlédnuté jiné služby přístupnosti. Jejich seznam se nikdy nesmí
  nahradit jedinou vlastní službou bez zachování ostatních položek.

## Zdroj, sestavení a instalace

Použij oficiální repozitář CleanYourTV. Zaznamenej a zkontroluj konkrétní commit;
zjištění z referenčního commitu se nepřenáší na novější kód automaticky.
Nepouštěj `build-and-install.ps1` / `.sh`: kombinují sestavení s granty,
preferencí HOME a deaktivací původního launcheru. Ani volba `StockLauncher none`
není zárukou zachování všech nastavení a oprávnění.

Pro referenční commit se osvědčilo JDK 17, Gradle 8.9, Android SDK platform 34
a Build Tools 34.0.0. Verze odvoď z prověřených build souborů. Nástroje ukládej
přenosně do pracovní složky; ověř oficiální zdroj a publikované součty.
Gradle wrapper i distribuci ověř před spuštěním. Zkompiluj pouze základní app:
`testReleaseUnitTest lintRelease assembleRelease`. Kontrola se vztahuje na
výsledné APK, ne jen na zdrojový AndroidManifest.xml.

Zkontroluj `aapt dump badging`, `aapt dump permissions`, sloučený manifest,
`apksigner verify --verbose --print-certs`, SHA-256 a limity projektu.
Referenční build používá lokální vývojový klíč i pro release; uchovej ho
soukromě pro další aktualizace. Certifikát s názvem Android Debug není důkaz
původu od autora. Nepoužívej APK od náhodného třetího distributora.

Na Windows:

- Nenazývej proměnnou `$home`; PowerShell používá vestavěné `$HOME`.
- Pro Python pomocné nástroje s českým textem použij UTF-8 režim.
- Vyhni se konfliktu ANDROID_USER_HOME a zastaralého ANDROID_SDK_HOME;
  všechny cache a klíče směruj vědomě do pracovní složky.
- Novější Google CLI může mít jiné přepínače než starý sdkmanager. Ověř aktuální
  oficiální dokumentaci. Nebouraj Windows Application Control kvůli nástroji.
  Při přímé přípravě SDK z ověřených archivů rozliš základní API 34 od rozšíření
  android-34-extN; novější repository XML uvádí base-extension.
- Nepřijímej automaticky nové telemetrické nebo systémové instalace mimo úkol.

První instalace používá `adb -s SERIAL install --user 0 APK`, bez `-g`.
Pokud balíček už existuje, nejprve ho zazálohuj a posuď aktualizaci. `-r`
je pro schválenou aktualizaci vlastního známého APK; nikdy neřeš kolizi
odinstalováním aplikace se ztrátou dat. Při odmítnutí verifikace skonči.

Ruční spuštění:

```text
am start -W -a android.intent.action.MAIN -c android.intent.category.LEANBACK_LAUNCHER -n com.gathin.tvhome/.MainActivity
```

Použití explicitní komponenty nepředstavuje změnu systémového HOME.
První test nevyžaduje přístupnost, polohu, notification listener ani změnu Domů.

## Dvě oddělené konfigurace

| Volba | Test Domů | Test probuzení |
|---|---|---|
| home_long_press_home | true | true |
| power_on_home_always | false | true |
| power_on_home | false | false |
| stock_home_redirect | prázdné | prázdné |
| restore_key_services | false | false |
| boot_to_live_tv / open_on_start_choice | false | false |
| consume_volume_keys | false | false |

Preferuj změnu pouze uvedených resource bool hodnot v kopii nebo kontrolovaném
checkoutu zdrojů, sestavení, uložení diffu a aktualizaci stejným podpisem.
Původní zdroje a APK zachovej. Nový `config.json` přes mechanismus témat může
v tomto commitu resetovat část vzhledových preferencí; nepřepisuj uživatelův
existující motiv. Před volbou zdroje nastavení zkontroluj jeho případné override.

HomeKeyService umí filtrovat klávesy globálně. Kromě HOME v této implementaci
obsluhuje ALL_APPS a SETTINGS. Netvrď, že dostává jen tlačítko Domů. Bez
stock_home_redirect nepotřebuje sledovat všechny změny oken.

Aktivace přes ADB vyžaduje změnu secure seznamu služeb přístupnosti a zapnutí
`accessibility_enabled`. K současnému seznamu přidej přesně
`com.gathin.tvhome/com.gathin.tvhome.HomeKeyService`, idempotentně, se zachováním
ostatních služeb. Není potřeba udělit launcheru WRITE_SECURE_SETTINGS: změnu
provádí autorizovaný ADB shell. Nic dalšího negrantuj.

Pokud je globální přístupnost vypnutá, ale seznam obsahuje cizí služby,
nejprve zjisti jejich skutečný stav. Zapnutí globálního switche by mohlo
znovu aktivovat i je. Tento rozpor neřeš smazáním seznamu ani nevyžádaným
zapnutím jiných služeb; vyjasni stav a rozsah s uživatelem.

Ověř nejen enabled seznam, ale skutečné navázání služby v `dumpsys accessibility`
a `dumpsys activity services com.gathin.tvhome`. Update APK může službu odpojit;
po schválené aktualizaci ověř její stav znovu. Nepoužívej `am force-stop` jako
test: může vypnout služby přístupnosti. Bez vlastního písemného záznamu
nezaměňuj odpojení služby s povolením dodatečné automatické opravy.

### Test Domů

Uživatel fyzicky otevře Oneplay z ikony, ověří video a zkusí krátké i dlouhé
Domů. Následují šipky, Zpět, Menu/Nastavení a podržení hlasitosti. Zároveň
porovnej snapshot. Přidaná služba může na některých firmwarech změnit
opakování tlačítek, i když samotná hlasitost nemá přemapování.

### Test probouzení

Z referenčního kódu plyne jednorázový pokus o Home asi 800 ms po SCREEN_ON.
Další klávesa jej může zrušit a OEM může Oneplay spustit později. Proto
sleduj několik cyklů i po 30–60 s a nepřidávej `stock_home_redirect` jako
automatickou opravu. Služba musí přežít nebo být znovu navázaná při probuzení.
Ověř ruční Oneplay i po této změně. Případný restart vztahuj ke konkrétnímu
APK a chronologii; úspěšné volání `am start -W` není úplný test videa/DRM.

## Úzký návrat při potížích

1. Odstraň jen vlastní HomeKeyService ze současného seznamu přístupnosti;
   zachovej ostatní služby včetně těch přidaných mezitím. Přístupnost nevypínej,
   pokud ji používá jiná služba. Jinak obnov skutečně zaznamenanou původní
   přítomnost a hodnotu switche, která v referenčním případě byla 0.
2. Obnov pouze změněnou konfiguraci / původní podepsané APK s `install -r`,
   bez mazání dat. Pokud instalační chyba nechala původní APK nedotčené,
   zbytečně ho nepřepisuj. Nepoužívej plošný restore skript projektu.
3. Obnov pouze vlastní změny dotčených settings klíčů. Pokud se mezitím
   nezměnil stav jiných služeb, obnov přesnou původní přítomnost a hodnoty.
   Pokud přibyla jiná služba, zachování jejího aktuálního stavu má přednost
   před doslovným přepsáním původním seznamem. Prázdná hodnota je jiná než
   chybějící klíč; chybějící se maže, neplní textem `null`.
4. Otevři explicitně `cz.o2.o2tv/.MainActivity`, ověř původní HOME a
   funkčnost skutečným ovladačem i videem. Znovu zaznamenej stav.

Oneplay ani jeho komponenty se během tohoto workflow nikdy nevypínají.
Při ztrátě ADB nepokračuj neviditelnými zásahy. Záloha konfigurace není
zaručená cesta zpět z nefunkčního systému nebo po továrním resetu.
