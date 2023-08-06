source ./deploy_eks/config.sh

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
aws ecr describe-repositories --repository-names $NAME || aws ecr create-repository --repository-name $NAME
#docker build -t $NAME .
docker tag $NAME:$TAG $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$NAME:$TAG
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$NAME:$TAG