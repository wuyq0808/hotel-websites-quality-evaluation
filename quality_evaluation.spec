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
strands_tools_hiddenimports = collect_submodules('strands_tools')

# Additional hidden imports that PyInstaller might miss
hidden_imports = [
    'yaml',
    'tenacity',
    'boto3',
    'botocore',
    'playwright',
    'strands',
    'strands.models',
    'strands_tools.browser',
    'strands_tools.browser.models',
    'enum',
    'logging',
    'json',
    'datetime',
] + strands_hiddenimports + strands_tools_hiddenimports

# Data files to include
datas = [
    ('config.yaml', '.'),              # Bundle config.yaml (self-documented)
]

a = Analysis(
    ['src/quality_evaluation/quality_evaluator_agent.py'],    # Main entry point
    pathex=['src'],                     # Add src to path for imports
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
