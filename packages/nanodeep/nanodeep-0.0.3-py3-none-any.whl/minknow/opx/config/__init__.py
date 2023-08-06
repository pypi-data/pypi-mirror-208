import argparse
import minknow.conf
import logging

protocol_selector_choices = {
    "NC": "conf/package/utility/protocol_selector.py",
    "Prod": "conf/package/utility/protocol_selector.py",
    "ONT": "conf/package/utility/protocol_selector.py",
}


def configure_app_conf(
    app_conf, simulator=False, analysis=None, installation="NC", setup_for_bream=True
):
    if analysis is not None:
        logging.warning(
            "Analysis argument to `configure_app_conf` is no longer supported. use `analysis_configuration.set_analysis_enabled_state` instead."
        )
        if not analysis:
            raise Exception("`configure_app_conf` is unable to turn off analysis.")

    if simulator is not False:
        logging.warning(
            "Simulator argument to `configure_app_conf` is no longer supported. use arguments to ManagerProcess and MinKNOWTestCase instead."
        )
        raise Exception("`configure_app_conf` is unable to turn on simulation.")

    if setup_for_bream:
        app_conf["script_entrypoint"] = protocol_selector_choices[installation]

    app_conf["disk_space_warnings.reads.minimum_space_mb"] = 500000  # 500 gb stop
    app_conf[
        "disk_space_warnings.reads.warning_space_mb"
    ] = 4000000  # 4 tb warnings begin


def configure_sys_conf(sys_conf):
    sys_conf["ping_url"] = "primary=https://ping.oxfordnanoportal.com/promethion"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure minknow for promethion")
    parser.add_argument(
        "--installation",
        action="store",
        default="NC",
        choices=list(protocol_selector_choices.keys()),
        help='Installaton type for the protocol-selector, (defaults to "NC")',
    )
    args = parser.parse_args()

    filenames = minknow.conf.default_config_full_filenames()

    app_conf = minknow.conf.Conf(
        minknow.conf.APPLICATION_CONF_TAG, filenames[minknow.conf.APPLICATION_CONF_TAG]
    )
    configure_app_conf(app_conf, installation=args.installation)
    app_conf.save()

    sys_conf = minknow.conf.Conf(
        minknow.conf.SYSTEM_CONF_TAG, filenames[minknow.conf.SYSTEM_CONF_TAG]
    )
    configure_sys_conf(sys_conf)
    sys_conf.save()
