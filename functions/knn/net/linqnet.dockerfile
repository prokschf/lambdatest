# Define the base image for the build stage from the .NET SDK
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-env
WORKDIR /app

# Copy csproj and restore as distinct layers
COPY functions/knn/net/*.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY functions/knn/net/ ./
RUN dotnet publish -c Release -o out -r linux-x64 --self-contained false

# Define the base image for the final stage from AWS Lambda runtime
FROM public.ecr.aws/lambda/dotnet:6
WORKDIR /var/task
COPY --from=build-env /app/out .

# Set the handler information directly via CMD
CMD ["linqnet::KnnLambdaFunction.Function::FunctionHandler"]
