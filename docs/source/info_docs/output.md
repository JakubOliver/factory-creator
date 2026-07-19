# Výstup

## Zakódování

Po uprave interního gridu přichází na řadu převést do výstupního formátu. Kvůli
tomu, že pro továrnu využíváme přístup a assety z Factoria, tak je potřeba
převést interní grid do formátu, který je kompatibilní s Factoriem. Tento převod
je prováděn v několika krocích:

Nejdříve je potřeba převést grid do specifického JSON formátu. V aktuální
podobně je tato transformace podporována pouze pro malou podmnožinu Factorio
objektů, které jsou využívány v rámci projektu.

Po převedení do JSON formátu je potřeba převedený soubor zazipovat a následný
zip zakódovat do Base64.

## Zobrazování

Base64 zakódovaná továrna představuje v tomto stavu string který je možné vložit
do hry. Pro zjednodušení je využíván
[open source projekt](https://github.com/teoxoy/factorio-blueprint-editor),
který umožňuje zobrazit továrnu.

Vlastníci tohoto projektu hostují tuto službu na `https://fbe.teoxoy.com/`. Je
ale také možné spustit tuto službu lokálně a nastavit URL na vlastní instanci.

## Modularita

Celý process továrny je modulární a je možné používat libovolné recepty, které
mají nic společného s Factorio. Jediné aktuální omezení je právě export.
Poněvadž nepodporované recepty a objekty, které z nich vyjdou, nejdou vykreslit.
Tento problé má 2 řešení.

První je vytvořit interní mapování custom objektů na podporované objekty. Tedy
pokud bychom chtěli použít recept, který má na výstupu chleba. Tak bychom mohli
chleba mapovat na jiný objekt, který je podporován. Což ale způsobí, že ikona
chleba bude vypadat jako ikona mapovaného objektu. (Zobrazování tupů v výrobnách
jde vypnout, takže by nebylo tolik matoucí.)

Druhý přístup je modifikovat open source projekt. Co jsem prozatím zjistil, tak
projekt je velmi modulární a objekty nejsou nijak hardocoded, ale používají
Factorio API pro stažení assetů. Tedy by nejspíš nebyl problém rozšířit tuto
množinu assetu o nové. Tím bychom, ale od uživatele požadovali, nejen aby
poskytl recepty, ale také assety pro zobrazení. Nebo alespoň bych musel vytvořit
nějakou množinu generických assetů např. počáteční písmena, nebo z názvu objektu
vytvořit asset s jménem.
