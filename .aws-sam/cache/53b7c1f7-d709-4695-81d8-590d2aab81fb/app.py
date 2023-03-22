import json
import yaml

import requests


def lambda_handler(event, context):
    event_type = event.get('detail-type')
    if event_type == 'EC2 Instance State-change Notification':
        instance_id = event['detail']['instance-id']
        state = event['detail']['state']
        # ec2 state: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instance-state-changes.html
        if state == 'running':
            pass
        else if state == 'terminated':
            pass

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "alarm created/destroyed",
                # "location": ip.text.replace("\n", "")
            }),
        }

    with open('ec2-alarm.yaml') as file:
        # 将文件内容解析为 YAML
        config = yaml.load(file, Loader=yaml.FullLoader)
        # 访问配置数据
        print(config)


