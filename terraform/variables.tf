variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "escalas"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "escalas-app"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "Fargate CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "Fargate memory in MB (512, 1024, 2048, 3072, 4096, 5120, 6144, 7168, 8192)"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

# Database Configuration (SQLite via EFS)
variable "database_name" {
  description = "SQLite database filename"
  type        = string
  default     = "escalas.db"
}

variable "efs_throughput_mode" {
  description = "EFS throughput mode (bursting or provisioned)"
  type        = string
  default     = "bursting"
  validation {
    condition     = contains(["bursting", "provisioned"], var.efs_throughput_mode)
    error_message = "Throughput mode must be bursting or provisioned."
  }
}

# Network Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# Backup Configuration
variable "enable_efs_backup" {
  description = "Enable automated backups via AWS Backup"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
  validation {
    condition     = var.backup_retention_days > 0 && var.backup_retention_days <= 35
    error_message = "Retention must be between 1 and 35 days."
  }
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
