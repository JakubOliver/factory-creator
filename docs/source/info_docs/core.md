# Core

Nejzajímavější a nejkomplexnější částí projektu je Core modul, který zahrnuje
konkrétní implementaci evolučního algoritmu a práci s maticí/gridem/2D polem,
které reprezentuje továrnu.

## Převod na grid

Jak už bylo zmíněno v [Loader modulu](loader.html), recepty se nepřevádějí přímo
do gridu, ale nejprve se převádějí na dependency tree, který je následně
převeden na grid.

Navíc graf, který dochází z Loader modulu, už není pouhý obecný diskrétní strom,
díky spojením inputů a outputů, se na vstupu dostává orientovaný acyklický graf
(DAG), který je následně převeden na grid.

Převod probíhá v 2 fázích jeden je přidání budov do gridu a druhý je jejich
propojení. Postup pro přidávání budov do gridu je podle topologického uspořádání
(tento přístup je hlavně pozůstatek z původní implementace, kdy neexistovali 2
fázi a budovy se propojovali ihned po jejich přidání do gridu, tento přístup ale
doprovázel neduh, že při složitějších strukturách továrny nejde obecně zaručit,
že propojovací pásy budou vždy postupovat směrem už k vybudovaným budovám, tedy
se stávalo, že místo v gridu, kde měla být budova přidána už bylo opsazené
propojovacícimi pásy).

Tedy v první fázi se přidají budovy do gridu v pořadí jednoho z možných
topologických uspořádání a jsou umísněni podle odhadů pocházejících z dependency
tree. Poté následuje druhá fáze, kdy se budovy propojí pomocí propojovacích
pásů.

## Reprezentace gridu

Grid není pouze matice viditelných entit, ale uchovává i informaci o prostoru,
který je jednotlivými entitami obsazený. To je důležité hlavně u budov, protože
jedna budova nezabírá jen jedno políčko, na kterém je ukotvená, ale i své okolní
části. V gridu se proto rozlišují samotné prvky továrny a políčka, která jsou
blokována jejich rozměrem. Díky tomu může algoritmus jednotně kontrolovat
kolize při pokládání budov i pásů, aniž by musel při každém kroku znovu
dopočítávat tvar všech objektů.

Další důležitou vlastností gridu je, že propojovací prvky nejsou navázané pouze
na souřadnice, ale na identitu prvků, které propojují. To je užitečné hlavně
později při evoluci, protože budova může změnit svou pozici, ale pořád je možné
poznat, ke kterým ostatním budovám nebo zdrojům byla původně připojená.

## Propojování budov

V druhé fázi se znovu prochází budovy v topologickém pořadí a pro každý aktuální
vrchol se hledá nejkratší cesta k jeho potomkům. Problém je lehce rozšířen tím,
že nehledáme nejkratší cestu mezi dvoumi atomickými body, ale pracuejme s 2
neprázdnymi množinami atomických bodů, v implementaci tvoří jedna množina bodů
jednu komponentu souvislosti (pokud by tvořila více komponent souvislosti tak by
i tak algoritmus níže našel korektní cestu).

