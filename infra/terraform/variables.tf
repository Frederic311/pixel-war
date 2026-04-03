variable "cluster_name" {
  description = "Name of the local kind cluster"
  type        = string
  default     = "pixelwar"
}

variable "kind_config_path" {
  description = "Path to kind cluster config"
  type        = string
  default     = "../../k8s/kind-config.yaml"
}

variable "deploy_manifests" {
  description = "Apply Kubernetes manifests from Terraform"
  type        = bool
  default     = true
}

variable "redis_password" {
  description = "Redis password used for Kubernetes Secret"
  type        = string
  sensitive   = true
}
