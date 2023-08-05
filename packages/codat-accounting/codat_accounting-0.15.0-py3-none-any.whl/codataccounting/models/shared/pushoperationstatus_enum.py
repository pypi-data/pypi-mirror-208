"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
from enum import Enum

class PushOperationStatusEnum(str, Enum):
    r"""The status of the push operation."""
    PENDING = 'Pending'
    FAILED = 'Failed'
    SUCCESS = 'Success'
    TIMED_OUT = 'TimedOut'
