# Define the base image for the build stage
FROM golang:1.22 as builder

# Set the working directory in the container
WORKDIR /go/src/app

# Copy the go.mod and go.sum files to the container's workspace to download dependencies
# This assumes your functions/invmatrix/go directory contains these files
COPY functions/s3read/go/sdk/go.mod functions/s3read/go/sdk/go.sum ./
# Download the dependencies - this can be cached if not changed
RUN go mod download

# Now copy the local package files to the container's workspace
COPY functions/s3read/go/sdk/ .

# Build the Go app for Linux as AWS Lambda runs on Linux
# -o specifies the output filename, here assuming the output binary is named "main"
RUN CGO_ENABLED=0 GOOS=linux go build -v -o main .

# Use the AWS provided base image for Go runtime
FROM public.ecr.aws/lambda/go:1

# Copy the binary from the builder stage to the production image
COPY --from=builder /go/src/app/main ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (assuming "main" is both the binary name and handler function)
CMD [ "main" ]
