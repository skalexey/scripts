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

# Prints all errors in the passed list.
# You can pass array named '$error' - the list of errors in the whole terminal session.
function LogAllErrors {
    param ($errorList)
    for ($i = 0; $i -lt $errorList.Count; $i++) {
        LogError "Error $($i): $($errorList[$i])\n"
    }
}
Export-ModuleMember -Function * -Alias *
