data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

module "ecr" {
  source = "../../modules/ecr"

  name_prefix = local.name_prefix

  image_names = [
    "api",
    "worker",
  ]

  tags = local.common_tags
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "${local.name_prefix}-vpc"
  cidr = var.vpc_cidr

  azs = slice(
    data.aws_availability_zones.available.names,
    0,
    local.az_count
  )

  public_subnets = [
    "10.42.1.0/24",
    "10.42.2.0/24",
  ]

  private_subnets = []

  enable_nat_gateway      = false
  map_public_ip_on_launch = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  tags = local.common_tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "${local.name_prefix}-eks"
  kubernetes_version = var.eks_cluster_version

  endpoint_public_access       = true
  endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs

  endpoint_private_access = false

  enable_cluster_creator_admin_permissions = true

  authentication_mode = "API_AND_CONFIG_MAP"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni = {
      before_compute = true
    }

  }

  eks_managed_node_groups = {
    default = {
      name = "${local.name_prefix}-default"

      min_size     = 1
      max_size     = 1
      desired_size = 1

      capacity_type  = var.node_capacity_type
      instance_types = var.node_instance_types

      ami_type = "AL2023_x86_64_STANDARD"

      disk_size = 20

      labels = {
        workload = "general"
      }
    }
  }

  tags = local.common_tags
}
