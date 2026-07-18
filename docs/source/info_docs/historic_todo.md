# TODO history

::::{dropdown} Odmítnout řetězce sousedních inserterů
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Grid, Routing, Tests`

Kontrola spojení považovala sousední insertery za souvislou transportní cestu.
Ve Factorio si ale dva insertery nemohou předat materiál přímo mezi sebou, takže
takový layout nesmí projít validací.


**Vytvořeno:** 2026-07-11
**Vyřešeno:** 2026-07-11
**Historické soubory:** `src/factory_creator/grid.py`,
`tests/factory_creator/test_grid.py`
::::

## Aktuální tasky

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} Přidat přepínač podrobnosti výpisu evoluce
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`GUI, Evolution`

GUI má nabídnout volbu, zda během evoluce zobrazovat pouze průběh výpočtu,
nebo také důvody selhání jednotlivých kandidátů včetně tracebacků.


+++
**Vytvořeno:** 2026-07-11
**Umístění:** `src/factory_creator/evolution.py:11`
:::

:::{grid-item-card} Rozložit fitness na pojmenované složky
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Evolution, Fitness`

Fitness je nyní počítána jako jedno výsledné číslo s vahami zapsanými přímo
ve funkci. Výsledek vyhodnocení by měl obsahovat pojmenované složky, například
plochu, počet použitých polí, vzdálenost od středu, cenu inserterů, zarovnání
pásů a validitu spojení, spolu s celkovým skóre. Váhy jednotlivých složek mají
být přesunuty do konfigurace, aby šlo fitness snáze ladit, porovnávat a později
nastavovat z GUI.


+++
**Vytvořeno:** 2026-07-18
**Umístění:** `src/factory_creator/evolution.py:254`
:::

:::{grid-item-card} Načítat reálné rozměry strojů
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Loader`

Loader zatím používá pevně zadané rozměry továren místo dat z receptů nebo
entit.


+++
**Vytvořeno:** 2026-03-22
**Umístění:** `src/factory_creator/factory_loader.py:54`
:::

:::{grid-item-card} Přidat vlastní chybu pro neplatný vstup
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Loader`

Validace receptů pořád spoléhá na obecnou runtime chybu; chybí doménová výjimka
pro špatný vstup.


+++
**Vytvořeno:** 2026-03-22
**Umístění:** `src/factory_creator/factory_loader.py:115`
:::

:::{grid-item-card} Zjednodušit formát výsledků ve vstupních datech
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Loader`

Loader řeší výsledky jako pole, i když by pro běžné recepty dával smysl jeden
objekt.


+++
**Vytvořeno:** 2026-04-16
**Umístění:** `src/factory_creator/factory_loader.py:48`
:::

:::{grid-item-card} Určit terminalitu materiálů konfigurovatelně
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Loader`

Plate materiály jsou natvrdo považované za terminální; mělo by to být odvozené z
dat nebo parametru.


+++
**Vytvořeno:** 2026-04-16
**Umístění:** `src/factory_creator/factory_loader.py:39`
:::

:::{grid-item-card} Zpřehlednit výpočet dependency graphu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

Část výpočtu toku surovin je stále těžší čitelná a zaslouží rozdělení nebo
pojmenování kroků.


+++
**Vytvořeno:** 2026-04-17
**Umístění:** `src/factory_creator/dependency_graph.py:241`
:::

:::{grid-item-card} Dopsat balení projektu přes `pyproject.toml`
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Packaging`

Projekt se stále spouští přes explicitní `src.factory_creator...` importy místo
instalace v editable režimu.


+++
**Vytvořeno:** 2026-04-17
**Umístění:** `main.py:8`
:::

:::{grid-item-card} Dořešit elektrickou spotřebu v layoutu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

Layout zatím řeší výrobní strukturu, ale neplánuje elektrickou infrastrukturu
ani její dopady.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/dependency_graph.py:12`
:::

:::{grid-item-card} Opravit model splitterů v grafu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

