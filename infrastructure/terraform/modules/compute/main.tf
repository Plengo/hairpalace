variable "project" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_id" { type = string }
variable "instance_type" { type = string }
variable "ami_id" { type = string }
variable "key_pair_name" { type = string }
variable "allowed_ssh_cidr" { type = string }
variable "db_sg_id" { type = string }

# Separate SG: only inbound 80/443 from internet + SSH from operator IP
resource "aws_security_group" "app" {
  name        = "${var.project}-${var.environment}-app-sg"
  description = "Application server — HTTP/HTTPS public + SSH restricted"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH — operator only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project}-${var.environment}-app-sg" }
}

resource "aws_instance" "app" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  key_name                    = var.key_pair_name
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true

  # Docker + Docker Compose bootstrapped on first boot
  user_data = base64encode(<<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
    curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
  EOF
  )

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true   # data-at-rest encryption
    delete_on_termination = true
  }

  tags = { Name = "${var.project}-${var.environment}-app" }
}

output "public_ip" { value = aws_instance.app.public_ip }
output "app_sg_id" { value = aws_security_group.app.id }
