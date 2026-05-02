# Terraform for AWS EC2

This directory provisions AWS infrastructure for cloud deployment.

Provisioned resources:

- Ubuntu EC2 instance
- Security group with inbound ports: 22, 80, 8000, 3000, 9090, 3100
- Public IP / DNS outputs

Required inputs (see `terraform.tfvars.example`):

- `aws_region`
- `instance_name`
- `instance_type`
- `key_name`
- `allowed_cidr_blocks`

Usage:

1. `terraform init`
2. `terraform plan -var-file=terraform.tfvars`
3. `terraform apply -var-file=terraform.tfvars`

Key outputs:

- `public_ip`
- `public_dns`
- `ssh_command`
- `application_url`
