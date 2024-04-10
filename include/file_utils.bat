@echo off

REM Define a function "symlink":
REM 	- If the second argument does not exist, create a symlink to the first argument with the path in the second argument
REM 	- If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
REM 	- If the first argument is a file, create a symlink to it with the path in the second argument
REM 	- If the first argument is a directory, create a symlink to it with the path in the second argument

:symlink
	REM Get the basename + extension of the first argument
	set base_name=%~nx2
	set what=%2
	set where=%3
	REM If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
	if EXIST %what%\ set mklink_args= /D
	REM Ensure if there is no file pointing at %where
	set where_complete=%where%
	if EXIST %where% /A EXIT /B 1 else if EXIST %where% /D set where_complete=%where%\%base_name%
	set cmd=MKLINK%mklink_args% %where_complete% %what% 
	REM Call the cmd
	REM echo Command: %cmd%
	%cmd%
EXIT /B 0

REM Equivalent to bash's:
REM if [ "$#" -gt 0 ]; then
REM		__init__
REM		$@
REM fi

if "%~1" neq "" (
	REM Call a function with the name of the first argument and pass the rest of the arguments to it
	call :%~1 %*
)
