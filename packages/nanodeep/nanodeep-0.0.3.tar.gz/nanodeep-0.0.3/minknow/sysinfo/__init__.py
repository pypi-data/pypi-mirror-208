# Copyright (c) 2008-2021 Oxford Nanopore Technologies PLC. All rights reserved.

"""Information about the system we are running on."""

import os, sys


def is_windows():
    """True if the current platform is Windows."""
    return sys.platform == "win32"


def _find_effective_username():
    """Attempt to determine the username of the effective user."""
    try:
        # this is the most accurate value: the name of the effective user
        import pwd

        return pwd.getpwuid(os.geteuid())[0]
    except KeyError:
        # the effective user id is not in the password database (/etc/passwd);
        # the user id will be enough for our purposes
        return str(os.geteuid())
    except (ImportError, AttributeError):
        # the pwd module is not supported (Windows); use environment variables
        # instead
        import getpass

        return getpass.getuser()


effective_username = _find_effective_username()
"""The username of the effective user.

If the effective user has no associated username, this will be the effective
user id (as a string). If the effective user could not be determined, this will
be the username of the real user.
"""

# constants for process_owned_by_self
try:
    _current_euid = os.geteuid()
    _usernames = [effective_username.lower()]
except AttributeError:
    _current_euid = None
    try:
        import win32api, win32con

        _usernames = []
        try:
            _usernames.append(
                win32api.GetUserNameEx(win32con.NameSamCompatible).lower()
            )
        except:
            pass
        try:
            _usernames.append(win32api.GetUserName().lower())
        except:
            pass
        try:
            _usernames.append(win32api.GetUserNameEx(win32con.NameDnsDomain).lower())
        except:
            pass
    except ImportError:
        _usernames = [effective_username.lower()]


def process_owned_by_self(process):
    """Return True if the psutil process is owned by the effective user.

    process -- a Process object from psutil; specifically, it is expected to
               provide at least a username property, and optionally also a uids
               property.
    """
    try:
        if _current_euid is not None:
            try:
                (ruid, euid, suid) = process.uids()
                return euid == _current_euid
            except AttributeError:
                pass

        # remove domain, if present
        process_username = process.username().lower().split("\\")[-1]
        for username in _usernames:
            if username == process_username:
                return True
        return False
    except:  # psutil.AccessDenied, normally
        return False


def same_file(path1, path2):
    """Return True if path1 and path2 refer to the same file or directory.

    Does not account for hard links.
    """
    return os.path.normcase(os.path.abspath(path1)) == os.path.normcase(
        os.path.abspath(path2)
    )


class ProxySettings(object):
    def __init__(self, auto_detect, auto_config_script, https_proxy, bypass_globs):
        self.auto_detect = auto_detect
        self.auto_config_script = auto_config_script
        self.https_proxy = https_proxy
        self.bypass_globs = bypass_globs


def get_proxy_settings():
    if is_windows():
        import ctypes
        import re

        class WINHTTP_CURRENT_USER_IE_PROXY_CONFIG(ctypes.Structure):
            _fields_ = [
                ("fAutoDetect", ctypes.c_bool),
                ("lpszAutoConfigUrl", ctypes.c_wchar_p),
                ("lpszProxy", ctypes.c_wchar_p),
                ("lpszProxyBypass", ctypes.c_wchar_p),
            ]

        config = WINHTTP_CURRENT_USER_IE_PROXY_CONFIG()

        if ctypes.windll.winhttp.WinHttpGetIEProxyConfigForCurrentUser(
            ctypes.byref(config)
        ):
            bypass = re.split("[\s;]+", str(config.lpszProxyBypass or ""))
            proxies = str(config.lpszProxy or "").split(";")
            https_proxy = ""
            for proxy in proxies:
                if proxy.startswith("https="):
                    https_proxy = proxy[len("https=") :]
                elif not https_proxy and "=" not in proxy:
                    https_proxy = proxy
            return ProxySettings(
                bool(config.fAutoDetect),
                str(config.lpszAutoConfigUrl or ""),
                https_proxy,
                bypass,
            )
    else:
        try:
            return ProxySettings(
                True,
                None,
                os.environ["https_proxy"],
                [
                    "*" + x if x.startswith(".") else x
                    for x in os.environ.get("no_proxy", "").split(",")
                ],
            )
        except KeyError:
            pass
    return None
