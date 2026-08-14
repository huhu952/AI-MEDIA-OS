# API 统一路由架构（AI-MEDIA-OS）

## 目标

不让系统锁死在某一家 AI 厂商。未来可平滑接入：OpenAI、国内大模型、图像生成、
视频生成、TTS、STT、搜索服务、本地模型与云端 ComfyUI。换模型/换厂商时，
只改配置，不改业务代码。

## 分层

```text
Client（技能/工作流/主 Codex）
        │
        ▼
Model Router（路由层：按能力类型 + 配置选 Provider）
        │
        ▼
Provider Adapter（适配层：统一请求/响应格式）
        │
        ▼
Backend（OpenAI / DeepSeek / 本地 Whisper / ComfyUI ...）
```

## 路由规则

1. 按能力类型路由：chat / image / video / tts / stt / search。
2. 按配置选择默认 Provider；失败时按 fallback 顺序切换。
3. 模型名与参数不写死在业务代码，统一从
   `configs/model-router.example.json`（或环境变量）读取。

## Provider 接入方式

1. 在 `model-router.example.json` 增加 provider 条目（name/type/endpoint/env_key/model）。
2. 在 `.env` 设置对应 API Key。
3. 在 Adapter 层实现该提供商的请求/响应转换（响应统一为：
   文本 → string；图像 → 文件路径/URL；视频 → 文件路径/URL；STT → segments 列表）。
4. 跑最小测试，更新 INSTALLATION_LOG.md。

## 密钥管理

- 所有密钥只存在于环境变量或系统密钥管理器中，禁止写死在代码。
- `.env` 不入 Git（.gitignore 已配置）；提交模板用 `.env.example`（仅占位符）。
- 轮换密钥：改环境变量即可，无需改代码。
- 泄露处理：立即吊销旧 Key 并更换，检查日志是否残留。

## 成本控制

- 每个请求记录：模型、token/文件大小、耗时、费用估算（如 API 提供用量）。
- 高成本操作（视频生成、大批量生图）先给用户报价/确认再执行。
- 设置月度预算提醒；批量任务拆小批执行。

## 错误处理与回退

- 超时/限流：指数退避重试（默认 3 次）。
- 服务不可用：按 fallback 切备用 Provider，并在结果中标注实际使用方。
- 参数错误：不重试，返回错误说明。
- 记录失败日志到 logs/，供复盘。

## 为什么不在代码中硬编码密钥

硬编码会导致：Git 历史泄露、多环境无法切换、轮换困难、协作风险。
统一走环境变量是行业标准做法，也是本项目的安全红线。
