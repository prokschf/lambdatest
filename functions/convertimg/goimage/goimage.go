package main

import (
	"bytes"
	"context"
	"fmt"
	"image"
	"image/jpeg"
	"net/http"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/disintegration/imaging"
	"github.com/google/uuid"
)

const OUTPUT_BUCKET = "imgtemp2" // Set your bucket name

type Event struct {
	URLs []string `json:"urls"`
}

func HandleRequest(ctx context.Context, event Event) (string, error) {
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return "", fmt.Errorf("error loading AWS config: %w", err)
	}

	s3Client := s3.NewFromConfig(cfg)

	for _, url := range event.URLs {
		img, err := downloadImage(url)
		if err != nil {
			return "", err
		}

		// Resize the image to 500x500 px
		resizedImg := imaging.Resize(img, 500, 500, imaging.Lanczos)

		// Apply a Gaussian blur with a radius of 5
		blurredImg := imaging.Blur(resizedImg, 5)

		// Convert to NRGBA for pixel manipulation (example for saturation change)
		nrgbaImg := imaging.Clone(blurredImg)

		// Example: Increase brightness to simulate saturation (Adjust this part for proper saturation)
		brighterImg := imaging.AdjustBrightness(nrgbaImg, 20)

		outputFileKey := fmt.Sprintf("processed_%s.jpg", uuid.New().String())
		if err := uploadToS3(ctx, s3Client, OUTPUT_BUCKET, outputFileKey, brighterImg); err != nil {
			return "", err
		}
	}

	return "Image processing completed.", nil
}

func downloadImage(url string) (image.Image, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to download image: %w", err)
	}
	defer resp.Body.Close()

	img, _, err := image.Decode(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to decode image: %w", err)
	}

	return img, nil
}

func uploadToS3(ctx context.Context, client *s3.Client, bucket, key string, img image.Image) error {
	buf := new(bytes.Buffer)
	if err := jpeg.Encode(buf, img, nil); err != nil {
		return fmt.Errorf("failed to encode image: %w", err)
	}

	_, err := client.PutObject(ctx, &s3.PutObjectInput{
		Bucket:      &bucket,
		Key:         &key,
		Body:        bytes.NewReader(buf.Bytes()),
		ContentType: aws.String("image/jpeg"),
	})
	if err != nil {
		return fmt.Errorf("failed to upload image to S3: %w", err)
	}

	return nil
}

func main() {
	lambda.Start(HandleRequest)
}