Splitter neumí obecně reprezentovat rozdělení jednoho pásu do více výstupů bez
zjednodušení.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/dependency_graph.py:90`
:::

:::{grid-item-card} Revidovat minimální rychlost všech stage
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

Výpočet nutí každou stage vyrábět alespoň jednu jednotku za periodu, což může
zbytečně nafukovat továrnu.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/dependency_graph.py:237`
:::

:::{grid-item-card} Přesunout pomocnou metodu z dependency graphu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

V grafové vrstvě zůstává metoda, která pravděpodobně patří do obecnější utility
nebo modelové vrstvy.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/dependency_graph.py:303`
:::

:::{grid-item-card} Doplnit referenci v dependency graphu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

V grafu chybí přesnější odkaz nebo identifikátor na související prvek.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/dependency_graph.py:134`
:::

:::{grid-item-card} Dokončit export reálných hodnot do JSON reprezentace
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Export`

JSON export obsahuje placeholder, který má být nahrazen skutečnými hodnotami.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/export/json_matrix_representation.py:16`
:::

:::{grid-item-card} Zvážit nedeterministické vrstvení grafu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Současné BFS vrstvení dává jeden deterministický layout; pro hledání lepších
layoutů by se hodila variabilita.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/graph_to_matrix.py:162`
:::

:::{grid-item-card} Navrhnout vlastní BFS pro hloubky uzlů
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Hloubky uzlů by mohly být přiřazované vlastním algoritmem, aby vznikaly různé
planární varianty.


+++
**Vytvořeno:** 2026-04-18
**Umístění:** `src/factory_creator/graph_to_matrix.py:165`
:::

:::{grid-item-card} Zvážit vestavěné vrstvení z NetworkX
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Ruční výpočet vrstev by možná šel nahradit standardní funkcí nad grafem.


+++
**Vytvořeno:** 2026-04-19
**Umístění:** `src/factory_creator/graph_to_matrix.py:178`
:::

:::{grid-item-card} Upravit dočasnou opravu ve smyčce
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

V dependency graphu zůstává dočasný zásah, který má být vyčištěn a opraven přímo
v iteraci.


+++
**Vytvořeno:** 2026-05-13
**Umístění:** `src/factory_creator/dependency_graph.py:96`
:::

:::{grid-item-card} Zkrášlit a zjednodušit část transformace grafu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Část `graph_to_matrix` funguje, ale forma kódu je pořád provizorní.


+++
**Vytvořeno:** 2026-05-13
**Umístění:** `src/factory_creator/graph_to_matrix.py:183`
:::

:::{grid-item-card} Přidat mapování identifikátorů na objekty gridu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Grid`

Grid má identifikátory prvků, ale chybí pohodlná cesta zpět na konkrétní objekt.


+++
**Vytvořeno:** 2026-07-04
**Umístění:** `src/factory_creator/grid.py:10`
:::

:::{grid-item-card} Ověřit rotaci inserterů při JSON exportu
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Export`

Export do Factorio reprezentace možná musí rotovat insertery podle směru toku.


+++
**Vytvořeno:** 2026-07-04
**Umístění:** `src/factory_creator/export/json_matrix_representation.py:50`
:::

:::{grid-item-card} Zlepšit estetiku výběru nejkratší cesty
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

A\* teď bere libovolnou nejkratší cestu; pro hezčí factory layout by měl
preferovat stabilnější tvary.


+++
**Vytvořeno:** 2026-07-04
**Umístění:** `src/factory_creator/graph_to_matrix.py:474`
:::

:::{grid-item-card} Vytáhnout opakovanou logiku do funkce
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

V `graph_to_matrix` zůstává blok, který si říká o izolovanou pomocnou funkci.


+++
**Vytvořeno:** 2026-07-05
**Umístění:** `src/factory_creator/graph_to_matrix.py:233`
:::

:::{grid-item-card} Dopracovat reopening pro penalizované A\*
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Korektní A\* s penalizacemi potřebuje umět znovu otevřít už navštívené stavy.


+++
**Vytvořeno:** 2026-07-05
**Umístění:** `src/factory_creator/graph_to_matrix.py:519`
:::

:::{grid-item-card} Odstranit dummy test
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing, Tests`

