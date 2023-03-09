if ($args.Count -lt 1) {
    Write-Host "No variable name provided" -ForegroundColor Red
    exit 1
}

$a = $args[0]
(Get-Item -Path env:\$a).Value
