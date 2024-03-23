# lambda_function.py
from annoy import AnnoyIndex
import numpy as np
import json

def build_annoy_index(embeddings, dimension=512):
    """
    Builds an Annoy index for the given embeddings.
    
    Parameters:
    - embeddings: List of embeddings.
    - dimension: The dimensionality of the embeddings.
    
    Returns:
    - An Annoy index built with the embeddings.
    """
    annoy_index = AnnoyIndex(dimension, 'euclidean')
    for i, embedding in enumerate(embeddings):
        annoy_index.add_item(i, embedding)
    annoy_index.build(10)  # 10 trees
    return annoy_index

def find_k_nearest_neighbors(annoy_index, input_embedding, k=5):
    """
    Finds the k-nearest neighbors for a given input embedding using the Annoy index.
    
    Parameters:
    - annoy_index: An Annoy index of embeddings.
    - input_embedding: The input embedding as a list.
    - k: The number of nearest neighbors to find.
    
    Returns:
    - Indices of the k-nearest neighbors in the list of embeddings.
    """
    nearest_neighbors = annoy_index.get_nns_by_vector(input_embedding, k, include_distances=False)
    return nearest_neighbors

def lambda_handler(event, context):
    embeddings = event.get('embeddings', [])
    input_embedding = event.get('input_embedding', [])
    k = event.get('k', 5)
    
    # Validate inputs
    if len(embeddings) == 0 or len(input_embedding) == 0:
        return {'statusCode': 400, 'body': json.dumps('Error: embeddings or input_embedding not provided')}
    
    # Assuming all embeddings have the same dimension
    dimension = len(embeddings[0])
    annoy_index = build_annoy_index(embeddings, dimension)
    
    # Find k-nearest neighbors
    nearest_neighbors = find_k_nearest_neighbors(annoy_index, input_embedding, k)
    
    # Return the indices of the nearest neighbors
    return {'statusCode': 200, 'body': json.dumps({'nearest_neighbors': nearest_neighbors})}
