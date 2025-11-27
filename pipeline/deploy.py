#!/usr/bin/env python3
"""
Deploy churn prediction training job to Vertex AI.
"""
import argparse

from google.cloud import aiplatform
from kfp import compiler, dsl
from kfp.dsl import Metrics, Model, Output, component

# Use custom container image with all modules pre-installed
CONTAINER_IMAGE = "us-central1-docker.pkg.dev/lily-demo-ml/churn-pipeline/churn-trainer:latest"


@component(base_image=CONTAINER_IMAGE)
def train_churn_model(
    project_id: str,
    model_output: Output[Model],
    metrics_output: Output[Metrics],
):
    import sys

    sys.path.append("/app")
    from trainer.main import main

    # Run the pipeline
    model, metrics = main()

    # Log metrics
    print(f"Test PR-AUC: {metrics['pr_auc_test']:.4f}")
    print(f"Test ROC-AUC: {metrics['roc_auc_test']:.4f}")

    # Record metrics for Vertex AI
    metrics_output.log_metric("pr_auc_test", metrics["pr_auc_test"])
    metrics_output.log_metric("roc_auc_test", metrics["roc_auc_test"])


@dsl.pipeline(name="churn-prediction-pipeline")
def churn_pipeline(project_id: str = "lily-demo-ml"):
    """Churn prediction pipeline."""
    train_task = train_churn_model(project_id=project_id)
    train_task.set_cpu_limit("4")
    train_task.set_memory_limit("16G")


def deploy(project_id: str, region: str = "us-central1", bucket: str = None):
    """Compile and run pipeline."""
    # Compile
    compiler.Compiler().compile(
        pipeline_func=churn_pipeline, package_path="churn_demo_pipeline.json"
    )
    print("Pipeline compiled to churn_demo_pipeline.json")

    # Deploy
    if bucket is None:
        bucket = f"{project_id}-pipeline"

    aiplatform.init(project=project_id, location=region)

    job = aiplatform.PipelineJob(
        display_name="churn-prediction",
        template_path="churn_demo_pipeline.json",
        pipeline_root=f"gs://{bucket}/churn",
        parameter_values={"project_id": project_id},
        enable_caching=False,
    )

    job.submit(service_account=None)
    print(f"Pipeline submitted: {job.resource_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--region", default="us-central1")
    parser.add_argument("--bucket")
    args = parser.parse_args()

    deploy(args.project_id, args.region, args.bucket)
