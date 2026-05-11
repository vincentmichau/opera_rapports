#define MyAppName "Opera Rapports"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Opera Rapports"
#define MyAppExeName "opera-rapports.exe"

[Setup]
AppId={{7D857949-7C90-4C1F-A88D-26394D5D7A40}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Opera Rapports
DefaultGroupName={#MyAppName}
OutputBaseFilename=OperaRapports-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le bureau"; GroupDescription: "Raccourcis :"

[Files]
Source: "..\..\dist\opera-rapports\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent
