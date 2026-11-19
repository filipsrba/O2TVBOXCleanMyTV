# Ověřený profil a hranice použitelnosti

Níže jsou technické charakteristiky jednoho referenčního zařízení,
nikoli seznam certifikované kompatibility pro všechny O2/ZTE boxy.

| Položka | Pozorovaná hodnota |
|---|---|
| Model / product device | ZTE O2 TV Box / `O2TV_B866V2` |
| Marketingové označení | ZXV10 B866V2 |
| Android | 12, API 31, uživatelský build |
| Firmware | `V82811306.3113` |
| Fingerprint | `O2/O2TV_B866V2/O2TV_B866V2:12/SC/V82811306.3113:user/release-keys` |
| ABI | armeabi-v7a / armeabi |
| Hardware | Amlogic S905X2, 4× Cortex-A53, přibližně 2 GB RAM |
| Původní HOME a TV aktivita | `cz.o2.o2tv/.MainActivity` |
| Oneplay | 4.0.42 v době zkoušky |
| Nový launcher | `com.gathin.tvhome`, Home 3.5, versionCode 14 |
| Zdrojový commit | `3ece7766ad5d6af79a2c4dd73e77b4b9623dfeca` |
| CleanYourTV min/target SDK | 26 / 34 v tomto commitu |

## Proč se Oneplay nesmí vypínat

Statická analýza souborů `/system/system_ext/app/ControlDevice/ControlDevice.apk`
a `/system/framework/FrameworkCustomization.jar` přímo z tohoto zařízení zjistila:

1. `PMSImpl.getBestActivity` po dokončeném setupu preferuje systémovou HOME
   aplikaci. Výjimky pro jiné trhy neodpovídaly zkoumanému boxu.
2. `ZteKeyInterceptorReceiver.Q` hledá HOME aplikaci s příznakem SYSTEM;
   ignoruje `com.android.tv.settings` / FallbackHome a setupwraith. Tu zde
   představuje Oneplay, nikoli dodatečně instalovaný launcher.
3. Plánovaná úloha `F.run` kontroluje, zda je vybraný balíček nainstalovaný
   a zapnutý. V negativní větvi je reset produktové konfigurace a broadcast
   `android.intent.action.FACTORY_RESET` pro balíček `android`.
4. Časovač byl plánován po 10 sekundách a opakovaně po 30 minutách.
   Provozní logy skutečně ukazovaly kontrolu Oneplay s `installed=true`,
   `enabled=true`, `is normal=true`, včetně kontroly po uživatelském restartu.

Destruktivní větev nebyla spuštěna. Celá dekompilace nebyla bezchybná;
relevantní větev byla čitelná a podpořená provozními logy. Nedělej z tohoto
zjištění absolutní bezpečnostní záruku. Kopie proprietárního firmware ani
uživatelské logy nejsou součástí skillu. Při neznámé verzi získej důkazy
čtecím způsobem a nespoléhej na podobnost názvu zařízení.

Projektové návody pro B866F nebo B866V2K s jiným Androidem jsou pouze vodítko.
Nepřenášej automaticky jejich příkazy pro přebírání HOME nebo vypínání balíčků.

## Co skutečně prošlo zkouškou

- Ručně otevřený základní launcher fungoval plynule.
- Po změně jediného resource flagu `home_long_press_home` a aktivaci
  HomeKeyService uživatel potvrdil krátké i dlouhé Domů, přehrávání Oneplay
  z ikony a ostatní ovládání včetně podržení hlasitosti.
- Poté byla přidána funkce `power_on_home_always`. Uživatel hlásil funkční
  probouzení i restart. Z časové osy ale restart předcházel instalaci poslední
  varianty APK: nelze jej nezávisle vykazovat jako restart finální varianty.
- Původní HOME, jeho preference, stav Oneplay a ControlDevice byly zachovány.
  V secure nastavení přibyly pouze hodnoty aktivující HomeKeyService.
- Nebyla prokázána dlouhodobá spolehlivost ani odstranění automatického
  spouštění procesu Oneplay na pozadí. Chyby streamů nebyly tímto vyřešeny.

## Soukromí kontrolovaného launcheru

Ve zdrojovém i výsledném manifestu nebyl INTERNET, RECORD_AUDIO nebo CAMERA.
Deklarované ACCESS_FINE_LOCATION a WRITE_SECURE_SETTINGS nebyly uděleny.
Normální ACCESS_NETWORK_STATE a ACCESS_WIFI_STATE přiděluje Android při instalaci.
Služba přístupnosti měla capability pro filtrování kláves, bez čtení stromu
oken a bez odběru událostí oken při prázdném stock_home_redirect.

To není audit všech tranzitivních závislostí ani absolutní důkaz nemožnosti
úniku přes jiné aplikace či zranitelnost systému. Doplňky jsou samostatné
aplikace, mohou mít INTERNET a nejsou zahrnuté v tomto závěru.

Primární projekt: https://github.com/Gathin23/cleanyourtv
Kontrolovaný zdroj: https://github.com/Gathin23/cleanyourtv/tree/3ece7766ad5d6af79a2c4dd73e77b4b9623dfeca
Android AccessibilityService: https://developer.android.com/reference/android/accessibilityservice/AccessibilityService
