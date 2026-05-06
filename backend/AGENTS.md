# FastAPIのルール
- Docstringを必ず実施して。

# アーキテクチャ設計指針 (Architecture Guidelines)

## 1. 採用パターン: オニオンアーキテクチャ
本プロジェクトでは、変更に強く、テストが容易な **Onion Architecture** を採用する。
中心に「ビジネスロジック（Domain）」を配置し、外部（DB、UI、フレームワーク）への依存を内側に向かって制御する。

```mermaid
graph TD
    subgraph "External (Infrastructure/Presentation)"
        API[Presentation Layer (FastAPI/WebSocket)]
        DB[Infrastructure Layer (SQLAlchemy/Redis)]
    end

    subgraph "Core"
        App[Application Layer (Use Cases)]
        Domain[Domain Layer (Entities, Repository Interfaces)]
    end

    API --> App
    API --> Domain
    App --> Domain
    DB --> Domain (Interfaces)
```
