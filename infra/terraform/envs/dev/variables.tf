variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for naming and tagging resources."
  type        = string
  default     = "gcr-runner"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Resource owner tag."
  type        = string
  default     = "mykhailo"
}

variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster."
  type        = string
  default     = "1.33"
}

variable "vpc_cidr" {
  description = "CIDR block for project VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDR ranges allowed to access the public EKS API endpoint."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS worker nodes."
  type        = list(string)
  default     = ["t3.small", "t3a.small"]
}

variable "node_capacity_type" {
  description = "Capacity type for EKS managed node group: ON_DEMAND or SPOT."
  type        = string
  default     = "SPOT"
}
