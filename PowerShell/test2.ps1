$branch = "master"
if ($branch -eq "master") {
	$r = "Master!"
} else {
	$r = "Not master!"
}
Write-Host $r