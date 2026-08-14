# One-click: install @playwright/mcp locally and register it in ~/.codex/config.toml
# Why not `codex mcp add ...`: the desktop app's codex.exe (MSIX) cannot be run
# directly from a normal terminal, and npx may hit the PowerShell execution policy.
# Usage: right-click > Run with PowerShell, or:
#   powershell -ExecutionPolicy Bypass -File .\install-playwright-mcp.ps1

$ErrorActionPreference = "Stop"

$browserDir = "C:\Users\administered\Documents\Codex\AI-MEDIA-OS\tools\browser"
$mcpPkg = Join-Path $browserDir "node_modules\@playwright\mcp"

# 1) install the package locally if missing
if (-not (Test-Path $mcpPkg)) {
    Write-Host "[1/3] Installing @playwright/mcp (npmmirror)..."
    Push-Location $browserDir
    npm.cmd install @playwright/mcp --registry=https://registry.npmmirror.com --no-audit --no-fund
    Pop-Location
}
if (-not (Test-Path $mcpPkg)) { throw "Package install failed: $mcpPkg" }

# 2) resolve the CLI entry from package.json bin
$pkg = Get-Content -Raw -LiteralPath (Join-Path $mcpPkg "package.json") | ConvertFrom-Json
if ($pkg.bin -is [string]) { $rel = $pkg.bin } else { $rel = $pkg.bin."playwright-mcp" }
if (-not $rel) { $rel = "cli.js" }
$cli = Join-Path $mcpPkg ($rel -replace "\\", "/" -replace "^\./", "")
if (-not (Test-Path $cli)) {
    $fallback = Join-Path $mcpPkg "cli.js"
    if (Test-Path $fallback) { $cli = $fallback } else { throw "Cannot locate MCP cli under $mcpPkg" }
}
$cliFwd = $cli -replace "\\", "/"
Write-Host "[2/3] MCP cli: $cliFwd"
$ver = node $cliFwd --version 2>&1
Write-Host "cli check: $ver"

# 3) register in ~/.codex/config.toml (idempotent, with backup)
$cfg = Join-Path $HOME ".codex\config.toml"
if (-not (Test-Path $cfg)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $cfg) | Out-Null
    Set-Content -LiteralPath $cfg -Value "" -Encoding UTF8
}
$content = Get-Content -Raw -LiteralPath $cfg
if ($content -match "\[mcp_servers\.playwright\]") {
    Write-Host "[SKIP] playwright MCP already registered."
} else {
    Copy-Item -LiteralPath $cfg -Destination "$cfg.bak-playwright-$(Get-Date -Format yyyyMMdd-HHmmss)" -Force
    $entry = "`n[mcp_servers.playwright]`ncommand = `"node`"`nargs = [`"$cliFwd`"]`n"
    Add-Content -LiteralPath $cfg -Value $entry -Encoding UTF8
    Write-Host "[3/3] playwright MCP registered."
}

Write-Host ""
Write-Host "Next: fully quit and restart the Codex app."
Write-Host "Then ask me to open a webpage and I will use Playwright."
