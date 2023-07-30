[Setup]
AppId={{C7A4B040-273A-45E3-B223-C8C47A987544}}
AppName=GaziGuard
AppVersion=1.0.1
DefaultDirName={pf}\GaziGuard
DefaultGroupName=GaziGuard
UninstallDisplayIcon={app}\icon64.ico
OutputBaseFilename=GaziGuardSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\dento\Desktop\Python_Projects\modding\dl2\gazi-guard\dist\merged_output_20230729191406\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Program Files\Meld\*"; DestDir: "{pf}\Meld"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\GaziGuard"; Filename: "{app}\GaziGuard.exe"; IconFilename: "{app}\icon64.ico"
Name: "{group}\Uninstall GaziGuard"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon64.ico"

[Code]
var
  LicenseAcceptedCheckBox: TNewCheckBox;
  
procedure InitializeWizard;
var
  LicenseMemo: TMemo;
  LicensePage: TWizardPage;
  LicenseLabel: TLabel;
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
  LicenseMemo.Lines.Text :=
    '                    GNU GENERAL PUBLIC LICENSE' + #13#10 +
    '                       Version 2, June 1991' + #13#10 +
    ' ' + #13#10 +
    ' Copyright (C) 1989, 1991 Free Software Foundation, Inc.,' + #13#10 +
    ' 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA' + #13#10 +
    ' Everyone is permitted to copy and distribute verbatim copies' + #13#10 +
    ' of this license document, but changing it is not allowed.' + #13#10 +
    ' ' + #13#10 +
    '                            Preamble' + #13#10 +
    ' ' + #13#10 +
    '  The licenses for most software are designed to take away your' + #13#10 +
    ' freedom to share and change it.  By contrast, the GNU General Public' + #13#10 +
    ' License is intended to guarantee your freedom to share and change free' + #13#10 +
    ' software--to make sure the software is free for all its users.  This' + #13#10 +
    ' General Public License applies to most of the Free Software' + #13#10 +
    ' Foundation''s software and to any other program whose authors commit to' + #13#10 +
    ' using it.  (Some other Free Software Foundation software is covered by' + #13#10 +
    ' the GNU Lesser General Public License instead.)  You can apply it to' + #13#10 +
    ' your programs, too.' + #13#10 +
    ' ' + #13#10 +
    '  When we speak of free software, we are referring to freedom, not' + #13#10 +
    ' price.  Our General Public Licenses are designed to make sure that you' + #13#10 +
    ' have the freedom to distribute copies of free software (and charge for' + #13#10 +
    ' this service if you wish), that you receive source code or can get it' + #13#10 +
    ' if you want it, that you can change the software or use pieces of it' + #13#10 +
    ' in new free programs; and that you know you can do these things.' + #13#10 +
    ' ' + #13#10 +
    '  To protect your rights, we need to make restrictions that forbid' + #13#10 +
    ' anyone to deny you these rights or to ask you to surrender the rights.' + #13#10 +
    ' These restrictions translate to certain responsibilities for you if you' + #13#10 +
    ' distribute copies of the software, or if you modify it.' + #13#10 +
    ' ' + #13#10 +
    '  For example, if you distribute copies of such a program, whether' + #13#10 +
    ' gratis or for a fee, you must give the recipients all the rights that' + #13#10 +
    ' you have.  You must make sure that they, too, receive or can get the' + #13#10 +
    ' source code.  And you must show them these terms so they know their' + #13#10 +
    ' rights.' + #13#10 +
    ' ' + #13#10 +
    '  We protect your rights with two steps: (1) copyright the software, and' + #13#10 +
    ' (2) offer you this license which gives you legal permission to copy,' + #13#10 +
    ' distribute and/or modify the software.' + #13#10 +
    ' ' + #13#10 +
    '  Also, for each author''s protection and ours, we want to make certain' + #13#10 +
    ' that everyone understands that there is no warranty for this free' + #13#10 +
    ' software.  If the software is modified by someone else and passed on, we' + #13#10 +
    ' want its recipients to know that what they have is not the original, so' + #13#10 +
    ' that any problems introduced by others will not reflect on the original' + #13#10 +
    ' authors'' reputations.' + #13#10 +
    ' ' + #13#10 +
    '  Finally, any free program is threatened constantly by software' + #13#10 +
    ' patents.  We wish to avoid the danger that redistributors of a free' + #13#10 +
    ' program will individually obtain patent licenses, in effect making the' + #13#10 +
    ' program proprietary.  To prevent this, we have made it clear that any' + #13#10 +
    ' patent must be licensed for everyone''s free use or not licensed at all.' + #13#10 +
    ' ' + #13#10 +
    '  The precise terms and conditions for copying, distribution and' + #13#10 +
    ' modification follow.' + #13#10 +
    ' ' + #13#10 +
    '                    GNU GENERAL PUBLIC LICENSE' + #13#10 +
    '   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION' + #13#10 +
    ' ' + #13#10 +
    '  0. This License applies to any program or other work which contains' + #13#10 +
    ' a notice placed by the copyright holder saying it may be distributed' + #13#10 +
    ' under the terms of this General Public License.  The "Program", below,' + #13#10 +
    ' refers to any such program or work, and a "work based on the Program"' + #13#10 +
    ' means either the Program or any derivative work under copyright law:' + #13#10 +
    ' that is to say, a work containing the Program or a portion of it,' + #13#10 +
    ' either verbatim or with modifications and/or translated into another' + #13#10 +
    ' language.  (Hereinafter, translation is included without limitation in' + #13#10 +
    ' the term "modification".)  Each licensee is addressed as "you".' + #13#10 +
    ' ' + #13#10 +
    ' Activities other than copying, distribution and modification are not' + #13#10 +
    ' covered by this License; they are outside its scope.  The act of' + #13#10 +
    ' running the Program is not restricted, and the output from the Program' + #13#10 +
    ' is covered only if its contents constitute a work based on the' + #13#10 +
    ' Program (independent of having been made by running the Program).' + #13#10 +
    ' Whether that is true depends on what the Program does.' + #13#10 +
    ' ' + #13#10 +
    '  1. You may copy and distribute verbatim copies of the Program''s' + #13#10 +
    ' source code as you receive it, in any medium, provided that you' + #13#10 +
    ' conspicuously and appropriately publish on each copy an appropriate' + #13#10 +
    ' copyright notice and disclaimer of warranty; keep intact all the' + #13#10 +
    ' notices that refer to this License and to the absence of any warranty;' + #13#10 +
    ' and give any other recipients of the Program a copy of this License' + #13#10 +
    ' along with the Program.' + #13#10 +
    ' ' + #13#10 +
    ' You may charge a fee for the physical act of transferring a copy, and' + #13#10 +
    ' you may at your option offer warranty protection in exchange for a fee.' + #13#10 +
    ' ' + #13#10 +
    '  2. You may modify your copy or copies of the Program or any portion' + #13#10 +
    ' of it, thus forming a work based on the Program, and copy and' + #13#10 +
    ' distribute such modifications or work under the terms of Section 1' + #13#10 +
    ' above, provided that you also meet all of these conditions:' + #13#10 +
    ' ' + #13#10 +
    '    a) You must cause the modified files to carry prominent notices' + #13#10 +
    '    stating that you changed the files and the date of any change.' + #13#10 +
    ' ' + #13#10 +
    '    b) You must cause any work that you distribute or publish, that in' + #13#10 +
    '    whole or in part contains or is derived from the Program or any' + #13#10 +
    '    part thereof, to be licensed as a whole at no charge to all third' + #13#10 +
    '    parties under the terms of this License.' + #13#10 +
    ' ' + #13#10 +
    '    c) If the modified program normally reads commands interactively' + #13#10 +
    '    when run, you must cause it, when started running for such' + #13#10 +
    '    interactive use in the most ordinary way, to print or display an' + #13#10 +
    '    announcement including an appropriate copyright notice and a' + #13#10 +
    '    notice that there is no warranty (or else, saying that you provide' + #13#10 +
    '    a warranty) and that users may redistribute the program under' + #13#10 +
    '    these conditions, and telling the user how to view a copy of this' + #13#10 +
    '    License.  (Exception: if the Program itself is interactive but' + #13#10 +
    '    does not normally print such an announcement, your work based on' + #13#10 +
    '    the Program is not required to print an announcement.)' + #13#10 +
    ' ' + #13#10 +
    ' These requirements apply to the modified work as a whole.  If' + #13#10 +
    ' identifiable sections of that work are not derived from the Program,' + #13#10 +
    ' and can be reasonably considered independent and separate works in' + #13#10 +
    ' themselves, then this License, and its terms, do not apply to those' + #13#10 +
    ' sections when you distribute them as separate works.  But when you' + #13#10 +
    ' distribute the same sections as part of a whole which is a work based' + #13#10 +
    ' on the Program, the distribution of the whole must be on the terms of' + #13#10 +
    ' this License, whose permissions for other licensees extend to the' + #13#10 +
    ' entire whole, and thus to each and every part regardless of who wrote it.' + #13#10 +
    ' ' + #13#10 +
    ' Thus, it is not the intent of this section to claim rights or contest' + #13#10 +
    ' your rights to work written entirely by you; rather, the intent is to' + #13#10 +
    ' exercise the right to control the distribution of derivative or' + #13#10 +
    ' collective works based on the Program.' + #13#10 +
    ' ' + #13#10 +
    ' In addition, mere aggregation of another work not based on the Program' + #13#10 +
    ' with the Program (or with a work based on the Program) on a volume of' + #13#10 +
    ' a storage or distribution medium does not bring the other work under' + #13#10 +
    ' the scope of this License.' + #13#10 +
    ' ' + #13#10 +
    '  3. You may copy and distribute the Program (or a work based on it,' + #13#10 +
    ' under Section 2) in object code or executable form under the terms of' + #13#10 +
    ' Sections 1 and 2 above provided that you also do one of the following:' + #13#10 +
    ' ' + #13#10 +
    '    a) Accompany it with the complete corresponding machine-readable' + #13#10 +
    '    source code, which must be distributed under the terms of Sections' + #13#10 +
    '    1 and 2 above on a medium customarily used for software interchange; or,' + #13#10 +
    ' ' + #13#10 +
    '    b) Accompany it with a written offer, valid for at least three' + #13#10 +
    '    years, to give any third party, for a charge no more than your' + #13#10 +
    '    cost of physically performing source distribution, a complete' + #13#10 +
    '    machine-readable copy of the corresponding source code, to be' + #13#10 +
    '    distributed under the terms of Sections 1 and 2 above on a medium' + #13#10 +
    '    customarily used for software interchange; or,' + #13#10 +
    ' ' + #13#10 +
    '    c) Accompany it with the information you received as to the offer' + #13#10 +
    '    to distribute corresponding source code.  (This alternative is' + #13#10 +
    '    allowed only for noncommercial distribution and only if you' + #13#10 +
    '    received the program in object code or executable form with such' + #13#10 +
    '    an offer, in accord with Subsection b above.)' + #13#10 +
    ' ' + #13#10 +
    ' The source code for a work means the preferred form of the work for' + #13#10 +
    ' making modifications to it.  For an executable work, complete source' + #13#10 +
    ' code means all the source code for all modules it contains, plus any' + #13#10 +
    ' associated interface definition files, plus the scripts used to' + #13#10 +
    ' control compilation and installation of the executable.  However, as a' + #13#10 +
    ' special exception, the source code distributed need not include' + #13#10 +
    ' anything that is normally distributed (in either source or binary' + #13#10 +
    ' form) with the major components (compiler, kernel, and so on) of the' + #13#10 +
    ' operating system on which the executable runs, unless that component' + #13#10 +
    ' itself accompanies the executable.' + #13#10 +
    ' ' + #13#10 +
    ' If distribution of executable or object code is made by offering' + #13#10 +
    ' access to copy from a designated place, then offering equivalent' + #13#10 +
    ' access to copy the source code from the same place counts as' + #13#10 +
    ' distribution of the source code, even though third parties are not' + #13#10 +
    ' compelled to copy the source along with the object code.' + #13#10 +
    ' ' + #13#10 +
    '  4. You may not copy, modify, sublicense, or distribute the Program' + #13#10 +
    ' except as expressly provided under this License.  Any attempt' + #13#10 +
    ' otherwise to copy, modify, sublicense or distribute the Program is' + #13#10 +
    ' void, and will automatically terminate your rights under this License.' + #13#10 +
    ' However, parties who have received copies, or rights, from you under' + #13#10 +
    ' this License will not have their licenses terminated so long as such' + #13#10 +
    ' parties remain in full compliance.' + #13#10 +
    ' ' + #13#10 +
    '  5. You are not required to accept this License, since you have not' + #13#10 +
    ' signed it.  However, nothing else grants you permission to modify or' + #13#10 +
    ' distribute the Program or its derivative works.  These actions are' + #13#10 +
    ' prohibited by law if you do not accept this License.  Therefore, by' + #13#10 +
    ' modifying or distributing the Program (or any work based on the' + #13#10 +
    ' Program), you indicate your acceptance of this License to do so, and' + #13#10 +
    ' all its terms and conditions for copying, distributing or modifying' + #13#10 +
    ' the Program or works based on it.' + #13#10 +
    ' ' + #13#10 +
    '  6. Each time you redistribute the Program (or any work based on the' + #13#10 +
    ' Program), the recipient automatically receives a license from the' + #13#10 +
    ' original licensor to copy, distribute or modify the Program subject to' + #13#10 +
    ' these terms and conditions.  You may not impose any further' + #13#10 +
    ' restrictions on the recipients'' exercise of the rights granted herein.' + #13#10 +
    ' You are not responsible for enforcing compliance by third parties to' + #13#10 +
    ' this License.' + #13#10 +
    ' ' + #13#10 +
    '  7. If, as a consequence of a court judgment or allegation of patent' + #13#10 +
    ' infringement or for any other reason (not limited to patent issues),' + #13#10 +
    ' conditions are imposed on you (whether by court order, agreement or' + #13#10 +
    ' otherwise) that contradict the conditions of this License, they do not' + #13#10 +
    ' excuse you from the conditions of this License.  If you cannot' + #13#10 +
    ' distribute so as to satisfy simultaneously your obligations under this' + #13#10 +
    ' License and any other pertinent obligations, then as a consequence you' + #13#10 +
    ' may not distribute the Program at all.  For example, if a patent' + #13#10 +
    ' license would not permit royalty-free redistribution of the Program by' + #13#10 +
    ' all those who receive copies directly or indirectly through you, then' + #13#10 +
    ' the only way you could satisfy both it and this License would be to' + #13#10 +
    ' refrain entirely from distribution of the Program.' + #13#10 +
    ' ' + #13#10 +
    ' If any portion of this section is held invalid or unenforceable under' + #13#10 +
    ' any particular circumstance, the balance of the section is intended to' + #13#10 +
    ' apply and the section as a whole is intended to apply in other' + #13#10 +
    ' circumstances.' + #13#10 +
    ' ' + #13#10 +
    ' It is not the purpose of this section to induce you to infringe any' + #13#10 +
    ' patents or other property right claims or to contest validity of any' + #13#10 +
    ' such claims; this section has the sole purpose of protecting the' + #13#10 +
    ' integrity of the free software distribution system, which is' + #13#10 +
    ' implemented by public license practices.  Many people have made' + #13#10 +
    ' generous contributions to the wide range of software distributed' + #13#10 +
    ' through that system in reliance on consistent application of that' + #13#10 +
    ' system; it is up to the author/donor to decide if he or she is willing' + #13#10 +
    ' to distribute software through any other system and a licensee cannot' + #13#10 +
    ' impose that choice.' + #13#10 +
    ' ' + #13#10 +
    '  8. If the distribution and/or use of the Program is restricted in' + #13#10 +
    ' certain countries either by patents or by copyrighted interfaces, the' + #13#10 +
    ' original copyright holder who places the Program under this License' + #13#10 +
    ' may add an explicit geographical distribution limitation excluding' + #13#10 +
    ' those countries, so that distribution is permitted only in or among' + #13#10 +
    ' countries not thus excluded.  In such case, this License incorporates' + #13#10 +
    ' the limitation as if written in the body of this License.' + #13#10 +
    ' ' + #13#10 +
    '  9. The Free Software Foundation may publish revised and/or new versions' + #13#10 +
    ' of the General Public License from time to time.  Such new versions will' + #13#10 +
    ' be similar in spirit to the present version, but may differ in detail to' + #13#10 +
    ' address new problems or concerns.' + #13#10 +
    ' ' + #13#10 +
    ' Each version is given a distinguishing version number.  If the Program' + #13#10 +
    ' specifies that a certain numbered version of the GNU General Public' + #13#10 +
    ' License "or any later version" applies to it, you have the option of' + #13#10 +
    ' following the terms and conditions either of that numbered version or of' + #13#10 +
    ' any later version published by the Free Software Foundation.  If the' + #13#10 +
    ' Program does not specify a version number of the GNU General Public' + #13#10 +
    ' License, you may choose any version ever published by the Free Software' + #13#10 +
    ' Foundation.' + #13#10 +
    ' ' + #13#10 +
    '  10. If you wish to incorporate parts of the Program into other free' + #13#10 +
    ' programs whose distribution conditions are different, write to the author' + #13#10 +
    ' to ask for permission.  For software which is copyrighted by the Free' + #13#10 +
    ' Software Foundation, write to the Free Software Foundation; we sometimes' + #13#10 +
    ' make exceptions for this.  Our decision will be guided by the two goals' + #13#10 +
    ' of preserving the free status of all derivatives of our free software and' + #13#10 +
    ' of promoting the sharing and reuse of software generally.' + #13#10 +
    ' ' + #13#10 +
    '                            NO WARRANTY' + #13#10 +
    ' ' + #13#10 +
    '  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY' + #13#10 +
    ' FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN' + #13#10 +
    ' OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES' + #13#10 +
    ' PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED' + #13#10 +
    ' OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF' + #13#10 +
    ' MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS' + #13#10 +
    ' TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE' + #13#10 +
    ' PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,' + #13#10 +
    ' REPAIR OR CORRECTION.' + #13#10 +
    ' ' + #13#10 +
    '  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING' + #13#10 +
    ' WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS' + #13#10 +
    ' THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY' + #13#10 +
    ' GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE' + #13#10 +
    ' USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF' + #13#10 +
    ' DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD' + #13#10 +
    ' PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN' + #13#10 +
    ' IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH' + #13#10 +
    ' DAMAGES.' + #13#10 +
    ' ' + #13#10 +
    '  END OF TERMS AND CONDITIONS' + #13#10 +
    ' ' + #13#10 +
    ' ' + #13#10 +
    '     How to Apply These Terms to Your New Programs' + #13#10 +
    ' ' + #13#10 +
    ' If you develop a new program, and you want it to be of the greatest' + #13#10 +
    ' possible use to the public, the best way to achieve this is to make it' + #13#10 +
    ' free software which everyone can redistribute and change under these terms.' + #13#10 +
    ' ' + #13#10 +
    ' To do so, attach the following notices to the program.  It is safest' + #13#10 +
    ' to attach them to the start of each source file to most effectively' + #13#10 +
    ' state the exclusion of warranty; and each file should have at least' + #13#10 +
    ' the "copyright" line and a pointer to where the full notice is found.' + #13#10 +
    ' ' + #13#10 +
    '     One line to give the program''s name and an idea of what it does.' + #13#10 +
    '     Copyright (C) yyyy  name of author' + #13#10 +
    '     This program is free software; you can redistribute it and/or modify' + #13#10 +
    '     it under the terms of the GNU General Public License as published by' + #13#10 +
    '     the Free Software Foundation; either version 2 of the License, or' + #13#10 +
    '     (at your option) any later version.' + #13#10 +
    ' ' + #13#10 +
    '     This program is distributed in the hope that it will be useful,' + #13#10 +
    '     but WITHOUT ANY WARRANTY; without even the implied warranty of' + #13#10 +
    '     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the' + #13#10 +
    '     GNU General Public License for more details.' + #13#10 +
    ' ' + #13#10 +
    '     You should have received a copy of the GNU General Public License' + #13#10 +
    '     along with this program; if not, write to the Free Software' + #13#10 +
    '     Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA' + #13#10 +
    ' ' + #13#10 +
    ' Also add information on how to contact you by electronic and paper mail.' + #13#10 +
    ' ' + #13#10 +
    ' If the program does terminal interaction, make it output a short' + #13#10 +
    ' notice like this when it starts in an interactive mode:' + #13#10 +
    ' ' + #13#10 +
    '     Gnomovision version 69, Copyright (C) year name of author' + #13#10 +
    '     Gnomovision comes with ABSOLUTELY NO WARRANTY; for details type `show w`' + #13#10 +
    '     This is free software, and you are welcome to redistribute it' + #13#10 +
    '     under certain conditions; type `show c'' for details.' + #13#10 +
    ' ' + #13#10 +
    ' The hypothetical commands `show w'' and `show c'' should show the appropriate' + #13#10 +
    ' parts of the General Public License.  Of course, your program''s commands' + #13#10 +
    ' might be different; for a GUI interface, you would use an "about box".' + #13#10 +
    ' ' + #13#10 +
    ' You should also get your employer (if you work as a programmer) or your' + #13#10 +
    ' school, if any, to sign a "copyright disclaimer" for the program, if' + #13#10 +
    ' necessary.  Here is a sample; alter the names:' + #13#10 +
    ' ' + #13#10 +
    '     Yoyodyne, Inc., hereby disclaims all copyright interest in the program' + #13#10 +
    '     `Gnomovision'' (which makes passes at compilers) written by James Hacker.' + #13#10 +
    ' ' + #13#10 +
    '     signature of Ty Coon, 1 April 1989' + #13#10 +
    '     Ty Coon, President of Vice' + #13#10 +
    ' ' + #13#10 +
    ' This General Public License does not permit incorporating your program into' + #13#10 +
    ' proprietary programs.  If your program is a subroutine library, you may' + #13#10 +
    ' consider it more useful to permit linking proprietary applications with the' + #13#10 +
    ' library.  If this is what you want to do, use the GNU Lesser General' + #13#10 +
    ' Public License instead of this License.  But first, please read ' + #13#10 +
    'http://www.gnu.org/philosophy/why-not-lgpl.html' + #13#10 +
    ' ' + #13#10 +
    '  END OF TERMS AND CONDITIONS' + #13#10 

  LicenseLabel := TLabel.Create(WizardForm);
  LicenseLabel.Parent := LicensePage.Surface;
  LicenseLabel.Left := 0;
  LicenseLabel.Top := LicenseMemo.Height + 10;
  LicenseLabel.Width := LicensePage.SurfaceWidth;
  LicenseLabel.Caption := 'Do you accept the terms of the license agreement? By continuing, you agree to the'
   + ' terms set forth by Meld editor';

  LicenseAcceptedCheckBox := TNewCheckBox.Create(WizardForm);
  LicenseAcceptedCheckBox.Parent := LicensePage.Surface;
  LicenseAcceptedCheckBox.Left := LicenseLabel.Left;
  LicenseAcceptedCheckBox.Top := LicenseLabel.Top + LicenseLabel.Height + 5;
  LicenseAcceptedCheckBox.Width := LicensePage.SurfaceWidth;
  LicenseAcceptedCheckBox.Caption := 'I accept the terms of the license agreement';
end;


function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = wpLicense) and LicenseAcceptedCheckBox.Checked;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if (CurPageID = wpReady) and not LicenseAcceptedCheckBox.Checked then
  begin
    MsgBox('You must accept the terms of the license agreement to continue.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;
