; ============================================================
;  FileFinder - Instalador con selección de idioma (Inno Setup 6.3+)
;  Colocar este archivo en la carpeta FileFinder\ (junto a dist\ y logo.ico)
;  Compilar: abrir en Inno Setup y pulsar Ctrl+F9
;  Resultado: installer\FileFinder-Setup.exe
; ============================================================

#define MyAppName      "FileFinder"
#define MyAppVersion   "1.0"
#define MyAppPublisher "FileFinder"

[Setup]
; GUID único de la app (no lo cambies entre versiones para que actualice bien)
AppId={{B7E2C1D4-5A3F-4E8B-9C21-6D0F4A7E1B35}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=FileFinder-Setup
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\logo.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; Siempre preguntar el idioma al arrancar el instalador
ShowLanguageDialog=yes
UsePreviousLanguage=no

; Los .exe son de 64 bits
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Instala para el usuario actual sin pedir admin (puede elegir "todos los usuarios")
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Según el idioma elegido se instala un exe u otro
Source: "dist\FileFinderEN.exe"; DestDir: "{app}"; Flags: ignoreversion; Languages: english
Source: "dist\FileFinderES.exe"; DestDir: "{app}"; Flags: ignoreversion; Languages: spanish
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[InstallDelete]
; Si ya había instalada la otra versión, la elimina para no dejar los dos
Type: files; Name: "{app}\FileFinderES.exe"; Languages: english
Type: files; Name: "{app}\FileFinderEN.exe"; Languages: spanish

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\FileFinderEN.exe"; IconFilename: "{app}\logo.ico"; Languages: english
Name: "{group}\{#MyAppName}"; Filename: "{app}\FileFinderES.exe"; IconFilename: "{app}\logo.ico"; Languages: spanish
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\FileFinderEN.exe"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon; Languages: english
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\FileFinderES.exe"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon; Languages: spanish

[Run]
Filename: "{app}\FileFinderEN.exe"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent; Languages: english
Filename: "{app}\FileFinderES.exe"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent; Languages: spanish
