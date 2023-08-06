source ./deploy_eks/config.sh

# delete deployment
# kubectl delete deployment {name-your-service}

# delete service
# kubectl delete service {name-your-service}

# kubectl apply -f ./deploy_eks/app-aws_gke-stg.yaml
kubectl create namespace {name-your-service}
kubectl create deployment {name-your-service} --image=$IMAGE_PATH
# Replace the placeholder with the actual image path
sed "s|IMAGE_PLACEHOLDER|${IMAGE_PATH}|g" ./deploy_eks/app-aws_gke-stg.yaml > ./deploy_eks/app-aws_gke-stg-modified.yaml
kubectl apply -f ./deploy_eks/app-aws_gke-stg-modified.yaml
kubectl apply -f ./deploy_eks/app-aws_gke_service-stg.yaml

# kubectl get deployments
# kubectl get services
# kubectl get all -n $NAME
# kubectl delete all --all -n {name-your-service}