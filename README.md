A Discord Rich Presence addon for Guild Wars 2.

https://gw2rpc.info

Features:
* Display maps with loading screens
* Display character and elite spec
* Automatic update checking
* Web based registry for maps
* Supports multiple accounts

Exe versions are made using Pyinstaller

# Development Instructions
This project was tested with python3 version 3.9.1, allthough later versions might work too.
## Install dependencies
Install dependencies with the command `pip3 install -r requirements.txt`
## Generating locales
First you have to generate the binary locale files with `msgformat.py`, i.e.
```
cd locales/de/LC_MESSAGES/
../../../Tools/i18n/msgfmt.py -o base.mo base
```
to do this for all available languages in one command, run the following from the project root directory:
```
for file in $(ls locales); do cd locales/${file}/LC_MESSAGES && ../../../Tools/i18n/msgf
mt.py -o base.mo base && cd ../../../; done
```
Inside the LC_MESSAGES folders, you should now have the `base.po` and `base.mo` files.
## Running
Make sure to change `locales_path = resource_path("./locales")` to `locales_path = resource_path("../locales")` in `gw2rpc.py` and run the program from the projects root directory with `python.exe .\run.py`.

 Make sure that you run it from a Windows Terminal / Powershell as there are some Windows specific dependencies to get the tasks list. The tray icon should appear when the program is running.
## Debugging
Something like 
```
        print("{} {}".format(map_id, map_name))
        print("{} {}".format(position.x, position.y))
```
in the `get_map_asset` function in `gw2rpc.py` might be helpful to develop and debug.
## Build
First make sure to change the `locales_path` back to `./locales`, as mentioned above.

Next, create a .spec file for the project and place it in the projects root directory. It might look like the following:
```
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [("locales", "locales"), ('icon.ico', '.'), ('RPC.ico', '.')]

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