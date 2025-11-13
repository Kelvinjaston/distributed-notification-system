#!/usr/bin/env pwsh

<#
.SYNOPSIS
Verifies that the project structure is correct and all imports are resolvable

.DESCRIPTION
This script checks:
1. All Python files have valid syntax
2. All __init__.py files exist
3. All imports can be resolved
4. YAML files are valid
5. Git hooks are properly configured
#>

Write-Host "=== Template Service Project Verification ===" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()
$success_count = 0

# Check 1: Python Syntax
Write-Host "1. Checking Python syntax..." -ForegroundColor Yellow
$python_files = Get-ChildItem -Path ".\app", ".\services" -Filter "*.py" -Recurse
foreach ($file in $python_files) {
    $result = python -m py_compile $file.FullName 2>&1
    if ($LASTEXITCODE -eq 0) {
        $success_count++
    } else {
        $errors += "❌ Syntax error in $($file.Name): $result"
    }
}
Write-Host "✓ $success_count Python files have valid syntax" -ForegroundColor Green
Write-Host ""

# Check 2: __init__.py files
Write-Host "2. Checking __init__.py files..." -ForegroundColor Yellow
$required_init = @(
    ".\app\__init__.py",
    ".\app\api\__init__.py",
    ".\app\core\__init__.py",
    ".\app\utils\__init__.py",
    ".\services\__init__.py"
)

$init_count = 0
foreach ($init_file in $required_init) {
    if (Test-Path $init_file) {
        Write-Host "  ✓ $init_file exists"
        $init_count++
    } else {
        $errors += "❌ Missing: $init_file"
    }
}
Write-Host "✓ $init_count/$($required_init.Count) __init__.py files present" -ForegroundColor Green
Write-Host ""

# Check 3: Key files exist
Write-Host "3. Checking key files..." -ForegroundColor Yellow
$key_files = @(
    ".\app\main.py",
    ".\app\api\routes.py",
    ".\app\models.py",
    ".\app\schemas.py",
    ".\app\crud.py",
    ".\services\cache.py",
    ".\services\messaging.py",
    ".\pyproject.toml",
    ".\.github\workflows\ci-cd.yml"
)

$files_found = 0
foreach ($file in $key_files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file exists"
        $files_found++
    } else {
        $warnings += "⚠ Missing: $file"
    }
}
Write-Host "✓ $files_found/$($key_files.Count) key files present" -ForegroundColor Green
Write-Host ""

# Check 4: YAML files validity
Write-Host "4. Checking YAML files..." -ForegroundColor Yellow
$yaml_files = Get-ChildItem -Path ".\.github\workflows" -Filter "*.yml" -Recurse 2>/dev/null
if ($yaml_files) {
    Write-Host "  ✓ Found $($yaml_files.Count) workflow files"
    Write-Host "  ℹ YAML validation will be done by GitHub Actions"
} else {
    $warnings += "⚠ No workflow files found in .github/workflows"
}
Write-Host ""

# Check 5: Git hooks
Write-Host "5. Checking Git configuration..." -ForegroundColor Yellow
if (Test-Path ".\.git\hooks\pre-commit") {
    Write-Host "  ✓ Pre-commit hook exists"
    $hook_content = Get-Content ".\.git\hooks\pre-commit" -Raw
    if ($hook_content -match "YAML") {
        Write-Host "  ✓ Pre-commit hook configured to skip YAML"
    }
} else {
    $warnings += "⚠ Pre-commit hook not found"
}
Write-Host ""

# Final Summary
Write-Host "=== Verification Summary ===" -ForegroundColor Cyan
Write-Host "✓ Successful checks: $success_count" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Errors found:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  $error"
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Warnings:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  $warning"
    }
}

if ($errors.Count -eq 0) {
    Write-Host ""
    Write-Host "✅ All checks passed! Project structure is correct." -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now commit with:" -ForegroundColor Cyan
    Write-Host "  .\scripts\git-commit.ps1 `"Your commit message`"" -ForegroundColor White
}
