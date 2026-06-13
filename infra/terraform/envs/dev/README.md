# Dev Terraform Environment

This directory contains Terraform configuration for the dev environment.

## Current step

This step does not create paid AWS resources yet.

It only validates Terraform setup and reads:

- current AWS account ID
- current AWS region

## Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
