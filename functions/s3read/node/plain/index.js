// Import required AWS SDK clients and commands for Node.js
const { S3Client, GetObjectCommand } = require("@aws-sdk/client-s3");
const { Lambda } = require("aws-sdk");

// Define the streamToString function directly in this script
async function streamToString(stream) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("error", reject);
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
  });
}

// Lambda handler function
exports.handler = async (event) => {
  // Extract bucketName and objectKey from the event object
  const bucketName = event.bucketName; // Ensure these values are passed in the event
  const objectKey = event.objectKey; // Ensure these values are passed in the event

  // Create an S3 client
  const client = new S3Client({
    region: "us-east-1", // Specify the AWS Region
  });

  // Create the command to get the object
  const command = new GetObjectCommand({
    Bucket: bucketName,
    Key: objectKey,
  });

  try {
    // Send the command to get the object
    const { Body } = await client.send(command);

    // Convert the stream to a string using the defined function
    const content = await streamToString(Body);

    // Return the text content
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Successfully retrieved object",
        content: content,
      }),
    };
  } catch (err) {
    console.error("Failed to get object:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: "Failed to retrieve object",
        error: err.toString(),
      }),
    };
  }
};
