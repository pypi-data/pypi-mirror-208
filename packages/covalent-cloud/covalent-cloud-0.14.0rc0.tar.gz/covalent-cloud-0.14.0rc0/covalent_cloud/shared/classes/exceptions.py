# Copyright 2023 Agnostiq Inc.

"""Covalent Cloud SDK Exception module."""


class CovalentSDKError(Exception):
    """Covalent Cloud SDK Base Exception class.

    Attributes:
        message (str): Explanation of the error.
        code (str): String enum representing error analogous to error code.
    """

    def __init__(self, message: str = "Generic Error", code: str = "error/generic") -> None:
        """
        Initializes a new instance of the CovalentSDKError class.

        Args:
            message (str): Explanation of the error.
            code (str): String enum representing error analogous to error code.

        """
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")
