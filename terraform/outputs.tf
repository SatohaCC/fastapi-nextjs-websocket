output "alb_dns_name" {
  description = "ALB の DNS 名（フロントエンドの NEXT_PUBLIC_API_URL / NEXT_PUBLIC_WS_URL に使用）"
  value       = aws_lb.main.dns_name
}

output "rds_endpoint" {
  description = "RDS のエンドポイント（ホスト:ポート）"
  value       = aws_db_instance.main.endpoint
}

output "redis_primary_endpoint" {
  description = "ElastiCache replication group のプライマリエンドポイント"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "ecr_repository_url" {
  description = "バックエンドイメージの ECR リポジトリ URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecs_cluster_name" {
  description = "ECS クラスタ名（aws ecs run-task 等で使用）"
  value       = aws_ecs_cluster.main.name
}

output "ecs_task_definition_arn" {
  description = "ECS タスク定義 ARN（1回限りのマイグレーションタスク実行に使用）"
  value       = aws_ecs_task_definition.backend.arn
}

output "private_subnet_ids" {
  description = "プライベートサブネットID一覧（aws ecs run-task のネットワーク設定に使用）"
  value       = aws_subnet.private[*].id
}

output "ecs_security_group_id" {
  description = "ECS タスク用セキュリティグループID（aws ecs run-task のネットワーク設定に使用）"
  value       = aws_security_group.ecs.id
}
