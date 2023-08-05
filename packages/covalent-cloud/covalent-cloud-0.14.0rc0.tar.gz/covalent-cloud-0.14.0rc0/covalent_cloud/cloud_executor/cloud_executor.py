# Copyright 2023 Agnostiq Inc.


import json
from dataclasses import asdict
from datetime import timedelta
from typing import Union

from pydantic import validator
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder

executor_plugin_name = "cloud"


@dataclass
class CloudExecutor:
    @property
    def short_name(self) -> str:
        return executor_plugin_name

    num_cpus: int = 1
    memory: int = 1024
    num_gpus: int = 0
    gpu_type: str = ""
    env: str = "default"
    time_limit: Union[int, timedelta] = 60

    # Convert timedelta to seconds
    def __post_init__(self):
        if isinstance(self.time_limit, timedelta):
            self.time_limit = self.time_limit.total_seconds()

    # validators

    @validator("num_cpus", "memory", "time_limit")
    def gt_than_zero(cls, v):
        if v < 0:
            raise ValueError(f"{v} must be greater than 0")
        return v

    # model methods

    def to_json(self):
        return json.dumps(self, default=pydantic_encoder)

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        return {
            "type": str(self.__class__),
            "short_name": self.short_name,
            "attributes": asdict(self),
        }
