rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\0.90\clamwin
set ISTOOLDIR=C:\Program Files (x86)\ISTool
set SEVENZIP=C:\Program Files\7-Zip\7z.exe
set UPX_UTIL=C:\tools\upx.exe

set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio 8\VC

set MSSDKDIR=C:\Program Files\Microsoft Platform SDK
set PYTHONDIR=C:\python23

set WGET_UTIL=c:\tools\wget.exe
set DB_MIRROR=db.au.clamav.net

rem build pyclamav
cd ..\addons\pyc
call build.cmd release
copy .\build\lib.win32-2.3\pyc.pyd "%THISDIR%\py"
if not "%ERRORLEVEL%"=="0" goto ERROR

rem build ExplorerShell
rem cd %THISDIR%\cpp
rem call build.bat
rem if not "%ERRORLEVEL%"=="0" goto ERROR
rem cd ..\
rem build BalloonTip.pyd
rem cd py\BalloonTip
rem call build.bat
rem if not "%ERRORLEVEL%"=="0" goto ERROR

rem build py2exe binaries
cd %THISDIR%\setup\py2exe
rd dist /s /q 
call "%PYTHONDIR%\python" setup_all.py
if not "%ERRORLEVEL%"=="0" goto ERROR

rem recompress library with max compression
rem cd dist\lib
rem call "%SEVENZIP%" -aoa x clamwin.zip -olibrary\ 
rem del clamwin.zip
rem cd library
rem call "%SEVENZIP%" a -tzip -mx9 ..\clamwin.zip -r
rem cd ..
rd library /s /q 

rem upx all files now
rem call "%UPX_UTIL%" -9 *.* 
rem cd ..\bin
rem call "%UPX_UTIL%" -9 *.* 

rem cd ..\..\..\..\


rem get the latest db files
call %WGET_UTIL% http://%DB_MIRROR%/main.cvd -N -O "%THISDIR%\Setup\cvd\main.cvd"
if not "%ERRORLEVEL%"=="0" goto ERROR
call %WGET_UTIL% http://%DB_MIRROR%/daily.cvd -N -O "%THISDIR%\Setup\cvd\daily.cvd"
if not "%ERRORLEVEL%"=="0" goto ERROR
call %WGET_UTIL% http://%DB_MIRROR%/bytecode.cvd -N -O "%THISDIR%\Setup\cvd\bytecode.cvd"
if not "%ERRORLEVEL%"=="0" goto ERROR

rem build setups
call "%ISTOOLDIR%\ISTool.exe" -compile "%THISDIR%\Setup\Setup-nodb.iss"
if not "%ERRORLEVEL%"=="0" goto ERROR

rem move nodb setup to -nodb file
del "%THISDIR%\Setup\Output\Setup-nodb.exe"
move "%THISDIR%\Setup\Output\Setup.exe" "%THISDIR%\Setup\Output\Setup-nodb.exe"
if not "%ERRORLEVEL%"=="0" goto ERROR

call "%ISTOOLDIR%\ISTool.exe" -compile "%THISDIR%\Setup\Setup.iss"
if not "%ERRORLEVEL%"=="0" goto ERROR

goto END

:ERROR
@echo an error occured
pause

:end

