ECR_REPO_NAME={name-your-artifacts}

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${ECR_REPO_NAME}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${ECR_REPO_NAME}" > /dev/null
fi