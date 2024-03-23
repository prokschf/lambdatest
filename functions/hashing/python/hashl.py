import hashlib
import json

def lambda_handler(event, context):
    # Extract the input string from the event object
    input_string = event.get('inputString', '')

    if not input_string:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: inputString not provided')
        }

    # Calculate the SHA-256 hash of the input string
    sha256_hash = hashlib.sha256(input_string.encode('utf-8')).hexdigest()

    # Return the hash as the response
    return {
        'statusCode': 200,
        'body': json.dumps({'sha256Hash': sha256_hash})
    }
