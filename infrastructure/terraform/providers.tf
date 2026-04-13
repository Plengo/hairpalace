terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state — swap bucket/table for your own
  backend "s3" {
    bucket         = "strands-terraform-state"
    key            = "strands/terraform.tfstate"
    region         = "af-south-1"
    dynamodb_table = "strands-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "STRANDS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
