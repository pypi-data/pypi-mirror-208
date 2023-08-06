#!/usr/bin/python
"""
MinKNOW OPX calibration script.

OPX (currently just PromethION) devices use an Analogue to Digital Converter with an 11-bit unsigned
output. The values can be between 0 and 2047.

Depending on the given integration settings (sample rate, capacitor etc.) the value of an ADC unit
in terms of pA current can vary. We want to find out the base value for zero current (an offset),
and the ratio of pA to ADC value - which we prefer to express as the total range of pA to the total
range of ADC values (2048). When we have those two numbers for each channel, future measurements
with the same integration settings can be converted directly to pA.

To find those numbers we use the chip's ability to produce a known test current. We can gather mean
raw adc values across all channels with 0pA test current applied and with 100pA test current
applied. Then we can use these to derive the range and offset.
"""
import sys
import time
import traceback

import logging
import minknow
import minknow_api
from minknow import Device
from minknow_api import Connection

RECORD_SECONDS = 1
CHANNEL_COUNT = 3000
DIGITISATION = 2048
VERBOSE_CHANNELS = [1, 2, 36, 249, 250, 251, 511, 512, 513, 2001]
FRAME_TIME_DIFF = 21.1 * 10**-6
V_REF = 1.49
PICOAMP_CONVERT = 1 * 10**12  # conversion to pico-amps
ADC_GAIN = 1 / 0.92


def range_for_settings(sample_rate, gcds, cfb):
    actual_cfb = float(cfb) * 10**-15
    tcds = (1.0 / sample_rate) - FRAME_TIME_DIFF
    factor = (V_REF / (gcds * ADC_GAIN)) * (actual_cfb / tcds)
    rng = PICOAMP_CONVERT * factor
    return rng


def range_for_channel(sample_rate, pixel_settings, channel):
    PixelSettings = minknow_api.promethion_device_service.PixelSettings
    gcds = 4 if pixel_settings.gain_multiplier == PixelSettings.INTGAIN_4 else 2

    cfb = 0
    if pixel_settings.gain_capacitor == PixelSettings.INTCAP_100fF:
        cfb = 100
    if pixel_settings.gain_capacitor == PixelSettings.INTCAP_200fF:
        cfb = 200
    if pixel_settings.gain_capacitor == PixelSettings.INTCAP_500fF:
        cfb = 500
    if pixel_settings.gain_capacitor == PixelSettings.INTCAP_600fF:
        cfb = 600

    return range_for_settings(sample_rate, gcds, cfb)


def capture_channel_means_at_current_pA(device):
    sample_rate = device.rpc.device.get_sample_rate().sample_rate

    print("Capturing data at {} Hz".format(sample_rate))

    sample_count = RECORD_SECONDS * sample_rate
    data = device.get_signal(
        samples=sample_count,
        first_channel=1,
        last_channel=CHANNEL_COUNT,
        calibrated_data=False,
    )

    m = {}
    for channel in data.channels:
        name = channel.name
        data = channel.signal
        m[name] = float(sum(data)) / len(data)
        if name in VERBOSE_CHANNELS:
            print("channel={}, values={}... mean={}".format(name, data, m[name]))
    return m


def clear_saturation(device, overload_mode):
    PixelSettings = minknow_api.promethion_device_service.PixelSettings

    device.rpc.promethion_device.change_device_settings(
        saturation_control_enabled=False
    )

    device.rpc.promethion_device.change_pixel_settings(
        pixel_default=PixelSettings(overload_mode=PixelSettings.OVERLOAD_CLEAR)
    )
    time.sleep(0.2)

    device.rpc.promethion_device.change_pixel_settings(
        pixel_default=PixelSettings(overload_mode=overload_mode)
    )
    time.sleep(0.2)

    device.rpc.promethion_device.change_device_settings(saturation_control_enabled=True)


def calibrate_grpc(device, start_acquisition=False):
    PixelSettings = minknow_api.promethion_device_service.PixelSettings

    if start_acquisition:
        device.rpc.acquisition.start(purpose=device.rpc.acquisition._pb.CALIBRATION)

    device.rpc.promethion_device.change_device_settings(ramp_voltage=0)

    device.rpc.promethion_device.change_pixel_settings(
        pixel_default=PixelSettings(input=PixelSettings.InputWell())
    )

    clear_saturation(device, PixelSettings.OVERLOAD_LATCH_OFF)

    means_a = capture_channel_means_at_current_pA(device)

    # TODO Count channels which saturated during calibration.
    saturated_channels = []

    if start_acquisition:
        device.rpc.acquisition.stop(wait_until_ready=True)

    # If too many channels become saturated then we should mark that the
    # calibration has failed - it is sufficient to return without
    # calling store_calibration.
    print("There were {0} saturated channels.".format(len(saturated_channels)))
    if len(saturated_channels) > 51:
        print("Failed calibration because too many channels were saturated.")
        return False

    ### Take the means and calculate offset and range for each channel
    ### required to correct future values

    sample_rate = device.rpc.device.get_sample_rate().sample_rate
    current_settings = device.rpc.promethion_device.get_pixel_settings(
        pixels=list(range(1, CHANNEL_COUNT + 1))
    ).pixels
    channels = [x for x in means_a.keys() if x not in saturated_channels]
    # The range is the pA delta traversed whilst moving between the lowest
    # possible and highest possible values on the 11-bit output of the ADC.
    # i.e. 0 to 2048, as given by the DIGITISATION.
    # For example, if mean_delta has value around say 600, then we have a ratio
    # 600 adc/100 pA = 6 adc/pA.
    # So 2048 adc units would mean = 341 pA.

    offsets = []
    ranges = []
    for c in channels:
        offsets.append(-int(round(means_a[c])))
        ranges.append(range_for_channel(sample_rate, current_settings[c - 1], c))

    print("Results for some channels:")
    for c in VERBOSE_CHANNELS:
        print("channel={}, range={} offset={}".format(c, ranges[c - 1], offsets[c - 1]))

    device.rpc.device.set_calibration(
        first_channel=1, last_channel=CHANNEL_COUNT, offsets=offsets, pa_ranges=ranges
    )
    return True


if __name__ == "__main__":
    device = Device()
    is_calibration_successful = calibrate_grpc(device, start_acquisition=True)

    if not is_calibration_successful:
        sys.exit(1)
