---
name: content-repurposer
description: 内容复用：把一篇长文/一个视频拆成多平台、多形态的内容矩阵。Use when the user wants to reuse existing content across platforms and formats.
---

# 内容复用

## 输入
- 源内容：长文、视频、直播回放、播客转写
- 可选：目标平台清单与各平台侧重

## 输出
- 内容矩阵表（平台 × 形态 × 角度 × 标题）
- 各形态草稿：图文笔记、短视频脚本、图文卡片、金句图、问答贴
- 发布排期建议

## 执行流程
1. 提炼核心资产：观点、数据、故事、金句（每个都能单独成内容）。
2. 按平台拆形态：抖音→短视频脚本；小红书→图文笔记；快手→真实感口播；公众号→长文。
3. 每平台换角度：同样素材，标题和开头按平台人群重写。
4. 生成金句卡片与封面（visual-agent）。
5. 排期：避免同一天全平台首发，先主平台验证再铺开。

## 调用工具
- faster-whisper：视频/直播转文字提取素材
- tools/video_analysis.py：视频切精华片段
- ai-screenwriter：脚本改写
- xiaohongshu-content / douyin-content / kuaishou-content：各平台成稿
- visual-agent / scene-visualizer：封面与金句图

## 质量检查
- [ ] 每个平台版本标题与开头针对该平台人群重写过（非复制粘贴）
- [ ] 至少提炼 3 个可独立使用的核心资产
- [ ] 金句卡片文字无错别字
- [ ] 视频切片时长适合目标平台
- [ ] 发布排期有主次

## 失败处理
- 素材太少拆不动：先补充 2-3 个具体案例/数据点。
- 跨平台效果差：复盘各平台数据（content-data-analyst），砍掉无效形态。
- 转写质量差：换 base/small 模型或人工校对关键句。
