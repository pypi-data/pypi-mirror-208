import argparse
import json
import sys

from .utils import connect_to_manager, find_position


def tag_value(struct):
    name = struct.WhichOneof("tag_value")
    if name is None:
        return None
    if name == "array_value" or name == "object_value":
        return json.loads(getattr(struct, name))
    return getattr(struct, name)


def should_display(filters, tags):
    for key, value in filters:
        try:
            tag = tag_value(tags[key])
            tag_type = type(tag)
            if tag is None:
                print("Ignoring None value for", key, file=sys.stderr)
                return False
            elif tag_type is list:
                if value not in tag:
                    return False
            elif tag_type is dict:
                raise RuntimeError("Cannot filter on objects")
            else:
                if tag_type(value) != tag:
                    return False
        except KeyError:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="""
        List the available protocols.
        """
    )
    parser.add_argument("--host", default="localhost", help="the host to connect to")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="force MinKNOW to reload the protocol list",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="display information about each protocol",
    )
    parser.add_argument(
        "--filter",
        nargs=2,
        metavar=("TAG", "VALUE"),
        action="append",
        default=[],
        help="limit results to protocols with a particular tag value",
    )
    parser.add_argument(
        "position", metavar="POSITION", nargs="?", help="the position to query"
    )
    args = parser.parse_args()

    manager = connect_to_manager(args.host)
    if args.position:
        position = find_position(manager, args.position)
        if not position:
            args.error("Unknown position " + args.position)
    else:
        try:
            position = next(manager.flow_cell_positions())
        except StopIteration:
            args.error("No flow cell positions available to query")

    api = position.connect()
    response = api.rpc.protocol.list_protocols(force_reload=args.reload)
    for protocol in response.protocols:
        if not should_display(args.filter, protocol.tags):
            continue
        print(protocol.identifier)
        if args.verbose:
            print("  name:", protocol.name)
            if protocol.tag_extraction_result.success:
                print("  tags:")
                for name, value in protocol.tags.items():
                    print("    ", name, ": ", tag_value(value), sep="")
            else:
                print(
                    "  Failed to get tags:", protocol.tag_extraction_result.error_report
                )


if __name__ == "__main__":
    main()
