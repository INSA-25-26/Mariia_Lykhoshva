# End-to-End Deployment Guide

This document provides strict, production-ready deployment instructions for the pipeline project on AWS EC2.

---

## Architecture Overview

- **CI/CD**: GitHub Actions (on push to `main`)
- **Container Registry**: Docker Hub
- **Infrastructure**: AWS EC2 (Ubuntu 24.04 LTS)
- **IaC**: Terraform (provisions EC2 + security group)
- **Configuration Management**: Ansible (deploys services)
- **Orchestration**: Docker Compose (app + Prometheus + Grafana + Loki + Promtail)

---

## Prerequisites

### Local Machine

- `terraform` (>= 1.6.0)
- `ansible` (>= 2.12)
- `awscli` configured with AWS credentials
- SSH private key: `telco-key.pem` (or `~/.ssh/telco-key.pem`)
- Docker (for testing locally)

### GitHub Repository

Secrets configured in GitHub Actions:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

How to add them:

1. Open your GitHub repository.
2. Go to `Settings` → `Secrets and variables` → `Actions`.
3. Click `New repository secret`.
4. Add `DOCKERHUB_USERNAME` with your Docker Hub username.
5. Add `DOCKERHUB_TOKEN` with your Docker Hub access token.
6. Save both secrets.

### Docker Hub

- Create a Docker Hub repository named `pipeline-project` under your Docker Hub namespace.
- Create a Docker Hub access token in Account Settings → Security → New Access Token.
- Add the Docker Hub username and access token to GitHub repository secrets.
- The CI workflow publishes the image as `docker.io/<DOCKERHUB_USERNAME>/pipeline-project:latest`.
- If you want a different image name, update the `IMAGE_NAME` value in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

How to create the Docker Hub repository:

