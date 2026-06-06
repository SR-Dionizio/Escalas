# ==========================================
# Descobre o ID da conta AWS
# ==========================================

data "aws_caller_identity" "current" {}

# ==========================================
# IAM Role para EventBridge Scheduler
# ==========================================

resource "aws_iam_role" "scheduler_role" {
  name = "${var.project_name}-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-scheduler-role"
  }
}

resource "aws_iam_role_policy" "scheduler_policy" {
  name = "${var.project_name}-scheduler-policy"
  role = aws_iam_role.scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]

        Resource = [
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:instance/${aws_instance.app.id}"
        ]
      }
    ]
  })
}

# ==========================================
# Liga a EC2 às 09:00
# ==========================================

resource "aws_scheduler_schedule" "start_ec2" {
  name = "${var.project_name}-start"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 9 * * ? *)"
  schedule_expression_timezone = "America/Sao_Paulo"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ec2:startInstances"
    role_arn = aws_iam_role.scheduler_role.arn

    input = jsonencode({
      InstanceIds = [
        aws_instance.app.id
      ]
    })
  }
}

# ==========================================
# Desliga a EC2 às 22:00
# ==========================================

resource "aws_scheduler_schedule" "stop_ec2" {
  name = "${var.project_name}-stop"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 22 * * ? *)"
  schedule_expression_timezone = "America/Sao_Paulo"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ec2:stopInstances"
    role_arn = aws_iam_role.scheduler_role.arn

    input = jsonencode({
      InstanceIds = [
        aws_instance.app.id
      ]
    })
  }
}