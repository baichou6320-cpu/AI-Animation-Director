# 关键帧确认：敦煌壁画中的夜行信使

delivery_mode: keyframe_review
concept_approval: approved
keyframe_approval: pending

## 当前候选资产
| 编号 | 用途 | 状态 | 查看/生成方式 |
| --- | --- | --- | --- |
| `REF-CHAR-A` | 少年信使角色参考 | candidate | generated |
| `REF-SCENE-A` | 夜色洞窟外景参考 | candidate | generated |
| `IMG-S01` | 信使护住灯火的开场关键帧 | candidate | generated |
| `IMG-S02` | 微光唤醒色彩的转折关键帧 | candidate | generated |

## 已继承的方向
- 角色：虚构少年信使，简洁剪影轮廓，手中暖色灯火是唯一高亮锚点。
- 场景：夜色、赭石岩壁、克制的装饰性色带，不复制具体壁画人物。
- 光影：深靛环境色与暖琥珀灯光对比，光线从低位向脸部和岩壁扩散。

## 请重点检查
- 少年年龄、服装轮廓和灯具是否符合已确认方向。
- 场景是否具有敦煌地域与矿物色感，同时没有复刻具体壁画。
- `IMG-S01`、`IMG-S02` 构图是否留有缓慢横移或推近空间。

## 你可以回复
- `关键帧确认`：批准候选资产并开始视频生产。
- `只改 IMG-S02：色彩醒来的范围更克制`：仅返修该关键帧。

未确认前不生成视频。

```json
{
  "approval_state": {"concept_approval": "approved", "keyframe_approval": "pending", "approval_override": false},
  "approved_assets": [],
  "candidate_assets": ["REF-CHAR-A", "REF-SCENE-A", "IMG-S01", "IMG-S02"],
  "execution_state": {"next_action": "await_keyframe_approval"}
}
```