Test suite stále obsahuje úmyslně padající dummy assert.


+++
**Vytvořeno:** 2026-07-05
**Umístění:** `tests/graph_to_matrix_test.py:142`
:::

:::{grid-item-card} Přidat volbu fitness parametrů do GUI
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Evolution`

Uživatel by měl v GUI vybírat, které fitness metriky se použijí při evoluci
layoutu.


+++
**Vytvořeno:** 2026-07-05
**Umístění:** `src/factory_creator/evolution.py:232`
:::

:::{grid-item-card} Ošetřit cestu délky 2 speciálním inserterem
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Krátká cesta mezi prvky vyžaduje konkrétní typ inserteru, jinak může layout
generovat neplatné spojení.


+++
**Vytvořeno:** 2026-07-05
**Umístění:** `src/factory_creator/graph_to_matrix.py:369`
:::

:::{grid-item-card} Slučovat stejné typy mezivýrobků
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Dependency graph`

Seskupování stejných typů uzlů se nyní vztahuje jen na terminální suroviny.
Je potřeba podporovat také sloučení produkce mezivýrobků, například
`iron-gear-wheel` a `copper-cable`, na společný pás a její následné rozdělení
mezi více spotřebitelů.


+++
**Vytvořeno:** 2026-07-11
**Umístění:** `src/factory_creator/dependency_graph.py:83`
:::

:::{grid-item-card} Validovat párování podzemních pásů
:class-card: sd-shadow-sm sd-border-warning
:class-title: sd-text-warning

{bdg-warning}`open` {bdg-secondary}`Routing`

Po vytvoření layoutu je potřeba ověřit, že se každý endpoint podzemního pásu
ve Factorio blueprintu spojí se zamýšleným protějškem. Kontrola má zahrnout
kompatibilní směr, dvojici `input`/`output`, povolenou vzdálenost a případný
bližší kompatibilní endpoint, který by spojení zachytil.


+++
**Vytvořeno:** 2026-07-11
**Umístění:** `src/factory_creator/graph_to_matrix.py:480`
:::

::::

## Splněné tasky

::::{dropdown} Ověření existence vybraného souboru
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

První GUI poznámka k validaci, že uživatel skutečně vybral existující vstupní
soubor.


**Vytvořeno:** 2026-03-22
**Vyřešeno:** 2026-03-22
**Historické soubory:** `src/GUI/main_window.py`
::::

::::{dropdown} Validace existence souboru v GUI
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

Dlouhodobější verze kontroly vstupních cest v GUI po přesunech balíčků.


**Vytvořeno:** 2026-03-22
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/GUI/main_window.py`,
`src/factory_creator/GUI/main_window.py`,
`src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Doménová chyba pro chybějící ingredienci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Factory`

Factory model měl signalizovat chybějící ingredienci srozumitelnější výjimkou.


**Vytvořeno:** 2026-04-16
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory.py`, `src/factory_creator/factory.py`
::::

::::{dropdown} Spouštění výpočtu mimo hlavní GUI thread
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

GUI při výpočtu layoutu nemělo blokovat hlavní smyčku.


**Vytvořeno:** 2026-04-16
**Vyřešeno:** 2026-04-17
**Historické soubory:** `src/GUI/main_window.py`,
`src/factory_creator/GUI/main_window.py`
::::

::::{dropdown} Přechod ze zjednodušeného na plný dependency model
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Dependency graph, Factory`

Starší logika mezi zjednodušeným a nezjednodušeným grafem potřebovala sjednotit.


**Vytvořeno:** 2026-04-16
**Vyřešeno:** 2026-04-16
**Historické soubory:** `src/dependency_graph.py`, `src/factory.py`
::::

::::{dropdown} Přehodnotit minimální výkon stage
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Dependency graph`

Starší formulace stejného problému s povinnou minimální výrobou každé stage.


