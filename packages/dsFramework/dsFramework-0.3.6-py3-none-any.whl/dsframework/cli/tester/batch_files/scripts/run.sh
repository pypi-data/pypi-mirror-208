#!/bin/bash
# export GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
gcloud config set project dozi-data-science-research-1

# Replace "primary" with desired workflow name throughout this script
bash ./batch_files/scripts/build.sh primary
dsf-cli upload-batch-files primary all
# python ./batch_files/workflow/auto_scaling_policy.py
dsf-cli workflow-template primary create
dsf-cli dag primary create
# dsf-cli dag primary import
# dsf-cli workflow-template primary instantiate

gcloud config set project dozi-stg-ds-apps-1
