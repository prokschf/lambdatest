# Use the AWS Lambda Node.js base image
FROM public.ecr.aws/lambda/nodejs:20

# Set the working directory to /var/task which is the working directory of the base image
WORKDIR /var/task

# Copy package.json and package-lock.json (if available) to the container
COPY functions/knn/node/mlknn/package*.json ./

# Install dependencies defined in package.json
RUN npm install

# Copy the rest of your Lambda function code
COPY functions/knn/node/mlknn/ .

# Set the CMD to your handler (assuming the handler is defined in index.js with an export name of 'handler')
CMD ["index.handler"]
