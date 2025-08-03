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

function PromptFallbackCredentials {
    param ($login)
    LogInfo("PromptFallbackCredentials(): Using manual prompt for '$login'")
    $password = Read-Host "Enter password for '$login'" -AsSecureString
    return New-Object System.Management.Automation.PSCredential($login, $password)
}


function AskCredentials {
    param ($login)
    Log("AskCredentials(): Attempting Get-Credential for '$login'")

    if ([System.Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
        LogInfo("AskCredentials(): Current thread is not STA. Get-Credential UI may not work.")
    }

    try {
        $cred = Get-Credential -Message "Enter credentials for '$login'" -UserName "$login"
    } catch {
        Log("AskCredentials(): Get-Credential threw an error: $_. Using fallback.")
        $cred = $null
    }

    if (-Not $cred) {
        Log("AskCredentials(): Falling back to console prompt.")
        $cred = PromptFallbackCredentials $login
    }

    if (-Not $cred) {
        LogError("Can't get credentials for '$login'. Exiting...")
        exit 3
    }

    $credFpath = CredFPath $login
    # Log("AskCredentials(): Saving credentials to $credFpath")
    $cred | Export-Clixml -Path $credFpath
    Log("AskCredentials(): Done")
    return $cred
}

function GetCred {
    param ($login)

    if (-Not (Test-Path -Path $credsDir)) {
        LogInfo("No creds directory. Creating at '$credsDir'...")
        New-Item $credsDir -ItemType Directory *> $null
    } elseif (-Not $onlyGet) {
        LogSuccess("Creds directory OK")
    }

    $credFpath = CredFPath $login
    if (-Not (Test-Path -Path $credFpath -PathType Leaf)) {
        Log("Credentials for '$login' not found. Please enter them.")
        $cred = AskCredentials($login)
    } else {
        if (-Not $onlyGet) {
            LogSuccess("Credentials OK")
        }
        try {
            $cred = Import-Clixml -Path $credFpath
        } catch {
            LogInfo("Import failed: $_. Re-prompting.")
            $cred = $null
        }

        if (-Not $cred) {
            LogInfo("Can't import credentials for '$login'. Please enter them.")
            $cred = AskCredentials($login)
        }
    }

    if (-Not $cred) {
        LogError("Bad credentials. Exiting...")
        exit 2
    }

    return $cred
}

$cred = GetCred($credLogin)
$pass = $cred.GetNetworkCredential().Password

if ($onlyGet) {
    $pass
    exit 0
}

Set-Clipboard -Value $pass
LogSuccess("Done")
