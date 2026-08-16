# 内容实验数据库

目的：记录每个作品从生产到数据回传的全过程，逐步回答：

- 什么题材最容易获得播放？
- 什么 Hook 留存最好？
- 什么角色最容易涨粉？
- 什么视频模型成功率最高、单位成本最低？
- 什么类型值得继续？什么类型应该停止？

## 文件

| 文件 | 说明 |
| --- | --- |
| `schema.sql` | 表结构定义（入库文件） |
| `content_experiments.sqlite` | 实际数据库（`init` 生成，不入 Git） |
| `content_experiments_template.csv` | 手工录入模板（含 1 行示例，导入前删除） |

## 使用

```bash
python scripts/content_db.py init                                            # 初始化数据库
python scripts/content_db.py import database/content_experiments_template.csv # 导入 CSV
python scripts/content_db.py export --out database/content_experiments_backup.csv  # 导出
python scripts/content_db.py stats                                          # 基础统计
python scripts/content_db.py list                                           # 列出全部
```

## 字段与单位（数据字典）

| 字段 | 说明 | 单位/取值 |
| --- | --- | --- |
| content_id | 作品唯一 ID（建议 P001-20260816） | 文本 |
| platform | 平台 | douyin / kuaishou / short_drama |
| publish_date | 发布日期 | YYYY-MM-DD |
| series | 所属系列 | 文本 |
| topic | 题材 / 选题 | 文本 |
| content_type | 内容类型（竖屏短视频 / 图文 / 短剧集等） | 文本 |
| duration | 成片时长 | 秒 |
| hook_type | Hook 类型（悬念提问 / 冲突开场 / 利益前置 / 视觉冲击等） | 文本 |
| visual_style | 视觉风格（写实3D / 2D动画 / 真人感 / 纪录片等） | 文本 |
| characters | 出现角色 | 分号分隔 |
| generation_models | 使用的生成模型 | 分号分隔 |
| image_generation_count | 生图次数 | 次数 |
| video_generation_count | 生视频次数 | 次数 |
| failed_generation_count | 失败 / 废弃次数 | 次数 |
| estimated_image_cost | 生图成本 | 元 |
| estimated_video_cost | 生视频成本 | 元 |
| estimated_audio_cost | 配音 / 音乐 / 音效成本 | 元 |
| total_cost | 总成本（= 前三者之和） | 元 |
| production_time | 制作耗时 | 分钟 |
| views / likes / comments / shares / favorites | 播放 / 点赞 / 评论 / 转发 / 收藏 | 数值 |
| followers_gained | 净涨粉 | 数值 |
| three_second_retention | 3 秒留存 | % |
| completion_rate | 完播率 | % |
| revenue | 收入（收益 / 广告 / 带货等） | 元 |
| notes | 备注（异常、经验、失败原因） | 文本 |

## 数据纪律

- 数据缺失用空值，**不编造**。
- 发布后由用户提供平台后台数据，Codex 负责录入、清洗、比较、统计与复盘。
- 成本字段与 `analytics/ai_costs.csv` 互相印证：单次调用看账本，作品级合计看本库。
