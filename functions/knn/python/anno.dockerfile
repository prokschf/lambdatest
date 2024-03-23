# Define the base image
FROM public.ecr.aws/lambda/python:3.8

# Install build tools
RUN yum install -y gcc-c++ && \
    yum clean all

# Install Python packages
RUN pip3 install annoy numpy --no-cache-dir

# Copy function code
COPY functions/knn/python/anno.py ./

# Set the CMD to your handler (AWS Lambda sets the handler via environment variables)
CMD ["anno.lambda_handler"]
