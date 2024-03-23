package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"

	"github.com/aws/aws-lambda-go/lambda"
)

type MyEvent struct {
	InputString string `json:"inputString"`
}

type MyResponse struct {
	SHA256Hash string `json:"sha256Hash"`
}

func HandleRequest(ctx context.Context, event MyEvent) (MyResponse, error) {
	// Calculate SHA-256 hash of the input string
	h := sha256.New()
	h.Write([]byte(event.InputString))
	sha256Hash := hex.EncodeToString(h.Sum(nil))

	return MyResponse{SHA256Hash: sha256Hash}, nil
}

func main() {
	lambda.Start(HandleRequest)
}
