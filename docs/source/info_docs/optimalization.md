# Optimalizace Python kódu

Defaultně je Python pro numerické výpočty velmi pomalý. Obecně se tento problém
řeší použitím knihoven, Numpy, Scipy etc. Bohužel pro svůj projekt se mi
nepovedlo podařit použít tyto knihovny, poněvadž nepodporovali potřebnou
modularitu pro zakódování.

Absence rychlých knihoven je možné řešit pomocí použití optimalizačních
principů, které převádějí určité "typované" částí kódu a rychlejších jazyků či
nahracují způsob jakým Python kód běží.

Možné optimalizační principy jsou například:

- Cython $\rightarrow$ převedení částí kódu na Cython kompatibilního kódu, který
  je možné následně převést na C kód a zkompilovat do Python modulu.
- Numba $\rightarrow$ použití JIT kompilátoru, který převádí část kódu na
  strojový kód a následně jej spouští.
- PyPy $\rightarrow$ též používá JIT kompilátor, pro optimalizaci.
- mypyc $\rightarrow$ převádí část kódu na C kód a následně jej zkompiluje do
  Python modulu.

Všechny tyto přístupy z větší či menší míry potřebují typování kódu, aby bylo
možné převést jej na rychlejší jazyk. Proto se v mém kódu na mnoha částech
používá typování, které je pro klasický Python nepovinné a pouze kosmetické.
Nicméně pro optimalizaci je typování nezbytné. (Z osobního hlediska mi typování
přijde, že i bez optimalizace výrazně pomáhá udržitelnosti a přehlednosti kódu.)
