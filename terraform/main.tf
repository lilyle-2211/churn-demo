terraform {
  required_version = ">= 1.0"

  # TODO: Enable GCS backend once billing issue is resolved
  # backend "gcs" {
  #   bucket = "lily-demo-ml-tfstate"
  #   prefix = "terraform/state"
  # }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# Create Artifact Registry repository
resource "google_artifact_registry_repository" "churn_pipeline" {
  location      = var.region
  repository_id = "churn-pipeline"
  format        = "DOCKER"
  description   = "Docker repository for churn prediction pipeline"

  depends_on = [google_project_service.required_apis]
}

# Create GCS bucket for pipeline artifacts
resource "google_storage_bucket" "pipeline_bucket" {
  name     = "${var.project_id}-pipeline"
  location = "US" # Multi-region bucket

  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.required_apis]
}

# Grant user permissions
resource "google_project_iam_member" "user_aiplatform_admin" {
  project = var.project_id
  role    = "roles/aiplatform.admin"
  member  = "user:${var.user_email}"
}

resource "google_project_iam_member" "user_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "user:${var.user_email}"
}

resource "google_project_iam_member" "user_cloudbuild_editor" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "user:${var.user_email}"
}

resource "google_project_iam_member" "user_artifact_registry_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "user:${var.user_email}"
}

resource "google_project_iam_member" "user_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "user:${var.user_email}"
}

# Grant Compute Engine service account permissions
resource "google_project_iam_member" "compute_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_bigquery_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant Cloud Build service account permissions
resource "google_project_iam_member" "cloudbuild_logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Grant AI Platform service account permissions
resource "google_project_iam_member" "aiplatform_sa_bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "aiplatform_sa_bigquery_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "aiplatform_sa_storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

# ============================================================================
# GitHub Actions - Workload Identity Federation
# ============================================================================

module "github_actions" {
  source = "./modules/github-actions"

  project_id  = var.project_id
  github_org  = var.github_org
  github_repo = var.github_repo

  project_roles = [
    "roles/aiplatform.user",
    "roles/artifactregistry.writer",
    "roles/storage.objectAdmin",
    "roles/storage.admin",
    "roles/cloudbuild.builds.builder",
    "roles/serviceusage.serviceUsageConsumer",
    "roles/iam.serviceAccountUser",
  ]

  depends_on = [google_project_service.required_apis]
}
