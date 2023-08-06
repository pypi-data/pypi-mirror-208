import argparse
import json
import os
import sys
import subprocess
import time


class ProtocolHandler(object):
    """
    Handler for protocol script interaction.

    The handler is intended to be used to list and start MinKNOW protocol scripts.

    A user should implement list and start methods, then run [run_command] in their main method.
    The handler will then invoke list or start as MinKNOW queries scripts from it.
    """

    def __init__(self):
        self._protocols = []

    def _add_protocol(
        self, name, identifier=None, tags=None, success=True, errors=None
    ):
        """
        Invoke this method from a derived class in order to add a protocol MinKNOW can start.

        :param name: The user readable string for the script to be shown in a UI.
        :param identifier: The machine usable identifier for this script (passed back to start as the args.identifier member)
        :param tags: Tags usable for filtering and grouping scripts. The UI is expected to use these for refining user shown scripts.
        :param success: Indicates whether extraction of tags from the protocol was successful.
        :param errors: String containing information about errors that occurred extracting tags.  None, if there were no errors.
        """
        protocol_data = {
            "name": name,
            "tags": tags if tags is not None else {},
            "identifier": identifier if identifier is not None else name,
            "success": success,
        }
        if errors:
            protocol_data["errors"] = errors

        self._protocols.append(protocol_data)

    def __repr__(self):
        """
        Format the available scripts as a string.
        """
        return json.dumps(self._protocols, indent=2)

    def run_command(self, args, extra_args):
        """
        Run the handler with arguments given by [args]. Any spare arguments should be passed as [extra_args]

        This method will invoke the [start] or [list] methods defined by a derived class to inform MinKNOW
        what scripts are available.

        Once the command is complete, the method calls exit with the required exit code.
        """
        acceptable_commands = ["start", "list", "report"]
        if not hasattr(self, args.command) or args.command not in acceptable_commands:
            raise Exception("Unrecognized command '{}'\n".format(args.command))

        # use dispatch pattern to invoke method with same name
        return getattr(self, args.command)(args, extra_args)

    def list(self, args, extra_args):
        """
        List available protocols to run.
        """
        print(self)
        return 0

    def report(self, args, extra_args):
        """
        Generate custom reports.
        """
        print("No custom reports available.")
        return 0


class FileBasedProtocolHandler(ProtocolHandler):
    """
    A protocol handler specialised for listing a directory tree.
    """

    def _extract_tags(self, protocol_file_path):
        """
        Method for extracting tags from a protocol file.  The file is imported
        as a Python module, and the tags are read from the variable bream_protocol_tags
        within that module.

        Return value is a tuple, consisting of:
        - the dict containing the tags. If there is any point of failure during the
          process, an empty dict is returned
        - a flag indicating success.  This is False if there is any point of failure
          during the process, or True otherwise
        - a string containing the error to be reported.  If there are no errors, this
          is None
        """

        tags = {}

        path, filename = os.path.split(protocol_file_path)
        modulename, ext = os.path.splitext(filename)

        import importlib.util

        try:
            spec = importlib.util.spec_from_file_location(
                modulename, protocol_file_path
            )
        except ImportError as e:
            return (
                tags,
                False,
                "An exception occurred while finding the protocol: {}".format(str(e)),
            )

        try:
            # Suppress warnings, as they will pollute the output, which must
            # be pure Json.
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                protocol = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(protocol)
        except Exception as e:
            return (
                tags,
                False,
                "An exception occurred while loading the protocol: {}".format(str(e)),
            )

        try:
            tags = protocol.bream_protocol_tags
            if type(tags) is not dict:
                return {}, False, "bream_protocol_tags is not a Python dict"

        except AttributeError as e:
            return (
                {},
                False,
                "An exception occurred while reading the value of bream_protocol_tags: {}".format(
                    str(e)
                ),
            )

        return tags, True, None

    def add_directory(self, path, excludes=None, extension=".py"):
        """
        Add a new directory of scripts to the available protocols.

        :param path: The directory to recursively enumerate.
        :param excludes: A list of paths to ignore in the protocols added.
        :param extension: A list of extensions to allow when adding protocols.
        """
        if extension and len(extension) == 0:
            raise Exception("Invalid empty extension specified")
        full_excludes = (
            set(os.path.abspath(p) for p in excludes) if excludes is not None else set()
        )
        for root, subdirs, files in os.walk(path):
            for file in files:
                if not extension or file.endswith(extension):
                    full_path = os.path.abspath(os.path.join(root, file))
                    if full_path not in full_excludes:
                        (
                            protocol_tags,
                            protocol_success,
                            protocol_errors,
                        ) = self._extract_tags(full_path)
                        self._add_protocol(
                            os.path.splitext(file)[0],
                            identifier=full_path,
                            tags=protocol_tags,
                            success=protocol_success,
                            errors=protocol_errors,
                        )

    def start(self, args, extra_args):
        """
        Start the protocol defined by [args.identifier] (interpreted as a file path).
        Any arguments in [extra_args] are passed as script arguments.
        """
        script = args.identifier
        if len(script) == 0:
            raise RuntimeError("Invalid start script with no arguments passed")

        if not os.path.exists(script):
            raise RuntimeError("Invalid script path '{}'".format(script))

        invoke_args = [sys.executable, script] + extra_args
        return subprocess.call(invoke_args)


def build_protocol_handler_argparser():
    """
    Build an argparser which is capable of parsing arguments required for
    the ProtocolHandler interface.
    """
    parser = argparse.ArgumentParser(
        description="Interact with MinKNOW protocol scripts",
    )

    subparsers = parser.add_subparsers(dest="command")

    start_group = subparsers.add_parser("start")
    start_group.add_argument("identifier")

    list_group = subparsers.add_parser("list")
    report_group = subparsers.add_parser("report")
    report_group.add_argument("--output-dir", help="Path to write reports to.")
    report_group.add_argument(
        "--file-name-suffix", help="Suffix to use when naming custom reports."
    )
    report_group.add_argument(
        "--protocol_id", help="Protocol id to generate reports for."
    )
    report_group.add_argument(
        "identifier",
        help="Idenfier of the script to report for (was passed to `start` for the passed protocol_id",
    )

    return parser
