# AGENTS.md — AI-MEDIA-OS 项目约定

## 角色

主 Codex 是本工作站的主控 Agent，负责：接收任务 → 判断是否拆解 →
按需调用子代理 → 汇总验证 → 交付。子代理定义见 agents/。

## 子代理调用规则

- 每个任务只交给一个最合适的子代理，避免重复劳动。
- 子代理输出必须返回给主代理复核后再交付用户。
- 高风险任务（发布、付款、账号操作、删除、公开推送）主代理不自动执行，
  必须停下询问用户。

## 文件与 Git

- 所有交付物写入 outputs/；中间产物放 temp/；日志放 logs/。
- 禁止把密钥、Cookie、token、.env 提交到 Git。
- 每个里程碑结束运行一次完整测试，并更新 SYSTEM_STATUS.md。

## 工具使用

- 视频/音频：ffmpeg、ffprobe、faster-whisper（见 tools/video_analysis.py）。
- 图片：Pillow、OpenCV、ImageMagick（magick）。
- 文档：PyMuPDF、python-docx、openpyxl、python-pptx、pandas。
- 浏览器自动化：Playwright；仅限用户授权的任务。
- 生图：本机 GPU（GTX 1050 2GB）不适合本地扩散模型，走云端 API；
  ComfyUI 仅在该硬件升级后才考虑本地部署。

## 测试纪律

- 安装新组件：先记录版本与环境，再安装，随后执行最小测试，
  结果写入 INSTALLATION_LOG.md。
- 失败先诊断，禁止用破坏性命令修复 Python/Node/CUDA 环境。

## 内容合规

- yt-dlp 仅用于有权获取或平台允许的内容。
- 生成内容遵守平台规则与版权要求；AI 生成内容按平台要求标注。
