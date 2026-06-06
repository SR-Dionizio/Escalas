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