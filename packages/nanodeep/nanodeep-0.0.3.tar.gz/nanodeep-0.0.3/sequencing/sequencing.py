from __future__ import annotations

import copy
import logging
import sys
import time
from typing import Optional

import bream4.toolkit.procedure_components.command.keystore as keystore
from bream4.device_interfaces import device_wrapper
from bream4.device_interfaces.devices.base_device import BaseDeviceInterface
from bream4.toolkit.calibration.calibrate_device import calibrate
from bream4.toolkit.procedure_components.command.phase_management import ProtocolPhaseManagement
from bream4.toolkit.procedure_components.feature_manager import FeatureManager
from bream4.toolkit.procedure_components.sequencing_features.channel_disable import ChannelDisable
from bream4.toolkit.procedure_components.sequencing_features.drift_correction import DriftCorrection
from bream4.toolkit.procedure_components.sequencing_features.experiment_pauser import ExperimentPauser
from bream4.toolkit.procedure_components.sequencing_features.feature_manager_triggers import GlobalTrigger
from bream4.toolkit.procedure_components.sequencing_features.group_manager import GroupManager
from bream4.toolkit.procedure_components.sequencing_features.internal_state_information import InternalStateInformation
from bream4.toolkit.procedure_components.sequencing_features.mux_scan import MuxScan
from bream4.toolkit.procedure_components.sequencing_features.mux_scan_trigger import MuxScanTrigger
from bream4.toolkit.procedure_components.sequencing_features.profiler import Profiler
from bream4.toolkit.procedure_components.sequencing_features.progressive_unblock import ProgressiveUnblock
from bream4.toolkit.procedure_components.sequencing_features.static_drift_correction import StaticDriftCorrection
from bream4.toolkit.procedure_components.sequencing_features.temperature_adjust import TemperatureManager
from bream4.toolkit.procedure_components.voltage_operations import global_flick, maintain_relative_unblock_voltage
from bream4.utility.simulation import setup_playback
from utility.config_argparse import config_argument_parser
from utility.config_file_utils import find_path, recursive_merge, set_path

DEFAULTS = {
    "run_time": 36000,
    "start_bias_voltage": -180,
    "temperature": {"target": 34.0, "tolerance": 0.5},
    "mux_scan": {"enabled": False},
    "group_manager": {"swap_out_disabled_channels": False, "global_mux_change": {"enabled": False}},
    "effective_unblock_voltage": 120,  # To aid backwards compatibility due to new calculation
}


def channel_wind_down_loop(config: dict, device: BaseDeviceInterface) -> None:
    """Performs a channel wind down -> Gives a chance for strands to exit.

    Config options: ::

      {
        "channel_states_disable": Config to pass to ChannelDisable
        "progressive_unblock": Config to pass to progressive unblock
        "timeout": How long to give the wind down to finish (seconds) (default 60)
      }

    After this nanodeep has run, channels will be what well they were in,
    but with bias voltage at 0.

    :param config: config options
    :param device: MinKNOW device wrapper
    """

    logger = logging.getLogger(__name__)
    logger.info("Performing Channel Wind Down")

    channel_disable_config = config.get("channel_states_disable", {"enabled": False})
    channel_disable = ChannelDisable(channel_disable_config, device)

    progressive_unblock_config = config.get("progressive_unblock", {"enabled": False})
    progressive_unblock = ProgressiveUnblock(progressive_unblock_config, device)

    # Cooling down causes channels to swap to well 0 so that no more strand is processed
    # When we are done, we want it restored
    old_state = device.get_channel_configuration()
    old_channel_config = {channel: data.well for (channel, data) in old_state.items()}

    with FeatureManager(device) as feature_manager:
        if channel_disable_config["enabled"]:
            feature_manager.start(
                channel_disable,
                triggers_on=[feature_manager.channel_update()],
                on_trigger=feature_manager.just_run,
                allow_exit_manager_sleep=True,
            )
        if progressive_unblock_config["enabled"]:
            feature_manager.start(
                progressive_unblock,
                triggers_on=[feature_manager.channel_update(), feature_manager.interval(0.1)],
                on_trigger=feature_manager.just_run,
            )
        feature_manager.sleep(config.get("timeout", 60))

    device.set_bias_voltage(0)

    # Finished so restore the channel configuration
    device.unlock_channel_states(device.get_channel_list())
    device.set_channels_to_well(old_channel_config)


