# https://codelabs.developers.google.com/codelabs/cloud-deploy-website-on-gke#4
source ./mlops/setup_deploy_params.sh

gcloud container clusters get-credentials ${CLUSTER_NAME}
kubectl create deployment ${APP_NAME} --image=${IMAGE_NAME}
kubectl scale deployment ${APP_NAME} --replicas=1
kubectl autoscale deployment ${APP_NAME} --cpu-percent=80 --min=1 --max=20
#kubectl edit hpa ${APP_NAME}
kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME}
kubectl expose deployment ${APP_NAME} --type=LoadBalancer --name=${SERVICE_NAME} --port=80 --target-port=8080

#debug
kubectl get pods
kubectl get svc
gcloud builds list
gcloud container images list
kubectl describe hpa ${APP_NAME}
kubectl describe replicasets
kubectl describe pods
kubectl describe svc
#kubectl logs deployment-name-here
#gcloud container clusters delete $CLUSTER_NAME
#

kubectl get pods --all-namespaces -o jsonpath="{.items[*].spec.containers[*].image}" |\
tr -s '[[:space:]]' '\n' |\
sort |\
uniq -c
