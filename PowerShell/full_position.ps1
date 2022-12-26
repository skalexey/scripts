Import-Module ArrayUtils -Force

# Helper functions for building the class
###########################################################################################
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
        public class NativeMethods {
            $nativeMethodsCode
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
###########################################################################################


# Add your Win32 API here:
###########################################################################################
Register-NativeMethod "user32.dll" "bool GetWindowRect(IntPtr hWnd, out RECT lpRect)"
Register-NativeMethod "user32.dll" "bool SetForegroundWindow(IntPtr hWnd)"
Register-NativeMethod "user32.dll" "bool ShowWindow(IntPtr hWnd, int nCmdShow)"
Register-NativeMethod "user32.dll" "bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint)"
Register-NativeMethod "user32.dll" "bool AnimateWindow(IntPtr hwnd, UInt32 dwTime, UInt32 dwFlags)"
Register-NativeMethod "user32.dll" "IntPtr FindWindow(IntPtr ZeroOnly, string lpWindowName)"
Register-NativeMethod "user32.dll" "void keybd_event(Byte bVk, Byte bScan, UInt32 dwFlags, UInt32 dwExtraInfo)"
Register-NativeMethod "user32.dll" "bool InvalidateRect(IntPtr hWnd, IntPtr ZeroOnly, bool bErase)"
###########################################################################################


#Build class and registers them:
Add-NativeMethods

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
			$len = [apifuncs]::GetWindowTextLength($hwnd)
			if($len -gt 0){
				$sb = New-Object text.stringbuilder -ArgumentList ($len + 1)
				$rtnlen = [apifuncs]::GetWindowText($hwnd,$sb,$sb.Capacity)
				$sb.tostring()
			}
		}
	
		if (("APIFuncs" -as [type]) -eq $null) {
			Add-Type  @"
			using System;
			using System.Runtime.InteropServices;
			using System.Collections.Generic;
			using System.Text;
			public class APIFuncs
			  {
				[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
				public static extern int GetWindowText(IntPtr hwnd,StringBuilder lpString, int cch);
	
				[DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
				public static extern IntPtr GetForegroundWindow();
	
				[DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
				public static extern Int32 GetWindowThreadProcessId(IntPtr hWnd,out Int32 lpdwProcessId);
	
				[DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
				public static extern Int32 GetWindowTextLength(IntPtr hWnd);
	
				[DllImport("user32")]
				[return: MarshalAs(UnmanagedType.Bool)]
				public static extern bool EnumChildWindows(IntPtr window, EnumWindowProc callback, IntPtr i);
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
"@
			}
	}
	
	PROCESS{
		foreach ($child in ([apifuncs]::GetChildWindows($MainWindowHandle))){
			Write-Output (,([PSCustomObject] @{
				MainWindowHandle = $MainWindowHandle
				ChildId = $child
				ChildTitle = (Get-WindowName($child))
			}))
		}
	}
}

$r = GetWindowBounds "chrome"
$r
[NativeMethods]::MoveWindow($r.Handler, 0, 0, 800, 800, $true)

#Get-Process | Where-Object {$_.ProcessName -eq 'powershell'} | Get-ChildWindow
$a = Get-ChildWindow $r.Handler
foreach ($e in $a) {
	Write-Host "Child: $($e.ChildTitle):"
	$r = GetWindowBounds $e.ChildId
	$r.Rect
	Get-Process | Where-Object {$_.Id -eq $e.ChildId}
	if ($r.Rect.Left -eq 267) {
		Write-Host "Move window $(e.ChildTitle)"
		[NativeMethods]::MoveWindow($e.ChildId, 0, 0, 800, 800, $true)
	}
}