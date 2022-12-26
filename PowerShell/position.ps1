Import-Module WindowUtils -Force
# Helper functions for building the class
###########################################################################################

$r = GetWindowBounds "chrome"
$r
[NativeMethods]::MoveWindow($r.Handler, 0, 0, 800, 800, $true)

#Get-Process | Where-Object {$_.ProcessName -eq 'powershell'} | Get-ChildWindow
$a = Get-ChildWindow $r.Handler
foreach ($e in $a) {
	Write-Host "Child: $($e.ChildTitle):"
	$r = GetWindowBounds $e.ChildId
	$r.Rect
	Get-Process | Where-Object {$_.Id -eq $e.ChildId}
	if ($r.Rect.Left -eq 267) {
		Write-Host "Move window $(e.ChildTitle)"
		[NativeMethods]::MoveWindow($e.ChildId, 0, 0, 800, 800, $true)
	}
}