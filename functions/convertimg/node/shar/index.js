const AWS = require('aws-sdk');
const axios = require('axios');
const sharp = require('sharp');
const { v4: uuidv4 } = require('uuid');

const s3 = new AWS.S3();
const OUTPUT_BUCKET = "imgtemp2"; // Set your bucket name in Lambda environment variables

exports.handler = async (event) => {
    for (let url of event.urls) {
        try {
            // Download the image
            const response = await axios({
                url,
                responseType: 'arraybuffer',
            });
            const imageBuffer = Buffer.from(response.data, 'binary');

            // Process the image: resize, apply color filter, blur a region
            // Adjust values as needed
            const processedImage = await sharp(imageBuffer)
                .resize(500, 500) // Example resize
                .modulate({ saturation: 2 }) // Example color filter (increase saturation)
                .composite([{ // Example blur a region
                    input: await sharp(imageBuffer)
                        .extract({ left: 0, top: 0, width: 100, height: 100 }) // Coordinates of the region to blur
                        .blur(10) // Blur intensity
                        .toBuffer(),
                    left: 0,
                    top: 0,
                }])
                .toBuffer();

            // Generate a unique filename for the output image
            const outputFileKey = `processed_${uuidv4()}.jpg`;

            // Upload the processed image to S3
            await s3.putObject({
                Bucket: OUTPUT_BUCKET,
                Key: outputFileKey,
                Body: processedImage,
                ContentType: 'image/jpeg',
            }).promise();

            console.log(`Processed image uploaded: ${outputFileKey}`);
        } catch (error) {
            console.error(`Failed to process image ${url}:`, error);
            throw error; // Re-throw the error to mark the Lambda invocation as failed
        }
    }

    return { statusCode: 200, body: 'Image processing completed.' };
};
