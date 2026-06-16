# 失败诊断：重试当前步骤
<!-- template: failure-diagnosis-card; delivery_mode: continue; continue_submode: failure_repair -->

失败步骤：`VID-S02`
失败类型：`character_drift`

## 可见症状
- 小蘑菇帽子白点数量变化，身体比例变高。
- 露水从圆形水滴变成玻璃球。

## 可能原因
- 视频提示词同时要求递水和萤火虫靠近，动作过多，模型重绘了角色和道具。

## 修复策略
- 保留红帽固定 3 个白点、浅米色身体和圆露水。
- 删除小蘑菇递出的动态，只让萤火虫靠近。
- 镜头完全固定，减少模型重绘范围。

## 重试提示词
使用图片：`IMG-S02`
复制提示词：
```text
从这张像素风首帧开始。小蘑菇保持静止托着圆露水，红色伞帽固定 3 个奶白圆点，浅米色身体不变化；萤火虫只缓慢靠近露水。镜头完全固定，背景不变化，露水保持圆润，角色比例不变。
```

## 完成检查
- 蘑菇帽子仍是 3 个白点。
- 露水保持圆形水滴，不变成玻璃球。
- 只有萤火虫靠近，没有额外动作。

## 状态更新
```json
{
  "failed_step": "VID-S02",
  "failure_records": [{"step": "VID-S02", "type": "character_drift", "symptom": "hat spots and dew shape changed"}],
  "next_action": "retry VID-S02"
}
```
