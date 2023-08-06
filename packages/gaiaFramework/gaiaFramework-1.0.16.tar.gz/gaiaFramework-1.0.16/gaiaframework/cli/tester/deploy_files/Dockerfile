#--------- BEGIN DEVELOPER MODIFY FOR YOUR BUILD PROCESS ---------#
#Do not change the "AS build_image" part on the FROM
FROM python:3.9-slim AS build_image
#FROM docker.io/library/model_artifcats AS build_image
#Do not remove the BUILD_ACTION ARG, you can change its default value. You must use it in your build command in the RUN section for Jenkins to deploy your artifact.

ARG PIP_ACTION=install
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_PASSWORD

ENV GIT_PYTHON_REFRESH=quiet
ENV ARTIFACTORY_USR=$ARTIFACTORY_USERNAME
ENV ARTIFACTORY_PSW=$ARTIFACTORY_PASSWORD
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG AWS_CONFIG_FOLDER
ARG AWS_PROFILE

#ENV TRANSFORMERS_CACHE='/app/.transformers_cache'

WORKDIR /app

RUN apt-get -o Acquire::Max-FutureTime=86400 update
RUN apt-get install -y --no-install-recommends build-essential gcc
RUN pip install --upgrade pip
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

#ADD serving/ /app/serving/
ADD requirements_docker.txt /app/requirements_docker.txt
RUN pip ${PIP_ACTION} --no-cache-dir -r /app/requirements_docker.txt


# Add the application source code.

ADD ./pipeline /app/pipeline
ADD ./server /app/server
ADD ./config /app/config
ADD ./tester /app/tester
ADD ./scripts /app/scripts
ADD ./pipeline_test.py /app
ADD ./gunicorn.conf.py /app

# Download artifacts
#ADD ./gcloud_credentials.json /app

# adding AWS_CONFIG_FOLDER if passed using docker build --build-arg AWS_SSO_CREDS=
ADD $AWS_CONFIG_FOLDER /app/.aws
ENV AWS_CONFIG_FILE=/app/.aws/config
#ENV AWS_SSO_START_URL=https://d-906791fee0.awsapps.com/start
#ENV AWS_DEFAULT_REGION=us-east-1
#ENV AWS_PROFILE $AWS_PROFILE

# adding GOOGLE_APPLICATION_CREDENTIALS if passed using docker build --build-arg GOOGLE_APPLICATION_CREDENTIALS=
ADD $GOOGLE_APPLICATION_CREDENTIALS $GOOGLE_APPLICATION_CREDENTIALS

# ingore warning since downloading a bert pretrained model generates a warning
#RUN python -W ignore /app/app/download_artifacts.py
RUN groupadd -g 999 appuser && \
        useradd -r -d /app -u 999 -g appuser appuser
RUN chown -R appuser:appuser /app
#RUN chown -R appuser:appuser /opt/venv
#RUN chown -R appuser:appuser /bin/sh
#
USER appuser

RUN ["chmod", "+x", "/app/scripts/dvc_download_artifacts.sh"]
RUN ./scripts/dvc_download_artifacts.sh

RUN python /app/pipeline_test.py

#--------- END DEVELOPER MODIFY FOR YOUR BUILD PROCESS ---------#

#--------- BEGIN DEVELOPER MODIFY FOR YOUR DEPLOYMENT APP ---------#
#Do not change the "AS deploy_image" part of the FROM
FROM python:3.9-slim AS deploy_image

MAINTAINER GAIA

WORKDIR /app

EXPOSE 8080/tcp
#Do not change "--from=build_image" it applies logic we us for our builds. sonar_scan will always have the same files as build_image
ENV PATH="/opt/venv/bin:$PATH"
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2
ENV PYTORCH_INTEROP_THREADS=8
ENV ATEN_THREADING=TBB
RUN groupadd -g 999 appuser && \
        useradd -r -d /app -u 999 -g appuser appuser

COPY --from=build_image --chown=appuser:appuser /opt/venv /opt/venv
COPY --from=build_image --chown=appuser:appuser /app /app


#RUN chown -R appuser:appuser /app
#RUN chown -R appuser:appuser /opt/venv

#USER 1001
USER appuser

ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py", "server.main:app"]
#CMD ["gunicorn", "-k uvicorn.workers.UvicornWorker", "--log-file=-", "--graceful-timeout", "240", "--timeout", "120", "--bind=0.0.0.0:8080", "--workers=3", "server.main:app"]
#--------- END DEVELOPER MODIFY FOR YOUR DEPLOYMENT APP ---------#
