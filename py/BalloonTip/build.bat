mkdir Release
"%MSCL%" /O1 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "BALLOONTIP_EXPORTS" /FD /EHsc /MT /Yc"stdafx.h" /Fp".\Release/BalloonTip.pch" /Fo".\Release/" /Fd".\Release/" /W3 /c /TP .\StdAfx.cpp
if not "%ERRORLEVEL%"=="0" goto END  
"%MSCL%" /O1 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "BALLOONTIP_EXPORTS" /FD /EHsc /MT /Yu"stdafx.h" /Fp".\Release/BalloonTip.pch" /Fo".\Release/" /Fd".\Release/" /W3 /c /TP .\BalloonTip.cpp .\BalloonHelp.cpp
if not "%ERRORLEVEL%"=="0" goto END  
"%MSLINK%" /OUT:"../BalloonTip.pyd" /INCREMENTAL:NO /NOLOGO /DLL /PDB:".\Release/BalloonTip.pdb" /IMPLIB:".\Release/BalloonTip.lib" /MACHINE:X86 odbc32.lib odbccp32.lib comctl32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib .\Release\BalloonHelp.obj .\Release\BalloonTip.obj .\Release\StdAfx.obj
if not "%ERRORLEVEL%"=="0" goto END  

:END


