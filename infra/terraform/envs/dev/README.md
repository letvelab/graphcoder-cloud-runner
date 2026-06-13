# Dev Terraform Environment

This directory contains Terraform configuration for the dev environment.

## Current resources

This environment creates:

- ECR repository for API image
- ECR repository for worker image
- ECR lifecycle policies for cleanup

## Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
