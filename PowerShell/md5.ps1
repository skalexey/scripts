#converts string to MD5 hash in hyphenated and uppercase format

$input = $args[0]
if (-Not $input) {
    $input = Read-Host "Enter value to be hashed"
}


$md5 = new-object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
$utf8 = new-object -TypeName System.Text.UTF8Encoding
$hash = [System.BitConverter]::ToString($md5.ComputeHash($utf8.GetBytes($input)))

#to remove hyphens and downcase letters add:
$hash = $hash -replace '-', ''

if ($args[1] -Eq "-l") {
	$hash = $hash.ToLower()
}
$hash