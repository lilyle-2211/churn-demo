output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.churn_pipeline.repository_id}"
}

output "bucket_name" {
  description = "GCS bucket name for pipeline artifacts"
  value       = google_storage_bucket.pipeline_bucket.name
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}