def mux_scan_loop(mux_scan_feature: MuxScan, config: dict, device: BaseDeviceInterface) -> dict[int, list[int]]:
    """Perform a mux scan, including any background features

    Config options: ::

      {
        "mux_scan_progressive_unblock": Config for progressive unblock during the scan,
        "mux_scan": Config for mux scan
      }

    :param running_voltage: What voltage to run the mux scan at
    :param config: Config options
    :param device: MinKNOW device wrapper
    :returns: channel -> [well order]
    :rtype: dict of lists

    """
    logger = logging.getLogger(__name__)

    mux_scan_progressive_unblock_config = config.get("mux_scan_progressive_unblock", {"enabled": False})
    mux_scan_progressive_unblock = ProgressiveUnblock(mux_scan_progressive_unblock_config, device)

    logger.info("Performing a Mux Scan")

    with FeatureManager(device) as feature_manager:
        if device.is_flongle:
            logger.log_to_gui("sequencing.channel_scan")
        else:
            logger.log_to_gui("sequencing.mux_scan")

        if mux_scan_progressive_unblock_config["enabled"]:
            feature_manager.start(
                mux_scan_progressive_unblock,
                triggers_on=[feature_manager.channel_update(), feature_manager.interval(0.1)],
                on_trigger=feature_manager.just_run,
            )

        keystore.set_state(device, "RUNNING_MUX_SCAN")

        # Start the mux scan
        mux_scan_feature.run_mux_scan(feature_manager=feature_manager)
        mux_groups = mux_scan_feature.get_pore_group()
        feature_manager.stop_all()

    return mux_groups


