#!/usr/bin/env python

"""
MinKNOW package uninstallation and installation on OSX platform is managed by this script.
This script provides several options to drive partial or total uninstallation and/or installation.
It logs its results either on stdout/stderr (this can be forced with the --std-log option) or in the same directory as the
output directory specified in the user configuration if it exists, otherwise in the /private/var/log directory.

Uninstall Only
--------------

The --uninstall-only option uninstalls the current application which at the specified location (the
default is /Applications/MinKNOW.app). You have to select an uninstallation mode:

- If the 'full' mode is selected MinKNOW is uninstalled as well as the .plist file OSX needs to start mk_manager_svc as a daemon process.
- If the 'skip-mk-manager-svc-daemon' mode is selected the .plist file is not removed

Installation
------------

There are two ways to drive the installation.
If the '--install-mk-manager-svc-daemon-only' is specified the installer will install only the daemon .plist file without installing MinKNOW (it should
have already been installed in the default location).
If no option is specified the installation is full.

Run the --help option to list details about all the installer options and arguments
"""

import os
import shutil
import subprocess
import argparse
import logging
import sys
import time
import stat
import psutil

from minknow import conf

# for convenience
pjoin = os.path.join
pexists = os.path.exists

#############################
# global objects
#############################

MINKNOW_APP_NAME = "MinKNOW.app"
MINKNOW_PKG_NAME = "MinKNOW.pkg"

#############################
# global objects
#############################

logger = logging.getLogger(__name__)

#############################
# free functions
#############################


def choices_help(choices):
    help = ""
    for k, v in choices.items():
        help = help + "<" + k + "> - " + v + ";"
    return help


def minknow_app_dir(app_location):
    return pjoin(app_location, MINKNOW_APP_NAME)


def minknow_app_working_dir(app_location):
    return pjoin(minknow_app_dir(app_location), "Contents", "Resources")


def init_log(filename=None):
    """
    Initialize log infrastructure. If a filename is defined the messages are logged into a that file,
    otherwise they are printed on the std out/err
    """

    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    if filename:
        handler = logging.FileHandler(filename=filename)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    if filename:
        logger.info("Installer log file initialized")


def log_exception():
    logger.error(
        "Caught exception of type %s. Message: %s", sys.exc_info()[0], sys.exc_info()[1]
    )


def set_rw_permissions(directory):
    """
    Sets directory and each file and directory inside it to be readable and writable by everyone.
    Permissions are set to 0777 for directories and executables and to 0666 for regular files. Symlinks are followed
    """

    # See MK-4419 to understand why this is needed
    os.chmod(directory, 0o777)
    for f in os.listdir(directory):
        p = pjoin(directory, f)
        if os.path.isfile(p):
            mode = os.stat(p).st_mode
            if mode & stat.S_IXUSR:
                mode = 0o777
            else:
                mode = 0o666
            os.chmod(p, mode)
        elif os.path.isdir(p):
            set_rw_permissions(p)


#############################
# classes
#############################


