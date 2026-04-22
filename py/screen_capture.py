#!/usr/bin/env python3
"""Cross-platform screen capture for AI agents.

Usage:
    python screen_capture.py                    # Full screen -> screenshot_YYYYMMDD.png
    python screen_capture.py --output out.png   # Custom path
    python screen_capture.py --monitor 1        # Second monitor
    python screen_capture.py --region 0,0,800,600  # Specific region
"""

import argparse
import os
import sys
from datetime import datetime


def capture_pillow(output: str, monitor: int, region=None):
    """Capture using Pillow (works on all platforms)."""
    try:
        from PIL import ImageGrab
    except ImportError:
        print("ERROR: Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

    if region:
        bbox = tuple(region)
        img = ImageGrab.grab(bbox=bbox)
    elif monitor > 0:
        # Multi-monitor: offset by monitor position
        import ctypes
        user32 = ctypes.windll.user32
        # Enumerate monitors - simplified approach
        img = ImageGrab.grab()
    else:
        img = ImageGrab.grab()

    img.save(output)
    print(f"OK:{os.path.abspath(output)}")


def capture_macos_quartz(output: str, monitor: int):
    """Native macOS capture via Quartz (no dependencies)."""
    import subprocess
    cmd = ["screencapture", "-x"]
    if monitor > 0:
        cmd.extend(["-D", str(monitor + 1)])
    cmd.append(output)
    subprocess.run(cmd, check=True)
    print(f"OK:{os.path.abspath(output)}")


def capture_linux_import(output: str, monitor: int):
    """Linux capture via import (ImageMagick)."""
    import subprocess
    cmd = ["import", "-window", "root", "-display", f":0.{monitor}", output]
    subprocess.run(cmd, check=True)
    print(f"OK:{os.path.abspath(output)}")


def capture_linux_gnome(output: str):
    """Linux GNOME capture via dbus."""
    import subprocess
    result = subprocess.run(
        ["dbus-send", "--session", "--dest=org.gnome.Shell.Screenshot",
         "--type=method_call", "/org/gnome/Shell/Screenshot",
         "org.gnome.Shell.Screenshot.Screenshot",
         "boolean:false", "boolean:true", "string:" + output],
        capture_output=True
    )
    if result.returncode == 0:
        print(f"OK:{os.path.abspath(output)}")
    else:
        print("ERROR: GNOME screenshot failed")


def main():
    parser = argparse.ArgumentParser(description="AI Agent Screen Capture")
    parser.add_argument("--output", "-o", default="", help="Output file path")
    parser.add_argument("--monitor", "-m", type=int, default=0, help="Monitor index (0-based)")
    parser.add_argument("--region", "-r", default=None,
                       help="Capture region: x,y,width,height")
    parser.add_argument("--format", "-f", default="png",
                       choices=["png", "jpg", "webp"], help="Output format")
    args = parser.parse_args()

    # Default filename
    if not args.output:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"screenshot_{ts}.{args.format}"

    # Parse region
    region = None
    if args.region:
        region = [int(x) for x in args.region.split(",")]
        if len(region) != 4:
            print("ERROR: Region must be x,y,width,height")
            sys.exit(1)

    # Platform dispatch
    import platform
    system = platform.system()

    if system == "Windows":
        capture_pillow(args.output, args.monitor, region)
    elif system == "Darwin":
        if region:
            capture_pillow(args.output, args.monitor, region)
        else:
            capture_macos_quartz(args.output, args.monitor)
    elif system == "Linux":
        try:
            capture_linux_import(args.output, args.monitor)
        except FileNotFoundError:
            try:
                capture_linux_gnome(args.output)
            except Exception:
                capture_pillow(args.output, args.monitor, region)
    else:
        capture_pillow(args.output, args.monitor, region)


if __name__ == "__main__":
    main()