**Vytvořeno:** 2026-04-16
**Vyřešeno:** 2026-04-18
**Historické soubory:** `src/dependency_graph.py`,
`src/factory_creator/dependency_graph.py`
::::

::::{dropdown} Threadování výpočtu v novém GUI modulu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

Po přesunu GUI do balíčku zůstal úkol přesunout výpočet mimo UI thread.


**Vytvořeno:** 2026-04-17
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Skrýt výběr receptu po změně souboru
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

GUI mělo resetovat combobox receptů, když uživatel změní zdrojový soubor.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-04-19
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Nejdřív umístit budovy, potom pásy
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Layout algoritmus měl oddělit pokládání výrobních budov od následného routování
pásů.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Obecné úklidy v routování a GUI
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing, GUI`

Zastřešující poznámka k několika místům, kde byl kód stále jen provizorně lepší.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`,
`src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Vylepšit výjimky při routování
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Chybové stavy v `graph_to_matrix` měly mít jasnější výjimky.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Zvážit NetworkX grid místo numpy matice
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Starší návrh zjednodušit reprezentaci layoutu přes NetworkX grid.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-04-19
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Omezit délku identifikátorů v gridu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Identifikátory prvků měly mít maximální délku kvůli čitelnosti nebo exportu.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-04-19
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Iterovat přes všechny následníky v grafu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Připojování uzlů mělo počítat se všemi successors, ne jen s jedním směrem.


**Vytvořeno:** 2026-04-18
**Vyřešeno:** 2026-04-19
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Přepočítat souřadnice Factorio budov
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Factorio používá střed budovy jako souřadnici, což bylo potřeba promítnout do
layoutu.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Odstranit varování kolem `get_cords`
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Souřadnicová metoda byla používaná pro více typů objektů, než původně dovoloval
návrh.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Omezit výšku comboboxu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

GUI combobox s recepty potřeboval praktičtější maximální výšku.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Přidat heuristiku pro BFS
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Raný routing zvažoval heuristiku nad BFS, než se vývoj posunul k jinému
přístupu.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-04-19
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Odstranit limit počtu navštívených stavů
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

A\* měl dočasnou pojistku velikosti hledání, kterou bylo potřeba nahradit
robustnějším řešením.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Používat underground belts jen když dávají smysl
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Routing měl zabránit zbytečnému používání underground beltů.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Odstranit dočasné části routingu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Více provizorních bloků v `graph_to_matrix` bylo potřeba nahradit finální
logikou.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Kontrolovat shodu základních vektorů
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Při navazování pásů bylo nutné ověřovat kompatibilitu směrů.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Lépe reprezentovat průchod underground beltem
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Stav routingu neměl držet celý streak, ale jen informaci potřebnou k průchodu.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Resetovat GUI prvky po změně vstupu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

Pozdější varianta úkolu pro combobox a související odkaz po změně vstupního
souboru.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Odstranit dummy factory funkci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Factory`

Factory model obsahoval provizorní metodu určenou jen pro ověření návrhu.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/factory.py`
::::

::::{dropdown} Zpřesnit hodnoty v grid entry slovníku
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing, Grid`

Hodnoty v dictionary gridu měly nést víc informací než jen textový typ.


**Vytvořeno:** 2026-04-19
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`,
`src/factory_creator/grid.py`
::::

::::{dropdown} Přenastavit cenu underground beltů
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Náklady routingu měly zohlednit použití underground beltů váhou, ne jen
jednotkovou cenou.


**Vytvořeno:** 2026-05-13
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Opravit a odstranit dočasný routing kód
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Část kódu kolem cest měla být opravena a zbavena provizorní větve.


**Vytvořeno:** 2026-05-13
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Přesunout GUI helper mimo GUI vrstvu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

Pomocná funkce používaná v GUI patřila do sdílené vrstvy nebo utility modulu.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Najít lepší místo pro sdílenou logiku
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

Obecnější varianta refaktoringu funkcí, které neměly zůstávat v GUI.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Rozšířit obsazenost gridu mimo pásy
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing, Grid`

