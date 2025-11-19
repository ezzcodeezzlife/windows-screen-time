# Screen Time Tracker - Simple Installer Script
# This script installs the application and sets up auto-start

param(
    [switch]$Uninstall
)

$AppName = "Screen Time Tracker"
$AppFolder = "$env:ProgramFiles\ScreenTimeTracker"
$ExeName = "ScreenTimeTracker.exe"
$SourceExe = Join-Path $PSScriptRoot "dist\$ExeName"
$TargetExe = Join-Path $AppFolder $ExeName
$RegistryKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$RegistryValue = "ScreenTimeTracker"

if ($Uninstall) {
    Write-Host "Uninstalling $AppName..." -ForegroundColor Yellow
    
    # Remove from auto-start
    if (Test-Path $RegistryKey) {
        Remove-ItemProperty -Path $RegistryKey -Name $RegistryValue -ErrorAction SilentlyContinue
        Write-Host "Removed from auto-start" -ForegroundColor Green
    }
    
    # Remove shortcuts
    $DesktopShortcut = "$env:USERPROFILE\Desktop\$AppName.lnk"
    $StartMenuShortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"
    
    if (Test-Path $DesktopShortcut) {
        Remove-Item $DesktopShortcut -Force
        Write-Host "Removed desktop shortcut" -ForegroundColor Green
    }
    
    if (Test-Path $StartMenuShortcut) {
        Remove-Item $StartMenuShortcut -Force
        Write-Host "Removed Start Menu shortcut" -ForegroundColor Green
    }
    
    # Remove application folder
    if (Test-Path $AppFolder) {
        Remove-Item $AppFolder -Recurse -Force
        Write-Host "Removed application files" -ForegroundColor Green
    }
    
    Write-Host "`nUninstallation complete!" -ForegroundColor Green
    exit 0
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This installer requires administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host "`nRight-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if source file exists
if (-not (Test-Path $SourceExe)) {
    Write-Host "Error: $SourceExe not found!" -ForegroundColor Red
    Write-Host "Please build the executable first using: python build.py" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Installing $AppName..." -ForegroundColor Cyan
Write-Host ""

# Create application folder
if (-not (Test-Path $AppFolder)) {
    New-Item -ItemType Directory -Path $AppFolder -Force | Out-Null
    Write-Host "Created application folder: $AppFolder" -ForegroundColor Green
}

# Copy executable
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item $SourceExe $TargetExe -Force
Write-Host "Files copied successfully" -ForegroundColor Green

# Set up auto-start in registry
Write-Host "Setting up auto-start..." -ForegroundColor Yellow
Set-ItemProperty -Path $RegistryKey -Name $RegistryValue -Value $TargetExe -Type String
Write-Host "Auto-start configured" -ForegroundColor Green

# Create desktop shortcut
$WshShell = New-Object -ComObject WScript.Shell
$DesktopShortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\$AppName.lnk")
$DesktopShortcut.TargetPath = $TargetExe
$DesktopShortcut.WorkingDirectory = $AppFolder
$DesktopShortcut.Description = "Screen Time Tracker"
$DesktopShortcut.Save()
Write-Host "Created desktop shortcut" -ForegroundColor Green

# Create Start Menu shortcut
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
if (-not (Test-Path $StartMenuPath)) {
    New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
}
$StartMenuShortcut = $WshShell.CreateShortcut("$StartMenuPath\$AppName.lnk")
$StartMenuShortcut.TargetPath = $TargetExe
$StartMenuShortcut.WorkingDirectory = $AppFolder
$StartMenuShortcut.Description = "Screen Time Tracker"
$StartMenuShortcut.Save()
Write-Host "Created Start Menu shortcut" -ForegroundColor Green

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "The application will start automatically on next boot." -ForegroundColor Cyan
Write-Host "You can also start it now from the desktop shortcut." -ForegroundColor Cyan
Write-Host ""
Write-Host "To uninstall, run: .\install.ps1 -Uninstall" -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Would you like to start the application now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process $TargetExe
    Write-Host "Application started!" -ForegroundColor Green
}

pause

