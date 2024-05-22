import boto3
import os

alb_arn                 = os.environ['alb_arn']
target_group_arn        = os.environ['target_group_arn']
health_check_path       = os.environ['health_check_path']
health_check_port       = os.environ['health_check_port']
health_check_body_value = os.environ['health_check_body_value']
health_check_protocol   = os.environ['health_check_protocol']

elbv2 = boto3.client('elbv2')
lambda_client = boto3.client('lambda')

def get_registered_targets(target_group_arn):
    # Get the registered targets for the target group
    registered_targets = elbv2.describe_target_health(
        TargetGroupArn=target_group_arn
    )['TargetHealthDescriptions']

    # Return the list of registered targets
    return registered_targets

def get_instance_info(instance_id):
    # Get the instance info
    instance_info = ec2.describe_instances(
        InstanceIds=[
            instance_id
        ]
    )['Reservations'][0]['Instances'][0]

    # Return the instance info
    return instance_info

def get_lambda_url(lambda_name):
    # Get the lambda URL
    lambda_url = lambda_client.get_function_url(
        FunctionName=lambda_name
    )['FunctionUrl']

    # Return the lambda URL
    return lambda_url

def get_alb_url(alb_arn):
    # Get the ALB URL
    alb_url = elbv2.describe_load_balancers(
        LoadBalancerArns=[
            alb_arn
        ]
    )['LoadBalancers'][0]['DNSName']

    # Return the ALB URL
    return alb_url

def check_target(target_id):
    # Check the health of the target
    health_check_response = elbv2.describe_target_health(
        TargetGroupArn=target_group_arn,
        Targets=[
            {
                'Id': target_id
            }
        ]
    )['TargetHealthDescriptions'][0]['TargetHealth']['State']

    # Return the health check response
    return health_check_response

def get_target_type(target_group_arn):
    # Get the target type
    target_type = elbv2.describe_target_groups(
        TargetGroupArns=[
            target_group_arn
        ]
    )['TargetGroups'][0]['TargetType']

    # Return the target type
    return target_type


def lambda_handler(event, context):
    registered_targets = get_registered_targets(target_group_arn)
    target_type = get_target_type(target_group_arn)
    for target in registered_targets:
        print(target['Target']['Id'])
        if target_type == 'lambda':
            url = get_lambda_url(target['Target']['Id'])
            print(lambda_url)
        elif target_type == 'instance':
            url = get_instance_info(target['Target']['Id'])
            print(instance_info)
        elif target_type == 'ip':
            url = target['Target']['Id']
            print(target['Target']['Id'])
        else:
            print('Unsupported target type.')
    print(registered_targets)
    for target in registered_targets:
        print(target['Target']['Id'])
        elbv2.deregister_targets(
            TargetGroupArn=target_group_arn,
            Targets=[
                {
                    'Id': target['Target']['Id']
                }
            ]
        )
    return {
        'statusCode': 200,
        'body': 'Targets deregistered successfully.'
    }
    """
    A simple AWS Lambda function that returns a "Hello, World!" message.
    
    Args:
        event (dict): The event data that triggered the Lambda function.
        context (object): Provides information about the invocation, function, and runtime environment.
    
    Returns:
        dict: A dictionary containing the response message.
    """
    return {
        'statusCode': 200,
        'body': 'Hello, World!'
    }
