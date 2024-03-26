import boto3

def get_latest_image_size_for_each_repo():
    # Create an ECR client
    client = boto3.client('ecr')
    
    # List all ECR repositories
    response = client.describe_repositories()
    repositories = response['repositories']
    
    # Dictionary to hold the latest image size for each repo
    latest_image_sizes = {}
    
    # Iterate through repositories
    for repo in repositories:
        repo_name = repo['repositoryName']
        # List images in the current repository, sorted by push time in descending order
        images_response = client.describe_images(
            repositoryName=repo_name,
            filter={'tagStatus': 'ANY'},
            maxResults=1
        )
        
        # Check if there are images in the repository
        if images_response['imageDetails']:
            # Get the latest image
            latest_image = images_response['imageDetails'][0]
            # Extract the image size
            image_size = latest_image['imageSizeInBytes']
            latest_image_sizes[repo_name] = image_size
    
    return latest_image_sizes

# Call the function and print the results
latest_image_sizes = get_latest_image_size_for_each_repo()
for repo_name, size in latest_image_sizes.items():
    print(f"Repository: {repo_name}, Latest Image Size: {size} bytes")
