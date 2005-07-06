mkdir Release
"%MSRC%" /d "NDEBUG" /l 0x409 /fo".\Release/ExplorerShell.res" .\ExplorerShell.rc
if not "%ERRORLEVEL%"=="0" goto END  
"%MSCL%" /O1 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "EXPLORERSHELL_EXPORTS" /FD /EHsc /MT /YX"stdafx.h" /Fp".\Release/ExplorerShell.pch" /Fo".\Release/" /Fd".\Release/" /W3 /c /TP .\ShellExtImpl.cpp .\ShellExt.cpp
if not "%ERRORLEVEL%"=="0" goto END  
"%MSLINK%" /OUT:".\Release/ExpShell.dll" /INCREMENTAL:NO /NOLOGO /DLL /DEF:".\ExplorerShell.def" /PDB:".\Release/ExplorerShell.pdb" /IMPLIB:".\Release/ExplorerShell.lib" /MACHINE:X86  kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib .\Release\ExplorerShell.res .\Release\ShellExt.obj .\Release\ShellExtImpl.obj
if not "%ERRORLEVEL%"=="0" goto END  
:END




