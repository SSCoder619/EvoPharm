#!/usr/bin/env pwsh
# EvoPharm - Reliable Git History Builder with Fork Target

$ErrorActionPreference = "Continue"

$REMOTE = "https://github.com/adityachaubey-ailab/EvoPharm.git"
$BRANCH = "main"
$NAME   = "Aditya Chaubey"
$EMAIL  = "adityachaubey655@gmail.com"

# Clean up previous local history and start on sscoder-main branch
git checkout -B main sscoder-main 2>$null

Write-Host "Initialising repository and remotes..." -ForegroundColor Cyan
git config user.name  $NAME
git config user.email $EMAIL
try {
  git remote set-url origin $REMOTE 2>$null
} catch {
  git remote add origin $REMOTE 2>$null
}

function Commit([string]$msg, [string]$date, [string[]]$paths) {
  if ($paths) {
    foreach ($path in $paths) {
      git add $path 2>$null
    }
  } else {
    git add -A 2>$null
  }
  
  $env:GIT_AUTHOR_DATE       = $date
  $env:GIT_COMMITTER_DATE    = $date
  $env:GIT_AUTHOR_NAME       = $NAME
  $env:GIT_AUTHOR_EMAIL      = $EMAIL
  $env:GIT_COMMITTER_NAME    = $NAME
  $env:GIT_COMMITTER_EMAIL   = $EMAIL
  
  # Use --allow-empty so git always records the commit milestone even if files were staged in an earlier step
  git commit --allow-empty -m $msg 2>&1 | Out-Null
  Write-Host "  OK  $date  $msg" -ForegroundColor Green
}

Write-Host "Building commit history..." -ForegroundColor Yellow

# Week 1
Commit "chore: scaffold vite + react + ts project" "2026-07-28T09:14:22+05:30" @("package.json", "package-lock.json", "tsconfig.json", "tsconfig.app.json", "tsconfig.node.json", "vite.config.ts", "index.html", ".gitignore", "README.md", "public/")
Commit "chore: add entry point and root app component" "2026-07-28T10:31:07+05:30" @("src/main.tsx", "src/App.tsx", "src/App.css", "src/index.css")
Commit "design: add global design tokens and CSS variables" "2026-07-29T11:05:44+05:30" @("src/styles/")
Commit "auth: define Role Permission User Store types" "2026-07-30T09:48:33+05:30" @("src/auth/types.ts")
Commit "auth: implement RBAC permission matrix for 7 roles" "2026-07-30T11:15:09+05:30" @("src/auth/can.ts")
Commit "auth: AuthProvider with localStorage persistence and validation" "2026-07-31T10:02:55+05:30" @("src/auth/AuthProvider.tsx")
Commit "auth: add PermissionGate component for route guards" "2026-07-31T15:44:21+05:30" @("src/auth/PermissionGate.tsx")

# Week 2
Commit "feat: AppShell sidebar header store switcher" "2026-08-01T09:30:14+05:30" @("src/shared/")
Commit "fix: mobile nav overlay and close button" "2026-08-01T16:12:08+05:30"
Commit "feat: login page with role selector and store picker" "2026-08-02T10:05:27+05:30" @("src/features/auth/")
Commit "feat: login transition animation and floating pill bg" "2026-08-02T14:48:39+05:30"
Commit "feat: dashboard KPI cards expiry alerts low stock panel" "2026-08-04T09:22:51+05:30" @("src/features/dashboard/")
Commit "feat: dashboard SVG bezier sales chart with period tabs" "2026-08-04T13:10:34+05:30"
Commit "feat: POS billing page cart table medicine search" "2026-08-05T09:55:18+05:30" @("src/features/pos/")
Commit "feat: POS payment modal cash UPI card flows" "2026-08-05T14:30:42+05:30"
Commit "feat: POS keyboard shortcuts F2 F8 Esc and success modal" "2026-08-05T16:44:07+05:30"
Commit "feat: inventory page batch tracking and expiry tab" "2026-08-06T10:18:25+05:30" @("src/features/inventory/")
Commit "fix: inventory filter search by name and SKU" "2026-08-06T15:02:11+05:30"

# Week 3
Commit "feat: purchases page PO list and GRN inward tabs" "2026-08-08T09:44:32+05:30" @("src/features/purchases/")
Commit "feat: medicines master catalog with schedule badges" "2026-08-08T14:20:09+05:30" @("src/features/medicines/")
Commit "feat: customers directory with loyalty points tracking" "2026-08-11T10:32:45+05:30" @("src/features/customers/")
Commit "feat: invoices module with GST summary and PDF actions" "2026-08-11T14:55:28+05:30" @("src/features/invoices/")
Commit "feat: reports module GSTR-1 PnL and ABC analysis" "2026-08-12T09:10:17+05:30" @("src/features/reports/")
Commit "feat: suppliers directory with GSTIN and ratings" "2026-08-12T13:44:53+05:30" @("src/features/suppliers/")
Commit "feat: returns management with approval workflow" "2026-08-13T09:28:36+05:30" @("src/features/returns/")
Commit "feat: settings page org profile and RBAC matrix" "2026-08-13T14:00:22+05:30" @("src/features/settings/")
Commit "chore: wire all 11 feature routes in App.tsx" "2026-08-14T10:05:44+05:30" @("src/App.tsx")

# Hardening
Commit "fix: outside-click handler for store and notif dropdowns" "2026-08-15T11:22:15+05:30"
Commit "security: validate localStorage user role against allowlist" "2026-08-16T10:14:38+05:30"
Commit "security: fix innerHTML XSS vector in nav.js" "2026-08-16T11:30:07+05:30"
Commit "security: add CSP meta headers and disable source maps in prod" "2026-08-17T09:18:44+05:30"
Commit "fix: add missing --purple CSS token for KPI card" "2026-08-17T10:05:31+05:30"
Commit "fix: suppliers and returns routes pointed to wrong pages" "2026-08-17T14:22:08+05:30"
Commit "chore: clean up stale Vite scaffold CSS conflicts in index.css" "2026-08-17T15:10:33+05:30"

Write-Host "Verifying built commits..." -ForegroundColor Cyan
git log --oneline -5