def main(device: Optional[BaseDeviceInterface] = None, config: Optional[dict] = None) -> None:
    """This runs a sample sequencing script
    * Wait for a certain temperature to be reached
    * Calibrate device
    * Start acquisition
    * Start any features specified in the config
    * Continue for run_time
    * End acquisition

    Also potentially do a mux scan at set intervals

    :param device: Device to run sequencing on. Attempts to find one if not specified
    :param config: Dict of config to run with
    """

    # ----------- DEVICE SETUP -------------- #
    # Grab a device if not specified
    if not device:
        device = device_wrapper.create_grpc_client()
    if not config:
        config = {}

    logger = logging.getLogger(__name__)

    # Grab settings and merge them with the DEFAULTS
    # i.e. If any are not present in the config file, go with the defaults
    settings = config.get("custom_settings", {})
    default_settings = copy.deepcopy(DEFAULTS)
    recursive_merge(default_settings, settings)
    settings = default_settings

    if "interval" not in settings["mux_scan"] or settings["mux_scan"]["interval"] <= 0:
        settings["mux_scan"]["interval"] = settings["run_time"]

    phase_management = ProtocolPhaseManagement(device)
    phase_management.set_phase("INITIALISING")

    # Wait for temperature to be reached
    device.set_temperature(**settings["temperature"])

    if "simulation" in settings:
        setup_playback(device, settings["simulation"])
    else:
        calibrate(device, output_bulk=False, ping_data=False, purpose="sequencing")

    # ----------- SEQUENCING SETUP ------------ #

    # Allow GUI to say how long this experiment is going to take
    device.set_estimated_run_time(settings["run_time"])

    # Use GUI args to set the min_read_length if needed
    if "min_read_length_base_pairs" in settings:
        read_length = settings["min_read_length_lookup"][str(settings["min_read_length_base_pairs"])]
        logger.info(f"Setting read_filters.event_count_min={read_length} in the writer config")
        wc = device.get_writer_configuration()
        set_path("read_filters.event_count_min", wc, read_length)
        device.set_writer_configuration(wc)

    # Start acquisition, making sure to send extra data
    device.start_acquisition(purpose="sequencing")
    current_bias_voltage = settings["start_bias_voltage"]

    # This value is used to track the voltage changes across a sequencing cycles, its used to calculate an adjustment
    # of the voltage for the next mux scan and sequencing sections.
    start_bias_voltage = settings["start_bias_voltage"]
    logger.log_to_gui("sequencing.start")
    temperature = settings["temperature"]["target"]
    tolerance = settings["temperature"]["tolerance"]

    # Give UI extra information
    keystore.set_protocol_data(
        device,
        speed_min=settings.get("translocation_speed_min", 0),
        speed_max=settings.get("translocation_speed_max", 0),
        q_score_min=find_path("basecaller_configuration.read_filtering.min_qscore", config) or 0,
        q_score_max=settings.get("q_score_max", 0),
        temp_min=temperature - tolerance,
        temp_max=temperature + tolerance,
    )

    # Update core using new 5.0 methods
    device.update_acquisition_display_targets(
        q_score_target=(
            find_path("basecaller_configuration.read_filtering.min_qscore", config) or 0,
            settings.get("q_score_max", 0),
        ),
        temperature_target=(temperature - tolerance, temperature + tolerance),
        translocation_speed_target=(
            settings.get("translocation_speed_min", 0),
            settings.get("translocation_speed_max", 0),
        ),
    )

    # #------------------ Experiment Features Setup ------------------ # #

    ########################
    # per-Channel features #
    ########################
    mux_group_manager_config = settings["group_manager"]
    internal_state_object = InternalStateInformation(
        cycle_groups=mux_group_manager_config.get("cycle_groups", False),
        cycle_limit_per_channel=mux_group_manager_config.get("cycle_limit_per_channel", device.wells_per_channel),
    )

    mux_group_manager = GroupManager(mux_group_manager_config, device, internal_state_object)

    progressive_unblock_config = settings.get("progressive_unblock", {"enabled": False})
    progressive_unblock = ProgressiveUnblock(progressive_unblock_config, device)

    channel_disable_config = settings.get("channel_states_disable", {"enabled": False})
    channel_disable = ChannelDisable(channel_disable_config, device)

    drift_correction_config = settings.get("drift_correction", {"enabled": False})
    drift_correction = DriftCorrection(
        drift_correction_config,
        device,
        effective_unblock_voltage=settings["effective_unblock_voltage"],
        enable_relative_unblock_voltage=settings.get("enable_relative_unblock_voltage"),
    )

    static_drift_correction_config = settings.get("static_drift_correction", {"enabled": False})
    static_drift_correction = StaticDriftCorrection(
        static_drift_correction_config,
        device,
        effective_unblock_voltage=settings["effective_unblock_voltage"],
        enable_relative_unblock_voltage=settings.get("enable_relative_unblock_voltage"),
    )

    ###################
    # Global Features #
    ###################

    channel_wind_down_config = settings.get("channel_wind_down", {"enabled": False})

    mux_scan_config = settings.get("mux_scan", {"enabled": False})
    mux_scan_trigger = MuxScanTrigger(device=device)
    mux_scan_trigger.enable = True  # Make sure we start with a mux scan

    mux_scan_feature = MuxScan(
        device,
        relative_scan_voltage=current_bias_voltage,
        config=mux_scan_config,
    )

    global_flick_config = settings.get("global_flick", {"enabled": False})
    global_flick_trigger = GlobalTrigger()

    global_mux_change_trigger = GlobalTrigger()

    temperature_manager_config = settings.get("temperature_manager", {"enabled": False})
    temperature_manager = TemperatureManager(config=temperature_manager_config, device=device)

    ##################
    # Other Features #
    ##################

    experiment_pause = ExperimentPauser(device)
    profiler = Profiler(device)

    # Stores a timeline of events to execute
    events_not_yet_executed = None
    time_end = time.monotonic() + settings["run_time"]

    # #------------------ Experiment Features Setup end ------------------ # #

    # ----------- MAIN LOOP -------------- #
    while time_end > time.monotonic():

        # ----------- MUX SCAN -------------- #
        if mux_scan_trigger.enable:

            phase_management.set_phase("MUX_SCAN")

            # If mux scan enabled then get groups from that, else just use all wells per channel
            if mux_scan_config["enabled"]:
                mux_groups = mux_scan_loop(mux_scan_feature=mux_scan_feature, config=settings, device=device)
            else:
                # Pick everything
                mux_groups = {channel: device.get_well_list() for channel in device.get_channel_list()}

            internal_state_object.set_groups(mux_groups)
            mux_group_manager.set_next_group()  # Trigger everything to be in the first group

            mux_scan_trigger.enable = False
        # #--------------------------------------------------------------#

        if settings.get("enable_relative_unblock_voltage"):
            maintain_relative_unblock_voltage(device, current_bias_voltage, settings["effective_unblock_voltage"])

        device.set_bias_voltage(current_bias_voltage)

        # #------------------  START SEQUENCING SECTION ----------------------#
        logger.info("Performing a Sequencing Period")

        with FeatureManager(device, phase_management=phase_management, add=events_not_yet_executed) as feature_manager:

            ########################
            # per-Channel features #
            ########################

            # Watch the channel states and also refresh every 0.1 seconds
            if progressive_unblock_config["enabled"]:
                feature_manager.start(
                    progressive_unblock,
                    triggers_on=[feature_manager.channel_update(), feature_manager.interval(0.1)],
                    on_trigger=feature_manager.just_run,
                )

            if drift_correction_config["enabled"]:
                interval = drift_correction_config.get("interval")
                if interval:
                    if interval < 60:
                        raise RuntimeError("Drift corrector minimum interval has to be >= 60 seconds")
                    feature_manager.start(
                        drift_correction,
                        triggers_on=[feature_manager.interval(interval)],
                        on_trigger=feature_manager.just_run,
                    )
                else:
                    raise RuntimeError("Drift corrector is enabled but with no interval time")

            if channel_disable_config["enabled"]:
                feature_manager.start(
                    channel_disable, triggers_on=[feature_manager.channel_update()], on_trigger=feature_manager.just_run
                )

            # Controls active mux swapping
            if mux_group_manager_config["swap_out_disabled_channels"]:
                # Only need to listen on channel states if we have said we wish to swap channels
                feature_manager.start(
                    mux_group_manager,
                    triggers_on=[feature_manager.channel_update()],
                    on_trigger=feature_manager.just_run,
                )

            if static_drift_correction_config["enabled"]:
                interval = static_drift_correction_config.get("interval")
                if interval:
                    feature_manager.start(
                        static_drift_correction,
                        triggers_on=[feature_manager.interval(interval)],
                        on_trigger=feature_manager.just_run,
                    )
                else:
                    raise RuntimeError("Static Drift Correction is enabled but with no interval time")

            ###################
            # Global Features #
            ###################

            feature_manager.start(
                mux_scan_trigger,
                triggers_on=[
                    feature_manager.keystore_update(),
                    feature_manager.mux_scan_action(),
                    feature_manager.interval(settings["mux_scan"]["interval"]),
                ],
                allow_exit_manager_sleep=True,
            )

            if global_flick_config["enabled"]:
                interval = global_flick_config.get("interval")
                if interval:
                    feature_manager.start(
                        global_flick_trigger,
                        triggers_on=[feature_manager.interval(interval)],
                        allow_exit_manager_sleep=True,
                    )
                else:
                    raise RuntimeError("Global Flick is enabled but with no interval time")

            if mux_group_manager_config["global_mux_change"]["enabled"]:
                interval = mux_group_manager_config["global_mux_change"].get("interval")
                if interval:
                    feature_manager.start(
                        global_mux_change_trigger,
                        triggers_on=[feature_manager.interval(interval)],
                        on_trigger=feature_manager.reset_all,
                        allow_exit_manager_sleep=True,
                    )
                else:
                    raise RuntimeError("Global Mux Change is enabled but with no interval time")

            if temperature_manager_config["enabled"]:
                feature_manager.start(
                    temperature_manager, triggers_on=[feature_manager.interval(temperature_manager_config["interval"])]
                )

            ##################
            # Other Features #
            ##################

            feature_manager.start(profiler, triggers_on=[feature_manager.interval(60)])

            feature_manager.start(
                experiment_pause,
                triggers_on=[
                    feature_manager.keystore_update(),
                    feature_manager.pause_action(),
                ],
                on_trigger=feature_manager.pause_all,
            )

            # Sequence for however long specified.
            remaining_time = time_end - time.monotonic()
            if remaining_time <= 0:
                break

            phase_management.set_phase("SEQUENCING")
            keystore.set_state(device, "RUNNING_SEQUENCING")  # Will be deprecated next major version

            # Everything is set up so the body of this is just sleep really!
            feature_manager.sleep(remaining_time)

            # Save timings from interval triggers - So that if they've partially got
            # to their execute time, that isn't forgotten
            events_not_yet_executed = feature_manager.stop_all()

        # #--------------------  END SEQUENCING SECTION ----------------------#
        # #--------------------  Channel_cool_down  ----------------------#

        if channel_wind_down_config["enabled"]:
            channel_wind_down_loop(channel_wind_down_config, device)

        # #----------------------  Global Mux Change  ----------------------#

        if global_mux_change_trigger.enable:
            logger.info("Performing a Global Mux Change")
            mux_group_manager.set_next_group(bias_voltage=start_bias_voltage)
            global_mux_change_trigger.enable = False

        # #----------------------  Global Flick  ---------------------------#

        if global_flick_trigger.enable:
            logger.info("Performing a Global Flick")
            global_flick(
                device,
                current_run_voltage=current_bias_voltage,
                flick_voltage=global_flick_config.get("flick_voltage"),
                flick_duration=global_flick_config.get("flick_duration"),
                rest_voltage=global_flick_config.get("rest_voltage"),
                rest_duration=global_flick_config.get("rest_duration"),
                voltage_gap=global_flick_config.get("voltage_gap"),
                perform_relative_flick=global_flick_config.get("perform_relative_flick"),  # type: ignore
            )  # todo need to add the config
            global_flick_trigger.enable = False

        # #---------------------  Prep for mux scan  -------------------------#
        if mux_scan_trigger.enable:
            # Remove any mux scans scheduled as we are going for one:
            events_not_yet_executed = [item for item in events_not_yet_executed if item[1] != mux_scan_trigger]

    device.set_bias_voltage(0)  # Finish in a safe state
    logger.log_to_gui("sequencing.finish")
    device.unlock_channel_states(channels=device.get_channel_list())
    device.stop_acquisition()
    phase_management.stop()


if __name__ == "__main__":
    # --config <> to run with a specific config
    parser = config_argument_parser()
    args = parser.parse_args()
    sys.exit(main(config=args.config))