Z podstaty toho, že jako výstup se využívají **Factorio** assety, tak toto
přináší určitá další omezení (mnohá z těchto omezení by dávala smysl v "reálném
světě"). Jedním z hlavních omezení je, že propojovací pásy se nesmí křížit, na
toto existuje mechanika podzemních pásu, které ale přináší omezení, že pásy před
vstupem a výstupem podzeního pásu musí minimálně 2 polička určovat stejnou
orientaci. Podobné omezení, dávající smysl i v realitě, je že orientaci musíme
kontrolovat i u napojení na samotné budovy, tedy konkrétně napojení pomocí
překladačů, poněvadž potřebujeme zajistit, že překladače "ukazují" na korektní
pozice, nestačí pouze, že sousedí s pásem a budouvou zároveň.

Tyto omezení nás nutí používat komplexnější statový prostor než pouze 2D mřížku.
V aktuální implementaci je stavový prostor rozšířen ještě o informaci "streaku"
tedy kolik pásů/políček v řadě má stejnou orientaci. Tedy stav nám tvoří
uspořádáná trojice (souřadnice, orientace, streak). Naivní implementace by
násobně zvětšila stavový prostor, poněvadž by streak mohl nabývat libovolné
hodnoty, ale my v omezeních potřebujeme streak pouze do hodnoty 2, tedy můžeme
streak omezit konečnou hodnotou větší než tento treshold.

Pro nalezené cesty mezi množina bodů se používá A\* algoritmus, který je
rozšířen o výše zmíněné omezení. Jeho ohodnocení je poměrně přímočaré, cena
cesty je dána počtem políček, a heuristika, díky tomu, že se jedná o 2D mřížku,
je dána Manhattanovou vzdáleností mezi množinami bodů (tedy nejmenší
Manhattanovská vzdálenost mezi libovolnými body z obou množin).

S rozšířeným statovým prostorem se nám objevují další problémy. Z pohledu A\*
algoritmu je možné na jedné cestě vícekrát navštívit jednu souřadnici, ale s
různou orientací a streakem. Což by nám ale způsobovalo, že na jedné souřadnici
by se nacházelo více definic pásů. Zároveň si nemůeme "naivně" pamatovat, že
jsme už danou souřadnici navštívili, protože by nám to způsobovalo, že bychom
mohli danou souřadnici využít s jinou orientací a streakem.

Problém by se zdá býti jednoduše řešitelný tím, že si každý vrchol A\* algoritmu
bude pamatovat, odkazy na své předky a ty kontroloval, či by si pamatoval seznam
(spíše set) předků. Oba tyto přístupy jsou validní a vedou k správnému řešení.
Bohužel oba tyto přístupy mají nevýhodu, že v případě kontroly předků je tato
kontrola poměrně náročná, při delších cestách. O něco horší je přístup, kdy si
každý vrchol pamatuje seznam předků, poněvadž při takovémto řešení "exploduje"
paměťová náročnost.

Tím že, datová struktura, která si má pamatovat předky, velmi rychle roste (z
globálního hlediska), ale velké části se opakují. Tak mě vedli cesty k využití
nějaké semi-persistentní či persistnetní datové struktury. Z prvu jsem zkoušel
najít nějakou rozumnou implementaci semi-persistentní stromů, ale nenašel jsem
nic vhodného. Následně jsem narazil na knihovny
[pyrsistent](https://github.com/tobgu/pyrsistent), která obsahuje implementaci
persistentního setu, což je přesně to, co je potřeba. PSet není implementován
jako strom, ale jako nadstavba nad persistentní mapou, která je implementována
(alespoň co se mi podařilo najít) jako Hash Array Mapped Trie (HAMT). Což je
velmi zajímavá kombinace semi-persitentní stromu a TRIE. Tedy pro PSet a PMap se
používá persistentní strom, který ale ukládá hashe elementů. Využití této datové
struktury zdánlivě vyřešilo problém s pamětí.

## Konstrukce cesty

Pokud bychom měli stavový prostor pouze 2D mřížku, tak bychom mohli pro nalezené
cestu použít jednoduchý backtracking, pomocí např. matice času navštívení. Tento
přístup bohužel v rozšířeném stavovém prostoru není možný, proto je potřeba pro
každý vrchol A\* si pamatovat jeho předka, což ale potom zjedodušuje konstrukci
cesty.

## Evoluční algoritmus

## Hill climbing

Hill climbing je jednoduchý evoluční algortmus, který v mé implementaci pracuje
s populací o velikosti 1. V každé generaci posune každou pohyblivou budovu o 1
políčko ve všechn 4 směrech znovu napojí na ostatní budovy a vyhodnotí fitness.
Pokud je fitness lepší než fitness předchozí generace, tak se tato nová generace
stává aktuální generací. Pokud ne, si ponecháme jedince z minulé generace.

Při posunu jedné budovy se nejprve odstraní její původní propojovací pásy, ale
zůstane zachována informace o tom, se kterými sousedními prvky byla propojena a
v jakém směru dané propojení vedlo. Po vložení budovy na novou pozici se tato
propojení znovu sestaví stejným algoritmem pro hledání cest jako při prvotní
konstrukci gridu. Evoluce tedy nemění receptovou strukturu továrny, ale pouze
hledá jiné geometrické rozmístění stejných prvků a jejich spojů.

Tento process opakujeme dokud nenastane situace, kdy se fitness nezlepší po
určitém počtu generací. Nebo dojde počet generací k nastavenému limitu.

## Fitness funkce

V aktuální implementaci se fitness skládá s z několika částí:

Funkce, které se snaží minimalizovat:

- Obsah blochy obdelníku, který obklopuje všechny budovy.
- Počet využitých políček.

Funkce, které se snaží o kompaktnost:

- Součet vzdáleností budov od středu.

Funkce, které se snaží o "estetiku":

- Bonusové body, pokud se pásy napojují na střed továrny.

Kontrolní funkce, které penalizují:

- Kontrola, zda jsou budovy opravdu propojené.

Právě tato část s evolučními algoritmy bude nejvíce rozvíjena existuje už
několik nápadů, které jsou v současné době sepsány v poznámkách.
