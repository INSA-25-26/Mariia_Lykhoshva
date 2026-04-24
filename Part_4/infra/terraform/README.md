# Terraform for Azure VM

This directory provisions the Azure infrastructure needed for the final cloud deployment.

Expected resources:

- Resource group
- Virtual network and subnet
- Network security group with SSH, app, Prometheus, and Grafana ports
- Public IP + network interface
- Ubuntu Linux virtual machine with SSH key authentication

Recommended outputs:

- VM public IP
- SSH connection string
- URLs for the app, Prometheus, and Grafana endpoints
