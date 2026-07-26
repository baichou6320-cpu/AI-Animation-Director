# 进化信号待确认

template: evolution-signal-card

## 触发原因
- 来源：用户反馈 / reviewer 发现 / 重复失败 / 平台限制变化
- 相关阶段：director_scene / reference_index / motion_prompt / storyboard / sample_review / output_composer
- 相关编号：

## 可泛化规则
建议新增或修改的规则：

```text
[写成可放进 Skill 的稳定规则，不写一次性项目细节]
```

## 为什么值得加入
- 影响范围：
- 可减少的失败：
- 可能副作用：

## 等待用户确认
回复 `同意进化` 后，才允许把规则写入对应 Skill 文件；回复 `跳过` 则只记录为项目经验，不修改 Skill。

## Project Packet Updates
```json
{
  "evolution_signals": [
    {
      "id": "EV-001",
      "status": "pending_user_approval",
      "source": "reviewer",
      "target_module": "stage_gate_reviewer",
      "rule_summary": "motion prompt 审核必须回看导演讲戏本和原始剧本"
    }
  ],
  "next_action": "await_evolution_approval"
}
```
