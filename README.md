# PAC-M'S VS PETABYTE

Pac-man inspirovana hra vytvorena v Pythonu pomoci knihovny PyGame. Hrac prochazi bludistem, sbira body, vyhyba se ruznym typum nepratel a snazi se vycistit cely level.

## Spusteni

dist/PAC-M'S VS PETABYTE.exe

## Ovladani

- Pohyb: sipky, WASD nebo obe varianty podle nastaveni
- `Esc`: pauza ve hre
- V menu lze vybrat level, nastavit ovladani a vybrat skin hrace

## Herni obsah

Projekt obsahuje 3 levely definovane v `core/level.py`. Levely se skladaji z mapy znaku:

- `#` - zed
- `.` - bod
- `O` - specialni boost bod
- `P` - start hrace
- `E` - spawn nepritele

Ve hre jsou 4 hracske skiny:

- Bejcek
- Majkl
- Komi
- Seda

## Typy nepratel

Hra obsahuje 5 ruznych typu nepratel. Vsechny dedi ze zakladni tridy `Enemy`, ale kazdy typ prepisuje metodu `choose_target()`, diky cemu se chova jinak.

- `ChaserEnemy` - lovec, jde primo po hraci
- `PredatorEnemy` - predator, miri pred hrace podle smeru jeho pohybu
- `WandererEnemy` - bloudil, pohybuje se po nahodnych bodech mapy
- `GuardEnemy` - strazce, hlida okoli sveho spawnu a pri priblizeni zacne hrace honit
- `CowardEnemy` - zbabelec, pri priblizeni hrace utika, jinak ho sleduje

Rozlozeni nepratel podle levelu:

- Level 1: `ChaserEnemy`
- Level 2: `PredatorEnemy`, `WandererEnemy`
- Level 3: `GuardEnemy`, `CowardEnemy`, `ChaserEnemy`

## Struktura projektu

```text
pololet-projekt/
|-- main.py                  # vstupni bod aplikace
|-- PacMsVsPetabyte.spec     # PyInstaller konfigurace pro build
|-- README.md                # dokumentace projektu
|-- config/
|   |-- constants.py         # konstanty hry
|-- core/
|   |-- game.py              # hlavni herni trida Game
|   |-- level.py             # trida Level a definice map
|-- entities/
|   |-- player.py            # trida Player
|   |-- enemy.py             # Enemy a konkretni typy nepratel
|-- ui/
|   |-- screens.py           # menu, nastaveni, pauza, info, win/death obrazovky
|-- utils/
|   |-- resources.py         # nacitani assetu pro Python i .exe build
|-- imgs/                    # obrazky, skiny, ikona a pozadi
|-- dist/                    # vystupni .exe soubor po buildu
|-- build/                   # pomocne soubory PyInstalleru
```

## OOP navrh

Projekt je rozdeleny do trid podle odpovednosti:

- `Game` ridi hlavni herni smycku, spousteni levelu, reset levelu, kolize a vykreslovani.
- `UI` se stara o hlavni menu, nastaveni, vyber levelu, info obrazovku, pauzu, obrazovku smrti a obrazovku vyhry.
- `Level` uchovava mapu, pocita body, zjistuje zdi a prevadi souradnice mezi gridem a pixely.
- `Player` reprezentuje hrace, jeho pohyb, skin, score a sbirani bodu.
- `Enemy` je zakladni trida pro nepratele. Obsahuje spolecny pohyb, pathfinding a kolize.
- `ChaserEnemy`, `PredatorEnemy`, `WandererEnemy`, `GuardEnemy` a `CowardEnemy` jsou konkretni potomci `Enemy`.

### Dedicnost

```text
pygame.sprite.Sprite
|-- Player
|-- Enemy
    |-- ChaserEnemy
    |-- PredatorEnemy
    |-- WandererEnemy
    |-- GuardEnemy
    |-- CowardEnemy
```

### Polymorfismus

Polymorfismus probiha hlavne u nepratel:

- `Game` vytvari ruzne tridy nepratel podle levelu.
- Vsechny enemy objekty se v herni smycce pouzivaji stejne pres `update(dt, level, player)`.
- Kazda podtrida `Enemy` ma vlastni implementaci `choose_target()`.
- Diky tomu nemusi `Game` resit konkretni chovani nepratel, pouze vola stejne metody.

## Splneni zadani

- Minimalne dva komplexnejsi levely: splneno, hra obsahuje 3 levely.
- Nejmene 5 druhu nepratel: splneno.
- Vyber herniho skinu: splneno, hra obsahuje 4 skiny.
- Herni menu, nastaveni a pauza: splneno.
- PyGame: splneno.
- Dokumentace v README.md: splneno.
- OOP struktura: splneno, projekt je rozdeleny do logickych slozek a enemy vyuzivaji dedicnost a polymorfismus.
- .exe build s ikonou: splneno po spusteni PyInstaller buildu, vystup je v `dist/`.
