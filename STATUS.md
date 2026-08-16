# STATUS — AI-MEDIA-OS 项目状态

更新日期：2026-08-16
维护：Codex（每次完成重要建设后更新）

## 当前阶段

Phase 0：基础建设阶段（禁止发布、禁止大量付费调用、禁止养号类自动化）。

## 已完成事项

- 环境基线（2026-08-13~14）：Python 3.12 / Node 24 / FFmpeg 9 / ImageMagick / yt-dlp /
  faster-whisper / PyMuPDF / python-docx / openpyxl / pandas / python-pptx / Pillow / OpenCV；
  Playwright 浏览器自动化（`tools/browser/`）；统一视频分析器 `tools/video_analysis.py`
  （元数据 / 抽帧 / 音频 / 转写 / 镜头 / Hook / 节奏 / 综合报告）。
- Git 仓库初始化与历史提交；`.gitignore` 覆盖密钥、临时文件、大媒体。
- 10 个 Skills、8 个 Agent 定义；模型路由与密钥模板（`configs/`）；API 架构文档。
- 2026-08-16 基础设施补齐：
  - 目录：accounts / strategy / assets / scenes / storyboards / analytics / outputs 平台子目录
  - `accounts/account_registry.md` 账号档案模板（4 个账号占位）
  - 内容实验库：`database/schema.sql` + 录入模板 CSV + `scripts/content_db.py` + SQLite 空库
  - AI 成本账本：`analytics/ai_costs.csv` + README
  - 生产管线框架：`workflows/SHORT_VIDEO_PIPELINE.md`（13 阶段，仅框架）
  - 本文件 STATUS.md 建立；README / AGENTS.md / validate_project.js 同步更新

## 正在进行

- 账号档案等待回填（抖音主 / 备用、快手、短剧平台，共 4 个账号）。
- 云端生图 / 视频服务商选择（AutoDL / RunPod / Replicate / fal / 火山等）与真实 API Key 接入。
- Playwright MCP 注册（需沙箱外 `codex mcp add`，或继续用本地 `tools/browser/` 方案）。

## 等待用户

1. 账号档案字段（昵称 / 定位 / 实名 / 状态 / 商业化等）。
2. 云端生图 + 视频服务选型与预算（先小额试点，先报价后执行）。
3. API Key（只放环境变量或系统密钥管理器，绝不入仓库）。
4. 首个正式选题方向（与 ChatGPT 协商后下达）。

## 下一步

1. 回填账号档案，确定账号定位。
2. 选定 1 个生图 + 1 个视频服务并接入（小额预算，≤ 数元级别测试，先报价）。
3. 用角色参考图一致性小测试验证 IMAGE 阶段工作流。
4. 建立选题库 / 实验计划（`strategy/experiments/`）。
5. 等待用户与 ChatGPT 定义 Phase 1 首个内容实验。

## 技术问题

- GPU：GTX 1050 2GB → 本地扩散 / 视频模型不可行，走云端 API。
- 内存 8GB（可用约 1.3GB）：多任务易卡，大任务前关闭后台程序。
- C 盘剩余约 16.7GB：大文件放 D / F 盘。
- PowerShell 执行策略阻止 .ps1：使用 npm.cmd / `-ExecutionPolicy Bypass`。
- 国内网络：GitHub / HF / npm / PyPI 需镜像（已配置 npmmirror / 清华 / hf-mirror）。

## 成本风险

- 当前付费调用为 0（未产生）。
- 风险点：视频生成抽卡费用不可控 → 用管线纪律控制（先分镜后生成、失败上限、QC 门禁）。
- 衡量口径：最终可用作品成本，而非单次生成价格。
- 所有生成类调用先记录 `analytics/ai_costs.csv`；高成本任务先报价后执行。
