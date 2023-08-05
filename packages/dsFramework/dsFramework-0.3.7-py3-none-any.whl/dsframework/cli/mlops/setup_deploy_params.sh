### Basic configuration
export VERSION=1.11.15
export PROJECT_ID=zi-devland-israel-ds
export ZONE=us-east1-b
export REGION=us-east1
export APP_NAME={name-your-service}

### Create advanced configuration
export DOCKER_BUILDKIT=1
export SERVICE_NAME=${APP_NAME}-service
export CLUSTER_NAME=${APP_NAME}-cluster
export IMAGE_NAME=gcr.io/${PROJECT_ID}/${APP_NAME}:${VERSION}

### Use configuration for environment setup
echo Service: ${SERVICE_NAME} Project: ${PROJECT_ID} Image: ${IMAGE_NAME} on ${CLUSTER_NAME} at ${ZONE}
gcloud config set project $PROJECT_ID
gcloud config set compute/zone $ZONE
