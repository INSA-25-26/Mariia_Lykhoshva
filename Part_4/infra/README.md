# Infrastructure

This folder contains the AWS EC2 deployment workflow for Part IV.

## Layout

- `terraform/` - EC2 provisioning with security group and public IP outputs
- `ansible/` - playbook and inventory templates for Docker-based deployment

## Intended flow

1. Build and publish the Docker image from GitHub Actions on push to `main`.
2. Use Terraform to provision an Ubuntu EC2 instance.
3. Use Ansible to install Docker, pull the published image, and run the app + monitoring stack via Compose.
4. Validate deployment:
	- App: `http://<public-ip>:8000/health`
	- App (port 80): `http://<public-ip>/health`
	- Grafana: `http://<public-ip>:3000`
	- Prometheus: `http://<public-ip>:9090`
