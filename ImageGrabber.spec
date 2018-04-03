# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['B:\\dev\\ImageGrabber'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [('preview.png', 'B:\\dev\\ImageGrabber', 'DATA')]

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
          console=False)
