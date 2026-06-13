output "aws_account_id" {
  description = "Current AWS account ID used by Terraform."
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Current AWS region."
  value       = data.aws_region.current.name
}

output "name_prefix" {
  description = "Name prefix that will be used for resources."
  value       = local.name_prefix
}

output "ecr_repository_urls" {
  description = "ECR repository URLs for Docker images."
  value       = module.ecr.repository_urls
}

output "ecr_repository_names" {
  description = "ECR repository names."
  value       = module.ecr.repository_names
}
