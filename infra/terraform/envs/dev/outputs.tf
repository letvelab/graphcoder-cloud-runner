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
