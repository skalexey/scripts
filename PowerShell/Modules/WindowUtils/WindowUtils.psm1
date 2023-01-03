using module Rectangle
Import-Module Rectangle -Force
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
		using System.Drawing;
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

		public struct POINT
		{
			public int X;
			public int Y;

			public POINT(int x, int y)
			{
				this.X = x;
				this.Y = y;
			}
		}

		public enum ShowWindowCommands
		{
			Hide = 0,
			Normal = 1,
			ShowMinimized = 2,
			Maximize = 3, // is this the right value?
			ShowMaximized = 3,
			ShowNoActivate = 4,
			Show = 5,
			Minimize = 6,
			ShowMinNoActive = 7,
			ShowNA = 8,
			Restore = 9,
			ShowDefault = 10,
			ForceMinimize = 11
		}
		
		public struct WINDOWPLACEMENT
		{
			public int Length;
			public int Flags;
			public ShowWindowCommands ShowCmd;

			public POINT MinPosition;

			public POINT MaxPosition;

			public RECT NormalPosition;
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
Register-NativeMethod "user32.dll" "IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex)";
Register-NativeMethod "user32.dll" "IntPtr SetWindowLongPtr(IntPtr hWnd, int nIndex, IntPtr dwNewLong)";
Register-NativeMethod "user32.dll" "bool GetWindowPlacement(IntPtr hWnd, ref WINDOWPLACEMENT lpwndpl)";

# For Get-ChildWindow
Register-NativeMethod "user32.dll" "int GetWindowText(IntPtr hwnd,StringBuilder lpString, int cch)"
Register-NativeMethod "user32.dll" "IntPtr GetForegroundWindow()"
Register-NativeMethod "user32.dll" "Int32 GetWindowThreadProcessId(IntPtr hWnd,out Int32 lpdwProcessId)"
Register-NativeMethod "user32.dll" "Int32 GetWindowTextLength(IntPtr hWnd)"
Register-NativeMethod "user32.dll" "bool EnumChildWindows(IntPtr window, EnumWindowProc callback, IntPtr i)"

# Call the native methods declaration
Add-NativeMethods

# Public functions

function IsWindowMaximized {
	param($handle)
	$lptr = [NativeMethods]::GetWindowLongPtr($h, -16)
	$lptr -band 0x01000000L
}

function DemaximizeWindow {
	param($handle)
	$lptr = [NativeMethods]::GetWindowLongPtr($h, -16)
	$lptr = $lptr -band 0x10111111L
	[NativeMethods]::SetWindowLongPtr($h, -16, $lptr)
}
function GetWindowBounds {
	param($name, $index = -1)
	# Log "GetWindowBounds($name)"
	$h = $null
	
	if ($name -is [string]) {
		$r = $(Get-Process -Name $name -ErrorAction SilentlyContinue)
		if (-not $r) {
			# LogError "Can't find process $name"
			$null
			return
		}
		$h = $r.MainWindowHandle
	}
	else {
		$h = $name
	}
	if (!$h) {
		throw "Unexpected error: undefined handler while looking for process '$name'"
		$null
	}
	$r = New-Object RECT
	if ($h -is [array]) {
		if ($index -ge 0) {
			$h = $h[$index]
		} else {
			$h = FindFirstNotEqual $h 0
		}
	}
	if (IsWindowMaximized $h) {
		# LogInfo "Window '$h' is maximized. Demaximize it"
		DemaximizeWindow $h
	} else {
		# LogInfo "Window '$h' is not maximized"
	}
	# Log "Try to get window bounds for process '$h'"
	if (-Not [NativeMethods]::GetWindowRect($h, [ref]$r)) {
		LogError "Can't get window bounds for process '$h'"
		$null
		return
	}
	[PSCustomObject]@{
		Rect = [Rectangle]::new($r.Left, $r.Top, $r.Right - $r.Left, $r.Bottom - $r.Top)
		Handle = $h
	}
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
		$a = ([NativeMethods]::GetChildWindows($MainWindowHandle));
		if (-not $a -or $a.Count -eq 0) {
			return
		}
		foreach ($child in $a){
			Write-Output (,([PSCustomObject] @{
				MainWindowHandle = $MainWindowHandle
				ChildId = $child
				ChildTitle = $(Get-WindowName($child))
			}))
		}
	}
}

function IsProcessRunning {
	param($name)
	$null -ne $(Get-Process -Name $name -ErrorAction SilentlyContinue)
}

Export-ModuleMember -Function * -Alias *