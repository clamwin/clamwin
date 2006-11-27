@echo off

set LIBS=kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib advapi32.lib shell32.lib ole32.lib 
set DEFINES=/D "WIN32" /D "_CRT_SECURE_NO_DEPRECATE" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "EXPLORERSHELL_EXPORTS"
set UNICODE=/D "UNICODE" /D "_UNICODE"

call "%VCINSTALLDIR%\vcvarsall.bat" x86

:: 32 bit unicode
echo Building 32bit Release Unicode
mkdir Release_Unicode
rc.exe /d "NDEBUG" /l 0x409 /fo".\Release_Unicode/ExplorerShell.res" .\ExplorerShell.rc
if not "%ERRORLEVEL%"=="0" goto END
cl /O1 %DEFINES% %UNICODE% /O1 /FD /EHsc /MT /Fo".\Release_Unicode/" /Fd".\Release_Unicode/" /W3 /c /TP .\ShellExtImpl.cpp .\ShellExt.cpp
if not "%ERRORLEVEL%"=="0" goto END
link.exe /OUT:".\Release_Unicode/ExpShell.dll" /INCREMENTAL:NO /NOLOGO /DLL /DEF:".\ExplorerShell.def" /PDB:".\Release_Unicode/ExplorerShell.pdb" /IMPLIB:".\Release_Unicode/ExplorerShell.lib" /MACHINE:X86 .\Release_Unicode\ExplorerShell.res .\Release_Unicode\ShellExt.obj .\Release_Unicode\ShellExtImpl.obj %LIBS%
if not "%ERRORLEVEL%"=="0" goto END

:: 32 bit ansi
echo Building 32bit Release Ansi
mkdir Release
rc.exe /d "NDEBUG" /l 0x409 /fo".\Release/ExplorerShell.res" .\ExplorerShell.rc
if not "%ERRORLEVEL%"=="0" goto END
cl /O1 %DEFINES% /O1 /FD /EHsc /MT /Fo".\Release/" /Fd".\Release/" /W3 /c /TP .\ShellExtImpl.cpp .\ShellExt.cpp
if not "%ERRORLEVEL%"=="0" goto END
link.exe /OUT:".\Release/ExpShell.dll" /INCREMENTAL:NO /NOLOGO /DLL /DEF:".\ExplorerShell.def" /PDB:".\Release/ExplorerShell.pdb" /IMPLIB:".\Release/ExplorerShell.lib" /MACHINE:X86 .\Release\ExplorerShell.res .\Release\ShellExt.obj .\Release\ShellExtImpl.obj %LIBS%
if not "%ERRORLEVEL%"=="0" goto END

:: 64 bit unicode
call "%VCINSTALLDIR%\vcvarsall.bat" x86_amd64

echo Building 64bit Release Unicode
mkdir Release_x64
rc.exe /d "NDEBUG" /l 0x409 /fo".\Release_x64/ExplorerShell.res" .\ExplorerShell.rc
if not "%ERRORLEVEL%"=="0" goto END
cl /Wp64 /O1 %DEFINES% /O1 /FD /EHsc /MT /Fo".\Release_x64/" /Fd".\Release_x64/" /W3 /c /TP .\ShellExtImpl.cpp .\ShellExt.cpp
if not "%ERRORLEVEL%"=="0" goto END
link.exe /OUT:".\Release_x64/ExpShell64.dll" /INCREMENTAL:NO /NOLOGO /DLL /DEF:".\ExplorerShell.def" /PDB:".\Release_x64/ExplorerShell.pdb" /IMPLIB:".\Release_x64/ExplorerShell.lib" /MACHINE:X64 .\Release_x64\ExplorerShell.res .\Release_x64\ShellExt.obj .\Release_x64\ShellExtImpl.obj %LIBS%
if not "%ERRORLEVEL%"=="0" goto END

:END
