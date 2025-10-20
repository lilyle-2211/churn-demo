# Churn Prediction Demo

This project demonstrates a production-ready pipeline for churn prediction using Google Cloud Platform (Vertex AI, BigQuery, Artifact Registry, GCS).

## Features
- Data loading and preprocessing from BigQuery
- Time-ordered train/val/test split
- Hyperparameter tuning with Optuna
- Model training with XGBoost
- Evaluation metrics: PR-AUC, ROC-AUC, Precision@k
- Terraform for infras
- Makefile automation

## Directory Structure
```
churn-demo/
├── README.md
├── pyproject.toml
├── Makefile
├── docker/
│   ├── Dockerfile
│   ├── build_image.sh
│   └── cloudbuild.yaml
├── eda/
│   ├── README.md
│
├── pipeline/
│   ├── deploy.py
│
├── sql/
│   └── input.sql
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│
├── tests/
│   ├── test_data_preprocessing.py
│   ├── test_model_training.py
│
└── trainer/
   ├── data_preprocessing.py
   ├── data_loader.py
   ├── main.py
   ├── model_training.py
   ├── model_evaluation.py
   └── config.yaml
```



## Usage

- Run the pipeline locally: `make run`
- Run tests: `make test`
- Build Docker image: `make build`
- Deploy pipeline: `make deploy`
- Provision infrastructure: `make terraform`




## eda
- Example notebooks for model evaluation and metrics are provided.
