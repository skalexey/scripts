
if ($args.Length -lt 2) {
    Write-Error -Message "Usage: p4_enter.ps1 <user> <workspace_name>" -ErrorAction Stop
}

$user = $args[0]
$workspace = $args[1]

p4 set P4USER=$user
p4 set P4CLIENT=$workspace

if ($args.Length -ge 3) {
    $addr = $args[2]
    p4 set P4PORT=$addr
}

p4 set P4CONFIG=.p4config

if ($args.Length -ge 4) {
    $pass = $args[3]
    # Uncomment in you need to use P4PASSWD parameter of the p4config
    # $hash = & $PSScriptRoot\..\md5.ps1 $pass
    # p4 set P4PASSWD=$hash
    echo $pass | p4 login -a
} else {
    p4 login -a
}
