package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func main() {
	bucketName := "imgtemp2" // Specify your bucket name
	objectKey := "short.txt" // Specify the S3 object key

	// Load the AWS default configuration
	cfg, err := config.LoadDefaultConfig(context.TODO(),
		config.WithRegion("us-east-1"), // Specify the AWS Region
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to load configuration, %v\n", err)
		os.Exit(1)
	}

	// Create an Amazon S3 service client
	client := s3.NewFromConfig(cfg)

	// Call S3 to get the object from the bucket
	getObjectOutput, err := client.GetObject(context.TODO(), &s3.GetObjectInput{
		Bucket: &bucketName,
		Key:    &objectKey,
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to get object, %v\n", err)
		os.Exit(1)
	}
	defer getObjectOutput.Body.Close()

	// Read the content of the S3 object
	content, err := ioutil.ReadAll(getObjectOutput.Body)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to read object body, %v\n", err)
		os.Exit(1)
	}

	// Output the text content
	fmt.Printf("S3 Object Content:\n%s\n", string(content))
}
