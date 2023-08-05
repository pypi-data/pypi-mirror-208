# Copyright 2023 Agnostiq Inc.

"""Module for Covalent Cloud dispatching and related functionalities."""


import lzma
from copy import deepcopy
from functools import wraps
from typing import Any, Callable

from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject

from ..shared.classes.settings import Settings, settings
from . import results_manager as rm
from .helpers import register, start, validate_executors

API_KEY = "fake"  # pragma: allowlist secret


def _compressed_transportable(data: Any) -> bytes:
    """Applies LZMA compression to a transportable object serialized into bytes."""
    return lzma.compress(TransportableObject(data).serialize())


def dispatch(
    orig_lattice: Lattice,
    settings: Settings = settings,
) -> Callable:
    """
    Wrapping the dispatching functionality to allow input passing
    and server address specification.

    Afterwards, send the lattice to the dispatcher server and return
    the assigned dispatch id.

    Args:
        orig_lattice: The lattice/workflow to send to the dispatcher server.
        dispatcher_addr: The address of the dispatcher server.  If None then then defaults to the address set in Covalent's config.

    Returns:
        Wrapper function which takes the inputs of the workflow as arguments
    """

    dispatcher_addr = settings.dispatcher_uri

    @wraps(orig_lattice)
    def wrapper(*args, **kwargs) -> str:
        """
        Send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            *args: The inputs of the workflow.
            **kwargs: The keyword arguments of the workflow.

        Returns:
            The dispatch id of the workflow.
        """

        lattice = deepcopy(orig_lattice)

        lattice.build_graph(*args, **kwargs)

        # Check that only CloudExecutors are specified.
        if settings.validate_executors:
            if not validate_executors(lattice):
                raise ValueError("One or more electrons have invalid executors.")

        dispatch_id = register(lattice, settings)(*args, **kwargs)

        return start(dispatch_id)

    return wrapper


def get_result(
    dispatch_id: str,
    wait: bool = False,
    settings: Settings = settings,
    *,
    status_only: bool = False,
) -> Result:
    """
    Get the results of a dispatch from a file.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.

    Returns:
        The result from the file.

    """
    return rm.get_result(
        dispatch_id=dispatch_id,
        wait=wait,
        settings=settings,
        status_only=status_only,
    )
