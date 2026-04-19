from os import path, mkdir
import json

class FileUtil:
    @staticmethod
    def validate_json_file(file_path: str) -> None:
        """
        Validates whether the json file is valid.

        :param file_path: Path to the json file
        """

        if not path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} does not exist!")

        try:
            with open(file_path) as json_file:
                json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            raise f"{file_path} is not a valid json file! ({e})"

    @staticmethod
    def create_output_dir() -> None:
        """
        Creates the output directory.
        """

        if not path.isdir("output"):
            mkdir("output")