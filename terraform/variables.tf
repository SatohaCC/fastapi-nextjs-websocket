variable "aws_region" {
  description = "デプロイ先の AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "リソース名のプレフィックスとして使うプロジェクト名"
  type        = string
  default     = "fastapi-nextjs-websocket"
}

variable "environment" {
  description = "環境名（タグ付け用）"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC の CIDR ブロック"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "リソースを分散させる2つの AZ"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

# --- アプリケーション設定 ---

variable "allowed_origin" {
  description = "CORS で許可するフロントエンドのオリジン（Vercel の本番URL）"
  type        = string
}

variable "backend_image_tag" {
  description = "ECR にプッシュしたバックエンドイメージのタグ"
  type        = string
  default     = "latest"
}

variable "desired_count" {
  description = "ECS サービスの desired task count（2以上で単一障害点を排除）"
  type        = number
  default     = 2
}

# --- シークレット（terraform.tfvars で実際の値を設定すること） ---

variable "db_password" {
  description = "RDS マスターパスワード"
  type        = string
  sensitive   = true
}

variable "admin_password" {
  description = "SQLAdmin 管理画面のログインパスワード"
  type        = string
  sensitive   = true
}

variable "users_json" {
  description = "ログイン可能なユーザーマスター（JSON文字列。例: {\"alice\":\"password1\"}）"
  type        = string
  sensitive   = true
}

# --- インスタンスサイズ ---

variable "db_instance_class" {
  description = "RDS インスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache ノードタイプ"
  type        = string
  default     = "cache.t3.micro"
}

variable "ecs_task_cpu" {
  description = "ECS タスクの CPU ユニット（Fargate）"
  type        = string
  default     = "256"
}

variable "ecs_task_memory" {
  description = "ECS タスクのメモリ（MiB、Fargate）"
  type        = string
  default     = "512"
}
