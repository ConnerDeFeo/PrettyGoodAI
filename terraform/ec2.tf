# Security group for the EC2 instance
resource "aws_security_group" "pgai_voice_bot_sg" {
  name        = "pgai-voice-bot-sg"
  description = "Allow SSH and HTTP access to pgai voice bot server"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "pgai-voice-bot-sg"
  }
}

# Ec2 role for the instance to allow it to access AWS services like DynamoDB and Bedrock
resource "aws_iam_role" "pgai_voice_bot_role" {
  name = "pgai-voice-bot-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach a policy to the role to allow access to DynamoDB and Bedrock
resource "aws_iam_role_policy" "pgai_voice_bot_policy" {
  name = "pgai-voice-bot-policy"
  role = aws_iam_role.pgai_voice_bot_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the role to the EC2 instance
resource "aws_iam_instance_profile" "pgai_voice_bot_instance_profile" {
  name = "pgai-voice-bot-instance-profile"
  role = aws_iam_role.pgai_voice_bot_role.name
}

# Associate the instance profile with the EC2 instance
resource "aws_instance" "pgai_receptionist" {
  ami           = "ami-0edc0a81903bf24ef"
  instance_type = "t3.small"

  vpc_security_group_ids = [aws_security_group.pgai_voice_bot_sg.id]
  iam_instance_profile = aws_iam_instance_profile.pgai_voice_bot_instance_profile.name

  user_data = file("${path.module}/userdata.sh")

  tags = {
    Name = "pgai-voice-bot-server"
  }
}

# Elastic IP for the EC2 instance
resource "aws_eip" "pgai_voice_bot_eip" {
  instance = aws_instance.pgai_receptionist.id
  domain   = "vpc"

  tags = {
    Name = "pgai-voice-bot-eip"
  }
}

output "server_ip" {
  value = aws_eip.pgai_voice_bot_eip.public_ip
}