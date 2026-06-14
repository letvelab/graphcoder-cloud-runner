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

## EKS cost warning

EKS is not free. The cluster control plane has an hourly cost, and worker nodes are regular EC2 instances.

For this dev project:

- use only 1 managed node
- avoid NAT Gateway
- use SPOT capacity by default
- destroy the cluster after testing

## EKS workflow

```bash
make tf-init-upgrade
make tf-fmt
make tf-validate
make tf-plan
make tf-apply
make eks-update-kubeconfig
make eks-nodes
```

Destroy after testing:

make tf-destroy


---

# 9. Важливо: обмеж доступ до EKS API своїм IP

У `terraform.tfvars` краще постав не:

```hcl
cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]
```

