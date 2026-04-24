# Terraform: intentional insecure patterns for static IaC analyzers. Not applied by default.
# RESEARCH ONLY — do not use for real infrastructure.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Hard-coded "secret" (tfsec / checkov style findings)
variable "insecure_token" {
  type    = string
  default = "RESEARCH-STATIC-CRED-DO-NOT-USE-IN-AWS"
  sensitive = false
}

# Example: public ingress rule (0.0.0.0/0) and plaintext description of secret usage
resource "aws_security_group" "bookstore_misconfig" {
  name        = "python-vuln-app-sg"
  description = "Research SG — overly broad ingress for static analysis only"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "exposed app port"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Placeholder bucket without encryption block (IaC scanner noise)
resource "aws_s3_bucket" "insecure_artifacts" {
  bucket = "python-vuln-app-research-bucket-UNUSED"
  tags = {
    Purpose = "research-iac-misconfig-demo"
  }
}

output "insecure_var_echo" {
  value     = var.insecure_token
  sensitive = false
}
