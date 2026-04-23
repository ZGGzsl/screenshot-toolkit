#Requires -Version 5.1
<#
.SYNOPSIS
    Native-resolution Windows screenshot via Win32 API — bypasses DPI scaling.

.DESCRIPTION
    Uses GetDC / BitBlt to capture the desktop at its TRUE physical pixel resolution,
    ignoring Windows DPI virtualization (Per-Monitor DPI aware). Designed for AI agents
    that need the actual display pixels rather than the scaled/logical resolution.

    Output: PNG file at the monitor's native resolution.

.PARAMETER Monitor
    Which monitor to capture (0-based index). Default: 0 (primary).

.PARAMETER Output
    Output file path. Default: native_screenshot_YYYYMMDD_HHmmss.png in current dir.

.PARAMETER WindowTitle
    Instead of full-screen, capture a specific window by its title (partial match).
    If omitted, captures the whole virtual screen.

.EXAMPLE
    .\native_resolution.ps1                          # Primary monitor, auto filename
    .\native_resolution.ps1 -Monitor 1                # Second monitor
    .\native_resolution.ps1 -Output "screenshot.png"  # Custom path
    .\native_resolution.ps1 -WindowTitle "微信"       # Capture specific window
#>
param(
    [int]    $Monitor   = 0,
    [string] $Output    = "",
    [string] $WindowTitle = ""
)

Add-Type -Definition @"
using System;
using System.Runtime.InteropServices;

public class NativeCapture {
    [DllImport("user32.dll")]
    public static extern IntPtr GetDesktopWindow();

    [DllImport("user32.dll")]
    public static extern IntPtr GetWindowDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll")]
    public static extern bool BitBlt(IntPtr hdcDest, int xDest, int yDest,
        int wDest, int hDest, IntPtr hdcSrc, int xSrc, int ySrc, int rop);

    [DllImport("gdi32.dll")]
    public static extern IntPtr CreateCompatibleDC(IntPtr hdc);

    [DllImport("gdi32.dll")]
    public static extern IntPtr CreateCompatibleBitmap(IntPtr hdc, int w, int h);

    [DllImport("gdi32.dll")]
    public static extern IntPtr SelectObject(IntPtr hdc, IntPtr hObject);

    [DllImport("gdi32.dll")]
    public static extern bool DeleteObject(IntPtr hObject);

    [DllImport("gdi32.dll")]
    public static extern bool DeleteDC(IntPtr hdc);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left, Top, Right, Bottom;
        public int Width  => Right - Left;
        public int Height => Bottom - Top;
    }

    public const int SRCCOPY = 0x00CC0020;
}
"@

# ── Helpers ───────────────────────────────────────────────────────────────────

function Get-NativeResolution {
    param([int]$Mon)
    Add-Type -AssemblyName System.Windows.Forms
    $screens = [System.Windows.Forms.Screen]::AllScreens
    if ($Mon -ge $screens.Count) {
        Write-Error "Monitor $Mon not found. Available: $($screens.Count - 1)"
        exit 1
    }
    $bounds = $screens[$Mon].Bounds
    return @{
        X      = $bounds.X
        Y      = $bounds.Y
        Width  = $bounds.Width
        Height = $bounds.Height
    }
}

function Capture-FullScreen {
    param([int]$X, [int]$Y, [int]$Width, [int]$Height, [string]$OutPath)

    $desktopHwnd = [NativeCapture]::GetDesktopWindow()
    $srcDC       = [NativeCapture]::GetWindowDC($desktopHwnd)
    $memDC       = [NativeCapture]::CreateCompatibleDC($srcDC)
    $hBmp        = [NativeCapture]::CreateCompatibleBitmap($srcDC, $Width, $Height)
    $oldBmp      = [NativeCapture]::SelectObject($memDC, $hBmp)

    [void][NativeCapture]::BitBlt($memDC, 0, 0, $Width, $Height, $srcDC, $X, $Y, [NativeCapture]::SRCCOPY)

    [void][NativeCapture]::SelectObject($memDC, $oldBmp)

    $bmp = [System.Drawing.Bitmap]::FromHBitmap($hBmp)
    $bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()

    [void][NativeCapture]::DeleteObject($hBmp)
    [void][NativeCapture]::DeleteDC($memDC)
    [void][NativeCapture]::ReleaseDC($desktopHwnd, $srcDC)
}

function Capture-Window {
    param([string]$Title, [string]$OutPath)
    $hwnd = [NativeCapture]::FindWindow("", $Title)
    if ($hwnd -eq [IntPtr]::Zero) {
        Write-Error "Window not found: $Title"
        exit 1
    }
    $rect = New-Object NativeCapture+RECT
    [void][NativeCapture]::GetWindowRect($hwnd, [ref]$rect)
    $W = $rect.Right - $rect.Left
    $H = $rect.Bottom - $rect.Top

    $desktopHwnd = [NativeCapture]::GetDesktopWindow()
    $srcDC       = [NativeCapture]::GetWindowDC($desktopHwnd)
    $memDC       = [NativeCapture]::CreateCompatibleDC($srcDC)
    $hBmp        = [NativeCapture]::CreateCompatibleBitmap($srcDC, $W, $H)
    $oldBmp      = [NativeCapture]::SelectObject($memDC, $hBmp)

    [void][NativeCapture]::BitBlt($memDC, 0, 0, $W, $H, $srcDC, $rect.Left, $rect.Top, [NativeCapture]::SRCCOPY)

    [void][NativeCapture]::SelectObject($memDC, $oldBmp)

    $bmp = [System.Drawing.Bitmap]::FromHBitmap($hBmp)
    $bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()

    [void][NativeCapture]::DeleteObject($hBmp)
    [void][NativeCapture]::DeleteDC($memDC)
    [void][NativeCapture]::ReleaseDC($desktopHwnd, $srcDC)
}

# ── Main ──────────────────────────────────────────────────────────────────────

if ($Output -eq "") {
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $Output = "native_screenshot_$ts.png"
}

if ($WindowTitle -ne "") {
    Capture-Window -Title $WindowTitle -OutPath $Output
} else {
    $res = Get-NativeResolution -Mon $Monitor
    Capture-FullScreen -X $res.X -Y $res.Y -Width $res.Width -Height $res.Height -OutPath $Output
}

$fullPath = (Resolve-Path $Output).Path
Write-Host "OK:$fullPath"