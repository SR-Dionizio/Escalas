# EFS File System
resource "aws_efs_file_system" "main" {
  creation_token   = "${var.project_name}-efs"
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  encrypted        = true

  tags = {
    Name = "${var.project_name}-efs"
  }
}

# EFS Mount Targets (um para cada subnet privada)
resource "aws_efs_mount_target" "private_1" {
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = aws_subnet.private_1.id
  security_groups = [aws_security_group.efs.id]

  depends_on = [aws_security_group.efs]
}

resource "aws_efs_mount_target" "private_2" {
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = aws_subnet.private_2.id
  security_groups = [aws_security_group.efs.id]

  depends_on = [aws_security_group.efs]
}

# EFS Access Point para a aplicação
resource "aws_efs_access_point" "app" {
  file_system_id = aws_efs_file_system.main.id

  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/app-data"

    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }

  tags = {
    Name = "${var.project_name}-app-access-point"
  }
}

