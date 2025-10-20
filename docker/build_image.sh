#!/bin/bash
# Build and push Docker image to Artifact Registry

set -e

PROJECT_ID="lily-demo-ml"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/churn-pipeline/churn-trainer:latest"

echo "Building Docker image: ${IMAGE_URI}"

gcloud builds submit --config docker/cloudbuild.yaml --project ${PROJECT_ID}
