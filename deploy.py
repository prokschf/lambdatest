import string
import random
import datetime
import time
import subprocess
import boto3
import base64
import random
import json
import botocore.exceptions
import numpy as np



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
    subprocess.run(['docker', 'build', '-t', full_image_name , '-f', dockerfile_path, '.'], check=True)
    print (dockerfile_path)
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
        time.sleep(5)
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=lambda_function_name,
            ImageUri=image_uri
        )

def get_timestamp_ms(year=None, month=None, day=None, hour=0, minute=0, second=0):
    if year is not None and month is not None and day is not None:
        # Create a datetime object for the specified date and time
        dt = datetime.datetime(year, month, day, hour, minute, second)
    else:
        # Use current datetime if no specific date and time are provided
        dt = datetime.datetime.now()
        
    # Convert to timestamp in milliseconds
    timestamp_ms = int(dt.timestamp() * 1000)
    return timestamp_ms        

def extract_latest_invocation_details(log_group_name, start_time, x=10):
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
        limit=6*x,  # Adjust based on how many latest events you want to fetch
        startTime=start_time 
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


def invoke_lambda_and_get_stats(lambda_function_name, log_group_name, function_payload):
    start_time = get_timestamp_ms()
    attempts = 0
    max_attempts = 10  # Set a max number of attempts to avoid infinite retries
    
    while attempts < max_attempts:
        print ('attempt')
        try:
            for _ in range(10):
                print ('inv')
                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=function_payload
                )
                time.sleep(0.1)
            # If invoke is successful, break out of the loop
            break
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                print(f"Attempt {attempts + 1} failed with ResourceConflictException. Waiting 3 seconds before retrying.")
                attempts += 1
                time.sleep(3)            
            else: 
                print(f"An unexpected error occurred: {str(e)}")
                raise  # Re-raise the unexpected exception to handle it according to the outer logic
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            raise  # Re-raise the unexpected exception to handle it according to the outer logic

    if attempts == max_attempts:
        raise Exception("Maximum retry attempts reached. Function invocation failed.")
    
    # Wait a bit for logs to generate
    time.sleep(5)
    
    # Assume extract_latest_invocation_details is implemented elsewhere
    stats = extract_latest_invocation_details(log_group_name, start_time)
    return stats

def full_create_pass(task, lang, lib):
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


def generate_random_string(size_kb):
    """
    Generates a random string of size size_kb kilobytes.

    :param size_kb: Size of the string to generate in kilobytes.
    :return: A string containing random characters.
    """
    # Define the size of the string in bytes
    size_bytes = size_kb * 1024
    
    # Define the pool of characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Generate a random string of the desired size
    random_string = ''.join(random.choice(characters) for _ in range(size_bytes))
    
    return random_string

def run_lambda(task, lang, lib, function_payload):
    repo_name =  task + lang + lib
    ecr_repository = '896349342502.dkr.ecr.us-east-1.amazonaws.com/' + repo_name  # Change to your ECR repository URI
    image_tag = 'latest'
    dockerfile_path = f"functions/{task}/{lang}/{lib}.dockerfile"
    lambda_function_name = f'{task}-{lib}-{lang}'
    log_group_name = f'/aws/lambda/{lambda_function_name}'
    proxy_endpoint = "896349342502.dkr.ecr.us-east-1.amazonaws.com"

    execution_stats = invoke_lambda_and_get_stats(lambda_function_name, log_group_name, function_payload)
    print(execution_stats)
    return execution_stats

def generate_random_embeddings(num_embeddings, dimension=512):
    """
    Generates a list of random embeddings.

    Parameters:
    - num_embeddings: The number of embeddings to generate.
    - dimension: The dimension of each embedding. Defaults to 512.

    Returns:
    - A numpy array of shape (num_embeddings, dimension) with random embeddings.
    """
    return np.random.rand(num_embeddings, dimension)

def test_runner():
    task = 'hashing'
    lang = 'python'
    lib = 'hazmat'
    payload = json.dumps({"inputString": generate_random_string(32)})
    full_create_pass(task, lang, lib)
    lambda_stats = run_lambda(task, lang, lib, payload)
    print (lambda_stats)

test_runner()
    
def runner():

    tasks = {}
    tasks['invmatrix'] = {}
    payloads = {}
    payloads['invmatrix'] = [
        json.dumps({"matrix": generate_random_matrix(5, 5, -10, 10)}), #25
        json.dumps({"matrix": generate_random_matrix(10, 10, -10, 10)}), #100
        json.dumps({"matrix": generate_random_matrix(20, 20, -10, 10)}), #400
        json.dumps({"matrix": generate_random_matrix(50, 50, -10, 10)}) #2500
    ]
    tasks['invmatrix']['python'] = ['plain', 'nump', 'pand', 'sci_py']
    tasks['invmatrix']['node'] = ['plain', 'mathjs']
    tasks['invmatrix']['net'] = ['mnet']
    tasks['invmatrix']['java'] = ['math3']
    tasks['invmatrix']['go'] = ['gonum']
    
    payloads['hashing'] = [
        json.dumps({"inputString": generate_random_string(1)}),
        json.dumps({"inputString": generate_random_string(16)}),
        json.dumps({"inputString": generate_random_string(32)}),
        json.dumps({"inputString": generate_random_string(48)})
    ]
    tasks['hashing']['go'] = ['gocrypto']
    tasks['hashing']['java'] = ['javasec']
    tasks['hashing']['net'] = ['syscrypt']
    tasks['hashing']['node'] = ['crypto']
    tasks['hashing']['node'] = ['cryptojs']
    tasks['hashing']['node'] = ['hashjs']
    tasks['hashing']['python'] = ['hashl']
    tasks['hashing']['python'] = ['hazmat']

    
    payloads['knn'] = [
        json.dumps({"inputString": generate_random_string(1)}),

    ]
    tasks['knn']['python'] = ['nump']

    for task in tasks:    
        for lang in tasks[task]:
            for lib in tasks[task][lang]:
    #            full_create_pass(task, lang, lib)
                pass


    results = {}
    for task in tasks:   
        results[task] = {} 
        for lang in tasks[task]:
            results[task][lang] = {}
            for lib in tasks[task][lang]:
                payload_index = 0
                results[task][lang][lib] = []
                for payload in payloads[task]:

                    print (task)
                    print (lang)
                    print (lib)
                    print (payload)
                    lambda_stats = []
                    while len(lambda_stats) == 0:
                        lambda_stats = run_lambda(task, lang, lib, payload)
                        print ("running")
                        

                    memory_used = np.array([float(stat['memory_used_mb']) for stat in lambda_stats[1:]])
                    billed_duration = np.array([float(stat['billed_duration_ms']) for stat in lambda_stats[1:]])

                    run_result = {
                        'payload' : payload_index,
                        'memory_used_mb': {
                            'average': np.mean(memory_used),
                            'median': np.median(memory_used),
                            'std_dev': np.std(memory_used)
                        },
                        'billed_duration_ms': {
                            'average': np.mean(billed_duration),
                            'median': np.median(billed_duration),
                            'std_dev': np.std(billed_duration)
                        },
                        'billed_duration_init': {
                            'value': lambda_stats[0]['billed_duration_ms'],
                        }                     
                    }

                    # Store the calculated stats
                    results[task][lang][lib].append(run_result)
                    payload_index = payload_index + 1
                    with open('lambda_stats.json', 'w') as f:
                        json.dump(results, f, indent=4)
    # Save the results to a JSON file

    print("Results stored in lambda_stats.json")