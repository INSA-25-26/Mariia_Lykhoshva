output "public_ip" {
  value       = aws_instance.this.public_ip
  description = "Public IP address of the EC2 instance"
}

output "public_dns" {
  value       = aws_instance.this.public_dns
  description = "Public DNS name of the EC2 instance"
}

output "application_url" {
  value       = "http://${aws_instance.this.public_ip}:8000"
  description = "FastAPI application URL"
}

output "grafana_url" {
  value       = "http://${aws_instance.this.public_ip}:3000"
  description = "Grafana URL"
}

output "prometheus_url" {
  value       = "http://${aws_instance.this.public_ip}:9090"
  description = "Prometheus URL"
}

output "ssh_command" {
  value       = "ssh -i ~/telco-key.pem ubuntu@${aws_instance.this.public_ip}"
  description = "SSH command for the provisioned EC2 instance"
}
