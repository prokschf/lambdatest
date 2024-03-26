import boto3

# Initialize the ECR client
ecr_client = boto3.client('ecr')

def delete_all_but_latest_image(repository_name):
    # List all images in the repository
    response = ecr_client.list_images(
        repositoryName=repository_name,
        maxResults=1000
    )
    image_ids = response['imageIds']
    if len(image_ids) == 0:
        return
    # Retrieve details for all images to get the image push date
    detailed_images = ecr_client.describe_images(
        repositoryName=repository_name,
        imageIds=image_ids
    )['imageDetails']
    
    # Sort images by push date
    detailed_images.sort(key=lambda x: x['imagePushedAt'], reverse=True)
    
    # Skip the latest image and prepare a list of all others for deletion
    images_to_delete = [{'imageDigest': image['imageDigest']} for image in detailed_images[1:]]
    
    if images_to_delete:
        # Delete all but the latest image
        ecr_client.batch_delete_image(
            repositoryName=repository_name,
            imageIds=images_to_delete
        )
        print(f"Deleted {len(images_to_delete)} images from repository {repository_name}.")
    else:
        print(f"No images to delete from repository {repository_name}.")
lambda_client = boto3.client('lambda')

def delete_all_lambda_functions():
    # List all Lambda functions
    functions = lambda_client.list_functions()
    
    if 'Functions' in functions:
        for function in functions['Functions']:
            function_name = function['FunctionName']
            try:
                # Delete the Lambda function
                lambda_client.delete_function(FunctionName=function_name)
                print(f"Deleted Lambda function: {function_name}")
            except Exception as e:
                print(f"Failed to delete Lambda function {function_name}: {str(e)}")
    else:
        print("No Lambda functions to delete.")

def main():
    delete_all_lambda_functions()
    # List all ECR repositories
    response = ecr_client.describe_repositories()
    repositories = response['repositories']
    
    # Process each repository
    for repo in repositories:
        repository_name = repo['repositoryName']
        delete_all_but_latest_image(repository_name)

if __name__ == "__main__":
    main()
