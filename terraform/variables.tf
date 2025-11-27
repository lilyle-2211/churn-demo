variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "lily-demo-ml"
}

variable "project_number" {
  description = "GCP Project Number"
  type        = string
  default     = "167672209455"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "user_email" {
  description = "User email for IAM permissions"
  type        = string
  default     = "lelisa.dk@gmail.com"
}
