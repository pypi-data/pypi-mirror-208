from __future__ import annotations

import logging
import sys
from typing import Optional

from bream4.device_interfaces import device_wrapper
from bream4.device_interfaces.devices.base_device import BaseDeviceInterface
from bream4.toolkit.calibration.calibrate_device import calibrate
from bream4.toolkit.procedure_components.command.keystore import set_hw_check_result
from utility.config_argparse import config_argument_parser


def main(device: Optional[BaseDeviceInterface] = None, config: Optional[dict] = None) -> None:
    """
    This script performs a hardware check

    The following things happen during the script:

    * Attempt to calibrate the device

    """
    # Setup
    if device is None:
        device = device_wrapper.create_grpc_client()

    if config is None:
        config = {}

    logger = logging.getLogger(__name__)

    logger.log_to_gui("ctc_script.start")

    try:
        if "simulation" not in config.get("custom_settings", {}):
            calibrate(device, purpose="ctc")
        set_hw_check_result(device, True)
        logger.log_to_gui("ctc_script.success")
    except RuntimeError:
        set_hw_check_result(device, False)
        logger.error("ctc_script.failed")


if __name__ == "__main__":
    parser = config_argument_parser()
    args = parser.parse_args()
    sys.exit(main(config=args.config))
