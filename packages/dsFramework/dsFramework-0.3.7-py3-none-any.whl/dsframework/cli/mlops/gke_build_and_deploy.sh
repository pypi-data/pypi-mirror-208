#!/bin/bash
source ./mlops/setup_deploy_params.sh

./mlops/build_and_register_image_in_devland.sh

#to be run only once
./mlops/gke/create_gke_cluster.sh

# every new build
./mlops/gke/deploy_app_to_gke_devland.sh

# faster only update app
# ./devland/gke/deploy_update_app_to_gke_devland.sh

kubectl get svc ${SERVICE_NAME} -o yaml
