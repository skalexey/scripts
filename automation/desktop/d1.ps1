using module Rectangle
Import-Module Rectangle -Force
Import-Module WindowUtils -Force
Import-Module Log -Force

###########################################################################################

$global:registeredWindows = @();

function startProcessImpl {
	param ([PSCustomObject]$e)
	LogInfo "startProcess"
	if ($e.Args -And ($e.Args.Count -gt 0)) {
		Start-Process $e.Path -ArgumentList $e.Args
	} else {
		Start-Process $e.Path
	}
}

function startProcess {
	param ([PSCustomObject]$e)
	startProcessImpl $e;
}

function startVSCode {
	param ([PSCustomObject]$e)
	LogInfo "startVSCode"
	if (IsProcessRunning $e.ProcessName) {
		LogInfo "Window $e.Id is running"
		return
	}
	startProcess $e
	$started = $false
	Do {
		$status = Get-Process $e.ProcessName -ErrorAction SilentlyContinue
		If (!($status)) { Write-Host 'Waiting for process to start' ; Start-Sleep -Seconds 1 }
		Else { Write-Host 'VS has started' ; $started = $true }
	}
	Until ( $started )
	Start-Sleep 1
}

function startSkipSplash {
	param ([PSCustomObject]$e)
	LogInfo "startSkipSplash"
	startProcess $e
	$started = $false
	Do {
		$status = Get-Process $e.ProcessName -ErrorAction SilentlyContinue
		$ret = GetWindowBounds $e.ProcessName
		if ($status) {
			Log 'Teams has started. Checking bounds...'
			if ($ret) {
				$r = $ret.Rect
				if (($r.w -gt $e.Splash.w) -and ($r.h -gt $e.Splash.h)) {
					Log "Found non-slpash window with bouds: $($r.x), $($r.y), $($r.w), $($r.h)"
					$started = $true
				} else {
					Log "Found splash window with bouds: $($r.x), $($r.y), $($r.w), $($r.h)"
				}
			} else {
				Log "Bouds: null"
			}
		} else {
			Log 'Waiting for process to start'
		}
		Start-Sleep -Seconds 1
	}
	Until ( $started )
	Start-Sleep 1
}

function startTeams {
	param ([PSCustomObject]$e)
	LogInfo "startTeams"
	if (IsProcessRunning $e.ProcessName) {
		LogInfo "Window $e.Id is running"
		return
	}
	startSkipSplash $e
}

function startChrome {
	param ([PSCustomObject]$e)
	LogInfo "startChrome"
	startProcess $e
}
function RegisterWindow {
	param (
		[string]$id,
		[string]$processName,
		[string]$path,
		[string[]]$launchArgs,
		[Rectangle]$position,
		[Rectangle]$splash,
		[scriptblock]$startProcessFunc=$function:startProcess
	)

	LogInfo "Registering window $id, $processName, $path, $launchArgs, $startProcessFunc"

	$global:registeredWindows += [PSCustomObject]@{
		Id=$id
		ProcessName=$processName
		Path=$path
		Args=$launchArgs
		Position=$position
		Splash=$splash
		Func=$startProcessFunc
	}
}

RegisterWindow "teams" "teams" '~\AppData\Local\Microsoft\Teams\Update.exe' @(
	'--processStart "Teams.exe"'
	) (ScreenRect 0 0.5 0.4 0.5) (Rect -1 -1 440 248) $function:startTeams


$chrome1Rect = $(ScreenRect 0 0 0.5 1.0)
RegisterWindow "chrome1" "chrome" "C:\Program Files\Google\Chrome\Application\chrome.exe" @(
	# "--login-profile=Alex"
	"--profile-email=skorohodov-ad@narod.ru"
	, "--window-position=$($chrome1Rect.x),$($chrome1Rect.y)"
	, "--window-size=$($chrome1Rect.w),$($chrome1Rect.h)"
	, "--new-window https://vllibrary.tech"
	# , "--app=https://vllibrary.tech"
	) $null $null $function:startChrome

$chrome2Rect = $(ScreenRect 0.5 0 0.5 1.0)
RegisterWindow "chrome2" "chrome" "C:\Program Files\Google\Chrome\Application\chrome.exe" @(
	# "--login-profile=Alex"
	"--profile-email=alexeiskorokhodov@gmail.com"
	, "--window-position=$($chrome2Rect.x),$($chrome2Rect.y)"
	, "--window-size=$($chrome2Rect.w),$($chrome2Rect.h)"
	, "--new-window https://vllibrary.tech"
	# , "--app=https://vllibrary.tech"
	) $null $null $function:startChrome
	

RegisterWindow "vs code" "code" '~\AppData\Local\Programs\Microsoft VS Code\Code' @(
	'~\Projects\arkanoid'
	) (ScreenRect 0.4 0 0.6 1.0) $null $function:startVSCode


foreach ($e in $registeredWindows) {
	$($e.Func.Invoke($e))
	if ($PSItem.Exception) {
		LogError "Failed to call start process function for the process '$($e.Id)'. Exit."
		Exit 1
	}

	# $r = GetWindowBounds $e.ProcessName
	# $r = GetWindowBounds $e.ProcessName
	# if (-not $r) {
	# 	LogError "Failed to get window bounds for the process '$($e.Id)'. Exit."
	# 	Exit 2
	# }
	$p = $e.Position
	if ($p) {
		$r = GetWindowBounds $e.ProcessName
		[NativeMethods]::MoveWindow($r.Handle, $p.x, $p.y, $p.w, $p.h, $true)
	}
}

exit
# LayoutWindow ""