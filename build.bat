rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\0.90\clamwin
set ISTOOLDIR=C:\Program Files (x86)\ISTool

set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio 8\VC

set MSSDKDIR=C:\Program Files\Microsoft Platform SDK
set PYTHONDIR=C:\python23

set WGET_UTIL=c:\tools\wget.exe
set DB_MIRROR=db.au.clamav.net
rem build ExplorerShell
cd cpp
call build.bat
if not "%ERRORLEVEL%"=="0" goto ERROR
cd ..\
rem build BalloonTip.pyd
cd py\BalloonTip
call build.bat
if not "%ERRORLEVEL%"=="0" goto ERROR
cd ..\..\
rem build pyclamav
cd ..\..\..\addons\pyclamav
call build.cmd
if not "%ERRORLEVEL%"="0" goto ERROR
cd ..\..\clamwin
rem build py2exe binaries
cd setup\py2exe
call %PYTHONDIR%\python setup_all.py
if not "%ERRORLEVEL%"=="0" goto ERROR

rem get the latest db files
call %WGET_UTIL% http://%DB_MIRROR%/main.cvd -O "%THISDIR%\Setup\cvd\main.cvd"
if not "%ERRORLEVEL%"=="0" goto ERROR
call %WGET_UTIL% http://%DB_MIRROR%/daily.cvd -O "%THISDIR%\Setup\cvd\daily.cvd"
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

