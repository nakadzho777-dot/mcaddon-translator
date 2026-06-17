[Setup]
AppName=MCAddon Translator PRO
AppVersion=1.0.0
DefaultDirName={pf}\MCAddonTranslatorPRO
DefaultGroupName=MCAddon Translator PRO
OutputDir=output
OutputBaseFilename=MCAddonTranslatorPRO_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\icon.ico
PrivilegesRequired=admin

[Files]
Source: "app\gui.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Dirs]
Name: "{app}\logs"

[Icons]
Name: "{group}\MCAddon Translator PRO"; Filename: "{app}\gui.exe"
Name: "{commondesktop}\MCAddon Translator PRO"; Filename: "{app}\gui.exe"

[Run]
Filename: "{app}\gui.exe"; Description: "起動する"; Flags: nowait postinstall skipifsilent