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
        LogSuccess("Creds directory OK")
    }
    $credFpath = CredFPath $login
    if (-Not (Test-Path -Path $credFpath -PathType Leaf)) {
        Log("Credentials for '$login' not found. Please enter them.")
        $cred = AskCredentials($login)
    } else {
        LogSuccess("Credentials OK")
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
Set-Clipboard -Value $cred.GetNetworkCredential().Password
LogSuccess("Done")