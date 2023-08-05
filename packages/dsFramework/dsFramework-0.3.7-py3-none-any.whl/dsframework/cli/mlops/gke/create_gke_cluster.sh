# https://codelabs.developers.google.com/codelabs/cloud-deploy-website-on-gke#0

source ./mlops/setup_deploy_params.sh
echo Creating cluster: ${CLUSTER_NAME}

gcloud services enable container.googleapis.com
#gcloud container clusters delete $CLUSTER_NAME --zone $ZONE
gcloud container clusters create ${CLUSTER_NAME} --machine-type=n1-standard-4 --enable-autoprovisioning --enable-vertical-pod-autoscaling --enable-autoscaling --num-nodes=2 --min-nodes 1 --max-nodes 4
#gcloud container clusters create-auto ${CLUSTER_NAME} --zone $ZONE
gcloud compute instances list
gcloud container clusters list

#gcloud container clusters stop ${CLUSTER_NAME}
# gcloud container clusters describe $CLUSTER_NAME --zone $ZONE
# gcloud compute project-info describe --project project-id
#gcloud compute project-info add-metadata --metadata google-compute-default-region=europe-west1,google-compute-default-zone=europe-west1-b