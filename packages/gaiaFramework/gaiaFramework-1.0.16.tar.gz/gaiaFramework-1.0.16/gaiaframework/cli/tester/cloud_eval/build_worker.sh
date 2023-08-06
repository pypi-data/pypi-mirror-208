#!/bin/bash

export DOCKER_BUILDKIT=1

# docker build -t base:37 --file Dockerfile_base .
#WORKER_IMAGE="batch_worker:5"

if [ "$1" != "" ]; then
  PROCESSOR_IMAGE="$1"
else
  echo Please provide target image name:version
  exit 9
fi

BUILD_IMAGE_BASE="769057607614.dkr.ecr.us-east-2.amazonaws.com/base:38"
DEPLOY_IMAGE_BASE="769057607614.dkr.ecr.us-east-2.amazonaws.com/python:3.8-slim"
#DEPLOY_IMAGE_BASE="python:3.8-slim"
#docker build -t base:38 --file cloud_eval/Dockerfile_base --build-arg BUILD_IMAGE_SOURCE=${DEPLOY_IMAGE_BASE} .
docker build -t ${PROCESSOR_IMAGE} --file cloud_eval/Dockerfile_batch_processor --build-arg BUILD_IMAGE_SOURCE=${BUILD_IMAGE_BASE} --build-arg DEPLOY_IMAGE_SOURCE=${DEPLOY_IMAGE_BASE} .