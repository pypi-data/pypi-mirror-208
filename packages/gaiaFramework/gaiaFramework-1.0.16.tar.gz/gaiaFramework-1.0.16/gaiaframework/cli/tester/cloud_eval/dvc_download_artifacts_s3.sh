#!/bin/bash


MODEL_DVC_DIR={name-your-artifacts}

#DVC_BUCKET="s3://datascience-il-dvc-storage"
DVC_BUCKET="s3://noamm-test-dvc"

export GIT_PYTHON_REFRESH=quiet
dvc init --no-scm -f
dvc remote add --default ds-ml-artifacts ${DVC_BUCKET}/${MODEL_DVC_DIR}
#dvc remote modify ds-ml-artifacts projectname gaia-stg-apps
dvc config core.analytics false

dvc pull
