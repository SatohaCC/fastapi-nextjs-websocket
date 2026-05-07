---
name: infrastructure-layer
description: ドメイン駆動設計のインフラ層のルール
---

# Infrastructure Layer (インフラストラクチャ層)

技術的な詳細（データベース、外部API、ファイルシステム、ネットワークなど）を実装し、他の層を技術的な制約から解放する層です。

## 1. 責務と制約

### 責務
*   **技術的詳細の隠蔽**: ドメイン層やアプリケーション層が「何をするか」に集中できるよう、「どうやって実現するか（SQLの組み立て、HTTP通信など）」を引き受ける。
*   **データの永続化**: エンティティのデータベースへの保存・復元を行う（Repositoryの実装）。
*   **外部リソース連携**: メール送信、他社APIの呼び出し、Redis/メッセージキューの操作などを実装する。

### 制約
*   **依存の方向**: ドメイン層やアプリケーション層（のインターフェース）に**依存する（向かう）**。逆に、ドメイン/アプリ層からインフラ層への直接的な依存は禁止（依存性逆転の原則）。
*   **ドメインロジックの排除**: ビジネスルールや計算ロジックをここに書いてはいけない。あくまでデータの変換や保存といった技術的関心事に徹する。

---

## 2. 構成要素

### 1. Repository Implementation (リポジトリ実装)
**役割**: ドメイン層で定義された `Repository Interface` を具体的に実装するクラス。
*   **特徴**: SQLAlchemy や PyMongo などの ORM/DB ドライバを直接扱う。
*   **相互変換の責務**: ドメインエンティティをそのままDBに保存するのではなく、一度 ORM などの技術的なデータ構造に変換してから保存する。取り出すときは逆（ORM -> Entity）を行う。

### 2. ORM Models (データモデル)
**役割**: データベースのテーブル構造を定義するクラス（例: SQLAlchemy の `Base` を継承したクラス）。
*   **特徴**: ドメインの「エンティティ」とは明確に区別する。ORMモデルはあくまで「DBにどう保存されるか」の設計図であり、ビジネスロジックは持たない。

### 3. External Clients / Adapters (外部クライアント)
**役割**: 外部 API やキャッシュ（Redis）などと通信するクラスの実装。
*   **例**: `RedisEventPublisher` (RedisのPub/Sub機能を使ってイベントを送信する実装)

---

## 3. インフラ層の典型的なフロー（Repository の実装例）

リポジトリにおける最も重要な役割は、「ドメインの世界」と「DBの世界」の橋渡し（マッピング）です。

```python
async def save(self, request: DirectRequest) -> DirectRequest:
    # 1. Domain Entity -> ORM Model への変換 (ドメインの型からDBの型へ)
    orm = RequestORM(
        sender=request.sender.value,       # DPからプリミティブな値を取り出す
        recipient=request.recipient.value,
        text=request.text.value,
        status=request.status.value,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )
    
    # 2. DB特有の処理（永続化技術の操作）
    if request.id is not None:
        orm.id = request.id.value
        orm = await self._session.merge(orm)
    else:
        self._session.add(orm)
        
    await self._session.commit()
    await self._session.refresh(orm)
    
    # 3. ORM Model -> Domain Entity への変換（復元してアプリケーション層に返す）
    return self._to_entity(orm)
```

---

## 4. DI (Dependency Injection) との関係

アプリケーション層が「どのインフラ実装を使っているか」を知らなくて済むように、`main.py` や `dependencies.py` などの構成ファイルで、インターフェースに対して具体的なインフラ実装を紐付け（DI）ます。

*   **利用する側 (Application層)**: `class RequestService(repo: RequestRepository)` 
    *   **役割**: 「具体的なDB技術は知らないが、保存機能（インターフェース）を持つ部品が欲しい」と要求するだけ。
*   **組み立てる側 (Presentation層 / FastAPIのDI)**: `RequestService(repo=SqlAlchemyRequestRepository(session))`
    *   **役割**: システム実行時に、`dependencies.py` などで「今回は PostgreSQL 向けの実装を渡すね」と具体的なインフラ実装を差し込む（注入する）。
