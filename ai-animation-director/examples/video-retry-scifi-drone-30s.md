# 视频失败重试：科幻无人机 30 秒短片
<!-- delivery_mode: continue; continue_submode: failure_repair; generation_strategy: single_image_per_shot -->

诊断：原任务请求 30 秒、引用三个不同场景，实际只输出 10 秒，主要升空与抵达动作没有完成。

失败类型：`duration_mismatch`、`under_motion`、`reference_confusion`

处理：保留三张关键帧，将一次多图任务拆成三个独立图生视频任务，每段约 10 秒。

## VID-S01 机库启动并升空
使用图片：`IMG-S01`
复制提示词：
```text
使用 IMG-S01 作为首帧。主要动作：WX-7 无人机启动四个旋翼，随后从充电底座平稳升起约半个机身高度，结尾稳定悬停。摄影机缓慢向前推进。门外雨线轻微移动。保持机身结构、四旋翼、传感器、底座、机库空间和冷蓝光线不变。避免只转旋翼却不起飞、突然冲出机库、机臂增减、机身变形、镜头摇晃、文字水印。
```
失败后改法：固定摄影机，只保留无人机从底座升高到稳定悬停。

## VID-S02 离开气象站
使用图片：`IMG-S02`
复制提示词：
```text
使用 IMG-S02 作为首帧。主要动作：WX-7 无人机从平台上方稳定悬停开始，沿海岸方向缓慢向前飞行，结尾接近画面远处灯塔方向。摄影机从侧后方轻柔跟随。水洼只产生一圈轻微下洗波纹。保持无人机结构、气象站、海岸线、灯塔位置和黎明光向不变。避免原地悬停、突然加速、翻滚、快速环绕、海岸变形和场景切换。
```
失败后改法：固定摄影机，让无人机只做清楚、缓慢的前向位移。

## VID-S03 报告送达
使用图片：`IMG-S03`
复制提示词：
```text
使用 IMG-S03 作为首帧。主要动作：WX-7 无人机保持稳定悬停，琥珀状态灯闪烁一次后转为长亮，表示天气报告已经送达。摄影机极慢向后拉远，结尾完整展现灯塔、礁石和海面。云层只做轻微散开。保持无人机结构、灯塔、接收设备、海岸地形和日出方向不变。避免可见电波、全息界面、无人机冲向镜头、结构漂移、太阳过曝和文字水印。
```
失败后改法：固定无人机，只做状态灯变化和极慢拉远。

## 状态更新
```json
{
  "failed_step": "VID-ALL",
  "failure_records": [
    {"step": "VID-ALL", "type": "duration_mismatch", "symptom": "requested 30s, actual 10s"},
    {"step": "VID-ALL", "type": "under_motion", "symptom": "takeoff and arrival did not complete"},
    {"step": "VID-ALL", "type": "reference_confusion", "symptom": "three different scenes were supplied to one task"}
  ],
  "video_execution": {"generation_strategy": "single_image_per_shot", "requested_duration_seconds": 30, "actual_duration_seconds": 10, "reference_count": 3},
  "shot_tasks": {
    "VID-S01": {"source_image": "IMG-S01", "requested_duration_seconds": 10, "actual_duration_seconds": null, "retry_count": 0},
    "VID-S02": {"source_image": "IMG-S02", "requested_duration_seconds": 10, "actual_duration_seconds": null, "retry_count": 0},
    "VID-S03": {"source_image": "IMG-S03", "requested_duration_seconds": 10, "actual_duration_seconds": null, "retry_count": 0}
  },
  "next_action": "retry VID-S01"
}
```
