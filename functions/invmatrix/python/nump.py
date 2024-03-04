import numpy as np
import json

def lambda_handler(event, context):
    # Assuming 'matrix' is passed in the event as a list of lists
    matrix = np.array(event['matrix'])
    try:
        inverse_matrix = np.linalg.inv(matrix)
        return {
            'statusCode': 200,
            'body': json.dumps(inverse_matrix.tolist())
        }
    except np.linalg.LinAlgError:
        return {
            'statusCode': 400,
            'body': 'The matrix is singular and cannot be inverted.'
        }
