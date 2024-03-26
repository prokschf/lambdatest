package main

import (
	"context"
	"fmt"
	"io"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

// Define the structure of your event here
// For this example, we're assuming the event has bucketName and objectKey fields
type MyEvent struct {
	BucketName string `json:"bucketName"`
	ObjectKey  string `json:"objectKey"`
}

// Handler is the Lambda function handler
func Handler(ctx context.Context, event MyEvent) (string, error) {
	// Load the AWS default configuration
	cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion("us-east-1")) // Specify the AWS Region
	if err != nil {
		return "", fmt.Errorf("failed to load configuration, %v", err)
	}

	// Create an Amazon S3 service client
	client := s3.NewFromConfig(cfg)

	// Call S3 to get the object from the bucket
	getObjectOutput, err := client.GetObject(context.TODO(), &s3.GetObjectInput{
		Bucket: &event.BucketName,
		Key:    &event.ObjectKey,
	})
	if err != nil {
		return "", fmt.Errorf("failed to get object, %v", err)
	}
	defer getObjectOutput.Body.Close()

	// Read the content of the S3 object
	content, err := io.ReadAll(getObjectOutput.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read object body, %v", err)
	}

	// Return the text content
	return string(content), nil
}

func main() {
	// Start the Lambda function handler
	lambda.Start(Handler)
}
