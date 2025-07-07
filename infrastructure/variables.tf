variable "prefix" {
  description = "Prefix for all resource names"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "pg_admin_username" {
  description = "Admin username for PostgreSQL"
  type        = string
}

variable "pg_admin_password" {
  description = "Admin password for PostgreSQL"
  type        = string
  sensitive   = true
}
