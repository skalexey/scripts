@echo off

REM Define a function "symlink":
REM 	- If the second argument does not exist, create a symlink to the first argument with the path in the second argument
REM 	- If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
REM 	- If the first argument is a file, create a symlink to it with the path in the second argument
REM 	- If the first argument is a directory, create a symlink to it with the path in the second argument

:symlink
	REM Get the basename + extension of the first argument
	set what=%2
	set where=%3
	if EXIST %what% /A:-D set base_name=%~nx2 else (
		for %%F in ("%what%") do set base_name=%%~nxF
	)
	echo base_name: %base_name%
	REM If the second argument exists, and it is a directory, create a symlink to the first argument in this directory
	if EXIST %what%\ set mklink_args= /D
	REM Ensure if there is no file pointing at %where
	set where_complete=%where%
	if EXIST %where% (
		if EXIST %where%\* (
			REM echo %where% is a directory
			set where_complete=%where%\%base_name%
		) else (
			REM echo %where% is a file
			EXIT /B 1
		)
	)
	set cmd=MKLINK%mklink_args% %where_complete% %what% 
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
