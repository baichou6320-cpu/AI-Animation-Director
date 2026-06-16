# 失败诊断：重试当前步骤
<!-- template: failure-diagnosis-card; delivery_mode: continue; continue_submode: failure_repair -->

失败步骤：`[VID-Sxx / IMG-Sxx / CV-OP-xx]`
失败类型：`[character_drift | style_drift | motion_error | camera_error | deformation | composition_error | lighting_error | duration_mismatch | generation_blocked | timeout | other]`

## 可见症状
- [用户看到的问题 1]
- [用户看到的问题 2]

## 可能原因
- [最可能原因]

## 修复策略
- [保留项]
- [简化项]
- [重试时只改变的一件事]

## 重试提示词
使用图片：`[IMG-Sxx，如适用]`
复制提示词：
```text
[只放本次重试要复制的提示词]
```

## 完成检查
- [检查点 1]
- [检查点 2]
- [检查点 3]

## 状态更新
```json
{
  "failed_step": "[VID-Sxx]",
  "failure_records": [{"step": "[VID-Sxx]", "type": "[failure_type]", "symptom": "[short symptom]"}],
  "next_action": "retry [VID-Sxx]"
}
```
