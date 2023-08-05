#  SPDX-License-Identifier: MIT
#  Copyright 2023 John Mille <john@ews-network.net>

"""Validators for resource and properties"""

from troposphere import AWSHelperFn


def capacity_validator(value: int):
    """Validates the Min & Max Capacity are valid"""
    if not isinstance(value, (int, AWSHelperFn)):
        raise TypeError("MinCapacity/MaxCapacity must be a positive integer", int)
    if isinstance(value, int) and value < 0:
        raise ValueError(
            "MinCapacity/MaxCapacity must be a positive integer. Got", value
        )


def validate_schedule(value: str):
    if not isinstance(value, (str, AWSHelperFn)):
        raise TypeError(f"Schedule must be a string. Got {type(value)}", str)
    if isinstance(value, str) and not (
        value.startswith("at(")
        or value.startswith("cron(")
        or value.startswith("rate(")
    ):
        raise ValueError(f"Schedule start with either at(|cron(|rate(. Got {value}")
