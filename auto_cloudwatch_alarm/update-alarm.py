import json
import os
import logging
import yaml
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def lambda_handler(event, context):
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    
    filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
    if event.get('ec2-prefix') != None:
        filters.append({'Name': 'tag:Name', 'Values': [event['ec2-prefix'] + '*']})
        
    region = os.environ['TARGET_REGION']
    ec2_client = boto3.client('ec2', region)
    # 使用 describe_instances() 方法查询符合条件的实例信息
    response = ec2_client.describe_instances(Filters=filters)

    # 处理第一页查询结果
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id, instance_name = instance['InstanceId'], instance['Tags'][0]['Value']
            logger.info('instance id: %s; instance name: %s', instance_id, instance_name)
            update_alarm_group(instance_id, instance_name)

    # 如果查询结果超过了 1000 条，则继续查询下一页的结果
    while 'NextToken' in response:
        next_token = response['NextToken']
        response = ec2_client.describe_instances(Filters=filters, NextToken=next_token)

        # 处理下一页查询结果
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id, instance_name = instance['InstanceId'], instance['Tags'][0]['Value']
                logger.info('instance id: %s; instance name: %s', instance_id, instance_name)
                update_alarm_group(instance_id, instance_name)
   

def update_alarm_group(instance_id, instance_name):
    with open('ec2-alarm.yaml') as file:
        # 将文件内容解析为 YAML
        config = yaml.load(file, Loader=yaml.FullLoader)
        # 访问配置数据
        for item in config:
            prefix=item['prefix']
            if instance_name.lower().startswith(prefix.strip().lower()):
                for alarm in item['alarms']:
                    update_ec2_alarm(alarm, instance_id, instance_name)
                
def update_ec2_alarm(alarm, instance_id, instance_name):
    cloudwatch = boto3.client('cloudwatch')
    
    alarm_name_pattern = alarm['alarmName']
    alarm_name = alarm_name_pattern.replace('{INSTANCENAME}', instance_name)
    logger.info('trying to update alarm: %s', alarm_name)
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
    logger.info('alarm updated: %s', alarm_name)