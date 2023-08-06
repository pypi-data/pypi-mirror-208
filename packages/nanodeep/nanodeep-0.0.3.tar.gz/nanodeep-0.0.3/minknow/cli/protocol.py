from minknow.protocols import FileBasedProtocolHandler, build_protocol_handler_argparser

import os
import sys


class FileBasedProtocolHandlerWithCustomReport(FileBasedProtocolHandler):
    def report(self, args, extra_args):
        """
        Generate custom reports.
        """

        if not args.output_dir:
            raise Exception("Invalid output dir passed to report")

        if not args.protocol_id:
            raise Exception("Invalid protocol id passed to report")

        with open(
            "%s/custom_report_%s.txt" % (args.output_dir, args.file_name_suffix), "w"
        ) as file:
            file.write("protocol_id: %s" % args.protocol_id)

        return 0


if __name__ == "__main__":
    recipes_handler = FileBasedProtocolHandlerWithCustomReport()
    recipes_handler.add_directory(os.path.dirname("python/recipes/"))

    parser = build_protocol_handler_argparser()

    args, unknown = parser.parse_known_args()
    exit(recipes_handler.run_command(args, unknown))