1. Open [hub.docker.com](https://hub.docker.com/) and sign in.
2. Go to `Repositories`.
3. Click `Create repository`.
4. Set the name to `pipeline-project`.
5. Keep it public unless you specifically want a private image.
6. Save the repository.

How to create the access token:

1. Open Docker Hub account settings.
2. Go to `Security`.
3. Click `New Access Token`.
4. Name the token, create it, and copy the value once.
5. Paste that token into the GitHub secret `DOCKERHUB_TOKEN`.

### AWS Account

- Active subscription
- EC2 VPC access
- IAM permissions for `ec2:*`
- Key pair `telco-key` already exists

---

## Step 1: Build and Publish Docker Image

### 1.1 Trigger CI/CD

Push code to `main` branch:

```bash
git add .
git commit -m "Deploy: production release"
git push origin main
```

GitHub Actions will automatically:
- Run tests (`pytest tests/ -v`)
- Build Docker image
- Push to Docker Hub: `docker.io/YOUR_DOCKERHUB_USERNAME/pipeline-project:latest`

### 1.2 Verify Image Published

```bash
docker pull docker.io/YOUR_DOCKERHUB_USERNAME/pipeline-project:latest
```

**Expected Output**: Image pulled successfully without errors.

If the push fails with a repository-not-found or unauthorized error, verify that:

- the `pipeline-project` repository exists in Docker Hub,
- `DOCKERHUB_USERNAME` matches your Docker Hub account,
- `DOCKERHUB_TOKEN` is a valid access token with write permissions.

---

## Step 2: Provision AWS EC2 with Terraform

### 2.1 Initialize Terraform

```bash
cd infra/terraform

terraform init
```

### 2.2 Review Infrastructure Plan

```bash
terraform plan \
  -var aws_region="eu-north-1" \
  -var instance_name="insa4" \
  -var instance_type="t3.micro" \
  -var key_name="telco-key"
```

**Expected Output**: Plan shows EC2, security group, network resources.

### 2.3 Apply Terraform

```bash
terraform apply \
  -var aws_region="eu-north-1" \
  -var instance_name="insa4" \
  -var instance_type="t3.micro" \
  -var key_name="telco-key"
```

**When prompted**: Type `yes` and press Enter.

### 2.4 Capture Outputs

```bash
terraform output -json > ../terraform_outputs.json
TERRAFORM_PUBLIC_IP=$(terraform output -raw public_ip)
echo "EC2 Public IP: $TERRAFORM_PUBLIC_IP"
```

**Expected Output**: Public IP address (e.g., `16.171.78.151`)

---

## Step 3: Configure Ansible Inventory

### 3.1 Update Inventory

Edit `infra/ansible/inventory.ini`:

```ini
[app]
# Production inventory for existing EC2
# Host: <PUBLIC_IP>
# SSH user: ubuntu
# Private key file: telco-key.pem
16.171.78.151 ansible_user=ubuntu ansible_ssh_private_key_file=~/telco-key.pem
```

Replace `16.171.78.151` with your current EC2 public IP (or use the Terraform output from Step 2.4).

### 3.2 Verify Ansible Connectivity

```bash
cd ../ansible

ansible -i inventory.ini app -m ping
```

**Expected Output**:
```
16.171.78.151 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## Step 4: Deploy with Ansible

### 4.1 Set Environment Variables

```bash
export APP_IMAGE="docker.io/YOUR_DOCKERHUB_USERNAME/pipeline-project:latest"
export GRAFANA_ADMIN_PASSWORD="your-secure-password"
```

Replace:
- `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username
- `your-secure-password` with a strong password (minimum 12 characters recommended)

### 4.2 Run Playbook

```bash
ansible-playbook -i inventory.ini playbook.yml
```

**Expected Output**:
- Docker and docker-compose installed
- Application image pulled from Docker Hub
- docker-compose stack started
- Health checks passing:
  - `TASK [Wait for application health endpoint] PASSED`
  - `TASK [Wait for Prometheus] PASSED`
  - `TASK [Wait for Grafana] PASSED`

### 4.3 Verify Playbook Succeeded

```bash
echo "✅ Deployment complete"
```

---

## Step 5: Verification and Testing

### 5.1 Test Application Health

```bash
curl -s http://16.171.78.151:8000/health | jq .
```

**Expected Response**:
```json
{
  "status": "ok"
}
```

### 5.2 Test Application API

```bash
python scripts/test_client.py --base-url http://16.171.78.151:8000
```

**Expected Output**:
```
status: 200
{
  "prediction": true,
  "probability": 0.95
}
```

### 5.3 Verify Metrics

```bash
curl -s http://16.171.78.151:8000/metrics | head -20
```

**Expected Output**: Prometheus metrics in text format containing `pipeline_http_requests_total`, `pipeline_http_request_duration_seconds`.

### 5.4 Access Monitoring Stack

Open in browser:

- **Application**: http://16.171.78.151:8000/  
  (or http://16.171.78.151/ on port 80)

- **Grafana**: http://16.171.78.151:3000/  
  - Username: `admin`
  - Password: (use `GRAFANA_ADMIN_PASSWORD` from Step 4.1)

- **Prometheus**: http://16.171.78.151:9090/  
  - Query: `sum(rate(pipeline_http_requests_total[5m]))`

- **Loki**: http://16.171.78.151:3100/  
  - Query: `{job="docker-containers"}`

---

## Step 6: SSH Access to EC2

To debug or manage the services directly on the VM:

```bash
ssh -i ~/telco-key.pem ubuntu@16.171.78.151
```

### Useful Commands on EC2

```bash
# View running containers
docker ps

# View compose logs
docker compose -f /opt/pipeline-project/repo/docker-compose.prod.yml logs -f

# Check app status
curl http://localhost:8000/health

# Restart services
docker compose -f /opt/pipeline-project/repo/docker-compose.prod.yml restart
```

---

## Complete End-to-End Command Sequence

For a fresh deployment (non-interactive reference):

```bash
# 1. Push to main (CI runs automatically)
git push origin main

# 2. Wait for GitHub Actions to complete (2-3 minutes)
# Check: https://github.com/YOUR_ORG/YOUR_REPO/actions

# 3. Provision infrastructure
cd infra/terraform
terraform init
terraform apply -var aws_region="eu-north-1" -var instance_name="insa4" -var instance_type="t3.micro" -var key_name="telco-key" -auto-approve
TERRAFORM_PUBLIC_IP=$(terraform output -raw public_ip)

# 4. Update Ansible inventory
cd ../ansible
sed -i -E "s/^([0-9]{1,3}\.){3}[0-9]{1,3}[[:space:]]/\$TERRAFORM_PUBLIC_IP /" inventory.ini

# 5. Deploy
export APP_IMAGE="docker.io/YOUR_DOCKERHUB_USERNAME/pipeline-project:latest"
export GRAFANA_ADMIN_PASSWORD="your-secure-password"
ansible-playbook -i inventory.ini playbook.yml

# 6. Verify
curl http://$TERRAFORM_PUBLIC_IP:8000/health
```

---

## Troubleshooting

### Issue: Ansible SSH Connection Fails

```
Permission denied (publickey)
```

**Solution**:
1. Verify key permissions:
   ```bash
   chmod 600 ~/telco-key.pem
   ```
2. Verify key path in inventory.ini
3. Test direct SSH:
   ```bash
   ssh -i ~/telco-key.pem -v ubuntu@16.171.78.151
   ```

### Issue: Docker Image Pull Fails

```
Error response from daemon: manifest not found
```

**Solution**:
1. Verify Docker Hub image is pushed:
   ```bash
   docker pull docker.io/YOUR_DOCKERHUB_USERNAME/pipeline-project:latest
   ```
2. Check GitHub Actions CI completed successfully
3. Verify `APP_IMAGE` environment variable is correct

### Issue: Services Not Starting

```
Error response from daemon: network pipeline_default not found
```

**Solution**:
1. SSH into EC2:
   ```bash
   ssh -i ~/telco-key.pem ubuntu@16.171.78.151
   ```
2. Check compose status:
   ```bash
   docker compose -f /opt/pipeline-project/repo/docker-compose.prod.yml logs
   ```
3. Restart services:
   ```bash
   docker compose -f /opt/pipeline-project/repo/docker-compose.prod.yml restart
   ```

### Issue: Health Check Timeout

```
FAILED - Waiting for application health endpoint - 20 retries completed, check failed
```

**Solution**:
1. SSH into EC2 and check container logs:
   ```bash
   docker logs pipeline-app
   ```
2. Verify port mappings:
   ```bash
   docker port pipeline-app
   ```
3. Check security group:
   ```bash
   aws ec2 describe-security-groups --group-ids sg-xxxxx --region eu-north-1
   ```

---

## Cleanup (Optional)

To destroy infrastructure and stop incurring costs:

```bash
cd infra/terraform

terraform destroy \
  -var aws_region="eu-north-1" \
  -var instance_name="insa4" \
  -var instance_type="t3.micro" \
  -var key_name="telco-key"
```

**When prompted**: Type `yes`.

---

## Production Checklist

- [ ] GitHub Actions CI workflow passing
- [ ] Docker image pushed to Docker Hub
- [ ] Terraform plan reviewed and approved
- [ ] EC2 instance running with public IP
- [ ] Ansible playbook completed without errors
- [ ] Health checks passing
- [ ] Application accessible on port 8000
- [ ] Grafana dashboard accessible
- [ ] Prometheus metrics collected
- [ ] Loki logs visible
- [ ] SSH access verified
- [ ] Monitoring stack operational

---

## Support and Monitoring

### View Application Logs

```bash
# Via SSH
docker logs pipeline-app

# Via Ansible
ansible app -i infra/ansible/inventory.ini -m shell -a "docker logs pipeline-app"
```

### Monitor Metrics

Open Prometheus: http://16.171.78.151:9090/

Useful queries:
- Request rate: `sum(rate(pipeline_http_requests_total[5m]))`
- Error rate: `sum(rate(pipeline_http_requests_total{status=~"5.."}[5m]))`
- Latency (p95): `histogram_quantile(0.95, rate(pipeline_http_request_duration_seconds_bucket[5m]))`

### Check Container Status

```bash
ansible app -i infra/ansible/inventory.ini -m shell -a "docker ps"
```

---

## Documentation References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Ansible Documentation](https://docs.ansible.com/)
- [Docker Compose Specification](https://compose-spec.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)

---

**Generated**: 2026-04-29  
**Status**: Production-Ready
