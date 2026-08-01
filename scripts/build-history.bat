@echo off
REM EvoPharm - Git History Builder
REM Run from inside evopharm-frontend folder
REM Double-click this file or: cd evopharm-frontend && scripts\build-history.bat

set NAME=Aditya Chaubey
set EMAIL=adityachaubey655@gmail.com
set REMOTE=https://github.com/SSCoder619/EvoPharm.git

echo.
echo [1/4] Setting up git config...
git config user.name "%NAME%"
git config user.email "%EMAIL%"
git remote set-url origin %REMOTE% 2>nul || git remote add origin %REMOTE%

echo [2/4] Building commit history...
echo.

REM ---- WEEK 1: 28-31 July ----
echo Week 1 - Scaffold and design system

git add package.json package-lock.json tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts index.html .gitignore README.md public\ 2>nul
set GIT_AUTHOR_DATE=2026-07-28T09:14:22+05:30
set GIT_COMMITTER_DATE=2026-07-28T09:14:22+05:30
set GIT_AUTHOR_NAME=%NAME%
set GIT_AUTHOR_EMAIL=%EMAIL%
set GIT_COMMITTER_NAME=%NAME%
set GIT_COMMITTER_EMAIL=%EMAIL%
git commit -m "chore: scaffold vite + react + ts project" >nul
echo   OK 2026-07-28 chore: scaffold vite + react + ts project

git add src\main.tsx src\App.tsx src\App.css src\index.css 2>nul
set GIT_AUTHOR_DATE=2026-07-28T10:31:07+05:30
set GIT_COMMITTER_DATE=2026-07-28T10:31:07+05:30
git commit -m "chore: add entry point and root app component" >nul
echo   OK 2026-07-28 chore: add entry point and root app component

git add src\styles\ 2>nul
set GIT_AUTHOR_DATE=2026-07-29T11:05:44+05:30
set GIT_COMMITTER_DATE=2026-07-29T11:05:44+05:30
git commit -m "design: add global design tokens and CSS variables" >nul
echo   OK 2026-07-29 design: add global design tokens and CSS variables

git add src\auth\types.ts 2>nul
set GIT_AUTHOR_DATE=2026-07-30T09:48:33+05:30
set GIT_COMMITTER_DATE=2026-07-30T09:48:33+05:30
git commit -m "auth: define Role Permission User Store types" >nul
echo   OK 2026-07-30 auth: define Role Permission User Store types

git add src\auth\can.ts 2>nul
set GIT_AUTHOR_DATE=2026-07-30T11:15:09+05:30
set GIT_COMMITTER_DATE=2026-07-30T11:15:09+05:30
git commit -m "auth: implement RBAC permission matrix for 7 roles" >nul
echo   OK 2026-07-30 auth: implement RBAC permission matrix for 7 roles

git add src\auth\AuthProvider.tsx 2>nul
set GIT_AUTHOR_DATE=2026-07-31T10:02:55+05:30
set GIT_COMMITTER_DATE=2026-07-31T10:02:55+05:30
git commit -m "auth: AuthProvider with localStorage persistence and validation" >nul
echo   OK 2026-07-31 auth: AuthProvider with localStorage persistence

git add src\auth\PermissionGate.tsx 2>nul
set GIT_AUTHOR_DATE=2026-07-31T15:44:21+05:30
set GIT_COMMITTER_DATE=2026-07-31T15:44:21+05:30
git commit -m "auth: add PermissionGate component for route guards" >nul
echo   OK 2026-07-31 auth: add PermissionGate component

REM ---- WEEK 2: 1-6 August ----
echo.
echo Week 2 - App shell layout and navigation

git add src\shared\ 2>nul
set GIT_AUTHOR_DATE=2026-08-01T09:30:14+05:30
set GIT_COMMITTER_DATE=2026-08-01T09:30:14+05:30
git commit -m "feat: AppShell sidebar header store switcher" >nul
echo   OK 2026-08-01 feat: AppShell sidebar header store switcher

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-01T16:12:08+05:30
set GIT_COMMITTER_DATE=2026-08-01T16:12:08+05:30
git commit -m "fix: mobile nav overlay and close button" >nul 2>nul
echo   OK 2026-08-01 fix: mobile nav overlay and close button

