if ($args.Count -eq 0)
{
	Write-Host "No mode specified (pass light or dark)" -ForegroundColor Red
	exit 1
}

$opt = $args[0]
if ($opt -eq "light")
{
	$terminalColorScheme = "Solarized Light"
}
elseif ($opt -eq "dark")
{
	$terminalColorScheme = "Dark+"
}
else
{
	Write-Host "Not supported option $opt" -ForegroundColor Red
	exit 2
}

$candidatePaths = @(
	"$Env:LocalAppData\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
	"$Env:LocalAppData\Microsoft\Windows Terminal\settings.json"
)

$settingsPath = $null
foreach ($path in $candidatePaths)
{
	if (Test-Path -LiteralPath $path)
	{
		$settingsPath = $path
		break
	}
}

if (-not $settingsPath)
{
	Write-Host "Windows Terminal settings.json not found; skipped color scheme update" -ForegroundColor Yellow
	exit 0
}

try
{
	$settings = Get-Content -LiteralPath $settingsPath -Raw | ConvertFrom-Json
	if (-not $settings.profiles)
	{
		$settings | Add-Member -MemberType NoteProperty -Name profiles -Value ([PSCustomObject]@{})
	}
	if (-not $settings.profiles.defaults)
	{
		$settings.profiles | Add-Member -MemberType NoteProperty -Name defaults -Value ([PSCustomObject]@{})
	}

	$settings.profiles.defaults | Add-Member -MemberType NoteProperty -Name colorScheme -Value $terminalColorScheme -Force
	$settings | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $settingsPath -Encoding UTF8
	Write-Host "Windows Terminal color scheme set to '$terminalColorScheme' in $settingsPath"
}
catch
{
	Write-Host "Failed to update Windows Terminal color scheme: $($_.Exception.Message)" -ForegroundColor Yellow
	exit 3
}