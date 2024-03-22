# Define the base image
FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install scipy --no-cache-dir


# Copy function code
COPY functions/invmatrix/python/sci_py.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "sci_py.lambda_handler" ]
