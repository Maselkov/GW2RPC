<p align="center"><img alt="Guild Wars 2 RPC" src="https://gw2rpc.info/static/img/logo.png" height="76"></p></img>

<h1 align="center">Guild Wars 2 RPC</h1>
<p align="center">A Discord Rich Presence addon for Guild Wars 2.</p> 

<p align="center" style="margin-bottom: 0px !important;">
  <img width="220" src="https://gw2rpc.info/static/img/showcases/n1tr0_1.png" alt="RPC status example" align="center">
</p>

<h3 align="center">
  <a href="https://gw2rpc.info">Go to website</a>・<a href="https://github.com/Maselkov/GW2RPC/releases">Download Latest</a>・<a href="https://github.com/Maselkov?tab=repositories">Other Projects</a>・<a href="https://www.paypal.com/donate/?hosted_button_id=KXMYX49C6MLLN">Donate</a></h3>

---
<p align="center">You need to install the <img src="https://api.iconify.design/bi:discord.svg?color=%23f9f9f9" height="12"> <b><a href="https://discord.com/download">Discord Desktop version</b></a> to run GW2RPC.</p>

<h2><img src="https://api.iconify.design/ic:baseline-auto-awesome.svg?color=%23ff8cf3" height="20">・Features</h2>
<details open markdown='1'><summary>Displaying off</summary>

* current map, as well as closest point of interest
* current raid, strike or fractal boss
* character name, race and profession (elite spec)
* commander icon if player is currently commanding a squad
* active guild tag (needs API key)
* time spent on map

</details>

<details open markdown='1'><summary>Also</summary>

* Automatic update checking
* Web based registry for maps
* Configurable settings
* Supports multiple accounts and multiboxing
* Automatic raid announcer (<a href="https://gw2rpc.info/#faq">FAQ</a>):

<p align="center" style="margin-bottom: 0px !important;">
  <img height="128" src="https://gw2rpc.info/static/img/announce_example.png" alt="RPC commander example" align="center">
</p>

</details>

<br>
<h2><img src="https://api.iconify.design/ic:baseline-browser-updated.svg?color=%23ff8cf3" height="20">・ How to install</h2>

1. Use the installer. Start either `gw2rpc.exe` or `launch_gw2_with_rpc.exe`.

or

2. Extract `gw2rpc.zip` and run the `gw2rpc.exe`. It will start in your system tray. It needs to be running in background for Rich Presence to work.

In the config.ini in the program's directory, you can input your API key so that your status can display region (EU/NA) and your current guild tag.

To make starting Rich Presence easier, there is an .exe called `launch_gw2_with_rpc.exe` included in the download. This script launches both GW2 and the RPC addon. For it to work, it needs to be present in `GW2FOLDER\addons\gw2rpc` . You may then replace your normal GW2 shortcut with it for ease of launching.

You can also put a shortcut to `gw2rpc.exe` into your autorun so that it runs automatically on Windows boot.

<br>
<h2><img src="https://api.iconify.design/ic:baseline-update.svg?color=%23ff8cf3" height="20">・ How to update</h2>

1. Run the new installer again. 

or


2. If a new version is released, simply replace the updated files. To get the newest configuration file, you might also delete the old one and let it be recreated on the first start of `gw2rpc.exe` for you.

<br>
<h2><img src="https://api.iconify.design/eos-icons:configuration-file.svg?color=%23ff8cf3" height="20">・Configuration file</h2>

See below for the example configuration file
```md

[API]
APIkey =                        ; ABCDE-FFFF-12345-....

[Settings]
CloseWithGW2 = False            ; Exit gw2rpc if GW2 exits
DisplayGuildTag = True          
HideCommanderTag = False        ; Dont show active comm tag if True
Lang = en                       ; Localization, one of en, es, fr, de, pt-br
LogLevel = info                 ; One of debug, info, warning, critical

[PointsOfInterest]
DisableInWvW = False
DisableCompletely = False
HidePoiButton = False           ; Dont show the copy paste button for PoI if true

[Webhooks]
webhook = https://discord.com/api/webhooks/887....b3bfdyCiz7y
AnnounceRaid = True
DisableInWvW = False
```
<br>

<h2><img src="https://api.iconify.design/ic:baseline-build.svg?color=%23ff8cf3" height="20">・Build and development Instructions</h2>
See <a href="BUILD.md">build section for instructions</a>

<br>
<h2><img src="https://api.iconify.design/bx:donate-heart.svg?color=%23ff8cf3" height="20">・Donate</h2>
This project is done in our free time by volunteers. If you want to support us, a donation is highly appreciated!

<br>

[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=UEBHM63V547KN)