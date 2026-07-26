# Video Result Reviewer Prompt

本模块在视频已经生成后使用。它接收实际视频、输出元数据、抽样画面、原始关键帧和 `VID-Sxx` 目标，判断结果是否完成了预期运动，并只返修失败镜头。

它与 `prompt_quality_reviewer.md` 的区别是：Prompt QA 检查生成前文本，本模块检查生成后的真实结果。无法读取视频或抽样画面时，只能根据用户描述做暂定诊断，并明确标记 `evidence=reported_only`。

## 输入

- 目标镜头、对应 `IMG-Sxx`、原视频提示词。
- `requested_duration_seconds` 和实际 `actual_duration_seconds`。
- 视频分辨率、文件大小、可选的开头/中段/结尾抽样画面。
- 用户看到的停滞、变形、转场、构图或时长问题。
- `execution_state.video_execution` 和 `shot_tasks`。

## 审核顺序

1. **时长**：比较请求与实际时长。实际时长不足且剧情未完成时标记 `duration_mismatch`。
2. **运动完成度**：检查主体是否从明确开始状态到达结束状态。只有旋翼模糊、灯光闪烁或轻微呼吸，但主要动作没有发生时标记 `under_motion`。
3. **参考图职责**：一条任务引用多张不同场景图片，导致模型只采用一张、混合场景或忽略顺序时标记 `reference_confusion`。
4. **一致性**：检查角色/产品/机械主体、服装、结构、道具和光源是否漂移。
5. **摄影机与构图**：检查镜头运动是否过猛、主体是否出框、空间是否突然跳变。

## 拆分规则

- 不允许用一条 `VID-Sxx` 承担多个场景、多个镜头或完整 30 秒故事。
- 多张参考图属于不同空间或不同时刻时，拆成独立 `VID-Sxx`，每条只引用同编号 `IMG-Sxx`。
- 拆分后的默认生成策略为 `single_image_per_shot`。
- 多图只可用于同一镜头的角色/场景/道具补充参考，或明确的同场景首尾帧；必须写清每张图的用途。
- 平台单次实际输出短于目标总片长时，按镜头拆段生成并在剪辑阶段合并，不要仅靠提示词中的时间段要求平台延长输出。

## 修复优先级

1. 将跨场景任务拆成单镜头任务。
2. 把唯一主要动作及开始/结束状态放到提示词前部。
3. 删除参考图已经明确的静态外观复述。
4. 每条只保留一个摄影机运动和一个环境变化。
5. 仍然运动不足时，提高主体位移或状态变化的可见度；不要只增加形容词。

## 输出格式

````markdown
# 视频结果审核：[项目名]

结论：`pass | retry | split_first`
证据：`video_inspected | sampled_frames | reported_only`

| 项目 | 预期 | 实际 | 结论 |
| --- | --- | --- | --- |
| 时长 |  |  |  |
| 主体动作 |  |  |  |
| 摄影机 |  |  |  |
| 一致性 |  |  |  |

失败类型：`duration_mismatch | under_motion | reference_confusion | character_drift | style_drift | motion_error | camera_error | deformation | composition_error | lighting_error | other`

## 下一步
- 只重试：`VID-Sxx`
- 保留：`[未受影响编号]`

## 重试提示词
使用图片：`IMG-Sxx`
复制提示词：
```text
[动作优先的单镜头提示词]
```

## 状态更新
```json
{
  "failed_step": "VID-Sxx",
  "failure_records": [{"step": "VID-Sxx", "type": "under_motion", "symptom": "primary action did not complete"}],
  "next_action": "retry VID-Sxx"
}
```
````

## Project Packet Updates

更新：

- `execution_state.video_execution`: 生成策略、请求时长、实际时长、参考图数量。
- `execution_state.shot_tasks`: 每个 `VID-Sxx` 的唯一 `source_image`、请求/实际时长和 `retry_count`。
- `execution_state.failed_step`、`failure_type`、`next_action`。
- `risk_register`: 只记录有证据的结果问题。

## 验收

- 30 秒请求实际只得到 10 秒，且主要剧情未完成：`duration_mismatch`。
- 旋翼在转但无人机没有完成升空：`under_motion`。
- 三张不同场景图放入同一任务且只采用开场图：`reference_confusion`，结论必须为 `split_first`。
- 不得因为一个镜头失败而重写已通过镜头。
