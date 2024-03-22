from scipy.linalg import inv
import json

def lambda_handler(event, context):
    # Assuming 'matrix' is passed in the event as a list of lists
    matrix = event['matrix']
    try:
        inverse_matrix = inv(matrix)
        return {
            'statusCode': 200,
            'body': json.dumps(inverse_matrix.tolist())
        }
    except ValueError:
        return {
            'statusCode': 400,
            'body': 'The matrix is singular and cannot be inverted.'
        }
