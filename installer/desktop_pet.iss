; Inno Setup Script for DesktopPet
; Supports parameter overrides via /DName=Value:
;   /DAppVersion=1.0.0
;   /DSourceDir=dist\DesktopPet
;   /DOutBase=DesktopPet-1.0.0-Windows-Setup

#define MyAppName "DesktopPet"
#define MyAppPublisher "DesktopPet"
#define MyAppURL "https://example.com"
#define MyAppExeName "DesktopPet.exe"

#define MyAppVersion GetStringDef("AppVersion", "0.0.0")
#define SourceDir GetStringDef("SourceDir", "dist\\DesktopPet")
#define OutBase GetStringDef("OutBase", "DesktopPet-Windows-Setup")
#define OutputDir GetStringDef("OutputDir", "dist\\installer")

[Setup]
AppId={{7A9C3121-3328-4B72-9B1C-4C6C9D1B4A92}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename={#OutBase}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "额外图标:"; Flags: unchecked

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent