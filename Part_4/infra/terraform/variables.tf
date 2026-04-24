variable "subscription_id" {
  type        = string
  description = "Azure subscription ID used by the provider"
  default     = null
}

variable "azure_location" {
  type        = string
  description = "Azure region for all resources"
  default     = "westeurope"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name"
  default     = "rg-pipeline-project"
}

variable "instance_name" {
  type        = string
  description = "Name for the Azure virtual machine"
  default     = "pipeline-project"
}

variable "vm_size" {
  type        = string
  description = "Azure VM size"
  default     = "Standard_B1s"
}

variable "admin_username" {
  type        = string
  description = "Admin username for SSH login"
  default     = "azureuser"
}

variable "public_key_path" {
  type        = string
  description = "Path to the SSH public key used for the Azure VM"
  default     = "~/.ssh/id_rsa.pub"
}

variable "private_key_path" {
  type        = string
  description = "Path to the SSH private key used for connecting to the Azure VM"
  default     = "~/.ssh/id_rsa"
}

variable "vnet_cidr" {
  type        = string
  description = "Address range for the virtual network"
  default     = "10.10.0.0/16"
}

variable "subnet_cidr" {
  type        = string
  description = "Address range for the VM subnet"
  default     = "10.10.1.0/24"
}

variable "ssh_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to SSH into the VM"
  default     = ["0.0.0.0/0"]
}

variable "app_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to reach app and monitoring ports"
  default     = ["0.0.0.0/0"]
}
