---
name: ddd-onion-bestpractices
description: ドメイン駆動設計とオニオンアーキテクチャのベストプラクティス
---

# Domain-Driven Design (DDD) Best Practices
## 1. レイヤー定義と責務

### 1.1 Domain Layer (ドメイン層)
*   **責務**: ビジネスルール、状態の正当性、およびビジネス概念を表現する。外部に一切依存しない純粋なロジックを置く。
*   **ルール**: 他のどの層にも依存してはならない。
*   **詳細**: [Domain Layer リファレンス](references/domain-layer.md)

### 1.2 Application Layer (アプリケーション層)
*   **責務**: ドメインオブジェクトを組み合わせて、具体的な「ユースケース」を実現する。
*   **ルール**: ドメインオブジェクトの操作のみを行い、具体的な DB 操作などは行わない。
*   **詳細**: [Application Layer リファレンス](references/application-layer.md)

### 1.3 Infrastructure Layer (インフラ層)
*   **責務**: 技術的な詳細（DB接続、外部API通信、メッセージブローカー）の実装。
*   **ルール**: ドメイン層で定義されたインターフェースを実装する（依存性逆転）。
*   **詳細**: [Infrastructure Layer リファレンス](references/infrastructure-layer.md)

### 1.4 Presentation Layer (プレゼンテーション層)
*   **責務**: 外部（ユーザー、他システム）との入出力。
*   **ルール**: 直接ドメイン層を操作せず、アプリケーション層（ユースケース）を呼び出す。
*   **詳細**: [Presentation Layer リファレンス](references/presentation-layer.md)



## 1.5. 依存性逆転の原則 (DIP)
「上位モジュール（Domain/App）は下位モジュール（Infra）に依存してはならない。両者は抽象（Interface）に依存すべきである」

*   **メリット**: DB を PostgreSQL から他のものに変えても、ビジネスロジック（Domain/App）を一切書き換える必要がない。
*   **実装**: Python では `typing.Protocol` や `abc.ABC` を使ってインターフェースをドメイン層に定義する。
*   **詳細**: [Dependency Inversion Principle リファレンス](references/dependency-inversion-principle.md)


### 1.5.1 データフローの原則
1.  **入力**: `Presentation` -> `Application` (Use Case) へデータが渡される。
2.  **ロジック**: `Application` が `Domain Entity` を生成・操作する。
3.  **永続化**: `Application` が `Repository Interface` を介して保存を依頼する。
4.  **実行**: `Infrastructure` が実際に DB に書き込むが、`Application` はその詳細を知らない。

## 1.6 トランザクション管理（Unit of Work: UoW）
*   **責務**: 関連する一連のデータベース操作を一つの「仕事の単位」として扱い、成功したら一括保存（Commit）、失敗したら全キャンセル（Rollback）を行う。
*   **ルール**:
    *   `Application Layer` で `uow` を受け取り、その `commit()` メソッドを呼ぶことでトランザクションを完了させる。
    *   `Infrastructure Layer` は `commit()` を呼んではならない（`flush()` は内部で行う）。
*   **詳細**: [Unit of Work リファレンス](references/unit-of-work.md)
