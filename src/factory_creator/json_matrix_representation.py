import base64, zlib
import itertools
import sys
import json

import numpy as np


class MatrixJsonConvertor:
    #TODO: make real

    @staticmethod
    def _get_blueprint_header():
        return {
            "icons" : [{
                "signal" : {
                    "type" : "recipe",
                    "name" : "Blueprint"
                },
                "index" : 1
            }]
        }

    @staticmethod
    def _get_blueprint_footer():
        return {
            "item" : "blueprint",
            "version" : 562949956239360,
            "label" : "Blueprint",
            "wires" : []
        }

    @staticmethod
    def _load_entities(matrix: np.ndarray):
        entities = {
            "entities" : []
        }

        entity_number = 1
        for i, j in itertools.product(range(matrix.shape[0]), range(matrix.shape[1])):
            if matrix[i, j] != "":
                entities["entities"].append(MatrixJsonConvertor._get_entity(
                    matrix[i, j], (i, j), entity_number
                ))

                entity_number += 1

        return entities


    @staticmethod
    def _get_entity(name: str, position: tuple, entity_number: int):
        return {
            "name" : name,
            "position" : {
                "x" : position[0],
                "y" : position[1],
            },
            "direction" : 0,
            entity_number: entity_number
        }

    @staticmethod
    def encode(matrix: np.ndarray) -> None:
        blueprint_json = {
            "blueprint": (
                MatrixJsonConvertor._get_blueprint_header() |
                MatrixJsonConvertor._load_entities(matrix) |
                MatrixJsonConvertor._get_blueprint_footer()
            )
        }

        print(json.dumps(blueprint_json))

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(blueprint_json, f, ensure_ascii=False, indent=2)

class BluePrintRepresentation:
    @staticmethod
    def decode(coded: str):
        # Factorio adds 0 at the stars which should be skipped
        coded_trunc = coded.strip()[1:]

        compressed = base64.b64decode(coded_trunc)
        decompressed = zlib.decompress(compressed)
        text = decompressed.decode("ascii")

        print(text)
        return json.loads(text)

    @staticmethod
    def encode(json_file) -> None:
        data = json.dumps(json_file)

        compressed = zlib.compress(data.encode("ascii"))
        encoded = base64.b64encode(compressed).decode("ascii")

        print("0" + encoded)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="ascii") as f:
            json_file = f.read()
            #json_file = BluePrintRepresentation.decode(f.read())
            BluePrintRepresentation.encode(json_file)