class DiskImageExtractor:
    """
    Manages mounting and unmounting of MinKNOW package (dmg file)
    """

    __volumes_dir = "/Volumes"
    __mounted = []

    def extract(self, dmg_file_path):
        (dummy, filename) = os.path.split(dmg_file_path)
        (filename, dummy) = os.path.splitext(filename)

        mounted_image_path = pjoin(self.__volumes_dir, filename)

        # make sure the image is not already mounted
        if pexists(mounted_image_path):
            self.execute_hdiutil("detach", mounted_image_path)

        if self.execute_hdiutil("attach", dmg_file_path):
            self.__mounted.append(filename)
            return mounted_image_path
        return None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for mounted_disk in self.__mounted:
            logger.info("Unmounting %s", mounted_disk)
            self.execute_hdiutil("detach", pjoin(self.__volumes_dir, mounted_disk))
        return False

    def execute_hdiutil(self, command, file):

        if not pexists(file):
            raise IOError("file " + file + " not found")

        (unused, filename) = os.path.split(file)
        (filename, unused) = os.path.splitext(filename)

        hdiutil_cmd = " ".join(["hdiutil", command, file])
        hdiutil_proc = subprocess.Popen(
            hdiutil_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        (out, err) = hdiutil_proc.communicate()

        if hdiutil_proc.returncode is 0:
            if out:
                logger.info("Executed command %s. Output: %s", hdiutil_cmd, out)
            return True
        else:
            logger.error("Error executing command %s", hdiutil_cmd)
            if err:
                logger.info("Error: %s", err)
            return False


class MkManager:
    """
    Drives daemon mk_manager_svc
    """

    __port = None
    __server_proc_name = "mk_manager_svc"

    def __init__(self, app_location, port=9500):
        self.__port = port
        self.__app_location = app_location
        self.__server_exec_full_path = os.path.abspath(
            pjoin(
                minknow_app_working_dir(self.__app_location),
                "bin",
                self.__server_proc_name,
            )
        )
        self.__mk_manager_svc_p_list_filename = pjoin(
            "/Library", "LaunchDaemons", self.__server_proc_name + ".plist"
        )

    class TerminateResult:
        wasnt_running = 1
        stopped = 2
        # failed_to_stop = 3 throw exception in this case

    def terminate_server(self):
        """
        Search for minknow_server processes and send them a TERM signal
        :return: termination result
        """
        found = False
        for proc in psutil.process_iter():
            if proc.name() == self.__server_proc_name:
                found = True
                logger.info(
                    "Terminating %s by sending SIGTERM. (This is normal)",
                    self.__server_proc_name,
                )
                proc.terminate()

                # wait for the server to clean-up and exit
                try:
                    gone, alive = psutil.wait_procs([proc], timeout=120)
                except Exception as e:
                    logger.error(
                        "wait_procs threw an exception waiting for process {}: {}. Trying to continue "
                        "the software update process".format(proc, e.message)
                    )
                else:
                    if len(gone) == 1:
                        logger.info("Process %s terminated", self.__server_proc_name)
                        return MkManager.TerminateResult.stopped
                    else:
                        logger.error(
                            "Process %s didn't terminate", self.__server_proc_name
                        )
                        raise RuntimeError("Failed to terminate server")
        if not found:
            logger.info(
                "Process %s will not be terminated because it's not running",
                self.__server_proc_name,
            )
            return MkManager.TerminateResult.wasnt_running

    def start_server(self):
        cmd_line = ["launchctl", "unload", "-w", self.__mk_manager_svc_p_list_filename]
        logger.info(
            "Stopping service %s: %s", self.__server_proc_name, " ".join(cmd_line)
        )
        proc = subprocess.run(cmd_line)

        cmd_line = ["launchctl", "load", "-w", self.__mk_manager_svc_p_list_filename]
        logger.info("Starting %s: %s", self.__server_proc_name, " ".join(cmd_line))
        proc = subprocess.run(cmd_line)
        logger.info("Finished starting: %s", proc.returncode)

    def check_server(self):
        """
        Returns True if the server is running
        """
        found = False
        for proc in psutil.process_iter():
            try:
                if proc.name() == self.__server_proc_name:
                    found = True
            except:
                # proc.name() may throw if, for example a process exits between the iter and nanodeep, ignore it.
                pass

        return found

    def generate_mk_manager_p_list(self):
        options = [
            "Add:Label string " + self.__server_proc_name,
            "Add:ProgramArguments array",
            "Add:ProgramArguments: string " + self.__server_exec_full_path,
            "Add:RunAtLoad bool true",
            "Add:WorkingDirectory string "
            + minknow_app_working_dir(self.__app_location),
        ]

        full_options = []
        for opt in options:
            full_options.append("-c")
            full_options.append(opt)

        self.remove_mk_manager_p_list()

        cmd_line = ["/usr/libexec/PlistBuddy"]
        cmd_line.extend(full_options)
        cmd_line.append(self.__mk_manager_svc_p_list_filename)

        proc = subprocess.Popen(
            cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        (out, err) = proc.communicate()

        if proc.returncode is 0:
            if out and pexists(self.__mk_manager_svc_p_list_filename):
                logger.info(
                    "Generated %s. Output: %s",
                    self.__mk_manager_svc_p_list_filename,
                    out,
                )
            else:
                logger.error(
                    "%s returned 0 but plist file %s has not been generated",
                    cmd_line[0],
                    self.__mk_manager_svc_p_list_filename,
                )
        else:
            error_string = "Failed to generate " + self.__mk_manager_svc_p_list_filename
            logger.error(error_string)
            if err:
                logger.info("Error: %s", err)
            raise RuntimeError(error_string)

    def p_list_exists(self):
        return pexists(self.__mk_manager_svc_p_list_filename)

    def remove_mk_manager_p_list(self):
        cmd_line = ["launchctl", "unload", "-w", self.__mk_manager_svc_p_list_filename]
        if self.p_list_exists():
            logger.info("Removing %s", self.__mk_manager_svc_p_list_filename)
            os.remove(self.__mk_manager_svc_p_list_filename)


class MinknowAppManager:
    """
    Manages file operations of the app
    """

    def __init__(self, app_location):
        self.__app_location = app_location
        self.__minknow_tmp_old_app_dir = pjoin(app_location, "MinKNOW_old.app")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.remove("old tmp MinKNOW app", self.__minknow_tmp_old_app_dir)
        return False

    def minknow_app_dir(self):
        return pjoin(self.__app_location, MINKNOW_APP_NAME)

    def uninstall_old_app(self):
        self.remove("old MinKNOW app", self.minknow_app_dir())

    def install_app_pkg(self, pkg_file):
        cmd_line = ["installer", "-pkg", pkg_file, "-target", "/"]
        p = subprocess.run(cmd_line)
        if p.returncode != 0:
            logger.error("Failed to install minknow pkg file: %s", pkg_file)
            return False
        return True

    def terminate_current_app(self):
        # assume that at most one web gui is running
        logger.info("Terminating current app")
        command = 'osascript -e "tell application \\"MinKNOW\\" to quit"'

        p = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        (out, err) = p.communicate()
        if out:
            logger.info("stdout: %s", out)
        if err:
            logger.info("stderr: %s", err)

    def launch_app(self):
        app_name = pjoin(
            minknow_app_dir(self.__app_location), "Contents", "MacOS", "MinKNOW"
        )
        logger.info("Launching app %s", app_name)
        subprocess.Popen(app_name)

    def copy(self, what_str_descr, from_dir, to_dir):
        self.remove("", to_dir)
        logger.info("Copying %s from %s to %s...", what_str_descr, from_dir, to_dir)

        shutil.copytree(from_dir, to_dir, symlinks=True)
        logger.info("...done!")

    def remove(self, what_str_descr, dir):
        if pexists(dir):
            if what_str_descr:
                logger.info("Removing %s from %s...", what_str_descr, dir)
            else:
                logger.info("Removing %s...", dir)
            shutil.rmtree(dir)
            logger.info("...done")

    def move(self, from_dir, to_dir):
        logger.info("Moving %s to %s", from_dir, to_dir)
        shutil.move(from_dir, to_dir)


#############################
# main
#############################


def main():
    default_config_filenames = conf.default_config_filenames()

    parser = argparse.ArgumentParser("Osx installer setup")
    parser.add_argument(
        "--dmg-location",
        help="Full path of the dmg file containing the MinKNOW application",
        default="MinKNOW.dmg",
    )

    install_group = parser.add_mutually_exclusive_group()

    choices = {
        "full": "Remove MinKNOW completely",
        "skip-mk-manager-svc-daemon": "Does not remove the plist which allow mk_manager_svc to run as a daemon",
    }
    install_group.add_argument(
        "--uninstall-only",
        help="If defined the existing app is uninstalled without installing the new one. Different"
        "levels are available:\n" + choices_help(choices),
        default=None,
        choices=[k for k in choices],
    )

    choices = {
        "start-now": "The manager is started after the plist is created",
        "start-on-boot": "The manager is not started after the plist is created. It will run on the next system boot",
    }
    install_group.add_argument(
        "--install-mk-manager-svc-daemon-only",
        help="If defined sets up mk_manager_svc to run as a daemon process. "
        "The executable will not be installed and it is supposed to exist already. "
        "The option must have one of the following arguments:\n"
        + choices_help(choices)
        + ". If the plist already exists this command and its option have no effect",
        default=None,
        choices=[k for k in choices],
    )

    install_group.add_argument(
        "--skip-mk-manager-svc-daemon-installation",
        help="If defined mk_manager_svc will not be installed as a daemon process. "
        "The current running mk_manager_svc is stopped and the new one will be run, though."
        "This option should be used only in debug or running tests",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--app-location",
        help="The directory where MinKNOW has to be installed/uninstalled.",
        default="/Applications",
    )

    parser.add_argument(
        "--nolaunch",
        help="If defined the installer does not launch the application after it is installed. "
        "This option is discarded if only the uninstaller is going to run",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--std-log",
        help="If defined log messages are sent to stdout/stderr, \
                otherwise they are stored to in a file in the MinKNOW output directory if it exists",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    conf_dir = pjoin(minknow_app_working_dir(args.app_location), "conf")

    # retrieve the MinKNOW output directory of the existing app, if possible
    user_conf_file = pjoin(conf_dir, default_config_filenames[conf.USER_CONF_TAG])
    log_dir = None
    failed_init_log_dir_msg = None
    if pexists(user_conf_file):
        user_conf = conf.Conf(conf.USER_CONF_TAG, user_conf_file)

        try:
            base_output_dir = user_conf["output_dirs.base"]
            log_dir = os.path.join(base_output_dir, user_conf["output_dirs.logs"])

            # MK-4419 set read and write permission to each existing file and directories
            set_rw_permissions(base_output_dir)
        except Exception as e:
            failed_init_log_dir_msg = str(e)

    if not args.std_log:
        if log_dir is None or not pexists(log_dir):
            log_dir = (
                "/private/var/log"  # default to this if mk output dir does not exist
            )
        init_log(pjoin(log_dir, "ont_MinKNOW_installer_log.txt"))
        if failed_init_log_dir_msg is not None:
            logger.warning(
                "Failed to initialise log dir reading user conf: {0}".format(
                    failed_init_log_dir_msg
                )
            )
    else:
        init_log(None)

    try:
        os.setsid()
        logger.info("Detached process from parent session.")
    except:
        log_exception()
        logger.warning(
            "Failed to detach from parent session. This script may be unexpectedly terminated."
        )

    mk_manager_running = False

    try:
        warning = False  # True if some error occurs which does not prevent minknow to be installed and run

        mk_manager = MkManager(args.app_location)
        if args.install_mk_manager_svc_daemon_only != None:
            if mk_manager.p_list_exists():
                logger.warning(
                    "mk_manager plist already exists and it will be overwritten"
                )
            mk_manager.generate_mk_manager_p_list()
            if args.install_mk_manager_svc_daemon_only == "start-now":
                mk_manager.start_server()
            return 0

        # now run the uninstaller and, if required, the installer
        with MinknowAppManager(args.app_location) as app_manager:
            with DiskImageExtractor() as image_extractor:
                volume_dir = None
                if args.uninstall_only is None:
                    # this is not an immediate operation. Do it before uninstalling the current app
                    volume_dir = image_extractor.extract(args.dmg_location)

                # terminate the server before the app. The server will terminate each running instance of MinKNOW
                # and broadcast an "I'm shutting down" message
                terminate_server_result = mk_manager.terminate_server()
                if terminate_server_result == MkManager.TerminateResult.stopped:
                    time.sleep(40)  # TODO wait until the service port is "free"
                app_manager.terminate_current_app()

                if args.uninstall_only is not None:
                    app_manager.uninstall_old_app()
                    if args.uninstall_only == "full":
                        mk_manager.remove_mk_manager_p_list()
                    logger.info("Minknow uninstalled successfully!")
                    return 0

                app_src_dir = pjoin(volume_dir, MINKNOW_APP_NAME)
                pkg_src_file = pjoin(volume_dir, MINKNOW_PKG_NAME)

                if os.path.exists(pkg_src_file):
                    if not app_manager.install_app_pkg(pkg_src_file):
                        raise RuntimeError("Failed to install Minknow pkg")
                else:
                    raise RuntimeError("Missing pkg installer in dmg file")

                if not args.nolaunch:
                    # start new web gui
                    app_manager.launch_app()

                mk_manager_running = False
                # it could happen that the manager starts and stops immediately for apparently network reasons
                # Retry to start it in that case
                time.sleep(2)
                for i in range(0, 3):
                    mk_manager_running = mk_manager.check_server()
                    if not mk_manager_running:
                        time.sleep(20 * (i + 1))
                        mk_manager.start_server()
                    else:
                        break
    except:
        log_exception()
        logger.error("Minknow installation failed!")
        return 1

    if mk_manager_running:
        if not warning:
            logger.info("Minknow installation completed successfully!")
        else:
            logger.info(
                "Minknow has been installed and can run correctly, but some warnings occurred \
                during installation."
            )
    else:
        logger.warning("Minknow has been installed but mk_manager_svc is not running")
    return 0


if __name__ == "__main__":
    sys.exit(main())
