variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "af-south-1"
}

variable "environment" {
  description = "Deployment environment (staging | production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be 'staging' or 'production'."
  }
}

variable "project" {
  description = "Project name used as a naming prefix"
  type        = string
  default     = "strands"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs (one per AZ)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs (one per AZ)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "ec2_instance_type" {
  description = "EC2 instance type for the application server"
  type        = string
  default     = "t3.small"
}

variable "ec2_ami_id" {
  description = "AMI ID for the application server (Ubuntu 24.04 LTS)"
  type        = string
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair for SSH access"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "DB allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "strands"
}

variable "db_username" {
  description = "PostgreSQL master username — inject from secrets manager"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL master password — inject from secrets manager"
  type        = string
  sensitive   = true
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into the server (your static IP)"
  type        = string
}
