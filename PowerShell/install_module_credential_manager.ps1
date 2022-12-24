if (Get-Module -ListAvailable -Name CredentialManager) {
    Write-Host "CredentialManager module OK"
} else {
    Write-Host "CredentialManager module for PowerShell is not installed. Let's install it..."
	Install-Module -Name CredentialManager
}

# Test the CredentialManager module
# Get-Command -Module CredentialManager
