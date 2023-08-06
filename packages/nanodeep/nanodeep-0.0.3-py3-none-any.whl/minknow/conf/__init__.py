# Copyright 2015 Oxford Nanopore Technologies, PLC

"""Classes for managing configuration files."""

import subprocess, os, sys, platform
import logging
from minknow.paths import minknow_base_dir
from minknow import sysinfo

logger = logging.getLogger(__name__)

##################
# Helper methods #
##################


def conf_editor_application():
    """
    Returns the path of the config_editor application
    """
    ret = os.path.join(minknow_base_dir(), "bin", "config_editor")
    if platform.system() == "Windows":
        ret += ".exe"
    return ret


class ConfigEditorError(Exception):
    def __init__(self, cmd, returncode, output, error):
        self.cmd = cmd
        self.returncode = returncode
        self.output = output
        self.error = error

    def __str__(self):
        if self.error:
            return (
                "Configuration editor exited with non-zero exit status "
                "{0}: {1}{2}".format(self.returncode, self.output, self.error)
            )
        else:
            return (
                "Configuration editor exited with non-zero exit status "
                "{0}".format(self.returncode)
            )


def call_config_editor(args):
    """Calls the configuration editor executable.

    On success, returns the output as a dict.

    On failure, raises an OSError (if editor could not be executed at all) or a
    ConfigEditorError (if it returned an error).
    """
    SEPARATOR = ": "  # note the space after the colon

    command = [conf_editor_application()] + args

    p = subprocess.Popen(
        command, cwd=minknow_base_dir(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (out_data, err_data) = p.communicate()

    if p.returncode != 0:
        raise ConfigEditorError(command, p.returncode, out_data, err_data)
    else:
        if err_data:
            logger.warning(
                "Config editor reported: {0}".format(err_data.decode("utf-8").strip())
            )
        data = {}
        for line in out_data.splitlines():
            decoded_line = line.decode("utf-8")
            sep_pos = decoded_line.find(SEPARATOR)
            if sep_pos > 0:
                data[decoded_line[:sep_pos]] = decoded_line[
                    (sep_pos + len(SEPARATOR)) :
                ]
            else:
                logger.warning("Discarding line from config editor: '{0}'".format(line))
        return data


#############
# Constants #
#############


def get_default_output_dir():
    """Returns the default root output directory"""
    conf = Conf(USER_CONF_TAG)
    return conf["output_dirs.base"]


#   These are the tag used to refer to a particular configuration. The names are duplicated but we check
#   immediately that they are the same as the config editor
USER_CONF_TAG = "user"
APPLICATION_CONF_TAG = "application"
SYSTEM_CONF_TAG = "system"

CONF_TAGS = [USER_CONF_TAG, APPLICATION_CONF_TAG, SYSTEM_CONF_TAG]


def default_config_filenames():
    default_config_filenames.value = None
    if default_config_filenames.value is not None:
        return default_config_filenames.value

    tags_default_filenames = call_config_editor(["--default_filenames"])

    # The default names of the configuration files
    default_config_filenames.value = {
        USER_CONF_TAG: tags_default_filenames[USER_CONF_TAG],
        APPLICATION_CONF_TAG: tags_default_filenames[APPLICATION_CONF_TAG],
        SYSTEM_CONF_TAG: tags_default_filenames[SYSTEM_CONF_TAG],
    }

    return default_config_filenames.value


default_config_filenames.value = None

# directory where old_conf_file and new configuration files are supposed to be
def conf_dir():
    return os.path.normpath(os.path.join(minknow_base_dir(), "conf"))


def default_config_full_filenames():
    if default_config_full_filenames.value is not None:
        return default_config_full_filenames.value

    filenames = default_config_filenames()

    #  Full default filenames of new configuration files, created using default paths
    default_config_full_filenames.value = {
        USER_CONF_TAG: os.path.join(conf_dir(), filenames[USER_CONF_TAG]),
        APPLICATION_CONF_TAG: os.path.join(conf_dir(), filenames[APPLICATION_CONF_TAG]),
        SYSTEM_CONF_TAG: os.path.join(conf_dir(), filenames[SYSTEM_CONF_TAG]),
    }

    return default_config_full_filenames.value


default_config_full_filenames.value = None


DEFAULT_PING_URL = "default=https://ping-dev.oxfordnanoportal.com/info"

CONF_OVERWRITE_WITH_DEFAULTS = {
    USER_CONF_TAG: [
        "output_dirs.protocol_output_pattern",
        "output_dirs.reads",
    ],
    SYSTEM_CONF_TAG: [],
    APPLICATION_CONF_TAG: [],
}


def build_customer_config():
    return {
        # NB If you change these values, you may need to change them for
        # 'offline' too.
        SYSTEM_CONF_TAG: {
            # We've only ever used a default URL here, so use "default" queue
            # name.
            "ping_url": "default=https://ping.oxfordnanoportal.com/info",
            "on_acquisition_ping_failure": "error",
        },
        APPLICATION_CONF_TAG: {
            "script_entrypoint": "conf/package/utility/protocol_selector.py"
        },
        USER_CONF_TAG: {},
    }


# installation types choices and configuration values related to them.
# TODO check with the config editor application if installation types match with those of the C++ code
INSTALLATION_TYPES = {
    "nc": build_customer_config(),
    "q_release": build_customer_config(),
    "ond_release": build_customer_config(),
    "offline": {
        # As NC, but can start experiments without an internet connection
        SYSTEM_CONF_TAG: {
            # ping_url is set later, when we know the base output dir
            "on_acquisition_ping_failure": "ignore",
        },
        APPLICATION_CONF_TAG: {
            "script_entrypoint": "conf/package/utility/protocol_selector.py"
        },
        USER_CONF_TAG: {},
    },
    "ont": {
        # NB If you change these values, you may need to change them for
        # 'prod' and 'dev' too.
        SYSTEM_CONF_TAG: {
            # Continue to use "primary" queue name, because we previously had
            # "primary" and "test" queues/URLs.  This stops any extant "primary"
            # queue being deleted.
            "ping_url": "primary=https://ping-internal.oxfordnanoportal.com/info",
            "on_acquisition_ping_failure": "warn",
        },
        APPLICATION_CONF_TAG: {
            "script_entrypoint": "conf/package/utility/protocol_selector.py"
        },
        USER_CONF_TAG: {},
    },
    "prod": {
        # This configuration should only be used for deployments to production areas
        # These deployments should only be used for running production protocols
        SYSTEM_CONF_TAG: {
            # Continue to use "primary" queue name, because we previously had
            # "primary" and "test" queues/URLs.  This stops any extant "primary"
            # queue being deleted.
            "ping_url": "primary=https://ping-internal.oxfordnanoportal.com/info",
            "on_acquisition_ping_failure": "warn",
        },
        APPLICATION_CONF_TAG: {
            "script_entrypoint": "conf/package/utility/protocol_selector.py"
        },
        USER_CONF_TAG: {},
    },
    "dev": {
        # Installation values used in development environments.
        # Mostly the same as ont, but with a different protocol selector
        # so it will work without Bream.
        SYSTEM_CONF_TAG: {
            "ping_url": "primary=https://ping-dev.oxfordnanoportal.com/info",
            "on_acquisition_ping_failure": "warn",
        },
        APPLICATION_CONF_TAG: {
            # Use the built-in protocol selector for development builds
            # so it will work without Bream installed
            "script_entrypoint": "minknow.cli.protocol"
        },
        USER_CONF_TAG: {},
    },
}


###################
# Core conf class #
###################


class Conf:
    """Allows the MinKNOW configuration to be accessed from Python code.

    This wraps the configuration editor application, using it to load the
    current configuration and to write out an updated configuration.
    """

    def __init__(self, config_type, config_filename=None):
        """Initializes the instance specifying its type and the name of the underlying config editor application.
        If config_filename is provided the configuration is loaded from disk, otherwise the
        configuration is set to its default value
        """
        self._config_type = config_type  # the type of configuration, used to call underlying application
        self._config_filename = config_filename

        self._fields = {}  # config fields dictionary
        self.load()

    def load(self, filename=None):
        """Loads the configuration passing its file name. If filename is not provided
        the value specified when the object had been constructed is used. If it was None or an empty string
        the default configuration is set.
        filename becomes the new file name value stored by this instance. This only happens if no errors occur.
        """
        if not filename:
            filename = self._config_filename

        args = ["--conf", self._config_type]
        if filename:
            args.extend(["--load", filename])
        args.append("--get_all")

        self._fields = call_config_editor(args)

        # update _config_filename
        if filename:
            self._config_filename = filename

    def save(self, filename=None):
        """Saves the configuration passing its file name. If filename is not provided
        the value specified when the object had been constructed is used. If it was Null or an empty
        string an exception is thrown.
        filename becomes the new file name value stored by this instance. This only happens if no errors occur.
        """

        if not filename:
            filename = self._config_filename
            if filename is None:
                raise RuntimeError(
                    "Cannot save config: filename not specified and not previously initialised"
                )

        args = ["--conf", self._config_type]
        for field_name, field_value in self._fields.items():
            args.extend(["--set", field_name + "=" + str(field_value)])
        args.extend(["--save", filename])

        call_config_editor(args)

        # update _config_filename
        if filename:
            self._config_filename = filename

    def __getitem__(self, field_name):
        return self._fields[field_name]

    def __setitem__(self, field_name, field_value):
        # the field must exist
        if self._fields.get(field_name) == None:
            raise ValueError("Field " + field_name + " does not exist in configuration")
        # save booleans as 1 or 0
        if isinstance(field_value, bool):
            self._fields[field_name] = 1 if field_value else 0
        else:
            self._fields[field_name] = field_value

    def filename(self):
        """Returns the current stored filename. It corresponds to the last value used calling the save or load
        method or the value passed on construction. It is the default value for a next call to save or load
        if a new filename value is not provided.
        The nanodeep returns None if such a filename has never been provided.
        """
        return self._config_filename

    def config_type(self):
        return self._config_type

    def print_config(self):
        """Prints all the configuration fields and their value"""
        for k, v in self._fields.items():
            print(k + ":", v)


##########################
# Installation utilities #
##########################
def create_config(type, filename=None):
    """Create a config of the specified type.
    filename is a filename to load when creating the config - by default no file is loaded for the config,
    which initialises the config with default values.
    """
    load_from = None
    if filename and os.path.exists(filename):
        load_from = filename

    return Conf(type, load_from)


def set_fields_to_installation_type_default(conf, installation_type):
    conf_type = conf.config_type()

    # Set installation type dependant fields for conf
    for field in INSTALLATION_TYPES[installation_type][conf_type].keys():
        conf[field] = INSTALLATION_TYPES[installation_type][conf_type][field]

    default_conf = Conf(conf_type)
    for name in CONF_OVERWRITE_WITH_DEFAULTS[conf_type]:
        conf[name] = default_conf[name]


def upgrade_user_config(
    load_conf,
    user_config_filepath,
    output_dir,
    installation_type,
    make_intermediate_dir_absolute,
):
    """Upgrades MinKNOW user configuration files, loading any existing config and saving
    to disk with updated values.

    - load_conf: If false no config data is migrated from old config files.
        If True old config data is loaded into new files.
    - user_config_filepath: A path to use for loading and saving the user config filename.
    - output_dir: the output directory to set in the user configuration file. If None output directories
        are copied from the existing configuration file (the old one or the new one)
    - installation_type: The type of installation (NC/ONT/OFFLINE).
    - make_intermediate_dir_absolute Should the intermediate dir be made absolute rather than relative to base_dir.
    """

    new_user_conf = create_config(
        USER_CONF_TAG, user_config_filepath if load_conf else None
    )

    set_fields_to_installation_type_default(new_user_conf, installation_type)

    # output directories
    if output_dir is not None:
        new_user_conf["output_dirs.base"] = output_dir

    # Proxy
    if sysinfo.is_windows():
        # On Windows, there is no "system-wide" proxy configuration;
        # instead, we make MinKNOW's proxy configuration default to
        # that of the installing user
        if new_user_conf["proxy.use_system_settings"]:
            proxy_config = sysinfo.get_proxy_settings()
            if proxy_config is not None:
                new_user_conf["proxy.use_system_settings"] = 0
                new_user_conf["proxy.auto_detect"] = int(proxy_config.auto_detect)
                new_user_conf[
                    "proxy.auto_config_script"
                ] = proxy_config.auto_config_script
                new_user_conf["proxy.https_proxy"] = proxy_config.https_proxy
                new_user_conf["proxy.proxy_bypass"] = ",".join(
                    proxy_config.bypass_globs
                )

    # Linux configs which are set to default value should be moved to the new location.
    if platform.system() == "Linux":
        if os.path.normpath(new_user_conf["output_dirs.logs"]) == os.path.normpath(
            "/var/log/MinKNOW"
        ):
            new_user_conf["output_dirs.logs"] = "/var/log/minknow"

    if make_intermediate_dir_absolute:
        base_dir = new_user_conf["output_dirs.base"]
        if not os.path.isabs(base_dir):
            logger.warning(
                "Unable to make intermediate dir absolute, base directory is not absolute."
            )
        elif not new_user_conf["output_dirs.intermediate"].startswith(base_dir):
            existing_intermediate_dir = new_user_conf["output_dirs.intermediate"]
            if not os.path.isabs(existing_intermediate_dir):
                new_user_conf["output_dirs.intermediate"] = os.path.join(
                    base_dir, existing_intermediate_dir
                )
            else:
                logger.warning(
                    "Not making intermediate dir absolute as it is already absolute."
                )

    new_user_conf.save(user_config_filepath)


def build_application_config(application_config_filepath, installation_type):
    """Build MinKNOW app configuration files, saving them on the disk.

    - application_config_filepath: Destination path for application conf file
    - installation_type: specifies the installation type
    """
    new_application_conf = Conf(APPLICATION_CONF_TAG)

    set_fields_to_installation_type_default(new_application_conf, installation_type)

    # set the ui_installation field to the default install directories for the different platforms
    ui_per_platform = {
        "Windows": "C:/Program Files/OxfordNanopore/MinKNOW/Client/MinKNOW.exe",
        "Linux": "/opt/ont/minknow-ui/MinKNOW",
        "Darwin": "/Applications/MinKNOW.app/Contents/Resources/Client/MinKNOW.app/Contents/MacOS/MinKNOW",
    }

    new_application_conf["installers.ui_installation"] = ui_per_platform[
        platform.system()
    ]

    new_application_conf.save(application_config_filepath)


def build_system_config(
    user_config_filepath,
    system_config_filepath,
    installation_type,
    installation_type_ping_url,
):
    """Installs MinKNOW app + sys configuration files, saving them on the disk.

    - user_config_filepath: A user config to load and use and use if app conf needs to refer to user conf values.
    - system_config_filepath: A system conf path to copy update settings from, preserves only the auto update location and only if the old and new installation type is ont.
    - installation_type: specifies the installation type
    - installation_type_ping_url: if true the ping_url is set depending on the installation type,
        otherwise it is reset to the default value
    """
    loaded_user_conf = create_config(USER_CONF_TAG, user_config_filepath)
    new_system_conf = Conf(SYSTEM_CONF_TAG)

    ##### edit configuration depending on arguments and previous configuration
    runtime_installation_type = installation_type
    if installation_type == "dev":
        runtime_installation_type = "ont"
    if installation_type == "offline":
        runtime_installation_type = "nc"

    # set the installation type
    new_system_conf["update.installation_type"] = runtime_installation_type

    set_fields_to_installation_type_default(new_system_conf, installation_type)

    # Assume this package is being installed to modify an existing installation
    # and set the distribution_status to "modified". If this is part of a
    # complete installation, the meta-package or other distribution installer
    # will set this to "stable" after installing the other components.
    new_system_conf["distribution_status"] = "modified"

    # ping server
    if installation_type == "offline":
        abs_output_dir = os.path.join(
            minknow_base_dir(), loaded_user_conf["output_dirs.base"], "pings"
        )
        ping_path = abs_output_dir.replace("\\", "/").strip("/")
        new_system_conf["ping_url"] = "default=file:///" + ping_path
    elif installation_type_ping_url:
        new_system_conf["ping_url"] = INSTALLATION_TYPES[installation_type][
            SYSTEM_CONF_TAG
        ]["ping_url"]
    else:
        new_system_conf["ping_url"] = DEFAULT_PING_URL

    ##### finally:

    # save configurations
    new_system_conf.save(system_config_filepath)
