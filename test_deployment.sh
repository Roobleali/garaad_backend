#!/bin/bash

echo "Building Docker image..."
docker build -t garaad-backend-test .

echo "Starting container..."
docker run --name garaad-test -d -p 8080:8080 --env-file .env garaad-backend-test

echo "Waiting for container to start..."
sleep 10

echo "Testing health check endpoint..."
curl -v http://localhost:8080/health/

echo "Checking container logs..."
docker logs garaad-test

echo "Cleaning up..."
docker stop garaad-test
docker rm garaad-test 