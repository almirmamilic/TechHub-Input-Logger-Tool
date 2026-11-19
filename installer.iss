; Inno Setup script for TechHub Input Logger Tool
; Compile with: ISCC.exe installer.iss
; (requires Inno Setup 6: https://jrsoftware.org/isinfo.php)

#define AppName "TechHub Input Logger Tool"
#define AppVersion "1.0"
#define AppExeName "TechHub Input Logger Tool.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Slydeviant
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
OutputDir=installer
OutputBaseFilename=TechHubInputLoggerTool-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
