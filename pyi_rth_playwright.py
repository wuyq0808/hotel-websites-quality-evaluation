"""
PyInstaller runtime hook for rebrowser-playwright
Sets up the browser path to use bundled browsers
"""
import os
import sys

# Set the PLAYWRIGHT_BROWSERS_PATH to the bundled browser location
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
    browsers_path = os.path.join(bundle_dir, 'ms-playwright')

    if os.path.exists(browsers_path):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
        print(f"✓ Using bundled Playwright browsers from: {browsers_path}")
    else:
        print(f"⚠ Warning: Bundled browser path not found: {browsers_path}")
