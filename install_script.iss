[Setup]
AppId={{C7A4B040-273A-45E3-B223-C8C47A987544}}
AppName=GaziGuard
AppVersion=0.1.0
DefaultDirName={pf}\GaziGuard
DefaultGroupName=GaziGuard
UninstallDisplayIcon={app}\icon64.ico
OutputBaseFilename=GaziGuardSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\dento\Desktop\Python_Projects\modding\dl2\pak_merge_helper\distro\2023.07.22 Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\dento\Desktop\Python_Projects\modding\dl2\pak_merge_helper\distro\meld\*"; DestDir: "{pf}\Meld"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\GaziGuard"; Filename: "{app}\GaziGuard.exe"; IconFilename: "{app}\icon64.ico"
Name: "{group}\Uninstall GaziGuard"; Filename: "{uninstallexe}"

[Code]
var
  LicenseAccepted: boolean;

procedure LicenseButtonClick(Sender: TObject);
begin
  LicenseAccepted := True;
end;

procedure InitializeWizard;
var
  LicenseMemo: TMemo;
  LicensePage: TWizardPage;
  LicenseLabel: TLabel;
  LicenseButton: TButton;
begin
  LicensePage := CreateCustomPage(wpWelcome, 'License Agreement', 'Please read the following license agreement:');
  LicenseMemo := TMemo.Create(WizardForm);
  LicenseMemo.Parent := LicensePage.Surface;
  LicenseMemo.Left := 0;
  LicenseMemo.Top := 0;
  LicenseMemo.Width := LicensePage.SurfaceWidth;
  LicenseMemo.Height := LicensePage.SurfaceHeight - 70;
  LicenseMemo.ScrollBars := ssVertical;
  LicenseMemo.ReadOnly := True;
  LicenseMemo.Lines.LoadFromFile('C:\Users\dento\Desktop\Python_Projects\modding\dl2\pak_merge_helper\distro\meld\license.txt'); 

  LicenseLabel := TLabel.Create(WizardForm);
  LicenseLabel.Parent := LicensePage.Surface;
  LicenseLabel.Left := 0;
  LicenseLabel.Top := LicenseMemo.Height + 10;
  LicenseLabel.Width := LicensePage.SurfaceWidth;
  LicenseLabel.Caption := 'Do you accept the terms of the license agreement?';

  LicenseButton := TButton.Create(WizardForm);
  LicenseButton.Parent := LicensePage.Surface;
  LicenseButton.Left := LicensePage.SurfaceWidth - 100;
  LicenseButton.Top := LicenseMemo.Height + 35;
  LicenseButton.Width := 75;
  LicenseButton.Caption := 'Accept';
  LicenseButton.OnClick := @LicenseButtonClick;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = wpLicense) and LicenseAccepted;
end;

