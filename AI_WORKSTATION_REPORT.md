# AI_WORKSTATION_REPORT — AI-MEDIA-OS 环境基线

生成日期：2026-08-14
检测方式：PowerShell/.NET/nvidia-smi/registry（沙箱禁用了 WMI，部分数据以替代来源确认）

## 1. 硬件

| 项目 | 数值 | 评价 |
| --- | --- | --- |
| CPU | Intel Core i5-7300HQ @ 2.50GHz（4C/8T，Kaby Lake） | 2017 年笔记本级，够用但偏弱 |
| GPU | NVIDIA GeForce GTX 1050，显存 2048 MiB（2GB），算力 6.1，驱动 560.76 | **本地跑扩散模型/视频生成不可行** |
| 内存 | 总 7.9GB，可用约 1.3GB | **明显偏紧**，多任务需注意 |
| 磁盘 C: | 104GB 总量 / 16.7GB 空闲 | 紧，避免往 C 盘装大件 |
| 磁盘 D: | 310GB / 208.3GB 空闲 | 建议作为项目/媒体主盘 |
| 磁盘 E: | 310.8GB / 75.1GB 空闲 | |
| 磁盘 F: | 310.7GB / 161.9GB 空闲 | |
| 磁盘 G: | 13.9GB / 2.1GB 空闲 | 容量小 |

## 2. 操作系统与运行时

| 组件 | 版本/状态 | 位置 |
| --- | --- | --- |
| Windows | 10 22H2（build 19045），AMD64 | - |
| Python | 3.12.10 ✅ | %LOCALAPPDATA%\Programs\Python\Python312 |
| Node.js | 24.19.0 ✅ | C:\Users\administered\.ai-manager\runtimes\node\24.19.0 |
| npm | 随 Node ✅ | 同上（ps1 包装受执行策略限制，需用 npm.cmd） |
| Git | 2.55.0.windows.1 ✅ | C:\Users\administered\AppData\Local\Programs\Git |
| winget | ✅ | WindowsApps |
| CUDA Toolkit | **12.6 已安装** ✅（nvcc 可用） | 系统 |
| NVIDIA 驱动 | 560.76（支持 CUDA 12.x） | - |
| Docker | ❌ 未安装 | 需 WSL2/虚拟化，见建议 |
| WSL | 存在但当前会话访问被拒 | 需在正常终端确认状态 |
| 7-Zip | ❌ 未安装 | 可选 |
| cmake | ❌ 未安装 | 编译源码时才需要 |

## 3. 已装工具链（本工作站核心）

| 工具 | 版本 | 用途 |
| --- | --- | --- |
| FFmpeg / FFprobe | 9.0.1 ✅ | 视频切割/抽帧/音频/转码/合并 |
| ImageMagick | 7.1.2-29 ✅ | 批量图片处理（magick） |
| yt-dlp | 2026.07.04 ✅ | 公开内容下载（限有权/平台允许） |
| faster-whisper | 1.2.1 ✅ | 语音转文字（首次用需下载模型） |
| PyMuPDF | 1.28.2 ✅ | PDF |
| python-docx | 1.2.0 ✅ | Word |
| openpyxl | 3.1.5 ✅ | Excel |
| pandas | 3.0.5 ✅ | 数据分析 |
| python-pptx | 1.0.2 ✅ | PPT |
| Pillow | 12.3.0 ✅ | 图片 |
| OpenCV | 5.0.0.93 ✅ | 图片/视频帧分析 |

## 4. 缺失组件与潜在冲突

### 缺失
- Playwright / 浏览器自动化（第一阶段补装）
- ComfyUI（见第 5 节，本地不建议装）
- Docker（可选；装 WSL2 需系统级操作，待确认）
- 7-Zip、cmake（按需）

### 潜在冲突与风险
1. **内存吃紧**：8GB 总内存、当前可用仅约 1.3GB。同时开浏览器 + 编辑器 + 转码 + 转录会卡顿/崩溃，建议先关后台程序，或后续加内存。
2. **C 盘空间**：仅 16.7GB 空闲。Python 已装在用户目录（约几百 MB），继续扩大时应把项目、缓存、模型放 D/F 盘。
3. **执行策略**：本机 PowerShell 默认禁止运行 .ps1（我们已用 Bypass/RemoteSigned 处理），后续脚本统一带 `-ExecutionPolicy Bypass`。
4. **HuggingFace 访问**：faster-whisper 模型默认从 HF 下载，国内慢/不稳定，用 `HF_ENDPOINT=https://hf-mirror.com`。
5. **npm/PyPI 网络**：官方源慢，建议 npm 用 npmmirror、pip 用清华镜像（本次安装已验证清华 pip 镜像速度 14-17MB/s）。
6. **GitHub 被墙**：FFmpeg/ImageMagick 官方包在 GitHub，本次已用官网直连+断点续传解决；后续下载优先官网或国内镜像。
7. **Codex 当前主模型 DeepSeek V4 仅文本**：图片识别受限；需要原生看图时切到支持 image 的模型（如 gpt-5.6-terra）。

## 5. ComfyUI 评估（结论：本地不部署）

### 依据
- GTX 1050 仅 2GB 显存：SDXL 需要 ≥8GB，SD 1.5 低显存模式约 4GB 起（2GB 勉强且极慢），视频/角色一致性模型要求更高。
- Pascal 架构（算力 6.1）对新模型优化支持差。
- 8GB 内存 + 笔记本散热，长任务不稳。

### 本地方案（暂不执行）
若未来升级到 RTX 4060（8GB）以上，再按框架→模型→测试顺序部署 ComfyUI。

### 云端方案（推荐，供你选择）
| 平台 | 特点 | 适合 |
| --- | --- | --- |
| AutoDL / 恒源云（国内） | 按小时租 GPU，性价比高，中文文档 | 常用、长期跑图 |
| RunPod / Vast.ai | 按秒计费，模板多 | 偶尔大批量 |
| Replicate / fal.ai | API 调用，无需管理机器 | 直接接 API Router |
| 火山引擎/阿里云百炼 | 国内合规、有生图/视频 API | 生产级接入 |

## 6. 建议的下一步（按优先级）
1. 第一阶段补装 Playwright + 浏览器自动化测试
2. 建立统一视频分析工具并完成验收测试
3. 完善 10 个技能与 8 个子代理（本次并行进行）
4. 确定云端生图/视频服务并接入 API Router
5. 建立选题库/内容库（database/）与复盘工作流

## 7. 安全红线
- API Key/密码/Cookie 只放环境变量，永不入 Git。
- 发布、付款、账号修改、删除等高风险操作必须先人工确认。
- 系统级修改（Docker/WSL2、驱动、注册表、PATH 系统级）先询问。
