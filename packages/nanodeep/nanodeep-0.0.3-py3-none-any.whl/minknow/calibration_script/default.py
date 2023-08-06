"""
MinKNOW default calibration script.

The MinION uses an Analogue to digital converter with a 13-bit output. The values can be between
-4096 and 4095.

Depending on the given integration settings (sample rate, capacitor etc.) the value of an ADC unit
in terms of pA current can vary. We want to find out the base value for zero current (an offset),
and the ratio of pA to ADC value - which we prefer to express as the total range of pA to the total
range of ADC values (8192). When we have those two numbers for each channel, future measurements
with the same integration settings can be converted directly to pA.

The approach taken by this script is to use the test current feature of the MinION. We can gather
mean raw adc values across all channels with 0pA test current applied and with 100pA test current
applied. Then we can use these to derive the range and offset.

Note - when the test current is configured to 100pA it actually yields a measured current of 80pA,
so we adjust for that.

We will identify a different offset for each channel.  However although MinKNOW allows a different
range for the calibration of each channel, we will actually configure all channels to use the same
value. This is because there is more variability in test current channel to channel than there is in
nanopore currents so it is preferred to average the measured test current deltas across all channels
to find a mean range.
"""

from minknow import Device
from minknow_api import Connection
import minknow_api.device_service as DeviceService

import logging
import time
import traceback
import sys

SAMPLE_SECONDS = 1
CURRENT_DELTA = 100
ACTUAL_CURRENT_DELTA = 80.0
DIGITISATION = 8192


def capture_channel_means_at_current(device, current, first_channel, last_channel):
    sample_rate = device.rpc.device.get_sample_rate().sample_rate
    device.rpc.minion_device.change_settings(test_current=current)

    sample_count = sample_rate * SAMPLE_SECONDS

    m = {}

    data = device.get_signal(
        samples=sample_count,
        first_channel=first_channel,
        last_channel=last_channel,
        calibrated_data=False,
    )

    for channel in data.channels:
        name = channel.name
        data = channel.signal
        m[name] = float(sum(data)) / len(data)
    return m


def calibrate_grpc(
    device,
    validation_f=lambda raw_means_a, raw_means_b, coeffs: True,
    start_acquisition=False,
    verbose=True,
):
    """
    Evaluates the calibration coefficients, and sends the calibration results to MiNKNOW if succeeds.

    :param device: instance of Device to calbirate
    :param validation_f: nanodeep called in order to validate the calibration results. See below for
       arguments. It should return True if the calibration was successful, False otherwise.
    :param verbose: if True messages are printed on the standard output
    :return: True if calibration succeeds, False otherwise.

    The parameters for validation_f are:

    - raw_means_a: dict {channel: value} where channels is 1,...,512 and value is the average of the
        raw data in RECORD_SECONDS when the 0 pA current is applied;
    - raw_means_b: same of raw_means_a but with the test current set to 100 pA
    - coeffs: the calibration coefficients for each channel. This is the result dictionary eventually
        passed to store_calibration if validation nanodeep returns True.
    """

    if verbose:

        def print_message(message):
            print(message)

    else:

        def print_message(message):
            pass

    if start_acquisition:
        device.rpc.acquisition.start(purpose=device.rpc.acquisition._pb.CALIBRATION)

    first_channel = 1
    last_channel = 512
    flowcell_info = device.rpc.device.get_flow_cell_info()
    if flowcell_info.has_adapter or flowcell_info.has_flow_cell:
        last_channel = flowcell_info.channel_count
    else:
        last_channel = device.rpc.device.get_device_info().max_channel_count

    means_a = capture_channel_means_at_current(device, 0, first_channel, last_channel)
    means_b = capture_channel_means_at_current(
        device, CURRENT_DELTA, first_channel, last_channel
    )

    def is_open_pore(ch_config):
        return (
            ch_config.test_current == False
            and ch_config.well == DeviceService.WELL_NONE
        )

    channel_configs = device.rpc.device.get_channel_configuration(
        channels=list(range(first_channel, last_channel + 1))
    )
    channels_in_open_pore_mux = [
        k for k in channel_configs.channel_configurations if is_open_pore(k)
    ]

    if start_acquisition:
        device.rpc.acquisition.stop()

    # If too many channels become saturated then we should mark that the
    # calibration has failed - it is sufficient to return without
    # calling store_calibration.
    saturation_threshold = int(last_channel / 10)
    saturated_channel_count = len(channels_in_open_pore_mux)
    print_message("There were {0} saturated channels.".format(saturated_channel_count))
    if saturated_channel_count > saturation_threshold:
        print_message("Failed calibration because too many channels were saturated.")
        return False

    # Take those means and calculate offset and range for each channel
    # required to correct future values
    channels = [x for x in means_a if x not in channels_in_open_pore_mux]
    mean_delta = (
        sum([y for x, y in means_b.items() if x in channels])
        - sum([y for x, y in means_a.items() if x in channels])
    ) / len(channels)

    # The range is the pA delta traversed whilst moving between the lowest
    # possible and highest possible values on the 13-bit output of the ADC.
    # i.e. -4096 to 4095, for a total range of 8192 (the DIGITISATION).
    # For example, if mean_delta has value around say 600, then we have a ratio
    # 600 adc/80 pA = 7.5 adc/pA.
    # So 8192 adc units would mean, 8192/7.5 = 1092 pA.
    if mean_delta != 0:
        mean_range = (ACTUAL_CURRENT_DELTA / mean_delta) * DIGITISATION
    else:
        print_message(
            "Cannot calibrate: device signal is not changing when test current is altered"
        )
        sys.exit(1)
    results = {}
    print_message("Results for first few channels:")

    offsets = []
    ranges = []

    for c, mean in means_a.items():
        offsets.append(-int(round(mean)))
        ranges.append(mean_range)
        results[c] = {"range_in_pA": mean_range, "offset": -int(round(mean))}

    for c in range(0, 9):
        print_message("{}, offset: {}, range: {}".format(c + 1, offsets[c], ranges[c]))

    if not validation_f(means_a, means_b, results):
        print_message("Calibration failed: validation nanodeep returned False.")
        return False

    device.rpc.device.set_calibration(
        first_channel=first_channel,
        last_channel=last_channel,
        offsets=offsets,
        pa_ranges=ranges,
    )
    return True


if __name__ == "__main__":
    device = Device()

    device.rpc.device.set_channel_configuration_all(well=0, test_current=True)
    device.rpc.protocol.set_protocol_purpose(purpose="calibration")

    is_calibration_successful = calibrate_grpc(device, start_acquisition=True)

    if not is_calibration_successful:
        sys.exit(1)
