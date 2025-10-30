# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Quality Evaluation Tool
Bundles the Python application into a standalone executable

Usage:
    pyinstaller quality_evaluation.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all strands-related modules
strands_hiddenimports = collect_submodules('strands')

# Additional hidden imports that PyInstaller might miss
hidden_imports = [
    'yaml',
    'tenacity',
    'boto3',
    'botocore',
    'rebrowser_playwright',
    'rebrowser_playwright.sync_api',
    'rebrowser_playwright.async_api',
    'strands',
    'strands.models',
    'enum',
    'logging',
    'json',
    'datetime',
    'nest_asyncio',
] + strands_hiddenimports

# Data files to include
# Note: config.yaml should NOT be bundled - it needs to be editable by users
# Include rebrowser-playwright driver (node binary and package)
datas = []
try:
    import rebrowser_playwright
    import os
    from pathlib import Path

    # Bundle the driver
    playwright_driver = os.path.join(os.path.dirname(rebrowser_playwright.__file__), 'driver')
    if os.path.exists(playwright_driver):
        datas.append((playwright_driver, 'rebrowser_playwright/driver'))
        print(f"✓ Bundled rebrowser-playwright driver")

    # Bundle Chromium browser from cache
    browser_cache = Path.home() / 'Library' / 'Caches' / 'ms-playwright'
    chromium_headless = browser_cache / 'chromium_headless_shell-1169'

    if chromium_headless.exists():
        # Bundle chromium_headless_shell for headless mode
        datas.append((str(chromium_headless), 'ms-playwright/chromium_headless_shell-1169'))
        print(f"✓ Bundled Chromium headless shell browser")
    else:
        print(f"⚠ Warning: Chromium headless browser not found at {chromium_headless}")

except ImportError:
    print("⚠ Warning: rebrowser_playwright not found, driver won't be bundled")
except Exception as e:
    print(f"⚠ Warning: Could not bundle rebrowser_playwright components: {e}")

# Bundle mshell and saml2aws binaries for AWS authentication
binaries_to_bundle = [
    ('bin/mshell', 'bin'),      # Bundle mshell to bin/ in executable
    ('bin/saml2aws', 'bin'),    # Bundle saml2aws to bin/ in executable
]

a = Analysis(
    ['src/quality_evaluator_agent.py'],    # Main entry point
    pathex=['src'],                        # Add src to path for imports
    binaries=binaries_to_bundle,           # Include AWS auth binaries
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_playwright.py'],  # Set PLAYWRIGHT_BROWSERS_PATH
    excludes=[
        'matplotlib',                   # Exclude unnecessary packages
        'PIL',
        'scipy',
        'pandas',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='quality_evaluation',          # Output executable name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,                       # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
