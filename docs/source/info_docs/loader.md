# Loader

Loader je zodpovědný za načtení receptu a převedení jeho obsahu do stromu
reprentujícího závislosti, který je následně předán do další části systému,
kterou je Grid.

## Načtení receptu

Samotný loader je zodpovědný za načtení receptu, který je předán buď z CLI či
GUI. Recept je možné načíst ve formátu JSON, který je následně převeden do
interní reprezentace receptu. Z načteného souboru jsou zpracovány pouze položky
typu `recipe`, ze kterých vznikají objekty `Factory`. Pokud některé informace v
receptu chybí, loader používá výchozí hodnoty, například `energy_required = 0.5`
nebo výstupní množství `1`.

Při načítání loader zároveň určuje, kde se může pozdější dependency tree
zastavit. Recepty, jejichž název obsahuje `plate`, jsou označeny jako terminální
vstupy. Pokud se pro některou ingredienci nenajde odpovídající recept, je
reprezentována pouze jako objekt `Item`, tedy jako jednoduchý vstup bez dalších
závislostí. Tím loader nepřímo ovlivňuje nejen podobu stromu závislostí, ale i
následné rozložení továrny v gridu.

## Dependency tree

Zajímavější částí Loaderu je převod načteného receptu do stromu závislostí,
který je následně předán do další části systému, kterou je Grid. Strom
závislostí je reprezentován pomocí vrcholů typu `DependencyTreeNode`. Každý
vrchol kromě reference na recept drží také své potomky, vrstvu ve stromu a
odhadované rozměry příslušného podstromu. Strom je následně převeden na
`networkx.DiGraph`, se kterým pracuje převod do gridu.

Dependency tree má 2 základní způsoby, jak může být vybudován. Prvním je
**simplified structure**, která zobrazuje pouze závislosti mezi jednotlivými
typy receptů. Druhým je **full structure**, která bere v úvahu také potřebná
množství a podle nich může vytvářet opakované podstromy. Tato volba tedy
neovlivňuje pouze vzhled výsledného grafu, ale i následně vytvořený grid a
výsledek evolučního algoritmu.

Strom je vytvářen pomocí rekurzivního top down přístupu. V módu **full
structure** se podle požadovaného využití výstupního receptu (root nodu)
dopočítávají množství závislostí tak, aby bottleneck receptu vznikl až v
koncovém vrcholu. Tato možnost není v projektu příliš využita, protože výchozí
nastavení počítá s maximálním využitím továrny na výstupu, tedy s využitím
nastaveným na 1.0 neboli 100 %.

Dependency tree v sobě neukládá pouze závislosti, ale představuje první entry
point pro vytvoření rovinného nákresu továrny. Díky své struktuře se používá pro
odhady rozložení a rozměrů továrny. Šířka továrny (hloubka stromu, x-ová osa) je
poměrně přímočará a je dána strukturou stromu. Délka továrny (y-ová osa) je
počítána rekurzivně jako odhad z podstromů. Listové vrcholy stromu, tedy vstupní
výrobny, dokážeme odhadnout jejich vlastní velikostí. Vnitřní vrcholy dokážeme
odhadnout součtem velikostí jejich podstromů, případně přidáním paddingu. Tento
přístup umožňuje dostávat horní odhady pro rozměry továrny, které jsou následně
využívány pro konstrukci Gridu.

Mimo samotné struktury je přidán také aspekt slučování vstupů a výstupů, kdy
stejné typy materiálů ve stejných podstromech jsou slučovány do kompaktnějších
struktur.
