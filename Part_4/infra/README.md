# Infrastructure (Part 4 Deployment)

This directory contains the full deployment workflow for running the Pipeline Project on AWS EC2 using Docker, Ansible, and Terraform.

---

## Overview

The project is deployed as a containerized application with a monitoring stack:

- **Application (FastAPI)** – ML inference service
- **Grafana** – visualization dashboard
- **Prometheus** – metrics collection
- **Loki** – log aggregation

Deployment is automated using:

- **Terraform** → provisions EC2 instance
- **Ansible** → installs Docker and runs services
- **Docker Compose** → orchestrates containers

---

## Project Structure

- `terraform/` – EC2 provisioning (instance + security group + outputs)
- `ansible/` – playbook and inventory for deployment
- `docker-compose.prod.yml` – defines application and monitoring stack

---

## Deployment Flow

1. Build and push Docker image (via GitHub Actions or manually)
2. Provision EC2 instance using Terraform
3. Run Ansible playbook to:
   - install Docker
   - pull the image
   - start services using Docker Compose
4. Access services via public IP

---

## Running Deployment (Live Demo)

All services are publicly доступні:

- Application UI:  
  http://16.171.78.151:8000/

- Health check:  
  http://16.171.78.151:8000/health

- Metrics:  
  http://16.171.78.151:8000/metrics

- Grafana:  
  http://16.171.78.151:3000  
  Username: admin  
  Password: MyStrongPass_2026!

- Prometheus:  
  http://16.171.78.151:9090/

- Loki (health check):  
  http://16.171.78.151:3100/ready

---

## Result

The deployment results in a fully working cloud-based system with:

- ML inference API
- Monitoring (metrics + logs)
- Visualization via Grafana

This completes Part 4 (Infrastructure & Deployment).


