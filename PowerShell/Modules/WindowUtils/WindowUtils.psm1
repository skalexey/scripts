Import-Module ArrayUtils -Force

$script:nativeMethods = @();
function Register-NativeMethod([string]$dll, [string]$methodSignature)
{
    $script:nativeMethods += [PSCustomObject]@{ Dll = $dll; Signature = $methodSignature; }
}
function Add-NativeMethods()
{
    $nativeMethodsCode = $script:nativeMethods | % { "
        [DllImport(`"$($_.Dll)`")]
        public static extern $($_.Signature);
    " }

    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
		using System.Collections.Generic;
		using System.Text;
        public class NativeMethods {
            $nativeMethodsCode
			
			public static List<IntPtr> GetChildWindows(IntPtr parent)
			{
				List<IntPtr> result = new List<IntPtr>();
				GCHandle listHandle = GCHandle.Alloc(result);
				try
				{
					EnumWindowProc childProc = new EnumWindowProc(EnumWindow);
					EnumChildWindows(parent, childProc,GCHandle.ToIntPtr(listHandle));
				}
				finally
				{
					if (listHandle.IsAllocated)
						listHandle.Free();
				}
				return result;
			}

			private static bool EnumWindow(IntPtr handle, IntPtr pointer)
			{
				GCHandle gch = GCHandle.FromIntPtr(pointer);
				List<IntPtr> list = gch.Target as List<IntPtr>;
				if (list == null)
				{
					throw new InvalidCastException("GCHandle Target could not be cast as List<IntPtr>");
				}
				list.Add(handle);
				//  You can modify this to check to see if you want to cancel the operation, then return a null here
				return true;
			}
			public delegate bool EnumWindowProc(IntPtr hWnd, IntPtr parameter);
        }

		public struct RECT
		{
			public int Left;        // x position of upper-left corner
			public int Top;         // y position of upper-left corner
			public int Right;       // x position of lower-right corner
			public int Bottom;      // y position of lower-right corner
		}
"@
}
# Register native methods
Register-NativeMethod "user32.dll" "bool GetWindowRect(IntPtr hWnd, out RECT lpRect)"
Register-NativeMethod "user32.dll" "bool SetForegroundWindow(IntPtr hWnd)"
Register-NativeMethod "user32.dll" "bool ShowWindow(IntPtr hWnd, int nCmdShow)"
Register-NativeMethod "user32.dll" "bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint)"
Register-NativeMethod "user32.dll" "bool AnimateWindow(IntPtr hwnd, UInt32 dwTime, UInt32 dwFlags)"
Register-NativeMethod "user32.dll" "IntPtr FindWindow(IntPtr ZeroOnly, string lpWindowName)"
Register-NativeMethod "user32.dll" "void keybd_event(Byte bVk, Byte bScan, UInt32 dwFlags, UInt32 dwExtraInfo)"
Register-NativeMethod "user32.dll" "bool InvalidateRect(IntPtr hWnd, IntPtr ZeroOnly, bool bErase)"

# For Get-ChildWindow
Register-NativeMethod "user32.dll" "int GetWindowText(IntPtr hwnd,StringBuilder lpString, int cch)"
Register-NativeMethod "user32.dll" "IntPtr GetForegroundWindow()"
Register-NativeMethod "user32.dll" "Int32 GetWindowThreadProcessId(IntPtr hWnd,out Int32 lpdwProcessId)"
Register-NativeMethod "user32.dll" "Int32 GetWindowTextLength(IntPtr hWnd)"
Register-NativeMethod "user32.dll" "bool EnumChildWindows(IntPtr window, EnumWindowProc callback, IntPtr i)"

# Call the native methods declaration
Add-NativeMethods

# Public functions
function GetWindowBounds {
	param($name, $index = -1)
	if ($name -is [string]) {
		Get-Process -Name $name
		$h = (Get-Process -Name $name).MainWindowHandle
	}
	else {
		$h = $name
	}
	if (!$h) {
		return
	}
	$r = New-Object RECT
	if ($h -is [array]) {
		if ($index -ge 0) {
			$h = $h[$index]
		} else {
			$h = FindFirstNotEqual $h 0
		}
	}
	if (-Not [NativeMethods]::GetWindowRect($h, [ref]$r)) {
		$r = $null
	}
	$result = New-Object PSObject
	$result | Add-Member -NotePropertyName Rect -NotePropertyValue $r
	$result | Add-Member -NotePropertyName Handler -NotePropertyValue $h
	$result
}

function Get-ChildWindow {
	[CmdletBinding()]
	param (
		[Parameter(ValueFromPipeline = $true, ValueFromPipelinebyPropertyName = $true)]
		[ValidateNotNullorEmpty()]
		[System.IntPtr]$MainWindowHandle
	)
	
	BEGIN {
		function Get-WindowName($hwnd) {
			$len = [NativeMethods]::GetWindowTextLength($hwnd)
			if($len -gt 0){
				$sb = New-Object text.stringbuilder -ArgumentList ($len + 1)
				$rtnlen = [NativeMethods]::GetWindowText($hwnd,$sb,$sb.Capacity)
				$sb.tostring()
			}
		}
	}
	
	PROCESS{
		foreach ($child in ([NativeMethods]::GetChildWindows($MainWindowHandle))){
			Write-Output (,([PSCustomObject] @{
				MainWindowHandle = $MainWindowHandle
				ChildId = $child
				ChildTitle = (Get-WindowName($child))
			}))
		}
	}
}

function IsProcessRunning {
	param($name)
	(Get-Process -Name $name -ErrorAction SilentlyContinue) -ne $null
}

Export-ModuleMember -Function * -Alias *