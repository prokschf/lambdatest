# Define the base image
FROM public.ecr.aws/lambda/python:3.8


RUN pip3 install numpy --no-cache-dir

# Copy function code
COPY functions/hashing/python/hazmat.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "hazmat.lambda_handler" ]
