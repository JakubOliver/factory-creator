# Uživatelské prostředí

Projekt je možné ovládat dvěma způsoby, a to buď pomocí příkazového řádku (CLI)
nebo pomocí grafického uživatelského rozhraní (GUI). Oba způsoby umožňují
načtení receptu a jeho předání do další části systému, kterou je Loader. Více o
tom, jak Uživatelské rozhraní funguje, je možné se dočíst v
[uživatelské dokumentaci](../user_docs/index.md).

## Grafické uživatelské rozhraní (GUI)

Grafické uživatelské rozhraní je vytvořeno pomocí knihovny PyQt6, která umožňuje
vytváření nativních aplikací pro různé operační systémy. GUI je koncipované jako
one-page aplikace, jejíž obsah se případně přidává podle akcí uživatele či
podle stavu aplikace.

Za větší zmínku stojí funkce embedded prohlížeče, který je zodpovědný za
zobrazení výsledného JSONu, který reprezentuje továrnu. Embedovaný prohlížeč je
vytvořen pomocí knihovny PyQt6.QtWebEngineWidgets, která umožňuje zobrazování
webového obsahu v aplikaci.

Pro zpracování JSONu využívám už existující stránku
[fbe.teoxoy.com](https://fbe.teoxoy.com/?source=https://pastebin.com/uc4n81GP),
která umožňuje zobrazení blueprintu továrny. Projekt je open source a je možné
si ho stáhnout z [GitHubu](https://github.com/teoxoy/factorio-blueprint-editor).

Konkrétní kód je možné nalézt v modulu `factory_creator/gui`, kde je možné nalézt
`MainWindow` třídu, která je zodpovědná za vytvoření hlavního okna aplikace a
jeho interakci s uživatelem. Za zmínku stojí také třída `FactoryResultWidget`,
která je zodpovědná za zobrazení výsledného JSONu v embedded prohlížeči.

Ještě je přítomná třída `ComputeRecipeWorker`, která je zodpovědná za výpočet
receptu v samostatném vlákně, aby nedošlo k zablokování hlavního vlákna
aplikace.

## Příkazový řádek (CLI)

Je přítomné i jednoduché příkazové rozhraní, které umožňuje rychlejší přístup k
core modulu a možnou automatizaci pomocí skriptů. Celé zpracování argumentů z
příkazové řádky je zajištěno pomocí knihovny argparse.

Konkrétní kód je možné nalézt v modulu `factory_creator/cli`, kde je možné nalézt
2 třídy, které zajišťují zpracování argumentů a CLI a to `ArgumentParser` a
`CLI`. Třída `ArgumentParser` je zodpovědná za definování argumentů a jejich
zpracování, zatímco třída `CLI` je zodpovědná za samotné spuštění příkazového
řádku a jeho interakci s uživatelem.
