# INSTALLATION_LOG — 安装记录

规则：每安装一个核心组件 → 记录版本/位置/命令/测试结果/问题/解决。

## 2026-08-13~14 基础工具链

### Python 3.12.10
- 位置：%LOCALAPPDATA%\Programs\Python\Python312
- 命令：winget install --id Python.Python.3.12（脚本内执行）
- 测试：`python --version` → Python 3.12.10 ✅
- 问题：系统自带 WindowsApps 占位符不可用；解决方案：winget 装真实 Python，脚本内用全路径调用。

### pip 工具包（Tsinghua 镜像）
- 命令：`python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pymupdf python-docx openpyxl python-pptx pillow pandas opencv-python faster-whisper yt-dlp`
- 版本：pymupdf 1.28.2 / python-docx 1.2.0 / openpyxl 3.1.5 / pandas 3.0.5 / python-pptx 1.0.2 / pillow 12.3.0 / opencv-python 5.0.0.93 / faster-whisper 1.2.1 / yt-dlp 2026.07.04
- 测试：逐个 import 通过 ✅（faster_whisper 首次导入约 4 秒）
- 问题：直连 PyPI 15 分钟超时；解决：清华镜像，2 分 22 秒装完。

### FFmpeg / FFprobe 9.0.1
- 位置：C:\ffmpeg\bin（已加用户 PATH）
- 命令：官网 zip → Expand-Archive → 复制 bin → PATH
- 测试：`ffmpeg -version` / `ffprobe -version` ✅
- 问题1：GitHub Release 被墙（winget 下载 0x80072efd）；解决：官网 gyan.dev 直连。
- 问题2：官网单线程下载 15 分钟中断；解决：自写断点续传脚本（HTTP Range，后台运行），2.5 分钟续传完成。

### ImageMagick 7.1.2-29
- 位置：%LOCALAPPDATA%\ImageMagick（已加用户 PATH）
- 命令：download.imagemagick.org 下载 → `/VERYSILENT /NORESTART /DIR=...` 静默安装
- 测试：`magick -version` ✅
- 问题：GitHub 包被墙；解决：官网 binaries 目录直连（24MB，10 秒下完）。

### Git 仓库（AI-MEDIA-OS）
- 命令：git init + 本地 user.name/email + 首次提交
- 测试：`git log --oneline` ✅（root commit f919295）

## 2026-08-14 第一阶段（进行中）

### Playwright（待装，见下方补记）
- 计划：npm.cmd + npmmirror 安装 playwright，浏览器二进制用镜像下载。

### ComfyUI（评估结论：不装）
- 原因：GTX 1050 2GB 显存不满足 SDXL（≥8GB）要求；见 AI_WORKSTATION_REPORT.md 云端方案。

### 统一视频分析工具（本阶段新增）
- 位置：tools/video_analysis.py
- 测试：用 ffmpeg 合成测试视频，跑 info/frames/audio/shots/hook/report 全流程。

### Playwright（浏览器自动化）
- 位置：tools/browser/（package.json + node_modules + .browsers/）
- 命令：`npm.cmd install playwright --registry=https://registry.npmmirror.com`
  + `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/ npx playwright install chromium`
- 版本：playwright 最新稳定版（npm 安装）
- 测试：`node test.js` → 无头 Chromium 打开页面并读取文本 ✅
- 问题：npm 官方源超时；解决：npmmirror 源 + 镜像下载，4 秒装包、69 秒下浏览器。

### 验收测试（2026-08-14）
- 图片读取（Pillow）：PASS
- PDF 读取（PyMuPDF）：PASS（中文需 fontname="china-s"）
- Word（python-docx）：PASS
- Excel（openpyxl）：PASS
- pandas：PASS
- 视频元数据/抽帧/音频提取（video_analysis.py）：PASS
- Whisper 真实中文语音转写（Windows Huihui TTS 合成 + tiny 模型）：PASS（同音字误差属 tiny 模型正常水平，生产用 base/small）
- 浏览器自动化（Playwright）：PASS
- Git（init/commit/status）：PASS
- ComfyUI：未安装（GTX 1050 2GB 不适合，已评估，见报告云端方案）

> 已知待办：Playwright MCP 需写入 ~/.codex/config.toml（沙箱外执行）：
> `codex mcp add playwright -- npx -y @playwright/mcp@latest`

> 本文件由主 Codex 维护，随每个组件安装即时更新。
