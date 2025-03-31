# Quake .map file linter
# LICENSE: BSD-3-Clause
import glob
import os

import map_linters


def read_config_file(filename: str = "") -> dict:
    """Load a json-formatted configuration file.

    If present, default to `.qmaplint.json` if no file name is specified.
    """
    config = {}
    if not filename and os.path.isfile(".qmaplint.json"):
        filename = ".qmaplint.json"
    elif not filename:
        return config

    if not os.path.isfile(filename):
        exit_error(f"Configuration file {filename} not found!")
    with open(filename, "r") as config_file:
        try:
            config = json.loads(config_file.read())
        except Exception as exc:
            exit_error(f"Failed to read configuration file {filename}! Error: {exc}")
    return config


def exit_error(message: str):
    print(message)
    exit(1)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config_file", default="",
                        help="The configuration file to use.", type=str)
    parser.add_argument("mapfile", nargs="*", default=glob.glob("lq1/maps/src/*/*.map"),
                        help="A list of .map files to read.")

    args = parser.parse_args()
    formatter = map_linters.BaseFormatter()
    config = read_config_file(args.config_file)

    for linter in map_linters.linters():
        for filename in args.mapfile:
            for result in linter(external_config=config).lint(filename):
                formatter.format_result(result)
