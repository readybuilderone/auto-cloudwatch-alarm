import json
import os
import logging
import yaml
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def lambda_handler(event, context):
    # logger.info('This is an info message')
    # logger.warning('This is a warning message')
    # logger.error('This is an error message')
    event_type = event.get('detail-type')
    if event_type == 'EC2 Instance State-change Notification':
        instance_id = event['detail']['instance-id']
        state = event['detail']['state']
        instance_name = get_instance_name(instance_id)
        logger.info('instance id: %s; instance name: %s; state: %s', instance_id, instance_name, state)
        # ec2 state: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instance-state-changes.html
        if state == 'running':
            create_alarm_group(instance_id, instance_name)
        elif state == 'terminated':
            delete_alarm_group(instance_id, instance_name) #create this function

        return {
            "statusCode": 200
        }
    logger.warning('Not a supported event type: %s', event_type)

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
            prefix=item['prefix']
            if instance_name.lower().startswith(prefix.strip().lower()):
                for alarm in item['alarms']:
                    create_ec2_alarm(alarm, instance_id, instance_name)
def create_ec2_alarm(alarm, instance_id, instance_name):
    cloudwatch = boto3.client('cloudwatch')
    
    alarm_name_pattern = alarm['alarmName']
    alarm_name = alarm_name_pattern.replace('{INSTANCENAME}', instance_name)
    logger.info('trying to create alarm: %s', alarm_name)
    # Create alarm
    # cloudwatch.put_metric_alarm(
    #     AlarmName=alarm_name,
    #     ComparisonOperator='GreaterThanThreshold',
    #     EvaluationPeriods=1,
    #     MetricName='CPUUtilization',
    #     Namespace='AWS/EC2',
    #     Period=60,
    #     Statistic='Average',
    #     Threshold=70.0,
    #     ActionsEnabled=False,
    #     AlarmDescription='Alarm when server CPU exceeds 70%',
    #     Dimensions=[
    #         {
    #         'Name': 'InstanceId',
    #         'Value': 'i-01082ea242dcdc08c'
    #         },
    #     ],
    #     Unit='Seconds'
    # )
    cloudwatch.put_metric_alarm(
        Namespace ='AWS/EC2',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id,
            },
        ],
        AlarmName= alarm_name,
        MetricName=alarm['metricName'],
        Statistic=alarm['statistic'],
        Period=alarm['period'],
        EvaluationPeriods=alarm['evaluationPeriods'],
        Threshold=alarm['threshold'],
        ComparisonOperator = alarm['comparisonOperator'],
        TreatMissingData =  alarm['treatMissingData'],
        OKActions=[
            alarm['okActions'],
        ],
        AlarmActions=[
            alarm['alarmActions'],
        ],
        InsufficientDataActions=[
            alarm['insufficientDataActions'],
        ],
    )
    logger.info('alarm created: %s', alarm_name)

def delete_alarm_group(instance_id, instance_name):
    with open('ec2-alarm.yaml') as file:
        # 将文件内容解析为 YAML
        config = yaml.load(file, Loader=yaml.FullLoader)
        # 访问配置数据
        for item in config:
            prefix=item['prefix']
            if instance_name.lower().startswith(prefix.strip().lower()):
                for alarm in item['alarms']:
                    delete_ec2_alarm(alarm, instance_name)
                    
def delete_ec2_alarm(alarm, instance_name):
    cloudwatch = boto3.client('cloudwatch')
    alarm_name_pattern = alarm['alarmName']
    alarm_name = alarm_name_pattern.replace('{INSTANCENAME}', instance_name)
    logger.info('trying to delete alarm: %s', alarm_name)
    cloudwatch.delete_alarms(
        AlarmNames=[
            alarm_name
        ]
    ) 
    logger.info('alarm deleted: %s', alarm_name)