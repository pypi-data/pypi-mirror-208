import argparse

from .utils import connect_to_manager


def main():
    parser = argparse.ArgumentParser(
        description="""
        List the available flow cell positions.
        """
    )
    parser.add_argument(
        "host", default="localhost", nargs="?", help="The host to connect to."
    )
    parser.add_argument(
        "--simple", action="store_true", help="Only list the names, not the state."
    )
    args = parser.parse_args()

    manager = connect_to_manager(args.host)
    for position in manager.flow_cell_positions():
        if args.simple:
            print(position.name)
        else:
            print(position.name, " (", position.state, ")", sep="")


if __name__ == "__main__":
    main()
