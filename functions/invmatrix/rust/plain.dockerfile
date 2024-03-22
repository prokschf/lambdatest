# Start with Amazon Linux 2 to build the Rust application
FROM amazonlinux:2 as builder

# Install GCC, necessary build tools and OpenSSL (common dependency)
RUN yum install -y gcc gcc-c++ make openssl-devel

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the working directory
WORKDIR /usr/src/myapp

# Copy your Rust application to the image
COPY ./functions/invmatrix/rust/Cargo.toml ./Cargo.toml
COPY ./functions/invmatrix/rust/Cargo.lock ./Cargo.lock
COPY ./functions/invmatrix/rust/src ./src

# Compile the release build of your application
RUN cargo build --release

# Use AWS's provided base image for the Lambda runtime environment
FROM public.ecr.aws/lambda/provided:al2

# Copy the compiled application from the builder stage; name it 'bootstrap' (AWS Lambda's default expectation)
COPY --from=builder /usr/src/myapp/target/release/invmatrix /var/task/bootstrap

# Ensure 'bootstrap' (your Rust binary) is executable
RUN chmod +x /var/task/bootstrap

# The entrypoint is set to execute your binary. AWS Lambda custom runtime will execute the `bootstrap` binary.
ENTRYPOINT ["/var/task/bootstrap"]

CMD [ "app.handler" ]