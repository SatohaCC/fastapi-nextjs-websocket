---
name: domain-layer
description: ドメイン駆動設計・オニオンアーキテクチャのドメイン層のルール
---

# Domain Layer (ドメイン層)

システムの核となるビジネスルールを記述する層です。

### オニオンアーキテクチャにおけるドメイン層

### 特徴

- **最内層**：他の層から依存されるが、逆方向の依存はない
- **最優先**：ビジネスロジックの品質が最重要
- **抽象化**：実装詳細（DB、フレームワーク）に依存しない
- **テスト可能**：外部依存がないため、単体テストが容易


## 1. 責務と制約

### 責務
*   ビジネスルール（値の妥当性、計算ロジック、状態遷移）の完結。
*   ドメイン知識を「コード」として表現し、不変条件を維持する。

### 制約
*   **純粋な Python のみを使用**: `FastAPI` や `SQLAlchemy` などの外部ライブラリに依存してはいけません。
*   **標準ライブラリのみ**: `dataclasses`, `enum`, `typing`, `datetime` などに限定します。
*   **外部の無知**: データベースや API、Web フレームワークの存在を知っていてはいけません。

---

## 2. 構成要素

### 1. Domain Primitive (DP)
**定義:** 基本型（str, int 等）をラップし、ドメインの概念を最小単位で表現するもの。
*   **特徴**: 単一の値を持ち、生成時にその値がドメイン内で「存在可能か」を検証（自己検証）する。不正な値を持つオブジェクトのインスタンス化を物理的に防ぐ。
*   **不変性**: `__slots__ = ()` や `frozen=True` により厳格に守られる。
*   **例**: `Email`, `Price`, `Quantity`, `ZipCode`, `OrderStatus` (Enum)

### 2. Value Object (VO)
**定義:** 複数の属性を組み合わせ、一つの「値」として扱う不変のオブジェクト。
*   **特徴**: 同一性（ID）を持たず、すべての属性値が同じであれば同じものとみなす。
*   **役割**: DP を組み合わせたり、複雑な値のルールを表現する。
*   **例**: `Address` (City + Street + Zip), `Money` (Amount + Currency), `FullName` (First + Last)

### 3. Entity
**定義:** 唯一識別子（ID）を持ち、ライフサイクル（状態変化）がある主要なビジネス対象。
*   **特徴**: ID により同一性が判定される。属性が変わっても ID が同じなら同一オブジェクト。
*   **可変性**: ビジネスルールに基づく状態遷移メソッドを持つ。
*   **例**: `User`, `Order`, `Product`, `BankAccount`

### 4. Aggregate (アグリゲート)
**定義:** Entity と VO を階層化した「一貫性の境界」。
*   **特徴**: **Aggregate Root**（一つの Entity）を通じてのみ操作され、境界内の整合性を保証する。
*   **制約**: 外部（Application 層など）からは Aggregate Root 以外を直接操作してはならない
*   **例**: `Order` (Root とその配下の OrderItems), `User` (Root とその配下の Profile)

### 5. Domain Service
**定義:** 複数の Entity や VO にまたがる、特定のオブジェクトに閉じ込められないビジネスロジック。
*   **特徴**: 状態を持たない (Stateless)。
*   **例**: `TransferService` (銀行振込処理), `TaxCalculator` (税金計算), `PasswordHasher`

### 6. Repository Interface
**定義:** 永続化（保存・取得）に関する抽象的な定義（インターフェース）。
*   **役割**: ドメイン層が「何ができるか」を定義し、具体的な DB 操作は隠蔽する。
*   **例**: `IUserRepository`, `IOrderRepository`

### 7. Domain Exception
**定義:** ビジネスルール違反を表現する専用の例外クラス。
*   **特徴**:
    *   **送出場所**: エンティティや DP の内部でルールチェックに失敗した際に `raise` される。
    *   **定義場所**: 循環参照を避け、管理を容易にするために `domain/exceptions.py` などに集約される。
*   **例**: `InsufficientBalanceException` (残高不足), `OutOfStockException` (在庫切れ)

---

## 3. ディレクトリ構成

ドメイン層内は、役割と依存関係を明確にするため以下のように分割します。

```text
domain/
  primitives/     # 1. 最小単位 (DP, Enum)
  value_objects/  # 2. 複合的な値 (VO)
  entities/       # 3. 識別子を持つオブジェクト
  repositories/   # 6. インターフェース定義
  services/       # 5. 横断的なロジック
  exceptions.py   # 7. ドメイン例外
