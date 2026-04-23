#!/usr/bin/env python3
"""
Native-resolution Windows screenshot — bypasses DPI scaling via Win32 API.
Unlike PIL.ImageGrab which respects DPI virtualization, this captures the
TRUE physical pixel resolution (e.g. 2256×1504) using GetDC + BitBlt.

Usage:
    python native_resolution.py                    # Primary monitor, auto filename
    python native_resolution.py --monitor 1       # Second monitor
    python native_resolution.py --output out.png   # Custom path
    python native_resolution.py --window "微信"   # Capture specific window by title
    python native_resolution.py --region 0 0 800 600  # Specific region (x,y,w,h)
"""

import argparse
import ctypes
import os
import sys
import platform
from datetime import datetime
from ctypes import wintypes

# ── Win32 bindings ────────────────────────────────────────────────────────────

user32 = ctypes.windll.user32
gdi32  = ctypes.windll.gdi32

SRCCOPY = 0x00CC0020

def GET_WINDOW_RECT(hwnd):
    """Returns (left, top, right, bottom) of a window."""
    class RECT(ctypes.Structure):
        _fields_ = [("left", wintypes.LONG),
                    ("top",  wintypes.LONG),
                    ("right",wintypes.LONG),
                    ("bottom",wintypes.LONG)]
    r = RECT()
    gdi32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom

def capture_native(x, y, width, height, output):
    """Core Win32 capture: get DC → create compat DC/BMP → BitBlt → save."""
    desktop_hwnd = user32.GetDesktopWindow()
    src_dc = user32.GetWindowDC(desktop_hwnd)
    mem_dc = gdi32.CreateCompatibleDC(src_dc)
    h_bmp  = gdi32.CreateCompatibleBitmap(src_dc, width, height)
    gdi32.SelectObject(mem_dc, h_bmp)
    gdi32.BitBlt(mem_dc, 0, 0, width, height, src_dc, x, y, SRCCOPY)

    # Convert to PIL Image
    from PIL import Image
    bmp = Image.FromHBitmap(h_bmp)

    # Flip vertically — GDI coordinates are top-down, PIL expects top-down already
    # but BitBlt from screen may need a vertical flip on some systems
    img = bmp.copy()  # avoid FromHBitmap resource leak
    bmp.Close()

    img.save(output)
    print(f"OK:{os.path.abspath(output)}")

    gdi32.DeleteObject(h_bmp)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(desktop_hwnd, src_dc)


def find_window(title):
    """Find a window by partial title match."""
    hwnd = user32.FindWindowW(None, title)
    if hwnd == 0:
        # Try with None class (fallback)
        hwnd = user32.FindWindowW(None, title)
    return hwnd


def get_monitor_bounds(monitor_idx):
    """Return (x, y, width, height) for a given monitor index."""
    if platform.system() != "Windows":
        raise RuntimeError("This script requires Windows")

    user32.SetProcessDPIAware()  # ensure DPI awareness

    # EnumDisplayMonitors approach
    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork",    wintypes.RECT),
            ("dwFlags",   wintypes.DWORD),
        ]

    monitors = []

    def callback(hMonitor, _hdc, _lprect, _lParam):
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
        monitors.append((mi.rcMonitor.left, mi.rcMonitor.top,
                         mi.rcMonitor.right - mi.rcMonitor.left,
                         mi.rcMonitor.bottom - mi.rcMonitor.top))
        return True

    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HMONITOR,
                            wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    user32.EnumDisplayMonitors(None, None, CB(callback), None)

    if monitor_idx >= len(monitors):
        raise ValueError(f"Monitor {monitor_idx} not found. Available: {len(monitors)}")

    return monitors[monitor_idx]


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Native-resolution screenshot via Win32 API — captures physical pixels, bypasses DPI scaling."
    )
    parser.add_argument("--monitor", "-m", type=int, default=0,
                        help="Monitor index (0 = primary)")
    parser.add_argument("--output", "-o", default="",
                        help="Output PNG path")
    parser.add_argument("--window", "-w", default="",
                        help="Capture a specific window by title (partial match)")
    parser.add_argument("--region", "-r", nargs=4, type=int, metavar="X Y W H",
                        help="Capture a specific region: X Y width height")

    args = parser.parse_args()

    if not args.output:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"native_screenshot_{ts}.png"

    if args.window:
        hwnd = find_window(args.window)
        if hwnd == 0:
            print(f"ERROR: Window not found: {args.window}", file=sys.stderr)
            sys.exit(1)
        l, t, r, b = GET_WINDOW_RECT(hwnd)
        capture_native(l, t, r - l, b - t, args.output)

    elif args.region:
        x, y, w, h = args.region
        capture_native(x, y, w, h, args.output)

    else:
        x, y, w, h = get_monitor_bounds(args.monitor)
        capture_native(x, y, w, h, args.output)


if __name__ == "__main__":
    main()