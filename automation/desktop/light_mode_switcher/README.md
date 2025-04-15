# switch_light_mode.sh

## Requirements to use `switch_light_mode.sh`:

1. Clone the whole Scripts repo.

2. Create 2 custom theme files in `%LOCALAPPDATA%\Microsoft\Windows\Themes\` using Windows Settings → Personalisation → Themes  
	**a.** `CustomLight.theme`  
	**b.** `CustomDark.theme`

3. Setup any bash shell (e.g. WSL)

4. Make sure you have `%USERPROFILE%\.p4qt\ApplicationSettings.xml` and `%USERPROFILE%\.p4merge\ApplicationSettings.xml` with field:  
	```xml
	<Bool varName="DarkTheme">false</Bool>
	```

5. Make sure you have `%USERPROFILE%\AppData\Roaming\Code\User\settings.json` with field  
	```json
	"workbench.colorTheme": "<Anything> Light",
	```
	or  
	```json
	"workbench.colorTheme": "<Anything> Dark",
	```
	where `<Anything>` can be Solarized/Visual Studio/Modern/etc.

6. Close P4V before running the script (it only reads the settings on launch and overwrites them from memory on exit)

7. Launch `switch_light_mode.sh dark` or `switch_light_mode.sh light` depending on your current choice.

8. Alternatively, create 2 shortcuts for light and dark modes with Target field set as

    ```C:\Windows\System32\wsl.exe -e /bin/bash -i -c "~/Scripts/automation/desktop/light_mode_switcher/switch_light_mode.sh dark"```
