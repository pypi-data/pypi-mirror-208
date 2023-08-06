#export GOOGLE_APPLICATION_CREDENTIALS=/app/gcloud_credentials.json
export GIT_PYTHON_REFRESH=quiet
export GOOGLE_CLOUD_PROJECT='gaia-stg-apps'

dvc init --no-scm
dvc remote add --default ds-ml-artifacts s3://gaia-stg-apps-ds-ml-artifacts/{name-your-artifacts}
#dvc remote modify ds-ml-artifacts projectname gaia-stg-apps
dvc config core.analytics false

dvc status
dvc fetch
dvc pull
#python script_load_model.py
