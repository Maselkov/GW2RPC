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

!define StrRep "!insertmacro StrRep"
!macro StrRep output string old new
    Push `${string}`
    Push `${old}`
    Push `${new}`
    !ifdef __UNINSTALL__
        Call un.StrRep
    !else
        Call StrRep
    !endif
    Pop ${output}
!macroend

!macro Func_StrRep un
    Function ${un}StrRep
        Exch $R2 ;new
        Exch 1
        Exch $R1 ;old
        Exch 2
        Exch $R0 ;string
        Push $R3
        Push $R4
        Push $R5
        Push $R6
        Push $R7
        Push $R8
        Push $R9
        StrCpy $R3 0
        StrLen $R4 $R1
        StrLen $R6 $R0
        StrLen $R9 $R2
        loop:
            StrCpy $R5 $R0 $R4 $R3
            StrCmp $R5 $R1 found
            StrCmp $R3 $R6 done
            IntOp $R3 $R3 + 1 ;move offset by 1 to check the next character
            Goto loop
        found:
            StrCpy $R5 $R0 $R3
            IntOp $R8 $R3 + $R4
            StrCpy $R7 $R0 "" $R8
            StrCpy $R0 $R5$R2$R7
            StrLen $R6 $R0
            IntOp $R3 $R3 + $R9 ;move offset by length of the replacement string
            Goto loop
        done:
        Pop $R9
        Pop $R8
        Pop $R7
        Pop $R6
        Pop $R5
        Pop $R4
        Pop $R3
        Push $R0
        Push $R1
        Pop $R0
        Pop $R1
        Pop $R0
        Pop $R2
        Exch $R1
    FunctionEnd
!macroend
!insertmacro Func_StrRep ""
!insertmacro Func_StrRep "un."

Function .onInit
  ; The default installation directory of GW2
  SetRegView 64
  ReadRegStr $1 HKLM "Software\ArenaNet\Guild Wars 2" "Path"
  DetailPrint "$1"
  SetRegView lastused

  ; Check if the installation path was found
  StrCmp $1 "" install_path_not_found
  ; Replace Gw2-64.exe with addons in the installation path
  ${StrRep} $2 $1 "Gw2-64.exe" "addons\GW2RPC"
  StrCmp $2 $1 install_path_not_found

  StrCpy $INSTDIR $2
  SetOutPath $2
  Goto done

  install_path_not_found:
    StrCpy $INSTDIR "C:\Program Files\Guild Wars 2\addons\GW2RPC\"
    SetOutPath $INSTDIR

  done:

FunctionEnd

;--------------------------------

; The stuff to install
Section "GW2RPC (required)"

  SectionIn RO

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

