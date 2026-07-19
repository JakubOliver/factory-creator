import base64, zlib
import sys

import json

from ..grid import Grid, GridEntry
from ..util.factorio_const import FactorioConst


class MatrixJsonConvertor:
    """
    Wrapper for the methods which converts grid factory representation into
    the json one which is used inside Factorio.
    """

    #TODO: make real

    @staticmethod
    def _get_blueprint_header():
        return {
            "icons" : [{
                "signal" : {
                    "type" : "recipe",
                    "name" : FactorioConst.TRANSPORT_BELT
                },
                "index" : 1
            }]
        }

    @staticmethod
    def _get_blueprint_footer():
        return {
            "item" : FactorioConst.BLUEPRINT,
            "version" : 562949956239360,
            "label" : "Blueprint",
            "wires" : []
        }

    @staticmethod
    def _load_entities(matrix: Grid, offset: tuple[int, int] = (0, 0), entity_number: int = 1):
        ox, oy = offset

        entities = {
            "entities" : []
        }

        for i, j in matrix:
            entry = matrix[i, j]

            #TODO: maybe is needed to rotate inserters
            if entry.name in [
                FactorioConst.TRANSPORT_BELT,
                FactorioConst.FAST_UNDERGROUND_BELT,
                FactorioConst.INSERTER,
                FactorioConst.LONG_HANDED_INSERTER,
            ] and entry.is_transportation():
                entity = MatrixJsonConvertor._get_entity(
                    entry.name,
                    (i + 1/2 + ox, j + 1/2 + oy),
                    entry.orientation,
                    entity_number
                )

                if entry.name == FactorioConst.FAST_UNDERGROUND_BELT and entry.underground_belt_type is not None:
                    entity["type"] = entry.underground_belt_type

                entities["entities"].append(entity)
            elif "source" in entry.name:
                entities["entities"].append(MatrixJsonConvertor._get_chest_entity(
                    FactorioConst.WOODEN_CHEST,
                    (i + 1/2 + ox, j + 1/2 + oy),
                    entry.orientation,
                    entity_number,
                    GridEntry.extract_item_name_from_source(entry.name)
                ))
            else:
                entities["entities"].append(MatrixJsonConvertor._get_assembling_machine(
                    FactorioConst.ASSEMBLING_MACHINE_2,
                    (i + 3/2 + ox, j + 3/2 + oy),
                    entry.orientation,
                    entity_number,
                    entry.name
                ))

            entity_number += 1

        return entities


    @staticmethod
    def _get_chest_entity(name: str, position: tuple, orientation: int, entity_number: int, content_name: str):
        content= MatrixJsonConvertor._get_entity(name, position, orientation, entity_number)
        content["items"] = [
            {
                "id": {
                    "name": content_name
                },
                "items": {
                    "in_inventory": [
                        {
                            "inventory": 1,
                            "stack": 0,
                            "count": 100
                        }
                    ]
                }
            }
        ]

        return content

    @staticmethod
    def _get_entity(name: str, position: tuple, orientation: int, entity_number: int):
        return {
            "name" : name,
            "position" : {
                "x" : position[0],
                "y" : position[1],
            },
            "direction" : orientation,
            "entity_number": entity_number
        }

    @staticmethod
    def _get_assembling_machine(name, position, orientation, entity_number, recipe):
        entry = MatrixJsonConvertor._get_entity(name, position, orientation, entity_number)
        entry["recipe"] = recipe

        return entry

    @staticmethod
    def process_presentation(worlds: list[Grid]):
        blueprint_json = {
            "blueprint": (
                MatrixJsonConvertor._get_blueprint_header() |
                MatrixJsonConvertor._get_blueprint_footer()
            )
        }

        blueprint_json["blueprint"]["entities"] = []

        horizontal_offset = 0
        entity_number_offset = 1
        for world in worlds:
            loaded = MatrixJsonConvertor._load_entities(
                world,
                offset = (horizontal_offset, 0),
                entity_number = entity_number_offset
            )

            blueprint_json["blueprint"]["entities"].extend(loaded["entities"])

            horizontal_offset += world.get_with() + 10
            entity_number_offset += len(loaded["entities"])

        with open("output/data_presentation.json", "w", encoding="utf-8") as f:
            json.dump(blueprint_json, f, ensure_ascii=False, separators=(",", ":"))

        return blueprint_json

    @staticmethod
    def encode(grid: Grid, offset: tuple[int, int] = (0, 0)):
        """
        Encodes the grid representation into json and returns the json representation.

        :param grid: Grid representation of the factory.
        :return: Json representation of the factory.
        """

        blueprint_json = {
            "blueprint": (
                    MatrixJsonConvertor._get_blueprint_header() |
                    MatrixJsonConvertor._load_entities(grid, offset = offset) |
                    MatrixJsonConvertor._get_blueprint_footer()
            )
        }

        with open("output/data.json", "w", encoding="utf-8") as f:
            json.dump(blueprint_json, f, ensure_ascii=False, separators=(",", ":"))

        return blueprint_json

class BluePrintRepresentation:
    """
    Wraps methods connected to the transforming json factory representation
    into the compressed one.
    """

    @staticmethod
    def decode(coded: str):
        """
        Decodes the compressed factory representation into json format and
        returns the json representation.

        :param coded: Encoded representation of the factory.
        :return: Json representation of the factory.
        """

        # Factorio adds 0 at the stars which should be skipped
        coded_trunc = coded.strip()[1:]

        compressed = base64.b64decode(coded_trunc)
        decompressed = zlib.decompress(compressed)
        text = decompressed.decode("ascii")

        print(text)
        return json.loads(text)

    @staticmethod
    def encode(json_data) -> str:
        """
        Encodes the json representation of the factory into the compressed one.

        :param json_data: Json representation of the factory.
        :return: Compresses representation of the factory.
        """

        json_bytes = json.dumps(json_data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        compressed = zlib.compress(json_bytes, level=9)
        blueprint_string = "0" + base64.b64encode(compressed).decode("ascii")

        return blueprint_string

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="ascii") as f:
            json_file = json.load(f)
            #json_file = BluePrintRepresentation.decode(f.read())
            BluePrintRepresentation.encode(json_file)

# the blueprint can the show via url:
# https://fbe.teoxoy.com/?source=0eNqd1t9ugjAUx/F36TUYOQW0XO41FrMAnmiTUgitc8bw7itTF7Itsb9d+a/9nGr8Jr2Kxpx4GLX1oroK3fbWier1Kpw+2NrM7/nLwKISI7c6PEmErbv5tR9r64Z+9GnDxospEdru+UNU2bRLBFuvveabdd9RO8ddY7Q9pF3dHrXllII39C4s7e08a96erYpEXERVroqA7nUYfPt4fWcvb/bUNTyGtcnjWJVo6nFkE84BzqPHPHo+jxbznGc26WBqz8uhP36W319P3scVz8dJxM3j3Rxxi3i3QNwy3i0RdxPvbhB3G+9uEVfFuwpwaR3vZuv/wHkEnC3gc9/v2abtkd0fbP5gswiWkPNKAEaKoxyAkeSoAGCkOSoBGImONgCMVEdbAEayIwXASHcS+B8T0p3MADhDYAJgpDwJlEdIeRIoj5DyJFAeIeVJoDxCypNAeYSUJ4HyCClPAuWRmu+S2nM3X/C+L6qJeOfRfe0pSlK5UuFBKlkGwdRhbFj9slh9DjPmm+humj4BjcKTSQ==
