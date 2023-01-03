class Rectangle
{
    [float]$x
	[float]$y
	[float]$w
	[float]$h

    Rectangle($x, $y, $w, $h) {
		$this.x = $x
		$this.y = $y
		$this.w = $w
		$this.h = $h
    }
}

Add-Type -AssemblyName System.Windows.Forms;
function ScreenRect {
	param (
		[float]$x,
		[float]$y,
		[float]$w,
		[float]$h
	)
	$screens = [System.Windows.Forms.Screen]::AllScreens
	$b = $screens[0].Bounds;
    [Rectangle]::new(
        $b.X + $b.Width * $x
        , $b.Y + $b.Height * $y
        , $b.Width * $w
        , $b.Height * $h
    )
}

function Rect {
	param (
		[float]$x,
		[float]$y,
		[float]$w,
		[float]$h
	)
    [Rectangle]::new($x, $y, $w, $h)
}

Export-ModuleMember -Function * -Alias *
