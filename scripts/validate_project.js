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

console.log(out.join("\n"));
