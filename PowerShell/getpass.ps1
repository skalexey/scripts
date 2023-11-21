#
Import-Module Log -Force

$credsDir = "~\creds"
$credLogin = $args[0]
if (-Not $credLogin) {
    $credLogin = Read-Host "Enter credentials login"
}

if (-Not $credLogin) {
    LogError("Login can't be empty")
    Pause
    exit 1
}

$onlyGet = $false
if ($args.Count -gt 1) {
    if ($args[1] -eq "--get") {
        $onlyGet = $true
    }
}

function CredFPath {
    param ($login)
    "$credsDir\$login.xml"
}

function AskCredentials {
    param ($login)
    $cred = Get-Credential -Message "Enter credentials for '$login'" -UserName "$login"
    $credFpath = CredFPath $login
    $cred | Export-Clixml -Path "$credFpath"
    $cred
}

function GetCred {
    param ($login)
    if (-Not (Test-Path -Path $credsDir)) {
        LogInfo("No creds directory. Creating at '$credsDir'...")
        New-Item $credsDir -ItemType Directory *> $null
    } else {
        if (-Not $onlyGet) {
            LogSuccess("Creds directory OK")
        }
    }
    $credFpath = CredFPath $login
    if (-Not (Test-Path -Path $credFpath -PathType Leaf)) {
        Log("Credentials for '$login' not found. Please enter them.")
        $cred = AskCredentials($login)
    } else {
        if (-Not $onlyGet) {
            LogSuccess("Credentials OK")
        }
        $cred = Import-Clixml -Path $credFpath
        if (-Not $cred) {
            LogInfo("Can't import credentials for '$login'. Please enter them.")
            $cred = AskCredentials($login)
        }
    }
    if (-Not $cred) {
        LogError("Bad credentials. Exiting...")
        exit 2
    }
    $cred
}

$cred = GetCred($credLogin)
$pass = $cred.GetNetworkCredential().Password
if ($onlyGet) {
    $pass
    exit 0
}

Set-Clipboard -Value $pass
LogSuccess("Done")