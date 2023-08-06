@echo off
if [%1]==[help] GOTO :help
if [%1]==[--help] GOTO :help
if [%1]==[h] GOTO :help
if [%1]==[-h] GOTO :help
if [%1]==[?] GOTO :help
if [%1]==[-?] GOTO :help
if [%1]==[] GOTO :help

if [%2]==[] GOTO :pkghelp

SET TMPCOUNTER=0
SET TMPPARAMS=
FOR %%p in (%*) DO CALL :makeparams %%p 3

REM python -m dhi.platform.cli.%1.%2 %3 %4 %5 %6 %7 %8 %9
python -m dhi.platform.cli.%1.%2 %TMPPARAMS%
GOTO :end

:help
ECHO %~n0 cfg		Platform configuration operations
ECHO     ds		Platform dataset operations
ECHO     eng		Platform engine execution operations
ECHO     prj		Platform project operations
ECHO     prjm	Platform project member operations
ECHO     raw		Platform raw service operations
ECHO     rb		Platform recycle bin operations
ECHO     reader	Platform readers operations
ECHO     tr		Platform transfers operations
ECHO     ts		Platform time series operations
ECHO     writer	Platform writers operations
ECHO     gw		Platform gateway operations
GOTO end

:pkghelp
python -m dhi.platform.cli.help dhi.platform.cli.%1
GOTO :end

:makeparams
IF NOT DEFINED TMPCOUNTER SET TMPCOUNTER=0
SET /A TMPCOUNTER+=1
IF %TMPCOUNTER% EQU %2 SET TMPPARAMS=%1
IF %TMPCOUNTER% GTR %2 SET TMPPARAMS=%TMPPARAMS% %1
EXIT /B

:end
SET TMPCOUNTER=
SET TMPPARAMS=
