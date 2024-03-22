import pandas as pd
import numpy as np
import json

def lambda_handler(event, context):
    # Assuming 'matrix' is passed in the event as a DataFrame-like list of lists
    df = pd.DataFrame(event['matrix'])
    try:
        inverse_matrix = pd.DataFrame(np.linalg.inv(df.values), index=df.columns, columns=df.index)
        return {
            'statusCode': 200,
            'body': json.dumps(inverse_matrix.values.tolist())
        }
    except np.linalg.LinAlgError:
        return {
            'statusCode': 400,
            'body': 'The matrix is singular and cannot be inverted.'
        }
