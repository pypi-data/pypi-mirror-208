import argparse

from .utils import connect_to_manager, find_position


def main():
    parser = argparse.ArgumentParser(
        description="""
        Run a protocol in a running MinKNOW instance.
        """
    )
    parser.add_argument("--host", default="localhost", help="the host to connect to")

    parser.add_argument("--sample-id", help="the sample ID to set")
    parser.add_argument(
        "--experiment-name",
        "--group-id",
        help="the experiment name (aka protocol group ID) to set",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="wait for the protocol to finish before returning",
    )
    parser.add_argument(
        "--wait-timeout",
        type=float,
        default=0.0,
        help="amount of time to wait when --wait is specified (default: forever)",
    )
    parser.add_argument(
        "position", metavar="POSITION", help="the position to run the protocol at"
    )
    parser.add_argument(
        "protocol",
        metavar="PROTOCOL",
        help="the identifier of the protocol to run (see list_protocols)",
    )
    parser.add_argument(
        "args", metavar="ARGS", nargs="*", help="arguments for the protocol"
    )
    args = parser.parse_args()

    manager = connect_to_manager(args.host)
    position = find_position(manager, args.position)
    if not position:
        args.error("Unknown position " + args.position)

    api = position.connect()
    user_info = api.rpc.protocol._pb.ProtocolRunUserInfo()
    if args.sample_id:
        user_info.sample_id.value = args.sample_id
    if args.experiment_name:
        user_info.protocol_group_id.value = args.experiment_name
    result = api.rpc.protocol.start_protocol(
        identifier=args.protocol, args=args.args, user_info=user_info
    )
    print("Protocol run ID:", result.run_id)

    if args.wait:
        run_info = api.rpc.protocol.wait_for_finished(
            run_id=result.run_id, timeout=args.wait_timeout
        )
        state_str = api.rpc.protocol._pb.ProtocolState.Name(run_info.state)
        print("Protocol finished with state", state_str)


if __name__ == "__main__":
    main()
