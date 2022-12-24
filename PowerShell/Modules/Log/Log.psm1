function Log {
    param ($msg)
    Write-Host $msg
}
function LogSuccess {
    param ($msg)
    Write-Host -ForegroundColor green $msg
}

function LogInfo {
    param ($msg)
    Write-Host -ForegroundColor Cyan $msg
}

function LogError {
    param ($msg)
    Write-Host -ForegroundColor Red $msg
}

Export-ModuleMember -Function * -Alias *
