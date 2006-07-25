rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\clamwin
set ISTOOLDIR=C:\Program Files (x86)\ISTool

set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio 8\VC

set MSSDKDIR=C:\Program Files\Microsoft Platform SDK
set PYTHONDIR=C:\python23

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
rem build py2exe binaries
cd setup\py2exe
call %PYTHONDIR%\python setup_all.py 
if not "%ERRORLEVEL%"=="0" goto ERROR  
rem build setup
call "%ISTOOLDIR%\ISTool.exe" -compile "%THISDIR%\Setup\Setup.iss"
if not "%ERRORLEVEL%"=="0" goto ERROR  

goto END

:ERROR
@echo an error occured
pause

:end

