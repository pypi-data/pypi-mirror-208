#!/bin/bash
# Please make sure that you are authenticated with gcloud, and all of the parameters in "setup_deploy_params.sh"
# and "deploy-gae-devland.yaml" are configured properly

# Load environment variables and configurations
source ./mlops/setup_deploy_params.sh

# Build a docker image and push it to gcr
./mlops/build_and_register_image_in_devland.sh

# Deploy the created image in GAE devland project
./mlops/gae/deploy-gae-devland.sh

gcloud builds list

#You can stream logs from the command line by running:
#> gcloud app logs tail -s $APP_NAME
#To view your application in the web browser run:
#> gcloud app browse -s $APP_NAME
