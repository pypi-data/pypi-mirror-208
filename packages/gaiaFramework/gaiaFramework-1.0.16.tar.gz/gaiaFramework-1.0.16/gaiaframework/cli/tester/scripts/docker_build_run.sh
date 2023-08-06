docker stop {name-your-service}
docker rm {name-your-service}
docker build -t {name-your-service} .
# for building locally using sso .aws login folder
# docker build --build-arg AWS_CONFIG_FOLDER=/.aws --build-arg AWS_PROFILE=your_profile -t {name-your-service} .
docker run --name {name-your-service} -dp 8080:8080 {name-your-service}
#debug - docker run -it -p 8080:8080 {name-your-service}
