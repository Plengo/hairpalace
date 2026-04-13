output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "app_server_public_ip" {
  description = "Public IP of the application server"
  value       = module.compute.public_ip
}

output "db_endpoint" {
  description = "RDS endpoint (private)"
  value       = module.database.db_endpoint
  sensitive   = true
}
