# switch_light_mode.sh

## Requirements to use `switch_light_mode.sh`:

1. Clone the whole Scripts repo.

2. Create 2 custom theme files in `%LOCALAPPDATA%\Microsoft\Windows\Themes\` using Windows Settings → Personalisation → Themes  
	**a.** `CustomLight.theme`  
	**b.** `CustomDark.theme`
    
    You can also setup a backround image for your custom themes.

3. Setup any bash shell (e.g. WSL)

4. Install Python 3 (used for cross-platform VS Code theme updates)

5. Add ```%USERPROFILE%\Scripts\PowerShell\Modules``` to your PSModulePath environment variable

6. Make sure you have `%USERPROFILE%\.p4qt\ApplicationSettings.xml` and `%USERPROFILE%\.p4merge\ApplicationSettings.xml` with field:  
	```xml
	<Bool varName="DarkTheme">false</Bool>
	```

7. Make sure you have `%USERPROFILE%\AppData\Roaming\Code\User\settings.json`.

	The script now sets explicit VS Code theme names:
	- `Solarized Light` for light mode
	- `Dark+` for dark mode

	VS Code theme switching is handled by `vscode_theme_switch.py` so it can run on Windows/macOS/Linux.
	On non-Windows systems, Windows desktop and Windows Terminal theme switching is skipped automatically.

	To use different themes, edit these variables in `switch_light_mode.sh`:
	- `vscode_light_theme`
	- `vscode_dark_theme`

8. Close P4V before running the script (it only reads the settings on launch and overwrites them from memory on exit)

9. Launch `switch_light_mode.sh dark` or `switch_light_mode.sh light` depending on your current choice.

10. Alternatively, create 2 shortcuts for light and dark modes with Target field set as

    ```C:\Windows\System32\wsl.exe -e /bin/bash -i -c "~/Scripts/automation/desktop/light_mode_switcher/switch_light_mode.sh dark"```
