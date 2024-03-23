package com.example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.stream.Collectors;

public class KnnFunction implements RequestHandler<Map<String, Object>, String> {

    @Override
    public String handleRequest(Map<String, Object> input, Context context) {
        // Extract embeddings and query embedding from the input map
        List<List<Double>> embeddings = (List<List<Double>>) input.get("embeddings");
        List<Double> queryEmbedding = (List<Double>) input.get("input_embedding");
        int k = (Integer) input.get("k");

        // Convert List<Double> to double[] for the query point
        double[] queryArray = queryEmbedding.stream().mapToDouble(Double::doubleValue).toArray();

        // Priority Queue to keep track of the k nearest neighbors
        PriorityQueue<double[]> neighbors = new PriorityQueue<>(Comparator.comparingDouble(e -> -euclideanDistance(e, queryArray)));
        
        // Iterate over embeddings to find the k nearest neighbors
        embeddings.forEach(embedding -> {
            double[] embeddingArray = embedding.stream().mapToDouble(Double::doubleValue).toArray();
            neighbors.add(embeddingArray);
            if (neighbors.size() > k) {
                neighbors.poll();
            }
        });

        // Count the labels of the k nearest neighbors
        Map<Double, Integer> labelCounts = new HashMap<>();
        neighbors.forEach(neighbor -> {
            double label = neighbor[neighbor.length - 1];
            labelCounts.put(label, labelCounts.getOrDefault(label, 0) + 1);
        });

        // Determine the most frequent label
        double mostFrequentLabel = labelCounts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElseThrow(() -> new RuntimeException("Unable to determine the most frequent label"));

        return "Most frequent label among " + k + " nearest neighbors is: " + mostFrequentLabel;
    }

    private double euclideanDistance(double[] a, double[] b) {
        double sum = 0.0;
        for (int i = 0; i < b.length; i++) {
            sum += Math.pow(a[i] - b[i], 2);
        }
        return Math.sqrt(sum);
    }
}
