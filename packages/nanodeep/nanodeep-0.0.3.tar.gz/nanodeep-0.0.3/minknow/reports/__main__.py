import argparse
import json
import logging
import sys

from run_report_generation_template.render_template import render_template
from run_report_generation_template.transform import transform

ERRORCODE_INPUT_DATA_NOT_VALID_FOR_REPORT = 8
ERRORCODE_UNKNOWN_ERROR_GENERATING_REPORT = 1

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    parser = argparse.ArgumentParser("Parse report arguments")
    parser.add_argument("input_data_file")
    parser.add_argument("output_report_file")

    args = parser.parse_args()

    with open(args.input_data_file, "r", encoding="utf-8") as f:
        json_report_data = json.load(f)
        if len(json_report_data["acquisitions"]) == 0:
            logging.error("No acquisitions available in report data")
            sys.exit(ERRORCODE_INPUT_DATA_NOT_VALID_FOR_REPORT)

    report_data = None
    try:
        report_data = transform(json_report_data)
    except:
        logging.exception(
            "Unknown Error: Input minknow report data failed to generate report input:"
        )
        sys.exit(ERRORCODE_UNKNOWN_ERROR_GENERATING_REPORT)

    with open(args.output_report_file, "w", encoding="utf-8") as report_file:
        report_file.write(render_template(report_data))
