output "repository_urls" {
  description = "Map of image name to ECR repository URL."
  value = {
    for name, repository in aws_ecr_repository.this :
    name => repository.repository_url
  }
}

output "repository_names" {
  description = "Map of image name to ECR repository name."
  value = {
    for name, repository in aws_ecr_repository.this :
    name => repository.name
  }
}
