output "ec2_instance_id" {
  value = aws_instance.app.id
}

output "elastic_ip" {
  value = aws_eip.app.public_ip
}

output "application_url" {
  value = "http://${aws_eip.app.public_ip}:8000"
}

output "vpc_id" {
  value = aws_vpc.main.id
}

# Route 53 Outputs
output "domain_name" {
  description = "Domain name"
  value       = var.domain_name
}

output "domain_url" {
  description = "Application URL with domain"
  value       = "http://${var.domain_name}"
}

output "domain_url_www" {
  description = "Application URL with www subdomain"
  value       = "http://www.${var.domain_name}"
}

output "nameservers" {
  description = "Route 53 nameservers for the hosted zone"
  value       = data.aws_route53_zone.main.name_servers
}