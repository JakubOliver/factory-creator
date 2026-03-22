#!/usr/bin/env python3

from src import factory
from src.factory import FactoryLoader

recipe_file_path = "data/recipe.json"

if __name__ == '__main__':
    factories = FactoryLoader.load(recipe_file_path)

    for factory in factories:
        print(factory)
