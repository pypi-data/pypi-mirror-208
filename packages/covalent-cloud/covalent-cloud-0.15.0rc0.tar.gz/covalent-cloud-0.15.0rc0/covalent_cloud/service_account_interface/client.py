# Copyright 2023 Agnostiq Inc.

from covalent_cloud.shared.classes.api import DispatcherAPI


def get_client():
    return DispatcherAPI()
