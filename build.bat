rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\clamwin
set ISTOOLDIR=C:\Program Files (x86)\ISTool

set VC7DIR=C:\Program Files (x86)\Microsoft Visual C++ Toolkit 2003
set VC8BUILD=C:\Program Files\Microsoft Visual Studio 8\VC\VCPackages\vcbuild.exe
set MSSDKDIR=C:\Program Files\Microsoft Platform SDK
set PYTHONDIR=C:\python23

set MSRC=%MSSDKDIR%\Bin\RC.exe
set MSCL=%VC7DIR%\bin\cl.exe
set MSLINK=%VC7DIR%\bin\link.exe
set INCLUDE=%VC7DIR%\include;%MSSDKDIR%\Include;%PYTHONDIR%\include
set LIB=%VC7DIR%\lib;%MSSDKDIR%\lib;%PYTHONDIR%\libs
rem set CFLAGS=-march=i386

if not "%1"=="ALL" goto _short
rem build clamav native port
call "%VC8BUILD%" .\clamav-devel\contrib\msvc\clamav.sln "Release|Win32"
if not "%ERRORLEVEL%"=="0" goto ERROR  
:_short 
call "%VC7DIR%\vcvars32.bat"
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

