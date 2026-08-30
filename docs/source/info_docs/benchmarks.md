# Výsledky Benchmarků

## Hill climbing optimalizace

V této sekci se budu věnovat tomu, jak optimalizace dvou mutací v hillclimbu
zrychlila dobu výpočtu.

### Omezení počtu mutačních pohybů

První a velkou změnou, kterou jsem provedl pro optimalizaci doby u hill
climbingu je omezení počtu mutačních pohybů. V původní verzi algoritmus počítal
jak se jedinec změní, když v jedné generaci pohneme s každou budovou do všech 4
možných směrů. Navzdory tomu, že tento přístup vede k tomu, že v každé generaci
pro hill climb najdeme nejlepší potomka/souseda, tak je tento přístup velmi
výpočetně/časově náročný. A v praxi nepoužitelný pro větší továrny. Zároveň
možná změna, že bychom použili pouze procentuální podmnožinu (podmnožinu, která
obsahuje pouze x procent budov) se ukázala, že má stejný problém. A to takový,
že se počítá velké množství mutačních pohybů, které se nikdy nepoužijí, poněvadž
kvůli tomu, že používáme pouze hill climbing, tak se využije pouze ten nejlepší,
takže ostatní výpočty mohou maximálně updatovat cache, u které je hittrate
po změně budovy velmi nízký (viz text níže).

Jako nejlepší řešení se ukázalo vybrat pevně danou velikost podmnožiny budov. V
mém případě jsem skončil u velikosti 4 budov, tedy se 4 směry
máme v každé generaci 16 mutačních pohybů a tedy 16 sousedů/potomků.

Tedy se zvětšujícím se počtem budov se nám lineárně zvyšoval počet mutačních
pohybů, které se musely vypočítat. A zároveň se nám alespoň lineárně zvyšovala
doba výpočtu jednoho daného mutačního pohybu, poněvadž grafy byly větší a
komplikovanější.

Díky tomu, že jsme omezili počet mutačních pohybů, tak jsme se zbavili
lineárního nárůstu počtu mutačních pohybů. A zároveň je hill climb stále plně
funkční, již nenajde nejoptimálnější posun z daného stavu, ale díky tomu
zrychlení výpočtu a pořád přítomného zlepšení z generace na generaci, dostáváme
ve výsledku drastické zrychlení za velmi malou cenu v kvalitě výsledku.

- S touto optimalizací jsem začal a v dané době jsem ještě neměl tak rozsáhlý
  způsob benchmarkování, takže máme pouze jeden benchmark, který se snaží
  napodobit původní nastavení a subjektivně/objektivní manuální pozorování, při
  kterém byla změna opravdu znatelná.

### Optimalizace výpočtu dle topologického uspořádání

Druhá přítomná mutace, tedy přepočítávání grafu pro nějaké jiné topologické
uspořádání, se ukázala být problematická i na poměrně malých továrnách. A to
kvůli tomu, že nějaká topologická uspořádání jsou méně vhodná než jiná, a v dané
době přítomný algoritmus se snažil i tato nevhodná uspořádání několikrát
přeškálovat a znovu dopočítat (přeškálování znamená, že se zvýší odstupy mezi
budovami, tedy pásy a napojení dostanou více místa pro nalezení cesty).

#### Nevhodná a neřešitelná napojení

Otázkou je, zda grafy, které nejde sestrojit, vůbec existují. A odpověď je ano,
existují. Ale jsou to spíše okrajové a ne tak zajímavé případy, jak např.
výrobna o velikosti 3x3 má pouze 12 okolních políček, která se dají použít pro
napojení (použití velkého překladače pouze pozmění napojovací políčko, ale žádné
nám nepřidá), tedy pokud bychom se někde snažili napojit 13 pásů, tak to není
možné.

Toto, ale není hlavní problém, s kterým jsem se potýkal. Mnohem větší problém
je, že hledání napojení pro továrnu je MAPF problém, ale my používáme pouze A\*
algoritmus, používáme ho chytře tak, že se snažíme nejdříve najít cestu pro
budovy nejblíže zdroje, ale i tak se může stát, že předchozí cesty zablokují
cestu pro další budovu.

Tedy se vlastně dostáváme k tomu, co vlastně je nevhodné topologické uspořádání,
to je takové, které vytváří konflikty v cestách, vynucuje přeškálování a bez
MAPF algoritmu není řešitelné. Naší výhodou je, ale že takováto nevhodná
uspořádání nevedou k dobrému výsledku. Jak z hlediska naší fitness, tak z
hlediska vizuálního, kdy předpokládám že upřednostníme taková napojení, která
jsou strukturovaná, přehledná a kompaktní, než taková, která jsou chaotická,
komplikovaná a konfliktní.

#### Co dál?

Další otázkou je, jak se tedy s takovýmito uspořádáními vypořádat. Víme, že tato
nevhodná uspořádání se vyskytují, může jich být potenciálně velmi mnoho, jsou
výpočetně náročná a nevedou k dobrým výsledkům. To by naznačovalo, že dobrý
nápad by byl úplně vypnout možnost přeškálování a využívat pouze prvotní
uspořádání, toto je dobrý nápad, ale ne úplně v globálu.

Při svých benchmarcích jsem zkoumal hlavně 2 věci: jakou rychlostí a s jakou
úspěšností dokážou různé konfigurace vyřešit podmnožinu všech topologických
uspořádání pro recept/graph `electric-mining-drill`, který je středně
komplikovaný, a jak se chovají při 5 seedovaných runech stejného receptu.

