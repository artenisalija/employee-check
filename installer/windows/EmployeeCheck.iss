#ifndef AppVersion
#define AppVersion "0.1.0"
#endif

#ifndef RoleName
#define RoleName "Employee"
#endif

#ifndef RoleArg
#define RoleArg "employee"
#endif

#ifndef OutputBaseFilename
#define OutputBaseFilename "EmployeeCheck-Windows-Employee-Setup"
#endif

[Setup]
AppName=Employee Check {#RoleName}
AppVersion={#AppVersion}
AppPublisher=Employee Check
DefaultDirName={autopf}\Employee Check {#RoleName}
DefaultGroupName=Employee Check
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installers
OutputBaseFilename={#OutputBaseFilename}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\EmployeeCheck.exe

[Files]
Source: "..\..\dist\EmployeeCheck.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Employee Check {#RoleName}"; Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"
Name: "{commondesktop}\Employee Check {#RoleName}"; Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "EmployeeCheck{#RoleName}"; ValueData: """{app}\EmployeeCheck.exe"" {#RoleArg}"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"; Description: "Launch Employee Check {#RoleName}"; Flags: nowait postinstall skipifsilent

