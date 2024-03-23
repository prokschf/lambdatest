# Define the base image
FROM public.ecr.aws/lambda/python:3.8


RUN pip3 install numpy scikit-learn --no-cache-dir

# Copy function code
COPY functions/knn/python/skl.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD [ "skl.lambda_handler" ]
