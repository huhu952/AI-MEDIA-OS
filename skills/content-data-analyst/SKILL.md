---
name: content-data-analyst
description: 内容数据分析：阅读、互动、涨粉、完播等指标复盘与下期优化。Use when the user has content performance data and wants analysis or optimization suggestions.
---

# 内容数据分析

## 输入
- 数据源：Excel/CSV 导出、平台后台截图/表格，或用户口述数字
- 指标口径：播放/阅读、点赞、评论、收藏、分享、涨粉、完播率

## 输出
- 数据清洗后的标准表（database/content_stats.csv）
- 分析报告：关键指标趋势、Top/Bottom 内容、相关性观察
- 下期优化建议（每条对应一个数据证据）

## 执行流程
1. 核对口径：明确时间范围、指标定义（完播=多少比例？），避免算错。
2. 清洗数据：统一列名与格式，去重，标缺失。
3. 计算核心指标：互动率=(赞+评+藏+转)/播放；涨粉效率=涨粉/播放。
4. 找规律：按内容类型/发布时间/标题类型分组对比。
5. 结论先行：3-5 条洞察，每条附数据与建议动作。
6. 存档：更新 database/content_stats.csv 与 reports。

## 调用工具
- pandas / openpyxl：数据处理
- python-pptx / python-docx：报告输出
- web-research：行业基准对比
- xiaohongshu-content 等：落地优化建议

## 质量检查
- [ ] 指标口径有明确定义
- [ ] 每个结论有对应数据
- [ ] 区分相关性与因果
- [ ] 建议可执行（具体到内容类型/标题/时间）
- [ ] 原始数据与清洗后数据都可追溯

## 失败处理
- 数据缺失：标注缺失范围，不硬算；优先分析完整子集。
- 样本太小（<5 条）：明确说明不可靠，只给方向不给结论。
- 指标口径不同：先统一口径再分析，避免跨期错比。
