output "instance_public_ip" {
  value       = azurerm_public_ip.this.ip_address
  description = "Public IP address of the Azure VM"
}

output "ssh_command" {
  value       = "ssh -i ${pathexpand(var.private_key_path)} ${var.admin_username}@${azurerm_public_ip.this.ip_address}"
  description = "SSH command for the provisioned VM"
}

output "application_url" {
  value       = "http://${azurerm_public_ip.this.ip_address}:8000"
  description = "FastAPI application URL"
}

output "grafana_url" {
  value       = "http://${azurerm_public_ip.this.ip_address}:3000"
  description = "Grafana URL"
}

output "prometheus_url" {
  value       = "http://${azurerm_public_ip.this.ip_address}:9090"
  description = "Prometheus URL"
}
