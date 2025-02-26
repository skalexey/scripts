param (
    [string]$sourceDir,    # Source directory in local file system
    [string]$targetDir     # Target directory in local file system
)

# Convert paths to Perforce-style paths with forward slashes
$sourceDirP4 = $sourceDir.Replace('\', '/')
$targetDirP4 = $targetDir.Replace('\', '/')

# Check if source directory exists
if (!(Test-Path -Path $sourceDir)) {
    Write-Host "Source directory does not exist: $sourceDir"
    exit 1
}

# Get all files in the source directory and open them for edit, then move them one by one
Get-ChildItem -Recurse -File -Path $sourceDir | ForEach-Object {
    $sourceFilePath = $_.FullName.Replace('\', '/')
    $relativePath = $_.FullName.Substring($sourceDir.Length).TrimStart('\')
    $targetFilePath = Join-Path -Path $targetDir -ChildPath $relativePath

    # Open the file for edit in Perforce if it's already added
    Write-Host "Opening $sourceFilePath for edit"
    p4 edit "$sourceFilePath" > $null 2>&1

    # Use `p4 move` to move the file from source to target path
    Write-Host "Moving $sourceFilePath to $targetFilePath"
    p4 move "$sourceFilePath" "$targetFilePath"
}

Write-Host "Completed moving files from $sourceDir to $targetDir"
