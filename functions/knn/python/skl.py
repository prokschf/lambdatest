import numpy as np
import json
from sklearn.neighbors import NearestNeighbors

def find_k_nearest_neighbors(embeddings, input_embedding, k=5):
    """
    Finds the k-nearest neighbors for a given input embedding using scikit-learn.
    
    Parameters:
    - embeddings: A numpy array of shape (n_samples, n_features) with the embeddings.
    - input_embedding: The input embedding as a numpy array of shape (n_features,).
    - k: The number of nearest neighbors to find.
    
    Returns:
    - Indices of the k-nearest neighbors in the list of embeddings.
    """
    # Initialize and fit the NearestNeighbors model
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(embeddings)
    
    # Find k-nearest neighbors for the input_embedding
    distances, indices = nbrs.kneighbors([input_embedding])
    return indices[0].tolist()

def lambda_handler(event, context):
    embeddings = np.array(event.get('embeddings', []))
    input_embedding = np.array(event.get('input_embedding', []))
    k = event.get('k', 5)
    
    # Validate inputs
    if embeddings.size == 0 or input_embedding.size == 0:
        return {'statusCode': 400, 'body': json.dumps('Error: embeddings or input_embedding not provided')}
    
    # Find k-nearest neighbors
    nearest_neighbors = find_k_nearest_neighbors(embeddings, input_embedding, k)
    
    # Return the indices of the nearest neighbors
    return {'statusCode': 200, 'body': json.dumps({'nearest_neighbors': nearest_neighbors})}
