import json

def get_matrix_inverse(matrix):
    n = len(matrix)
    # Initialize the identity matrix
    inverse = [[float(i == j) for i in range(n)] for j in range(n)]

    # Apply Gauss-Jordan elimination
    for i in range(n):
        # Find pivot
        pivot_element = matrix[i][i]
        if pivot_element == 0:
            # Simple strategy to handle a pivot of zero (swap rows)
            for k in range(i+1, n):
                if matrix[k][i] != 0:
                    matrix[i], matrix[k] = matrix[k], matrix[i]
                    inverse[i], inverse[k] = inverse[k], inverse[i]
                    break
            pivot_element = matrix[i][i]
            # If pivot_element is still zero, matrix might be singular
            if pivot_element == 0:
                raise ValueError("Matrix is singular and cannot be inverted.")
        
        # Normalize pivot row
        for j in range(n):
            matrix[i][j] /= pivot_element
            inverse[i][j] /= pivot_element

        # Eliminate column
        for k in range(n):
            if k != i:
                factor = matrix[k][i]
                for j in range(n):
                    matrix[k][j] -= factor * matrix[i][j]
                    inverse[k][j] -= factor * inverse[i][j]

    return inverse



def lambda_handler(event, context):
    matrix = event['matrix']
    
    try:
        inverse_matrix = get_matrix_inverse(matrix)
        return {
            'statusCode': 200,
            'body': json.dumps(inverse_matrix)
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': 'An error occurred: ' + str(e)
        }
