# -*- mode: python -*-
a = Analysis(['clickmaster2000/clickmaster.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
for path in ['clickmaster.html', 'clickmaster.ui']:
    a.datas.append((path, 'clickmaster2000/' + path, 'DATA'))
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='clickmaster2000.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False)
