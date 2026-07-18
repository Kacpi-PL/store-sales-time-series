terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_ecr_repository" "api" {
  name = "store-sales-api"
}

output "repository_url" {
  value = aws_ecr_repository.api.repository_url
}



resource "aws_iam_role" "ecs_execution" {
  name = "ecs-express-execution"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_iam_role" "ecs_infra" {
  name = "ecs-express-infra"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_infra" {
  role       = aws_iam_role.ecs_infra.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSInfrastructureRoleforExpressGatewayServices"
}


resource "aws_ecs_express_gateway_service" "api" {
  service_name            = "store-sales-express"
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  infrastructure_role_arn = aws_iam_role.ecs_infra.arn
  health_check_path       = "/health"
  cpu                     = "256"
  memory                  = "1024"

  primary_container {
    image          = "${aws_ecr_repository.api.repository_url}:latest"
    container_port = 8080
  }
}

output "express_ingress" {
  value = aws_ecs_express_gateway_service.api.ingress_paths
}