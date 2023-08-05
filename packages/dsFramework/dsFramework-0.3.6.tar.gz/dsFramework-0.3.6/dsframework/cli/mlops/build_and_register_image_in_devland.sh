#!/bin/bash
source ./mlops/setup_deploy_params.sh

echo Building and registering image: "${IMAGE_NAME}"

# git status  > gitlog.txt
# git log --graph --decorate --all --stat --pretty=full >> gitlog.txt

docker build -f Dockerfile -t "${IMAGE_NAME}" .
gcloud config set project "$PROJECT_ID"
gcloud auth configure-docker gcr.io
docker push "${IMAGE_NAME}"
