output "aws_account_id" {
  description = "Current AWS account ID used by Terraform."
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Current AWS region."
  value       = data.aws_region.current.region
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

output "vpc_id" {
  description = "VPC ID."
  value       = module.vpc.vpc_id
}

output "public_subnets" {
  description = "Public subnet IDs."
  value       = module.vpc.public_subnets
}

output "eks_cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint."
  value       = module.eks.cluster_endpoint
}

output "update_kubeconfig_command" {
  description = "Command to configure kubectl for this EKS cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