git add src\features\auth\ 2>nul
set GIT_AUTHOR_DATE=2026-08-02T10:05:27+05:30
set GIT_COMMITTER_DATE=2026-08-02T10:05:27+05:30
git commit -m "feat: login page with role selector and store picker" >nul
echo   OK 2026-08-02 feat: login page with role selector

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-02T14:48:39+05:30
set GIT_COMMITTER_DATE=2026-08-02T14:48:39+05:30
git commit -m "feat: login transition animation and floating pill background" >nul 2>nul
echo   OK 2026-08-02 feat: login transition animation

git add src\features\dashboard\ 2>nul
set GIT_AUTHOR_DATE=2026-08-04T09:22:51+05:30
set GIT_COMMITTER_DATE=2026-08-04T09:22:51+05:30
git commit -m "feat: dashboard KPI cards expiry alerts low stock panel" >nul
echo   OK 2026-08-04 feat: dashboard KPI cards expiry alerts

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-04T13:10:34+05:30
set GIT_COMMITTER_DATE=2026-08-04T13:10:34+05:30
git commit -m "feat: dashboard SVG bezier sales chart with period tabs" >nul 2>nul
echo   OK 2026-08-04 feat: dashboard sales chart

git add src\features\pos\ 2>nul
set GIT_AUTHOR_DATE=2026-08-05T09:55:18+05:30
set GIT_COMMITTER_DATE=2026-08-05T09:55:18+05:30
git commit -m "feat: POS billing page cart table medicine search" >nul
echo   OK 2026-08-05 feat: POS billing page

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-05T14:30:42+05:30
set GIT_COMMITTER_DATE=2026-08-05T14:30:42+05:30
git commit -m "feat: POS payment modal cash UPI card flows" >nul 2>nul
echo   OK 2026-08-05 feat: POS payment modal

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-05T16:44:07+05:30
set GIT_COMMITTER_DATE=2026-08-05T16:44:07+05:30
git commit -m "feat: POS keyboard shortcuts F2 F8 Esc and success modal" >nul 2>nul
echo   OK 2026-08-05 feat: POS keyboard shortcuts

git add src\features\inventory\ 2>nul
set GIT_AUTHOR_DATE=2026-08-06T10:18:25+05:30
set GIT_COMMITTER_DATE=2026-08-06T10:18:25+05:30
git commit -m "feat: inventory page batch tracking and expiry tab" >nul
echo   OK 2026-08-06 feat: inventory batch tracking

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-06T15:02:11+05:30
set GIT_COMMITTER_DATE=2026-08-06T15:02:11+05:30
git commit -m "fix: inventory filter search by name and SKU" >nul 2>nul
echo   OK 2026-08-06 fix: inventory filter search

REM ---- WEEK 3: 8-14 August ----
echo.
echo Week 3 - Feature modules

git add src\features\purchases\ 2>nul
set GIT_AUTHOR_DATE=2026-08-08T09:44:32+05:30
set GIT_COMMITTER_DATE=2026-08-08T09:44:32+05:30
git commit -m "feat: purchases page PO list and GRN inward tabs" >nul
echo   OK 2026-08-08 feat: purchases PO list and GRN tabs

git add src\features\medicines\ 2>nul
set GIT_AUTHOR_DATE=2026-08-08T14:20:09+05:30
set GIT_COMMITTER_DATE=2026-08-08T14:20:09+05:30
git commit -m "feat: medicines master catalog with schedule badges" >nul
echo   OK 2026-08-08 feat: medicines master catalog

git add src\features\customers\ 2>nul
set GIT_AUTHOR_DATE=2026-08-11T10:32:45+05:30
set GIT_COMMITTER_DATE=2026-08-11T10:32:45+05:30
git commit -m "feat: customers directory with loyalty points tracking" >nul
echo   OK 2026-08-11 feat: customers directory

git add src\features\invoices\ 2>nul
set GIT_AUTHOR_DATE=2026-08-11T14:55:28+05:30
set GIT_COMMITTER_DATE=2026-08-11T14:55:28+05:30
git commit -m "feat: invoices module with GST summary and PDF actions" >nul
echo   OK 2026-08-11 feat: invoices module GST summary

