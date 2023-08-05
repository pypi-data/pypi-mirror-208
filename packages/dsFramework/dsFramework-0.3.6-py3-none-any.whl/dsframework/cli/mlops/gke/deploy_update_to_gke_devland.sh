source ./mlops/setup_deploy_params.sh
gcloud container clusters get-credentials ${CLUSTER_NAME}
kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME}

kubectl get pods --all-namespaces -o jsonpath="{.items[*].spec.containers[*].image}" |\
tr -s '[[:space:]]' '\n' |\
sort |\
uniq -c


#Debug using dashboard
# > kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.3.1/aio/deploy/recommended.yaml
# > kubectl proxy
# open browser at: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
# guide at: https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/
