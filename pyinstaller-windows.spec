# -*- mode: python ; coding: utf-8 -*-

# import required modules
# ensures that PyInstaller fails if not found
import matplotlib.pyplot
import numpy
import scipy
import tabulate
import seaborn
import logging
import pandas
import more_itertools
import PyQt5


block_cipher = None


a = Analysis(['cdgo\\app.py'],
             pathex=None,
             binaries=[],
             datas=[],
             hiddenimports=['matplotlib.pyplot', 'pandas', 'numpy'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cdgo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
