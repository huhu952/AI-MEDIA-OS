---
name: viral-video-analyzer
description: 爆款视频拆解分析：结构、钩子、节奏、镜头、字幕与数据复盘。Use when the user wants to understand why a video went viral or wants to analyze any video.
---

# 爆款视频分析

## 输入
- 视频文件路径（MP4/MOV 等）或链接（yt-dlp 可获取的公开内容）
- 可选：该视频的公开数据（播放/点赞/评论/完播）

## 输出
- 分析报告（markdown）：基本信息、镜头结构、节奏、前 3 秒 Hook、字幕/文案、可复用的爆款公式
- 关键帧与音频文件（可选）

## 执行流程
1. 读取元数据：时长、分辨率、帧率（tools/video_analysis.py info）。
2. 抽关键帧：每 2-5 秒一帧，快速浏览画面信息。
3. 镜头切分：scenecut 检测镜头数与时长分布。
4. 前 3 秒 Hook：亮度/运动/音量/信息密度，判断钩子强度。
5. 节奏分析：平均镜头时长、每分钟切点数，判断节奏快慢。
6. 字幕/文案：Whisper 转写，提炼口播结构与金句。
7. 结论：拆出可复用公式（钩子类型+结构+节奏+文案套路）。

## 调用工具
- tools/video_analysis.py（info/frames/shots/hook/rhythm/transcribe）
- ffmpeg / ffprobe
- faster-whisper（模型建议 base 或 small）
- yt-dlp（仅限有权获取或平台允许的内容）

## 质量检查
- [ ] 基本信息完整（时长/分辨率/码率）
- [ ] 至少 6 张关键帧
- [ ] 镜头数与节奏指标已计算
- [ ] Hook 分析含亮度/运动/音量
- [ ] 转写文本非空且时间轴合理
- [ ] 结论给出可复用的“公式”，而非泛泛而谈

## 失败处理
- 视频打不开：先跑 ffprobe 确认文件完整；损坏则尝试 ffmpeg 修复（-err_detect ignore_err）。
- 转写为空：检查音频是否人声清晰；换 base/small 模型重试。
- yt-dlp 失败：网络/地区限制，改用本地文件分析并说明原因。
