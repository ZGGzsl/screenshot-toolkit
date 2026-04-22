param(
    [int]$Width = 0,
    [int]$Height = 0,
    [string]$Output = "",
    [int]$Monitor = 0
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Auto-detect screen size
if ($Width -eq 0 -or $Height -eq 0) {
    $screens = [System.Windows.Forms.Screen]::AllScreens
    if ($Monitor -ge $screens.Count) {
        Write-Error "Monitor $Monitor not found. Available: $($screens.Count)"
        exit 1
    }
    $bounds = $screens[$Monitor].Bounds
    if ($Width -eq 0) { $Width = $bounds.Width }
    if ($Height -eq 0) { $Height = $bounds.Height }
    $originX = $bounds.X
    $originY = $bounds.Y
} else {
    $originX = 0
    $originY = 0
}

# Default output path
if ($Output -eq "") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Output = "screenshot_${timestamp}.png"
}

# Capture
$bmp = New-Object System.Drawing.Bitmap($Width, $Height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($originX, $originY, 0, 0, (New-Object System.Drawing.Size($Width, $Height)))
$graphics.Dispose()

# Save
$bmp.Save((Resolve-Path -Path ".").Path + "\" + $Output, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

# Output for agent consumption
$fullPath = (Resolve-Path -Path ".").Path + "\" + $Output
Write-Host "OK:$fullPath"
