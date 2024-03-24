import requests
from PIL import Image, ImageFilter, ImageEnhance
import io
import boto3
import uuid

s3 = boto3.client('s3')
output_bucket = 'imgtemp2'  # Specify your output bucket name

def lambda_handler(event, context):
    for url in event['urls']:
        try:
            # Download the image
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))

            # Process the image (resize, apply color filter, blur a region)
            image = image.resize((500, 500))
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(2.0)
            blur_region = (0, 0, 100, 100)
            region = image.crop(blur_region)
            region = region.filter(ImageFilter.GaussianBlur(10))
            image.paste(region, blur_region)

            # Save the processed image to a buffer
            buffer = io.BytesIO()
            image.save(buffer, 'JPEG')
            buffer.seek(0)

            # Upload the processed image to S3
            unique_filename = str(uuid.uuid4()) + '.jpg'

       
            s3.put_object(Bucket=output_bucket, Key=unique_filename, Body=buffer, ContentType='image/jpeg')

            print(f"Processed image")
        except Exception as e:
            print(f"Failed to process image {url}: {str(e)}")

    return {
        'statusCode': 200,
        'body': 'Image processing completed.'
    }
