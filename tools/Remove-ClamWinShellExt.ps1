#Requires -Version 2.0
<#
.SYNOPSIS
    Removes all ClamWin shell extension registry entries from HKCU and HKLM.

.DESCRIPTION
    Cleans up every registry key written by the ClamWin installer for the
    Explorer context-menu ("Scan with ClamWin Free Antivirus") shell extension,
    including stale or malformed entries left by older installer versions.

    HKCU entries are removed for the current user. When running elevated, also
    removes HKCU entries for the real logged-on user (via HKEY_USERS\<SID>).
    HKLM entries require Administrator; they are skipped with a warning if not.

.PARAMETER Restart
    Restart Windows Explorer after cleaning up so the change takes effect
    immediately without a reboot.

.EXAMPLE
    .\Remove-ClamWinShellExt.ps1
    .\Remove-ClamWinShellExt.ps1 -Restart
#>
param(
    [switch]$Restart
)

$CLSID = '{65713842-C410-4f44-8383-BFE01A398C90}'

# ── Helpers ───────────────────────────────────────────────────────────────────

function Remove-RegKey {
    param([string]$path)
    # Use cmd /c so reg.exe stderr never reaches PowerShell error pipeline.
    $result = cmd /c "reg delete `"$path`" /f 2>&1"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Removed : $path"
    } elseif ("$result" -match 'unable to find|cannot find|does not exist') {
        Write-Host "  Missing : $path  (skipped)"
    } else {
        Write-Warning "  Failed  : $path -- $result"
    }
}

function Test-Admin {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $p  = New-Object System.Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# When elevated, the real user's HKCU is not loaded under HKCU.
# Resolve it via WMI explorer.exe owner -> SID -> HKU\<SID>.
function Get-RealUserHive {
    try {
        $explorerProc = Get-WmiObject Win32_Process -Filter "Name='explorer.exe'" |
                        Select-Object -First 1
        if (-not $explorerProc) { return $null }
        $owner = $explorerProc.GetOwner()
        $domain = $owner.Domain
        $user   = $owner.User
        $ntUser = if ($domain) { "$domain\$user" } else { $user }
        $sid = (New-Object System.Security.Principal.NTAccount($ntUser)).Translate(
                    [System.Security.Principal.SecurityIdentifier]).Value
        return "HKU\$sid"
    } catch {
        return $null
    }
}

# ── HKCU entries ─────────────────────────────────────────────────────────────

$hkuRoots = @("HKCU")

if (Test-Admin) {
    $realHive = Get-RealUserHive
    if ($realHive -and $realHive -ne "HKCU") {
        Write-Host "(Elevated: also targeting real user hive $realHive)"
        $hkuRoots += $realHive
    }
}

foreach ($hive in $hkuRoots) {
    Write-Host "`n[$hive] Removing per-user entries..."
    Remove-RegKey "$hive\Software\Classes\CLSID\$CLSID"
    Remove-RegKey "$hive\Software\Classes\*\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "$hive\Software\Classes\Folder\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "$hive\Software\Classes\Directory\shellex\ContextMenuHandlers\ClamWin"
}

# ── HKLM entries — require elevation ─────────────────────────────────────────

if (Test-Admin) {
    Write-Host "`n[HKLM] Removing all-users entries (native 64-bit hive)..."
    Remove-RegKey "HKLM\SOFTWARE\Classes\CLSID\$CLSID"
    Remove-RegKey "HKLM\SOFTWARE\Classes\*\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "HKLM\SOFTWARE\Classes\Folder\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "HKLM\SOFTWARE\Classes\Directory\shellex\ContextMenuHandlers\ClamWin"

    Write-Host "`n[HKLM] Removing WOW64 32-bit hive entries..."
    Remove-RegKey "HKLM\SOFTWARE\WOW6432Node\Classes\CLSID\$CLSID"
    Remove-RegKey "HKLM\SOFTWARE\WOW6432Node\Classes\*\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "HKLM\SOFTWARE\WOW6432Node\Classes\Folder\shellex\ContextMenuHandlers\ClamWin"
    Remove-RegKey "HKLM\SOFTWARE\WOW6432Node\Classes\Directory\shellex\ContextMenuHandlers\ClamWin"
} else {
    Write-Warning "Not running as Administrator -- HKLM entries were NOT removed."
    Write-Warning "Re-run this script as Administrator to remove all-users entries."
}

# ── Restart Explorer ──────────────────────────────────────────────────────────

if ($Restart) {
    Write-Host "`nRestarting Windows Explorer..."
    $procs = @(Get-Process -ProcessName explorer -ErrorAction SilentlyContinue)
    foreach ($p in $procs) {
        try { $p.Kill(); $p.WaitForExit(3000) | Out-Null } catch { }
    }
    Start-Sleep -Milliseconds 500
    Start-Process explorer.exe
    Write-Host "Explorer restarted."
} else {
    Write-Host "`nDone. Restart Windows Explorer (or log off/on) for changes to take effect."
    Write-Host "Tip: run with -Restart to do this automatically."
}
exit 0
