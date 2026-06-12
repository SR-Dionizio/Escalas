# Route 53 Configuration for escalas.click
# This configures DNS records to point to the EC2 instance

# Data source to get the existing hosted zone
data "aws_route53_zone" "main" {
  zone_id = var.hosted_zone_id
}

# A record for root domain (escalas.click)
resource "aws_route53_record" "root" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [aws_eip.app.public_ip]
}

# A record for www subdomain (www.escalas.click)
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [aws_eip.app.public_ip]
}

# Optional: CNAME record to redirect www to root
# Uncomment if you prefer CNAME instead of A record for www
# resource "aws_route53_record" "www_cname" {
#   zone_id = data.aws_route53_zone.main.zone_id
#   name    = "www.${var.domain_name}"
#   type    = "CNAME"
#   ttl     = 300
#   records = [var.domain_name]
# }