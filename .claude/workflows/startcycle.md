---
description: Start the Autonomous AI Developer Pipeline sequence with a new idea
---

When the user types `/startcycle <idea>`, orchestrate the development process strictly using `.agents/agents.md` and `.agents/skills/`.

### Execution Sequence:

1. Act as the **Product Manager** and execute the `write_specs.md` skill using the `<idea>`.
   - 既存プロジェクトの調査結果（影響を受けるファイルパス等）を仕様書に含めること。
   _(Wait for the user to explicitly approve the spec. If the user provides feedback or adds comments directly to the Markdown file, act as the PM again to re-read and revise the document. Loop this step until they type "Approved")._
2. Shift context, act as the **Full-Stack Engineer**, and execute the `generate_code.md` skill.
   - PMが作成した仕様書および特定した既存ファイルを参照して実装すること。
3. Shift context, act as the **QA Engineer**, and execute the `audit_code.md` skill.
4. Shift context, act as the **DevOps Master**, and execute the `deploy_app.md` skill.
