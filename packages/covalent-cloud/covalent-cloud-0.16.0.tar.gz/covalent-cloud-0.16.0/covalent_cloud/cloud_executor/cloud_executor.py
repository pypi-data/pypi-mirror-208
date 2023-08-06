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
    """
        CloudExecutor represents a configuration for executing a Covalent workflow on the Covalent Cloud.
        This class allows users to configure the resources (such as the number of CPUs, memory, GPUs, and GPU type) and the software environment for a Covalent workflow that will be executed on the Covalent Cloud. The time limit for the workflow execution can also be set.
    
        Attributes:
    
            num_cpus (int, optional): Number of CPUs to be used for the workflow. Defaults to 1.
            memory (int, optional): Amount of memory (in MB) to be used for the workflow. Defaults to 1024.
            num_gpus (int, optional): Number of GPUs to be used for the workflow. Defaults to 0.
            gpu_type (str, optional): Type of GPU to be used for the workflow. Defaults to an empty string.
            env (str, optional): Name of the software environment to be used for the workflow. Defaults to "default".
            time_limit (Union[int, timedelta], optional): Time limit for the workflow execution, in seconds or as a timedelta. Defaults to 60.
    
        Examples:
    
            # create a CloudExecutor with default resource configuration
            # executor = CloudExecutor()
    
            # create a custom CloudExecutor with specified resources and environment
            # executor = CloudExecutor(
            #     num_cpus=4,
            #     memory=2048,
            #     num_gpus=1,
            #     gpu_type="NVIDIA-Tesla-V100",
            #     env="my_custom_env",
            #     time_limit=1800  # 30 minutes
            # )
    
            import covalent as ct
            from covalent_cloud import CloudExecutor
    
            cloud_executor1 = CloudExecutor(num_cpus=1, memory=1024)
            cloud_executor2 = CloudExecutor(num_cpus=2, memory=2048)
            cloud_executor3 = CloudExecutor(num_cpus=1, memory=512)
    
            # Define manageable tasks as electrons with different cloud executors
            @ct.electron(executor=cloud_executor1)
            def add(x, y):
                return x + y
    
            @ct.electron(executor=cloud_executor2)
            def multiply(x, y):
                return x * y
    
            @ct.electron(executor=cloud_executor3)
            def divide(x, y):
                return x / y
    
            # Define the workflow as a lattice
            @ct.lattice
            def workflow(x, y):
                r1 = add(x, y)
                r2 = [multiply(r1, y) for _ in range(4)]
                r3 = [divide(x, value) for value in r2]
                return r3
    
            # Import the Covalent Cloud module
            import covalent_cloud as ctc
    
            # Dispatch the workflow to the Covalent Cloud
            dispatch_id = ctc.dispatch(workflow)(1, 2)
            result = ctc.get_result(dispatch_id, wait=True)
            print(result)
    """

    num_cpus: int = 1
    memory: int = 1024
    num_gpus: int = 0
    gpu_type: str = ""
    env: str = "default"
    time_limit: Union[int, timedelta] = 60

    @property
    def short_name(self) -> str:
        """
        Property which returns the short name
        of the executor used by Covalent for identification.

        Args:
            None
        
        Returns:
            The short name of the executor

        """

        return executor_plugin_name

    # Convert timedelta to seconds
    def __post_init__(self):
        if isinstance(self.time_limit, timedelta):
            self.time_limit = self.time_limit.total_seconds()

    # Validators:
    @validator("num_cpus", "memory", "time_limit")
    def gt_than_zero(cls, v: int) -> int:
        """
        Validator which ensures that the value is greater than 0.

        Args:
            v: The value to validate

        Returns:
            The validated value

        """
        
        if v <= 0:
            raise ValueError(f"{v} must be greater than 0")
        return v

    # Model methods:
    def to_json(self) -> str:
        """
        Return a JSON-serialized string representation of this object.

        Args:
            None
        
        Returns:
            The JSON-serialized string representation of this object.
        
        """

        return json.dumps(self, default=pydantic_encoder)

    def to_dict(self) -> dict:
        """
        Return a JSON-serializable dictionary representation of this object.

        Args:
            None
        
        Returns:
            The JSON-serializable dictionary representation of this object.
        """

        return {
            "type": str(self.__class__),
            "short_name": self.short_name,
            "attributes": asdict(self),
        }
