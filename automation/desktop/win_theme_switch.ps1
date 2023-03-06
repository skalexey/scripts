Import-Module ProcessUtils

if ($args.Count -eq 0)
{
	Write-Host "No theme specified (pass light or dark)" -ForegroundColor Red
	exit 1
}
$opt = $args[0]
if ($opt -eq "light")
{
	Write-Host "Switching desktop to light theme"
	#$theme = "C:\Windows\Resources\Themes\Light.theme"
	$theme = "$Env:LocalAppData\Microsoft\Windows\Themes\CustomLight.theme"
	
}
elseif ($opt -eq "dark")
{
	Write-Host "Switching desktop to dark theme"
	# $theme = "C:\Windows\Resources\Themes\dark.theme"
	$theme = "$Env:LocalAppData\Microsoft\Windows\Themes\CustomDark.theme"
}
else
{
	Write-Host "Not supported option $opt" -ForegroundColor Red
	exit 2
}
Write-Host "Theme path: $theme"
start "$theme"
WaitUntilRun -name "systemsettings" -max_timeout 3
taskkill /im "systemsettings.exe" /f