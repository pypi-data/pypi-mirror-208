#  SPDX-License-Identifier: MIT
#  Copyright 2023 John Mille <john@ews-network.net>

__author__ = """John Mille"""
__email__ = "john@ews-network.net"
__version__ = "0.1.1"


"""Troposphere resource to cover AwsCommunity::ApplicationAutoscaling::ScheduledAction"""

from troposphere import AWSObject, AWSProperty, PropsDictType

from troposphere_awscommunity_applicationautoscaling_scheduledaction.validators import (
    capacity_validator,
    validate_schedule,
)


class ScalableTargetAction(AWSProperty):
    """
    ScalableTargetAction: https://github.com/aws-cloudformation/community-registry-extensions/blob/main/resources/ApplicationAutoscaling_ScheduledAction/docs/scalabletargetaction.md
    """

    props: PropsDictType = {
        "MaxCapacity": (capacity_validator, False),
        "MinCapacity": (capacity_validator, False),
    }


class ScheduledAction(AWSObject):
    """
    `ScheduledAction`: https://github.com/aws-cloudformation/community-registry-extensions/tree/main/resources/ApplicationAutoscaling_ScheduledAction/docs
    """

    resource_type = "AwsCommunity::ApplicationAutoscaling::ScheduledAction"

    props: PropsDictType = {
        "EndTime": (str, False),
        "ResourceId": (str, True),
        "ScalableDimension": (str, True),
        "ScalableTargetAction": (ScalableTargetAction, True),
        "Schedule": (validate_schedule, True),
        "ScheduledActionName": (str, True),
        "ServiceNamespace": (str, True),
        "StartTime": (str, False),
        "Timezone": (str, False),
    }
