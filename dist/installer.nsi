;--------------------------------
!include MUI2.nsh
!define MUI_INSTFILESPAGE_COLORS "FFFFFF 000000" ;Two colors
!define MUI_ICON "..\icon.ico"

; The name of the installer
Name "GW2RPC"

; The file to write
OutFile "gw2rpc_installer.exe"

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

; Build Unicode installer
Unicode True

; The default installation directory
InstallDir "C:\Program Files\Guild Wars 2\addons\GW2RPC"

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\GW2RPC" "Install_Dir"

;--------------------------------

; Pages


!define MUI_PAGE_DIRECTORY_TEXT "Please select your Guild Wars 2 installation folder. To install in a different folder, click Browse and select another folder. GW2RPC needs to be installed inside 'Guild Wars 2\addons'. Click Install to start the installation."


!define MUI_FINISHPAGE_TEXT "GW2RPC installed successfully! You may use Launch_GW2_with_RPC.exe to start GW2 together with GW2RPC or start gw2rpc.exe by yourself."
!define MUI_FINISHPAGE_TITLE "GW2RPC"
!define MUI_FINISHPAGE_LINK "Visit the GW2RPC website for more information"
!define MUI_FINISHPAGE_LINK_LOCATION "https://gw2rpc.info"
!define MUI_FINISHPAGE_RUN "$INSTDIR\Launch_GW2_with_RPC.exe"
!define MUI_FINISHPAGE_RUN_TEXT 'Launch GW2 together with GW2RPC'
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\config.ini"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Open config file"
!define MUI_FINISHPAGE_NOREBOOTSUPPORT


!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS 
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "GW2RPC (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File "gw2rpc.exe"
  IfFileExists $INSTDIR\config.ini Skip
    File "config.ini"
  Skip:
  File "Launch_GW2_with_RPC.exe"
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\GW2RPC "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GW2RPC" "DisplayName" "GW2RPC"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GW2RPC" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GW2RPC" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GW2RPC" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\GW2RPC"
  CreateShortcut "$SMPROGRAMS\GW2RPC\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortcut "$SMPROGRAMS\GW2RPC\gw2rpc.lnk" "$INSTDIR\gw2rpc.exe"
  CreateShortcut "$SMPROGRAMS\GW2RPC\Launch_GW2_with_RPC.lnk" "$INSTDIR\Launch_GW2_with_RPC.exe"

SectionEnd

Section "Desktop Shortcuts"

  CreateShortcut "$desktop\gw2rpc.lnk" "$INSTDIR\gw2rpc.exe"
  CreateShortcut "$desktop\Launch_GW2_with_RPC.lnk" "$INSTDIR\Launch_GW2_with_RPC.exe"

SectionEnd

Section /o "Autorun on Windows Startup"

  CreateShortcut "$SMPROGRAMS\Startup\gw2rpc.lnk" "$INSTDIR\gw2rpc.exe"

SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GW2RPC"
  DeleteRegKey HKLM SOFTWARE\GW2RPC

  ; Remove files and uninstaller
  Delete "$INSTDIR\gw2rpc.exe"
  Delete "$INSTDIR\config.ini"
  Delete "$INSTDIR\Launch_GW2_with_RPC.exe"
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$desktop\gw2rpc.lnk"
  Delete "$desktop\Launch_GW2_with_RPC.lnk"
  Delete "$SMPROGRAMS\GW2RPC\*.lnk"
  Delete "$SMPROGRAMS\Startup\gw2rpc.lnk"

  ; Remove directories
  RMDir "$SMPROGRAMS\GW2RPC"
  RMDir "$INSTDIR"

SectionEnd

