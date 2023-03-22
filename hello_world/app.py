import json
import os
import yaml
import boto3

def lambda_handler(event, context):
    event_type = event.get('detail-type')
    if event_type == 'EC2 Instance State-change Notification':
        instance_id = event['detail']['instance-id']
        state = event['detail']['state']
        # ec2 state: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instance-state-changes.html
        if state == 'running':
            pass
            instance_name = get_instance_name(instance_id)
            print('instance name is: ', instance_name)
            create_alarm_group(instance_id, instance_name)
        elif state == 'terminated':
            pass

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "alarm created/destroyed",
                # "location": ip.text.replace("\n", "")
            }),
        }

def get_instance_name(instance_id):
    instance_name = ''
    region = os.environ['TARGET_REGION']
    ec2 = boto3.client('ec2', region)
    # 查询特定实例ID的详细信息，包括实例名称
    response = ec2.describe_instances(InstanceIds=[instance_id])

    # 输出实例名称
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
    return instance_name


def create_alarm_group(instance_id, instance_name):
    with open('ec2-alarm.yaml') as file:
        # 将文件内容解析为 YAML
        config = yaml.load(file, Loader=yaml.FullLoader)
        # 访问配置数据
        for item in config:
            # print(item)
            prefix=item['prefix']
            if instance_name.lower().startswith(prefix.strip().lower()):
                for alarm in item['alarms']:
                    print(alarm)
                    create_ec2_alarm()
def create_ec2_alarm():
    cloudwatch = boto3.client('cloudwatch')
    # Create alarm
    cloudwatch.put_metric_alarm(
        AlarmName='Web_Server_CPU_Utilization',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        ActionsEnabled=False,
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': 'i-01082ea242dcdc08c'
            },
        ],
        Unit='Seconds'
    )
    print('alarm created')