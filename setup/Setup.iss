; ClamWin Free Antivirus — Inno Setup script
; Packages the native C++ GUI build (clamwin-gui-cpp).
;
; Build outputs are taken from {#BuildDir32Gui}/{#BuildDir64Gui} and the
; per-platform engine directories below.
; Override individual dirs at compile time, e.g.:
;   iscc /DBuildDir64Gui=C:\path\to\gui-x64-build /DBuildDir64EngineLegacy=C:\path\to\engine-x64-legacy /DBuildDir64EngineModern=C:\path\to\engine-x64-modern Setup.iss

#DEFINE IncludeCVD
#DEFINE AppVersion "1.5.2.1"
#ifndef BuildDir98Engine
  #DEFINE BuildDir98Engine "..\..\binaries\clamav\clamav-legacy-win9x"
#endif
#ifndef BuildDir32Engine
  #DEFINE BuildDir32Engine "..\..\binaries\clamav\clamav-legacy-x86"
#endif
#ifndef BuildDir64EngineLegacy
  #ifdef BuildDir64Engine
    #DEFINE BuildDir64EngineLegacy BuildDir64Engine
  #else
    #DEFINE BuildDir64EngineLegacy "..\..\binaries\clamav\clamav-legacy-x64"
  #endif
#endif
#ifndef BuildDir64EngineModern
  #DEFINE BuildDir64EngineModern "..\..\binaries\clamav\clamav-x64"
#endif
#ifndef BuildDir98Gui
  #DEFINE BuildDir98Gui "..\build-x86-mingw-ansi"
#endif
#ifndef BuildDir32Gui
  #DEFINE BuildDir32Gui "..\build-x86-mingw-winxp"
#endif
#ifndef BuildDir64Gui
  #DEFINE BuildDir64Gui "..\build"
#endif
#ifndef BuildDir98ShellExt
  #DEFINE BuildDir98ShellExt BuildDir98Gui
#endif
#ifndef BuildDir32ShellExt
  #DEFINE BuildDir32ShellExt BuildDir32Gui
#endif
#ifndef BuildDir64ShellExt
  #DEFINE BuildDir64ShellExt BuildDir64Gui
#endif
#ifndef IncludeX64
  #DEFINE IncludeX64 1
#endif
#ifndef SetupMinVersion
  #DEFINE SetupMinVersion "4.10.1998,4.0"
#endif
#ifndef OutputBaseFilenamePrefix
  #DEFINE OutputBaseFilenamePrefix "clamwin-" + AppVersion + "-setup"
#endif

[Setup]
AppName=ClamWin Free Antivirus
AppVerName=ClamWin Free Antivirus {#AppVersion}
AppVersion={#AppVersion}
AppPublisher=ClamWin Pty Ltd
AppPublisherURL=http://www.clamwin.com/
AppSupportURL=http://www.clamwin.com/
AppUpdatesURL=http://www.clamwin.com/
DefaultDirName={code:BaseDir}\ClamWin
DefaultGroupName=ClamWin Antivirus
LicenseFile=Setupfiles\License.rtf
AllowNoIcons=true
MinVersion={#SetupMinVersion}
ShowLanguageDialog=no
LanguageDetectionMethod=none
OutputDir=Output
OutputBaseFilename={#OutputBaseFilenamePrefix}
Compression=lzma/ultra
InternalCompressLevel=max
SolidCompression=true
WizardImageFile=Setupfiles\WizModernImage.bmp
WizardSmallImageFile=Setupfiles\WizModernSmallImage.bmp

[Components]
Name: ClamAV;       Description: ClamAV Engine Files;              Flags: fixed; Types: full custom typical
Name: ClamWin;      Description: ClamWin GUI;                      Flags: fixed; Types: full custom typical
Name: ExplorerShell; Description: Windows Explorer Integration;    Types: full custom typical

[Types]
Name: typical; Description: Typical Installation
Name: custom;  Description: Custom Installation; Flags: iscustom
Name: full;    Description: Full Installation

[Tasks]
Name: DownloadDB;  Description: Download Virus Database Files after install; GroupDescription: Download; Components: ClamAV
Name: desktopicon; Description: Create a &desktop icon; GroupDescription: Additional icons:; Flags: unchecked

[Files]
; ── ClamWin GUI ───────────────────────────────────────────────────────────────
; clamwin.exe
Source: {#BuildDir98Gui}\clamwin.exe;    DestDir: {app}\bin; Components: ClamWin; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Gui}\clamwin.exe;    DestDir: {app}\bin; Components: ClamWin; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64Gui}\clamwin.exe;    DestDir: {app}\bin; Components: ClamWin; Check: IsWin64;     Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; libExpShell.dll
Source: {#BuildDir98ShellExt}\libExpShell.dll;    DestDir: {app}\bin; Components: ExplorerShell; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32ShellExt}\libExpShell.dll;    DestDir: {app}\bin; Components: ExplorerShell; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64ShellExt}\libExpShell.dll;    DestDir: {app}\bin; Components: ExplorerShell; Check: IsWin64;     Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; ── ClamAV Engine ─────────────────────────────────────────────────────────────
; clamscan.exe
Source: {#BuildDir98Engine}\clamscan.exe;    DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Engine}\clamscan.exe;    DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\clamscan.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir64EngineModern}\clamscan.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; freshclam.exe
Source: {#BuildDir98Engine}\freshclam.exe;    DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Engine}\freshclam.exe;    DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\freshclam.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir64EngineModern}\freshclam.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; sigtool.exe
Source: {#BuildDir98Engine}\sigtool.exe;    DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Engine}\sigtool.exe;    DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\sigtool.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir64EngineModern}\sigtool.exe; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; libclamav.dll
Source: {#BuildDir98Engine}\libclamav.dll;    DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Engine}\libclamav.dll;    DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\libclamav.dll; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir64EngineModern}\libclamav.dll; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; libfreshclam.dll
Source: {#BuildDir98Engine}\libfreshclam.dll;    DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir32Engine}\libfreshclam.dll;    DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: restartreplace uninsrestartdelete replacesameversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\libfreshclam.dll; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: restartreplace uninsrestartdelete replacesameversion
Source: {#BuildDir64EngineModern}\libfreshclam.dll; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: restartreplace uninsrestartdelete replacesameversion
#endif

; TLS CA bundle for XP-era libcurl/OpenSSL validation
Source: {#BuildDir98Engine}\curl-ca-bundle.crt;  DestDir: {app}\bin; Components: ClamAV; Check: IsWin98;      Flags: ignoreversion
Source: {#BuildDir32Engine}\curl-ca-bundle.crt;  DestDir: {app}\bin; Components: ClamAV; Check: Is32bitNT;   Flags: ignoreversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\curl-ca-bundle.crt; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitLegacyNT; Flags: ignoreversion
Source: {#BuildDir64EngineModern}\curl-ca-bundle.crt; DestDir: {app}\bin; Components: ClamAV; Check: Is64bitModernNT; Flags: ignoreversion
#endif

; certs
Source: {#BuildDir32Engine}\certs\clamav.crt; DestDir: {app}\bin\certs; Components: ClamAV; Check: IsWin98;      Flags: ignoreversion
Source: {#BuildDir32Engine}\certs\clamav.crt; DestDir: {app}\bin\certs; Components: ClamAV; Check: Is32bitNT;   Flags: ignoreversion
#if IncludeX64
Source: {#BuildDir64EngineLegacy}\certs\clamav.crt; DestDir: {app}\bin\certs; Components: ClamAV; Check: Is64bitLegacyNT; Flags: ignoreversion
Source: {#BuildDir64EngineModern}\certs\clamav.crt; DestDir: {app}\bin\certs; Components: ClamAV; Check: Is64bitModernNT; Flags: ignoreversion
#endif

; ── Virus Databases (optional) ────────────────────────────────────────────────
#IFDEF IncludeCVD
Source: cvd\main.cvd;     DestDir: {code:CommonProfileDir}\.clamwin\db; Components: ClamWin; Flags: ignoreversion comparetimestamp; Check: NoMainCld
Source: cvd\daily.cvd;    DestDir: {code:CommonProfileDir}\.clamwin\db; Components: ClamWin; Flags: ignoreversion comparetimestamp; Check: NoDailyCld
Source: cvd\bytecode.cvd; DestDir: {code:CommonProfileDir}\.clamwin\db; Components: ClamWin; Flags: ignoreversion comparetimestamp; Check: NoBytecodeCld
#ENDIF

[Dirs]
Name: {code:CommonProfileDir}\.clamwin\db;           Components: ClamAV; Permissions: authusers-full; Check: IsAllUsers
Name: {code:CommonProfileDir}\.clamwin\log;          Components: ClamAV; Permissions: authusers-full; Check: IsAllUsers
Name: {code:CommonProfileDir}\.clamwin\quarantine;   Components: ClamAV; Permissions: authusers-full; Check: IsAllUsers
Name: {code:CommonProfileDir}\.clamwin\db;           Components: ClamAV; Check: not IsAllUsers
Name: {code:CommonProfileDir}\.clamwin\log;          Components: ClamAV; Check: not IsAllUsers
Name: {code:CommonProfileDir}\.clamwin\quarantine;   Components: ClamAV; Check: not IsAllUsers
Name: {app}\bin; Components: ClamWin ExplorerShell

; ── Remove legacy wxPython files on upgrade ───────────────────────────────────
[InstallDelete]
; Old GUI Python executables
Type: files; Name: {app}\bin\ClamTray.exe
Type: files; Name: {app}\bin\OlAddin.exe
Type: files; Name: {app}\bin\w9xpopen.exe

; Old Python runtime DLL
Type: files; Name: {app}\bin\python23.dll
Type: files; Name: {app}\bin\unicows.dll

; Old shell extension DLLs (were ExpShell.dll / ExpShell64.dll in wxPython era)
Type: files; Name: {app}\bin\ExpShell.dll
Type: files; Name: {app}\bin\ExpShell64.dll

; Old docs
Type: files; Name: {app}\bin\manual.chm
Type: files; Name: {app}\bin\manual_en.pdf
Type: files; Name: {app}\bin\manual_fr.pdf
Type: files; Name: {app}\bin\manual_nl.pdf
Type: files; Name: {app}\bin\manual_nl.chm

; Entire old wxPython lib and img directories
Type: filesandordirs; Name: {app}\lib
Type: filesandordirs; Name: {app}\bin\img
Type: filesandordirs; Name: {app}\bin\Microsoft.VC80.CRT

; Old CVD format (upgrade to new if present)
Type: files; Name: {code:CommonProfileDir}\.clamwin\db\main.cvd;     Check: IsDeleteCvd
Type: files; Name: {code:CommonProfileDir}\.clamwin\db\daily.cvd;    Check: IsDeleteCvd
Type: files; Name: {code:CommonProfileDir}\.clamwin\db\bytecode.cvd; Check: IsDeleteCvd

[UninstallDelete]
Type: filesandordirs; Name: {app}
Type: filesandordirs; Name: {userappdata}\.clamwin
Type: filesandordirs; Name: {code:CommonProfileDir}\.clamwin

[Icons]
Name: {group}\ClamWin Antivirus;        Filename: {app}\bin\clamwin.exe; WorkingDir: {app}\bin; Comment: ClamWin Free Antivirus; Components: ClamWin
Name: {code:DesktopDir}\ClamWin Antivirus; Filename: {app}\bin\clamwin.exe; WorkingDir: {app}\bin; Comment: ClamWin Free Antivirus; Components: ClamWin; Tasks: desktopicon
Name: {group}\Uninstall ClamWin Free Antivirus; Filename: {uninstallexe}

[Run]
; Use ClamWin's update dialog for post-install DB downloads.
; Launch clamwin.exe when done
Filename: {app}\bin\clamwin.exe; Parameters: "{code:ClamWinPostInstallParams}"; WorkingDir: {app}\bin; Flags: nowait postinstall skipifsilent; Description: Launch ClamWin Free Antivirus; Components: ClamWin

[INI]
; Only write these if the key is currently empty — preserves existing config on upgrade
Filename: {code:ClamWinConfPath}; Section: ClamAV;   Key: clamscan;       String: {app}\bin\clamscan.exe;    Check: IsIniValueEmpty(ExpandConstant('ClamAV*clamscan*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: ClamAV;   Key: freshclam;      String: {app}\bin\freshclam.exe;   Check: IsIniValueEmpty(ExpandConstant('ClamAV*freshclam*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: ClamAV;   Key: database;       String: {code:CommonProfileDir}\.clamwin\db;          Check: IsIniValueEmpty(ExpandConstant('ClamAV*database*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: ClamAV;   Key: quarantinedir;  String: {code:CommonProfileDir}\.clamwin\quarantine;   Check: IsIniValueEmpty(ExpandConstant('ClamAV*quarantinedir*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: ClamAV;   Key: logfile;        String: {code:CommonProfileDir}\.clamwin\log\ClamScanLog.txt;   Check: IsIniValueEmpty(ExpandConstant('ClamAV*logfile*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: Updates;  Key: dbupdatelogfile; String: {code:CommonProfileDir}\.clamwin\log\ClamUpdateLog.txt; Check: IsIniValueEmpty(ExpandConstant('Updates*dbupdatelogfile*{code:ClamWinConfPath}'))
Filename: {code:ClamWinConfPath}; Section: Updates;  Key: time;            String: {code:CurTime};            Check: IsIniValueEmpty(ExpandConstant('Updates*time*{code:ClamWinConfPath}'))

[Registry]
; Start the tray app automatically at logon.
Root: HKLM;   Subkey: Software\Microsoft\Windows\CurrentVersion\Run; ValueType: string; ValueName: ClamWin; ValueData: """{app}\bin\clamwin.exe"""; Flags: uninsdeletevalue; Components: ClamWin; Check: IsAllUsers
Root: HKCU;   Subkey: Software\Microsoft\Windows\CurrentVersion\Run; ValueType: string; ValueName: ClamWin; ValueData: """{app}\bin\clamwin.exe"""; Flags: uninsdeletevalue; Components: ClamWin; Check: not IsAllUsers

; ── ClamWin path ────────────────────────────────────────────────────────────────
Root: HKLM;   Subkey: Software\ClamWin; ValueType: string; ValueName: Path;    ValueData: {app}\bin; Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: IsAllUsers
Root: HKLM;   Subkey: Software\ClamWin; ValueType: dword;  ValueName: Version; ValueData: 10502;     Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: IsAllUsers
Root: HKLM64; Subkey: Software\ClamWin; ValueType: string; ValueName: Path;    ValueData: {app}\bin; Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: IsAllUsers and IsWin64
Root: HKCU;   Subkey: Software\ClamWin; ValueType: string; ValueName: Path;    ValueData: {app}\bin; Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\ClamWin; ValueType: dword;  ValueName: Version; ValueData: 10502;     Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: not IsAllUsers
Root: HKCU64; Subkey: Software\ClamWin; ValueType: string; ValueName: Path;    ValueData: {app}\bin; Flags: uninsdeletekey deletevalue; Components: ClamWin; Check: not IsAllUsers and IsWin64

; ── ClamAV defaults for freshclam/clamd compatibility ─────────────────────────
Root: HKLM;   Subkey: Software\ClamAV; ValueType: string; ValueName: ConfDir; ValueData: {code:CommonProfileDir}\.clamwin;     Flags: uninsdeletevalue; Components: ClamAV; Check: IsAllUsers
Root: HKLM;   Subkey: Software\ClamAV; ValueType: string; ValueName: DataDir; ValueData: {code:CommonProfileDir}\.clamwin\db; Flags: uninsdeletevalue; Components: ClamAV; Check: IsAllUsers
Root: HKLM64; Subkey: Software\ClamAV; ValueType: string; ValueName: ConfDir; ValueData: {code:CommonProfileDir}\.clamwin;     Flags: uninsdeletevalue; Components: ClamAV; Check: IsAllUsers and IsWin64
Root: HKLM64; Subkey: Software\ClamAV; ValueType: string; ValueName: DataDir; ValueData: {code:CommonProfileDir}\.clamwin\db; Flags: uninsdeletevalue; Components: ClamAV; Check: IsAllUsers and IsWin64
Root: HKCU;   Subkey: Software\ClamAV; ValueType: string; ValueName: ConfDir; ValueData: {code:CommonProfileDir}\.clamwin;     Flags: uninsdeletevalue; Components: ClamAV; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\ClamAV; ValueType: string; ValueName: DataDir; ValueData: {code:CommonProfileDir}\.clamwin\db; Flags: uninsdeletevalue; Components: ClamAV; Check: not IsAllUsers
Root: HKCU64; Subkey: Software\ClamAV; ValueType: string; ValueName: ConfDir; ValueData: {code:CommonProfileDir}\.clamwin;     Flags: uninsdeletevalue; Components: ClamAV; Check: not IsAllUsers and IsWin64
Root: HKCU64; Subkey: Software\ClamAV; ValueType: string; ValueName: DataDir; ValueData: {code:CommonProfileDir}\.clamwin\db; Flags: uninsdeletevalue; Components: ClamAV; Check: not IsAllUsers and IsWin64

; ── Auto-start tray (not needed for new C++ build — clamwin.exe manages itself) ─

; ── Explorer shell extension (all users, 32-bit / Win98 / 32-bit-NT) ────────────
; HKCR on a 32-bit installer process is WOW64-redirected for CLSID keys, so this
; covers 32-bit Explorer on 32-bit Windows and 32-bit NT hosts only.
Root: HKCR;   Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90};             ValueType: string; ValueData: ClamWin Shell Extension;      Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and not IsWin64
Root: HKCR;   Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueData: {app}\bin\libExpShell.dll; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and not IsWin64
Root: HKCR;   Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueName: ThreadingModel; ValueData: Apartment;             Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and not IsWin64
Root: HKCR;   Subkey: *\shellex\ContextMenuHandlers\ClamWin;      ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and not IsWin64
Root: HKCR;   Subkey: Folder\shellex\ContextMenuHandlers\ClamWin; ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and not IsWin64

; ── Explorer shell extension (all users, 64-bit Windows) ─────────────────────────
; On 64-bit Windows the installer runs as a 32-bit process, so HKCR\CLSID writes
; are silently redirected to Wow6432Node by WOW64.  64-bit Explorer looks in the
; native (non-redirected) hive, so we must use HKCR64 for the CLSID entry.
; The ContextMenuHandlers path is exempt from WOW64 redirection and is shared.
#if IncludeX64
Root: HKCR64; Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90};             ValueType: string; ValueData: ClamWin Shell Extension;      Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and IsWin64
Root: HKCR64; Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueData: {app}\bin\libExpShell.dll; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and IsWin64
Root: HKCR64; Subkey: CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueName: ThreadingModel; ValueData: Apartment;             Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and IsWin64
Root: HKCR;   Subkey: *\shellex\ContextMenuHandlers\ClamWin;      ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and IsWin64
Root: HKCR;   Subkey: Folder\shellex\ContextMenuHandlers\ClamWin; ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: IsAllUsers and IsWin64
#endif

; ── Explorer shell extension (per-user) ─────────────────────────────────────────
; HKCU\Software\Classes\CLSID is not subject to WOW64 redirection, so a single
; set of entries works for both 32-bit and 64-bit Windows.
Root: HKCU;   Subkey: Software\Classes\CLSID\{{65713842-C410-4f44-8383-BFE01A398C90};             ValueType: string; ValueData: ClamWin Shell Extension;      Flags: uninsdeletekey; Components: ExplorerShell; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\Classes\CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueData: {app}\bin\libExpShell.dll; Flags: uninsdeletekey; Components: ExplorerShell; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\Classes\CLSID\{{65713842-C410-4f44-8383-BFE01A398C90}\InProcServer32; ValueType: string; ValueName: ThreadingModel; ValueData: Apartment;             Flags: uninsdeletekey; Components: ExplorerShell; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\Classes\*\shellex\ContextMenuHandlers\ClamWin;      ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: not IsAllUsers
Root: HKCU;   Subkey: Software\Classes\Folder\shellex\ContextMenuHandlers\ClamWin; ValueType: string; ValueData: {{65713842-C410-4f44-8383-BFE01A398C90}; Flags: uninsdeletekey; Components: ExplorerShell; Check: not IsAllUsers

[Code]

var
  AllUsers:       Boolean;
  SetupCompleted: Boolean;
  UninstallCloseAttempted: Boolean;
  Time:           String;
  PreviousVersion, ThisVersion: Integer;
  AllUsersPage:   TInputOptionWizardPage;

const
  WM_QUIT = $0012;

function FindWindow(lpClassName: string; lpWindowName: string): Integer;
  external 'FindWindowA@user32.dll stdcall';
function GetWindowThreadProcessId(hWnd: Integer; var ProcessId: Cardinal): Cardinal;
  external 'GetWindowThreadProcessId@user32.dll stdcall';
function PostThreadMessage(ThreadId: Cardinal; Msg: Cardinal; wParam: Cardinal; lParam: Cardinal): Boolean;
  external 'PostThreadMessageA@user32.dll stdcall';

//────────────────────────────────────────────────────────────────────────────
// Helpers
//────────────────────────────────────────────────────────────────────────────

function IsWin98(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  { Win98 = non-NT, major 4, minor 10 (98) or 90 (Me) }
  Result := (not Version.NTPlatform) and (Version.Major = 4) and (Version.Minor >= 10);
end;

function Is32bitNT(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  { NT 32-bit: must be NT platform, major >= 5, not 64-bit, and not Win9x }
  Result := Version.NTPlatform and (Version.Major >= 5) and (not IsWin64) and (not IsWin98());
end;

function Is64bitLegacyNT(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  Result := Version.NTPlatform and IsWin64 and (Version.Major < 6);
end;

function Is64bitModernNT(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  Result := Version.NTPlatform and IsWin64 and (Version.Major >= 6);
end;

function IsAllUsers(): Boolean;
begin
  Result := AllUsers;
end;

function BaseDir(Default: String): String;
begin
  if IsAllUsers() then
  begin
    if IsWin64 then
      Result := ExpandConstant('{pf64}')
    else
      Result := ExpandConstant('{pf}');
  end
  else
    Result := ExpandConstant('{userappdata}');
end;

function CommonProfileDir(Default: String): String;
begin
  if IsAllUsers() then
    Result := RemoveBackslash(ExpandConstant('{commonappdata}'))
  else
    Result := ExpandConstant('{userappdata}');
end;

function DesktopDir(Default: String): String;
begin
  if IsAllUsers() then
    Result := ExpandConstant('{commondesktop}')
  else
    Result := ExpandConstant('{userdesktop}');
end;

function CurTime(Default: String): String;
begin
  Result := Time;
end;

//────────────────────────────────────────────────────────────────────────────
// INI helper — used in [INI] Check: expressions
//────────────────────────────────────────────────────────────────────────────
function IsIniValueEmpty(Param: String): Boolean;
var
  Section, Key, Filename, Val, TempStr: String;
  EndPos: Integer;
begin
  TempStr := Param;

  EndPos  := Pos('*', TempStr);
  Section := Copy(TempStr, 0, EndPos - 1);
  TempStr := Copy(TempStr, EndPos + 1, Length(TempStr) - EndPos);

  EndPos := Pos('*', TempStr);
  Key    := Copy(TempStr, 0, EndPos - 1);
  TempStr := Copy(TempStr, EndPos + 1, Length(TempStr) - EndPos);

  Filename := TempStr;
  Val      := Trim(GetIniString(Section, Key, '', Filename));
  Result   := (Val = '');
end;

function IsClamWinRunning(): Boolean;
forward;

function PostQuitToClamWin(): Boolean;
forward;

procedure ForceKillClamWin();
forward;

//────────────────────────────────────────────────────────────────────────────
// CVD helpers — used in [Files] Check: and [InstallDelete] Check:
//────────────────────────────────────────────────────────────────────────────
function NoMainCld(): Boolean;
var Temp: String;
begin
  Result := not FileExists(CommonProfileDir(Temp) + '\.clamwin\db\main.cld');
end;

function NoDailyCld(): Boolean;
var Temp: String;
begin
  Result := not FileExists(CommonProfileDir(Temp) + '\.clamwin\db\daily.cld');
end;

function NoBytecodeCld(): Boolean;
var Temp: String;
begin
  Result := not FileExists(CommonProfileDir(Temp) + '\.clamwin\db\bytecode.cld');
end;

// Delete old CVD only when upgrading from a version that used a different format
function IsDeleteCvd(): Boolean;
begin
  Result := (PreviousVersion > 0) and (PreviousVersion < 10501);
end;

//────────────────────────────────────────────────────────────────────────────
// Close the old ClamTray if it is running
//────────────────────────────────────────────────────────────────────────────
procedure CloseClamTray();
var
  i: Integer;
begin
  if not CheckForMutexes('ClamWinMutex') then exit;

  if SuppressibleMsgBox(
      'The Setup detected that ClamWin is currently running.' + #13 +
      'Would you like to close it now? (Recommended)',
      mbConfirmation, MB_YESNO, IDYES) = idYes then
  begin
    PostQuitToClamWin();

    for i := 1 to 30 do
    begin
      Sleep(200);
      if not CheckForMutexes('ClamWinMutex') then
        exit;
    end;

    ForceKillClamWin();

    for i := 1 to 10 do
    begin
      Sleep(200);
      if not CheckForMutexes('ClamWinMutex') then
        exit;
    end;

    SuppressibleMsgBox(
      'ClamWin is still running. Please close clamwin.exe manually and retry Setup.',
      mbError, MB_OK, IDOK);
  end;
end;

function IsClamWinRunning(): Boolean;
begin
  Result := CheckForMutexes('ClamWinMutex');
end;

function PostQuitToClamWin(): Boolean;
var
  hwnd: Integer;
  processId, threadId: Cardinal;
begin
  Result := False;
  hwnd := FindWindow('ClamWinTrayClass', '');
  if hwnd = 0 then
    exit;

  processId := 0;
  threadId := GetWindowThreadProcessId(hwnd, processId);
  if threadId <> 0 then
    Result := PostThreadMessage(threadId, WM_QUIT, 0, 0);
end;

procedure ForceKillClamWin();
var
  resultcode: Integer;
begin
  Exec(ExpandConstant('{cmd}'), '/C taskkill /IM clamwin.exe /T /F >nul 2>&1 & tskill clamwin >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, resultcode);
end;

procedure CloseClamWinForUninstall();
var
  i: Integer;
begin
  if not IsClamWinRunning() then
    exit;

  PostQuitToClamWin();

  for i := 1 to 30 do
  begin
    Sleep(200);
    if not IsClamWinRunning() then
      exit;
  end;

  ForceKillClamWin();
end;

//────────────────────────────────────────────────────────────────────────────
// Wizard page skip logic
//────────────────────────────────────────────────────────────────────────────
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if PageID = AllUsersPage.ID then
    Result := not IsAdminLoggedOn()
  else
    Result := False;
end;

//────────────────────────────────────────────────────────────────────────────
// Next-button click handler
//────────────────────────────────────────────────────────────────────────────
function NextButtonClick(CurPage: Integer): Boolean;
begin
  Result := True;
  if CurPage = wpFinished then
    SetupCompleted := True
  else if CurPage = AllUsersPage.ID then
  begin
    case AllUsersPage.SelectedValueIndex of
      0: AllUsers := True;
      1: AllUsers := False;
    end;
  end
  else if CurPage = wpReady then
  begin
    CloseClamTray();
    Result := not IsClamWinRunning();
  end;
end;

//────────────────────────────────────────────────────────────────────────────
// Store AllUsers choice for next run
//────────────────────────────────────────────────────────────────────────────
procedure RegisterPreviousData(PreviousDataKey: Integer);
begin
  case AllUsersPage.SelectedValueIndex of
    0: SetPreviousData(PreviousDataKey, 'AllUsersMode', 'anyone');
    1: SetPreviousData(PreviousDataKey, 'AllUsersMode', 'onlyme');
  end;
end;

//────────────────────────────────────────────────────────────────────────────
// Initialise
//────────────────────────────────────────────────────────────────────────────
function InitializeSetup(): Boolean;
var value: Cardinal;
begin
  Result      := True;
  AllUsers    := IsAdminLoggedOn();
  ThisVersion := 10502;   { 1.5.2.x encoded as major*10000 + minor*100 + patch }
  Time        := GetDateTimeString('hh:nn', #0, ':') + ':00';

  value := 0;
  if not RegQueryDWordValue(HKEY_CURRENT_USER, 'SOFTWARE\ClamWin', 'Version', value) then
  begin
    value := 0;
    RegQueryDWordValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\ClamWin', 'Version', value);
  end;
  PreviousVersion := value;

  if PreviousVersion > ThisVersion then
  begin
    SuppressibleMsgBox(
      'Setup detected that a newer version of ClamWin is already installed.' + #13 +
      'Setup will now exit.',
      mbError, MB_OK, IDOK);
    Result := False;
  end;

  SetupCompleted := False;
end;

//────────────────────────────────────────────────────────────────────────────
// Wizard init — create the all-users selector page
//────────────────────────────────────────────────────────────────────────────
procedure InitializeWizard;
begin
  AllUsersPage := CreateInputOptionPage(wpLicense,
    'Select Installation Options',
    'Who should this application be installed for?',
    'Please select whether you wish to make this software available to all users or just yourself.',
    True, False);
  AllUsersPage.Add('&Anyone who uses this computer (all users)');
  AllUsersPage.Add('Only for &me (' + GetUserNameString() + ')');

  case GetPreviousData('AllUsersMode', '') of
    'anyone': AllUsers := True;
    'onlyme': AllUsers := False;
  end;
  if AllUsers then
    AllUsersPage.SelectedValueIndex := 0
  else
    AllUsersPage.SelectedValueIndex := 1;
end;

{ Returns the freshclam.conf path alongside ClamWin.conf in the profile dir. }
function ClamWinConfPath(Default: String): String;
begin
  Result := CommonProfileDir(Default) + '\.clamwin\ClamWin.conf';
end;

function ClamWinPostInstallParams(Default: String): String;
begin
  if IsTaskSelected('DownloadDB') then
    Result := '--mode=update --close'
  else
    Result := '--open-dashboard';
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if (CurUninstallStep = usUninstall) and (not UninstallCloseAttempted) then
  begin
    UninstallCloseAttempted := True;
    CloseClamWinForUninstall();
  end;
end;
