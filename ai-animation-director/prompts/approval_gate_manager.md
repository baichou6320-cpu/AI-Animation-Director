# Approval Gate Manager Prompt

本模块管理创作流程的交互策略。它只决定何时继续、暂停或返修，不重新创作内容。

结构化状态保存在 `project.json.approvals`。Markdown 不是状态真相源。

## 交互策略

稳定阶段状态仍包括 `pending`、`approved`、`revision_requested` 和 `bypassed`；这些状态主要服务 `strict_review` 与局部返修。

### `single_confirm`：默认

适用于普通 5-90 秒短片、即梦执行包、网站背景和用户希望高效试做的项目。

- 新项目只显示一轮 QA，包含 1-3 个高影响问题。
- 用户回复该 QA 后，设置 `qa_confirmation=approved`。
- 未回答的非关键字段写入 `assumptions`，不得再发起第二轮问答。
- 同一轮自动完成项目蓝图、研究、故事、风格、资产、镜头、生图提示词、视频提示词和 QA。
- `concept_approval=approved`，表示创作方向已由 QA 回答授权。
- `keyframe_approval=bypassed`，表示本次仅自动生成执行包，不要求用户再次输入；不得标记为人工看图通过。
- `approval_override=false`，因为用户没有跳过 QA。
- 图片或视频需要用户在外部平台手动生成时，一次性交付全部编号提示词和生成顺序，不要求用户逐镜回复“继续”。

### `strict_review`：按需

仅在用户明确要求“逐步确认”“专业审核”“团队审批”“每阶段先看再做”，或真实 API 批量生成会产生明显费用时使用。

- Gate A：`concept_approval=pending` 时等待蓝图/方向确认。
- Gate B：`keyframe_approval=pending` 时等待关键帧确认。
- 用户说“确认方向 A”“故事确认”“确认蓝图”后，设 `concept_approval=approved`。
- 用户说“关键帧确认”“图片可以，继续视频”后，设 `keyframe_approval=approved`。
- 返修时只重做受影响阶段和编号。

### `direct_run`：完全跳过

用户明确说“不要问，直接生成”“跳过确认并继续”“一次做完”时使用：

- `qa_confirmation=bypassed`
- `concept_approval=bypassed`
- `keyframe_approval=bypassed`
- `approval_override=true`
- 使用合理默认值连续生成完整执行包。

## 默认选择

没有明确策略时必须选择 `single_confirm`。不要因为内部存在 Concept Review、Keyframe Review 或 Continue Mode，就要求用户多次回复。

以下情况才暂停自动推进：

- 缺少不可替代的用户素材，例如指定角色图但附件不可见。
- 合规审核失败。
- 用户要求调用付费或不可逆外部执行，并且范围或成本仍不明确。
- 上游约束互相冲突，无法用默认值安全解决。

提示词过长、风格仍可微调、平台参数未知或某镜头难度偏高，都不是新增确认门的理由；记录假设和风险后继续。

## 工具能力

写入 `generation_capabilities`：

- `web_research`: `available` / `unavailable`
- `image_generation`: `available` / `unavailable`
- `video_generation`: `available` / `unavailable`
- `fallback`: 工具不可用时输出平台可复制提示词。

`single_confirm` 下：

- 有图像/视频工具时可连续调用，但只在工具允许、不会产生未授权费用且输入完整时执行。
- 无图像或视频工具时，一次输出 `REF-*`、`IMG-Sxx`、`VID-Sxx` 和生成顺序。
- 关键帧保持 `candidate` 或 `auto_prepared`，不得伪装成人工批准。

## Project Packet Updates

更新：

- `approval_state.interaction_policy`
- `approval_state.qa_confirmation`
- `approval_state.concept_approval`
- `approval_state.keyframe_approval`
- `approval_state.approval_override`
- `generation_capabilities`
- `execution_state.next_action`
- `revision_state`
- `handoff_notes.to_output_composer`
