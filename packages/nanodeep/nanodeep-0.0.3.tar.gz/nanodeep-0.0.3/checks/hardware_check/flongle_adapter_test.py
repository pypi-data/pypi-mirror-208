from __future__ import annotations

import copy
import logging
import sys
from typing import Any, Optional

import pandas as pd
from bream4.device_interfaces import device_wrapper
from bream4.device_interfaces.devices.base_device import BaseDeviceInterface
from bream4.toolkit.calibration.calibrate_device import calibrate
from bream4.toolkit.procedure_components.command.keystore import set_hw_check_result
from bream4.toolkit.procedure_components.data_extraction.collect_continuous_data import collect_continuous_data
from bream4.utility.simulation import setup_playback
from utility.config_argparse import config_argument_parser

DEFAULT_CONFIG: dict[str, Any] = {"collection_time": 5, "valid_threshold": 123, "extended_error_message": False}


def main(device: Optional[BaseDeviceInterface] = None, config: Optional[dict] = None) -> None:
    """

    1. Calibrate
    2. Connect all channels to mux 1 with 0mv
    3. record if any saturate
    4. record the std dev/mean for 5 seconds
    5. ping the data
    6. pass/fail based on number of channels that have saturated

    """
    if device is None:
        device = device_wrapper.create_grpc_client()

    if not device.is_flongle:
        raise RuntimeError("Device is not a flongle")

    if config is None:
        config = {}

    logger = logging.getLogger(__name__)

    custom_settings = copy.deepcopy(DEFAULT_CONFIG)
    custom_settings.update(config.get("custom_settings", {}))

    logger.log_to_gui("ctc_script.start")

    if "simulation" in custom_settings:
        setup_playback(device, custom_settings["simulation"])
    else:
        calibrate(device)

    device.start_acquisition()

    data = collect_continuous_data(
        device,
        voltages=[0],
        collection_periods=[custom_settings["collection_time"]],
        aggregations=["mean", "std"],
        muxes=[1],
        clean_field_names=True,
    ).reset_index()

    data.rename(columns={"well": "mux"}, inplace=True)

    # create a new state column with saturated if the offset_0mv_mean is null, not_saturated otherwise
    data["saturated"] = data["offset_0mv_mean"].isnull()
    total_failed = int(data["offset_0mv_mean"].isnull().sum())

    # remove null columns in saturated channels
    records: list[dict] = data.to_dict(orient="records")  # type: ignore
    fat_channel_metrics = [{k: v for k, v in m.items() if pd.notnull(v)} for m in records]
    overall_pass = (device.channel_count - total_failed) > custom_settings["valid_threshold"]

    ping = {
        "config": {"channel_threshold": custom_settings["valid_threshold"]},
        "fat_summary": {"pass": overall_pass, "total_failed": total_failed},
        "fat_channel_metrics": fat_channel_metrics,
    }
    device.send_ping_data(ping)

    device.stop_acquisition()

    if overall_pass:
        set_hw_check_result(device, True)
        logger.log_to_gui("ctc_script.success")
    else:
        set_hw_check_result(device, False)
        logger.info(f"CTC script failed with total failed {total_failed}")
        if custom_settings["extended_error_message"]:
            logger.log_to_gui(
                "ctc_script.failed_more_info",
                params={"total_failed": total_failed, "channel_count": device.channel_count},
            )
        else:
            logger.log_to_gui("ctc_script.failed")


if __name__ == "__main__":
    parser = config_argument_parser()
    args = parser.parse_args()
    sys.exit(main(config=args.config))
