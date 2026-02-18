#!/bin/bash

IMAGE_NAME=europe-west3-docker.pkg.dev/stable-plasma-427409-e7/avaluma-public/avaluma-livekit-runtime-x68-cu12
COMMIT_ID=$(git log -1 --format=%h)

# Build the Docker image
docker build -t $IMAGE_NAME . --no-cache
docker push $IMAGE_NAME:latest

docker tag $IMAGE_NAME $IMAGE_NAME:$COMMIT_ID
docker push $IMAGE_NAME:$COMMIT_ID
