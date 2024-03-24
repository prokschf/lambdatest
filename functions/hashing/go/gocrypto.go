package main

import (
	"bytes"
	"context"
	"crypto/rand"
	"fmt"
	"image"
	"image/draw"
	"image/jpeg"
	"net/http"
	"os"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func HandleRequest(ctx context.Context, event map[string][]string) (string, error) {
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return "", fmt.Errorf("loading AWS config: %w", err)
	}
	s3Client := s3.NewFromConfig(cfg)

	outputBucket := os.Getenv("OUTPUT_BUCKET")
	for _, url := range event["urls"] {
		resp, err := http.Get(url)
		if err != nil {
			return "", fmt.Errorf("downloading image: %w", err)
		}
		defer resp.Body.Close()

		img, _, err := image.Decode(resp.Body)
		if err != nil {
			return "", fmt.Errorf("decoding image: %w", err)
		}

		// Example resize, assuming img is square for simplicity
		// For actual resizing, consider third-party libraries like github.com/nfnt/resize
		resizedImg := image.NewRGBA(image.Rect(0, 0, 100, 100))
		draw.Draw(resizedImg, resizedImg.Bounds(), img, img.Bounds().Min, draw.Src)

		buf := new(bytes.Buffer)
		err = jpeg.Encode(buf, resizedImg, nil)
		if err != nil {
			return "", fmt.Errorf("encoding image: %w", err)
		}

		// Generate random file name
		fileName := generateRandomString(10) + ".jpg"
		_, err = s3Client.PutObject(ctx, &s3.PutObjectInput{
			Bucket:      aws.String(outputBucket),
			Key:         aws.String(fileName),
			Body:        bytes.NewReader(buf.Bytes()),
			ContentType: aws.String("image/jpeg"),
		})
		if err != nil {
			return "", fmt.Errorf("uploading image to S3: %w", err)
		}
	}

	return "Image processing completed.", nil
}

func generateRandomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	bytes := make([]byte, n)
	if _, err := rand.Read(bytes); err != nil {
		panic(err) // rand.Read should never fail
	}
	for i, b := range bytes {
		bytes[i] = letters[b%byte(len(letters))]
	}
	return string(bytes)
}

func main() {
	lambda.Start(HandleRequest)
}
