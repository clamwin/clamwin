rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\0.35\clamwin
set ISTOOLDIR=D:\Program Files\ISTool

set VC7DIR=D:\Program Files\Microsoft Visual C++ Toolkit 2003
set MSSDKDIR=H:\MSSDK_XP
set PYTHONDIR=c:\python23

call "%VC7DIR%\vcvars32.bat"
set MSRC=%MSSDKDIR%\Bin\RC.exe
set MSCL=%VC7DIR%\bin\cl.exe
set MSLINK=%VC7DIR%\bin\link.exe
set INCLUDE=%VC7DIR%\include;%MSSDKDIR%\Include;%PYTHONDIR%\include
set LIB=%VC7DIR%\lib;%MSSDKDIR%\lib;%PYTHONDIR%\libs
rem set CFLAGS=-march=i386

if not "%1"=="ALL" goto _short
rem build cygwin part of it
call %CYGWINDIR%\bin\bash --login "%thisdir%\build.sh"
if not "%ERRORLEVEL%"=="0" goto ERROR  
:_short 
rem build BalloonTip.pyd
cd py\BalloonTip
call build.bat
if not "%ERRORLEVEL%"=="0" goto ERROR  
cd ..\..\
rem build py2exe binaries
cd setup\py2exe
call python setup_all.py 
if not "%ERRORLEVEL%"=="0" goto ERROR  
rem build ExplorerShell
cd ..\..\cpp
call build.bat
if not "%ERRORLEVEL%"=="0" goto ERROR  
cd ..\
rem build setup
call "%ISTOOLDIR%\ISTool.exe" -compile "%THISDIR%\Setup\Setup.iss"
if not "%ERRORLEVEL%"=="0" goto ERROR  

goto END

:ERROR
@echo an error occured
pause

:end

