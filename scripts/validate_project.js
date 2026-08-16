const fs = require("fs");
const path = require("path");
const root = "C:/Users/administered/Documents/Codex/AI-MEDIA-OS";
const out = [];

const required = ["## 输入", "## 输出", "## 执行流程", "## 调用工具", "## 质量检查", "## 失败处理"];
const skills = fs.readdirSync(path.join(root, "skills")).filter((d) =>
  fs.statSync(path.join(root, "skills", d)).isDirectory());
for (const d of skills.sort()) {
  const p = path.join(root, "skills", d, "SKILL.md");
  if (!fs.existsSync(p)) { out.push("FAIL | skill " + d + " | missing"); continue; }
  const c = fs.readFileSync(p, "utf8");
  const ok = c.startsWith("---\n") && /^name: /m.test(c) && /^description: /m.test(c) &&
    required.every((h) => c.includes(h));
  out.push((ok ? "PASS" : "FAIL") + " | skill " + d);
}

const agentReqs = ["## 角色", "## 职责", "## 输入", "## 输出", "## 调用工具", "## 何时被主代理调用", "## 禁止事项"];
const agents = fs.readdirSync(path.join(root, "agents")).filter((f) => f.endsWith(".md")).sort();
for (const f of agents) {
  const c = fs.readFileSync(path.join(root, "agents", f), "utf8");
  const ok = agentReqs.every((h) => c.includes(h));
  out.push((ok ? "PASS" : "FAIL") + " | agent " + f);
}

try {
  const r = JSON.parse(fs.readFileSync(path.join(root, "configs", "model-router.example.json"), "utf8"));
  out.push("PASS | router json (" + Object.keys(r.router.providers).length + " providers)");
} catch (e) {
  out.push("FAIL | router json: " + e.message);
}

const env = fs.readFileSync(path.join(root, "configs", ".env.example"), "utf8");
out.push((/sk-[A-Za-z0-9]{10,}/.test(env) ? "FAIL" : "PASS") + " | .env.example no real keys");
out.push((env.includes("your-openai-key-here") ? "PASS" : "FAIL") + " | .env.example placeholders ok");

const requiredDirs = [
  "accounts", "strategy", "assets", "scenes", "storyboards", "analytics",
  "database", "workflows", "projects", "characters", "prompts", "references",
  "outputs", "skills", "agents", "tools", "configs", "scripts", "temp", "logs",
];
for (const d of requiredDirs) {
  out.push((fs.existsSync(path.join(root, d)) ? "PASS" : "FAIL") + " | dir " + d);
}

const requiredFiles = [
  "STATUS.md", "README.md", "AGENTS.md", ".gitignore",
  "accounts/account_registry.md",
  "analytics/ai_costs.csv",
  "database/schema.sql", "database/content_experiments_template.csv", "scripts/content_db.py",
  "workflows/SHORT_VIDEO_PIPELINE.md",
];
for (const f of requiredFiles) {
  out.push((fs.existsSync(path.join(root, f)) ? "PASS" : "FAIL") + " | file " + f);
}

const contentHead = [
  "content_id", "platform", "publish_date", "series", "topic", "content_type",
  "duration", "hook_type", "visual_style", "characters", "generation_models",
  "image_generation_count", "video_generation_count", "failed_generation_count",
  "estimated_image_cost", "estimated_video_cost", "estimated_audio_cost",
  "total_cost", "production_time", "views", "likes", "comments", "shares",
  "favorites", "followers_gained", "three_second_retention", "completion_rate",
  "revenue", "notes",
];
const contentCsvHead = fs.readFileSync(
  path.join(root, "database", "content_experiments_template.csv"), "utf8"
).split(/\r?\n/)[0].split(",");
out.push((JSON.stringify(contentCsvHead) === JSON.stringify(contentHead)
  ? "PASS" : "FAIL") + " | content template headers");

const costHead = [
  "date", "project", "model", "task", "generation_count", "success_count",
  "failure_count", "tokens_or_credits", "cost_rmb", "adopted", "notes",
];
const costCsvHead = fs.readFileSync(
  path.join(root, "analytics", "ai_costs.csv"), "utf8"
).split(/\r?\n/)[0].split(",");
out.push((JSON.stringify(costCsvHead) === JSON.stringify(costHead)
  ? "PASS" : "FAIL") + " | cost ledger headers");

const gi = fs.readFileSync(path.join(root, ".gitignore"), "utf8");
for (const pat of [".env", "temp/", "logs/", "database/*.sqlite*", "node_modules/"]) {
  out.push((gi.includes(pat) ? "PASS" : "FAIL") + " | gitignore " + pat);
}

console.log(out.join("\n"));
