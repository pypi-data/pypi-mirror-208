# Copyright 2023 Agnostiq Inc.

from covalent_cloud.shared.classes.api import DispatcherAPI


def get_client() -> DispatcherAPI:
    """
    A factory / getter method for the Dispatcher API client.

    Args:
        None

    Returns:
        An instance of `DispatcherAPI` client.

    """
    
    return DispatcherAPI()
