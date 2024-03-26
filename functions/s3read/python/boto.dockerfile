# Define the base image
FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install boto3 --no-cache-dir
# Copy function codeboto.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "boto.lambda_handler" ]
