# JWT 署名鍵・SQLAdmin 暗号化鍵は openssl rand -hex 32 相当の値を自動生成する
# （k8s/secret.yaml.example のコメント "openssl rand -hex 32" を Terraform に移植）。
resource "random_id" "secret_key" {
  byte_length = 32
}

resource "random_id" "admin_secret_key" {
  byte_length = 32
}

resource "aws_secretsmanager_secret" "database_url" {
  name = "${var.project}/DATABASE_URL"
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql+asyncpg://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.address}:5432/${aws_db_instance.main.db_name}"
}

resource "aws_secretsmanager_secret" "secret_key" {
  name = "${var.project}/SECRET_KEY"
}

resource "aws_secretsmanager_secret_version" "secret_key" {
  secret_id     = aws_secretsmanager_secret.secret_key.id
  secret_string = random_id.secret_key.hex
}

resource "aws_secretsmanager_secret" "admin_password" {
  name = "${var.project}/ADMIN_PASSWORD"
}

resource "aws_secretsmanager_secret_version" "admin_password" {
  secret_id     = aws_secretsmanager_secret.admin_password.id
  secret_string = var.admin_password
}

resource "aws_secretsmanager_secret" "admin_secret_key" {
  name = "${var.project}/ADMIN_SECRET_KEY"
}

resource "aws_secretsmanager_secret_version" "admin_secret_key" {
  secret_id     = aws_secretsmanager_secret.admin_secret_key.id
  secret_string = random_id.admin_secret_key.hex
}

resource "aws_secretsmanager_secret" "users" {
  name = "${var.project}/USERS"
}

resource "aws_secretsmanager_secret_version" "users" {
  secret_id     = aws_secretsmanager_secret.users.id
  secret_string = var.users_json
}
