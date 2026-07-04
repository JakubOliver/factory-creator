import argparse

class ArgumentProcessor:
    @staticmethod
    def process_arguments():
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-c",
            "--cli",
            required=False,
            action="store_true",
            default=False,
            help="denotes whether to use GUI or not"
        )
        parser.add_argument(
            "-i",
            "--input",
            required=False,
            type=str,
            help="input file"
        )

        parser.add_argument(
            "-b",
            "--building",
            required=False,
            type=str,
            help="building name"
        )

        parser.add_argument(
            "-t",
            "--iteration",
            required=False,
            type=int,
            help="number of iteration of evolution",
            default = 10 # TODO: const
        )

        args = parser.parse_args()

        if args.cli and (not args.input or not args.building):
            parser.error("When the cli version is run, then input and building have to be provided!!!")

        return args