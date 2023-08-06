import collections
import minknow_api
import numpy

from enum import Enum
from minknow_api.device import DeviceType

__all__ = [
    "DeviceType",
    "Device",
]


def _parse_Option(value):
    """Converts Pythonic arguments (True, False, None) into Option values for gRPC (FORCE, DISABLE,
    AUTO)."""

    if type(value) == bool:
        if value:
            return minknow_api.acquisition_service.FORCE
        else:
            return minknow_api.acquisition_service.DISABLE
    if value is None:
        return minknow_api.acquisition_service.AUTO
    return value


def _patch_if_option(descriptor, value):
    """If descriptor refers to a minknow_api.acquisition.Option field, apply _parse_Option to value.

    This makes it convenient to map the arguments to a nanodeep to turn friendly Pythonic values
    into ones suitable for sending over gRPC."""

    try:
        if descriptor.enum_type.full_name == "minknow_api.acquisition.Option":
            return _parse_Option(value)
    except AttributeError:
        pass
    return value


class Device(object):
    """High-level interface to a sequencing device.

    This can be used to control a single MinION, or a single flowcell port on a PromethION or
    GridION. It hides the details of the MinKNOW RPC interface (although the ``rpc`` property can be
    used to access the RPCs directly).

    Note that channels are counted from 1.

    Properties:

    rpc -- a minknow_api.Connection instance
    version_info -- the version information of the MinKNOW instance that has been connected to
    output_dirs -- the output directories of the MinKNOW instance
    device_info -- information about the device MinKNOW is managing
    numpy_data_types -- a NumpyDTypes tuple describing the data types provided by the data rpc service

    :param connection: a minknow_api.Connection object
    """

    def __init__(self, connection=None):
        if connection is None:
            self.rpc = minknow_api.Connection()
        else:
            self.rpc = connection
        self.version_info = self.rpc.instance.get_version_info()
        self.output_dirs = self.rpc.instance.get_output_directories()
        self.device_info = self.rpc.device.get_device_info()
        self.numpy_data_types = minknow_api.data.get_numpy_types(self.rpc)

    def __repr__(self):
        return "<minknow.Device for {}>".format(self.device_info.device_id)

    @property
    def minknow_version(self):
        """The MinKNOW version, as a string."""
        return self.version_info.minknow.full

    @property
    def protocols_version(self):
        """The version of the installed protocols, as a string."""
        return self.version_info.protocols

    @property
    def configuration_version(self):
        """The version of the installed configuration package, as a string."""
        return self.version_info.configuration

    @property
    def output_directory(self):
        """The location of the output directory.

        The returned path is only valid on the machine that MinKNOW is running on.
        """
        return self.output_dirs.output

    @property
    def log_directory(self):
        """The location MinKNOW writes its logs to.

        The returned path is only valid on the machine that MinKNOW is running on.
        """
        return self.output_dirs.log

    @property
    def reads_directory(self):
        """The location MinKNOW writes reads files to.

        Note that reads will actually be written to subdirectories of this location, depending on
        the read writer configuration.

        The returned path is only valid on the machine that MinKNOW is running on.
        """
        return self.output_dirs.reads

    @property
    def device_type(self):
        """The type of device."""
        return DeviceType(self.device_info.device_type)

    @property
    def device_id(self):
        """The globally unique identifier for the device."""
        return self.device_info.device_id

    @property
    def flow_cell_info(self):
        """Information about the attached flowcell, if any.

        Returns None if no flowcell is attached. Otherwise, returns an object with at least the
        following attributes:

        channel_count -- the number of channels available
        wells_per_channel    -- the number of wells available
        flowcell_id   -- the unique identifier of the attached flowcell
        """
        # TODO: when we have a streaming version of flowcell_info, cache this stuff and watch for
        # changes
        info = self.rpc.device.get_flow_cell_info()
        if info.has_flow_cell:
            return info
        return None

    def start_data_acquisition(self, **kwargs):
        """Start data acquisition.

        This is a wrapper around the acquisition.start() call, and accepts all the arguments that
        does. Where the argument has an Option type, it will accept True or False in place of FORCE
        or DISABLE, for convenience.

        """
        fields_by_name = self.rpc.acquisition._pb.StartRequest.DESCRIPTOR.fields_by_name
        args = {
            k: _patch_if_option(fields_by_name.get(k), v) for k, v in kwargs.items()
        }
        return self.rpc.acquisition.start(**args)

    def stop_data_acquisition(self, **kwargs):
        """Stop data acquisition.

        This is a wrapper around the acquisition.stop() call, and accepts all the arguments that
        does.
        """
        return self.rpc.acquisition.stop(**kwargs)

    def get_signal(self, callback=None, **kwargs):
        return minknow_api.data.get_signal(
            self.rpc, on_started=callback, numpy_dtypes=self.numpy_data_types, **kwargs
        )
