<#
.SYNOPSIS
    Install dependencies & start all 3 framework-based test websites.
.DESCRIPTION
    site6_ecommerce   — Next.js SSR   → http://localhost:3006
    site7_spa_taskboard — React + Vite SPA → http://localhost:3007
    site8_medical     — Express + EJS → http://localhost:3008

    The original 5 HTML sites still need Live Server on port 5500.
.USAGE
    .\scripts\start_framework_sites.ps1          # install + start
    .\scripts\start_framework_sites.ps1 -SkipInstall  # start only
#>
param([switch]$SkipInstall)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot   # repo root

$sites = @(
    @{ Name = "site6_ecommerce";      Dir = "$root\test_websites\site6_ecommerce";      Port = 3006; Cmd = "npm run dev" },
    @{ Name = "site7_spa_taskboard";   Dir = "$root\test_websites\site7_spa_taskboard";  Port = 3007; Cmd = "npm run dev" },
    @{ Name = "site8_medical";         Dir = "$root\test_websites\site8_medical";         Port = 3008; Cmd = "npm start" }
)

# ── Install dependencies ─────────────────────────────────────────────────────
if (-not $SkipInstall) {
    foreach ($s in $sites) {
        Write-Host "`n📦 Installing $($s.Name) ..." -ForegroundColor Cyan
        Push-Location $s.Dir
        npm install 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host "  ❌ npm install failed for $($s.Name)" -ForegroundColor Red }
        else { Write-Host "  ✅ Dependencies installed" -ForegroundColor Green }
        Pop-Location
    }
}

# ── Start each site in a background job ──────────────────────────────────────
$jobs = @()
foreach ($s in $sites) {
    Write-Host "`n🚀 Starting $($s.Name) on port $($s.Port) ..." -ForegroundColor Cyan
    $dir = $s.Dir
    $cmd = $s.Cmd
    $job = Start-Job -ScriptBlock {
        param($d, $c)
        Set-Location $d
        Invoke-Expression $c
    } -ArgumentList $dir, $cmd
    $jobs += $job
    Write-Host "  → Job $($job.Id) started" -ForegroundColor DarkGray
}

Write-Host "`n════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  All framework sites starting:" -ForegroundColor Yellow
Write-Host "    site6_ecommerce      → http://localhost:3006" -ForegroundColor White
Write-Host "    site7_spa_taskboard  → http://localhost:3007" -ForegroundColor White
Write-Host "    site8_medical        → http://localhost:3008" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop all sites." -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════`n" -ForegroundColor Yellow

# Wait — show output from jobs
try {
    while ($true) {
        foreach ($j in $jobs) {
            Receive-Job -Job $j -ErrorAction SilentlyContinue 2>&1 | ForEach-Object { Write-Host $_ }
        }
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`n🛑 Stopping all site jobs ..." -ForegroundColor Red
    $jobs | Stop-Job -ErrorAction SilentlyContinue
    $jobs | Remove-Job -Force -ErrorAction SilentlyContinue
}
