import glob


def check_player_starts(target_file: str) -> bool:
    # We care about Deathmatch starts in all types of maps
    min_starts = {
        "deathmatch": 4
    }
    if "src/dm" not in target_file:
        # For campaign maps only, we want to also check singleplayer and coop starts
        min_starts.update({
            "start": 1,
            "coop": 3
        })

    with open(target_file, "r") as map_file:
        map_data = map_file.read()

    for start_type, min_count in min_starts.items():
        starts_in_map = map_data.count(f"info_player_{start_type}")
        if starts_in_map < min_count:
            print(f"{target_file}:0:0: [min_{start_type}_starts] "
                  f"At least {min_count} {start_type} are required but only {starts_in_map} were found.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mapfile", nargs="*", default=glob.glob("lq1/maps/src/*/*.map"),
                        help="A list of .map files to read.")

    args = parser.parse_args()
    for filename in args.mapfile:
        check_player_starts(filename)
