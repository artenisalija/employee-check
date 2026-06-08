#ifndef AppVersion
#define AppVersion "0.1.6"
#endif

#ifndef RoleName
#define RoleName "Employee"
#endif

#ifndef RoleArg
#define RoleArg "employee"
#endif

#ifndef OutputBaseFilename
#define OutputBaseFilename "EmployeeCheck-v0.1.6-Windows-Employee-Setup"
#endif

[Setup]
AppName=Employee Check {#RoleName}
AppVersion={#AppVersion}
AppPublisher=Employee Check
AppId=EmployeeCheck-{#RoleArg}
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
CloseApplications=yes
CloseApplicationsFilter=EmployeeCheck.exe
RestartApplications=no

[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Files]
Source: "..\..\dist\EmployeeCheck.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\installers\EmployeeCheck-v{#AppVersion}-Windows-Full-Uninstall.ps1"; DestDir: "{app}"; DestName: "Full-Uninstall.ps1"; Flags: ignoreversion

[Icons]
Name: "{group}\Employee Check {#RoleName}"; Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"
Name: "{commondesktop}\Employee Check {#RoleName}"; Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "EmployeeCheck{#RoleName}"; ValueData: """{app}\EmployeeCheck.exe"" {#RoleArg}"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\EmployeeCheck.exe"; Parameters: "{#RoleArg}"; Description: "Launch Employee Check {#RoleName}"; Flags: nowait postinstall skipifsilent

[Code]
const
  UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall';

procedure StopRunningEmployeeCheck;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/IM EmployeeCheck.exe /F /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure RunUninstaller(UninstallString: string);
var
  ExePath: string;
  Params: string;
  QuoteEnd: Integer;
  SpacePos: Integer;
  ResultCode: Integer;
begin
  UninstallString := Trim(UninstallString);
  ExePath := '';
  Params := '';
  if UninstallString = '' then
    exit;

  if UninstallString[1] = '"' then begin
    QuoteEnd := Pos('"' , Copy(UninstallString, 2, Length(UninstallString)));
    if QuoteEnd > 0 then begin
      ExePath := Copy(UninstallString, 2, QuoteEnd - 1);
      Params := Trim(Copy(UninstallString, QuoteEnd + 2, Length(UninstallString)));
    end;
  end else begin
    SpacePos := Pos(' ', UninstallString);
    if SpacePos > 0 then begin
      ExePath := Copy(UninstallString, 1, SpacePos - 1);
      Params := Trim(Copy(UninstallString, SpacePos + 1, Length(UninstallString)));
    end else begin
      ExePath := UninstallString;
      Params := '';
    end;
  end;

  if ExePath = '' then
    exit;

  if Pos('/VERYSILENT', Uppercase(Params)) = 0 then
    Params := Params + ' /VERYSILENT /SUPPRESSMSGBOXES /NORESTART';
  Exec(ExePath, Params, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure UninstallExistingRole;
var
  Subkeys: TArrayOfString;
  I: Integer;
  Subkey: string;
  DisplayName: string;
  QuietUninstallString: string;
  UninstallString: string;
begin
  if RegGetSubkeyNames(HKLM, UninstallKey, Subkeys) then begin
    for I := 0 to GetArrayLength(Subkeys) - 1 do begin
      Subkey := UninstallKey + '\' + Subkeys[I];
      if RegQueryStringValue(HKLM, Subkey, 'DisplayName', DisplayName) then begin
        if DisplayName = 'Employee Check {#RoleName}' then begin
          if RegQueryStringValue(HKLM, Subkey, 'QuietUninstallString', QuietUninstallString) then
            RunUninstaller(QuietUninstallString)
          else if RegQueryStringValue(HKLM, Subkey, 'UninstallString', UninstallString) then
            RunUninstaller(UninstallString);
        end;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  OldDir: string;
begin
  if CurStep = ssInstall then begin
    StopRunningEmployeeCheck;
    UninstallExistingRole;
    OldDir := ExpandConstant('{app}');
    if DirExists(OldDir) then
      DelTree(OldDir, True, True, True);
  end;
end;
