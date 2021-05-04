rem @echo off
set CYGWINDIR=d:\cygwin
set THISDIR=l:\Projects\ClamWin\src\clamwin
set ISTOOLDIR=C:\Program Files (x86)\ISTool
set SEVENZIP=C:\Program Files\7-Zip\7z.exe
set UPX_UTIL=C:\tools\upx.exe

set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio 8\VC

set MSSDKDIR=C:\Program Files\Microsoft Platform SDK
set PYTHONDIR=C:\python23

set WGET_UTIL=c:\tools\wget.exe
set DB_MIRROR=db.au.clamav.net


rem get the latest db files
rem call %WGET_UTIL% http://%DB_MIRROR%/main.cvd -N -O "%THISDIR%\Setup\cvd\main.cvd"
rem if not "%ERRORLEVEL%"=="0" goto ERROR
rem call %WGET_UTIL% http://%DB_MIRROR%/daily.cvd -N -O "%THISDIR%\Setup\cvd\daily.cvd"
rem if not "%ERRORLEVEL%"=="0" goto ERROR
rem call %WGET_UTIL% http://%DB_MIRROR%/bytecode.cvd -N -O "%THISDIR%\Setup\cvd\bytecode.cvd"
rem if not "%ERRORLEVEL%"=="0" goto ERROR

rem build setups
call "%ISTOOLDIR%\ISTool.exe" -compile "%THISDIR%\Setup\Setup-nodb.iss"
if not "%ERRORLEVEL%"=="0" goto ERROR

move nodb setup to -nodb file
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

