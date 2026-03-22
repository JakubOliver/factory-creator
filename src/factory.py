import json

class Factory:
    def __init__(self, name, energy_required, ingredients, x_size, y_size):
        self.name = name
        self.energy_required = energy_required
        self.ingredients = ingredients
        self.x_size = x_size
        self.y_size = y_size

    def __str__(self):
        return f"name: {self.name}, energy_required: {self.energy_required}, ingredients: {self.ingredients}"

class FactoryLoader:
    @staticmethod
    def load(factory_definition_file_path):
        factories = []

        with open(factory_definition_file_path, "r") as file:
            data = json.load(file)

            for entry in data:
                if entry["type"] == "recipe":
                    if not "energy_required" in entry:
                        energy_required = 0
                    else:
                        energy_required = entry["energy_required"]

                    factory = Factory(entry["name"], energy_required, entry["ingredients"], 4, 4) #TODO: loading real sizes
                    factories.append(factory)

        return factories
