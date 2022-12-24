$logFname = $(Get-Date).ToString("yyyy-MM-dd_HH-mm-ss") + ".log"
$resultLogFname = "out_" + $logFname
$curPath = $(pwd).Path + "\"
$logFpath = $curPath + $logFname
$resultLogFpath = $curPath + $resultLogFname
Write-Host "$logFpath"
"Hello World" >> $logFpath
"Hello World" >> $logFpath
"Hello World" >> $logFpath

function Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Msg,
		[Parameter(Mandatory=$false)]
        [string]$Color
    )
	if ($Color) {
		Write-Host $Msg -ForegroundColor $Color
	} else {
		Write-Host $Msg
	}
    $Msg >> $logFpath
}

function LogInfo {
	param(
		[Parameter(Mandatory=$true)]
		[string]$Msg
	)
	Log -Msg $Msg -Color Cyan
}
function LogSuccess {
	param(
		[Parameter(Mandatory=$true)]
		[string]$Msg
	)
	Log -Msg $Msg -Color DarkGreen
}


Log -Msg "Test log"
LogInfo -Msg "Test info"
LogSuccess -Msg "Test success"

function RunAndLogCommand {
	param(
		[Parameter(Mandatory=$true)]
		[string]$Cmd
	)

	# Log the command
	$Cmd >> $logFpath
	$result = Invoke-Expression $Cmd

	# Log the full log
	$Cmd >> $resultLogFpath
	$result >> $resultLogFpath
}

RunAndLogCommand -Cmd "dir"
RunAndLogCommand -Cmd 'start "C:\Users\skoro\tmp\tmp.bat" /S'

exit

function LogError {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Msg,
		[Parameter(Mandatory=$false)]
        [bool]$Stop = $false
    )
	if ($Stop) {
    	Write-Error -Message $Msg -ErrorAction Stop
	} else {
		Write-Error -Message $Msg
	}
    "Error: " + $Msg >> $logFpath
}

LogError -Msg "An error"

Write-Host "Test 1"

LogError -Msg "The error 2" -Stop 1

Write-Host "A test 2"
