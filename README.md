# O2 TV: bezpečný launcher

Český skill pro Codex: čtecí diagnostika O2/ZTE Android TV boxu přes ADB,
samostatný launcher CleanYourTV a úzký návrat změn. Oneplay i operátorské
systémové komponenty zůstávají povolené.

Referenční zařízení je ZTE O2TV_B866V2 s Androidem 12 a firmwarem
V82811306.3113. Jiný model nebo firmware vyžaduje nové posouzení.
Nejde o oficiální nástroj O2, ZTE ani projektu CleanYourTV.

## Použití

1. Zkopíruj tuto složku pod názvem `o2-tv-safe-launcher` do
   `~/.codex/skills/` (na Windows do `.codex\skills\` ve svém uživatelském profilu).
2. V novém chatu Codexu použij `$o2-tv-safe-launcher`, uveď IP svého boxu
   a požadovaný rozsah práce. Začni čtecí diagnostikou.
3. ADB autorizuj na vlastní TV. Změny launcheru, přístupnosti a probouzení
   schvaluj podle konkrétního návrhu; samotné připojení není jejich schválením.

Postup a odkazy na podrobnosti jsou v [SKILL.md](SKILL.md).
Volitelný [čtecí sběrač](scripts/collect_android_tv.py) potřebuje Python 3.9+
a dostupné ADB; nepoužívá další Python knihovny. Nástroje, APK ani klíče
nejsou součástí tohoto repozitáře.

## Soukromí a publikování

Tento balíček obsahuje pouze návod, metadata skillu a zdrojový kód sběrače.
Model, build fingerprint, verze aplikací a zdrojový commit slouží k ověření
kompatibility. Neobsahuje skutečnou síťovou adresu boxu, identifikátory
konkrétního kusu, účty, hesla, klíče, obrázky obrazovky ani diagnostické výstupy.

**Výstupy sběrače jsou soukromé.** Mohou obsahovat IP/MAC adresy,
identifikátory zařízení, URL, údaje související s účty a tokeny vypsané do logů.
Sběrač je ukládá lokálně; neanonymizuje je. Výstupní adresář `--out` zvol
mimo repozitář a nesdílej nezkontrolované diagnostické archivy ani APK zálohy.

`.gitignore` povoluje pouze konkrétní veřejné soubory. Neodstraňuje citlivé
údaje z již vytvořené historie a nezabrání vynucenému přidání přes `git add -f`.
Před zveřejněním zkontroluj také autora a e-mail Git commitů. Tento balíček
neobsahuje žádnou historii Git ani nastavení vzdáleného repozitáře.

## Hranice postupu

- U referenčního firmwaru může vypnutí původního systémového HOME vyvolat
  tovární reset. Skill proto zachovává Oneplay a systémovou HOME aktivitu.
- Záloha konfigurace a APK není obraz firmware a nezaručuje obnovu přihlášení,
  soukromých dat aplikací, párování nebo DRM klíčů.
- Projektové instalační a debloat skripty se nespouštějí automaticky.
  Každá změna musí mít odpovídající souhlas, kontrolu a plán návratu.

Zdroj launcheru: [CleanYourTV](https://github.com/Gathin23/cleanyourtv).
