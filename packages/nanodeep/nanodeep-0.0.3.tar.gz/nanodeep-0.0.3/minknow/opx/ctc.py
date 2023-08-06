"""
CTC

This simulates DNA reads when using a CTC flow-cell. It is intended to be
used for testing that software and hardware can process the output from
experiments.

Copyright (c) 2008-2021 Oxford Nanopore Technologies PLC. All rights reserved.

"""

__author__ = "Richard Crewe"

import time
import random
import logging
import numpy as np

from google.protobuf.wrappers_pb2 import BoolValue, StringValue

import minknow_dev.acqhelpers
from minknow.opx.calibration.calibration_script import calibrate_grpc
import minknow_api

PixelSettings = minknow_api.promethion_device_service.PixelSettings
InputWell = PixelSettings.InputWell
MAX_RAMP_VOLTAGE_ADC = 2048


class RampVoltageCalibration:
    FirstCalibPoint = -10
    SecondCalibPoint = 30

    def __init__(self, adc_first_pa, adc_second_pa):
        y_delta = adc_second_pa - adc_first_pa
        x_delta = self.SecondCalibPoint - self.FirstCalibPoint
        self.grad = y_delta / x_delta
        self.intersect = adc_second_pa - (self.grad * self.SecondCalibPoint)

    def ramp_voltage_for_pa(self, pa):
        return int((pa - self.intersect) / self.grad)


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


def find_ramp_calibration(device, logger):
    def sample_pa_range():
        lower_cutoff = -1300
        count = 4000
        first_channel = 1
        last_channel = device.flow_cell_info.channel_count
        calibration = device.rpc.device.get_calibration(
            first_channel=first_channel, last_channel=last_channel
        )
        data = device.get_signal(
            samples=count,
            first_channel=first_channel,
            last_channel=last_channel,
            calibrated_data=False,
        )

        failed_channels = 0
        channels_calib_means = np.array([])
        assert len(data.channels) == len(calibration.offsets)
        for i, channel in enumerate(data.channels):
            if min(channel.signal) > lower_cutoff:
                calibrated = (channel.signal + calibration.offsets[i]) / float(
                    calibration.digitisation / calibration.pa_ranges[i]
                )
                channels_calib_means = np.append(
                    channels_calib_means, calibrated.mean()
                )
            else:
                failed_channels += 1

        logger.info(
            "%s channels were below lower cutoff when sampling pa values",
            failed_channels,
        )
        return channels_calib_means.mean()

    device.rpc.promethion_device.change_device_settings(
        ramp_voltage=RampVoltageCalibration.FirstCalibPoint
    )
    clear_saturation(device, PixelSettings.OVERLOAD_LATCH_OFF)
    first = sample_pa_range()
    logger.info(
        "Found ramp value of %s gives pa of %s",
        RampVoltageCalibration.FirstCalibPoint,
        first,
    )

    device.rpc.promethion_device.change_device_settings(
        ramp_voltage=RampVoltageCalibration.SecondCalibPoint
    )
    clear_saturation(device, PixelSettings.OVERLOAD_LATCH_OFF)
    second = sample_pa_range()
    logger.info(
        "Found ramp value of %s gives pa of %s",
        RampVoltageCalibration.SecondCalibPoint,
        second,
    )

    calib = RampVoltageCalibration(first, second)
    return calib


def run_squiggle(device, logger, squiggle):
    """
    Apply a squiggle to the model voltage simulating bases passing through the pore.
    """
    logger.info("DNA")
    for x in squiggle:
        device.rpc.promethion_device.change_device_settings(ramp_voltage=x[0])
        time.sleep(x[1])


def generate_squiggle(min_strand, max_strand):
    """
    Generate a squiggle, an array of tuples of voltages and times that look like DNA passing through a pore.
    """
    voltages = [
        random.randint(min_strand, max_strand) for x in range(random.randint(10, 120))
    ]
    times = [round(random.uniform(0.1, 0.5), 1) for x in range(len(voltages))]
    return list(zip(voltages, times))


def go_to_open_pore(device, logger, ramp_level):
    """
    Simulate an open pore for a period of time
    """
    logger.info("Open pore")
    device.rpc.promethion_device.change_device_settings(ramp_voltage=ramp_level)
    time.sleep(random.randint(1, 3))


