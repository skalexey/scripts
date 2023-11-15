

if ($args.Length -ne 2) {
    Write-Error -Message "Usage: p4_enter.ps1 <user> <workspace_name>" -ErrorAction Stop
}

$user = $args[0]
$workspace = $args[1]

p4 set P4USER=$user
p4 set P4CLIENT=$workspace

if ($args.Length -ge 3) {
    p4 set P4PORT=$args[2]
}

if ($args.Length -ge 4) {
    p4 set P4PASSWD=$args[3]
}

p4 login -a
