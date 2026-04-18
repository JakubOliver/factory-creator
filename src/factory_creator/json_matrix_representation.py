import base64
import zlib
import sys
import json


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
            json_file = BluePrintRepresentation.decode(f.read())
            BluePrintRepresentation.encode(json_file)