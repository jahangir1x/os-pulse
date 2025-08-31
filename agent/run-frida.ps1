#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory=$false)]
    [string]$Target = "notepad.exe",
    
    [Parameter(Mandatory=$false)]
    [switch]$Spawn,
    
    [Parameter(Mandatory=$false)]
    [switch]$Build = $true
)

# Activate Python environment
Write-Host "Activating Python environment..." -ForegroundColor Green
& .pyenv\Scripts\Activate.ps1

# Build project
if ($Build) {
    Write-Host "Building project..." -ForegroundColor Green
    npm run build
}

# Run Frida
if ($Spawn) {
    Write-Host "Spawning $Target with Frida..." -ForegroundColor Green
    frida -f "C:\Windows\System32\$Target" -l ".\_agent.js"
} else {
    Write-Host "Attaching to $Target with Frida..." -ForegroundColor Green
    frida -n $Target -l ".\_agent.js"
}
