import boto3
import os
import requests

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

def get_instance_ip(instance_id):
    # Get the instance IP
    instance_ip = ec2.describe_instances(
        InstanceIds=[
            instance_id
        ]
    )['Reservations'][0]['Instances'][0]['PrivateIpAddress']

    # Return the instance IP
    return instance_ip

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

def check_target(url):
    # Check the target health
    health_check_response = requests.get(url)
    # ensure health check response body contains os.environ['health_check_body_value']
    if os.environ['health_check_body_value'] in health_check_response.text:
        print('Target is healthy.')
        return True
    else:
        print('Target is unhealthy.')
        return False

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
            host_path = get_lambda_url(target['Target']['Id'])
        elif target_type == 'instance':
            host_path = get_instance_ip(target['Target']['Id'])
        elif target_type == 'ip':
            host_path = target['Target']['Id']
        else:
            print('Unsupported target type.')

        url = f"{os.environ['health_check_protocol'].lower()}://{host_path}:{os.environ['health_check_port']}{os.environ['health_check_path']}"
        if not check_target(url):
            print(f"Target {target['Target']['Id']} is unhealthy. Deregistering...")
            elbv2.deregister_targets(
                TargetGroupArn=target_group_arn,
                Targets=[
                    {
                        'Id': target['Target']['Id']
                    }
                ]
            )

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
