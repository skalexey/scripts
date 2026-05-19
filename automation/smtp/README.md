# Generic SMTP Automation Scripts

This directory contains generic SMTP setup and test scripts for automation workflows.

## Files
- `setup_smtp.sh`: interactive setup that stores SMTP environment variables in a private file.
- `send_test_email.sh`: sends a test email using loaded environment variables.

## Security model
- This public directory does not store project-specific data or secrets.
- Secrets are stored in `~/.config/automation/smtp.env` with file mode `600`.

## Quick start
1. `./setup_smtp.sh`
2. `source ~/.config/automation/smtp.env`
3. `./send_test_email.sh recipient@example.com`
