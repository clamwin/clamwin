@echo off
set LIBS=odbc32.lib odbccp32.lib comctl32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib
set DEFINES=/D"WINVER=0x0500" /D "WIN32" /D "_CRT_SECURE_NO_DEPRECATE" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "BALLOONTIP_EXPORTS" /I "%PYTHONDIR%\include"

call "%VCINSTALLDIR%\vcvarsall.bat" x86
set LIB=%LIB%;%PYTHONDIR%\libs
:: 32 bit ansi
echo Building 32bit Release Ansi
mkdir Release
cl %DEFINES% /O1 /FD /EHsc /MT /Fo".\Release/" /Fd".\Release/" /Yc"stdafx.h" /Fp".\Release/BalloonTip.pch" /Fo".\Release/" /Fd".\Release/" /W3 /c /TP /Yc"stdafx.h" /Fp".\Release/BalloonTip.pch" .\StdAfx.cpp
if not "%ERRORLEVEL%"=="0" goto END  
cl %DEFINES% /O1 /FD /EHsc /MT /Fo".\Release/" /Fd".\Release/" /Yu"stdafx.h" /Fp".\Release/BalloonTip.pch" /Fo".\Release/" /Fd".\Release/" /W3 /c /TP /Yc"stdafx.h" /Fp".\Release/BalloonTip.pch" .\BalloonTip.cpp .\BalloonHelp.cpp
if not "%ERRORLEVEL%"=="0" goto END  
link.exe  /OUT:"../BalloonTip.pyd" /INCREMENTAL:NO /NOLOGO /DLL /PDB:".\Release/BalloonTip.pdb" /IMPLIB:".\Release/BalloonTip.lib" /MACHINE:X86 %LIBS% .\Release\BalloonHelp.obj .\Release\BalloonTip.obj .\Release\StdAfx.obj
if not "%ERRORLEVEL%"=="0" goto END  


:END


