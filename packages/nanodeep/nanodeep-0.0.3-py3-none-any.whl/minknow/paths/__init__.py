import os
import sys
import platform

if platform.system() != "Windows":
    from stat import S_IXUSR


def is_minknow_base_dir(path):
    """
    Returns true is the specified path is a valid minknow working directory
    """

    bin_dir = os.path.join(path, "bin")
    if not os.path.exists(bin_dir) or not os.path.isdir(bin_dir):
        # no bin directory = not a minknow working directory
        return False

    # if these processes are there this is extremely likely to be a valid minknow working directory
    # config editor = used by python module conf
    # control_server = main MinKNOW process
    processes = ["config_editor", "control_server"]
    is_windows = platform.system() == "Windows"
    if is_windows:
        processes = [p + ".exe" for p in processes]
    for process in processes:
        path = os.path.join(bin_dir, process)
        if is_windows:
            is_exe = True
        else:
            is_exe = os.path.exists(path) and S_IXUSR & os.stat(path).st_mode

        if not os.path.isfile(path) or not is_exe:
            return False

    return True


def minknow_base_dir():
    """
    Finds the base directory of the MinKNOW installation this module belongs to
    """

    python_location = (
        sys.executable
    )  # this should be <minknow working dir>/ont-python/bin/python on osx and linux and <minknow working dir>/ont-python/python.exe on Windows
    candidate_wd = python_location

    if platform.system() != "Windows":
        levels_up = 3
    else:
        levels_up = 2

    for i in range(levels_up):
        candidate_wd = os.path.join(candidate_wd, os.pardir)

    candidate_wd = os.path.abspath(candidate_wd)
    candidates = [candidate_wd, os.getcwd()]
    for candidate in candidates:
        if is_minknow_base_dir(candidate):
            return candidate

    raise RuntimeError("Unable to retrieve MinKNOW base directory")


if __name__ == "__main__":
    # just for testing
    print(minknow_base_dir())
