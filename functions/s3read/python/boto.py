import boto3

def lambda_handler(event, context):
    bucket_name = "imgtemp2"  # Specify your bucket name
    object_key = "short.txt"  # Specify the S3 object key

    # Create an S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')  # Specify the AWS Region

    try:
        # Call S3 to get the object from the bucket
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read the content of the S3 object
        content = response['Body'].read().decode('utf-8')
        
        # Output the text content
        print("S3 Object Content:\n", content)
    except Exception as e:
        print("Failed to get object:", e)

if __name__ == "__main__":
    main()
