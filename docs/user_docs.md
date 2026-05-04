# User Documentation

## How to run

The code can be run via command

```
python3 main.py
```

or 

```
./main.py
```

Required modules can be imported by 

```
pip install -r requirements_in_construction.txt
```

* I was trying a lot of different libraries therefore in this **not final** requirements is several imports that are not used.

## Controls

The project is controlled via basic GUI. Firstly, you can enter the json file which contains the definition of the recipes. One of these files is prepared in file `data/recipe.json`. After loading the JSON file you can select for which recipe you want to create factory. At this stage (19.4.2026, very work in progress) works 100 % only on very small factories, you can try:
* barrel - very small
* electric-mining-drill - bigger (does not work 100 %)
* or inserter - bigger (does not work 100 %)

After generation a schematic dependency graph pop pup and shows up also button in the GUI which by clicking open browser with [online factory editor](https://fbe.teoxoy.com/) and loaded factory. 