# Define the base image
FROM public.ecr.aws/lambda/python:3.8




# Copy function code
COPY functions/hashing/python/hashl.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "hashl.lambda_handler" ]
