from collections.abc import Generator
from . import Result, Linter


class PlayerStartsLinter(Linter):
    def __init__(self, external_config: dict = {}):
        default_config = {
            "minimum_starts": {
                "start": 1,
                "deathmatch": 4,
                "coop": 4
            }
        }
        super(PlayerStartsLinter, self).__init__(default_config, external_config)

    def lint(self, target_file: str) -> Generator[Result]:
        with open(target_file, "r") as map_file:
            map_data = map_file.read()
        for start_type, min_count in self.config["minimum_starts"].items():
            if map_data.count(f"info_player_{start_type}") < min_count:
                yield Result(filename=target_file,
                             message=f"Not enough {start_type} starts, expecting {min_count}",
                             level="ERROR:",
                             rule=f"min_{start_type}_starts")
