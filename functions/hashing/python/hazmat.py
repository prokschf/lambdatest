from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import json

def lambda_handler(event, context):
    input_string = event.get('inputString', '')
    
    if not input_string:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: inputString not provided')
        }
    
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(input_string.encode('utf-8'))
    sha256_hash = digest.finalize().hex()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'sha256Hash': sha256_hash})
    }
