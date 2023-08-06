source ./deploy_eks/config.sh
# aws eks list-clusters --region us-east-1
#eksctl create cluster --name $CLUSTER_NAME --version 1.26 --node-type t2.micro --nodes 3 --region $REGION_CLUSTER --profile gaia_admin
#eksctl delete cluster --name=gaia
eksctl create cluster --name $CLUSTER_NAME --version 1.25 --node-type t2.micro --nodes 2
aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION
# verify
# kubectl config current-context

# aws iam create-role --role-name eksClusterRole --assume-role-policy-document file://"/Dev2016/eks-test/deploy_eks/cluster-trust-policy.json"

# aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy --role-name eksClusterRole