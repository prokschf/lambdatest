# lambda_function.py
import numpy as np
import json

def find_k_nearest_neighbors(input_embedding, embeddings, k=5):
    distances = np.linalg.norm(embeddings - input_embedding, axis=1)
    nearest_neighbor_indices = np.argsort(distances)[:k]
    return nearest_neighbor_indices.tolist()

def lambda_handler(event, context):
    # The event object should include 'embeddings', 'input_embedding', and 'k'
    embeddings = np.array(event.get('embeddings', []))
    input_embedding = np.array(event.get('input_embedding', []))
    k = event.get('k', 5)

    if embeddings.size == 0 or input_embedding.size == 0:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: embeddings or input_embedding not provided')
        }

    # Ensure input_embedding is one-dimensional
    if input_embedding.ndim != 1:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: input_embedding must be a one-dimensional array')
        }
    
    # Find k-nearest neighbors
    nearest_neighbors = find_k_nearest_neighbors(input_embedding, embeddings, k)
    
    # Return the indices of the nearest neighbors
    return {
        'statusCode': 200,
        'body': json.dumps({'nearest_neighbors': nearest_neighbors})
    }
