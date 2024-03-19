# Define the base image
FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install pandas --no-cache-dir


# Copy function code
COPY functions/invmatrix/python/pand.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "pand.lambda_handler" ]
