# Infrastructure

This folder contains the Azure deployment workflow for Part IV.

## Layout

- `terraform/` - Azure VM provisioning with VNet, subnet, NSG, and public IP
- `ansible/` - playbook and inventory template for configuring the VM and running the stack

## Intended flow

1. Build and publish the Docker image from GitHub Actions.
2. Use Terraform to provision an Azure Linux VM.
3. Use Ansible to install Docker, clone the repository, and start the stack with `docker compose`.
4. Validate the deployment with `scripts/test_client.py` and Grafana/Prometheus URLs.
