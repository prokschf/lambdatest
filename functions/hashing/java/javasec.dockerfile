# Define the base image for the build stage
FROM maven:3.8.4-openjdk-11-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml file to fetch dependencies
COPY functions/hashing/java/pom.xml .

# Fetch dependencies
RUN mvn dependency:go-offline

# Now copy the rest of the application source code
COPY functions/hashing/java/src /app/src

# Package the application
RUN mvn package

# Use the AWS provided base image for Java runtimejavav version

FROM public.ecr.aws/lambda/java:11

# Copy the built JAR file from the builder stage to the production image
COPY --from=builder /app/target/*.jar ${LAMBDA_TASK_ROOT}/lib/

# Set the handler information (adjust the handler class name as necessary)
CMD ["com.example.SHA256HashFunction::handleRequest"]
