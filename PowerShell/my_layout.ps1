Import-Module WindowUtils -Force
Import-Module Log -Force
# Helper functions for building the class
###########################################################################################

$global:registeredWindows = @();

function startProcess {
	param ([PSCustomObject]$e)
	Start-Process $e.Path -ArgumentList $e.Args
}

function startVS {
	param ([PSCustomObject]$e)
	startProcess $e
	$started = $false
	Do {
		$status = Get-Process $e.ProcessName -ErrorAction SilentlyContinue
		If (!($status)) { Write-Host 'Waiting for process to start' ; Start-Sleep -Seconds 1 }
		Else { Write-Host 'VS has started' ; $started = $true }
	}
	Until ( $started )
}

function RegisterWindow {
	param (
		[string]$id,
		[string]$processName,
		[string]$path,
		[string[]]$launchArgs,
		[scriptblock]$startProcessFunc=$function:startVS
	)

	LogInfo "Registering window $id, $processName, $path, $launchArgs, $startProcessFunc"

	$global:registeredWindows += [PSCustomObject]@{
		Id=$id;
		ProcessName=$processName;
		Path=$path;
		Args=$launchArgs;
		Func=$startProcessFunc;
	}
}

RegisterWindow "vs" "devenv" 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Visual Studio 2022' @(
	'/nosplash'
	, '/command File.OpenProject "C:\Users\skoro\Projects\arkanoid\Build-cmake\arkanoid.sln"'
	)

foreach ($e in $registeredWindows) {
	if (IsProcessRunning $e.ProcessName) {
		LogInfo "Window $e.Id is running"
	}
	else {
		Log "Window $($e.Id) is not running. Run it"
		$($e.Func.Invoke($e))
	}

	$r = GetWindowBounds $e.ProcessName
	[NativeMethods]::MoveWindow($r.Handler, 0, 0, 800, 800, $true)
}


# LayoutWindow ""