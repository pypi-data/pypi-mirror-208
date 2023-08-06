"""APIs for interacting with MinKNOW.

This module contains code for interacting with the MinKNOW instrument software, which controls
single-molecule sequencing devices including MinIONs, GridIONs and PromethIONs.
"""


__author__ = "Oxford Nanopore Technologies PLC"
from ._version import __version__

from ._rpc_wrapper import *