U prvního testu s nastavením 5 přepočítávání grafu, jsem pro 100 náhodných
topologických uspořádání, dokázal vyřešit všech 100.

| Success | Average time  | Min time    | Max time      |
| ------- | ------------- | ----------- | ------------- |
| 100/100 | 6.46493961384 | 0.107040703 | 258.604340126 |

Celý run tohoto testu běžel skoro 650 sekund, tedy můžeme vidět, že ano,
dokázali jsme vyřešit všechna topologická uspořádání, ale pouze nejnáročnějších
z nich nám zabralo polovinu celého času.

Při nastavení 3 přepočítávání grafu jsme už dostali pouze úspěšnost 97 %, ale
zato jsme se zbavili horních extrémů. Průměrný čas výpočtu se téměř 3krát
zkrátil.

| Success | Average time  | Min time    | Max time     |
| ------- | ------------- | ----------- | ------------ |
| 97/100  | 2.26809643938 | 0.076653482 | 44.431602511 |

U žádného opakování jsme se dostali na úspěšnost 62 % a na celkový čas 44 sekund.

Tedy jak můžeme vidět, myšlenka přeškálování grafu není špatná a má svoje
místo. Pouze je potřeba ji použít rozumně.

To je ihned vidět na druhém testu, kde jsem navíc testoval přístup, že se
opakování použije pouze při sestrojování prvotního grafu, ale nebude součástí
evoluce.

- výsledky níže jsou pouze pro první seed pro tento test, ale trend byl všude
  stejný

| Popisek                                                 | Duraton         | Final fitness      |
| ------------------------------------------------------- | --------------- | ------------------ |
| 5x přepočítávání i v evoluci                            | 4654.566225     | -4113.536121673005 |
| 5x přepočítávání pouze při sestrojování prvotního grafu | 166.516444      | -4113.536121673005 |
| 3x přepočítávání i v evoluci                            | 2186.471100     | -4113.536121673005 |
| 3x přepočítávání pouze při sestrojování prvotního grafu | obdobné jako 5x | obdobné jako 5x    |

Tedy na tomto příkladu můžeme vidět, že absence přepočítávání grafu v evoluci
zrychlí výpočet a zároveň dosahuje obdobně stejných výsledků. (To že se nám na
tomto benchmarku podařilo dosáhnout stejného výsledku je spíše díky tomu, že
daný recept, není úplně super obrovský. Proto v aktuální implementaci je v GUI
flag pro nastavení zda, chceme přepočítávání grafu v evoluci, či ne. Poněvadž v
nějakých případech to může dávat smysl. Defaultně je tento flag nastavený na
False.)

Ještě abych se vrátil k úplné absenci přepočítávání grafu, tak toto není velmi
dobrý nápad, poněvadž jenom na tomto středně těžkém benchmarku, se nám
nepodařilo vytvořit továrnu pro vstupní recept, navzdory tomu, že graf je
vytvářen pomocí Dependency tree, který již rozumně shlukuje budovy. Tedy dobrý
defaultní kompromis je, ponechání přepočítávání grafu pouze při sestrojování
prvotního grafu, ale ne v evoluci. Zde si chceme zachovat rychlost výpočtu a
zároveň využít pouze opravdu zlepšující topologická uspořádání (pořád je ale
možné přepočítávání spustit).

- dodatečně jsem se snažil ještě simulovat stav výpočtu, který byl v červenci
  2026, bohužel celý benchmark se nedokázal dopočítat do 5 hodin, tedy nemáme v
  tabulce celkové výsledky. Máme ale první test, stejný test, který se vyskytuje
  v tabulkách výše. Při tomto testu jsme bez přepočítávání v evoluci, tedy s
  aktuálním přístupem, ale s počítáním všech evolučních posunů, dostali čas okolo
  300 sekund. Při středně velkém receptu se nám tedy podařilo zrychlit výpočet
  2krát. Při větších receptech by se toto zrychlení mělo projevit ještě více (i
  když výpočetně náročnější je druhá mutace pracující s
  novými topologickými uspořádáními).

### Cachování

Jednou z implementačních optimalizací, které jsem už částečně měl připravené
předtím bylo cachování, jak pro fitness, tak pro výpočet mutace. Bohužel se
ukázalo, že pomoc, kterou cachování poskytuje, je velmi malá. Například pro
cachování mutace topologických uspořádání s receptem `electric-mining-drill` se
ukázalo, že existuje pro daný graf téměř 15 milionů topologických uspořádání
(hodnota vracená z networkx knihovní funkce, tak z jiného algoritmu), ale při
výpočtu s 100 generacemi vytvoříme pouze 400 topologických uspořádání. Tedy
hitrate cache je velmi nízký. A pro komplikovanější recepty může počet
topologických uspořádání růst až faktoriálně, takže se dá očekávat, že hitrate
cache bude ještě nižší (samozřejmě nemusí platit přímá úměra: více vrcholů, více
topologických uspořádání, ale u receptů toto pravidlo tak nějak platí).

## Tabulka benchmarků

Tabulka s vygenerovanými CSV tabulkami benchmarků s Github releasu pro
`benchmark` pipelinu.

```{github-release-assets}
:repository: JakubOliver/factory-creator
:tag: benchmark-results
```
