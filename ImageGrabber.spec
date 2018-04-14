# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['B:\\dev\\ImageGrabber'],
             binaries=[],
             datas=[('preview.png', '.'), ('.\\bin', 'bin'), ('icon.ico', '.')],
             hiddenimports=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ImageGrabber',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='icon.ico')
