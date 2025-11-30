# GitHub Actions IAM Permissions Summary

## Service Account
- **Email**: `github-actions@lily-demo-ml.iam.gserviceaccount.com`
- **Purpose**: Execute CI/CD workflows from GitHub Actions

## Required APIs
```terraform
- iam.googleapis.com                  # Identity and Access Management
- iamcredentials.googleapis.com       # Workload Identity Federation
- sts.googleapis.com                  # Security Token Service (for OIDC)
- cloudbuild.googleapis.com           # Build Docker images
- artifactregistry.googleapis.com     # Push/pull container images
- storage.googleapis.com              # Access Cloud Storage buckets
- aiplatform.googleapis.com           # Deploy to Vertex AI
```

## IAM Roles Granted

### 1. `roles/aiplatform.user`
**Purpose**: Deploy ML pipelines to Vertex AI
**Allows**:
- Submit pipeline jobs
- Create pipeline runs
- View pipeline status

**Used in workflow**: `make deploy` step

---

### 2. `roles/artifactregistry.writer`
**Purpose**: Push Docker images to Artifact Registry
**Allows**:
- Push container images
- Tag images
- Delete old images

**Used in workflow**: `make build` → Cloud Build pushes image

---

### 3. `roles/storage.objectAdmin`
**Purpose**: Manage objects in GCS buckets (pipeline artifacts)
**Allows**:
- Upload pipeline artifacts
- Download training data
- Store model outputs

**Used in workflow**: Vertex AI pipeline stores outputs

---

### 4. `roles/storage.admin`
**Purpose**: Full access to Cloud Storage (needed for Cloud Build bucket)
**Allows**:
- Access `lily-demo-ml_cloudbuild` bucket
- Create/delete buckets (if needed)
- Manage bucket permissions

**Why needed**: Cloud Build requires access to its staging bucket

---

### 5. `roles/cloudbuild.builds.builder`
**Purpose**: Trigger and manage Cloud Build jobs
**Allows**:
- Submit build requests
- View build logs
- Cancel builds

**Used in workflow**: `make build` → `gcloud builds submit`

---

### 6. `roles/serviceusage.serviceUsageConsumer`
**Purpose**: Use Google Cloud services
**Allows**:
- Enable/disable APIs
- Check service quotas
- View service status

**Why needed**: Cloud Build checks if services are enabled

---

### 7. `roles/iam.serviceAccountUser`
**Purpose**: Act as other service accounts
**Allows**:
- Impersonate Cloud Build service account
- Impersonate Compute Engine default service account

**Why needed**: Cloud Build runs as a service account, GitHub Actions needs permission to trigger it

---

## Workload Identity Federation

Instead of using service account keys (which can be leaked), we use **Workload Identity Federation**:

```yaml
# GitHub Actions authenticates directly to GCP
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```
