import time
import subprocess
import boto3
import base64
import random
import json



# Initialize boto3 clients
ecr_client = boto3.client('ecr', region_name='us-east-1')  # Update if using private ECR
lambda_client = boto3.client('lambda', region_name='us-east-1')
logs_client = boto3.client('logs')

def repository_exists(repository_name):
    try:
        response = ecr_client.describe_repositories(repositoryNames=[repository_name])
        return True
    except ecr_client.exceptions.RepositoryNotFoundException:
        return False

def create_or_update_repository(repository_name):
    if not repository_exists(repository_name):
        # Repository does not exist, so create it
        response = ecr_client.create_repository(repositoryName=repository_name)
        print(f"Repository created: {response['repository']['repositoryUri']}")
        time.sleep(4)
    else:
        # Repository exists, update as needed (example shown: set scan on push)
        response = ecr_client.put_image_scanning_configuration(
            repositoryName=repository_name,
            imageScanningConfiguration={'scanOnPush': True}
        )
        print(f"Repository updated: {repository_name}")


def authenticate_docker_to_ecr(proxy_endpoint):
    response = ecr_client.get_authorization_token()
    token = response['authorizationData'][0]['authorizationToken']
    username, password = base64.b64decode(token).decode('utf-8').split(':')
    
    # Use the decoded username and password to login
    login_command = ['docker', 'login', '--username', username, '--password', password, proxy_endpoint]
    ret = subprocess.run(login_command, check=True, shell=True)  # On Windows, you might need `shell=True` for this to work correctly.
    print (ret)

def build_and_push_docker_image(ecr_repository, image_tag, dockerfile_path):
    # Build the Docker image
    full_image_name = f'{ecr_repository}:{image_tag}'
    subprocess.run(['docker', 'build', '-t', full_image_name, '-f', dockerfile_path, '.'], check=True)

    # Tag the Docker image for ECR
    subprocess.run(['docker', 'tag', full_image_name, full_image_name], check=True)

    # Push the Docker image to ECR
    subprocess.run(['docker', 'push', full_image_name], check=True)

    return full_image_name

def create_or_update_lambda_function(image_uri, lambda_function_name):
    try:
        
        lambda_client.create_function(
            FunctionName=lambda_function_name,
            Code={'ImageUri': image_uri},
            PackageType='Image',
            Role='arn:aws:iam::896349342502:role/service-role/Bedrock_runner-role-xbe5r7cd',
            Timeout=15,
            MemorySize=128
        )
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=lambda_function_name,
            ImageUri=image_uri
        )

def extract_latest_invocation_details(log_group_name, x=10):
    # Get the latest log stream
    streams = logs_client.describe_log_streams(
        logGroupName=log_group_name,
        orderBy='LastEventTime',
        descending=True,
        limit=1
    )
    if not streams['logStreams']:
        return []

    latest_stream_name = streams['logStreams'][0]['logStreamName']
    
    # Fetch the latest log events from the stream, adjust limit as needed
    events = logs_client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=latest_stream_name,
        limit=6*x  # Adjust based on how many latest events you want to fetch
    )
    
    # Initialize list to hold details of each invocation
    invocations_details = []
    
    # Iterate through events to find memory and duration
    for event in events['events']:
        message = event['message']
        invocation_detail = {}
        
        # Parsing for Max Memory Used and Duration
        if "Max Memory Used" in message:
            memory_used_mb = message.split("Max Memory Used: ")[1].split(" MB")[0]
            invocation_detail['memory_used_mb'] = memory_used_mb
        if "Duration" in message:
            duration_parts = message.split("Duration: ")[1].split(" ms")
            billed_duration_ms = duration_parts[0].strip() if len(duration_parts) > 0 else None
            invocation_detail['billed_duration_ms'] = billed_duration_ms
        
        # Only append if both memory and duration were found
        if invocation_detail:
            invocations_details.append(invocation_detail)
    
    # Return the extracted details for the latest x invocations
    return invocations_details

def generate_random_matrix(rows, cols, min_value, max_value):
    return [[random.randint(min_value, max_value) for _ in range(cols)] for _ in range(rows)]


def invoke_lambda_and_get_stats(lambda_function_name, log_group_name):
    for _ in range(10):
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({"matrix": generate_random_matrix(5, 5, -10, 10)
            })
        )
        time.sleep(0.1)
    time.sleep(5)
    stats = extract_latest_invocation_details(log_group_name)
    return stats

def runner(task, lang, lib):
    repo_name =  task + lang + lib
    ecr_repository = '896349342502.dkr.ecr.us-east-1.amazonaws.com/' + repo_name  # Change to your ECR repository URI
    image_tag = 'latest'
    dockerfile_path = f"functions/{task}/{lang}/{lib}.dockerfile"
    lambda_function_name = f'{task}-{lib}-{lang}'
    log_group_name = f'/aws/lambda/{lambda_function_name}'
    proxy_endpoint = "896349342502.dkr.ecr.us-east-1.amazonaws.com"

    create_or_update_repository(repo_name)
    authenticate_docker_to_ecr(proxy_endpoint)      
    image_uri = build_and_push_docker_image(ecr_repository, image_tag, dockerfile_path)
    create_or_update_lambda_function(image_uri, lambda_function_name)
    execution_stats = invoke_lambda_and_get_stats(lambda_function_name, log_group_name)
    print(execution_stats)


task = "invmatrix"
lang = "java"
lib = "math3"

runner(task, lang, lib)