Grid occupancy měl pokrýt i další entity, nejen dopravní pásy.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`,
`src/factory_creator/grid.py`
::::

::::{dropdown} Přidat helper pro souřadnice budov
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Výpočet okolí budovy fungoval jen při určitém pořadí vytváření prvků.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Nahradit magickou konstantu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`CLI`

Argument processor obsahoval hodnotu, která měla být pojmenovaná konstanta.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/argument_processor.py`
::::

::::{dropdown} Jednoznačně odlišit pásy v malých továrnách
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing, Grid`

U malých layoutů se pásy málo překrývaly, takže bylo potřeba lepší rozlišení
prvků.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`,
`src/factory_creator/grid.py`
::::

::::{dropdown} Opravit používání `get_cords` v evoluci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Evolution`

Evoluční modul používal souřadnice způsobem, který neodpovídal dostupné metodě
na factory objektech.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/evol.py`,
`src/factory_creator/evolution.py`
::::

::::{dropdown} Zabránit překryvu budov v evoluci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Evolution`

Evoluční posuny neměly dovolit sloučení nebo překrytí výrobních budov.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/evol.py`,
`src/factory_creator/evolution.py`
::::

::::{dropdown} Nahradit dočasné integer stavy enumem
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Grid`

Grid používal syrové integer hodnoty pro stavy, které si říkaly o enum nebo
pojmenovaný typ.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/grid.py`
::::

::::{dropdown} Drobné zlepšení gridu
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Grid`

Krátká poznámka k lokálnímu úklidu grid reprezentace bez samostatné specifikace.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/grid.py`
::::

::::{dropdown} Rozpracovaný úkol v evoluci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Evolution`

Placeholder TODO v evoluční vrstvě byl odstraněn při větším úklidu modulu.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/evol.py`,
`src/factory_creator/evolution.py`
::::

::::{dropdown} Rozšířit testy o underground block
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Evolution`

Testy dočasně pokrývaly jen variantu bez blokace underground beltů.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/evol.py`
::::

::::{dropdown} Zohlednit matici po evoluci
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`GUI`

GUI po evolučním běhu ignorovalo nově vzniklou matici layoutu.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/gui/main_window.py`
::::

::::{dropdown} Opravit práci s extra marginem
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Routing měl dočasný problém s okrajem layoutu.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-04
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Sjednotit orientaci začátku a konce cesty
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Inserter a navazující transportní prvky potřebovaly kompatibilní orientaci na
začátku i konci cesty.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Přesunout konstantu underground beltů
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Grid`

Konstanta pro underground belts nemohla být v původním modulu kvůli cyklickým
importům.


**Vytvořeno:** 2026-07-04
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/grid.py`
::::

::::{dropdown} Rozlišit vstupní a výstupní underground belts
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Routing potřeboval vědět, zda konkrétní underground belt slouží jako vstup nebo
výstup.


**Vytvořeno:** 2026-07-05
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Rozšířit požadavek stejné orientace na start
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

Kontrola orientace se neměla týkat jen underground části a konce, ale i začátku
cesty.


**Vytvořeno:** 2026-07-05
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Zjednodušit stav pro průchod underground trasou
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Routing`

A\* nemusel nést celý streak stavů, stačila informace relevantní pro průchod.


**Vytvořeno:** 2026-07-05
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/graph_to_matrix.py`
::::

::::{dropdown} Přesunout cost do grid entry
:color: success
:icon: check-circle

{bdg-success}`done` {bdg-secondary}`Grid`

Cena průchodu měla být vlastností konkrétního grid prvku.


**Vytvořeno:** 2026-07-05
**Vyřešeno:** 2026-07-05
**Historické soubory:** `src/factory_creator/grid.py`
::::


* z velké míry je backlog historických TODO vygenerován pomocí extension, které požívá AI, z komentářů v kódu, takže některé položky mohou být nepřesné nebo zastaralé.