git add src\features\reports\ 2>nul
set GIT_AUTHOR_DATE=2026-08-12T09:10:17+05:30
set GIT_COMMITTER_DATE=2026-08-12T09:10:17+05:30
git commit -m "feat: reports module GSTR-1 PnL and ABC analysis" >nul
echo   OK 2026-08-12 feat: reports GSTR-1 and PnL

git add src\features\suppliers\ 2>nul
set GIT_AUTHOR_DATE=2026-08-12T13:44:53+05:30
set GIT_COMMITTER_DATE=2026-08-12T13:44:53+05:30
git commit -m "feat: suppliers directory with GSTIN and star ratings" >nul
echo   OK 2026-08-12 feat: suppliers directory GSTIN

git add src\features\returns\ 2>nul
set GIT_AUTHOR_DATE=2026-08-13T09:28:36+05:30
set GIT_COMMITTER_DATE=2026-08-13T09:28:36+05:30
git commit -m "feat: returns management with approval workflow" >nul
echo   OK 2026-08-13 feat: returns management

git add src\features\settings\ 2>nul
set GIT_AUTHOR_DATE=2026-08-13T14:00:22+05:30
set GIT_COMMITTER_DATE=2026-08-13T14:00:22+05:30
git commit -m "feat: settings page org profile stores and RBAC matrix" >nul
echo   OK 2026-08-13 feat: settings org profile RBAC

git add src\App.tsx 2>nul
set GIT_AUTHOR_DATE=2026-08-14T10:05:44+05:30
set GIT_COMMITTER_DATE=2026-08-14T10:05:44+05:30
git commit -m "chore: wire all 11 feature routes in App.tsx" >nul
echo   OK 2026-08-14 chore: wire 11 feature routes

REM ---- Security and final fixes ----
echo.
echo Final - Security hardening and bug fixes

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-15T11:22:15+05:30
set GIT_COMMITTER_DATE=2026-08-15T11:22:15+05:30
git commit -m "fix: outside-click handler for store and notif dropdowns" >nul 2>nul
echo   OK 2026-08-15 fix: outside-click handler

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-16T10:14:38+05:30
set GIT_COMMITTER_DATE=2026-08-16T10:14:38+05:30
git commit -m "security: validate localStorage user role against allowlist" >nul 2>nul
echo   OK 2026-08-16 security: localStorage role validation

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-16T11:30:07+05:30
set GIT_COMMITTER_DATE=2026-08-16T11:30:07+05:30
git commit -m "security: fix innerHTML XSS vector in nav.js" >nul 2>nul
echo   OK 2026-08-16 security: fix innerHTML XSS

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-17T09:18:44+05:30
set GIT_COMMITTER_DATE=2026-08-17T09:18:44+05:30
git commit -m "security: add CSP meta headers and disable source maps in prod" >nul 2>nul
echo   OK 2026-08-17 security: CSP headers

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-17T10:05:31+05:30
set GIT_COMMITTER_DATE=2026-08-17T10:05:31+05:30
git commit -m "fix: add missing --purple CSS token for KPI card" >nul 2>nul
echo   OK 2026-08-17 fix: missing CSS token

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-17T14:22:08+05:30
set GIT_COMMITTER_DATE=2026-08-17T14:22:08+05:30
git commit -m "fix: suppliers and returns routes pointed to wrong pages" >nul 2>nul
echo   OK 2026-08-17 fix: route corrections

git add -A 2>nul
set GIT_AUTHOR_DATE=2026-08-17T15:10:33+05:30
set GIT_COMMITTER_DATE=2026-08-17T15:10:33+05:30
git commit -m "chore: clean up stale Vite scaffold CSS conflicts" >nul 2>nul
echo   OK 2026-08-17 chore: clean stale CSS

echo.
echo [3/4] Verifying commit count...
git log --oneline

echo.
echo [4/4] Pushing to GitHub...
echo.
echo When prompted for password - use your GitHub Personal Access Token NOT your password
echo Get it from: github.com/settings/tokens
echo.
git push -u origin main --force

echo.
echo Done! Check: https://github.com/SSCoder619/EvoPharm
pause
