variable "project" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "app_sg_id" { type = string }
variable "db_instance_class" { type = string }
variable "db_allocated_storage" { type = number }
variable "db_name" { type = string }
variable "db_username" {
  type      = string
  sensitive = true
}
variable "db_password" {
  type      = string
  sensitive = true
}

# DB is isolated in private subnets — no public access
resource "aws_security_group" "db" {
  name        = "${var.project}-${var.environment}-db-sg"
  description = "RDS — inbound only from app tier"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from app only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project}-${var.environment}-db-sg" }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-db-subnet"
  subnet_ids = var.private_subnet_ids
  tags       = { Name = "${var.project}-${var.environment}-db-subnet" }
}

resource "aws_db_instance" "postgres" {
  identifier              = "${var.project}-${var.environment}-db"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  storage_type            = "gp3"
  storage_encrypted       = true      # data-at-rest encryption — mandatory

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false       # never expose DB to the internet

  backup_retention_period = 7
  deletion_protection     = true       # prevent accidental drops in prod
  skip_final_snapshot     = false
  final_snapshot_identifier = "${var.project}-${var.environment}-final"

  tags = { Name = "${var.project}-${var.environment}-db" }
}

output "db_endpoint" { value = aws_db_instance.postgres.endpoint }
output "db_sg_id" { value = aws_security_group.db.id }
