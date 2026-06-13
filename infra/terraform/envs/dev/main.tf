data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

module "ecr" {
  source = "../../modules/ecr"

  name_prefix = local.name_prefix

  image_names = [
    "api",
    "worker",
  ]

  tags = local.common_tags
}
