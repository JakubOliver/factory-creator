# Výsledky Benchmarků

## Hill climbing optimalizace

V této sekci se budu věnovat tomu jak optimalizace dvou mutací v hillclimbu
zrychlila dobu vypočtu.

### Omezení počtu mutačních pohybů

První a velkou změnou, kterou jsem provedl pro optimalizaci doby u hill
climbingu je omezení počtu mutačních pohybů. V původní verzi algoritmus počítal
jak se jedinec změný, když v jedné generaci pohneme s každou budovou do všech 4
možných směrů. Navzdory tomu, že tento přístup vede k tomu, že v každé generici
pro hill climb najdeme nejlepší potomka/souseda, tak je tento přístup velmi
výpočetně/časově náročný. A v praxi nepoužitelný pro větší továrny. Zároveň
možná změna, že bychom použili pouze procentuální podmnožinu (podmnožinu, která
obsahuje pouze x procent budov) se ukázala, že má stejný problém. A to takový,
že se počítá velké množství mutačních pohybů, které se nikdy nepoužijí, poněvadž
kvůli tomu, že používáme pouze hill climbing, tak se využije pouze ten nejlepší,
tak že ostatní výpočty, mohou tak maximálně updatovat cache, u které je hittrate
po změně budovy velmi nízký (viz text níže).

A tak se se nejlepší řešení ukázalo, že nejlepší je si vybrat pevně danou veliko
podmnožiny budov. V mém případě jsem skončit u velikosti 4 budov, tedy s 4 směry
máme v každé generaci 16 mutačních pohybů a tedy 16 sousedů/potomků.

## Tabulka benchmarků

Tabulka s vygenerovanými CSV tabulkami benchmarků s Github releasu pro
`benchmark` pipelinu.

```{github-release-assets}
:repository: JakubOliver/factory-creator
:tag: benchmark-results
```
