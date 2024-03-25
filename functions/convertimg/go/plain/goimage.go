package main

import (
	"bytes"
	"context"
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	"net/http"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/disintegration/imaging"
	"github.com/google/uuid"
)

const OUTPUT_BUCKET = "imgtemp2"

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
		// Download the image
		response, err := http.Get(url)
		if err != nil {
			return "", fmt.Errorf("failed to download image: %w", err)
		}
		defer response.Body.Close()

		img, err := imaging.Decode(response.Body)
		if err != nil {
			return "", fmt.Errorf("failed to decode image: %w", err)
		}

		// Process the image: resize, apply color filter, blur a region
		img = imaging.Resize(img, 500, 500, imaging.Lanczos)
		img = adjustSaturation(img, 2.0) // Adjust saturation by a factor of 2.0

		// Blur region
		blurRegion := imaging.Crop(img, image.Rect(0, 0, 100, 100))
		blurRegion = imaging.Blur(blurRegion, 10)
		img = imaging.Paste(img, blurRegion, image.Pt(0, 0))

		// Encode the image to buffer
		var buf bytes.Buffer
		err = jpeg.Encode(&buf, img, nil)
		if err != nil {
			return "", fmt.Errorf("failed to encode image: %w", err)
		}

		// Upload the processed image to S3
		outputFileKey := fmt.Sprintf("processed_%s.jpg", uuid.NewString())
		_, err = s3Client.PutObject(ctx, &s3.PutObjectInput{
			Bucket:      aws.String(OUTPUT_BUCKET),
			Key:         aws.String(outputFileKey),
			Body:        bytes.NewReader(buf.Bytes()),
			ContentType: aws.String("image/jpeg"),
		})
		if err != nil {
			return "", fmt.Errorf("failed to upload image to S3: %w", err)
		}
	}

	return "Image processing completed.", nil
}

// adjustSaturation increases the saturation of an image by the specified factor.
// A factor of 1.0 returns the original image. Less than 1.0 reduces saturation, greater than 1.0 increases it.
// This is a simplified approach and does not convert to HSL.
func adjustSaturation(img image.Image, factor float64) *image.NRGBA {
	bounds := img.Bounds()
	dst := image.NewNRGBA(bounds)
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			original := img.At(x, y)
			r, g, b, a := original.RGBA()
			// Convert to 0-255 range
			r8, g8, b8, a8 := uint8(r>>8), uint8(g>>8), uint8(b>>8), uint8(a>>8)
			// Apply a simple saturation algorithm
			nr, ng, nb := simpleSaturationAdjust(r8, g8, b8, factor)
			dst.Set(x, y, color.NRGBA{R: nr, G: ng, B: nb, A: a8})
		}
	}
	return dst
}

// simpleSaturationAdjust simulates saturation adjustment.
func simpleSaturationAdjust(r, g, b uint8, factor float64) (uint8, uint8, uint8) {
	// Convert RGB to grayscale using luminance-preserving approach
	gray := uint8(0.299*float64(r) + 0.587*float64(g) + 0.114*float64(b))
	// Apply saturation adjustment
	nr := saturate(uint8(float64(r-gray)*factor + float64(gray)))
	ng := saturate(uint8(float64(g-gray)*factor + float64(gray)))
	nb := saturate(uint8(float64(b-gray)*factor + float64(gray)))
	return nr, ng, nb
}

// saturate ensures the color values are within the 0-255 range.
func saturate(value uint8) uint8 {
	if value < 0 {
		return 0
	}
	if value > 255 {
		return 255
	}
	return value
}

func main() {
	lambda.Start(HandleRequest)
}
