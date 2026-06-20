resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project}-redis-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

# ElastiCache for Redis, replication group + automatic failover。
# 単一インスタンス・永続化なし（k8s/redis.yaml replicas:1）だったSPOFを解消する。
# アプリ側は redis.asyncio.from_url(単一URL) のままで対応可能
# （フェイルオーバー時のエンドポイント切替はAWSがDNSレベルで行うため、
# Sentinel対応のクライアントコード変更は不要）。
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "${var.project}-redis"
  description          = "Redis for WS pub/sub, presence, rate limit, sessions"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = var.redis_node_type
  port           = 6379

  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled           = true

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  tags = { Name = "${var.project}-redis" }
}
