# 样片测试计划

template: render-sample-plan

## 1. 样片优先
批量生成前先生成 1-2 条代表性样片。样片通过后再批量，避免一次性消耗大量积分。

## 2. 推荐样片
| 样片 | 类型 | 对应单元 | 为什么选它 | 通过标准 |
| --- | --- | --- | --- | --- |
| SAMPLE-01 | 动作类 | SD-S05 | 走位和物理动作最复杂 | 主体动作完成、结构不漂、故事板走位基本一致 |
| SAMPLE-02 | 情绪类 | SD-S17 | 微表情和台词节奏关键 | 表情递进自然、台词落点正确、镜头稳定 |

## 3. 样片审核
| 项目 | PASS 标准 | FAIL 后处理 |
| --- | --- | --- |
| 动作完成度 | 主体从开始状态到结束状态 | 回到 motion prompt 或故事板返修 |
| 引用一致性 | 角色、场景、道具与 reference_index 一致 | 检查 @引用用途和参考图数量 |
| 节奏 | 前后 0.5 秒安全区成立 | 调整分时段和动作密度 |
| 声音 | 音频/环境声/台词节奏匹配 | 修正 @音频 用途 |

## 4. Project Packet Updates
```json
{
  "render_plan": {
    "batch_policy": "sample_first",
    "sample_units": ["SD-S05", "SD-S17"],
    "batch_allowed": false
  },
  "sample_review": {
    "status": "pending",
    "next_action": "render SAMPLE-01"
  }
}
```
