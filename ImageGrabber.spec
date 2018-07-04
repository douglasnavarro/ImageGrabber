# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['B:\\dev\\ImageGrabber'],
             binaries=[],
             datas=[('preview.png', '.'), ('.\\bin', 'bin'), ('icon.ico', '.')],
             hiddenimports=['comtypes.gen._944DE083_8FB8_45CF_BCB7_C477ACB2F897_0_1_0', 'comtypes.gen.UIAutomationClient'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ImageGrabber',
          debug=False,
          strip=False,
          upx=True,
          clean=True,
          console=False , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ImageGrabber')
