# Copyright 2023 Agnostiq Inc.

"""FastAPI models for /api/v1/resultv2 endpoints"""

import platform

from pydantic import BaseModel

from .asset import AssetSchema
from .transport_graph import TransportGraphSchema

LATTICE_METADATA_KEYS = {
    "__name__",
    # metadata
    "executor",
    "workflow_executor",
    "executor_data",
    "workflow_executor_data",
}

LATTICE_ASSET_KEYS = {
    "workflow_function",
    "workflow_function_string",
    "__doc__",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
    # metadata
    "deps",
    "call_before",
    "call_after",
}

LATTICE_FUNCTION_FILENAME = "function.pkl"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.pkl"
LATTICE_NAMED_ARGS_FILENAME = "named_args.pkl"
LATTICE_NAMED_KWARGS_FILENAME = "named_kwargs.pkl"
LATTICE_RESULTS_FILENAME = "results.pkl"
LATTICE_DEPS_FILENAME = "deps.pkl"
LATTICE_CALL_BEFORE_FILENAME = "call_before.pkl"
LATTICE_CALL_AFTER_FILENAME = "call_after.pkl"
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
LATTICE_STORAGE_TYPE = "file"


ASSET_FILENAME_MAP = {
    "workflow_function": LATTICE_FUNCTION_FILENAME,
    "workflow_function_string": LATTICE_FUNCTION_STRING_FILENAME,
    "doc": LATTICE_DOCSTRING_FILENAME,
    "named_args": LATTICE_NAMED_ARGS_FILENAME,
    "named_kwargs": LATTICE_NAMED_KWARGS_FILENAME,
    "cova_imports": LATTICE_COVA_IMPORTS_FILENAME,
    "lattice_imports": LATTICE_LATTICE_IMPORTS_FILENAME,
    "deps": LATTICE_DEPS_FILENAME,
    "call_before": LATTICE_CALL_BEFORE_FILENAME,
    "call_after": LATTICE_CALL_AFTER_FILENAME,
}


class LatticeAssets(BaseModel):
    workflow_function: AssetSchema
    workflow_function_string: AssetSchema
    doc: AssetSchema  # __doc__
    named_args: AssetSchema
    named_kwargs: AssetSchema
    cova_imports: AssetSchema
    lattice_imports: AssetSchema

    # lattice.metadata
    deps: AssetSchema
    call_before: AssetSchema
    call_after: AssetSchema


class LatticeMetadata(BaseModel):
    name: str  # __name__
    executor: str
    executor_data: dict
    workflow_executor: str
    workflow_executor_data: dict
    python_version: str = platform.python_version()


class LatticeSchema(BaseModel):
    metadata: LatticeMetadata
    assets: LatticeAssets
    transport_graph: TransportGraphSchema
