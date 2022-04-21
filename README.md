<p align="center"><img alt="Guild Wars 2 RPC" src="https://gw2rpc.info/static/img/logo.png" height="76"></p></img>

<h1 align="center">Guild Wars 2 RPC</h1>
<p align="center">A Discord Rich Presence addon for Guild Wars 2.</p>

<a href="https://gw2rpc.info"><p align="center">Go to website</a>・<a href="https://github.com/Maselkov/GW2RPC/releases">Download Latest</a>・<a href="https://github.com/Maselkov?tab=repositories">Other Projects...</p></a>

---
<p align="center">Download <img src="https://api.iconify.design/bi:discord.svg?color=%23f9f9f9" height="12"> <b><a href="https://discord.com/download">Discord Desktop version</b></a> to run the rich presence.</p>

<h2><img src="https://api.iconify.design/ic:baseline-auto-awesome.svg?color=%23ff8cf3" height="20">・Features</h2>

* Displaying off:
   + current map, as well as closes point of interest
   + current raid or fractal boss
   + character name, race and profession (elite spec)
   + commander icon if player is currently commanding a squad
   + active guild tag (needs API key)
   + time spent on map
* Automatic raid announcer
* Automatic update checking
* Web based registry for maps
* Configurable settings
* Supports multiple accounts


<h2><img src="https://api.iconify.design/ic:baseline-browser-updated.svg?color=%23ff8cf3" height="20">・ How to install</h2>
Simply extract and run the `gw2rpc.exe`. It will start in your system tray. It needs to be running in background for Rich Presence to work.

In the config.ini in the program's directory, you can input your API key so that your status can display region (EU/NA) and your current guild tag.

To make starting Rich Presence easier, there is an .exe called `launch_gw2_with_rpc.exe` included in the download. This script launches both GW2 and the RPC addon. For it to work, it needs to be present in `GW2FOLDER\addons\gw2rpc` . You may then replace your normal GW2 shortcut with it for ease of launching.

You can also put a shortcut to `gw2rpc.exe` into your autorun so that it runs automatically on Windows boot.

<h2><img src="https://api.iconify.design/ic:baseline-update.svg?color=%23ff8cf3" height="20">・ How to update</h2>
If a new version is released, simply replace the updated files. To get the newest configuration file, you might also delete the old one and let it be recreated on the first start of `gw2rpc.exe` for you.

<h2><img src="https://api.iconify.design/eos-icons:configuration-file.svg?color=%23ff8cf3" height="20">・Configuration file</h2>

See below for the example configuration file
```md

[API]
APIkey =                        ; ABCDE-FFFF-12345-....

[Settings]
CloseWithGW2 = False            ; Exit gw2rpc if GW2 exits
DisplayGuildTag = True          
HideCommanderTag = False        ; Dont show active comm tag if True
Lang = en                       ; Localization, one of en, es, fr, de

[PointsOfInterest]
DisableInWvW = False
DisableCompletely = False
HidePoiButton = False           ; Dont show the copy paste button for PoI if true

[Webhooks]
webhook = https://discord.com/api/webhooks/887....b3bfdyCiz7y
AnnounceRaid = True
DisableInWvW = False
```

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
