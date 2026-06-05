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
          "ecs:UpdateService"
        ]
        Resource = [
          aws_ecs_service.main.id,
          aws_ecs_cluster.main.arn
        ]
      }
    ]
  })
}

# ==========================================
# Liga o ECS às 09:00 (Horário de Brasília)
# ==========================================

resource "aws_scheduler_schedule" "start_ecs" {
  name = "${var.project_name}-start"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 9 * * ? *)"
  schedule_expression_timezone = "America/Sao_Paulo"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ecs:updateService"
    role_arn = aws_iam_role.scheduler_role.arn

    input = jsonencode({
      Cluster      = aws_ecs_cluster.main.name
      Service      = aws_ecs_service.main.name
      DesiredCount = 1
    })
  }
}

# ==========================================
# Desliga o ECS às 22:00 (Horário de Brasília)
# ==========================================

resource "aws_scheduler_schedule" "stop_ecs" {
  name = "${var.project_name}-stop"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 22 * * ? *)"
  schedule_expression_timezone = "America/Sao_Paulo"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ecs:updateService"
    role_arn = aws_iam_role.scheduler_role.arn

    input = jsonencode({
      Cluster      = aws_ecs_cluster.main.name
      Service      = aws_ecs_service.main.name
      DesiredCount = 0
    })
  }
}