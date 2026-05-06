---
name: presentation-layer
description: ドメイン駆動設計のプレゼンテーション層のルール
---

# Presentation Layer (プレゼンテーション層)

外部（ユーザー、フロントエンド、他システム）からのリクエストを受け取り、システムに対する入力へと変換し、結果を返す「窓口」となる層です。
このプロジェクトにおいては **FastAPI** や **WebSocket** のルーターがこの層に該当します。

## 1. 責務と制約

### 責務
*   **ルーティング**: HTTP メソッドや WebSocket エンドポイントの定義。
*   **形式の変換とバリデーション**: JSON などの外部フォーマットを Pydantic スキーマ等で受け取り、アプリケーション層が理解できる形に変換・検証する。
*   **依存関係の注入 (DI)**: システム実行時に、アプリケーション層に対して具体的なインフラ実装をセットする（エンドポイントでの `Depends()` の活用）。
*   **エラーハンドリング**: ドメイン例外（Domain Exception）をキャッチし、適切な HTTP ステータスコード（400, 403, 404など）に変換する。

### 制約
*   **ビジネスロジックを持たない**: 計算、権限の最終判定、状態変更のルールなどはすべてアプリケーション層やドメイン層に任せる。
*   **データベースを直接触らない**: リポジトリの実装や ORM モデルをこの層で直接呼び出して操作してはいけない。必ず Application Service を経由する。

---

## 2. 構成要素

### 1. Routers / Controllers (`api/endpoints/`)
**役割**: エンドポイントの定義と、Application Service の呼び出し。
*   **特徴**: DI コンテナ（`Depends`）を利用して Application Service を受け取り、処理を委譲（丸投げ）する。結果を受け取ったらレスポンス用の JSON に変換して返す。

### 2. Request/Response Schemas (`schemas/`)
**役割**: Pydantic を使用したリクエスト・レスポンスのデータ定義。
*   **特徴**: 文字列長や必須チェックなどの「形式的な検証」はここで行うが、DBに存在するかどうか等の「ビジネスルールの検証」は行わない。

### 3. Dependencies (`api/dependencies.py`)
**役割**: 依存性注入（DI）の組み立てファクトリ。
*   **特徴**: `get_request_service` など、各サービスが動くために必要なコンポーネント（DBセッション、リポジトリのインスタンス化など）を定義し、ルーターに供給する。インフラ層の部品をセットする重要な場所。

---

## 3. 典型的なリクエスト処理フロー

プレゼンテーション層のコードは「入力を受ける」「サービスを呼ぶ」「結果を返す（例外を処理する）」の 3 ステップだけで構成されるのが理想的です。

```python
# Presentation Layer (FastAPI ルーター)
@router.post("/requests", response_model=RequestResponseSchema)
async def create_request(
    # 1. 入力を受ける: FastAPIがJSONを解釈し、Pydanticで形式的なバリデーションを行う
    payload: CreateRequestSchema,
    # (DIによるサービスの注入)
    service: RequestService = Depends(get_request_service) 
):
    try:
        # 2. サービスを呼ぶ: バリデーション済みのデータを渡し、実際の処理を委譲（丸投げ）する
        result = await service.send_request(
            sender=payload.sender,
            recipient=payload.recipient,
            text=payload.text
        )
        
        # 3. 結果を返す: 正常時はPydanticスキーマに自動変換されてレスポンスとなる
        return result
        
    except ValueError as e:
        # 3. (例外時) 例外を処理する: ドメイン例外を適切な HTTP ステータス(400等)に変換する
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 4. WebSockets の扱いについて

WebSocket もプレゼンテーション層の一部です。
HTTP と異なり「接続の維持」や「Pub/Subからの受信」が必要ですが、本質的なルールは同じです。

受け取ったメッセージの保存などの処理を行う際は、直接 DB 操作などを書くのではなく、**HTTP リクエストと同様に Application Service（例：`ChatService` の `send_message`）を呼び出して処理を委譲**してください。
