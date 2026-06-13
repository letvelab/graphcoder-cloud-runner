variable "name_prefix" {
  description = "Prefix used for ECR repository names."
  type        = string
}

variable "image_names" {
  description = "List of Docker image repositories to create."
  type        = set(string)
}

variable "tags" {
  description = "Common tags applied to ECR repositories."
  type        = map(string)
  default     = {}
}
