package main

import (
	"context"
	"log"
	"math"

	"github.com/aws/aws-lambda-go/lambda"
)

// Define the input structure
type KnnRequest struct {
	Embeddings     [][]float64 `json:"embeddings"`
	InputEmbedding []float64   `json:"input_embedding"`
	K              int         `json:"k"`
}

// Define the response structure
type KnnResponse struct {
	MostFrequentLabel float64 `json:"most_frequent_label"`
}

// HandleRequest is the Lambda function implementation
func HandleRequest(ctx context.Context, request KnnRequest) (KnnResponse, error) {
	labels := make(map[float64]int)
	distances := []float64{}

	log.Println("Starting to process embeddings")

	for i, embedding := range request.Embeddings {
		if len(embedding) == 0 {
			log.Printf("Empty embedding found at index %d\n", i)
			continue // Skip empty embeddings to avoid panics
		}

		if len(request.InputEmbedding) > len(embedding)-1 {
			log.Printf("Input embedding is longer than embedding[%d] - cannot compute distance\n", i)
			continue // Skip this embedding to avoid out-of-range access
		}

		dist := euclideanDistance(request.InputEmbedding, embedding[:len(embedding)-1])
		distances = append(distances, dist)
		label := embedding[len(embedding)-1] // Potential panic point if embedding is empty
		labels[label]++
		log.Printf("Processed embedding at index %d: distance=%.2f, label=%.2f\n", i, dist, label)
	}

	var mostFrequentLabel float64
	maxCount := 0
	for label, count := range labels {
		if count > maxCount {
			mostFrequentLabel = label
			maxCount = count
		}
	}

	log.Printf("Most frequent label: %.2f with count %d\n", mostFrequentLabel, maxCount)

	return KnnResponse{MostFrequentLabel: mostFrequentLabel}, nil
}

func euclideanDistance(a, b []float64) float64 {
	var sum float64
	minLength := math.Min(float64(len(a)), float64(len(b)))
	for i := 0; i < int(minLength); i++ {
		sum += math.Pow(a[i]-b[i], 2)
	}
	return math.Sqrt(sum)
}

func main() {
	lambda.Start(HandleRequest)
}
