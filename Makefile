.PHONY: help build deploy run terraform lint-terraform clean

# Project configuration
PROJECT_ID := lily-demo-ml
REGION := us-central1
IMAGE_URI := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/churn-pipeline/churn-trainer:latest

help:
	@echo "Available commands:"
	@echo "  make build           - Build and push Docker image to Artifact Registry"
	@echo "  make deploy          - Deploy training job to Vertex AI"
	@echo "  make run             - Run training locally with uv"
	@echo "  make terraform       - Apply Terraform infrastructure"
	@echo "  make lint-terraform  - Lint Terraform code with TFLint"

build:
	@echo "Building Docker image: $(IMAGE_URI)"
	gcloud builds submit --config docker/cloudbuild.yaml --project $(PROJECT_ID)
	@echo "Image built and pushed"

deploy:
	@echo "Deploying to Vertex AI..."
	uv run python pipeline/deploy.py --project-id=$(PROJECT_ID) --region=$(REGION)
	@echo "Pipeline deployed to Vertex AI"

run:
	@echo "Running training locally..."
	cd trainer && uv run python main.py

terraform:
	@echo "Applying Terraform configuration..."
	cd terraform && terraform init && terraform apply
	@echo "Infrastructure deployed"

lint-terraform:
	@echo "Linting Terraform code..."
	cd terraform && tflint --init && tflint
	@echo "Terraform linting complete"
