# AI-MEDIA-OS

本机 AI 自媒体生产工作站。面向小红书/抖音/快手运营、AI 电影与短剧制作、
图文音视频处理、市场研究与数据分析。

## 快速导航

- 环境报告：[AI_WORKSTATION_REPORT.md](AI_WORKSTATION_REPORT.md)
- 安装日志：[INSTALLATION_LOG.md](INSTALLATION_LOG.md)
- 系统状态：[SYSTEM_STATUS.md](SYSTEM_STATUS.md)
- 项目约定：[AGENTS.md](AGENTS.md)
- 项目状态：[STATUS.md](STATUS.md)

## 目录

| 目录 | 用途 |
| --- | --- |
| skills/ | 自媒体/AI 创作技能（每个含输入/输出/流程/工具/质检/失败处理） |
| agents/ | 子代理定义（研究、策略、编剧、导演、视觉、视频分析、数据分析、开发） |
| tools/ | 可复用工具脚本（视频分析器、文件处理等） |
| workflows/ | 端到端工作流（脚本→分镜→成片→发布复盘等） |
| prompts/ | 常用提示词模板（分镜、封面、选题、复盘等） |
| scripts/ | 一次性/维护脚本 |
| configs/ | 模型路由、Provider 配置、环境变量模板 |
| database/ | 本地结构化数据（选题库、内容库、竞品库） |
| accounts/ | 账号档案：account_registry.md 为唯一登记处 |
| strategy/ | 账号策略 / 商业化 / 实验计划 |
| assets/ | 图片 / 视频 / 音频 / 音乐 / 字体素材 |
| scenes/ | 场景设定与参考图 |
| storyboards/ | 分镜脚本 |
| analytics/ | AI 成本账本（ai_costs.csv）与数据复盘 |
| references/ | 参考资料、平台规范、竞品存档 |
| characters/ | 角色设定与一致性资产 |
| projects/ | 每个具体项目的独立工作目录 |
| outputs/ | 最终交付物（成片、封面、报告） |
| temp/ | 临时文件（不入库） |
| logs/ | 运行日志（不入库） |

## 安全原则

- API Key / 密码 / Cookie 一律走环境变量，绝不提交 Git。
- 发布、付款、账号修改、删除等高风险操作必须先人工确认。
- 安装组件先检查环境，装一个测一个，记录到 INSTALLATION_LOG.md。
