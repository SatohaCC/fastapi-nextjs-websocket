terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # state はローカル管理から開始する。チームで運用する場合は
  # S3 バックエンド + DynamoDB ロックテーブルへ移行すること。
  #
  # backend "s3" {
  #   bucket         = "<your-state-bucket>"
  #   key            = "fastapi-nextjs-websocket/terraform.tfstate"
  #   region         = "ap-northeast-1"
  #   dynamodb_table = "<your-lock-table>"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}
