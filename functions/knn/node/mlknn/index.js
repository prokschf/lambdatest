const KNN = require('ml-knn');
const math = require('mathjs');

exports.handler = async (event) => {
    const embeddings = event.embeddings;
    const input_embedding = event.input_embedding;
    const k = event.k || 5;

    // Convert the list of embeddings into a format suitable for ml-knn
    const labels = embeddings.map((_, index) => index); // Dummy labels
    const knn = new KNN(embeddings, labels, {k: k});

    // Predict the k-nearest neighbors for the input embedding
    const indices = knn.predict([input_embedding]);

    // Prepare the response
    const response = {
        statusCode: 200,
        body: JSON.stringify({
            message: "K-Nearest Neighbors indices",
            indices: indices
        })
    };

    return response;
};
