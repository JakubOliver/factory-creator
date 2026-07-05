import argparse

class ArgumentProcessor:
    CLI_DEFAULT_ITERATION = 10
    CLI_DEFAULT_STAGNATION = 10

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
            default = ArgumentProcessor.CLI_DEFAULT_ITERATION
        )

        parser.add_argument(
            "-s",
            "--stagnation",
            required=False,
            type=int,
            help="number of generation after what will be evolution algorithm terminated if no progress occurs",
            default = ArgumentProcessor.CLI_DEFAULT_STAGNATION
        )
        parser.add_argument(
            "-n",
            "--no-browser",
            required=False,
            action="store_true",
            default=False,
            help="use external browser links instead of embedded GUI browser"
        )

        args = parser.parse_args()

        if args.cli and (not args.input or not args.building):
            parser.error("When the cli version is run, then input and building have to be provided!!!")

        return args
