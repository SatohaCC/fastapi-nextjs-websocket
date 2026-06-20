# AWS デプロイ (Terraform + ECS Fargate)

このディレクトリは、旧 `k8s/`（単一インスタンス構成、SPOFあり）を置き換える
AWS本番デプロイ用の Terraform 定義です。

## アーキテクチャ概要

- **Backend**: ECS Fargate（`desired_count` 2以上、ALB配下、CPUターゲット追跡によるオートスケール）
- **PostgreSQL**: RDS for PostgreSQL（Multi-AZ、自動フェイルオーバー）
- **Redis**: ElastiCache for Redis（replication group、automatic failover + multi-AZ）
- **Frontend**: スコープ外。Vercel へ別途デプロイすること（BFFパターンのためNode実行環境が必須、静的書き出し不可）
- **NAT Gateway なし**: バックエンドは外部HTTPサービスを呼ばないため、ECR/Secrets Manager/CloudWatch Logs へは VPC エンドポイント経由でアクセスする

## 前提条件

- Terraform >= 1.7
- AWS CLI（認証済み: `aws configure` または環境変数）
- Docker（バックエンドイメージのビルド用）

## コストに関する注意

RDS Multi-AZ、ElastiCache replication group（2ノード）、ALB、ECS Fargate（2タスク）を
常時起動すると、最小構成でも**月額$100〜150程度**のオーダーになる見込みです。
検証目的であれば、確認後に `terraform destroy` で速やかに破棄してください。

## デプロイ手順

### 1. バックエンドイメージをビルドして ECR へ push

```bash
# まず ECR リポジトリだけ先に作る（初回のみ）
terraform init
terraform apply -target=aws_ecr_repository.backend

REPO_URL=$(terraform output -raw ecr_repository_url)
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin "$REPO_URL"

docker build -t "$REPO_URL:latest" ../backend
docker push "$REPO_URL:latest"
```

### 2. 変数を設定して `terraform apply`

```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集（<change-me> をすべて置き換える）

terraform apply
```

### 3. 初回マイグレーションを実行する

サービス本体のタスクは `RUN_MIGRATIONS=false` で起動するため、デプロイ直後に
1回限りの専用タスクでマイグレーションを実行する必要があります。

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEF=$(terraform output -raw ecs_task_definition_arn)
SUBNETS=$(terraform output -json private_subnet_ids | tr -d '[]" \n')
SG=$(terraform output -raw ecs_security_group_id)

aws ecs run-task \
  --cluster "$CLUSTER" \
  --task-definition "$TASK_DEF" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"backend","environment":[{"name":"RUN_MIGRATIONS","value":"true"},{"name":"MIGRATE_ONLY","value":"true"}]}]}'
```

タスクのステータスが `STOPPED` かつ `exitCode: 0` になればマイグレーション完了です
（CloudWatch Logs `/ecs/<project>-backend` でログを確認できます）。

新しいマイグレーションを追加した場合のデプロイ時も、同じコマンドを再実行してください
（既に最新なら何も変更せず正常終了します）。

### 4. 動作確認

```bash
curl http://$(terraform output -raw alb_dns_name)/health
# => {"status":"ok"}
```

### 5. フロントエンドを Vercel にデプロイ

Vercel のプロジェクト設定で以下の環境変数を設定してください。

- `BFF_SECRET`: `python -c "import secrets; print(secrets.token_hex(32))"` で生成
- `NEXT_PUBLIC_API_URL`: `http://<alb_dns_name>`（独自ドメインがあればそちらを推奨）
- `NEXT_PUBLIC_WS_URL`: `ws://<alb_dns_name>`

デプロイ後、Vercel の本番URLを `terraform.tfvars` の `allowed_origin` に設定して
`terraform apply` し直してください（CORS許可オリジンの更新）。

## 破棄する場合

```bash
terraform destroy
```

`aws_db_instance` には `skip_final_snapshot = false` を設定しているため、
destroy 時に最終スナップショットが作成されます（不要なら `rds.tf` で調整してください）。
