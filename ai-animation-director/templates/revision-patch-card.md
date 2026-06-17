# 改稿补丁：[一句话目标]
<!-- template: revision-patch-card; delivery_mode: revision -->

改稿类型：`[shot_patch | style_tune | duration_resize | aspect_ratio_change | platform_switch | prompt_simplify | asset_replace | other]`
影响范围：`[IMG-Sxx]`、`[VID-Sxx]`

## 保留不变
- `[不受影响的资产或镜头编号]`

## 替换内容
### [IMG-Sxx / ASSET-* / 全局锚点]
复制提示词：
```text
[只放本次替换提示词或锚点文本]
```

### [VID-Sxx，如适用]
使用图片：`[IMG-Sxx]`
复制提示词：
```text
[只放本次替换视频提示词]
```

## 完成检查
- [检查点 1]
- [检查点 2]
- [检查点 3]

## 状态更新
```json
{
  "current_step": "[IMG-Sxx]",
  "next_action": "regenerate [IMG-Sxx]",
  "revision": {
    "mode": "[revision_mode]",
    "affected_ids": ["[IMG-Sxx]", "[VID-Sxx]"],
    "preserved_ids": []
  }
}
```

完成后回复：`[IMG-Sxx] 已更新，继续`
