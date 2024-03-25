# Define the base image
FROM public.ecr.aws/lambda/python:3.8


# Copy function code
COPY functions/fib/python/plain.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "plain.lambda_handler" ]
