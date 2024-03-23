# lambda_function.py
import numpy as np
import json

def generate_random_embeddings(num_embeddings, dimension=512):
    return np.random.rand(num_embeddings, dimension)

def find_k_nearest_neighbors(input_embedding, embeddings, k=5):
    distances = np.linalg.norm(embeddings - input_embedding, axis=1)
    nearest_neighbor_indices = np.argsort(distances)[:k]
    return nearest_neighbor_indices

def lambda_handler(event, context):
    # Example event: {'num_embeddings': 100, 'k': 5, 'input_index': 10}
    num_embeddings = event.get('num_embeddings', 100)
    k = event.get('k', 5)
    input_index = event.get('input_index', 0)  # Index of the input embedding in the generated list
    
    # Generate embeddings
    embeddings = generate_random_embeddings(num_embeddings)
    
    # Assume we use one of the generated embeddings as the input
    input_embedding = embeddings[input_index]
    
    # Find k-nearest neighbors
    nearest_neighbors = find_k_nearest_neighbors(input_embedding, embeddings, k)
    
    # Return the indices of the nearest neighbors
    return {
        'statusCode': 200,
        'body': json.dumps({'nearest_neighbors': nearest_neighbors.tolist()})
    }