def adjust_analysis_config(device):
    device.rpc.analysis_configuration.set_analysis_enabled_state(enable=True)

    # modify analysis configuration to suit CTC simulation of sequencing
    analysis_config = device.rpc.analysis_configuration.get_analysis_configuration()
    analysis_config.read_detection.minimum_delta_mean = 30
    analysis_config.read_classification.parameters.ClearField(
        "rules_in_execution_order"
    )
    analysis_config.read_classification.parameters.rules_in_execution_order.extend(
        [
            "pore      = (median,gt,30)&(median,lt,85)&(median_sd,lt,5)",
            "strand    = (local_median,gt,3)&(local_median,lt,15)&(local_range,gt,2)&(local_range,lt,25)&(local_median_sd,lt,3)&(drift,lt,12)&(duration,gt,2)",
        ]
    )

    analysis_config.ClearField("channel_states")
    ChannelStates = minknow_api.analysis_configuration_service.ChannelStates
    Logic = ChannelStates.Logic
    state = analysis_config.channel_states["strand"]
    state.logic.criteria = "read_classification_sequence"
    state.logic.pattern = ".*"
    state.logic.rank = 0

    device.rpc.analysis_configuration.set_analysis_configuration(analysis_config)


def do_ctc(device, logger, run_time):
    logger.info("Starting CTC run")

    writer_config = device.rpc.analysis_configuration.get_writer_configuration()
    # enable raw and events
    bulk = writer_config.bulk
    bulk.compression_level = 1
    bulk.file_pattern = "ctc_bulk.fast5"
    bulk.raw.all_channels = False
    bulk.events.all_channels = True
    bulk.reads.all_channels = True
    bulk.ClearField("multiplex")
    bulk.ClearField("channel_states")
    bulk.device_metadata = True
    bulk.device_commands = True
    device.rpc.analysis_configuration.set_writer_configuration(writer_config)

    device.rpc.promethion_device.change_device_settings(
        sampling_frequency=4000,
        ramp_voltage=0,
        bias_voltage=0,
        saturation_control_enabled=False,
    )
    device.rpc.promethion_device.change_pixel_settings(
        pixel_default=PixelSettings(
            gain_multiplier=PixelSettings.INTGAIN_2,
            gain_capacitor=PixelSettings.INTCAP_200fF,
            overload_mode=PixelSettings.OVERLOAD_LATCH_OFF,
            cutoff_frequency=PixelSettings.LPF_20kHz,
            bias_current=PixelSettings.BIAS_NOMINAL,
        )
    )

    adjust_analysis_config(device)

    calibrate_grpc(device, start_acquisition=True)

    with minknow_dev.acqhelpers.acquire_data(device.rpc) as acqinfo:
        device.rpc.promethion_device.change_pixel_settings(
            pixel_default=PixelSettings(
                membrane_simulation_enabled=BoolValue(value=True),
            )
        )

        clear_saturation(device, PixelSettings.OVERLOAD_LATCH_OFF)

        logger.info("Finding squiggle levels")
        ramp_calib = find_ramp_calibration(device, logger)

        ramp_value = ramp_calib.ramp_voltage_for_pa(
            55
        )  # Read classifications specify pore is 55pa.
        if ramp_value > MAX_RAMP_VOLTAGE_ADC:
            logging.error(
                f"The ramp-voltage of {ramp_value} ADC units selected for open-pore levels is greater than the maximum of {MAX_RAMP_VOLTAGE_ADC}. "
                f"This is indicative of a failing flow-cell."
            )
            return False
        logging.info("Using open pore level of {} ramp adc".format(ramp_value))
        min_strand = ramp_calib.ramp_voltage_for_pa(
            3
        )  # Read classifications specify strand min is 3pa.
        max_strand = ramp_calib.ramp_voltage_for_pa(
            15
        )  # Read classifications specify strand max is 15pa.
        if min_strand > MAX_RAMP_VOLTAGE_ADC or max_strand > MAX_RAMP_VOLTAGE_ADC:
            logging.error(
                f"The ramp-voltage of {ramp_value} ADC units selected for open-pore levels is greater than the maximum of {MAX_RAMP_VOLTAGE_ADC}. "
                f"This is indicative of a failing flow-cell."
            )
            return False
        logging.info(
            "Using squiggle level of {}-{} ramp adc".format(min_strand, max_strand)
        )

        clear_saturation(device, PixelSettings.OVERLOAD_LATCH_OFF)

        logger.info("Starting sequencing simulation")
        # run until the time-limit is reached
        stop_time = time.time() + run_time
        while time.time() < stop_time:
            squiggle = generate_squiggle(min_strand, max_strand)
            run_squiggle(device, logger, squiggle)
            go_to_open_pore(device, logger, ramp_value)

            acquisition = device.rpc.acquisition.get_acquisition_info()
            logger.info("Found %s reads so far", acquisition.yield_summary.read_count)
        logger.info("Simulation complete")
    return True
