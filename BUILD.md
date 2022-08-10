<h2><img src="https://api.iconify.design/ic:baseline-build.svg?color=%23ff8cf3" height="20">・Build and development Instructions</h2>

This project was tested with python3 version 3.9.1, allthough later versions might work too.

<h3><img src="https://api.iconify.design/entypo:install.svg?color=%23ff8cf3" height="20">・Install dependencies</h3>

Install dependencies with the command `pip3 install -r requirements.txt`

<h3><img src="https://api.iconify.design/gridicons:create.svg?color=%23ff8cf3" height="20">・Generating locales</h3>

First you have to generate the binary locale files with `msgformat.py`, i.e.
```
cd locales/de/LC_MESSAGES/
../../../Tools/i18n/msgfmt.py -o base.mo base
```
to do this for all available languages in one command, run the following from the project root directory:
```
for file in $(ls locales); do cd locales/${file}/LC_MESSAGES && ../../../Tools/i18n/msgfmt.py -o base.mo base && cd ../../../; done
```
Inside the LC_MESSAGES folders, you should now have the `base.po` and `base.mo` files.

<h3><img src="https://api.iconify.design/carbon:run.svg?color=%23ff8cf3" height="20">・Running</h3>

Make sure to change `locales_path = resource_path("./locales")` to `locales_path = resource_path("../locales")` in `gw2rpc.py` and run the program from the projects root directory with `python.exe .\run.py`.

 Make sure that you run it from a Windows Terminal / Powershell as there are some Windows specific dependencies to get the tasks list. The tray icon should appear when the program is running.

<h3><img src="https://api.iconify.design/codicon:debug-alt.svg?color=%23ff8cf3" height="20">・Debugging</h3>

Something like 
```
        print("{} {}".format(map_id, map_name))
        print("{} {}".format(position.x, position.y))
```
in the `get_map_asset` function in `gw2rpc.py` might be helpful to develop and debug.

<h3><img src="https://api.iconify.design/ic:baseline-terminal.svg?color=%23ff8cf3" height="20">・Build</h3>

First make sure to change the `locales_path` back to `./locales`, as mentioned above.

Next, create a .spec file for the project and place it in the projects root directory. It might look like the following:
```
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [("locales", "locales"), ('icon.ico', '.'), ('RPC.ico', '.'), ('lib\\discord_game_sdk.dll', '.')]

a = Analysis(['run.py'],
             pathex=['C:\\Users\\X\\Projects\\GW2RPC'],
             binaries=[],
             datas=added_files,
             hiddenimports=['pkg_resources', 'infi.systray'],
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
          name='gw2rpc.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='RPC.ico')
```
Adapt the path to your project in the .spec file accordingly. 

Start compiling simply with `pyinstaller.exe --onefile .\run.spec`. Pyinstaller 4.3 was used for this.

Again make sure that you run pyinstaller from your Windows installation!

If you get any errors when starting the compiled exe (like `Failed to execute script`), change `console` to `True` in the .spec file, run pyinstaller again and start the compiled exe from a powershell window. You hopefully will get error messages then.

<h3><img src="https://api.iconify.design/ic:baseline-terminal.svg?color=%23ff8cf3" height="20"> Installer</h3>

The installer is created with <a href="https://nsis.sourceforge.io/Download">NSIS</a> and the nsis script located in dist folder
