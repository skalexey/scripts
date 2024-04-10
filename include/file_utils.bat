@echo off

REM Define a function "symlink":
REM 	- If the second argument does not exist, create a symlink to the first argument with the path in the second argument
REM 	- If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
REM 	- If the first argument is a file, create a symlink to it with the path in the second argument
REM 	- If the first argument is a directory, create a symlink to it with the path in the second argument

:symlink
	REM Get the basename + extension of the first argument
	set base_name=%~nx2
	REM If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
	if EXIST %2\ set mklink_args= /D
	REM Check if %3 is a directory
	if EXIST %3 /A:-D EXIT /B 1
	if EXIST %3\ (MKLINK%mklink_args% %3\%base_name% %2) ELSE (EXIT /B 2)
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
