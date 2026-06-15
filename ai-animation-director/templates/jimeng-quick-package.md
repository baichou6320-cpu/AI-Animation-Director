# Jimeng Quick Package Compatibility Template

即梦 Quick Mode 现在默认启用智能画布。

生成 Quick Mode 时使用同目录下的：

- `jimeng-canvas-package.md`

兼容规则：

- 保留 `IMG-REF`、`IMG-Sxx`、`VID-Sxx` 编号。
- 6 镜以内使用“逐镜头执行卡”，把画布关键帧、`IMG-Sxx` 导出和 `VID-Sxx` 放在一起。
- 制作开始后使用 `jimeng-continue-card.md`，每次只返回下一步。
- `Prompts Only` 不显示画布布局或 `CV-OP-*` 操作卡。
- 非即梦项目继续使用普通生图提示词结构。
