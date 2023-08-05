## AwsCommunity::ApplicationAutoscaling::ScheduledAction

Troposphere object for the `AwsCommunity::ApplicationAutoscaling::ScheduledAction` resource.

See [The AWS CFN Community Registry](https://github.com/aws-cloudformation/community-registry-extensions) or the original
resource [here](https://github.com/JohnPreston/awscommunity-applicationautoscaling-scheduledaction)

The [resoure properties](https://github.com/JohnPreston/awscommunity-applicationautoscaling-scheduledaction/tree/main/docs) detail
what attributes to assign for the resource


## Example

Creates a scheduled action for a dynamodb table

```python
from troposphere import Template
from troposphere_awscommunity_applicationautoscaling_scheduledaction import (
    ScheduledAction,
    ScalableTargetAction,
)


def test_scheduled_action():
    props: dict = {
        "ScheduledActionName": "cfn-testing-resource",
        "ServiceNamespace": "dynamodb",
        "ScalableDimension": "dynamodb:table:ReadCapacityUnits",
        "ScalableTargetAction": ScalableTargetAction(
            **{"MinCapacity": 1, "MaxCapacity": 4}
        ),
        "Schedule": "cron(5 2 ? * FRI)",
        "Timezone": "Europe/London",
        "ResourceId": "table/awscommunityscheduledactiontesttable",
    }
    tpl = Template()
    action = tpl.add_resource(ScheduledAction("MyAction", **props))
    print(tpl.to_yaml())
```
Renders, with the template, the following

```yaml
Resources:
  MyAction:
    Properties:
      ResourceId: table/awscommunityscheduledactiontesttable
      ScalableDimension: dynamodb:table:ReadCapacityUnits
      ScalableTargetAction:
        MaxCapacity: null
        MinCapacity: null
      Schedule: null
      ScheduledActionName: cfn-testing-resource
      ServiceNamespace: dynamodb
      Timezone: Europe/London
```
