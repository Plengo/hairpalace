module "networking" {
  source = "./modules/networking"

  project              = var.project
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  aws_region           = var.aws_region
}

module "compute" {
  source = "./modules/compute"

  project          = var.project
  environment      = var.environment
  vpc_id           = module.networking.vpc_id
  public_subnet_id = module.networking.public_subnet_ids[0]
  instance_type    = var.ec2_instance_type
  ami_id           = var.ec2_ami_id
  key_pair_name    = var.key_pair_name
  allowed_ssh_cidr = var.allowed_ssh_cidr
  db_sg_id         = module.database.db_sg_id
}

module "database" {
  source = "./modules/database"

  project              = var.project
  environment          = var.environment
  vpc_id               = module.networking.vpc_id
  private_subnet_ids   = module.networking.private_subnet_ids
  app_sg_id            = module.compute.app_sg_id
  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
}
