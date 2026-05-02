variable "aws_region" {
  type        = string
  description = "AWS region where resources are created"
  default     = "eu-north-1"
}

variable "instance_name" {
  type        = string
  description = "EC2 instance name"
  default     = "insa4"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "key_name" {
  type        = string
  description = "Existing AWS key pair name"
  default     = "telco-key"
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to access SSH and app ports"
  default     = ["0.0.0.0/0"]
}

variable "root_volume_size_gb" {
  type        = number
  description = "Root EBS volume size in GB"
  default     = 20
}

variable "environment" {
  type        = string
  description = "Environment tag value"
  default     = "prod"
}
