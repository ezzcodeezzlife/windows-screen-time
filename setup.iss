; Inno Setup Installer Script for Screen Time Tracker
; This creates a one-click installer that sets up auto-start and shortcuts

[Setup]
AppName=Screen Time Tracker
AppVersion=1.0
AppPublisher=Screen Time Tracker
AppPublisherURL=
DefaultDirName={autopf}\ScreenTimeTracker
DefaultGroupName=Screen Time Tracker
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=ScreenTimeTracker_Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenu"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ScreenTimeTracker.exe"; DestDir: "{app}"; Flags: ignoreversion
; Note: Don't use a DefaultDirName of {app}\bin to avoid putting the executable in a subfolder

[Icons]
Name: "{group}\Screen Time Tracker"; Filename: "{app}\ScreenTimeTracker.exe"
Name: "{group}\{cm:UninstallProgram,Screen Time Tracker}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Screen Time Tracker"; Filename: "{app}\ScreenTimeTracker.exe"; Tasks: desktopicon
Name: "{userstartmenu}\Programs\Screen Time Tracker"; Filename: "{app}\ScreenTimeTracker.exe"; Tasks: startmenu

[Run]
Filename: "{app}\ScreenTimeTracker.exe"; Description: "{cm:LaunchProgram,Screen Time Tracker}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom code to set up auto-start in registry
procedure CurStepChanged(CurStep: TSetupStep);
var
  RegPath: String;
  ExePath: String;
begin
  if CurStep = ssPostInstall then
  begin
    RegPath := 'Software\Microsoft\Windows\CurrentVersion\Run';
    ExePath := ExpandConstant('{app}\ScreenTimeTracker.exe');
    RegWriteStringValue(HKEY_CURRENT_USER, RegPath, 'ScreenTimeTracker', ExePath);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  RegPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegPath := 'Software\Microsoft\Windows\CurrentVersion\Run';
    RegDeleteValue(HKEY_CURRENT_USER, RegPath, 'ScreenTimeTracker');
  end;
end;

