Imports System
Imports System.Collections
Imports System.Diagnostics
Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Drawing.Imaging
Imports System.IO
Imports System.Runtime.CompilerServices
Imports System.Text
Imports System.Threading
Imports System.Windows.Forms
Imports BitMiracle.LibTiff.Classic
Imports ClosedXML.Excel
Imports fileconverter.DebenuPDFLibraryDLL1811
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices
Imports Scripting

Namespace fileconverter
	' Token: 0x02000046 RID: 70
	Friend NotInheritable Module modMain
		' Token: 0x06000E33 RID: 3635 RVA: 0x0001A972 File Offset: 0x00018B72
		Public Sub InitVintaSoft()
		End Sub

		' Token: 0x06000E34 RID: 3636 RVA: 0x00083044 File Offset: 0x00081244
		<STAThread()>
		Public Sub Main()
			Dim fixedLengthString As FixedLengthString = New FixedLengthString(100)
			If File.Exists(MyProject.Application.Info.DirectoryPath + "\PDFRenderer.txt") Then
				File.Delete(MyProject.Application.Info.DirectoryPath + "\PDFRenderer.txt")
			End If
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			modMain.temppath = modMain.GiveIni(text, "SYSTEM", "RAMDRIVE")
			Dim value As String
			If Not Directory.Exists(modMain.temppath) Then
				Dim text2 As String = "Folder for temporary data [SYSTEM.RAMDRIVE]=<" + modMain.temppath + "> doesn't exist!"
				Dim num As Short = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num, value)
			End If
			If Not Directory.Exists(MyProject.Application.Info.DirectoryPath + "\FilmLogs") Then
				Directory.CreateDirectory(MyProject.Application.Info.DirectoryPath + "\FilmLogs")
			End If
			value = "taskkill /F /T /IM PDFRenderer.exe"
			modMonitorTest.ExecCmd(value)
			value = "taskkill /F /T /IM PDFRenderer2.exe"
			modMonitorTest.ExecCmd(value)
			modMain.DeleteTempFiles()
			If Environment.Is64BitOperatingSystem Then
				modMain.lib1 = New PDFLibrary("DebenuPDFLibrary64DLL1811.dll")
			Else
				modMain.lib1 = New PDFLibrary("DebenuPDFLibraryDLL1811.dll")
			End If
			modMain.lib1.UnlockKey("jg5pb3k89yt49n34x74n7oj9y")
			Dim flag As Boolean = modMain.lib1.Unlocked() <> 0
			If Environment.Is64BitOperatingSystem Then
				modMain.lib1.SetPDFiumFileName("QPL1811PDFium64.DLL")
			Else
				modMain.lib1.SetPDFiumFileName("QPL1811PDFium.DLL")
			End If
			modDeclares.SystemData.Initialize()
			modDeclares.SystemData.VacErrorFile = MyProject.Application.Info.DirectoryPath + "\Vac.BMP"
			modDeclares.SystemData.RetryFirstLevel = 1S
			modDeclares.SystemData.ExtendedVacuumHandling = True
			modDeclares.SystemData.VacSteps = 20
			modDeclares.SystemData.RetrySecondLevel = 3
			modMain.SiColor = Information.RGB(245, 156, 42)
			value = "STARTED"
			modDeclares.OutputDebugString(value)
			Dim num2 As Integer = CInt(Math.Round(modMain.GetAvailableMem()))
			modMain.LoadSystemData()
			If modDeclares.SystemData.EXCELPROTOCOL AndAlso File.Exists(MyProject.Application.Info.DirectoryPath + "\xlsx.txt") Then
				File.Delete(MyProject.Application.Info.DirectoryPath + "\xlsx.txt")
			End If
			If modDeclares.SystemData.JPEGProcessor Then
				value = "taskkill /F /T /IM jpegaufbereiter.exe"
				modMonitorTest.ExecCmd(value)
			End If
			Dim value2 As String
			If modDeclares.SystemData.UsePdf2Img Then
				value = "PDF2IMG is no longer supported!"
				Dim num As Short = 0S
				value2 = "file-converter"
				modMain.msgbox2(value, num, value2)
			End If
			modLicense.WriteLastStarted()
			If Not modDeclares.UseDebug Then
				While True
					modMain.frmcomm1 = New frmComm()
					modMain.frmcomm1.Init()
					value2 = "LEDan"
					modDeclares.OutputDebugString(value2)
					If modSMCi.LEDAnSMCi() Then
						Exit For
					End If
					MyProject.Forms.frmNoConnection.ShowDialog()
					If modDeclares.UseDebug Then
						GoTo IL_3AE
					End If
					modMain.frmcomm1.DeInit()
				End While
				modSMCi.VakuumAusSMCi()
				Dim isOpen As Boolean = modMain.frmcomm1.MSComm1.IsOpen
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.SetTrinamicData(modTrinamic.InitTrinamic)
					modTrinamic.SendIniDataToTrinamic(modTrinamic.InitTrinamic)
				End If
				value2 = "nach LEDan"
				modDeclares.OutputDebugString(value2)
				If Not modDeclares.SystemData.SMCI Then
					modDeclares.Outputs = modDeclares.Outputs Or 8
					Dim text3 As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
						modMultiFly.Comm_Send(text3)
						value2 = "Comm_Read"
						modDeclares.OutputDebugString(value2)
						Dim num3 As Integer = 1
						text3 = modMultiFly.Comm_Read(num3, True)
						value2 = "nach Comm_Read"
						modDeclares.OutputDebugString(value2)
					End If
				End If
			End If
			IL_3AE:
			New FixedLengthString(256)
			If modDeclares.SystemData.UseAccuv16 Then
				value2 = "StaudeFoto"
				If modDeclares.IG_lic_solution_name_set(value2) <> 0 Then
					value2 = "Accu-Solution Name Error"
					Dim num As Short = 16S
					value = "file-converter"
					modMain.msgbox2(value2, num, value)
				End If
				If modDeclares.IG_lic_solution_key_set(-344470489, -1429975326, -722623364, -1093339212) <> 0 Then
					value = "Accu-Solution Key Error"
					Dim num As Short = 16S
					value2 = "file-converter"
					modMain.msgbox2(value, num, value2)
				End If
				value2 = "1.0.EgHzM07CLgizWSZG7e8g7CTzTuTVBKWKiV30MdIFLC7gHVPKPYcScV3YP0Lu9V3K7NilTSZKcNxE7EM0PYPSWYiV7YMdPzPgcdcY3FieBgBKcK9lIeZF3d7gMS7VLzxFWe3VBgTSWCZV8KxuTgHYTgLeBGxzWFHNxETCiFxKZz8CBEMuTdMV9SigZ0xliuTN80iN9d8NB0Z0Z0cdMdHKLCczHV7FZKIS3F3dTG3gIK7dZEZgBEMe7uizHl8uZlTeWu7V7zPl7lxVTE8YiY9d7VcNHCWeMdiYxeMzIKxE9lxKIKP03SxFclZSTg8SHKZYiV8YBFBYPYLY90Wg8CcgcNBYZCc0xSZVZe3EIzcNICHCPViCTV8ucd9KcFxUTZd"
				If modDeclares.IG_lic_OEM_license_key_set(value2) <> 0 Then
					value2 = "Accu-License Error"
					Dim num As Short = 16S
					value = "file-converter"
					modMain.msgbox2(value2, num, value)
				End If
				value = "JPEG2K"
				If modDeclares.IG_comm_comp_attach(value) <> 0 Then
					value = "Accu-JPEG2K Component Error!"
					Dim num As Short = 16S
					value2 = "file-converter"
					modMain.msgbox2(value, num, value2)
				End If
				value2 = "LZW"
				If modDeclares.IG_comm_comp_attach(value2) <> 0 Then
					value2 = "Accu-LZW Component Error!"
					Dim num As Short = 16S
					value = "file-converter"
					modMain.msgbox2(value2, num, value)
				End If
				value = "ABIC"
				If modDeclares.IG_comm_comp_attach(value) <> 0 Then
					value = "Accu-ABIC Component Error!"
					Dim num As Short = 16S
					value2 = "file-converter"
					modMain.msgbox2(value, num, value2)
				End If
			End If
			If modDeclares.IsSMA Then
				modDeclares.Version = "SMA 51 6.00.00-99 (12.02.2025)"
			Else
				modDeclares.Version = "file-converter 16/35 6.00.00-99 (12.02.2025)"
			End If
			modMain.CheckTextFileVersion()
			modMain.ReadExtensions()
			modDeclares.UserLevel = 1S
			modDeclares.InCore = False
			modMain.codes(1) = 101L
			modMain.codes(2) = 167L
			modMain.codes(3) = 239L
			modMain.codes(4) = 313L
			modMain.codes(5) = 397L
			modMain.codes(6) = 467L
			modMain.codes(7) = 569L
			modMain.codes(8) = 643L
			modDeclares.DEMOVERSION = True
			Dim str As String = "0"
			value2 = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			modDeclares.ALIAS_WERT = CShort(Math.Round(Conversion.Val(str + modMain.GiveIni(value2, "SYSTEM", "ALIAS"))))
			value2 = "SYSTEM"
			value = "SIMULATION"
			Dim nDefault As Integer = 0
			Dim text4 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			modDeclares.UseDebug = (modDeclares.GetPrivateProfileInt(value2, value, nDefault, text4) = 1)
			text4 = "SYSTEM"
			value = "SIMULATIONDELAY"
			Dim nDefault2 As Integer = 0
			value2 = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			modDeclares.SystemData.SIMULATIONDELAY = modDeclares.GetPrivateProfileInt(text4, value, nDefault2, value2)
			modDeclares.LastRelease = DateAndTime.Now
			modMultiFly.InitTable()
			text = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "RELEASEKEY"), "76467-OEM-0052905-35802", False) = 0 Then
				modDeclares.DEMOVERSION = False
			End If
			modDeclares.Sec_Width = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "SECONDARY_WIDTH"))))
			If modDeclares.Sec_Width = 0 Then
				modDeclares.Sec_Width = 2048
			End If
			modDeclares.Sec_Height = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "SECONDARY_HEIGHT"))))
			If modDeclares.Sec_Height = 0 Then
				modDeclares.Sec_Height = 1536
			End If
			Dim text5 As String = "C:\"
			Dim fixedLengthString2 As FixedLengthString = fixedLengthString
			Dim fixedLengthString3 As FixedLengthString = fixedLengthString2
			value2 = fixedLengthString2.Value
			Dim nVolumeNameSize As Integer = 100
			Dim fixedLengthString4 As FixedLengthString = fixedLengthString
			Dim fixedLengthString5 As FixedLengthString = fixedLengthString4
			value = fixedLengthString4.Value
			Dim number As Integer
			Dim num4 As Integer
			modDeclares.GetVolumeInformation(text5, value2, nVolumeNameSize, number, num4, num4, value, 100)
			fixedLengthString5.Value = value
			fixedLengthString3.Value = value2
			modDeclares.SystemData.SplitLicenseOK = False
			If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "SPLITKEY"), Conversion.Hex(number), False) = 0 Then
				modDeclares.SystemData.SplitLicenseOK = True
			End If
			If Not modDeclares.SystemData.SplitLicenseOK Then
				Dim text6 As String = Conversion.Hex(number)
				While Strings.Len(text6) < 8
					text6 = "0" + text6
				End While
				Dim num5 As Integer = 1
				Dim text7 As String
				Do
					' The following expression was wrapped in a unchecked-expression
					Dim number2 As Integer = CInt((CLng(Strings.Asc(Strings.Mid(text6, num5, 1))) * modMain.codes(num5)))
					text7 += Conversion.Hex(number2)
					num5 += 1
				Loop While num5 <= 8
				If Operators.CompareString(text7, modMain.GiveIni(text, "SYSTEM", "SPLITKEY"), False) = 0 Then
					modDeclares.SystemData.SplitLicenseOK = True
				End If
			End If
			MyProject.Forms.frmSMAMain.ShowDialog()
		End Sub

		' Token: 0x06000E35 RID: 3637 RVA: 0x00083880 File Offset: 0x00081A80
		Public Function Inits() As Boolean
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000E36 RID: 3638 RVA: 0x00083890 File Offset: 0x00081A90
		Public Sub MF(ByRef FText As String, Optional ByRef FFkt As String = "", Optional ByRef FNummer As Integer = 0, Optional ByRef FBetr As String = "")
			Dim str As String = FText
			If Strings.Len(FFkt) > 0 Then
				str = str + modDeclares.RT + modDeclares.RT
				str = str + "Module:      " + FFkt
			End If
			If Conversion.Val(Conversions.ToString(FNummer)) <> 0.0 Then
				str = str + modDeclares.RT + modDeclares.RT
				str = str + "Errorcode: " + Support.Format(FNummer, "#########", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			End If
			If Strings.Len(FBetr) <> 0 Then
				str = str + modDeclares.RT + modDeclares.RT
				str = str + "Source :    " + FBetr
			End If
			Dim text As String = str + modDeclares.RT
			Dim num As Short = 16S
			Dim text2 As String = "file-converter - Error"
			modMain.msgbox2(text, num, text2)
		End Sub

		' Token: 0x06000E37 RID: 3639 RVA: 0x0008395C File Offset: 0x00081B5C
		Public Sub MI(ByRef text As String)
			Dim num As Short = 64S
			Dim text2 As String = "file-converter - Info"
			modMain.msgbox2(text, num, text2)
		End Sub

		' Token: 0x06000E38 RID: 3640 RVA: 0x00083980 File Offset: 0x00081B80
		Public Function GiveIni(ByRef file As String, Topic As String, Item As String) As String
			Dim text As String = Strings.Space(200)
			Dim text2 As String = ""
			Dim obj As Object = modDeclares.GetPrivateProfileStringA(Topic, Item, text2, text, 200, file)
			Return modMain.cTrim(text)
		End Function

		' Token: 0x06000E39 RID: 3641 RVA: 0x000839C0 File Offset: 0x00081BC0
		Public Function GiveIniW(ByRef file As String, Topic As String, Item As String) As String
			Dim stringBuilder As StringBuilder = New StringBuilder(200)
			Dim obj As Object = modDeclares.GetPrivateProfileStringW(Topic, Item, "", stringBuilder, 200, file)
			Return stringBuilder.ToString()
		End Function

		' Token: 0x06000E3A RID: 3642 RVA: 0x000839FC File Offset: 0x00081BFC
		Public Function cTrim(text As String) As String
			If Strings.InStr(1, text, Conversions.ToString(Strings.Chr(Conversions.ToInteger("0"))), Microsoft.VisualBasic.CompareMethod.Binary) > 0 Then
				' The following expression was wrapped in a checked-expression
				text = Strings.Left(text, Strings.InStr(1, text, Conversions.ToString(Strings.Chr(Conversions.ToInteger("0"))), Microsoft.VisualBasic.CompareMethod.Binary) - 1)
			End If
			Return text
		End Function

		' Token: 0x06000E3B RID: 3643 RVA: 0x00083A54 File Offset: 0x00081C54
		Public Function msgbox2(ByRef text_alt As String, Optional ByRef flags As Short = 0, Optional ByRef Cap As String = "file-converter") As Short
			Dim array As Integer() = New Integer(3) {}
			If modDeclares.IsSMA Then
				Cap = "SMA 51"
			End If
			Dim num As Integer
			Select Case flags And 7S
				Case 0S
					num = 1
					array(1) = 2
				Case 1S
					num = 2
					array(1) = 2
					array(2) = 5
				Case 2S
					num = 3
					array(1) = 5
					array(2) = 1
					array(3) = 0
				Case 3S
					num = 3
					array(1) = 3
					array(2) = 4
					array(3) = 5
				Case 4S
					num = 2
					array(1) = 3
					array(2) = 4
				Case 5S
					num = 2
					array(1) = 1
					array(2) = 5
			End Select
			Dim text As String = text_alt
			Dim num2 As Integer = 0
			Dim num3 As Integer = 0
			Dim num4 As Integer = 1
			Dim size As modDeclares.Size
			Do
				Dim text2 As String
				If Strings.InStr(num3 + 1, text, vbLf, Microsoft.VisualBasic.CompareMethod.Binary) > 0 Then
					text2 = " " + Strings.Mid(text, num3 + 1, Strings.InStr(num3 + 1, text, vbLf, Microsoft.VisualBasic.CompareMethod.Binary) - num3 - 1) + " "
					num3 = Strings.InStr(num3 + 1, text, vbLf, Microsoft.VisualBasic.CompareMethod.Binary)
					num4 += 1
				Else
					text2 = " " + Strings.Mid(text, num3 + 1) + " "
					num3 = 0
				End If
				Dim sizeF As SizeF = MyProject.Forms.frmMessage.CreateGraphics().MeasureString(text2, MyProject.Forms.frmMessage.Font)
				modDeclares.GetTextExtentPoint32(CInt(MyProject.Forms.frmMessage.CreateGraphics().GetHdc()), text2, Strings.Len(text2), size)
				If CSng(num2) < sizeF.Width Then
					num2 = CInt(Math.Round(CDbl(sizeF.Width)))
				End If
			Loop While num3 <> 0
			Dim hdc As Integer = CInt(MyProject.Forms.frmMessage.CreateGraphics().GetHdc())
			Dim text3 As String = "QqÄ"
			modDeclares.GetTextExtentPoint32(hdc, text3, 3, size)
			Dim num5 As Integer = CInt(Math.Round(CDbl((MyProject.Forms.frmMessage.CreateGraphics().MeasureString("QqÄ", MyProject.Forms.frmMessage.Font).Height * CSng(num4) * Support.TwipsPerPixelY()))))
			Dim num6 As Integer = CInt(Math.Round(CDbl((CSng(num2) * Support.TwipsPerPixelX()))))
			Dim frmMessage As frmMessage = MyProject.Forms.frmMessage
			Dim num7 As Integer = CInt(Math.Round(Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(1S).Left)) - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(0S).Left)) - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(0S).Width))))
			Dim i As Integer = 0
			Do
				frmMessage.cmdBut(CShort(i)).Visible = False
				i += 1
			Loop While i <= 5
			Dim num8 As Integer = num
			i = 1
			While i <= num8
				frmMessage.cmdBut(CShort(array(i))).Visible = True
				i += 1
			End While
			Dim num9 As Integer = CInt(Math.Round(Support.PixelsToTwipsY(CDbl(frmMessage.Height)) - Support.PixelsToTwipsY(CDbl(frmMessage.lblInfo.Height)) - Support.PixelsToTwipsY(CDbl(frmMessage.cmdBut(0S).Height))))
			Dim num10 As Integer = CInt(Math.Round(Support.PixelsToTwipsX(CDbl(frmMessage.Width)) - Support.PixelsToTwipsX(CDbl(frmMessage.lblInfo.Width))))
			Dim num11 As Integer = CInt(Math.Round(Support.PixelsToTwipsY(CDbl(frmMessage.Height)) - Support.PixelsToTwipsY(CDbl(frmMessage.cmdBut(0S).Top))))
			frmMessage.lblInfo.Text = text
			frmMessage.lblInfo.Width = CInt(Math.Round(Support.TwipsToPixelsX(CDbl(num6))))
			frmMessage.lblInfo.Height = CInt(Math.Round(Support.TwipsToPixelsY(CDbl(num5))))
			Dim num12 As Integer
			Select Case num
				Case 2
					num12 = 350
			End Select
			frmMessage.Height = CInt(Math.Round(Support.TwipsToPixelsY(Support.PixelsToTwipsY(CDbl(frmMessage.lblInfo.Height)) + Support.PixelsToTwipsY(CDbl(frmMessage.cmdBut(0S).Height)) + CDbl(num9))))
			frmMessage.Width = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.lblInfo.Width)) + CDbl(num10))))
			If frmMessage.Width < num12 Then
				frmMessage.Width = num12
				frmMessage.lblInfo.Left = CInt(Math.Round(CDbl(num12) / 2.0 - CDbl(frmMessage.lblInfo.Width) / 2.0))
			End If
			frmMessage.Top = CInt(Math.Round(Support.TwipsToPixelsY(Support.PixelsToTwipsY(CDbl(Screen.PrimaryScreen.Bounds.Height)) / 2.0 - Support.PixelsToTwipsY(CDbl(frmMessage.Height)) / 2.0)))
			frmMessage.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - Support.PixelsToTwipsX(CDbl(frmMessage.Width)) / 2.0)))
			i = 0
			Do
				' The following expression was wrapped in a unchecked-expression
				frmMessage.cmdBut(CShort(i)).Top = CInt(Math.Round(Support.TwipsToPixelsY(Support.PixelsToTwipsY(CDbl(frmMessage.Height)) - CDbl(num11))))
				i += 1
			Loop While i <= 5
			Select Case num
				Case 1
					frmMessage.cmdBut(CShort(array(1))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.Width)) - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(1))).Width)) / 2.0)))
				Case 2
					frmMessage.cmdBut(CShort(array(1))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.Width)) / 2.0 - CDbl(num7) / 2.0 - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(1))).Width)))))
					frmMessage.cmdBut(CShort(array(2))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(1))).Left)) + CDbl(num7) + Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(1))).Width)))))
				Case 3
					frmMessage.cmdBut(CShort(array(2))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.Width)) - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(2))).Width)) / 2.0)))
					frmMessage.cmdBut(CShort(array(1))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(2))).Left)) - CDbl(num7) - Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(1))).Width)))))
					frmMessage.cmdBut(CShort(array(3))).Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(2))).Left)) + CDbl(num7) + Support.PixelsToTwipsX(CDbl(frmMessage.cmdBut(CShort(array(3))).Width)))))
			End Select
			frmMessage.Text = Cap
			modDeclares.MsgDefault = 0
			If(CInt(flags) And 65280 And 0) <> 0 Then
				modDeclares.MsgDefault = array(1)
			ElseIf(CInt(flags) And 65280 And -1) <> 0 Then
				modDeclares.MsgDefault = array(2)
			ElseIf(CInt(flags) And 65280 And -1) <> 0 Then
				modDeclares.MsgDefault = array(3)
			Else
				modDeclares.MsgDefault = array(1)
			End If
			modDeclares.MsgReturn = 2
			MyProject.Forms.frmMessage.ShowDialog()
			Return CShort(modDeclares.MsgReturn)
		End Function

		' Token: 0x06000E3C RID: 3644 RVA: 0x00084270 File Offset: 0x00082470
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub AddFicheToSuspectOnes(ByRef FicheNumber As String)
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), MyProject.Application.Info.DirectoryPath + "\Suspect.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
			FileSystem.PrintLine(CInt(num), New Object() { FicheNumber })
			FileSystem.FileClose(New Integer() { CInt(num) })
		End Sub

		' Token: 0x06000E3D RID: 3645 RVA: 0x000842C8 File Offset: 0x000824C8
		Public Function GetText(ByRef id As String) As String
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\fileconverter.Txt"
			Dim text2 As String = modMain.GiveIni(text, "TEXTE", id)
			If modDeclares.IsSMA Then
				Dim num As Integer = Strings.InStr(text2, "file-converter", Microsoft.VisualBasic.CompareMethod.Binary)
				If num > 0 Then
					' The following expression was wrapped in a checked-expression
					text2 = Strings.Left(text2, num - 1) + "SMA 51" + Strings.Mid(text2, num + 14)
				End If
			End If
			Return text2
		End Function

		' Token: 0x06000E3E RID: 3646 RVA: 0x00084338 File Offset: 0x00082538
		Public Sub SetTexts(ByRef f As Form)
			Dim text As String = Application.StartupPath + "\fileconverter.txt"
			f.Text = modMain.GiveIni(text, f.Name, "Caption")
			Try
				For Each obj As Object In f.Controls
					Dim control As Control = CType(obj, Control)
					Dim text2 As String = modMain.GiveIni(text, f.Name, control.Name)
					If Operators.CompareString(text2, "", False) <> 0 Then
						control.Text = text2
					End If
					If control.HasChildren Then
						modMain.SetTextSubChildren(f.Name, control)
					End If
				Next
			Finally
				Dim enumerator As IEnumerator
				If TypeOf enumerator Is IDisposable Then
					TryCast(enumerator, IDisposable).Dispose()
				End If
			End Try
		End Sub

		' Token: 0x06000E3F RID: 3647 RVA: 0x000843F8 File Offset: 0x000825F8
		Public Sub SetTextSubChildren(f1 As String, ByRef c As Control)
			Dim text As String = Application.StartupPath + "\fileconverter.txt"
			Try
				For Each obj As Object In c.Controls
					Dim control As Control = CType(obj, Control)
					Dim text2 As String = modMain.GiveIni(text, f1, control.Name)
					If Operators.CompareString(text2, "", False) <> 0 Then
						control.Text = text2
					End If
					If control.HasChildren Then
						modMain.SetTextSubChildren(f1, control)
					End If
				Next
			Finally
				Dim enumerator As IEnumerator
				If TypeOf enumerator Is IDisposable Then
					TryCast(enumerator, IDisposable).Dispose()
				End If
			End Try
		End Sub

		' Token: 0x06000E40 RID: 3648 RVA: 0x0001A972 File Offset: 0x00018B72
		Public Sub GetCaptions(ByRef f As Form)
		End Sub

		' Token: 0x06000E41 RID: 3649 RVA: 0x00084494 File Offset: 0x00082694
		Public Function GetPWD(ByRef id As String) As String
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Return modMain.GiveIni(text, "SYSTEM", id)
		End Function

		' Token: 0x06000E42 RID: 3650 RVA: 0x000844CC File Offset: 0x000826CC
		Public Sub SetPWD(ByRef id As String, ByRef txt As String)
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim lpAppName As String = "SYSTEM"
			Dim lpKeyName As String = id
			Dim text As String = Support.Format(txt, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			Dim flag As Boolean = -(modDeclares.WritePrivateProfileString(lpAppName, lpKeyName, modMain.Encrypt(text), lpFileName) > False)
		End Sub

		' Token: 0x06000E43 RID: 3651 RVA: 0x0008451C File Offset: 0x0008271C
		Public Function Decrypt(ByRef CryptedString As String) As String
			VBMath.Rnd(-1F)
			VBMath.Randomize(CDbl(0.5F))
			Dim text As String = ""
			Dim num As Short = CShort(Strings.Len(CryptedString))
			For num2 As Short = 1S To num
				' The following expression was wrapped in a checked-statement
				Dim num3 As Short = CShort(Strings.Asc(Strings.Mid(CryptedString, CInt(num2), 1)))
				num3 = CShort(Math.Round(CDbl((CSng(num3) - Conversion.Int(VBMath.Rnd() * 10F)))))
				If num3 < 65S Then
					num3 += 26S
				End If
				text += Conversions.ToString(Strings.Chr(CInt(num3)))
			Next
			Return text
		End Function

		' Token: 0x06000E44 RID: 3652 RVA: 0x000845A4 File Offset: 0x000827A4
		Public Function Encrypt(ByRef StringToCrypt As String) As String
			Dim num As Double = CDbl(0.5F)
			VBMath.Rnd(-1F)
			VBMath.Randomize(num)
			Dim text As String = ""
			Dim num2 As Short = CShort(Strings.Len(StringToCrypt))
			For num3 As Short = 1S To num2
				' The following expression was wrapped in a checked-statement
				Dim num4 As Short = CShort(Strings.Asc(Strings.Mid(StringToCrypt, CInt(num3), 1)))
				num4 = CShort(Math.Round(CDbl((CSng(num4) + Conversion.Int(VBMath.Rnd() * 10F)))))
				text += Conversions.ToString(Strings.Chr(CInt(num4)))
			Next
			Return text
		End Function

		' Token: 0x06000E45 RID: 3653 RVA: 0x00084624 File Offset: 0x00082824
		Public Function IG_device_rect_set(ByRef hIGear As Integer, ByRef lpRect As modDeclares.RECT) As Object
			Return modDeclares.IG_dspl_layout_set(hIGear, 0, 2, lpRect, lpRect, lpRect, 0, 0, 0, 0.0)
		End Function

		' Token: 0x06000E46 RID: 3654 RVA: 0x00084650 File Offset: 0x00082850
		Public Function IG_display_alias_set(hIGear As Integer, nAliasType As Integer, nThreshold As Integer, bSubSample As Integer) As Object
			New FixedLengthString(256)
			Dim num As Integer = If(nAliasType, 0)
			If nAliasType = 1 Then
				num = 2
			End If
			If nAliasType = 2 Then
				num = 1
			End If
			num += 256
			num = 1
			nThreshold = CInt(modDeclares.ALIAS_WERT)
			Return modDeclares.IG_dspl_antialias_set(hIGear, 0, num, 50)
		End Function

		' Token: 0x06000E47 RID: 3655 RVA: 0x000846A0 File Offset: 0x000828A0
		Public Function IG_display_image(hIGear As Integer, hwnd As Integer, hdc As Integer) As Integer
			Dim num As Integer
			Dim result As Integer
			Dim num2 As Integer
			Dim obj As Object
			Try
				ProjectData.ClearProjectError()
				num = 2
				Dim rect As modDeclares.RECT
				result = modDeclares.IG_dspl_image_drawD(hIGear, 0, hwnd, hdc, rect)
				IL_27:
				GoTo IL_6A
				IL_15:
				Interaction.MsgBox(Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_27
				IL_29:
				num2 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_3D:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num2 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_29
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_6A:
			If num2 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E48 RID: 3656 RVA: 0x00084730 File Offset: 0x00082930
		Public Function GetFileTitleFromName(ByRef path As String) As String
			Dim start As Short = 1S
			Dim num As Short
			Do
				num = CShort(Strings.InStr(CInt(start), path, "\", Microsoft.VisualBasic.CompareMethod.Binary))
				If num > 0S Then
					start = num + 1S
				End If
			Loop While num > 0S
			Return Strings.Mid(path, CInt(start))
		End Function

		' Token: 0x06000E49 RID: 3657 RVA: 0x00084768 File Offset: 0x00082968
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub LoadSystemData()
			Dim num As Integer
			Dim num16 As Integer
			Dim obj2 As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				Dim fixedLengthString As FixedLengthString = New FixedLengthString(1000)
				IL_15:
				num2 = 3
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_31:
				num2 = 4
				modDeclares.SystemData.PDFKONVERTER = modMain.GiveIni(text, "SYSTEM", "PDFKONVERTER")
				IL_4E:
				num2 = 5
				modDeclares.SystemData.PDFKONVERTERTEMP = modMain.GiveIni(text, "SYSTEM", "PDFKONVERTERTEMP")
				IL_6B:
				num2 = 6
				If Operators.CompareString(modDeclares.SystemData.PDFKONVERTER, "", False) = 0 Then
					GoTo IL_133
				End If
				IL_87:
				num2 = 7
				If modExpose.FileExists(modDeclares.SystemData.PDFKONVERTER) Then
					GoTo IL_B9
				End If
				IL_9A:
				num2 = 8
				Dim text2 As String = "The specified PDF Konverter doesn't exist!"
				Dim num3 As Short = 0S
				Dim value As String = "file-converter"
				modMain.msgbox2(text2, num3, value)
				IL_B9:
				num2 = 9
				If Operators.CompareString(modDeclares.SystemData.PDFKONVERTERTEMP, "", False) <> 0 Then
					GoTo IL_F5
				End If
				IL_D3:
				num2 = 10
				value = "Please specifiy the valid temporary folder for the PDF Konverter!"
				num3 = 0S
				text2 = "file-converter"
				modMain.msgbox2(value, num3, text2)
				GoTo IL_133
				IL_F5:
				num2 = 12
				If Not Conversions.ToBoolean(Operators.NotObject(modMain.CheckPath(modDeclares.SystemData.PDFKONVERTERTEMP))) Then
					GoTo IL_133
				End If
				IL_113:
				num2 = 13
				text2 = "The specified temporary folder for the PDF Konverter doesn't exist!"
				num3 = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num3, value)
				IL_133:
				num2 = 14
				If Operators.CompareString(modDeclares.SystemData.PDFKONVERTER, "", False) <> 0 Then
					GoTo IL_191
				End If
				IL_14D:
				num2 = 15
				modDeclares.SystemData.PDFKONVERTER = MyProject.Application.Info.DirectoryPath + "\PDFRenderer.exe"
				IL_173:
				num2 = 16
				modDeclares.SystemData.PDFKONVERTERTEMP = modMain.GiveIni(text, "SYSTEM", "Ramdrive")
				IL_191:
				num2 = 17
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "VerschlussRichtung"), "1", False) <> 0 Then
					GoTo IL_1C2
				End If
				IL_1B2:
				num2 = 18
				modDeclares.SystemData.VerschlussRichtung = 1
				GoTo IL_1D0
				IL_1C2:
				num2 = 20
				modDeclares.SystemData.VerschlussRichtung = 0
				IL_1D0:
				num2 = 21
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "EXCELPROTOCOL"), "1", False) <> 0 Then
					GoTo IL_201
				End If
				IL_1F1:
				num2 = 22
				modDeclares.SystemData.EXCELPROTOCOL = True
				GoTo IL_20F
				IL_201:
				num2 = 24
				modDeclares.SystemData.EXCELPROTOCOL = False
				IL_20F:
				num2 = 25
				modDeclares.SystemData.VacErrorFile = modMain.GiveIni(text, "SYSTEM", "VacErrorFile")
				IL_22D:
				num2 = 26
				If File.Exists(modDeclares.SystemData.VacErrorFile) Then
					GoTo IL_278
				End If
				IL_241:
				num2 = 27
				Dim text3 As String = "Vacuum Error Document [SYSTEM.VacErrorFile]=" + modDeclares.SystemData.VacErrorFile + " could not be found!"
				IL_25F:
				num2 = 28
				num3 = 0S
				value = "file-converter"
				modMain.msgbox2(text3, num3, value)
				IL_278:
				num2 = 29
				value = "SYSTEM"
				text2 = "RetryFirstLevel"
				modDeclares.SystemData.RetryFirstLevel = CShort(modDeclares.GetPrivateProfileInt(value, text2, 1, text))
				IL_2A0:
				num2 = 30
				text2 = "SYSTEM"
				value = "RetrySecondLevel"
				modDeclares.SystemData.RetrySecondLevel = modDeclares.GetPrivateProfileInt(text2, value, 1, text)
				IL_2C7:
				num2 = 31
				value = "SYSTEM"
				text2 = "VacSteps"
				modDeclares.SystemData.VacSteps = modDeclares.GetPrivateProfileInt(value, text2, 20, text)
				IL_2EF:
				num2 = 32
				text2 = "SYSTEM"
				value = "ExtendedVacuumHandling"
				modDeclares.SystemData.ExtendedVacuumHandling = (modDeclares.GetPrivateProfileInt(text2, value, 1, text) <> 0)
				IL_319:
				num2 = 33
				value = "SYSTEM"
				text2 = "AutoRollInsert"
				Dim nDefault As Integer = 0
				Dim text4 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modDeclares.SystemData.AutoRollInsert = CShort(modDeclares.GetPrivateProfileInt(value, text2, nDefault, text4))
				IL_35C:
				num2 = 34
				text4 = "SYSTEM"
				text2 = "StandardDPI"
				Dim nDefault2 As Integer = 0
				value = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modDeclares.StandardDPI = modDeclares.GetPrivateProfileInt(text4, text2, nDefault2, value)
				IL_399:
				num2 = 35
				value = "SYSTEM"
				text2 = "PRECACHEIMAGES"
				modDeclares.SystemData.PRECACHEIMAGES = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_3C3:
				num2 = 36
				If modDeclares.UseDebug Then
					GoTo IL_40D
				End If
				IL_3CD:
				num2 = 37
				text2 = "SYSTEM"
				value = "SIMULATION"
				Dim nDefault3 As Integer = 0
				text4 = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modDeclares.UseDebug = (modDeclares.GetPrivateProfileInt(text2, value, nDefault3, text4) = 1)
				IL_40D:
				num2 = 38
				text4 = "SYSTEM"
				value = "TRINAMIC"
				Dim nDefault4 As Integer = 0
				text2 = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modDeclares.SystemData.Trinamic = (modDeclares.GetPrivateProfileInt(text4, value, nDefault4, text2) = 1)
				IL_452:
				num2 = 39
				text2 = "SYSTEM"
				value = "SmallShutter"
				modDeclares.SystemData.SmallShutter = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_47C:
				num2 = 40
				value = "SYSTEM"
				text2 = "SmallShutterFirstDir"
				modDeclares.SystemData.SmallShutterFirstDir = CShort(modDeclares.GetPrivateProfileInt(value, text2, 0, text))
				IL_4A4:
				num2 = 41
				text2 = "SYSTEM"
				value = "USEDEBENU"
				modDeclares.SystemData.UseDebenu = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_4CE:
				num2 = 42
				value = "SYSTEM"
				text2 = "USEPDF2IMG"
				modDeclares.SystemData.UsePdf2Img = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_4F8:
				num2 = 43
				modDeclares.SystemData.PDF2IMGTEMPFOLDER = modMain.GiveIni(text, "SYSTEM", "PDF2IMGTEMPFOLDER")
				IL_516:
				num2 = 44
				modDeclares.SystemData.DebenuLic = modMain.GiveIni(text, "SYSTEM", "DEBENULIC")
				IL_534:
				num2 = 45
				modDeclares.SystemData.MonitorThreshold = CShort(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "MonitorThreshold"))))
				IL_567:
				num2 = 46
				If modDeclares.SystemData.MonitorThreshold <> 0S Then
					GoTo IL_585
				End If
				IL_576:
				num2 = 47
				modDeclares.SystemData.MonitorThreshold = 64S
				IL_585:
				num2 = 48
				Dim text5 As String = modMain.GiveIni(text, "SYSTEM", "NANOFACTOR")
				IL_59B:
				num2 = 49
				If Not Versioned.IsNumeric(text5) Then
					GoTo IL_5BB
				End If
				IL_5A7:
				num2 = 50
				modDeclares.SystemData.NanoFactor = Conversions.ToDouble(text5)
				IL_5BB:
				num2 = 51
				text2 = "SYSTEM"
				value = "SCHRITTEVOLL"
				modDeclares.SystemData.SchritteVolleUmdrehung = modDeclares.GetPrivateProfileInt(text2, value, 1600, text)
				IL_5E6:
				num2 = 52
				value = "SYSTEM"
				text2 = "PRECACHEIMAGESSTAGEII"
				modDeclares.SystemData.PRECACHEIMAGESSTAGEII = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_610:
				num2 = 53
				text2 = "SYSTEM"
				value = "SMCI"
				modDeclares.SystemData.SMCI = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_63A:
				num2 = 54
				value = "SYSTEM"
				text2 = "ISSMA"
				modDeclares.IsSMA = (modDeclares.GetPrivateProfileInt(value, text2, 1, text) <> 0)
				IL_65F:
				num2 = 55
				text2 = "SYSTEM"
				value = "IsSI"
				modDeclares.IsSI = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_684:
				num2 = 56
				value = "SYSTEM"
				text2 = "ISSMA"
				modDeclares.IsSMA = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_6A9:
				num2 = 57
				text2 = "SYSTEM"
				value = "ISSMA"
				modDeclares.SMAVersion = CShort(modDeclares.GetPrivateProfileInt(text2, value, 0, text))
				IL_6CC:
				num2 = 58
				value = "SYSTEM"
				text2 = "ACCUV16"
				modDeclares.SystemData.UseAccuv16 = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_6F6:
				num2 = 59
				text2 = "SYSTEM"
				value = "MagnetValue"
				modDeclares.MagnetValue = modDeclares.GetPrivateProfileInt(text2, value, 32, text)
				IL_719:
				num2 = 60
				value = "SYSTEM"
				text2 = "BAYHSTA"
				modDeclares.SystemData.BayHStA = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_743:
				num2 = 61
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "USERISADMIN"), "1", False) <> 0 Then
					GoTo IL_76E
				End If
				IL_764:
				num2 = 62
				modDeclares.UserLevel = 10S
				IL_76E:
				num2 = 63
				text2 = "DISPLAY"
				Dim fixedLengthString2 As FixedLengthString = fixedLengthString
				Dim fixedLengthString3 As FixedLengthString = fixedLengthString2
				value = fixedLengthString2.Value
				Dim privateProfileSection As Integer = modDeclares.GetPrivateProfileSection(text2, value, 1000, text)
				fixedLengthString3.Value = value
				Dim num4 As Integer = privateProfileSection
				IL_79F:
				num2 = 64
				If num4 = 0 Then
					GoTo IL_7B6
				End If
				IL_7A6:
				num2 = 65
				modDeclares.SystemData.USEDISPLAYSECTION = True
				GoTo IL_7C4
				IL_7B6:
				num2 = 67
				modDeclares.SystemData.USEDISPLAYSECTION = False
				IL_7C4:
				num2 = 68
				Dim text6 As String = modMain.GiveIni(text, "SYSTEM", "BackColor")
				IL_7DA:
				num2 = 69
				If Operators.CompareString(text6, "", False) <> 0 Then
					GoTo IL_7F6
				End If
				IL_7EC:
				num2 = 70
				text6 = "0"
				IL_7F6:
				num2 = 71
				modDeclares.SystemData.BACKCOLOR = Conversions.ToInteger("&H" + text6)
				IL_814:
				num2 = 72
				If Not modDeclares.SystemData.USEDISPLAYSECTION Then
					GoTo IL_B1C
				End If
				IL_826:
				num2 = 73
				Dim text7 As String = modMain.GiveIni(text, "DISPLAY", "DEFAULT").ToUpper()
				IL_841:
				num2 = 74
				If Operators.CompareString(text7, "", False) <> 0 Then
					GoTo IL_85D
				End If
				IL_853:
				num2 = 75
				text7 = "P"
				IL_85D:
				num2 = 76
				modDeclares.SystemData.DISPLAY_DEFAULT = text7
				IL_86C:
				num2 = 77
				modDeclares.SystemData.DISPLAY_BPP1 = text7
				IL_87B:
				num2 = 78
				modDeclares.SystemData.DISPLAY_BPP24 = text7
				IL_88A:
				num2 = 79
				modDeclares.SystemData.DISPLAY_BPP8 = text7
				IL_899:
				num2 = 80
				modDeclares.SystemData.DISPLAY_PDF = text7
				IL_8A8:
				num2 = 81
				text5 = modMain.GiveIni(text, "DISPLAY", "BPP1")
				IL_8BE:
				num2 = 82
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_945
				End If
				IL_8D0:
				num2 = 83
				If Not(Operators.CompareString(Strings.Left(text5, 1), "P", False) = 0 Or Operators.CompareString(Strings.Left(text5, 1), "A", False) = 0) Then
					GoTo IL_919
				End If
				IL_902:
				num2 = 84
				modDeclares.SystemData.DISPLAY_BPP1 = Strings.Left(text5, 1)
				GoTo IL_945
				IL_919:
				num2 = 86
				value = "Wrong Key (" + text5 + ") in [DISPLAY] Section for Entry BPP2"
				num3 = 0S
				text2 = "file-converter"
				modMain.msgbox2(value, num3, text2)
				IL_945:
				num2 = 87
				text5 = modMain.GiveIni(text, "DISPLAY", "BPP8")
				IL_95B:
				num2 = 88
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_9E2
				End If
				IL_96D:
				num2 = 89
				If Not(Operators.CompareString(Strings.Left(text5, 1), "P", False) = 0 Or Operators.CompareString(Strings.Left(text5, 1), "A", False) = 0) Then
					GoTo IL_9B6
				End If
				IL_99F:
				num2 = 90
				modDeclares.SystemData.DISPLAY_BPP8 = Strings.Left(text5, 1)
				GoTo IL_9E2
				IL_9B6:
				num2 = 92
				text2 = "Wrong Key (" + text5 + ") in [DISPLAY] Section for Entry BPP8"
				num3 = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num3, value)
				IL_9E2:
				num2 = 93
				text5 = modMain.GiveIni(text, "DISPLAY", "BPP24")
				IL_9F8:
				num2 = 94
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_A7F
				End If
				IL_A0A:
				num2 = 95
				If Not(Operators.CompareString(Strings.Left(text5, 1), "P", False) = 0 Or Operators.CompareString(Strings.Left(text5, 1), "A", False) = 0) Then
					GoTo IL_A53
				End If
				IL_A3C:
				num2 = 96
				modDeclares.SystemData.DISPLAY_BPP24 = Strings.Left(text5, 1)
				GoTo IL_A7F
				IL_A53:
				num2 = 98
				value = "Wrong Key (" + text5 + ") in [DISPLAY] Section for Entry BPP24"
				num3 = 0S
				text2 = "file-converter"
				modMain.msgbox2(value, num3, text2)
				IL_A7F:
				num2 = 99
				text5 = modMain.GiveIni(text, "DISPLAY", "PDF")
				IL_A95:
				num2 = 100
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_B1C
				End If
				IL_AA7:
				num2 = 101
				If Not(Operators.CompareString(Strings.Left(text5, 1), "P", False) = 0 Or Operators.CompareString(Strings.Left(text5, 1), "A", False) = 0) Then
					GoTo IL_AF0
				End If
				IL_AD9:
				num2 = 102
				modDeclares.SystemData.DISPLAY_PDF = Strings.Left(text5, 1)
				GoTo IL_B1C
				IL_AF0:
				num2 = 104
				text2 = "Wrong Key (" + text5 + ") in [DISPLAY] Section for Entry PDF"
				num3 = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num3, value)
				IL_B1C:
				num2 = 105
				value = "SYSTEM"
				text2 = "TESTMODE"
				modDeclares.TESTMODE = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_B41:
				num2 = 106
				Dim ptr As modDeclares.typSystem = modDeclares.SystemData
				IL_B4B:
				num2 = 107
				Dim ptr2 As modDeclares.typSystem = ptr
				text2 = "SYSTEM"
				value = "NeuerMagnet"
				ptr2.NeuerMagnet = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_B72:
				num2 = 108
				Dim ptr3 As modDeclares.typSystem = ptr
				value = "SYSTEM"
				text2 = "MagnetDelay"
				ptr3.MagnetDelay = modDeclares.GetPrivateProfileInt(value, text2, 50, text)
				IL_B97:
				num2 = 109
				Dim ptr4 As modDeclares.typSystem = ptr
				text2 = "SYSTEM"
				value = "EnableRollFrameExt"
				ptr4.EnableRollFrameExt = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_BBE:
				num2 = 110
				Dim ptr5 As modDeclares.typSystem = ptr
				value = "RollFrameExt"
				text2 = "Orientation"
				ptr5.RollFrameExtOrientation = modDeclares.GetPrivateProfileInt(value, text2, 0, text)
				IL_BE2:
				num2 = 111
				Dim ptr6 As modDeclares.typSystem = ptr
				text2 = "RollFrameExt"
				value = "LinePos1"
				ptr6.RollFrameExtLinePos1 = modDeclares.GetPrivateProfileInt(text2, value, 0, text)
				IL_C06:
				num2 = 112
				Dim ptr7 As modDeclares.typSystem = ptr
				value = "RollFrameExt"
				text2 = "LinePos2"
				ptr7.RollFrameExtLinePos2 = modDeclares.GetPrivateProfileInt(value, text2, 0, text)
				IL_C2A:
				num2 = 113
				Dim ptr8 As modDeclares.typSystem = ptr
				text2 = "RollFrameExt"
				value = "LinePos3"
				ptr8.RollFrameExtLinePos3 = modDeclares.GetPrivateProfileInt(text2, value, 0, text)
				IL_C4E:
				num2 = 114
				Dim ptr9 As modDeclares.typSystem = ptr
				value = "RollFrameExtFontSize"
				text2 = "FontSize"
				ptr9.RollFrameExtFontSize = modDeclares.GetPrivateProfileInt(value, text2, 100, text)
				IL_C73:
				num2 = 115
				Dim ptr10 As modDeclares.typSystem = ptr
				text2 = "SYSTEM"
				value = "EnableInfoWindow"
				ptr10.EnableInfoWindow = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_C9A:
				num2 = 116
				Dim ptr11 As modDeclares.typSystem = ptr
				value = "SYSTEM"
				text2 = "Verschlussmotorgradzahl"
				ptr11.Verschlussmotorgradzahl = CDbl(modDeclares.GetPrivateProfileInt(value, text2, 18, text))
				IL_CC0:
				num2 = 117
				ptr.HybridMode = False
				IL_CCB:
				num2 = 118
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "HybridMode"), "1", False) <> 0 Then
					GoTo IL_CF7
				End If
				IL_CEC:
				num2 = 119
				ptr.HybridMode = True
				IL_CF7:
				num2 = 120
				modDeclares.ShowLib = False
				IL_D00:
				num2 = 121
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "ShowLib"), "1", False) <> 0 Then
					GoTo IL_D2A
				End If
				IL_D21:
				num2 = 122
				modDeclares.ShowLib = True
				IL_D2A:
				num2 = 123
				ptr.FastColorExposure = False
				IL_D35:
				num2 = 124
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "FastColorExposure"), "1", False) <> 0 Then
					GoTo IL_D61
				End If
				IL_D56:
				num2 = 125
				ptr.FastColorExposure = True
				IL_D61:
				num2 = 126
				ptr.VacuumOn = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "VacuumWait"))
				IL_D8B:
				num2 = 127
				ptr.VacuumOff = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "VacuumOff"))
				IL_DB5:
				num2 = 128
				ptr.AfterVacuumOff = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "AfterVacuumOff"))
				IL_DE2:
				num2 = 129
				ptr.AfterVacuumOn = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "AfterVacuumOn"))
				IL_E0F:
				num2 = 130
				ptr.VacuumOnDelay = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "VacuumOnDelay"))
				IL_E3C:
				num2 = 131
				Dim ptr12 As modDeclares.typSystem = ptr
				text2 = modMain.GiveIni(text, "SYSTEM", "VORSPANN")
				ptr12.vorspann = CInt(Math.Round(Conversion.Val(modMain.KommazuPunkt(text2))))
				IL_E6E:
				num2 = 132
				Dim ptr13 As modDeclares.typSystem = ptr
				text2 = modMain.GiveIni(text, "SYSTEM", "NACHSPANN")
				ptr13.nachspann = CInt(Math.Round(Conversion.Val(modMain.KommazuPunkt(text2))))
				IL_EA0:
				num2 = 133
				ptr.nullpunkt = Conversions.ToInteger(modMain.GiveIni(text, "SYSTEM", "NULLPUNKT"))
				IL_EC3:
				num2 = 134
				ptr.umdrehung = Conversions.ToInteger(modMain.GiveIni(text, "SYSTEM", "UMDREHUNG"))
				IL_EE6:
				num2 = 135
				ptr.schlitze = Conversions.ToInteger(modMain.GiveIni(text, "SYSTEM", "SCHLITZE"))
				IL_F09:
				num2 = 136
				ptr.WaitAfterDraw = Conversions.ToInteger("0" + modMain.GiveIni(text, "SYSTEM", "WAITAFTERDRAW"))
				IL_F36:
				num2 = 137
				Dim num5 As Short = 0S
				Do
					IL_F3F:
					num2 = 138
					ptr.kopfname(CInt(num5)) = modMain.GiveIni(text, "SYSTEM", "Kopfname" + Conversions.ToString(CInt(num5)))
					IL_F6C:
					num2 = 139
					Dim filmlaenge As Integer() = ptr.filmlaenge
					Dim num6 As Integer = CInt(num5)
					text2 = modMain.GiveIni(text, "SYSTEM", "Filmlaenge" + Conversions.ToString(CInt(num5)))
					filmlaenge(num6) = CInt(Math.Round(Conversion.Val(modMain.KommazuPunkt(text2))))
					IL_FAD:
					num2 = 140
					ptr.portrait(CInt(num5)) = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "Portrait" + Conversions.ToString(CInt(num5))), "1", False) = 0, True, False))
					IL_FFE:
					num2 = 141
					Dim monitorHeightOnFilm As Double() = ptr.MonitorHeightOnFilm
					Dim num7 As Integer = CInt(num5)
					text2 = modMain.GiveIni(text, "SYSTEM", "MonitorHeightOnFilm" + Conversions.ToString(CInt(num5)))
					monitorHeightOnFilm(num7) = Conversion.Val(modMain.KommazuPunkt(text2))
					IL_1039:
					num2 = 142
					ptr.filmspeed(CInt(num5)) = Conversions.ToInteger(modMain.GiveIni(text, "SYSTEM", "FILMSPEED" + Conversions.ToString(CInt(num5))))
					IL_106B:
					num2 = 143
					Dim schrittepromm As Double() = ptr.schrittepromm
					Dim num8 As Integer = CInt(num5)
					text2 = modMain.GiveIni(text, "SYSTEM", "SCHRITTEPROMM" + Conversions.ToString(CInt(num5)))
					schrittepromm(num8) = Conversion.Val(modMain.KommazuPunkt(text2))
					IL_10A6:
					num2 = 144
					Dim schrittepropixel As Double() = ptr.schrittepropixel
					Dim num9 As Integer = CInt(num5)
					text2 = modMain.GiveIni(text, "SYSTEM", "SCHRITTEPROPIXEL" + Conversions.ToString(CInt(num5)))
					schrittepropixel(num9) = Conversion.Val(modMain.KommazuPunkt(text2))
					IL_10E1:
					num2 = 145
					Dim fresolution As Short() = ptr.FResolution
					Dim num10 As Integer = CInt(num5)
					text2 = "SYSTEM"
					value = "FILM_AUFLOESUNG" + Conversions.ToString(CInt(num5))
					fresolution(num10) = CShort(modDeclares.GetPrivateProfileInt(text2, value, 8, text))
					IL_1118:
					num2 = 146
					Dim belegeProFilm As Integer() = ptr.BelegeProFilm
					Dim num11 As Integer = CInt(num5)
					value = "SYSTEM"
					text2 = "BELEGEPROFILM" + Conversions.ToString(CInt(num5))
					belegeProFilm(num11) = modDeclares.GetPrivateProfileInt(value, text2, 0, text)
					IL_114E:
					num2 = 147
					Dim belegeVerfuegbar As Integer() = ptr.BelegeVerfuegbar
					Dim num12 As Integer = CInt(num5)
					text2 = "SYSTEM"
					value = "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num5))
					belegeVerfuegbar(num12) = modDeclares.GetPrivateProfileInt(text2, value, 0, text)
					IL_1184:
					num2 = 148

						num5 += 1S

				Loop While num5 <= 3S
				IL_1199:
				num2 = 149
				ptr.CheckVakuum = True
				IL_11A7:
				num2 = 150
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "CheckVakuum"), "", False) = 0 Then
					GoTo IL_120D
				End If
				IL_11CB:
				num2 = 151
				ptr.CheckVakuum = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "CheckVakuum"), "1", False) = 0, True, False))
				IL_120D:
				num2 = 152
				ptr.CheckIfImageOnScreen = False
				IL_121B:
				num2 = 153
				ptr.CheckIfImageOnScreen = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "CheckIfImageOnScreen"), "1", False) = 0, True, False))
				IL_125D:
				num2 = 154
				ptr.CheckIfImageOnScreenThreshold = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "CheckIfImageOnScreenThreshold"))))
				IL_1290:
				num2 = 155
				ptr.CheckFilmEnde = True
				IL_129E:
				num2 = 156
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "CheckFilmEnde"), "", False) = 0 Then
					GoTo IL_1304
				End If
				IL_12C2:
				num2 = 157
				ptr.CheckFilmEnde = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "CheckFilmEnde"), "1", False) = 0, True, False))
				IL_1304:
				num2 = 158
				Dim ptr14 As modDeclares.typSystem = ptr
				value = "SYSTEM"
				text2 = "VERSCHLUSS_AUFLOESUNG"
				ptr14.VResolution = CShort(modDeclares.GetPrivateProfileInt(value, text2, 8, text))
				IL_132C:
				num2 = 159
				Dim ptr15 As modDeclares.typSystem = ptr
				text2 = "SYSTEM"
				value = "NOHEAD"
				ptr15.NoHead = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_1356:
				num2 = 160
				Dim ptr16 As modDeclares.typSystem = ptr
				value = "SYSTEM"
				text2 = "USEUNICODE"
				ptr16.UseUnicode = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_1380:
				num2 = 161
				Dim ptr17 As modDeclares.typSystem = ptr
				text2 = "SYSTEM"
				value = "MotorProt"
				ptr17.MotorProt = (modDeclares.GetPrivateProfileInt(text2, value, 0, text) <> 0)
				IL_13AA:
				num2 = 162
				Dim ptr18 As modDeclares.typSystem = ptr
				value = "SYSTEM"
				text2 = "AmericanSizes"
				ptr18.UseAmericanSizes = (modDeclares.GetPrivateProfileInt(value, text2, 0, text) <> 0)
				IL_13D4:
				num2 = 163
				If Not ptr.UseAmericanSizes Then
					GoTo IL_172E
				End If
				IL_13E6:
				ProjectData.ClearProjectError()
				num = 2
				IL_13ED:
				num2 = 165
				Dim num13 As Short = CShort(FileSystem.FreeFile())
				IL_13FB:
				num2 = 166
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\Drawing Sizes.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
					GoTo IL_147A
				End If
				IL_142D:
				num2 = 167
				text2 = MyProject.Application.Info.DirectoryPath + "\Drawing Sizes.txt not found!" & vbCr & "The flag AmericanSizes=1 will be ignored!"
				num3 = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num3, value)
				IL_1464:
				num2 = 168
				modDeclares.SystemData.UseAmericanSizes = False
				GoTo IL_172E
				IL_147A:
				num2 = 170
				FileSystem.FileOpen(CInt(num13), MyProject.Application.Info.DirectoryPath + "\Drawing Sizes.txt", OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
				IL_14A4:
				num2 = 171
				text6 = FileSystem.LineInput(CInt(num13))
				IL_14B3:
				num2 = 172
				num5 = 1S
				Do
					IL_14BC:
					num2 = 173
					text6 = FileSystem.LineInput(CInt(num13))
					IL_14CB:
					num2 = 174
					Dim obj As Object = 1
					IL_14D9:
					num2 = 175
					Dim num14 As Short = CShort(Strings.InStr(Conversions.ToInteger(Operators.AddObject(obj, 1)), text6, ";", Microsoft.VisualBasic.CompareMethod.Binary))
					IL_1501:
					num2 = 176
					ptr.ASizes(CInt(num5)).Desc = Strings.Mid(text6, Conversions.ToInteger(obj), Conversions.ToInteger(Operators.SubtractObject(num14, obj)))
					IL_153B:
					num2 = 177
					obj = CInt((num14 + 1S))
					IL_154C:
					num2 = 178
					num14 = CShort(Strings.InStr(Conversions.ToInteger(Operators.AddObject(obj, 1)), text6, ";", Microsoft.VisualBasic.CompareMethod.Binary))
					IL_1574:
					num2 = 179
					ptr.ASizes(CInt(num5)).min = Conversion.Val(Strings.Mid(text6, Conversions.ToInteger(obj), Conversions.ToInteger(Operators.SubtractObject(num14, obj))))
					IL_15B3:
					num2 = 180
					obj = CInt((num14 + 1S))
					IL_15C4:
					num2 = 181
					num14 = CShort(Strings.InStr(Conversions.ToInteger(Operators.AddObject(obj, 1)), text6, ";", Microsoft.VisualBasic.CompareMethod.Binary))
					IL_15EC:
					num2 = 182
					ptr.ASizes(CInt(num5)).max = Conversion.Val(Strings.Mid(text6, Conversions.ToInteger(obj), Conversions.ToInteger(Operators.SubtractObject(num14, obj))))
					IL_162B:
					num2 = 183
					obj = CInt((num14 + 1S))
					IL_163C:
					num2 = 184
					num14 = CShort(Strings.InStr(Conversions.ToInteger(Operators.AddObject(obj, 1)), text6, ";", Microsoft.VisualBasic.CompareMethod.Binary))
					IL_1664:
					num2 = 185
					ptr.ASizes(CInt(num5)).MonitorX = Conversions.ToDouble(Strings.Mid(text6, Conversions.ToInteger(obj), Conversions.ToInteger(Operators.SubtractObject(num14, obj))))
					IL_16A3:
					num2 = 186
					obj = CInt((num14 + 1S))
					IL_16B4:
					num2 = 187
					ptr.ASizes(CInt(num5)).MonitorY = Conversions.ToDouble(Strings.Mid(text6, Conversions.ToInteger(obj), Conversions.ToInteger(Operators.AddObject(Operators.SubtractObject(Strings.Len(text6), obj), 1))))
					IL_1703:
					num2 = 188

						num5 += 1S

				Loop While num5 <= 5S
				IL_1718:
				num2 = 189
				FileSystem.FileClose(New Integer() { CInt(num13) })
				IL_172E:
				num2 = 190
				ptr.ShowWindowBorder = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "ShowWindowBorder"), "1", False) = 0, True, False))
				IL_178A:
				GoTo IL_1AE8
				IL_1772:
				num2 = 193
				Interaction.MsgBox(Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_178A
				IL_178F:
				Dim num15 As Integer = num16 + 1
				num16 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num15)
				IL_1AA5:
				GoTo IL_1ADD
				IL_1AA7:
				num16 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_1ABB:
			Catch obj3 When endfilter(TypeOf obj2 Is Exception And num <> 0 And num16 = 0)
				Dim ex As Exception = CType(obj3, Exception)
				GoTo IL_1AA7
			End Try
			IL_1ADD:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_1AE8:
			If num16 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000E4A RID: 3658 RVA: 0x00086284 File Offset: 0x00084484
		Public Function FH_IG_load_file(ByRef fname As String, ByRef handle As Integer, ByRef page As Integer) As Integer
			New FixedLengthString(256)
			Dim fd As Integer = modDeclares.lopen(fname, 0)
			Dim num As Integer = modDeclares.IG_load_FDD(fd, 0, page, 1, handle)
			If num <> 0 Then
				Dim flag As Boolean = num <> 0
			End If
			modDeclares.lclose(fd)
			Return num
		End Function

		' Token: 0x06000E4B RID: 3659 RVA: 0x000862C4 File Offset: 0x000844C4
		Public Function FH_IG_info_get(ByRef fname As String, ByRef lpFileType As Integer, ByRef lpCompression As Integer, ByRef lpdib As modDeclares.AT_DIB, ByRef page As Integer) As Integer
			Dim fixedLengthString As FixedLengthString = New FixedLengthString(256)
			Dim fd As Integer = modDeclares.lopen(fname, 0)
			Dim num As Integer = modDeclares.IG_info_get_FDD(fd, 0, page, lpFileType, lpCompression, lpdib)
			modDeclares.IG_error_checkD()
			Dim errorIndex As Integer = 0
			Dim value As String = fixedLengthString.Value
			Dim sizeOfFileName As Integer = 256
			Dim num2 As Integer = 0
			Dim num3 As Integer = 0
			Dim num4 As Integer
			Dim num5 As Integer
			modDeclares.IG_error_getD(errorIndex, value, sizeOfFileName, num4, num5, num2, num3)
			Dim flag As Boolean = num <> 0
			modDeclares.lclose(fd)
			Return num
		End Function

		' Token: 0x06000E4C RID: 3660 RVA: 0x00086324 File Offset: 0x00084524
		Public Function CheckPath(ByRef path As String) As Object
			Dim instance As Object = New FileSystemObjectClass()
			Dim type As Type = Nothing
			Dim memberName As String = "FolderExists"
			Dim array As Object() = New Object() { path }
			Dim array2 As Object() = array
			Dim argumentNames As String() = Nothing
			Dim typeArguments As Type() = Nothing
			Dim array3 As Boolean() = New Boolean() { True }
			Dim array4 As Boolean() = array3
			Dim value As Object = NewLateBinding.LateGet(instance, type, memberName, array, argumentNames, typeArguments, array3)
			If array4(0) Then
				path = CStr(Conversions.ChangeType(RuntimeHelpers.GetObjectValue(array2(0)), GetType(String)))
			End If
			Dim result As Object
			If Conversions.ToBoolean(value) Then
				result = True
			Else
				result = False
			End If
			Return result
		End Function

		' Token: 0x06000E4D RID: 3661 RVA: 0x00086398 File Offset: 0x00084598
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function GetImageInfos(ByRef pos As Short, ByRef path As String, ByRef od As Integer, ByRef FolderCount As Integer, ByRef Folders As String(), isDuplex As Boolean) As Boolean
			Dim num2 As Integer
			Dim result As Boolean
			Dim num61 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim fileSystemObject As FileSystemObject = New FileSystemObjectClass()
				IL_09:
				ProjectData.ClearProjectError()
				num2 = 1
				IL_10:
				num = 3
				If Not File.Exists(MyProject.Application.Info.DirectoryPath + "\ERRORLIST.TXT") Then
					GoTo IL_52
				End If
				IL_32:
				num = 4
				FileSystem.Kill(MyProject.Application.Info.DirectoryPath + "\ERRORLIST.TXT")
				IL_52:
				ProjectData.ClearProjectError()
				num2 = 2
				IL_59:
				num = 6
				result = True
				IL_5D:
				num = 7
				Dim frmImageXpress As frmImageXpress = New frmImageXpress()
				IL_66:
				num = 8
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_83:
				num = 9
				Dim text2 As String = "SYSTEM"
				Dim text3 As String = "DoDirSort"
				modDeclares.SystemData.DoDirSort = Conversions.ToBoolean(Interaction.IIf(modDeclares.GetPrivateProfileInt(text2, text3, 0, text) = 0, False, True))
				IL_C3:
				num = 10
				result = True
				IL_C8:
				num = 11
				text3 = "TXT_COULD_NOT_READ"
				Dim text4 As String = modMain.GetText(text3)
				IL_DB:
				num = 12
				If Operators.CompareString(text4, "", False) <> 0 Then
					GoTo IL_F7
				End If
				IL_ED:
				num = 13
				text4 = "Folgendes Verzeichnis konnte nicht gelesen werden:"
				IL_F7:
				num = 14
				If Not Conversions.ToBoolean(Operators.NotObject(modMain.CheckPath(path))) Then
					GoTo IL_13F
				End If
				IL_10C:
				num = 15
				result = False
				IL_111:
				num = 16
				text3 = text4 + vbCr + path
				Dim num3 As Short = 0S
				text2 = "file-converter"
				modMain.msgbox2(text3, num3, text2)
				GoTo IL_2FF6
				IL_13F:
				num = 18
				text2 = "TXT_ANALYZING"
				text4 = modMain.GetText(text2)
				IL_152:
				num = 19
				If Operators.CompareString(text4, "", False) <> 0 Then
					GoTo IL_16E
				End If
				IL_164:
				num = 20
				text4 = "Datenträger wird analysiert"
				IL_16E:
				num = 21
				text4 = "Datenträger wird analysiert (Level 1 Scan)"
				IL_178:
				num = 22
				Dim num4 As Long = 0L
				IL_17F:
				num = 23
				MyProject.Forms.frmCheckImages.Show()
				IL_191:
				num = 24
				MyProject.Forms.frmCheckImages.lblInfo.Text = text4
				IL_1AA:
				num = 25
				Application.DoEvents()
				IL_1B2:
				num = 26
				If FolderCount <> 0 Then
					GoTo IL_377
				End If
				IL_1BC:
				num = 27
				If modDeclares.SystemData.UseUnicode Then
					GoTo IL_28F
				End If
				IL_1CE:
				num = 28
				Dim text5 As String = FileSystem.Dir(path + "\*.*", Microsoft.VisualBasic.FileAttribute.Directory)
				Dim array As String()
				Dim win32_FIND_DATA As modDeclares.WIN32_FIND_DATA
				Dim num7 As Integer
				Dim array2 As String()
				Dim num11 As Short
				Dim array3 As Integer()
				Dim array4 As String(,)
				Dim array5 As String()
				Dim hObject As Integer
				Dim hObject2 As Integer
				Dim num26 As Short
				Dim num27 As Long
				While True
					IL_275:
					num = 30
					If Operators.CompareString(text5, "", False) = 0 Then
						Exit For
					End If
					IL_1EB:
					num = 31
					If(If(-If(((Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0) > False), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal) And (FileSystem.GetAttr(path + "\" + text5) And Microsoft.VisualBasic.FileAttribute.Directory)) > Microsoft.VisualBasic.FileAttribute.Normal Then
						IL_22F:
						num = 32
						array = CType(Utils.CopyArray(array, New String(CInt(num4) + 1 - 1) {}), String())
						IL_24A:
						num = 33
						array(CInt(num4)) = path + "\" + text5
						IL_261:
						num = 34
						num4 += 1L
					End If
					IL_26B:
					num = 35
					text5 = FileSystem.Dir()
				End While
				GoTo IL_3CE
				IL_28F:
				num = 38
				text5 = path + "\*.*"
				IL_2A0:
				num = 39
				modDeclares.handle = modDeclares.FindFirstFile(text5, win32_FIND_DATA)
				Dim num5 As Integer
				Do
					IL_2B1:
					num = 41
					If(CULng(win32_FIND_DATA.dwFileAttributes) And 16UL) = 16UL Then
						IL_2C8:
						num = 42
						If Operators.CompareString(modMain.trunc(win32_FIND_DATA.cFileName), ".", False) <> 0 And Operators.CompareString(modMain.trunc(win32_FIND_DATA.cFileName), "..", False) <> 0 Then
							IL_302:
							num = 43
							array = CType(Utils.CopyArray(array, New String(CInt(num4) + 1 - 1) {}), String())
							IL_31D:
							num = 44
							array(CInt(num4)) = path + "\" + modMain.trunc(win32_FIND_DATA.cFileName)
							IL_33E:
							num = 45
							num4 += 1L
						End If
					End If
					IL_348:
					num = 46
					num5 = CInt(modDeclares.FindNextFile(modDeclares.handle, win32_FIND_DATA))
					IL_35A:
					num = 47
				Loop While num5 <> 0
				IL_367:
				num = 48
				modDeclares.FindClose(modDeclares.handle)
				GoTo IL_3CE
				IL_377:
				num = 50
				array = CType(Utils.CopyArray(array, New String(FolderCount - 1 + 1 - 1) {}), String())
				IL_393:
				num = 51
				Dim num6 As Long = CLng((FolderCount - 1))
				num4 = 0L
				While num4 <= num6
					IL_3A3:
					num = 52
					array(CInt(num4)) = Folders(CInt((num4 + 1L)))
					IL_3B6:
					num = 53
					num4 += 1L
				End While
				IL_3C6:
				num = 54
				num4 = CLng(FolderCount)
				IL_3CE:
				num = 55
				text4 = "Datenträger wird analysiert (Sortierung)"
				IL_3D8:
				num = 56
				MyProject.Forms.frmCheckImages.lblInfo.Text = text4
				IL_3F1:
				num = 57
				Application.DoEvents()
				IL_3F9:
				num = 58
				num7 = CInt((num4 - 1L))
				IL_404:
				num = 59
				If Not(od = 5 Or od = 4 Or od = 2) Then
					GoTo IL_46D
				End If
				IL_41A:
				num = 60
				If num7 <= 1 Then
					GoTo IL_677
				End If
				IL_425:
				num = 61
				If od <> 5 Then
					GoTo IL_44D
				End If
				IL_42D:
				num = 62
				Dim sortStyles As modSort.SortStyles = modSort.SortStyles.StyleExplorer
				Dim flag As Boolean = True
				Dim flag2 As Boolean = True
				modSort.SortStrings(array, num7, sortStyles, flag, flag2)
				GoTo IL_677
				IL_44D:
				num = 64
				sortStyles = modSort.SortStyles.StyleXP
				flag2 = True
				flag = True
				modSort.SortStrings(array, num7, sortStyles, flag2, flag)
				GoTo IL_677
				IL_46D:
				num = 66
				Dim num8 As Integer = num7 - 1
				For i As Integer = 0 To num8
					IL_47E:
					num = 67
					Dim num9 As Integer = i + 1
					Dim num10 As Integer = num7
					For j As Integer = num9 To num10
						IL_490:
						num = 68
						Dim text6 As String = Strings.Mid(array(i), Strings.InStrRev(array(i), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						IL_4B2:
						num = 69
						Dim text7 As String = Strings.Mid(array(j), Strings.InStrRev(array(j), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						IL_4D4:
						num = 70
						Select Case od
							Case 1
								IL_4FF:
								num = 73
								Dim lastWriteTime As DateTime = File.GetLastWriteTime(array2(i))
								IL_50E:
								num = 74
								Dim lastWriteTime2 As DateTime = File.GetLastWriteTime(array2(j))
								IL_51D:
								num = 75
								If DateTime.Compare(lastWriteTime, lastWriteTime2) > 0 Then
									IL_52F:
									num = 76
									Dim text8 As String = array(i)
									IL_539:
									num = 77
									array(i) = array(j)
									IL_546:
									num = 78
									array(j) = text8
								End If
							Case 2
								IL_555:
								num = 80
								If Operators.CompareString(Support.Format(text6, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(text7, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) > 0 Then
									IL_580:
									num = 81
									Dim text8 As String = array(i)
									IL_58A:
									num = 82
									array(i) = array(j)
									IL_597:
									num = 83
									array(j) = text8
								End If
							Case 3
								IL_5A6:
								num = 85
								If Conversion.Val(text6) > Conversion.Val(text7) Then
									IL_5BC:
									num = 86
									Dim text8 As String = array(i)
									IL_5C6:
									num = 87
									array(i) = array(j)
									IL_5D3:
									num = 88
									array(j) = text8
								End If
							Case 4
								IL_5DF:
								num = 90
								If Conversion.Val(text6) > Conversion.Val(text7) Then
									IL_5F2:
									num = 91
									Dim text8 As String = array(i)
									IL_5FC:
									num = 92
									array(i) = array(j)
									IL_609:
									num = 93
									array(j) = text8
								End If
							Case 5
								IL_615:
								num = 95
								Dim x As String = text6
								IL_61C:
								num = 96
								Dim y As String = text7
								IL_623:
								num = 97
								If modSort.StrCmpLogicalW(x, y) > 0 Then
									IL_632:
									num = 98
									Dim text8 As String = array(i)
									IL_63C:
									num = 99
									array(i) = array(j)
									IL_649:
									num = 100
									array(j) = text8
								End If
						End Select
						IL_653:
						num = 102
					Next
					IL_665:
					num = 103
				Next
				IL_677:
				num = 104
				If num7 <> -1 Then
					GoTo IL_68A
				End If
				IL_67F:
				num = 105
				num11 = 1S
				GoTo IL_A10
				IL_68A:
				num = 107
				array3 = New Integer(num7 + 1 - 1) {}
				IL_698:
				num = 108
				num11 = 2S
				IL_69E:
				num = 109
				Dim num12 As Short = -1S
				IL_6A4:
				num = 110
				Dim num13 As Integer = 0
				IL_6AA:
				num = 111
				text4 = "Datenträger wird analysiert (Level 2 Scan)"
				IL_6B4:
				num = 112
				MyProject.Forms.frmCheckImages.lblInfo.Text = text4
				IL_6CD:
				num = 113
				MyProject.Forms.frmCheckImages.lblStapel.Text = Conversions.ToString(num7 + 1)
				IL_6ED:
				num = 114
				Dim num14 As Long = CLng(num7)
				num4 = 0L
				While num4 <= num14
					IL_6FE:
					num = 115
					Dim i As Integer = 0
					IL_704:
					num = 116
					IL_89A:
					num = 137
					text5 = array(CInt(num4)) + "\*.*"
					IL_8B2:
					num = 138
					Dim directories As String() = Directory.GetDirectories(array(CInt(num4)))
					IL_8C5:
					num = 139
					Dim num15 As Integer = 0
					IL_8CE:
					num = 140
					If directories.Length > 0 Then
						While True
							IL_8DE:
							num = 142
							If i > CInt(num12) Then
								IL_8EA:
								num = 143
								array4 = CType(Utils.CopyArray(array4, New String(1000, i + 50 + 1 - 1) {}), String(,))
								IL_90F:
								num = 144
								num12 = CShort((i + 50))
							End If
							IL_91D:
							num = 145
							array4(CInt(num4), i) = directories(num15)
							IL_934:
							num = 146
							num15 += 1
							IL_940:
							num = 147
							i += 1
							IL_94C:
							num = 148
							num13 += 1
							IL_958:
							num = 149
							num11 = 3S
							IL_961:
							num = 150
							MyProject.Forms.frmCheckImages.lblDokumente.Text = Conversions.ToString(num13)
							IL_982:
							num = 151
							If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
								Exit For
							End If
							IL_9D9:
							num = 155
							If num15 = directories.Length Then
								GoTo IL_9EA
							End If
						End While
						IL_9AC:
						num = 152
						MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
						IL_9CC:
						num = 153
						result = False
						GoTo IL_2EAA
					End If
					IL_9EA:
					num = 156
					array3(CInt(num4)) = i - 1
					IL_9FA:
					num = 157
					num4 += 1L
				End While
				IL_A10:
				num = 158
				If Not(od = 5 Or od = 4 Or od = 2) Then
					GoTo IL_B86
				End If
				IL_A2C:
				num = 159
				Dim num16 As Long = CLng(num7)
				num4 = 0L
				While num4 <= num16
					IL_A40:
					num = 160
					If array3(CInt(num4)) > 1 Then
						IL_A52:
						num = 161
						array5 = New String(array3(CInt(num4)) + 1 - 1) {}
						IL_A67:
						num = 162
						Dim num17 As Integer = array3(CInt(num4))
						For i As Integer = 0 To num17
							IL_A7A:
							num = 163
							array5(i) = array4(CInt(num4), i)
							IL_A91:
							num = 164
						Next
						IL_AA3:
						num = 165
						If od = 5 Then
							IL_AAE:
							num = 166
							Dim array6 As Integer() = array3
							Dim num18 As Integer = CInt(num4)
							sortStyles = modSort.SortStyles.StyleExplorer
							flag = True
							flag2 = True
							modSort.SortStrings(array5, array6(num18), sortStyles, flag, flag2)
						Else
							IL_AD6:
							num = 168
							If od = 4 Then
								IL_AE1:
								num = 169
								Dim array7 As Integer() = array3
								Dim num19 As Integer = CInt(num4)
								sortStyles = modSort.SortStyles.StyleXP
								flag2 = True
								flag = True
								modSort.SortStrings(array5, array7(num19), sortStyles, flag2, flag)
							Else
								IL_B09:
								num = 171
								Dim array8 As Integer() = array3
								Dim num20 As Integer = CInt(num4)
								sortStyles = modSort.SortStyles.Style2000
								flag = True
								flag2 = True
								modSort.SortStrings(array5, array8(num20), sortStyles, flag, flag2)
							End If
						End If
						IL_B2F:
						num = 172
						Dim num21 As Integer = array3(CInt(num4))
						For i As Integer = 0 To num21
							IL_B42:
							num = 173
							array4(CInt(num4), i) = array5(i)
							IL_B59:
							num = 174
						Next
					End If
					IL_B6B:
					num = 175
					num4 += 1L
				End While
				GoTo IL_F3F
				IL_B86:
				num = 177
				Dim num22 As Long = CLng(num7)
				num4 = 0L
				While num4 <= num22
					IL_B9A:
					num = 178
					Dim num23 As Integer = array3(CInt(num4)) - 1
					For i As Integer = 0 To num23
						IL_BB2:
						num = 179
						Dim num24 As Integer = i + 1
						Dim num25 As Integer = array3(CInt(num4))
						For j As Integer = num24 To num25
							IL_BCB:
							num = 180
							Dim text6 As String = Strings.Mid(array4(CInt(num4), i), Strings.InStrRev(array4(CInt(num4), i), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
							IL_BFE:
							num = 181
							Dim text7 As String = Strings.Mid(array4(CInt(num4), j), Strings.InStrRev(array4(CInt(num4), j), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
							IL_C31:
							num = 182
							Select Case od
								Case 1
									IL_C5F:
									num = 185
									Dim lastWriteTime3 As DateTime = File.GetLastWriteTime(array2(i))
									IL_C71:
									num = 186
									Dim lastWriteTime4 As DateTime = File.GetLastWriteTime(array2(j))
									IL_C83:
									num = 187
									If DateTime.Compare(lastWriteTime3, lastWriteTime4) > 0 Then
										IL_C95:
										num = 188
										Dim text8 As String = array4(CInt(num4), i)
										IL_CA9:
										num = 189
										array4(CInt(num4), i) = array4(CInt(num4), j)
										IL_CC7:
										num = 190
										array4(CInt(num4), j) = text8
									End If
									IL_CDB:
									num = 191
									modDeclares.CloseHandle(hObject)
									IL_CE9:
									num = 192
									modDeclares.CloseHandle(hObject2)
								Case 2
									IL_CFC:
									num = 194
									If Operators.CompareString(Support.Format(text6, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(text7, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) > 0 Then
										IL_D2A:
										num = 195
										Dim text8 As String = array4(CInt(num4), i)
										IL_D3E:
										num = 196
										array4(CInt(num4), i) = array4(CInt(num4), j)
										IL_D5C:
										num = 197
										array4(CInt(num4), j) = text8
									End If
								Case 3
									IL_D75:
									num = 199
									If Conversion.Val(text6) > Conversion.Val(text7) Then
										IL_D8E:
										num = 200
										Dim text8 As String = array4(CInt(num4), i)
										IL_DA2:
										num = 201
										array4(CInt(num4), i) = array4(CInt(num4), j)
										IL_DC0:
										num = 202
										array4(CInt(num4), j) = text8
									End If
								Case 4
									IL_DD9:
									num = 204
									If Conversion.Val(text6) > Conversion.Val(text7) Then
										IL_DF2:
										num = 205
										Dim text8 As String = array4(CInt(num4), i)
										IL_E06:
										num = 206
										array4(CInt(num4), i) = array4(CInt(num4), j)
										IL_E24:
										num = 207
										array4(CInt(num4), j) = text8
									End If
								Case 5
									IL_E3A:
									num = 209
									Dim x As String = text6
									IL_E44:
									num = 210
									Dim y As String = text7
									IL_E4E:
									num = 211
									If modSort.StrCmpLogicalW(x, y) > 0 Then
										IL_E60:
										num = 212
										Dim text8 As String = array4(CInt(num4), i)
										IL_E74:
										num = 213
										array4(CInt(num4), i) = array4(CInt(num4), j)
										IL_E92:
										num = 214
										array4(CInt(num4), j) = text8
									End If
							End Select
							IL_EA6:
							num = 216
							If Operators.CompareString(text6, text7, False) > 0 Then
								IL_EB9:
								num = 217
								Dim text8 As String = array4(CInt(num4), i)
								IL_ECD:
								num = 218
								array4(CInt(num4), i) = array4(CInt(num4), j)
								IL_EEB:
								num = 219
								array4(CInt(num4), j) = text8
							End If
							IL_EFF:
							num = 220
						Next
						IL_F14:
						num = 221
					Next
					IL_F29:
					num = 222
					num4 += 1L
				End While
				IL_F3F:
				num = 223
				modDeclares.imagecount = -1
				IL_F4B:
				num = 224
				num26 = num11 + 1S
				IL_F58:
				num = 225
				num27 = 0L
				IL_F62:
				num = 226
				Dim num28 As Long = CLng(modMain.GetTotalFileCount2(path))
				IL_F71:
				num = 227
				Dim timeOfDay As DateTime = DateAndTime.TimeOfDay
				IL_F7E:
				num = 228
				text4 = "Datenträger wird analysiert (Dokumentenanalyse)"
				IL_F8B:
				num = 229
				MyProject.Forms.frmCheckImages.lblInfo.Text = text4
				IL_FA7:
				num = 230
				If num7 < 0 Then
					GoTo IL_219F
				End If
				IL_FB5:
				num = 231
				Dim num29 As Long = CLng(num7)
				Dim num5 As Integer
				Dim sortStyles As modSort.SortStyles
				Dim flag As Boolean
				Dim flag2 As Boolean
				Dim i As Integer
				Dim win32_FIND_DATA2 As modDeclares.WIN32_FIND_DATA
				Dim num42 As Integer
				num4 = 0L
				While num4 <= num29
					IL_FC9:
					num = 232
					If array3(CInt(num4)) >= 0 Then
						IL_FDB:
						num = 233
						Dim num30 As Integer = array3(CInt(num4))
						i = 0
						While i <= num30
							IL_FF1:
							num = 234
							Dim num31 As Long = 0L
							IL_FFB:
							num = 235
							If Not modDeclares.SystemData.UseUnicode Then
								IL_100D:
								num = 236
								text5 = array4(CInt(num4), i) + "\*.*"
								IL_102B:
								num = 237
								modDeclares.handle = modDeclares.FindFirstFile(text5, win32_FIND_DATA)
								IL_103F:
								num = 238
								text5 = modMain.trunc(win32_FIND_DATA.cFileName)
							Else
								IL_1058:
								num = 240
								text5 = array4(CInt(num4), i) + "\*.*"
								IL_1076:
								num = 241
								text2 = text5
								win32_FIND_DATA2 = win32_FIND_DATA
								modDeclares.handle = modDeclares.FindFirstFile(text2, win32_FIND_DATA2)
								IL_1092:
								num = 242
								text5 = modMain.trunc(win32_FIND_DATA.cFileName)
							End If
							Dim text9 As String
							Dim array9 As String()
							While True
								IL_1269:
								num = 244
								If Operators.CompareString(text5, "", False) = 0 Then
									Exit For
								End If
								IL_10AB:
								num = 245
								If Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0 And modMain.IsValidExtension(text5) Then
									IL_10DF:
									num = 246
									path = array4(CInt(num4), i) + "\" + text5
									IL_10FF:
									num = 247
									If modMain.IsUnicode(path) Then
										IL_110D:
										num = 248
										text9 = MyProject.Application.Info.DirectoryPath + "\X.IMG"
										IL_112E:
										num = 249
										If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
											IL_1155:
											num = 250
											text9 = MyProject.Application.Info.DirectoryPath + "\X.PDF"
										End If
										IL_1176:
										num = 251
										fileSystemObject.CopyFile(path, text9, True)
									Else
										IL_118A:
										num = 253
										text9 = path
									End If
									IL_1194:
									num = 254
									num31 += 1L
									IL_11A1:
									num = 255
									array9 = CType(Utils.CopyArray(array9, New String(CInt(num31) + 1 - 1) {}), String())
									IL_11BF:
									num = 256
									array9(CInt(num31)) = text9
								End If
								IL_11CD:
								num = 257
								If Not modDeclares.SystemData.UseUnicode Then
									IL_11DF:
									num = 258
									num5 = CInt(modDeclares.FindNextFile(modDeclares.handle, win32_FIND_DATA))
									IL_11F4:
									num = 259
									If num5 = 0 Then
										IL_11FE:
										num = 260
										text5 = ""
									Else
										IL_120D:
										num = 262
										text5 = modMain.trunc(win32_FIND_DATA.cFileName)
									End If
								Else
									IL_1223:
									num = 264
									Dim handle As Long = modDeclares.handle
									win32_FIND_DATA2 = win32_FIND_DATA
									num5 = CInt(modDeclares.FindNextFile(handle, win32_FIND_DATA2))
									IL_123C:
									num = 265
									If num5 = 0 Then
										IL_1246:
										num = 266
										text5 = ""
									Else
										IL_1255:
										num = 268
										text5 = modMain.trunc(win32_FIND_DATA.cFileName)
									End If
								End If
							End While
							IL_1281:
							num = 270
							modDeclares.FindClose(modDeclares.handle)
							IL_1292:
							num = 271
							If od = 5 Then
								IL_129D:
								num = 272
								Dim num32 As Integer = CInt(num31)
								sortStyles = modSort.SortStyles.StyleExplorer
								flag2 = True
								flag = True
								modSort.SortStrings(array9, num32, sortStyles, flag2, flag)
								num31 = CLng(num32)
							End If
							IL_12C5:
							num = 273
							If od = 4 Then
								IL_12D0:
								num = 274
								Dim array10 As Integer() = array3
								Dim num33 As Integer = CInt(num4)
								sortStyles = modSort.SortStyles.StyleXP
								flag = True
								flag2 = True
								modSort.SortStrings(array5, array10(num33), sortStyles, flag, flag2)
							End If
							IL_12F6:
							num = 275
							If od = 2 Then
								IL_1301:
								num = 276
								Dim array11 As Integer() = array3
								Dim num34 As Integer = CInt(num4)
								sortStyles = modSort.SortStyles.Style2000
								flag2 = True
								flag = True
								modSort.SortStrings(array5, array11(num34), sortStyles, flag2, flag)
							End If
							IL_1327:
							num = 277
							Dim num35 As Long = num31
							For num36 As Long = 1L To num35
								IL_133A:
								num = 278
								path = array9(CInt(num36))
								IL_1348:
								num = 279
								MyProject.Forms.frmCheckImages.lblFile.Text = path.ToString()
								IL_1369:
								num = 280
								MyProject.Forms.frmCheckImages.lblFile.Refresh()
								IL_1383:
								num = 281
								Dim num37 As Long
								If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
									IL_13AA:
									num = 282
									num37 = 999L
								End If
								IL_13B8:
								num = 284
								Dim num38 As Integer
								If num37 = 999L Then
									IL_13C8:
									num = 285
									frmImageXpress.GetPDFPageCount(text9, num38)
								Else
									IL_13DC:
									num = 287
									num38 = CInt(frmImageXpress.NumPages(text9))
									IL_13EE:
									num = 288
									If num38 < 0 Then
										IL_13F9:
										num = 289
										num38 = 1
									End If
								End If
								IL_1402:
								num = 290
								Dim num39 As Integer
								If num38 = 0 Then
									IL_140C:
									num = 291
									Dim num32 As Integer = 0
									num39 = -1
									modMain.AddToErrorList(path, num32, num39)
								End If
								IL_1422:
								num = 292
								num27 += 1L
								IL_142F:
								num = 293
								Dim text10 As String = Strings.Mid(array(CInt(num4)), Strings.InStrRev(array(CInt(num4)), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
								IL_1456:
								num = 294
								MyProject.Forms.frmCheckImages.lblProzent.Text = Support.Format(CDbl((num27 * 100L)) / CDbl(num28), "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
								IL_148C:
								num = 295
								MyProject.Forms.frmCheckImages.lblProzent.Refresh()
								IL_14A6:
								num = 296
								MyProject.Forms.frmCheckImages.ProgressBar1.Value = CInt(Math.Round(CDbl((num27 * 100L)) / CDbl(num28)))
								IL_14D1:
								num = 297
								Dim timeOfDay2 As DateTime = DateAndTime.TimeOfDay
								IL_14DE:
								num = 298
								Dim flag3 As Boolean

									Dim num40 As Double = timeOfDay2.ToOADate() - timeOfDay.ToOADate()
									IL_14F5:
									num = 299
									MyProject.Forms.frmCheckImages.lblZeit.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									IL_1522:
									num = 300
									num40 = num40 / CDbl(num27) * CDbl((num28 - num27))
									IL_1537:
									num = 301
									If num27 Mod 10L = 0L Then
										IL_1545:
										num = 302
										MyProject.Forms.frmCheckImages.lblRest.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									End If
									IL_1572:
									num = 303
									If num37 = 999L Then
										IL_1582:
										num = 304
										flag3 = modDeclares.SystemData.OnePagePDFs
									Else
										IL_1596:
										num = 306
										flag3 = modDeclares.SystemData.OnePageTIFFs
									End If
									IL_15A8:
									num = 307
									num39 = num38

								For k As Integer = 1 To num39
									IL_15BA:
									num = 308
									MyProject.Forms.frmCheckImages.lblPage.Text = k.ToString()
									IL_15DB:
									num = 309
									MyProject.Forms.frmCheckImages.lblPage.Refresh()
									IL_15F5:
									num = 310
									If(k = 1 And num38 > 1) Or (k = 1 AndAlso flag3) Then
										IL_1611:
										num = 311
										num26 += 1S
										IL_161E:
										num = 312
										text10 = text5
									End If
									IL_1628:
									num = 313
									Dim num41 As Integer
									modMain.AddImage(modDeclares.imagecount, path, num41, num26, k, text10)
									IL_1641:
									num = 314
									If num26 > 1S Then
										IL_164C:
										num = 315
										num26 = 1S
									End If
									IL_1655:
									num = 316
									If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
										IL_167F:
										num = 317
										MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
										IL_169F:
										num = 318
										result = False
										GoTo IL_2EAA
									End If
									IL_16AC:
									num = 320
								Next
								IL_16C1:
								num = 321
								If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
									IL_16EB:
									num = 322
									MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
									IL_170B:
									num = 323
									result = False
									GoTo IL_2EAA
								End If
								IL_1718:
								num = 325
								MyProject.Forms.frmCheckImages.lblImages.Text = Conversions.ToString(modDeclares.imagecount)
								IL_173C:
								num = 326
								MyProject.Forms.frmCheckImages.lblImages.Refresh()
								IL_1756:
								num = 327
								If modMain.IsUnicode(path) Then
									IL_1764:
									num = 328
									FileSystem.Kill(text9)
								End If
								IL_1771:
								num = 329
							Next
							IL_1787:
							num = 330
							num26 = 2S
							IL_1790:
							num = 331
							i += 1
						End While
					Else
						IL_17AA:
						num = 333
						text5 = array(CInt(num4)) + "\*.*"
						IL_17C2:
						num = 334
						text5 = array(CInt(num4))
						IL_17D0:
						num = 335
						Dim files As String() = Directory.GetFiles(text5)
						IL_17DF:
						num = 336
						num42 = 0
						IL_17E8:
						num = 337
						Dim num43 As Integer = 0
						While True
							IL_1880:
							num = 339
							If num43 >= files.Length Then
								Exit For
							End If
							IL_17F6:
							num = 340
							text5 = files(num43)
							IL_1803:
							num = 341
							If Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0 And modMain.IsValidExtension(text5) Then
								IL_1834:
								num = 342
								path = text5
								IL_183E:
								num = 343
								num42 += 1
								IL_184A:
								num = 344
								array2 = CType(Utils.CopyArray(array2, New String(num42 + 1 - 1) {}), String())
								IL_1867:
								num = 345
								array2(num42) = path
							End If
							IL_1874:
							num = 346
							num43 += 1
						End While
						IL_1891:
						num = 348
						If od = 5 Or od = 4 Or od = 2 Then
							IL_18AD:
							num = 349
							If num42 > 1 Then
								IL_18BB:
								num = 350
								If od = 5 Then
									IL_18C6:
									num = 351
									sortStyles = modSort.SortStyles.StyleExplorer
									flag = True
									flag2 = True
									modSort.SortStrings(array2, num42, sortStyles, flag, flag2)
								Else
									IL_18E9:
									num = 353
									If od = 4 Then
										IL_18F4:
										num = 354
										sortStyles = modSort.SortStyles.StyleXP
										flag2 = True
										flag = True
										modSort.SortStrings(array2, num42, sortStyles, flag2, flag)
									Else
										IL_1917:
										num = 356
										sortStyles = modSort.SortStyles.Style2000
										flag = True
										flag2 = True
										modSort.SortStrings(array2, num42, sortStyles, flag, flag2)
									End If
								End If
							End If
						Else
							IL_193A:
							num = 358
							Dim num32 As Integer = num42 - 1
							i = 1
							While i <= num32
								IL_194E:
								num = 359
								MyProject.Forms.frmCheckImages.lblInfo.Text = Support.Format(CDbl((100 * i)) / CDbl((num42 - 1)), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "%"
								IL_198F:
								num = 360
								Dim num44 As Integer = i + 1
								Dim num45 As Integer = num42
								For j As Integer = num44 To num45
									IL_19A4:
									num = 361
									Dim text6 As String = Strings.Mid(array2(i), Strings.InStrRev(array2(i), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
									IL_19C9:
									num = 362
									Dim text7 As String = Strings.Mid(array2(j), Strings.InStrRev(array2(j), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
									IL_19EE:
									num = 363
									Select Case od
										Case 1
											IL_1A1C:
											num = 366
											Dim lastWriteTime5 As DateTime = File.GetLastWriteTime(array2(i))
											IL_1A2E:
											num = 367
											Dim lastWriteTime6 As DateTime = File.GetLastWriteTime(array2(j))
											IL_1A40:
											num = 368
											If DateTime.Compare(lastWriteTime5, lastWriteTime6) > 0 Then
												IL_1A52:
												num = 369
												Dim text8 As String = array2(i)
												IL_1A5F:
												num = 370
												array2(i) = array2(j)
												IL_1A6F:
												num = 371
												array2(j) = text8
											End If
											IL_1A7C:
											num = 372
											modDeclares.CloseHandle(hObject)
											IL_1A8A:
											num = 373
											modDeclares.CloseHandle(hObject2)
										Case 2
											IL_1A9D:
											num = 375
											If String.Compare(text6, text7) > 1 Then
												IL_1AB2:
												num = 376
												Dim text8 As String = array2(i)
												IL_1ABF:
												num = 377
												array2(i) = array2(j)
												IL_1ACF:
												num = 378
												array2(j) = text8
											End If
										Case 3
											IL_1AE1:
											num = 380
											If Conversion.Val(text6) > Conversion.Val(text7) Then
												IL_1AFA:
												num = 381
												Dim text8 As String = array2(i)
												IL_1B07:
												num = 382
												array2(i) = array2(j)
												IL_1B17:
												num = 383
												array2(j) = text8
											End If
										Case 4
											IL_1B29:
											num = 385
											If Conversion.Val(text6) > Conversion.Val(text7) Then
												IL_1B3F:
												num = 386
												Dim text8 As String = array2(i)
												IL_1B4C:
												num = 387
												array2(i) = array2(j)
												IL_1B5C:
												num = 388
												array2(j) = text8
											End If
										Case 5
											IL_1B6B:
											num = 390
											Dim x As String = text6
											IL_1B75:
											num = 391
											Dim y As String = text7
											IL_1B7F:
											num = 392
											If modSort.StrCmpLogicalW(x, y) > 0 Then
												IL_1B91:
												num = 393
												Dim text8 As String = array2(i)
												IL_1B9E:
												num = 394
												array2(i) = array2(j)
												IL_1BAE:
												num = 395
												array2(j) = text8
											End If
									End Select
									IL_1BBB:
									num = 397
								Next
								IL_1BD0:
								num = 398
								If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
									IL_1BFA:
									num = 399
									MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
									IL_1C1A:
									num = 400
									result = False
									GoTo IL_2EAA
								End If
								IL_1C27:
								num = 402
								i += 1
							End While
						End If
						IL_1C3C:
						num = 403
						Dim num46 As Integer = num42
						For j As Integer = 1 To num46
							IL_1C4E:
							num = 404
							text5 = Strings.Mid(array2(j), Strings.InStrRev(array2(j), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
							IL_1C73:
							num = 405
							If Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0 And modMain.IsValidExtension(text5) Then
								IL_1CA7:
								num = 406
								path = array(CInt(num4)) + "\" + text5
								IL_1CC1:
								num = 407
								Dim text9 As String
								If modMain.IsUnicode(path) Then
									IL_1CCF:
									num = 408
									text9 = MyProject.Application.Info.DirectoryPath + "\X.IMG"
									IL_1CF0:
									num = 409
									If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
										IL_1D17:
										num = 410
										text9 = MyProject.Application.Info.DirectoryPath + "\X.PDF"
									End If
									IL_1D38:
									num = 411
									fileSystemObject.CopyFile(path, text9, True)
								Else
									IL_1D4C:
									num = 413
									text9 = path
								End If
								IL_1D56:
								num = 414
								Dim num37 As Long
								If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
									IL_1D7D:
									num = 415
									num37 = 999L
								Else
									IL_1D8D:
									num = 417
									num37 = 1L
								End If
								IL_1D97:
								num = 418
								If num37 <> 0L Then
									IL_1DA4:
									num = 419
									Dim num38 As Integer
									If num37 = 999L Then
										IL_1DB4:
										num = 420
										frmImageXpress.GetPDFPageCount(text9, num38)
									Else
										IL_1DC8:
										num = 422
										num38 = CInt(frmImageXpress.NumPages(text9))
										IL_1DDA:
										num = 423
										If num38 < 0 Then
											IL_1DE5:
											num = 424
											num38 = 1
										End If
									End If
									IL_1DEE:
									num = 425
									If Not Information.IsNothing(modMain.glImage) Then
										IL_1E00:
										num = 426
										modMain.glImage.Dispose()
									End If
									IL_1E10:
									num = 427
									Dim text10 As String = Strings.Mid(array(CInt(num4)), Strings.InStrRev(array(CInt(num4)), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
									IL_1E37:
									num = 428
									num27 += 1L
									IL_1E44:
									num = 429
									MyProject.Forms.frmCheckImages.lblProzent.Text = Support.Format(CDbl((num27 * 100L)) / CDbl(num28), "#0.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									IL_1E7A:
									num = 430
									MyProject.Forms.frmCheckImages.lblProzent.Refresh()
									IL_1E94:
									num = 431
									MyProject.Forms.frmCheckImages.ProgressBar1.Value = CInt(Math.Round(CDbl((num27 * 100L)) / CDbl(num28)))
									IL_1EBF:
									num = 432
									Dim timeOfDay2 As DateTime = DateAndTime.TimeOfDay
									IL_1ECC:
									num = 433
									Dim flag3 As Boolean
									Dim num47 As Integer

										Dim num40 As Double = timeOfDay2.ToOADate() - timeOfDay.ToOADate()
										IL_1EE3:
										num = 434
										MyProject.Forms.frmCheckImages.lblZeit.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
										IL_1F10:
										num = 435
										num40 = num40 / CDbl(num27) * CDbl((num28 - num27))
										IL_1F25:
										num = 436
										MyProject.Forms.frmCheckImages.lblRest.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
										IL_1F52:
										num = 437
										If num37 = 999L Then
											IL_1F62:
											num = 438
											flag3 = modDeclares.SystemData.OnePagePDFs
										Else
											IL_1F76:
											num = 440
											flag3 = modDeclares.SystemData.OnePageTIFFs
										End If
										IL_1F88:
										num = 441
										num47 = num38

									For k As Integer = 1 To num47
										IL_1F9A:
										num = 442
										MyProject.Forms.frmCheckImages.lblPage.Text = k.ToString()
										IL_1FBB:
										num = 443
										MyProject.Forms.frmCheckImages.lblPage.Refresh()
										IL_1FD5:
										num = 444
										If(k = 1 And num38 > 1) Or (k = 1 AndAlso flag3) Then
											IL_1FF1:
											num = 445
											num26 += 1S
											IL_1FFE:
											num = 446
											num11 = 2S
											IL_2007:
											num = 447
											text10 = text5
											IL_2011:
											num = 448
											If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
												IL_203B:
												num = 449
												MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
												IL_205B:
												num = 450
												result = False
												GoTo IL_2EAA
											End If
										End If
										IL_2068:
										num = 452
										Dim num41 As Integer
										modMain.AddImage(modDeclares.imagecount, path, num41, num26, k, text10)
										IL_2081:
										num = 453
										If num26 > 1S Then
											IL_208C:
											num = 454
											num26 = 1S
										End If
										IL_2095:
										num = 455
										If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
											IL_20BF:
											num = 456
											MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
											IL_20DF:
											num = 457
											result = False
											GoTo IL_2EAA
										End If
										IL_20EC:
										num = 459
									Next
									IL_2101:
									num = 460
									MyProject.Forms.frmCheckImages.lblImages.Text = Conversions.ToString(modDeclares.imagecount)
								End If
								IL_2125:
								num = 461
								If modMain.IsUnicode(path) Then
									IL_2133:
									num = 462
									FileSystem.Kill(text9)
								End If
							End If
							IL_2140:
							num = 463
							IL_2155:
							num = 466
						Next
						IL_216A:
						num = 467
						Dim useUnicode As Boolean = modDeclares.SystemData.UseUnicode
					End If
					IL_217B:
					num = 468
					num26 = 3S
					IL_2184:
					num = 469
					num4 += 1L
				End While
				GoTo IL_2CEA
				IL_219F:
				num = 471
				num42 = 0
				IL_21A8:
				num = 472
				If modDeclares.SystemData.UseUnicode Then
					GoTo IL_2279
				End If
				IL_21BD:
				num = 473
				text5 = FileSystem.Dir(path + "\*.*", Microsoft.VisualBasic.FileAttribute.Normal)
				While True
					IL_225C:
					num = 475
					If Operators.CompareString(text5, "", False) = 0 Then
						Exit For
					End If
					IL_21DC:
					num = 476
					If Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0 And modMain.IsValidExtension(text5) Then
						IL_220D:
						num = 477
						num42 += 1
						IL_2219:
						num = 478
						array2 = CType(Utils.CopyArray(array2, New String(num42 + 1 - 1) {}), String())
						IL_2236:
						num = 479
						array2(num42) = path + "\" + text5
					End If
					IL_224F:
					num = 480
					text5 = FileSystem.Dir()
				End While
				GoTo IL_238F
				IL_2279:
				num = 483
				text5 = path + "\*.*"
				IL_228D:
				num = 484
				text2 = text5
				win32_FIND_DATA2 = win32_FIND_DATA
				modDeclares.handle = modDeclares.FindFirstFile(text2, win32_FIND_DATA2)
				Do
					IL_22A9:
					num = 486
					If(CULng(win32_FIND_DATA.dwFileAttributes) And 16UL) <> 16UL Then
						IL_22C3:
						num = 487
						If modMain.IsValidExtension(text5) Then
							IL_22D5:
							num = 488
							array2 = CType(Utils.CopyArray(array2, New String(num42 + 1 - 1) {}), String())
							IL_22F2:
							num = 489
							num42 += 1
							IL_22FE:
							num = 490
							array2 = CType(Utils.CopyArray(array2, New String(num42 + 1 - 1) {}), String())
							IL_231B:
							num = 491
							array2(num42) = modMain.trunc(win32_FIND_DATA.cFileName)
							IL_2332:
							num = 492
							array2(num42) = path + "\" + modMain.trunc(win32_FIND_DATA.cFileName)
						End If
					End If
					IL_2355:
					num = 493
					Dim handle2 As Long = modDeclares.handle
					win32_FIND_DATA2 = win32_FIND_DATA
					num5 = CInt(modDeclares.FindNextFile(handle2, win32_FIND_DATA2))
					IL_236E:
					num = 494
				Loop While num5 <> 0
				IL_237E:
				num = 495
				modDeclares.FindClose(modDeclares.handle)
				IL_238F:
				num = 496
				If Not(od = 5 Or od = 4 Or od = 2) Then
					GoTo IL_2438
				End If
				IL_23AB:
				num = 497
				If num42 <= 1 Then
					GoTo IL_2752
				End If
				IL_23B9:
				num = 498
				If od <> 5 Then
					GoTo IL_23E7
				End If
				IL_23C4:
				num = 499
				sortStyles = modSort.SortStyles.StyleExplorer
				flag2 = True
				flag = True
				modSort.SortStrings(array2, num42, sortStyles, flag2, flag)
				GoTo IL_2752
				IL_23E7:
				num = 501
				If od <> 4 Then
					GoTo IL_2415
				End If
				IL_23F2:
				num = 502
				sortStyles = modSort.SortStyles.StyleXP
				flag = True
				flag2 = True
				modSort.SortStrings(array2, num42, sortStyles, flag, flag2)
				GoTo IL_2752
				IL_2415:
				num = 504
				sortStyles = modSort.SortStyles.Style2000
				flag2 = True
				flag = True
				modSort.SortStrings(array2, num42, sortStyles, flag2, flag)
				GoTo IL_2752
				IL_2438:
				num = 506
				Dim num48 As Integer = num42 - 1
				i = 1
				While i <= num48
					IL_244C:
					num = 507
					MyProject.Forms.frmCheckImages.lblInfo.Text = Support.Format(CDbl((100 * i)) / CDbl(num42), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "%"
					IL_248B:
					num = 508
					MyProject.Forms.frmCheckImages.lblInfo.Refresh()
					IL_24A5:
					num = 509
					Dim num49 As Integer = i + 1
					Dim num50 As Integer = num42
					For j As Integer = num49 To num50
						IL_24BA:
						num = 510
						Dim text6 As String = Strings.Mid(array2(i), Strings.InStrRev(array2(i), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						IL_24DF:
						num = 511
						Dim text7 As String = Strings.Mid(array2(j), Strings.InStrRev(array2(j), "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						IL_2504:
						num = 512
						Select Case od
							Case 1
								IL_2532:
								num = 515
								Dim lastWriteTime7 As DateTime = File.GetLastWriteTime(array2(i))
								IL_2544:
								num = 516
								Dim lastWriteTime8 As DateTime = File.GetLastWriteTime(array2(j))
								IL_2556:
								num = 517
								If DateTime.Compare(lastWriteTime7, lastWriteTime8) > 0 Then
									IL_256B:
									num = 518
									Dim text8 As String = array2(i)
									IL_2578:
									num = 519
									array2(i) = array2(j)
									IL_2588:
									num = 520
									array2(j) = text8
								End If
							Case 2
								IL_259A:
								num = 522
								If Operators.CompareString(Support.Format(text6, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(text7, ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) > 0 Then
									IL_25C8:
									num = 523
									Dim text8 As String = array2(i)
									IL_25D5:
									num = 524
									array2(i) = array2(j)
									IL_25E5:
									num = 525
									array2(j) = text8
								End If
							Case 3
								IL_25F7:
								num = 527
								If Conversion.Val(text6) > Conversion.Val(text7) Then
									IL_2610:
									num = 528
									Dim text8 As String = array2(i)
									IL_261D:
									num = 529
									array2(i) = array2(j)
									IL_262D:
									num = 530
									array2(j) = text8
								End If
							Case 4
								IL_263F:
								num = 532
								If Conversion.Val(text6) > Conversion.Val(text7) Then
									IL_2655:
									num = 533
									Dim text8 As String = array2(i)
									IL_2662:
									num = 534
									array2(i) = array2(j)
									IL_2672:
									num = 535
									array2(j) = text8
								End If
							Case 5
								IL_2681:
								num = 537
								Dim x As String = text6
								IL_268B:
								num = 538
								Dim y As String = text7
								IL_2695:
								num = 539
								If modSort.StrCmpLogicalW(x, y) > 0 Then
									IL_26A7:
									num = 540
									Dim text8 As String = array2(i)
									IL_26B4:
									num = 541
									array2(i) = array2(j)
									IL_26C4:
									num = 542
									array2(j) = text8
								End If
						End Select
						IL_26D1:
						num = 544
					Next
					IL_26E6:
					num = 545
					If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
						IL_2710:
						num = 546
						MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
						IL_2730:
						num = 547
						result = False
						GoTo IL_2EAA
					End If
					IL_273D:
					num = 549
					i += 1
				End While
				IL_2752:
				num = 550
				Dim num51 As Long = CLng(num42)
				num4 = 1L
				While num4 <= num51
					IL_2766:
					num = 551
					Dim num37 As Long = 0L
					IL_2770:
					num = 552
					path = array2(CInt(num4))
					IL_277E:
					num = 553
					If Operators.CompareString(path, "H:\Images\ExplorerTest\Büdingen_Ortenberg_17_K_1976-2009_0033.jpg", False) = 0 Then
						IL_2793:
						num = 554
						Dim j As Integer = 1
					End If
					IL_279C:
					num = 555
					Dim text9 As String
					Dim num38 As Integer
					If modMain.IsUnicode(path) Then
						IL_27AD:
						num = 556
						text9 = MyProject.Application.Info.DirectoryPath + "\X.IMG"
						IL_27CE:
						num = 557
						If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
							IL_27F5:
							num = 558
							text9 = MyProject.Application.Info.DirectoryPath + "\X.PDF"
						End If
						IL_2816:
						num = 559
						fileSystemObject.CopyFile(path, text9, True)
						IL_2828:
						num = 560
						num38 = CInt(frmImageXpress.NumPages(text9))
						IL_283A:
						num = 561
						If num38 < 1 Then
							IL_2845:
							num = 562
							num38 = 1
						End If
					Else
						IL_2850:
						num = 564
						If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) <> 0 Then
							IL_2877:
							num = 565
							num38 = CInt(frmImageXpress.NumPages(path))
							IL_2889:
							num = 566
							If num38 < 1 Then
								IL_2894:
								num = 567
								num38 = 1
							End If
						End If
					End If
					IL_289D:
					num = 568
					If Operators.CompareString(Support.Format(Strings.Right(path, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
						IL_28C4:
						num = 569
						num37 = 999L
					End If
					IL_28D2:
					num = 570
					If num37 = 999L Then
						IL_28E2:
						num = 571
						If modMain.IsUnicode(path) Then
							IL_28F0:
							num = 572
							frmImageXpress.GetPDFPageCount(text9, num38)
						Else
							IL_2904:
							num = 574
							frmImageXpress.GetPDFPageCount(path, num38)
						End If
					Else
						IL_2917:
						num = 576
						If Operators.CompareString(path, "", False) = 0 Then
							IL_292C:
							num = 577
							Dim j As Integer = 1
						End If
						IL_2935:
						num = 578
						If path Is Nothing Then
							IL_293F:
							num = 579
							Dim j As Integer = 1
						End If
						IL_2948:
						num = 580
						num38 = CInt(frmImageXpress.GetNumberOfPagesInTIFForJPEG(path))
						IL_295A:
						num = 581
						modMain.IsUnicode(path)
						IL_2967:
						num = 583
						If num38 < 0 Then
							IL_2972:
							num = 584
							num38 = 1
						End If
					End If
					IL_297B:
					num = 585
					Dim text10 As String = Strings.Mid(path, Strings.InStrRev(path, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
					IL_299A:
					num = 586
					num27 += 1L
					IL_29A7:
					num = 587
					MyProject.Forms.frmCheckImages.lblProzent.Text = Support.Format(CDbl((num27 * 100L)) / CDbl(num28), "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					IL_29DD:
					num = 588
					MyProject.Forms.frmCheckImages.lblProzent.Refresh()
					IL_29F7:
					num = 589
					MyProject.Forms.frmCheckImages.ProgressBar1.Value = CInt(Math.Round(CDbl((num27 * 100L)) / CDbl(num28)))
					IL_2A22:
					num = 590
					Dim timeOfDay2 As DateTime = DateAndTime.TimeOfDay
					IL_2A2F:
					num = 591
					Dim flag3 As Boolean
					Dim num52 As Integer

						Dim num40 As Double = timeOfDay2.ToOADate() - timeOfDay.ToOADate()
						IL_2A46:
						num = 592
						MyProject.Forms.frmCheckImages.lblZeit.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						IL_2A73:
						num = 593
						num40 = num40 / CDbl(num27) * CDbl((num28 - num27))
						IL_2A88:
						num = 594
						MyProject.Forms.frmCheckImages.lblRest.Text = Support.Format(num40, "hh:mm:ss", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						IL_2AB5:
						num = 595
						If num27 Mod 10L = 0L Then
							IL_2AC3:
							num = 596
							MyProject.Forms.frmCheckImages.lblProzent.Refresh()
							IL_2ADD:
							num = 597
							MyProject.Forms.frmCheckImages.lblZeit.Refresh()
							IL_2AF7:
							num = 598
							MyProject.Forms.frmCheckImages.lblRest.Refresh()
						End If
						IL_2B11:
						num = 599
						If num37 = 999L Then
							IL_2B21:
							num = 600
							flag3 = modDeclares.SystemData.OnePagePDFs
						Else
							IL_2B35:
							num = 602
							flag3 = modDeclares.SystemData.OnePageTIFFs
						End If
						IL_2B47:
						num = 603
						MyProject.Forms.frmCheckImages.lblFile.Text = path
						IL_2B63:
						num = 604
						MyProject.Forms.frmCheckImages.lblFile.Refresh()
						IL_2B7D:
						num = 605
						num52 = num38

					For k As Integer = 1 To num52
						IL_2B8F:
						num = 606
						MyProject.Forms.frmCheckImages.lblPage.Text = k.ToString()
						IL_2BB0:
						num = 607
						MyProject.Forms.frmCheckImages.lblPage.Refresh()
						IL_2BCA:
						num = 608
						If(k = 1 And num38 > 1) Or (k = 1 AndAlso flag3) Then
							IL_2BE6:
							num = 609
							num26 += 1S
							IL_2BF3:
							num = 610
							num11 = 2S
						End If
						IL_2BFC:
						num = 611
						Dim num41 As Integer
						modMain.AddImage(modDeclares.imagecount, path, num41, num26, k, text10)
						IL_2C15:
						num = 612
						If num26 > 1S Then
							IL_2C20:
							num = 613
							num26 = 1S
						End If
						IL_2C29:
						num = 614
						If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) = 1.0 Then
							IL_2C53:
							num = 615
							MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
							IL_2C73:
							num = 616
							result = False
							GoTo IL_2EAA
						End If
						IL_2C80:
						num = 618
					Next
					IL_2C95:
					num = 619
					MyProject.Forms.frmCheckImages.lblImages.Text = Conversions.ToString(modDeclares.imagecount)
					IL_2CB9:
					num = 620
					If modMain.IsUnicode(path) Then
						IL_2CC7:
						num = 621
						FileSystem.Kill(text9)
					End If
					IL_2CD4:
					num = 622
					num4 += 1L
				End While
				IL_2CEA:
				ProjectData.ClearProjectError()
				num2 = 0
				IL_2CF1:
				num = 624
				If modDeclares.NO_PREVIEW Then
					GoTo IL_2D2F
				End If
				IL_2CFE:
				num = 625
				Dim num53 As Integer = 5
				Dim num54 As Long = CLng(modMain.min(num53, modDeclares.imagecount))
				num4 = 0L
				While num4 <= num54
					IL_2D1C:
					num = 626
					num4 += 1L
				End While
				IL_2D2F:
				num = 627
				modDeclares.gllevel = CInt(num11)
				IL_2D3C:
				num = 628
				Dim num55 As Long = CLng(modDeclares.imagecount)
				num4 = 0L
				While num4 <= num55
					IL_2D50:
					num = 629
					If CInt(modDeclares.Images(CInt(num4)).Level) > modDeclares.gllevel Then
						IL_2D6F:
						num = 630
						modDeclares.Images(CInt(num4)).Level = CShort(modDeclares.gllevel)
					End If
					IL_2D8D:
					num = 631
					num4 += 1L
				End While
				IL_2DA0:
				num = 632
				Dim num56 As Integer = 0
				IL_2DA9:
				num = 633
				Dim num57 As Integer = 0
				IL_2DB2:
				num = 634
				Dim num58 As Integer = 0
				IL_2DBB:
				num = 635
				Dim num59 As Long = CLng(modDeclares.imagecount)
				num4 = 0L
				While num4 <= num59
					IL_2DD2:
					num = 636
					num3 = modDeclares.Images(CInt(num4)).Level
					Select Case num3
						Case 1S
							IL_2E03:
							num = 638
							num56 += 1
						Case 2S
							IL_2E11:
							num = 640
							num56 = 0
							IL_2E1A:
							num = 641
							num57 += 1
						Case 3S
							IL_2E28:
							num = 643
							num56 = 0
							IL_2E31:
							num = 644
							num57 = 0
							IL_2E3A:
							num = 645
							num58 += 1
					End Select
					IL_2E46:
					num = 647
					modDeclares.Images(CInt(num4)).Blip1Level = num56
					IL_2E60:
					num = 648
					modDeclares.Images(CInt(num4)).Blip2Level = num57
					IL_2E7A:
					num = 649
					modDeclares.Images(CInt(num4)).Blip3Level = num58
					IL_2E94:
					num = 650
					num4 += 1L
				End While
				IL_2EAA:
				num = 651
				MyProject.Forms.frmCheckImages.Close()
				IL_2EBF:
				num = 652
				fileSystemObject = Nothing
				IL_2EC8:
				num = 653
				array4 = New String(0, 0) {}
				IL_2ED7:
				num = 654
				array = New String(0) {}
				IL_2EE5:
				num = 655
				MyProject.Forms.frmCheckImages.Close()
				IL_2EFA:
				num = 656
				If Not modMain.DoCheckImage Then
					GoTo IL_2FF6
				End If
				IL_2F0A:
				num = 657
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\ERRORLIST.TXT", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_2FF6
				End If
				IL_2F3F:
				num = 658
				modMain.ShowErrorList()
				IL_2F4A:
				num = 659
				text2 = "Bitte beachten Sie die Fehlerliste!!!"
				Dim num60 As Short = 0S
				text3 = "file-converter"
				modMain.msgbox2(text2, num60, text3)
				IL_2FF6:
				GoTo IL_3AB0
				IL_70C:
				num = 117
				text5 = FileSystem.Dir(array(CInt(num4)) + "\*.*", Microsoft.VisualBasic.FileAttribute.Directory)
				GoTo IL_880
				IL_72D:
				num = 120
				If(If(-If(((Operators.CompareString(text5, ".", False) <> 0 And Operators.CompareString(text5, "..", False) <> 0) > False), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal) And (FileSystem.GetAttr(array(CInt(num4)) + "\" + text5) And Microsoft.VisualBasic.FileAttribute.Directory)) <= Microsoft.VisualBasic.FileAttribute.Normal Then
					GoTo IL_81C
				End If
				IL_778:
				num = 121
				Dim num12 As Short
				If i <= CInt(num12) Then
					GoTo IL_7A8
				End If
				IL_781:
				num = 122
				array4 = CType(Utils.CopyArray(array4, New String(CInt(num4) + 1 - 1, i + 1 - 1) {}), String(,))
				IL_7A0:
				num = 123
				num12 = CShort(i)
				IL_7A8:
				num = 124
				array4(CInt(num4), i) = array(CInt(num4)) + "\" + text5
				IL_7C9:
				num = 125
				i += 1
				IL_7D2:
				num = 126
				Dim num13 As Integer
				num13 += 1
				IL_7DB:
				num = 127
				num11 = 3S
				IL_7E1:
				num = 128
				MyProject.Forms.frmCheckImages.lblDokumente.Text = Conversions.ToString(num13)
				IL_802:
				num = 129
				MyProject.Forms.frmCheckImages.lblDokumente.Refresh()
				IL_81C:
				num = 130
				text5 = FileSystem.Dir()
				IL_829:
				num = 131
				If Conversions.ToDouble(MyProject.Forms.frmCheckImages.cmdStop.Tag) <> 1.0 Then
					GoTo IL_880
				End If
				IL_853:
				num = 132
				MyProject.Forms.frmCheckImages.cmdStop.Tag = 0
				IL_873:
				num = 133
				result = False
				GoTo IL_2EAA
				IL_880:
				num = 119
				If Operators.CompareString(text5, "", False) <> 0 Then
					GoTo IL_72D
				End If
				GoTo IL_9EA
				IL_2148:
				num = 464
				text5 = FileSystem.Dir()
				GoTo IL_2155
				IL_2F72:
				num = 661
				Interaction.MsgBox("GetImageInfos" + Information.Err().Description + vbCrLf + Information.Err().Source, MsgBoxStyle.OkOnly, Nothing)
				IL_2FA3:
				num = 662
				Dim stackTrace As StackTrace = New StackTrace(True)
				IL_2FB1:
				num = 663
				Dim str As String = "Line: "
				num53 = stackTrace.GetFrame(0).GetFileLineNumber()
				MessageBox.Show(str + num53.ToString())
				IL_2FDD:
				num = 664
				ProjectData.ClearProjectError()
				If num61 <> 0 Then
					GoTo IL_2FFB
				End If
				Throw ProjectData.CreateProjectError(-2146828268)
				IL_2FFB:
				Dim num62 As Integer = num61 + 1
				num61 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num62)
				IL_3A6D:
				GoTo IL_3AA5
				IL_3A6F:
				num61 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_3A83:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num61 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_3A6F
			End Try
			IL_3AA5:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_3AB0:
			If num61 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E4E RID: 3662 RVA: 0x00089E7C File Offset: 0x0008807C
		Public Sub AddImage(ByRef imagecount As Integer, ByRef path As String, ByRef count As Integer, ByRef Level As Short, ByRef page As Integer, ByRef dok As String)
			Dim num2 As Integer
			Dim num6 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				If Operators.CompareString(Strings.Right(path, 5), "X.PDF", False) <> 0 Then
					GoTo IL_19
				End If
				IL_17:
				num = 2
				IL_19:
				num = 3
				If(FileSystem.GetAttr(path) And Microsoft.VisualBasic.FileAttribute.Directory) <> Microsoft.VisualBasic.FileAttribute.Directory Then
					GoTo IL_3F
				End If
				IL_29:
				num = 4
				Interaction.MsgBox(path + vbCr & "ist keine Datei!" & vbCr & "Wahrscheinlich ist die Dokumentenstruktur zu tief (>3).", MsgBoxStyle.OkOnly, Nothing)
				IL_3F:
				num = 5
				imagecount += 1
				IL_47:
				num = 6
				modDeclares.Images = CType(Utils.CopyArray(modDeclares.Images, New modDeclares.typImage(imagecount + 1 - 1) {}), modDeclares.typImage())
				IL_66:
				num = 7
				modDeclares.Images(imagecount).Name = path
				IL_7B:
				num = 8
				modDeclares.Images(imagecount).IsPDF = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(Support.Format(Strings.Right(modDeclares.Images(imagecount).Name, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0, True, False))
				IL_D5:
				num = 9
				modDeclares.Images(imagecount).Level = Level
				IL_EB:
				num = 10
				modDeclares.Images(imagecount).count = count
				IL_101:
				num = 11
				modDeclares.Images(imagecount).page = page
				IL_118:
				num = 12
				modDeclares.Images(imagecount).DokumentName = dok
				IL_12F:
				ProjectData.ClearProjectError()
				num2 = 2
				IL_136:
				num = 14
				If Not modMain.DoCheckImage Then
					GoTo IL_317
				End If
				IL_143:
				num = 15
				If Not modDeclares.Images(imagecount).IsPDF Then
					GoTo IL_224
				End If
				IL_15C:
				num = 16
				Dim frmImageXpress As frmImageXpress = MyProject.Forms.frmImageXpress
				Dim num3 As Integer = 25
				If Not frmImageXpress.OpenPDFDocumentAlt(path, page, num3, modMain.glImage) Then
					GoTo IL_20E
				End If
				IL_181:
				num = 17
				Dim width As Integer = modMain.glImage.Width
				IL_18F:
				num = 18
				Dim height As Integer = modMain.glImage.Height
				IL_19E:
				num = 19
				Dim num4 As Double = 100.0 / CDbl(width)
				IL_1AF:
				num = 20
				Dim targetWidth As Integer = CInt(Math.Round(CDbl(width) * num4))
				IL_1BF:
				num = 21
				Dim targetHeight As Integer = CInt(Math.Round(CDbl(height) * num4))
				IL_1D0:
				num = 22
				If MyProject.Forms.frmCheckImages.chkAnzeige.CheckState = CheckState.Checked Then
					GoTo IL_2F7
				End If
				IL_1ED:
				num = 23
				MyProject.Forms.frmCheckImages.ImagXpress1.Image = modMain.glImage
				GoTo IL_2F7
				IL_20E:
				num = 25
				num3 = -2
				modMain.AddToErrorList(path, page, num3)
				GoTo IL_2F7
				IL_224:
				num = 27
				IL_227:
				num = 28
				If page <> 1 Then
					GoTo IL_241
				End If
				IL_230:
				num = 29
				modMain.glImage = Image.FromFile(path)
				GoTo IL_257
				IL_241:
				num = 31
				MyProject.Forms.frmImageXpress.OpenRasterDocument(path, page)
				IL_257:
				num = 32
				width = modMain.glImage.Width
				IL_265:
				num = 33
				height = modMain.glImage.Height
				IL_274:
				num = 34
				num4 = 100.0 / CDbl(width)
				IL_285:
				num = 35
				targetWidth = CInt(Math.Round(CDbl(width) * num4))
				IL_295:
				num = 36
				targetHeight = CInt(Math.Round(CDbl(height) * num4))
				IL_2A6:
				num = 37
				If MyProject.Forms.frmCheckImages.chkAnzeige.CheckState = CheckState.Checked Then
					GoTo IL_2F7
				End If
				IL_2C0:
				num = 38
				modMain.glImage = modPaint.ResizeImage(CType(modMain.glImage, Bitmap), targetWidth, targetHeight)
				IL_2DB:
				num = 39
				MyProject.Forms.frmCheckImages.ImagXpress1.Image = modMain.glImage
				IL_2F7:
				num = 40
				Application.DoEvents()
				IL_2FF:
				num = 41
				Dim checkState As CheckState = MyProject.Forms.frmCheckImages.chkAnzeige.CheckState
				IL_317:
				num = 42
				count += 1
				IL_320:
				num = 43
				If Information.IsNothing(modMain.glImage) Then
					GoTo IL_3CC
				End If
				IL_332:
				num = 44
				modMain.glImage.Dispose()
				IL_3CC:
				GoTo IL_4EA
				IL_344:
				num = 46
				Dim text As String = "Addmage:" + Information.Err().Description + vbCrLf + Information.Err().Source
				Dim num5 As Short = 0S
				Dim text2 As String = "file-converter"
				modMain.msgbox2(text, num5, text2)
				IL_382:
				num = 47
				Dim stackTrace As StackTrace = New StackTrace(True)
				IL_38D:
				num = 48
				Dim str As String = "Line: "
				num3 = stackTrace.GetFrame(0).GetFileLineNumber()
				MessageBox.Show(str + num3.ToString())
				IL_3B6:
				num = 49
				ProjectData.ClearProjectError()
				If num6 <> 0 Then
					GoTo IL_3D1
				End If
				Throw ProjectData.CreateProjectError(-2146828268)
				IL_3D1:
				Dim num7 As Integer = num6 + 1
				num6 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num7)
				IL_4A7:
				GoTo IL_4DF
				IL_4A9:
				num6 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_4BD:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num6 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_4A9
			End Try
			IL_4DF:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_4EA:
			If num6 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000E4F RID: 3663 RVA: 0x0008A398 File Offset: 0x00088598
		Public Sub WriteToArray(ByRef dest As Byte(), ByRef source As String)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				ProjectData.ClearProjectError()
				num = 2
				Dim num2 As Short = CShort(Strings.Len(source))
				For num3 As Short = 1S To num2
					' The following expression was wrapped in a checked-expression
					dest(CInt(num3)) = CByte(Strings.Asc(Strings.Mid(source, CInt(num3), 1)))
				Next
				dest(Strings.Len(source) + 1) = 0
				IL_3D:
				GoTo IL_80
				IL_3F:
				num4 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_53:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_3F
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_80:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000E50 RID: 3664 RVA: 0x0008A440 File Offset: 0x00088640
		Public Function min(ByRef X As Integer, ByRef y As Integer) As Integer
			Dim result As Integer = X
			If y < X Then
				result = y
			End If
			Return result
		End Function

		' Token: 0x06000E51 RID: 3665 RVA: 0x0008A45C File Offset: 0x0008865C
		Public Function KommazuPunkt(ByRef s As String) As String
			Dim text As String = ""
			Dim num As Short = CShort(Strings.Len(s))
			For num2 As Short = 1S To num
				If Operators.CompareString(Strings.Mid(s, CInt(num2), 1), ",", False) = 0 Then
					text += "."
				Else
					text += Strings.Mid(s, CInt(num2), 1)
				End If
			Next
			Return text
		End Function

		' Token: 0x06000E52 RID: 3666 RVA: 0x0008A4BC File Offset: 0x000886BC
		Public Function maximum(ByRef a As Integer, ByRef b As Integer) As Integer
			Dim result As Integer
			If a >= b Then
				result = a
			Else
				result = b
			End If
			Return result
		End Function

		' Token: 0x06000E53 RID: 3667 RVA: 0x0008A4D8 File Offset: 0x000886D8
		Public Function trunc(ByRef s As String) As String
			Dim text As String = ""
			Dim num As Integer = Strings.Len(s)
			Dim num2 As Integer = 1
			While num2 <= num AndAlso Operators.CompareString(Strings.Mid(s, num2, 1), vbNullChar, False) <> 0
				text += Strings.Mid(s, num2, 1)
				num2 += 1
			End While
			Return text
		End Function

		' Token: 0x06000E54 RID: 3668 RVA: 0x0008A528 File Offset: 0x00088728
		Public Function IsUnicode(ByRef s As String) As Boolean
			Return False
		End Function

		' Token: 0x06000E55 RID: 3669 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub TranslateTemplatesToNumberOfExposures()
		End Sub

		' Token: 0x06000E56 RID: 3670 RVA: 0x0008A538 File Offset: 0x00088738
		Public Function GetDocumentCount(ByRef ind As Integer) As Integer
			Dim num As Integer = 0
			Dim level As Integer = CInt(modDeclares.Images(ind).Level)
			Dim num2 As Integer = ind
			Do
				num += 1
				num2 += 1
			Loop While num2 <= modDeclares.imagecount AndAlso CInt(modDeclares.Images(num2).Level) <> level
			Return num
		End Function

		' Token: 0x06000E57 RID: 3671 RVA: 0x0008A580 File Offset: 0x00088780
		Public Function GetInfoText(ByRef CurFrame As Integer, ByRef CurFileName As String, ByRef CurRollNr As String) As Object
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E58 RID: 3672 RVA: 0x0008A590 File Offset: 0x00088790
		Public Function SplitNorwayFileName(ByRef FolderName As String, ByRef datum As String, ByRef zeitung As String) As Boolean
			zeitung = ""
			datum = ""
			Dim result As Boolean = False
			Dim num As Integer = Strings.InStr(1, FolderName, "_", Microsoft.VisualBasic.CompareMethod.Binary)
			If num <> 0 Then
				zeitung = Strings.Left(FolderName, num - 1)
				Dim num2 As Integer = Strings.InStr(num + 1, FolderName, "_", Microsoft.VisualBasic.CompareMethod.Binary)
				If num2 <> 0 Then
					Dim num3 As Integer = Strings.InStr(num2 + 1, FolderName, "_", Microsoft.VisualBasic.CompareMethod.Binary)
					If num3 <> 0 Then
						Dim num4 As Integer = Strings.InStr(num3 + 1, FolderName, "_", Microsoft.VisualBasic.CompareMethod.Binary)
						If num4 <> 0 Then
							datum = Strings.Mid(FolderName, num3 + 1, num4 - num3 - 1)
							result = True
						End If
					End If
				End If
			End If
			Return result
		End Function

		' Token: 0x06000E59 RID: 3673 RVA: 0x0008A620 File Offset: 0x00088820
		Public Function GetFolderNamesThatFitOnFilm(ByRef Images_ As modDeclares.typImage(), ByRef imagecount As Integer, startindex As Integer, ByRef StartFolder As String, ByRef EndFolder As String, ByRef kopfindex As Short) As Boolean
			If startindex < 0 Then
				startindex = 0
			End If
			Dim num As Double = CDbl((modDeclares.SystemData.filmlaenge(CInt(kopfindex)) * 1000))
			Dim schrittweite As Double = modDeclares.SystemData.schrittweite
			StartFolder = Images_(startindex).DokumentName
			EndFolder = Images_(startindex).DokumentName
			Dim num2 As Integer = startindex
			Dim num3 As Double = 0.0
			num -= CDbl((modDeclares.SystemData.vorspann * 10 + modDeclares.SystemData.nachspann * 10)) + schrittweite * 1.0
			Do
				Dim documentCount As Integer = modMain.GetDocumentCount(num2)
				If num3 + CDbl(documentCount) * schrittweite >= num Then
					Exit Do
				End If
				EndFolder = Images_(num2 + 1).DokumentName
				num3 += CDbl(documentCount) * schrittweite
				num2 += documentCount
			Loop While num2 < imagecount
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000E5A RID: 3674 RVA: 0x0008A6E8 File Offset: 0x000888E8
		Public Function ConvertFolderToDate(ByRef Folder As String) As String
			Dim result As String = ""
			Dim str As String
			Dim text As String
			If modMain.SplitNorwayFileName(Folder, str, text) Then
				Dim num As Double = Conversion.Val(Strings.Mid(str, 5, 2))
				If num = 1.0 Then
					result = Strings.Mid(str, 7, 2) + " January"
				ElseIf num = 2.0 Then
					result = Strings.Mid(str, 7, 2) + " February"
				ElseIf num = 3.0 Then
					result = Strings.Mid(str, 7, 2) + " March"
				ElseIf num = 4.0 Then
					result = Strings.Mid(str, 7, 2) + " April"
				ElseIf num = 5.0 Then
					result = Strings.Mid(str, 7, 2) + " May"
				ElseIf num = 6.0 Then
					result = Strings.Mid(str, 7, 2) + " June"
				ElseIf num = 7.0 Then
					result = Strings.Mid(str, 7, 2) + " July"
				ElseIf num = 8.0 Then
					result = Strings.Mid(str, 7, 2) + " August"
				ElseIf num = 9.0 Then
					result = Strings.Mid(str, 7, 2) + " September"
				ElseIf num = 10.0 Then
					result = Strings.Mid(str, 7, 2) + " October"
				ElseIf num = 11.0 Then
					result = Strings.Mid(str, 7, 2) + " November"
				ElseIf num = 12.0 Then
					result = Strings.Mid(str, 7, 2) + " December"
				End If
			End If
			Return result
		End Function

		' Token: 0x06000E5B RID: 3675 RVA: 0x0008A8BC File Offset: 0x00088ABC
		Public Function GetRollCountInfo(ByRef kopfindex As Integer) As String
			Dim text As String = "TXT_INFO_FILMLEN"
			Dim text2 As String = modMain.GetText(text)
			Dim text3 As String
			Dim text4 As String
			Dim text5 As String
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Film length"
				text3 = "Spacing"
				text4 = "Rolls"
				text5 = "Allocation last roll"
			Else
				text = "TXT_INFO_STEPWIDTH"
				text3 = modMain.GetText(text)
				text = "TXT_INFO_ROLLS"
				text4 = modMain.GetText(text)
				text = "TXT_INFO_SPACE"
				text5 = modMain.GetText(text)
			End If
			Dim text6 As String
			If modDeclares.SystemData.FesteBelegzahlProFilm Then
				Dim num As Integer = CInt((CDbl((modDeclares.imagecount + 1)) / CDbl(modDeclares.SystemData.BelegeProFilm(kopfindex))))
				Dim num2 As Integer = modDeclares.SystemData.BelegeProFilm(kopfindex)
				If CDbl((num * modDeclares.SystemData.BelegeProFilm(kopfindex))) < CDbl((modDeclares.imagecount + 1)) Then
					num2 = modDeclares.imagecount + 1 - num * modDeclares.SystemData.BelegeProFilm(kopfindex)
					num += 1
				End If
				Dim num3 As Double = CDbl((num2 * 100)) / CDbl(modDeclares.SystemData.BelegeProFilm(kopfindex))
				text6 = String.Concat(New String() { "# ", text4, " = ", Conversions.ToString(num), "    " })
				text6 = String.Concat(New String() { text6, text5, " : ", Conversions.ToString(num2), " (=", Support.Format(num3, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "%)" })
			ElseIf modDeclares.SystemData.EnableRollFrameExt Then
				If modDeclares.SystemData.schrittweite = 0.0 Then
					modDeclares.SystemData.schrittweite = Conversions.ToDouble(modDeclares.ffrmFilmPreview.txtSchritte.Text)
				End If
				Dim num As Integer = 0
				Dim num4 As Integer
				Do
					num += 1
					Dim startindex As Integer = num4
					Dim num5 As Short = CShort(kopfindex)
					Dim text7 As String
					Dim right As String
					modMain.GetFolderNamesThatFitOnFilm(modDeclares.Images, modDeclares.imagecount, startindex, text7, right, num5)
					Dim flag As Boolean = False
					Dim num6 As Integer = num4
					Dim num7 As Integer = modDeclares.imagecount + 1
					For i As Integer = num6 To num7
						If i = modDeclares.imagecount + 1 Then
							GoTo IL_26B
						End If
						If flag Then
							If Operators.CompareString(modDeclares.Images(i).DokumentName, right, False) <> 0 Then
								num4 = i
								Exit For
							End If
						ElseIf Operators.CompareString(modDeclares.Images(i).DokumentName, right, False) = 0 Then
							flag = True
						End If
					Next
				Loop While num4 < modDeclares.imagecount
				IL_26B:
				Dim text8 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				text = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + modDeclares.ffrmFilmPreview.cmbTemplate.Text
				Dim num8 As Double = Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "Schrittweite"))
				If num8 <> 0.0 Then
					text = modMain.GiveIni(text8, "SYSTEM", "FILMLAENGE" + Conversions.ToString(kopfindex))
					Dim num9 As Double = Conversion.Val(modMain.KommazuPunkt(text)) - CDbl(modDeclares.SystemData.vorspann) / 100.0 - CDbl(modDeclares.SystemData.nachspann) / 100.0 - num8 * 3.0 / 1000.0
					Dim num2 As Integer = CInt(Math.Round(CDbl((modDeclares.imagecount - num4)) * num8))
					text6 = text2 + " = " + Conversions.ToString(num9) + "m    "
					text6 = String.Concat(New String() { text6, text3, " = ", Conversions.ToString(num8), "mm    " })
					text6 = String.Concat(New String() { text6, "# ", text4, " = ", Conversions.ToString(num), "    " })
					Dim num3 As Double = CDbl((num2 * 100)) / (num9 / (num8 / 1000.0))
					text6 = String.Concat(New String() { text6, text5, " : ", Conversions.ToString(num2), " (=", Support.Format(num3, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "%)" })
				End If
			Else
				Dim text8 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				text = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + modDeclares.ffrmFilmPreview.cmbTemplate.Text
				Dim num8 As Double = Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "Schrittweite"))
				If num8 <> 0.0 Then
					text = modMain.GiveIni(text8, "SYSTEM", "FILMLAENGE" + Conversions.ToString(kopfindex))
					Dim num9 As Double = Conversion.Val(modMain.KommazuPunkt(text)) - CDbl(modDeclares.SystemData.vorspann) / 100.0 - CDbl(modDeclares.SystemData.nachspann) / 100.0 - num8 * 3.0 / 1000.0
					Dim num As Integer = CInt((CDbl((modDeclares.imagecount + 1)) * num8 / (num9 * 1000.0)))
					Dim num2 As Integer = CInt(Math.Round(num9 * 1000.0 / num8))
					If CDbl(num) * (num9 * 1000.0) < CDbl((modDeclares.imagecount + 1)) * num8 Then
						' The following expression was wrapped in a unchecked-expression
						' The following expression was wrapped in a checked-expression
						num2 = CInt(Math.Round(CDbl((modDeclares.imagecount + 1)) - CDbl(num) * num9 * 1000.0 / num8))
						num += 1
					End If
					text6 = text2 + " = " + Conversions.ToString(num9) + "m    "
					text6 = String.Concat(New String() { text6, text3, " = ", Conversions.ToString(num8), "mm    " })
					text6 = String.Concat(New String() { text6, "# ", text4, " = ", Conversions.ToString(num), "    " })
					Dim num3 As Double = CDbl((num2 * 100)) / (num9 / (num8 / 1000.0))
					text6 = String.Concat(New String() { text6, text5, " : ", Conversions.ToString(num2), " (=", Support.Format(num3, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "%)" })
				End If
			End If
			Return text6
		End Function

		' Token: 0x06000E5C RID: 3676 RVA: 0x0008AF34 File Offset: 0x00089134
		Public Function IsValidExtension(ByRef fname As String) As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			If modDeclares.ExtCount = 0 Then
				result = True
			Else
				Dim left As String = Support.Format(Strings.Mid(fname, Strings.InStrRev(fname, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				Dim extCount As Integer = modDeclares.ExtCount
				For i As Integer = 1 To extCount
					If Operators.CompareString(left, modDeclares.Extensions(i), False) = 0 Then
						Return True
					End If
				Next
				result = False
			End If
			Return result
		End Function

		' Token: 0x06000E5D RID: 3677 RVA: 0x0008AF9C File Offset: 0x0008919C
		Public Sub ReadExtensions()
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim text2 As String = modMain.GiveIni(text, "SYSTEM", "Extensions")
			If Operators.CompareString(text2, "", False) = 0 Then
				modDeclares.ExtCount = 0
				Return
			End If
			Dim num As Integer = 1
			Dim flag As Boolean = False
			Do
				modDeclares.ExtCount += 1
				Dim num2 As Integer = Strings.InStr(num, text2, ";", Microsoft.VisualBasic.CompareMethod.Binary)
				If num2 > 1 Then
					modDeclares.Extensions(modDeclares.ExtCount) = Strings.Mid(text2, num, num2 - 1 - num + 1)
					num = num2 + 1
				Else
					modDeclares.Extensions(modDeclares.ExtCount) = Strings.Mid(text2, num)
					flag = True
				End If
			Loop While Not flag
		End Sub

		' Token: 0x06000E5E RID: 3678 RVA: 0x0008B048 File Offset: 0x00089248
		Public Function RemoveLeaderCharsFromFilenames(temp As String) As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			Dim num2 As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				Dim str As String = "0"
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + temp
				Dim num As Integer = CInt(Math.Round(Conversion.Val(str + modMain.GiveIni(text, "TEMPLATE", "IgnoreCharsCount"))))
				result = True
				ProjectData.ClearProjectError()
				num2 = 2
				Dim imagecount As Integer = modDeclares.imagecount
				For i As Integer = 0 To imagecount
					modDeclares.Images(i).DokumentName = Strings.Mid(modDeclares.Images(i).DokumentName, num + 1)
				Next
				IL_C1:
				GoTo IL_104
				IL_8C:
				result = False
				text = "RemoveLeaderCharsFromFilenames: " + Information.Err().Description
				Dim num3 As Short = 0S
				Dim text2 As String = "file-converter"
				modMain.msgbox2(text, num3, text2)
				ProjectData.ClearProjectError()
				num2 = 0
				GoTo IL_C1
				IL_C3:
				num4 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_D7:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_C3
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_104:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E5F RID: 3679 RVA: 0x0008B174 File Offset: 0x00089374
		Public Function WriteImageInfos() As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			Dim num As Integer
			Dim num3 As Integer
			Dim obj As Object
			Try
				result = True
				File.Delete(MyProject.Application.Info.DirectoryPath + "\LastLoadedImageStructure.txt")
				ProjectData.ClearProjectError()
				num = 2
				Using streamWriter As StreamWriter = New StreamWriter(MyProject.Application.Info.DirectoryPath + "\LastLoadedImageStructure.txt", True, Encoding.Unicode)
					streamWriter.WriteLine(modDeclares.imagecount)
					streamWriter.WriteLine(modDeclares.gllevel)
					Dim imagecount As Integer = modDeclares.imagecount
					For i As Integer = 0 To imagecount
						streamWriter.WriteLine(modDeclares.Images(i).Blip1Level)
						streamWriter.WriteLine(modDeclares.Images(i).Blip2Level)
						streamWriter.WriteLine(modDeclares.Images(i).Blip3Level)
						streamWriter.WriteLine(modDeclares.Images(i).count)
						streamWriter.WriteLine(modDeclares.Images(i).DokumentName)
						streamWriter.WriteLine(RuntimeHelpers.GetObjectValue(Interaction.IIf(modDeclares.Images(i).IsPDF, "1", "0")))
						streamWriter.WriteLine(CInt(modDeclares.Images(i).Level))
						streamWriter.WriteLine(modDeclares.Images(i).Name)
						streamWriter.WriteLine(modDeclares.Images(i).page)
						streamWriter.WriteLine(modDeclares.Images(i).PageCount)
					Next
					GoTo IL_1BC
				End Using
				IL_187:
				result = False
				Dim text As String = "WriteImageInfos: " + Information.Err().Description
				Dim num2 As Short = 0S
				Dim text2 As String = "file-converter"
				modMain.msgbox2(text, num2, text2)
				ProjectData.ClearProjectError()
				num = 0
				IL_1BC:
				GoTo IL_1FF
				IL_1BE:
				num3 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_1D2:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num3 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_1BE
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_1FF:
			If num3 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E60 RID: 3680 RVA: 0x0008B3C0 File Offset: 0x000895C0
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function ReadImageInfos() As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				Dim fileSystemObject As FileSystemObject = New FileSystemObjectClass()
				New frmImageXpress()
				MyProject.Forms.frmCheckImages.Show()
				Dim text As String
				MyProject.Forms.frmCheckImages.lblInfo.Text = text
				Application.DoEvents()
				result = True
				ProjectData.ClearProjectError()
				num = 2
				Using streamReader As StreamReader = New StreamReader(MyProject.Application.Info.DirectoryPath + "\LastLoadedImageStructure.txt", Encoding.Unicode)
					text = streamReader.ReadLine()
					modDeclares.imagecount = CInt(Math.Round(Conversion.Val(text)))
					text = streamReader.ReadLine()
					modDeclares.gllevel = CInt(Math.Round(Conversion.Val(text)))
					Dim num2 As Short
					If modDeclares.imagecount < 0 Then
						result = False
						FileSystem.FileClose(New Integer() { CInt(num2) })
						GoTo IL_3E1
					End If
					modDeclares.Images = New modDeclares.typImage(modDeclares.imagecount + 1 - 1) {}
					MyProject.Forms.frmCheckImages.lblDokumente.Text = "0"
					MyProject.Forms.frmCheckImages.lblStapel.Text = "0"
					Dim imagecount As Integer = modDeclares.imagecount
					For i As Integer = 0 To imagecount
						text = streamReader.ReadLine()
						modDeclares.Images(i).Blip1Level = CInt(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).Blip2Level = CInt(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).Blip3Level = CInt(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).count = CInt(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).DokumentName = text
						text = streamReader.ReadLine()
						modDeclares.Images(i).IsPDF = (Operators.CompareString(text, "1", False) = 0)
						text = streamReader.ReadLine()
						modDeclares.Images(i).Level = CShort(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).Name = text
						If Not fileSystemObject.FileExists(text) Then
							MyProject.Forms.frmErrorLoadingDocumentStructure.ShowDialog()
							result = False
							MyProject.Forms.frmCheckImages.Close()
							FileSystem.FileClose(New Integer() { CInt(num2) })
							GoTo IL_3E1
						End If
						text = streamReader.ReadLine()
						modDeclares.Images(i).page = CInt(Math.Round(Conversion.Val(text)))
						text = streamReader.ReadLine()
						modDeclares.Images(i).PageCount = CLng(Math.Round(Conversion.Val(text)))
						MyProject.Forms.frmCheckImages.lblImages.Text = Conversions.ToString(i)

							If modDeclares.Images(i).Level = 2S Then
								MyProject.Forms.frmCheckImages.lblDokumente.Text = Conversions.ToString(Conversion.Val(MyProject.Forms.frmCheckImages.lblDokumente.Text) + 1.0)
							End If
							If modDeclares.Images(i).Level = 3S Then
								MyProject.Forms.frmCheckImages.lblStapel.Text = Conversions.ToString(Conversion.Val(MyProject.Forms.frmCheckImages.lblStapel.Text) + 1.0)
							End If
							Application.DoEvents()

					Next
				End Using
				MyProject.Forms.frmCheckImages.Close()
				IL_3E1:
				GoTo IL_424
				IL_39D:
				MyProject.Forms.frmCheckImages.Close()
				result = False
				Dim text2 As String = "ReadImageInfos: " + Information.Err().Description
				Dim num3 As Short = 0S
				Dim text3 As String = "file-converter"
				modMain.msgbox2(text2, num3, text3)
				ProjectData.ClearProjectError()
				num = 0
				GoTo IL_3E1
				IL_3E3:
				num4 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_3F7:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_3E3
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_424:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E61 RID: 3681 RVA: 0x0008B830 File Offset: 0x00089A30
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub AddToErrorList(ByRef fname As String, ByRef page As Integer, ByRef error_Renamed As Integer)
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), MyProject.Application.Info.DirectoryPath + "\ERRORLIST.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
			FileSystem.PrintLine(CInt(num), New Object() { fname, page, error_Renamed })
			FileSystem.FileClose(New Integer() { CInt(num) })
		End Sub

		' Token: 0x06000E62 RID: 3682 RVA: 0x0008B89B File Offset: 0x00089A9B
		Public Sub ShowErrorList()
			Interaction.Shell("notepad.exe " + MyProject.Application.Info.DirectoryPath + "\ERRORLIST.TXT", AppWinStyle.MaximizedFocus, False, -1)
		End Sub

		' Token: 0x06000E63 RID: 3683 RVA: 0x0008B8C4 File Offset: 0x00089AC4
		Public Function fmax(ByRef X As Object, ByRef y As Object) As Object
			Dim objectValue As Object
			If Operators.ConditionalCompareObjectGreater(X, y, False) Then
				objectValue = RuntimeHelpers.GetObjectValue(X)
			Else
				objectValue = RuntimeHelpers.GetObjectValue(y)
			End If
			Return objectValue
		End Function

		' Token: 0x06000E64 RID: 3684 RVA: 0x0008B8F0 File Offset: 0x00089AF0
		Public Function GetAvailableMem() As Double
			' The following expression was wrapped in a checked-expression
			Return CULng(Math.Round(MyProject.Computer.Info.AvailablePhysicalMemory / 1024.0 / 1024.0)) / 1024.0
		End Function

		' Token: 0x06000E65 RID: 3685 RVA: 0x0008B938 File Offset: 0x00089B38
		Public Function BlockMemory(ByRef s As Integer) As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000E66 RID: 3686 RVA: 0x0008B948 File Offset: 0x00089B48
		Public Function FreeBlockedMemory() As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000E67 RID: 3687 RVA: 0x0008B958 File Offset: 0x00089B58
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub CheckTextFileVersion()
			' The following expression was wrapped in a checked-statement
			If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\fileconverter.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
				Dim str As String = Strings.Left("6.00.00-99 (12.02.2025)", 7)
				Dim num As Integer = CInt(Math.Round(Conversion.Val(Strings.Left(str, 1)) * 10000.0))
				num = CInt(Math.Round(CDbl(num) + Conversion.Val(Strings.Mid(str, 3, 2)) * 100.0))
				num = CInt(Math.Round(CDbl(num) + Conversion.Val(Strings.Mid(str, 6, 2))))
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\fileconverter.txt"
				Dim text2 As String = modMain.GiveIni(text, "VERSION", "VERSION")
				Dim num2 As Integer = 0
				If Strings.Len(text2) > 7 Then
					text2 = Strings.Left(text2, 7)
				End If
				If Strings.Len(text2) = 7 Then
					' The following expression was wrapped in a unchecked-expression
					num2 = CInt(Math.Round(Conversion.Val(Strings.Left(text2, 1)) * 10000.0))
					num2 = CInt(Math.Round(CDbl(num2) + Conversion.Val(Strings.Mid(text2, 3, 2)) * 100.0))
					num2 = CInt(Math.Round(CDbl(num2) + Conversion.Val(Strings.Mid(text2, 6, 2))))
				End If
				If num2 < num Then
					text = "The Text-File is outdated, please install a new one!"
					Dim num3 As Short = 64S
					Dim text3 As String = "file-converter"
					modMain.msgbox2(text, num3, text3)
				End If
			End If
		End Sub

		' Token: 0x06000E68 RID: 3688 RVA: 0x0008BAB5 File Offset: 0x00089CB5
		Private Function GetTotalFileCount2(ByRef path As String) As Integer
			Return Directory.GetFiles(path, "*.*", SearchOption.AllDirectories).Length
		End Function

		' Token: 0x06000E69 RID: 3689 RVA: 0x0008BAC8 File Offset: 0x00089CC8
		Private Function GetTotalFileCount(ByRef path As String) As Integer
			Dim num As Integer = 0
			Dim text As String = path + "\*.*"
			Dim win32_FIND_DATA As modDeclares.WIN32_FIND_DATA
			Dim hFindFile As Long = modDeclares.FindFirstFileW(text, win32_FIND_DATA)
			Dim num3 As Long
			Do
				' The following expression was wrapped in a unchecked-expression
				If(CULng(win32_FIND_DATA.dwFileAttributes) And 16UL) = 16UL Then
					If Operators.CompareString(modMain.trunc(win32_FIND_DATA.cFileName), ".", False) <> 0 And Operators.CompareString(modMain.trunc(win32_FIND_DATA.cFileName), "..", False) <> 0 Then
						Dim num2 As Integer = num
						Dim text2 As String = path + "\" + modMain.trunc(win32_FIND_DATA.cFileName)
						num = num2 + modMain.GetTotalFileCount(text2)
					End If
				Else
					Dim text2 As String = modMain.trunc(win32_FIND_DATA.cFileName)
					If modMain.IsValidExtension(text2) Then
						num += 1
					End If
				End If
				num3 = modDeclares.FindNextFile(hFindFile, win32_FIND_DATA)
			Loop While num3 <> 0L
			modDeclares.FindClose(hFindFile)
			Return num
		End Function

		' Token: 0x06000E6A RID: 3690 RVA: 0x0008BB94 File Offset: 0x00089D94
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub DummyLoad(ByRef n As String)
			Dim fixedLengthString As FixedLengthString = New FixedLengthString(10000)
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), n, OpenMode.Binary, OpenAccess.Read, OpenShare.[Default], 10000)
			While Not FileSystem.EOF(CInt(num))
				Dim fileNumber As Integer = CInt(num)
				Dim fixedLengthString2 As FixedLengthString = fixedLengthString
				Dim fixedLengthString3 As FixedLengthString = fixedLengthString2
				Dim value As String = fixedLengthString2.Value
				FileSystem.FileGet(fileNumber, value, -1L, False)
				fixedLengthString3.Value = value
			End While
			FileSystem.FileClose(New Integer() { CInt(num) })
		End Sub

		' Token: 0x06000E6B RID: 3691 RVA: 0x0008BBF8 File Offset: 0x00089DF8
		Public Function DuplexConversion(ByRef Abstand1 As Double, ByRef MaxLength As Double, ByRef DestPath As Object, ByRef DirName As String, ByRef sl As Boolean, ByRef bl As Boolean, ByRef reso As Integer) As Boolean
			Dim num2 As Integer
			Dim result As Boolean
			Dim num11 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim fileSystemObject As FileSystemObject = New FileSystemObjectClass()
				IL_09:
				ProjectData.ClearProjectError()
				num2 = 1
				IL_10:
				num = 3
				fileSystemObject.DeleteFolder(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName)), True)
				IL_32:
				num = 4
				If Not(Information.Err().Number <> 0 And Information.Err().Number <> 76) Then
					GoTo IL_C2
				End If
				IL_55:
				num = 5
				Interaction.MsgBox(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject("Ein Fehler (" + Information.Err().Number.ToString() + ") ist aufgetreten beim Löschen von <", DestPath), "\"), DirName), ">"), vbCr), "Die Duplex-Konvertierung kann nicht durchgeführt werden!"), MsgBoxStyle.OkOnly, Nothing)
				IL_B9:
				num = 6
				result = False
				GoTo IL_F25
				IL_C2:
				num = 8
				fileSystemObject.CreateFolder(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName)))
				IL_E4:
				ProjectData.ClearProjectError()
				num2 = 0
				IL_EB:
				num = 10
				Dim num3 As Integer = 0
				IL_F1:
				num = 11
				modDeclares.SystemData.PDFReso = reso
				IL_101:
				num = 12
				IL_104:
				num = 13
				Dim num4 As Integer = 0
				IL_10A:
				num = 14
				modMain.CancelDuplex = False
				IL_113:
				num = 15
				MyProject.Forms.frmDuplex.Show()
				IL_125:
				ProjectData.ClearProjectError()
				num2 = 2
				IL_12C:
				num = 17
				MyProject.Forms.frmDuplex.ProgressBar1.Maximum = modDeclares.imagecount + 1
				IL_14A:
				num = 18
				Dim fileSystemObject2 As FileSystemObject = New FileSystemObjectClass()
				IL_154:
				num = 19
				fileSystemObject2.DeleteFolder(modDeclares.SystemData.PDFKONVERTERTEMP, False)
				Dim description As String
				Dim text As String
				Do
					IL_169:
					num = 21
					MyProject.Forms.frmDuplex.ProgressBar1.Value = num3
					IL_182:
					num = 22
					MyProject.Forms.frmDuplex.lblCount.Text = Conversions.ToString(num3) + "/" + Conversions.ToString(modDeclares.imagecount + 1)
					IL_1B6:
					num = 23
					Application.DoEvents()
					IL_1BE:
					num = 24
					If num3 = 320 Then
						IL_1CA:
						num = 25
						num3 = 320
					End If
					IL_1D4:
					num = 26
					Dim dokumentName As String
					If modDeclares.Images(num3).Level = 2S Then
						IL_1EE:
						num = 27
						dokumentName = modDeclares.Images(num3).DokumentName
						IL_204:
						ProjectData.ClearProjectError()
						num2 = 1
						IL_20B:
						num = 29
						fileSystemObject.DeleteFolder(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName)), True)
						IL_23F:
						num = 30
						fileSystemObject.CreateFolder(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName)))
					End If
					IL_273:
					num = 31
					Dim num5 As Integer
					If modDeclares.Images(num3).IsPDF Then
						IL_289:
						num = 32
						num5 = modDeclares.SystemData.PDFReso
						IL_298:
						num = 33
						MyProject.Forms.frmImageXpress.OpenPDFDocumentAlt(modDeclares.Images(num3).Name, modDeclares.Images(num3).page, modDeclares.SystemData.PDFReso, modMain.glImage)
					Else
						IL_2DE:
						num = 35
						Dim path As String
						MyProject.Forms.frmImageXpress.NumPages(path)
					End If
					IL_2F3:
					num = 36
					Dim flag As Boolean = True
					IL_2F9:
					num = 37

						Dim num6 As Long
						If CDbl(num6) / CDbl(num5) * 25.4 > MaxLength Then
							IL_311:
							num = 38
							flag = False
						Else
							IL_319:
							num = 40
							Dim num7 As Long
							If CDbl(num7) / CDbl(num5) * 25.4 > MaxLength Then
								IL_331:
								num = 41
								flag = False
							End If
						End If
						IL_337:
						num = 42

					If Not flag Then
						IL_341:
						num = 43
						num4 += 1
						IL_34A:
						num = 44
						modDeclares.Images(num4 - 1).IsPDF = False
						IL_361:
						num = 45
						modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3).Level
						IL_388:
						num = 46
						modDeclares.Images(num4 - 1).page = 1
						IL_39F:
						num = 47
						modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
						IL_418:
						num = 48
						If MyProject.Forms.frmImageXpress.IBPP > 1L Then
							IL_42E:
							num = 49
							MyProject.Forms.frmImageXpress.SaveRasterFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP")), 0L)
						Else
							IL_48E:
							num = 51
							MyProject.Forms.frmImageXpress.SaveRasterFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP")), 1L)
						End If
						IL_4EC:
						num = 52
						num3 += 1
					Else
						IL_4FA:
						num = 54
						If MyProject.Forms.frmImageXpress.IWidth > MyProject.Forms.frmImageXpress.IHeight Then
							IL_51D:
							num = 55
							If sl Then
								IL_525:
								num = 56
								modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
							Else
								IL_535:
								num = 58
								modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
							End If
						End If
						IL_543:
						num = 59
						Dim path2 As String = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
						IL_561:
						num = 60
						Dim t As Long
						If MyProject.Forms.frmImageXpress.IBPP > 1L Then
							IL_577:
							num = 61
							t = 0L
						Else
							IL_580:
							num = 63
							t = 1L
						End If
						IL_587:
						num = 64
						MyProject.Forms.frmImageXpress.SaveRasterFile(path2, t)
						IL_59E:
						num = 65
						If num3 + 1 > modDeclares.imagecount Then
							IL_5AF:
							num = 66
							num4 += 1
							IL_5B8:
							num = 67
							description = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
							text = ""
							Dim text2 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP"))
							Dim num8 As Double
							modMain.MakeDuplexNet(description, text, text2, num8)
							IL_636:
							num = 68
							modDeclares.Images(num4 - 1).IsPDF = False
							IL_64D:
							num = 69
							modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3).Level
							IL_674:
							num = 70
							modDeclares.Images(num4 - 1).page = 1
							IL_68B:
							num = 71
							modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
							IL_704:
							num = 72
							num3 += 1
						Else
							IL_712:
							num = 74
							num3 += 1
							IL_71B:
							num = 75
							If modDeclares.Images(num3).Level = 2S Then
								IL_735:
								num = 76
								num4 += 1
								IL_73E:
								num = 77
								Dim text2 As String = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
								text = ""
								description = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP"))
								Dim num8 As Double
								modMain.MakeDuplexNet(text2, text, description, num8)
								IL_7BC:
								num = 78
								modDeclares.Images(num4 - 1).IsPDF = False
								IL_7D3:
								num = 79
								modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3 - 1).Level
								IL_7FC:
								num = 80
								modDeclares.Images(num4 - 1).page = 1
								IL_813:
								num = 81
								modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
							Else
								IL_891:
								num = 83
								If modDeclares.Images(num3).IsPDF Then
									IL_8A7:
									num = 84
									MyProject.Forms.frmImageXpress.OpenPDFDocumentAlt(modDeclares.Images(num3).Name, modDeclares.Images(num3).page, modDeclares.SystemData.PDFReso, modMain.glImage)
									IL_8EB:
									num = 85
									num5 = modDeclares.SystemData.PDFReso
								Else
									IL_8FC:
									num = 87
									num5 = CInt(MyProject.Forms.frmImageXpress.IResX)
								End If
								IL_911:
								num = 88
								flag = True
								IL_917:
								num = 89

									If CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(num5) * 25.4 > MaxLength Then
										IL_93C:
										num = 90
										flag = False
									Else
										IL_944:
										num = 92
										If CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(num5) * 25.4 > MaxLength Then
											IL_969:
											num = 93
											flag = False
										End If
									End If
									IL_96F:
									num = 94

								If Not flag Then
									IL_979:
									num = 95
									num4 += 1
									IL_982:
									num = 96
									Dim num8 As Double = Abstand1 / 25.4 * CDbl(num5)
									IL_997:
									num = 97
									description = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
									text = ""
									Dim text2 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP"))
									modMain.MakeDuplexNet(description, text, text2, num8)
									IL_A15:
									num = 98
									modDeclares.Images(num4 - 1).IsPDF = False
									IL_A2C:
									num = 99
									modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3 - 1).Level
									IL_A55:
									num = 100
									modDeclares.Images(num4 - 1).page = 1
									IL_A6C:
									num = 101
									modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
									IL_AE5:
									num = 102
									num4 += 1
									IL_AEE:
									num = 103
									path2 = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP"))
									IL_B3C:
									num = 104
									modDeclares.Images(num4 - 1).IsPDF = False
									IL_B53:
									num = 105
									modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3 - 1).Level
									IL_B7C:
									num = 106
									modDeclares.Images(num4 - 1).page = 1
									IL_B93:
									num = 107
									modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
									IL_C0C:
									num = 108
									If MyProject.Forms.frmImageXpress.IBPP > 1L Then
										IL_C22:
										num = 109
										t = 0L
									Else
										IL_C2B:
										num = 111
										t = 1L
									End If
									IL_C32:
									num = 112
									MyProject.Forms.frmImageXpress.SaveRasterFile(path2, t)
									IL_C49:
									num = 113
									num3 += 1
								Else
									IL_C57:
									num = 115
									If MyProject.Forms.frmImageXpress.IWidth > MyProject.Forms.frmImageXpress.IHeight Then
										IL_C7A:
										num = 116
										If sl Then
											IL_C82:
											num = 117
											MyProject.Forms.frmImageXpress.Rotate(90L)
										Else
											IL_C9A:
											num = 119
											MyProject.Forms.frmImageXpress.Rotate(-90L)
										End If
									End If
									IL_CB0:
									num = 120
									path2 = MyProject.Application.Info.DirectoryPath + "\DUPLEX.JPG"
									IL_CCE:
									num = 121
									num4 += 1
									IL_CD7:
									num = 122
									If MyProject.Forms.frmImageXpress.IBPP > 1L Then
										IL_CED:
										num = 123
										t = 0L
									Else
										IL_CF6:
										num = 125
										t = 1L
									End If
									IL_CFD:
									num = 126
									Dim num8 As Double = Abstand1 / 25.4 * CDbl(num5)
									IL_D12:
									num = 127
									If num3 = 321 Then
										IL_D1E:
										num = 128
										num3 = 321
									End If
									IL_D2B:
									num = 129
									Dim text2 As String = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
									text = MyProject.Application.Info.DirectoryPath + "\DUPLEX.JPG"
									description = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num4), ".DUP"))
									modMain.MakeDuplexNet(text2, text, description, num8)
									IL_DC0:
									num = 130
									modDeclares.Images(num4 - 1).IsPDF = False
									IL_DDA:
									num = 131
									modDeclares.Images(num4 - 1).Level = modDeclares.Images(num3 - 1).Level
									IL_E06:
									num = 132
									modDeclares.Images(num4 - 1).page = 1
									IL_E20:
									num = 133
									modDeclares.Images(num4 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num4), ".DUP"))
									IL_E9C:
									num = 134
									num3 += 1
								End If
							End If
						End If
					End If
					IL_EA8:
					num = 135
				Loop While num3 <= modDeclares.imagecount
				IL_EBA:
				num = 136
				MyProject.Forms.frmDuplex.Close()
				IL_ECF:
				num = 137
				modDeclares.imagecount = num4 - 1
				IL_F25:
				GoTo IL_11AF
				IL_EE0:
				num = 139
				Dim errObject As ErrObject = Information.Err()
				description = errObject.Description
				Dim num9 As Short = 0S
				text = "file-converter"
				modMain.msgbox2(description, num9, text)
				errObject.Description = description
				IL_F10:
				num = 140
				MyProject.Forms.frmDuplex.Close()
				GoTo IL_F25
				IL_F2A:
				Dim num10 As Integer = num11 + 1
				num11 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num10)
				IL_116C:
				GoTo IL_11A4
				IL_116E:
				num11 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_1182:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num11 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_116E
			End Try
			IL_11A4:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_11AF:
			If num11 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E6C RID: 3692 RVA: 0x0008CDDC File Offset: 0x0008AFDC
		Public Function DuplexConversionNet(ByRef Abstand1 As Double, ByRef MaxLength As Double, ByRef DestPath As Object, ByRef DirName As String, ByRef sl As Boolean, ByRef bl As Boolean, ByRef reso As Integer) As Boolean
			Dim num2 As Integer
			Dim result As Boolean
			Dim num21 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				New FileSystemObjectClass()
				IL_08:
				num = 2
				Dim imagecount As Integer = modDeclares.imagecount
				Dim i As Integer
				i = 0
				While i <= imagecount
					IL_16:
					num = 3
					modDeclares.Images(i).NameSaved = modDeclares.Images(i).Name
					IL_3A:
					num = 4
					i += 1
				End While
				IL_48:
				ProjectData.ClearProjectError()
				num2 = 1
				IL_4F:
				num = 6
				modMain.DeleteTempFiles(modDeclares.SystemData.PDFKONVERTERTEMP)
				IL_60:
				num = 7
				If Not Directory.Exists(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName))) Then
					GoTo IL_1A3
				End If
				IL_84:
				num = 8
				Dim flag As Boolean = False
				IL_89:
				num = 9
				Dim num3 As Integer = 10
				While True
					IL_90:
					num = 11
					Application.DoEvents()
					IL_98:
					num = 12
					Thread.Sleep(250)
					IL_A5:
					num = 13
					Directory.Delete(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName)), True)
					IL_C6:
					num = 14
					If Information.Err().Number <> 0 And Information.Err().Number <> 76 Then
						IL_ED:
						num = 15
						num3 -= 1
						IL_F6:
						num = 16
						If num3 = 0 Then
							Exit For
						End If
					Else
						IL_193:
						num = 21
						flag = True
					End If
					IL_199:
					num = 22
					If flag Then
						GoTo IL_1A3
					End If
				End While
				IL_100:
				num = 17
				Dim array As String() = New String(4) {}
				array(0) = "Ein Fehler ("
				Dim num4 As Integer = 1
				Dim num5 As Integer = Information.Err().Number
				array(num4) = num5.ToString()
				array(2) = ","
				array(3) = Information.Err().Description
				array(4) = ") ist aufgetreten beim Löschen von <"
				Interaction.MsgBox(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(String.Concat(array), DestPath), "\"), DirName), ">"), vbCr), "Die Duplex-Konvertierung kann nicht durchgeführt werden!"), MsgBoxStyle.OkOnly, Nothing)
				IL_189:
				num = 18
				result = False
				GoTo IL_174D
				IL_1A3:
				num = 23
				Directory.CreateDirectory(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName)))
				IL_1C4:
				ProjectData.ClearProjectError()
				num2 = 0
				IL_1CB:
				num = 25
				i = 0
				IL_1D1:
				num = 26
				modDeclares.SystemData.PDFReso = reso
				IL_1E1:
				num = 27
				IL_1E4:
				num = 28
				Dim num6 As Integer = 0
				IL_1EA:
				num = 29
				modMain.CancelDuplex = False
				IL_1F3:
				num = 30
				MyProject.Forms.frmDuplex.Show()
				IL_205:
				num = 31
				MyProject.Forms.frmDuplex.ProgressBar1.Maximum = modDeclares.imagecount + 1
				While True
					IL_373:
					num = 50
					If num6 Mod 50 = 0 Then
						IL_37D:
						num = 51
						GC.Collect()
					End If
					IL_385:
					num = 52
					If Not Information.IsNothing(modMain.glImage) Then
						IL_394:
						num = 53
						modMain.glImage.Dispose()
					End If
					IL_3A1:
					num = 54
					Dim bitmap As Bitmap
					If Not Information.IsNothing(bitmap) Then
						IL_3AD:
						num = 55
						bitmap.Dispose()
					End If
					IL_3B7:
					num = 56
					Dim bitmap2 As Bitmap
					If Not Information.IsNothing(bitmap2) Then
						IL_3C3:
						num = 57
						bitmap2.Dispose()
					End If
					IL_3CD:
					num = 58
					If modMain.CancelDuplex Then
						Exit For
					End If
					IL_3F3:
					num = 62
					MyProject.Forms.frmDuplex.ProgressBar1.Value = i
					IL_40C:
					num = 63
					MyProject.Forms.frmDuplex.lblCount.Text = Conversions.ToString(i) + "/" + Conversions.ToString(modDeclares.imagecount + 1)
					IL_440:
					num = 64
					Application.DoEvents()
					IL_448:
					num = 65
					If i = 320 Then
						IL_454:
						num = 66
						i = 320
					End If
					IL_45E:
					num = 67
					Dim dokumentName As String
					If modDeclares.Images(i).Level = 2S Then
						IL_478:
						num = 68
						dokumentName = modDeclares.Images(i).DokumentName
						IL_48E:
						ProjectData.ClearProjectError()
						num2 = 1
						IL_495:
						num = 70
						If Directory.Exists(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName))) Then
							IL_4C8:
							num = 71
							Directory.Delete(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName)), True)
						End If
						IL_4FA:
						num = 72
						Directory.CreateDirectory(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName)))
					End If
					IL_52C:
					num = 73
					Dim num7 As Integer
					Dim num10 As Long
					Dim num11 As Long
					Dim sim As String
					Dim dup As String
					Dim flag2 As Boolean

						If modDeclares.Images(i).IsPDF Then
							IL_545:
							num = 74
							num7 = modDeclares.SystemData.PDFReso
							IL_554:
							num = 75
							Dim frmImageXpress As frmImageXpress = MyProject.Forms.frmImageXpress
							Dim images As modDeclares.typImage() = modDeclares.Images
							Dim num8 As Integer = i
							Dim images2 As modDeclares.typImage() = modDeclares.Images
							Dim num9 As Integer = i
							Dim image As Image = bitmap
							frmImageXpress.OpenPDFDocumentAlt(images(num8).Name, images2(num9).page, modDeclares.SystemData.PDFReso, image)
							bitmap = CType(image, Bitmap)
							IL_5A2:
							num = 76
							bitmap = New Bitmap(modMain.glImage)
							IL_5B1:
							num = 77
							modMain.glImage.Dispose()
							IL_5BE:
							num = 78
							num7 = modDeclares.SystemData.PDFReso
							IL_5CD:
							num = 79
							bitmap.SetResolution(CSng(num7), CSng(num7))
							IL_5DD:
							num = 80
							num10 = CLng(bitmap.Width)
							IL_5EA:
							num = 81
							num11 = CLng(bitmap.Height)
						Else
							IL_5FC:
							num = 83
							If modDeclares.Images(i).page = 1 Then
								IL_613:
								num = 84
								bitmap = CType(Image.FromFile(modDeclares.Images(i).Name), Bitmap)
								IL_633:
								num = 85
								num7 = CInt(Math.Round(CDbl(bitmap.VerticalResolution)))
							Else
								IL_648:
								num = 87
								MyProject.Forms.frmImageXpress.OpenRasterDocument(modDeclares.Images(i).Name, modDeclares.Images(i).page)
								IL_67D:
								num = 88
								bitmap = New Bitmap(modMain.glImage)
								IL_68C:
								num = 89
								num7 = CInt(Math.Round(CDbl(modMain.glImage.VerticalResolution)))
								IL_6A2:
								num = 90
								bitmap.SetResolution(CSng(num7), CSng(num7))
								IL_6B2:
								num = 91
								modMain.glImage.Dispose()
							End If
							IL_6BF:
							num = 92
							num10 = CLng(bitmap.Width)
							IL_6CC:
							num = 93
							num11 = CLng(bitmap.Height)
						End If
						IL_6D9:
						num = 94
						sim = Strings.Mid(modDeclares.Images(i).NameSaved, Strings.InStrRev(modDeclares.Images(i).NameSaved, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						IL_713:
						num = 95
						dup = ""
						IL_71D:
						num = 96
						flag2 = True
						IL_723:
						num = 97
						If CDbl(num10) / CDbl(num7) * 25.4 > MaxLength Then
							IL_73B:
							num = 98
							flag2 = False
						Else
							IL_743:
							num = 100
							If CDbl(num11) / CDbl(num7) * 25.4 > MaxLength Then
								IL_75B:
								num = 101
								flag2 = False
							End If
						End If
						IL_761:
						num = 102

					If Not flag2 Then
						IL_76B:
						num = 103
						num6 += 1
						IL_774:
						num = 104
						modDeclares.Images(num6 - 1).IsPDF = False
						IL_78B:
						num = 105
						modDeclares.Images(num6 - 1).Level = modDeclares.Images(i).Level
						IL_7B2:
						num = 106
						modDeclares.Images(num6 - 1).page = 1
						IL_7C9:
						num = 107
						modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
						IL_842:
						num = 108
						modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP")), sim, dup)
						IL_897:
						num = 109
						If MyProject.Forms.frmImageXpress.IBPP > 1L Then
							IL_8AD:
							num = 110
							NewLateBinding.LateCall(bitmap, Nothing, "Save", New Object() { Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"), ImageFormat.Tiff }, Nothing, Nothing, Nothing, True)
						Else
							IL_919:
							num = 112
							NewLateBinding.LateCall(bitmap, Nothing, "Save", New Object() { Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"), ImageFormat.Tiff }, Nothing, Nothing, Nothing, True)
						End If
						IL_983:
						num = 113
						i += 1
					Else
						IL_991:
						num = 115
						If num10 > num11 Then
							IL_99A:
							num = 116
							If sl Then
								IL_9A2:
								num = 117
								bitmap.RotateFlip(RotateFlipType.Rotate90FlipNone)
							Else
								IL_9AF:
								num = 119
								bitmap.RotateFlip(RotateFlipType.Rotate270FlipNone)
							End If
						End If
						IL_9BA:
						num = 120
						Dim text As String = MyProject.Application.Info.DirectoryPath + "\SIMPLEX.JPG"
						IL_9D8:
						num = 121
						If MyProject.Forms.frmImageXpress.IBPP > 1L Then
							IL_9EE:
							num = 122
						Else
							IL_9F3:
							num = 124
						End If
						IL_9F6:
						num = 125
						If i + 1 > modDeclares.imagecount Then
							IL_A07:
							num = 126
							num6 += 1
							IL_A10:
							num = 127
							Dim text2 As String = ""
							Dim text3 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"))
							Dim num12 As Double
							modMain.MakeDuplexNeti(text, bitmap, text2, bitmap2, text3, num12, CSng(num7))
							IL_A7A:
							num = 128
							modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP")), sim, "")
							IL_AD5:
							num = 129
							modDeclares.Images(num6 - 1).IsPDF = False
							IL_AEF:
							num = 130
							modDeclares.Images(num6 - 1).Level = modDeclares.Images(i).Level
							IL_B19:
							num = 131
							modDeclares.Images(num6 - 1).page = 1
							IL_B33:
							num = 132
							modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
							IL_BAF:
							num = 133
							i += 1
						Else
							IL_BC0:
							num = 135
							i += 1
							IL_BCC:
							num = 136
							If modDeclares.Images(i).Level = 2S Then
								IL_BE9:
								num = 137
								num6 += 1
								IL_BF5:
								num = 138
								Dim text3 As String = ""
								Dim text2 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"))
								Dim num12 As Double
								modMain.MakeDuplexNeti(text, bitmap, text3, bitmap2, text2, num12, CSng(num7))
								IL_C62:
								num = 139
								modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP")), sim, "")
								IL_CBD:
								num = 140
								modDeclares.Images(num6 - 1).IsPDF = False
								IL_CD7:
								num = 141
								modDeclares.Images(num6 - 1).Level = modDeclares.Images(i - 1).Level
								IL_D03:
								num = 142
								modDeclares.Images(num6 - 1).page = 1
								IL_D1D:
								num = 143
								modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
							Else
								IL_D9E:
								num = 145
								dup = modDeclares.Images(i).DokumentName
								IL_DB7:
								num = 146
								dup = Strings.Mid(modDeclares.Images(i).NameSaved, Strings.InStrRev(modDeclares.Images(i).NameSaved, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
								IL_DF4:
								num = 147

									If modDeclares.Images(i).IsPDF Then
										IL_E10:
										num = 148
										Dim frmImageXpress2 As frmImageXpress = MyProject.Forms.frmImageXpress
										Dim images3 As modDeclares.typImage() = modDeclares.Images
										Dim num13 As Integer = i
										Dim images4 As modDeclares.typImage() = modDeclares.Images
										Dim num14 As Integer = i
										Dim image As Image = bitmap2
										frmImageXpress2.OpenPDFDocumentAlt(images3(num13).Name, images4(num14).page, modDeclares.SystemData.PDFReso, image)
										bitmap2 = CType(image, Bitmap)
										IL_E61:
										num = 149
										bitmap2 = New Bitmap(modMain.glImage)
										IL_E73:
										num = 150
										modMain.glImage.Dispose()
										IL_E83:
										num = 151
										num7 = modDeclares.SystemData.PDFReso
										IL_E95:
										num = 152
										bitmap2.SetResolution(CSng(num7), CSng(num7))
										IL_EA8:
										num = 153
										num10 = CLng(bitmap2.Width)
										IL_EB8:
										num = 154
										num11 = CLng(bitmap2.Height)
									Else
										IL_ECD:
										num = 156
										If modDeclares.Images(i).page = 1 Then
											IL_EE7:
											num = 157
											bitmap2 = CType(Image.FromFile(modDeclares.Images(i).Name), Bitmap)
											IL_F0A:
											num = 158
											num7 = CInt(Math.Round(CDbl(bitmap2.VerticalResolution)))
										Else
											IL_F25:
											num = 160
											MyProject.Forms.frmImageXpress.OpenRasterDocument(modDeclares.Images(i).Name, modDeclares.Images(i).page)
											IL_F5D:
											num = 161
											bitmap2 = New Bitmap(modMain.glImage)
											IL_F6F:
											num = 162
											num7 = CInt(MyProject.Forms.frmImageXpress.IResX)
											IL_F87:
											num = 163
											bitmap2.SetResolution(CSng(num7), CSng(num7))
											IL_F9A:
											num = 164
											modMain.glImage.Dispose()
										End If
										IL_FAA:
										num = 165
										num10 = CLng(bitmap2.Width)
										IL_FBA:
										num = 166
										num11 = CLng(bitmap2.Height)
									End If
									IL_FCA:
									num = 167
									flag2 = True
									IL_FD3:
									num = 168
									If CDbl(num10) / CDbl(num7) * 25.4 > MaxLength Then
										IL_FEE:
										num = 169
										flag2 = False
									Else
										IL_FF9:
										num = 171
										If CDbl(num11) / CDbl(num7) * 25.4 > MaxLength Then
											IL_1014:
											num = 172
											flag2 = False
										End If
									End If
									IL_101D:
									num = 173

								If Not flag2 Then
									IL_102A:
									num = 174
									num6 += 1
									IL_1036:
									num = 175
									Dim num12 As Double = Abstand1 / 25.4 * CDbl(num7)
									IL_104E:
									num = 176
									Dim text2 As String = ""
									Dim text3 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"))
									modMain.MakeDuplexNeti(text, bitmap, text2, bitmap2, text3, num12, CSng(num7))
									IL_10BB:
									num = 177
									modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP")), sim, "")
									IL_1116:
									num = 178
									modDeclares.Images(num6 - 1).IsPDF = False
									IL_1130:
									num = 179
									modDeclares.Images(num6 - 1).Level = modDeclares.Images(i - 1).Level
									IL_115C:
									num = 180
									modDeclares.Images(num6 - 1).page = 1
									IL_1176:
									num = 181
									modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
									IL_11F2:
									num = 182
									num6 += 1
									IL_11FE:
									num = 183
									Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"))
									IL_124E:
									num = 184
									modDeclares.Images(num6 - 1).IsPDF = False
									IL_1268:
									num = 185
									modDeclares.Images(num6 - 1).Level = modDeclares.Images(i - 1).Level
									IL_1294:
									num = 186
									modDeclares.Images(num6 - 1).page = 1
									IL_12AE:
									num = 187
									modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
									IL_132A:
									num = 188
									If MyProject.Forms.frmImageXpress.IBPP > 1L Then
										IL_1343:
										num = 189
									Else
										IL_134B:
										num = 191
									End If
									IL_1351:
									num = 192
									NewLateBinding.LateCall(bitmap2, Nothing, "Save", New Object() { Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"), ImageFormat.Tiff }, Nothing, Nothing, Nothing, True)
									IL_13BE:
									num = 193
									sim = modDeclares.Images(i).DokumentName
									IL_13D7:
									num = 194
									sim = Strings.Mid(modDeclares.Images(i).NameSaved, Strings.InStrRev(modDeclares.Images(i).NameSaved, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
									IL_1414:
									num = 195
									modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP")), sim, "")
									IL_1489:
									num = 196
									i += 1
								Else
									IL_149A:
									num = 198
									If num10 > num11 Then
										IL_14A6:
										num = 199
										If sl Then
											IL_14B1:
											num = 200
											bitmap2.RotateFlip(RotateFlipType.Rotate90FlipNone)
										Else
											IL_14C1:
											num = 202
											bitmap2.RotateFlip(RotateFlipType.Rotate270FlipNone)
										End If
									End If
									IL_14CF:
									num = 203
									Dim text4 As String = MyProject.Application.Info.DirectoryPath + "\DUPLEX.JPG"
									IL_14F0:
									num = 204
									num6 += 1
									IL_14FC:
									num = 205
									If MyProject.Forms.frmImageXpress.IBPP > 1L Then
										IL_1515:
										num = 206
									Else
										IL_151D:
										num = 208
									End If
									IL_1523:
									num = 209
									Dim num12 As Double = Abstand1 / 25.4 * CDbl(num7)
									IL_153B:
									num = 210
									If i = 321 Then
										IL_154A:
										num = 211
										i = 321
									End If
									IL_1557:
									num = 212
									Dim text3 As String = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), dokumentName), "\"), num6), ".DUP"))
									modMain.MakeDuplexNeti(text, bitmap, text4, bitmap2, text3, num12, CSng(num7))
									IL_15BD:
									num = 213
									modMain.CreateAnnoFile(Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP")), sim, dup)
									IL_162F:
									num = 214
									modDeclares.Images(num6 - 1).IsPDF = False
									IL_1649:
									num = 215
									modDeclares.Images(num6 - 1).Level = modDeclares.Images(i - 1).Level
									IL_1675:
									num = 216
									modDeclares.Images(num6 - 1).page = 1
									IL_168F:
									num = 217
									modDeclares.Images(num6 - 1).Name = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(DestPath, "\"), DirName), "\"), Interaction.IIf(Operators.CompareString(dokumentName, "", False) = 0, "", dokumentName + "\")), num6), ".DUP"))
									IL_170B:
									num = 218
									i += 1
								End If
							End If
						End If
					End If
					IL_1717:
					num = 219
					If i > modDeclares.imagecount Then
						GoTo IL_1729
					End If
				End While
				IL_3D7:
				num = 59
				MyProject.Forms.frmDuplex.Close()
				IL_3E9:
				num = 60
				result = False
				GoTo IL_174D
				IL_1729:
				num = 220
				MyProject.Forms.frmDuplex.Close()
				IL_173E:
				num = 221
				modDeclares.imagecount = num6 - 1
				IL_174D:
				GoTo IL_1B17
				IL_228:
				num = 33
				Dim num15 As Long = 10L
				IL_230:
				num = 34
				Dim num16 As Long = 1L
				IL_237:
				num = 35
				Dim num17 As Long = CLng(Math.Round(CDbl(modDeclares.imagecount) / CDbl(num15)))
				IL_24C:
				num = 36
				num5 = modDeclares.imagecount
				Dim num18 As Integer = CInt(num17)
				i = 1
				GoTo IL_2BA
				IL_260:
				num = 37
				num16 += 1L
				IL_26A:
				num = 38
				Process.Start(Application.StartupPath + "\MakeDuplexFast.exe", "d:\Images\TestMario\1-DUPLEX_DIN_A4_5000-Seiten_tiffs\ h:\temp\DUPLEXIMAGES\ " + Conversions.ToString(i) + " " + Conversions.ToString(Math.Min(CLng(i) + num17, CLng((modDeclares.imagecount + 1)))))
				IL_2B0:
				num = 39
				i += num18
				IL_2BA:
				If(num18 >> 31 Xor i) <= (num18 >> 31 Xor num5) Then
					GoTo IL_260
				End If
				IL_2CC:
				num = 40
				Dim flag3 As Boolean = False
				IL_2D2:
				num = 42
				Dim num19 As Integer = Directory.GetFiles("h:\temp\DUPLEXIMAGES", "*.DUP").Length
				IL_2E8:
				num = 43
				MyProject.Forms.frmDuplex.ProgressBar1.Value = num19 * 2
				IL_303:
				num = 44
				MyProject.Forms.frmDuplex.lblCount.Text = (num19 * 2).ToString() + "/" + (modDeclares.imagecount + 1).ToString()
				IL_341:
				num = 45
				If CDbl(num19) <> CDbl((modDeclares.imagecount + 1)) / 2.0 Then
					GoTo IL_361
				End If
				IL_35B:
				num = 46
				flag3 = True
				IL_361:
				num = 47
				Application.DoEvents()
				IL_369:
				num = 48
				If Not flag3 Then
					GoTo IL_2D2
				End If
				GoTo IL_373
				IL_1752:
				Dim num20 As Integer = num21 + 1
				num21 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num20)
				IL_1AD8:
				GoTo IL_1B0C
				IL_1ADA:
				num21 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_1AEA:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num21 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_1ADA
			End Try
			IL_1B0C:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_1B17:
			If num21 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E6D RID: 3693 RVA: 0x0008E928 File Offset: 0x0008CB28
		Public Function MakeDuplexNet(ByRef fnamesim As String, ByRef fnamedup As String, ByRef fnamedest As String, ByRef Abstand As Double) As Integer
			Dim num As Integer
			Dim result As Integer
			Dim num18 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				New modDeclares.AT_RGBQUAD(256) {}
				IL_14:
				num2 = 3
				result = -1
				IL_18:
				num2 = 4
				Dim image As Image = Image.FromFile(fnamesim)
				IL_23:
				num2 = 5
				Dim num3 As Double = CDbl(image.HorizontalResolution)
				IL_2F:
				num2 = 6
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_4B
				End If
				IL_40:
				num2 = 7
				Dim image2 As Image = Image.FromFile(fnamedup)
				IL_4B:
				num2 = 8
				Dim num4 As Integer = 0
				IL_50:
				num2 = 9
				Dim num5 As Integer = 0
				IL_56:
				num2 = 10
				Dim width As Integer = image.Width
				IL_62:
				num2 = 11
				Dim height As Integer = image.Height
				IL_6E:
				num2 = 12
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_27E
				End If
				IL_83:
				num2 = 13
				Dim num6 As Integer = image2.Width
				IL_8F:
				num2 = 14
				Dim height2 As Integer = image2.Height
				IL_9B:
				num2 = 15
				If CInt(Math.Round(CDbl(image.HorizontalResolution) + 0.5)) = CInt(Math.Round(CDbl(image2.HorizontalResolution) + 0.5)) Then
					GoTo IL_483
				End If
				IL_D3:
				num2 = 16
				If CInt(Math.Round(CDbl(image.HorizontalResolution) + 0.5)) <= CInt(Math.Round(CDbl(image2.HorizontalResolution) + 0.5)) Then
					GoTo IL_1A2
				End If
				IL_10B:
				num2 = 17
				image2 = modPaint.ResizeImage(CType(image2, Bitmap), CInt(Math.Round(CDbl((CSng(image2.Width) * image.HorizontalResolution / image2.HorizontalResolution)))), CInt(Math.Round(CDbl((CSng(image2.Height) * image.HorizontalResolution / image2.HorizontalResolution)))))
				IL_15A:
				num2 = 18
				Dim bitmap As Bitmap = New Bitmap(image2)
				IL_166:
				num2 = 19
				bitmap.SetResolution(image.HorizontalResolution, image.HorizontalResolution)
				IL_17E:
				num2 = 20
				image2 = bitmap
				IL_185:
				num2 = 21
				num6 = image2.Width
				IL_191:
				num2 = 22
				height2 = image2.Height
				GoTo IL_483
				IL_1A2:
				num2 = 24
				If CInt(Math.Round(CDbl(image.HorizontalResolution) + 0.5)) >= CInt(Math.Round(CDbl(image2.HorizontalResolution) + 0.5)) Then
					GoTo IL_483
				End If
				IL_1DA:
				num2 = 25
				image = modPaint.ResizeImage(CType(image, Bitmap), CInt(Math.Round(CDbl((CSng(image.Width) * image2.HorizontalResolution / image.HorizontalResolution)))), CInt(Math.Round(CDbl((CSng(image.Height) * image2.HorizontalResolution / image.HorizontalResolution)))))
				IL_229:
				num2 = 26
				Dim bitmap2 As Bitmap = New Bitmap(image)
				IL_235:
				num2 = 27
				bitmap2.SetResolution(image2.HorizontalResolution, image2.HorizontalResolution)
				IL_24D:
				num2 = 28
				image = bitmap2
				IL_254:
				num2 = 29
				width = image.Width
				IL_260:
				num2 = 30
				height = image.Height
				IL_26C:
				num2 = 31
				num3 = CDbl(image2.HorizontalResolution)
				GoTo IL_483
				IL_27E:
				num2 = 33
				num6 = width
				IL_483:
				num2 = 70
				Dim num7 As Integer = height
				IL_48A:
				num2 = 71
				If num7 >= height2 Then
					GoTo IL_49A
				End If
				IL_493:
				num2 = 72
				num7 = height2
				IL_49A:
				num2 = 73
				Dim bitmap3 As Bitmap = New Bitmap(CInt(Math.Round(CDbl((width + num6)) + Abstand + 1.0)), num7)
				IL_4BF:
				num2 = 74
				bitmap3.SetResolution(CSng(num3), CSng(num3))
				IL_4CF:
				num2 = 75
				Dim graphics As Graphics = Graphics.FromImage(bitmap3)
				IL_4DB:
				num2 = 76
				graphics.SmoothingMode = SmoothingMode.None
				IL_4E6:
				num2 = 77
				graphics.PixelOffsetMode = PixelOffsetMode.None
				IL_4F1:
				num2 = 78
				graphics.CompositingMode = CompositingMode.SourceCopy
				IL_4FC:
				num2 = 79
				graphics.CompositingQuality = CompositingQuality.HighSpeed
				IL_507:
				num2 = 80
				graphics.InterpolationMode = InterpolationMode.Low
				IL_512:
				num2 = 81
				graphics.DrawImage(image, 0, 0)
				IL_520:
				num2 = 82
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_557
				End If
				IL_532:
				num2 = 83
				Dim x As Integer = CInt(Math.Round(CDbl(image.Width) + Abstand))
				IL_548:
				num2 = 84
				graphics.DrawImage(image2, x, 0)
				IL_557:
				num2 = 85
				IL_55F:
				num2 = 87
				bitmap3.Save(fnamedest, ImageFormat.Bmp)
				IL_570:
				num2 = 88
				image.Dispose()
				IL_57A:
				num2 = 89
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_596
				End If
				IL_58C:
				num2 = 90
				image2.Dispose()
				IL_596:
				num2 = 91
				bitmap3.Dispose()
				IL_5A0:
				GoTo IL_762
				IL_28A:
				num2 = 35
				If num4 <= num5 Then
					GoTo IL_2BC
				End If
				IL_293:
				num2 = 36
				If num4 <> 8 Then
					GoTo IL_2A7
				End If
				IL_29B:
				num2 = 37
				Dim num8 As Integer
				modDeclares.IG_IP_color_promote(num8, 2)
				IL_2A7:
				num2 = 38
				If num4 <> 24 Then
					GoTo IL_2BC
				End If
				IL_2B0:
				num2 = 39
				modDeclares.IG_IP_color_promote(num8, 3)
				IL_2BC:
				num2 = 40
				If num4 >= num5 Then
					GoTo IL_2F5
				End If
				IL_2C5:
				num2 = 41
				If num5 <> 8 Then
					GoTo IL_2D9
				End If
				IL_2CD:
				num2 = 42
				Dim num9 As Integer
				modDeclares.IG_IP_color_promote(num9, 2)
				IL_2D9:
				num2 = 43
				If num5 <> 24 Then
					GoTo IL_2EE
				End If
				IL_2E2:
				num2 = 44
				modDeclares.IG_IP_color_promote(num9, 3)
				IL_2EE:
				num2 = 45
				num4 = num5
				IL_2F5:
				num2 = 46
				Dim interpolation As Integer = 0
				IL_2FB:
				num2 = 47
				Dim num10 As Integer
				Dim num11 As Integer
				Dim lpYResNumerator As Integer
				Dim lpYResDenominator As Integer
				Dim lpUnits As Integer
				modDeclares.IG_image_resolution_get(num9, num10, num11, lpYResNumerator, lpYResDenominator, lpUnits)
				IL_310:
				num2 = 48
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_446
				End If
				IL_325:
				num2 = 49
				Dim num12 As Integer
				Dim num13 As Integer
				Dim num14 As Integer
				Dim num15 As Integer
				Dim num16 As Integer
				modDeclares.IG_image_resolution_get(num8, num12, num13, num14, num15, num16)
				IL_33A:
				num2 = 50
				If CDbl(num10) / CDbl(num11) >= CDbl(num12) / CDbl(num13) Then
					GoTo IL_3D3
				End If
				IL_350:
				num2 = 51
				Dim new_width As Integer = CInt(Math.Round(CDbl((width * num12)) / CDbl(num13) * CDbl(num11) / CDbl(num10)))
				IL_36D:
				num2 = 52
				Dim new_height As Integer = CInt(Math.Round(CDbl((height * num12)) / CDbl(num13) * CDbl(num11) / CDbl(num10)))
				IL_38A:
				num2 = 53
				modDeclares.IG_IP_resize(num9, new_width, new_height, interpolation)
				IL_39B:
				num2 = 54
				modDeclares.IG_image_resolution_set(num9, num12, num13, num14, num15, num16)
				IL_3B0:
				num2 = 55
				num10 = num12
				IL_3B7:
				num2 = 56
				num11 = num13
				IL_3BE:
				num2 = 57
				lpYResNumerator = num14
				IL_3C5:
				num2 = 58
				lpYResDenominator = num15
				IL_3CC:
				num2 = 59
				lpUnits = num16
				IL_3D3:
				num2 = 60
				If CDbl(num10) / CDbl(num11) <= CDbl(num12) / CDbl(num13) Then
					GoTo IL_446
				End If
				IL_3E6:
				num2 = 61
				new_width = CInt(Math.Round(CDbl((num6 * num10)) / CDbl(num11) * CDbl(num13) / CDbl(num12)))
				IL_403:
				num2 = 62
				new_height = CInt(Math.Round(CDbl((height2 * num10)) / CDbl(num11) * CDbl(num13) / CDbl(num12)))
				IL_420:
				num2 = 63
				modDeclares.IG_IP_resize(num8, new_width, new_height, interpolation)
				IL_431:
				num2 = 64
				modDeclares.IG_image_resolution_set(num8, num10, num11, lpYResNumerator, lpYResDenominator, lpUnits)
				IL_446:
				num2 = 65
				modDeclares.IG_image_dimensions_get(num9, width, height, num4)
				IL_457:
				num2 = 66
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_47C
				End If
				IL_469:
				num2 = 67
				modDeclares.IG_image_dimensions_get(num8, num6, height2, num5)
				GoTo IL_483
				IL_47C:
				num2 = 69
				num6 = width
				GoTo IL_483
				IL_5A5:
				Dim num17 As Integer = num18 + 1
				num18 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num17)
				IL_723:
				GoTo IL_757
				IL_725:
				num18 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_735:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num18 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_725
			End Try
			IL_757:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_762:
			If num18 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E6E RID: 3694 RVA: 0x0008F0BC File Offset: 0x0008D2BC
		Public Function MakeDuplexNeti(ByRef fnamesim As String, ByRef img1 As Bitmap, ByRef fnamedup As String, ByRef img2 As Bitmap, ByRef fnamedest As String, ByRef Abstand As Double, Aufloesung As Single) As Integer
			Dim num As Integer
			Dim result As Integer
			Dim num19 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				New modDeclares.AT_RGBQUAD(256) {}
				IL_14:
				num2 = 3
				result = -1
				IL_18:
				num2 = 4
				Dim num3 As Double = CDbl(img1.HorizontalResolution)
				IL_24:
				num2 = 5
				Operators.CompareString(fnamedup, "", False)
				IL_34:
				num2 = 6
				Dim num4 As Integer = 0
				IL_39:
				num2 = 7
				Dim num5 As Integer = 0
				IL_3E:
				num2 = 8
				Dim width As Integer = img1.Width
				IL_49:
				num2 = 9
				Dim height As Integer = img1.Height
				IL_55:
				num2 = 10
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_25B
				End If
				IL_6A:
				num2 = 11
				Dim num6 As Integer = img2.Width
				IL_76:
				num2 = 12
				Dim height2 As Integer = img2.Height
				IL_82:
				num2 = 13
				If CInt(Math.Round(CDbl(img1.HorizontalResolution) + 0.5)) = CInt(Math.Round(CDbl(img2.HorizontalResolution) + 0.5)) Then
					GoTo IL_460
				End If
				IL_BA:
				num2 = 14
				If CInt(Math.Round(CDbl(img1.HorizontalResolution) + 0.5)) <= CInt(Math.Round(CDbl(img2.HorizontalResolution) + 0.5)) Then
					GoTo IL_184
				End If
				IL_F2:
				num2 = 15
				img2 = modPaint.ResizeImage(img2, CInt(Math.Round(CDbl((CSng(img2.Width) * img1.HorizontalResolution / img2.HorizontalResolution)))), CInt(Math.Round(CDbl((CSng(img2.Height) * img1.HorizontalResolution / img2.HorizontalResolution)))))
				IL_13C:
				num2 = 16
				Dim bitmap As Bitmap = New Bitmap(img2)
				IL_148:
				num2 = 17
				bitmap.SetResolution(img1.HorizontalResolution, img1.HorizontalResolution)
				IL_160:
				num2 = 18
				img2 = bitmap
				IL_167:
				num2 = 19
				num6 = img2.Width
				IL_173:
				num2 = 20
				height2 = img2.Height
				GoTo IL_460
				IL_184:
				num2 = 22
				If CInt(Math.Round(CDbl(img1.HorizontalResolution) + 0.5)) >= CInt(Math.Round(CDbl(img2.HorizontalResolution) + 0.5)) Then
					GoTo IL_460
				End If
				IL_1BC:
				num2 = 23
				img1 = modPaint.ResizeImage(img1, CInt(Math.Round(CDbl((CSng(img1.Width) * img2.HorizontalResolution / img1.HorizontalResolution)))), CInt(Math.Round(CDbl((CSng(img1.Height) * img2.HorizontalResolution / img1.HorizontalResolution)))))
				IL_206:
				num2 = 24
				Dim bitmap2 As Bitmap = New Bitmap(img1)
				IL_212:
				num2 = 25
				bitmap2.SetResolution(img2.HorizontalResolution, img2.HorizontalResolution)
				IL_22A:
				num2 = 26
				img1 = bitmap2
				IL_231:
				num2 = 27
				width = img1.Width
				IL_23D:
				num2 = 28
				height = img1.Height
				IL_249:
				num2 = 29
				num3 = CDbl(img2.HorizontalResolution)
				GoTo IL_460
				IL_25B:
				num2 = 31
				num6 = width
				IL_460:
				num2 = 68
				Dim num7 As Integer = height
				IL_467:
				num2 = 69
				If num7 >= height2 Then
					GoTo IL_477
				End If
				IL_470:
				num2 = 70
				num7 = height2
				IL_477:
				num2 = 71
				Dim bitmap3 As Bitmap = New Bitmap(CInt(Math.Round(CDbl((width + num6)) + Abstand + 1.0)), num7, PixelFormat.Format24bppRgb)
				IL_4A2:
				num2 = 72
				bitmap3.SetResolution(CSng(num3), CSng(num3))
				IL_4B2:
				num2 = 73
				Dim graphics As Graphics = Graphics.FromImage(bitmap3)
				IL_4BE:
				num2 = 74
				graphics.SmoothingMode = SmoothingMode.None
				IL_4C9:
				num2 = 75
				graphics.PixelOffsetMode = PixelOffsetMode.None
				IL_4D4:
				num2 = 76
				graphics.CompositingMode = CompositingMode.SourceCopy
				IL_4DF:
				num2 = 77
				graphics.CompositingQuality = CompositingQuality.HighSpeed
				IL_4EA:
				num2 = 78
				graphics.InterpolationMode = InterpolationMode.Low
				IL_4F5:
				num2 = 79
				graphics.DrawImage(img1, 0, 0)
				IL_503:
				num2 = 80
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_53B
				End If
				IL_515:
				num2 = 81
				Dim x As Integer = CInt(Math.Round(CDbl(img1.Width) + Abstand))
				IL_52C:
				num2 = 82
				graphics.DrawImage(img2, x, 0)
				IL_53B:
				num2 = 83
				IL_543:
				num2 = 85
				If img1.PixelFormat = PixelFormat.Format1bppIndexed Then
					GoTo IL_579
				End If
				IL_554:
				num2 = 86
				bitmap3.SetResolution(Aufloesung, Aufloesung)
				IL_562:
				num2 = 87
				bitmap3.Save(fnamedest, ImageFormat.Bmp)
				GoTo IL_637
				IL_579:
				num2 = 89
				Dim rect As Rectangle = New Rectangle(0, 0, bitmap3.Width, bitmap3.Height)
				IL_593:
				num2 = 90
				Dim bitmap4 As Bitmap = bitmap3.Clone(rect, PixelFormat.Format1bppIndexed)
				IL_5A6:
				num2 = 91
				Dim encoderParameters As EncoderParameters = New EncoderParameters(1)
				IL_5B1:
				num2 = 92
				encoderParameters.Param(0) = New EncoderParameter(System.Drawing.Imaging.Encoder.Compression, 4L)
				IL_5C9:
				num2 = 93
				Dim imageEncoders As ImageCodecInfo() = ImageCodecInfo.GetImageEncoders()
				IL_5D3:
				num2 = 94
				Dim num8 As Integer = imageEncoders.Length - 1
				Dim encoder As ImageCodecInfo
				For i As Integer = 0 To num8
					IL_5E3:
					num2 = 95
					If Operators.CompareString(imageEncoders(i).MimeType, "image/tiff", False) = 0 Then
						IL_5FD:
						num2 = 96
						encoder = imageEncoders(i)
						Exit For
					End If
					IL_609:
					num2 = 98
				Next
				IL_618:
				num2 = 99
				bitmap4.SetResolution(Aufloesung, Aufloesung)
				IL_626:
				num2 = 100
				bitmap4.Save(fnamedest, encoder, encoderParameters)
				IL_637:
				num2 = 101
				img1.Dispose()
				IL_641:
				num2 = 102
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_65D
				End If
				IL_653:
				num2 = 103
				img2.Dispose()
				IL_65D:
				num2 = 104
				bitmap3.Dispose()
				IL_667:
				GoTo IL_85D
				IL_267:
				num2 = 33
				If num4 <= num5 Then
					GoTo IL_299
				End If
				IL_270:
				num2 = 34
				If num4 <> 8 Then
					GoTo IL_284
				End If
				IL_278:
				num2 = 35
				Dim num9 As Integer
				modDeclares.IG_IP_color_promote(num9, 2)
				IL_284:
				num2 = 36
				If num4 <> 24 Then
					GoTo IL_299
				End If
				IL_28D:
				num2 = 37
				modDeclares.IG_IP_color_promote(num9, 3)
				IL_299:
				num2 = 38
				If num4 >= num5 Then
					GoTo IL_2D2
				End If
				IL_2A2:
				num2 = 39
				If num5 <> 8 Then
					GoTo IL_2B6
				End If
				IL_2AA:
				num2 = 40
				Dim num10 As Integer
				modDeclares.IG_IP_color_promote(num10, 2)
				IL_2B6:
				num2 = 41
				If num5 <> 24 Then
					GoTo IL_2CB
				End If
				IL_2BF:
				num2 = 42
				modDeclares.IG_IP_color_promote(num10, 3)
				IL_2CB:
				num2 = 43
				num4 = num5
				IL_2D2:
				num2 = 44
				Dim interpolation As Integer = 0
				IL_2D8:
				num2 = 45
				Dim num11 As Integer
				Dim num12 As Integer
				Dim lpYResNumerator As Integer
				Dim lpYResDenominator As Integer
				Dim lpUnits As Integer
				modDeclares.IG_image_resolution_get(num10, num11, num12, lpYResNumerator, lpYResDenominator, lpUnits)
				IL_2ED:
				num2 = 46
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_423
				End If
				IL_302:
				num2 = 47
				Dim num13 As Integer
				Dim num14 As Integer
				Dim num15 As Integer
				Dim num16 As Integer
				Dim num17 As Integer
				modDeclares.IG_image_resolution_get(num9, num13, num14, num15, num16, num17)
				IL_317:
				num2 = 48
				If CDbl(num11) / CDbl(num12) >= CDbl(num13) / CDbl(num14) Then
					GoTo IL_3B0
				End If
				IL_32D:
				num2 = 49
				Dim new_width As Integer = CInt(Math.Round(CDbl((width * num13)) / CDbl(num14) * CDbl(num12) / CDbl(num11)))
				IL_34A:
				num2 = 50
				Dim new_height As Integer = CInt(Math.Round(CDbl((height * num13)) / CDbl(num14) * CDbl(num12) / CDbl(num11)))
				IL_367:
				num2 = 51
				modDeclares.IG_IP_resize(num10, new_width, new_height, interpolation)
				IL_378:
				num2 = 52
				modDeclares.IG_image_resolution_set(num10, num13, num14, num15, num16, num17)
				IL_38D:
				num2 = 53
				num11 = num13
				IL_394:
				num2 = 54
				num12 = num14
				IL_39B:
				num2 = 55
				lpYResNumerator = num15
				IL_3A2:
				num2 = 56
				lpYResDenominator = num16
				IL_3A9:
				num2 = 57
				lpUnits = num17
				IL_3B0:
				num2 = 58
				If CDbl(num11) / CDbl(num12) <= CDbl(num13) / CDbl(num14) Then
					GoTo IL_423
				End If
				IL_3C3:
				num2 = 59
				new_width = CInt(Math.Round(CDbl((num6 * num11)) / CDbl(num12) * CDbl(num14) / CDbl(num13)))
				IL_3E0:
				num2 = 60
				new_height = CInt(Math.Round(CDbl((height2 * num11)) / CDbl(num12) * CDbl(num14) / CDbl(num13)))
				IL_3FD:
				num2 = 61
				modDeclares.IG_IP_resize(num9, new_width, new_height, interpolation)
				IL_40E:
				num2 = 62
				modDeclares.IG_image_resolution_set(num9, num11, num12, lpYResNumerator, lpYResDenominator, lpUnits)
				IL_423:
				num2 = 63
				modDeclares.IG_image_dimensions_get(num10, width, height, num4)
				IL_434:
				num2 = 64
				If Operators.CompareString(fnamedup, "", False) = 0 Then
					GoTo IL_459
				End If
				IL_446:
				num2 = 65
				modDeclares.IG_image_dimensions_get(num9, num6, height2, num5)
				GoTo IL_460
				IL_459:
				num2 = 67
				num6 = width
				GoTo IL_460
				IL_66C:
				Dim num18 As Integer = num19 + 1
				num19 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num18)
				IL_81E:
				GoTo IL_852
				IL_820:
				num19 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_830:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num19 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_820
			End Try
			IL_852:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_85D:
			If num19 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E6F RID: 3695 RVA: 0x0008F94C File Offset: 0x0008DB4C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Function CreateLicense() As Object
			VBMath.Randomize()
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), "c:\fileconverter.lic", OpenMode.Random, OpenAccess.[Default], OpenShare.[Default], 1)
			Dim num2 As Short = 1S
			Do
				' The following expression was wrapped in a checked-expression
				' The following expression was wrapped in a unchecked-expression
				Dim value As Byte = CByte(Math.Round(CDbl((VBMath.Rnd() * 255F))))
				FileSystem.FilePut(CInt(num), value, -1L)
				num2 += 1S
			Loop While num2 <= 1024S
			FileSystem.FileClose(New Integer() { CInt(num) })
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E70 RID: 3696 RVA: 0x0008F9B0 File Offset: 0x0008DBB0
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub ReadFile(ByRef f As String)
		End Sub

		' Token: 0x06000E71 RID: 3697 RVA: 0x0008F9C0 File Offset: 0x0008DBC0
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub ShowErrorFile(ByRef FilmNr As Integer)
			Dim flag As Boolean = False
			Dim text As String = modDeclares.SystemData.LogfileName + "\temp.txt"
			If Operators.CompareString(FileSystem.Dir(text, Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
				FileSystem.Kill(text)
			End If
			Dim num As Integer = FilmNr
			Dim num2 As Integer = num
			Dim flag2 As Boolean = False
			Dim num3 As Integer = 0
			Do
				Dim text2 As String = modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(num) + ".err"
				MyProject.Forms.frmFilming.lstInfo.Items.Add("FNR=" + Conversions.ToString(num))
				MyProject.Forms.frmFilming.lstInfo.Refresh()
				MyProject.Forms.frmFilming.lstInfo.TopIndex = MyProject.Forms.frmFilming.lstInfo.Items.Count - 1
				If Operators.CompareString(FileSystem.Dir(text2, Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
					If(FileSystem.GetAttr(text2) And Microsoft.VisualBasic.FileAttribute.Archive) = Microsoft.VisualBasic.FileAttribute.Archive Then
						flag2 = True
					Else
						num2 = num
						flag = True
					End If
				End If
				If Not flag2 Then
					num -= 1
					If num = 0 Then
						flag2 = True
					End If
				End If
				num3 += 1
				If num3 = 100 Then
					flag2 = True
					num2 = num
				End If
			Loop While Not flag2
			MyProject.Forms.frmFilming.lstInfo.Items.Add("STOPPED")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			MyProject.Forms.frmFilming.lstInfo.TopIndex = MyProject.Forms.frmFilming.lstInfo.Items.Count - 1
			If flag Then
				If Not Directory.Exists(modDeclares.SystemData.LogfileName) Then
					Dim text3 As String = "Folder for Log-Files doesn't exist!"
					Dim num4 As Short = 0S
					Dim text4 As String = "file-converter"
					modMain.msgbox2(text3, num4, text4)
					Return
				End If
				Dim num5 As Short = CShort(FileSystem.FreeFile())
				FileSystem.FileOpen(CInt(num5), text, OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
				Dim num6 As Short = CShort(FileSystem.FreeFile())
				Dim num7 As Integer = num2
				Dim num8 As Integer = FilmNr
				For i As Integer = num7 To num8
					MyProject.Forms.frmFilming.lstInfo.Items.Add("FNR=" + Conversions.ToString(i))
					MyProject.Forms.frmFilming.lstInfo.Refresh()
					MyProject.Forms.frmFilming.lstInfo.TopIndex = MyProject.Forms.frmFilming.lstInfo.Items.Count - 1
					Dim text2 As String = modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(i) + ".err"
					If Operators.CompareString(FileSystem.Dir(text2, Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 AndAlso (FileSystem.GetAttr(text2) And Microsoft.VisualBasic.FileAttribute.Archive) <> Microsoft.VisualBasic.FileAttribute.Archive Then
						FileSystem.SetAttr(text2, Microsoft.VisualBasic.FileAttribute.Archive)
						FileSystem.PrintLine(CInt(num5), New Object() { "Film: " + Conversions.ToString(i) })
						FileSystem.FileOpen(CInt(num6), text2, OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
						While Not FileSystem.EOF(CInt(num6))
							Dim text5 As String = FileSystem.LineInput(CInt(num6))
							FileSystem.PrintLine(CInt(num5), New Object() { text5 })
						End While
						FileSystem.FileClose(New Integer() { CInt(num6) })
						FileSystem.PrintLine(CInt(num5), New Object() { "" })
					End If
				Next
				FileSystem.FileClose(New Integer() { CInt(num5) })
				MyProject.Forms.frmFilming.lstInfo.Items.Add("Showfile=" + Conversions.ToString(flag))
				MyProject.Forms.frmFilming.lstInfo.Refresh()
				MyProject.Forms.frmFilming.lstInfo.TopIndex = MyProject.Forms.frmFilming.lstInfo.Items.Count - 1
				If flag Then
					Dim text4 As String = "TXT_ERRORS_FILMING1"
					Dim text6 As String = modMain.GetText(text4)
					If Operators.CompareString(text6, "", False) <> 0 Then
						Dim str As String = text6
						Dim str2 As String = vbCr
						text4 = "TXT_ERRORS_FILMING2"
						text6 = str + str2 + modMain.GetText(text4)
					Else
						text6 = "Es sind Fehler beim Verfilmen aufgetreten!" & vbCr & "Bitte folgenden Report überprüfen!"
					End If
					Dim num4 As Short = 0S
					text4 = "file-converter"
					modMain.msgbox2(text6, num4, text4)
					Interaction.Shell("notepad " + text, AppWinStyle.MaximizedFocus, False, -1)
				End If
			End If
		End Sub

		' Token: 0x06000E72 RID: 3698 RVA: 0x0008FDDD File Offset: 0x0008DFDD
		Public Sub EnterCore()
			modDeclares.InCore = True
		End Sub

		' Token: 0x06000E73 RID: 3699 RVA: 0x0008FDE5 File Offset: 0x0008DFE5
		Public Sub LeaveCore()
			modDeclares.InCore = False
		End Sub

		' Token: 0x06000E74 RID: 3700 RVA: 0x0008FDF0 File Offset: 0x0008DFF0
		Public Function UpdateRollInfoFileFrameCounter(ByRef roll As String) As Object
			Dim text As String = modDeclares.SystemData.LogfileName + "\" + roll + ".Ini"
			If Not File.Exists(text) Then
				Using streamWriter As StreamWriter = New StreamWriter(text, True, Encoding.Unicode)
					streamWriter.Write("[UNICODE]")
					streamWriter.Close()
				End Using
			End If
			Dim text2 As String = "INFO"
			Dim text3 As String = "FRAMECOUNT"
			Dim lpString As String = (modDeclares.GetPrivateProfileInt(text2, text3, 0, text) + 1).ToString()
			Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("INFO", "FRAMECOUNT", lpString, text) > False)
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E75 RID: 3701 RVA: 0x0008FE98 File Offset: 0x0008E098
		Public Sub ClearCoreErrorCondition()
			modDeclares.ErrorInCore = False
		End Sub

		' Token: 0x06000E76 RID: 3702 RVA: 0x0008FEA0 File Offset: 0x0008E0A0
		Public Sub SetCoreErrorCondition()
			modDeclares.ErrorInCore = True
		End Sub

		' Token: 0x06000E77 RID: 3703 RVA: 0x0008FEA8 File Offset: 0x0008E0A8
		Public Function UpdateRollInfoFileForRefilm(ByRef roll As String, FileName As String, ByRef Index As Integer) As Object
			Dim num2 As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim lpString As String = Support.Format(Index, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				IL_17:
				ProjectData.ClearProjectError()
				num2 = 1
				IL_1E:
				num = 3
				If Directory.Exists(MyProject.Application.Info.DirectoryPath + "\ROLLDESCS") Then
					GoTo IL_60
				End If
				IL_40:
				num = 4
				FileSystem.MkDir(MyProject.Application.Info.DirectoryPath + "\ROLLDESCS")
				IL_60:
				num = 5
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\ROLLDESCS\" + roll + ".desc"
				IL_84:
				num = 6
				If File.Exists(text) Then
					GoTo IL_C1
				End If
				IL_8F:
				num = 7
				Using streamWriter As StreamWriter = New StreamWriter(text, True, Encoding.Unicode)
					streamWriter.Write("[UNICODE]")
					streamWriter.Close()
				End Using
				IL_C1:
				num = 8
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "LASTFILE", FileName, text) > False)
				IL_DA:
				num = 9
				Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "LASTFILEINDEX", lpString, text) > False)
				IL_F5:
				num = 10
				If Operators.CompareString(modMain.GiveIniW(text, "INFO", "FIRSTFILE"), "", False) <> 0 Then
					GoTo IL_14B
				End If
				IL_116:
				num = 11
				Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "FIRSTFILE", FileName, text) > False)
				IL_130:
				num = 12
				Dim flag4 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "FIRSTFILEINDEX", lpString, text) > False)
				IL_14B:
				num = 13
				Dim text2 As String = "INFO"
				Dim text3 As String = "IMAGECOUNT"
				Dim privateProfileInt As Integer = modDeclares.GetPrivateProfileInt(text2, text3, 0, text)
				IL_16A:
				num = 14
				Dim lpString2 As String = Support.Format(privateProfileInt + 1, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				IL_184:
				num = 15
				Dim flag5 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "IMAGECOUNT", lpString2, text) > False)
				IL_19F:
				GoTo IL_231
				IL_1A4:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_1F2:
				GoTo IL_226
				IL_1F4:
				num4 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_204:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_1F4
			End Try
			IL_226:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_231:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E78 RID: 3704 RVA: 0x00090124 File Offset: 0x0008E324
		Public Function GetRoll(ByRef KStRolle As String) As String
			' The following expression was wrapped in a checked-expression
			Return Strings.Right(Strings.Left(KStRolle, Strings.Len(KStRolle) - 10), 5)
		End Function

		' Token: 0x06000E79 RID: 3705 RVA: 0x0009014C File Offset: 0x0008E34C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function AddProtLine(ByRef roll As Integer, ByRef FileName As String, ByRef page As Integer, ByRef blip As String, ByRef pos As String, ByRef docsize As String, ByRef err2 As Boolean, ByRef Index As Integer) As Boolean
			' The following expression was wrapped in a checked-statement
			Dim num As Integer
			Dim result As Boolean
			Dim num7 As Integer
			Dim obj As Object
			Try
				Dim fileSystem As IFileSystem3 = New FileSystemObjectClass()
				Dim fixedLengthString As FixedLengthString = New FixedLengthString(512)
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\fileconverter.txt"
				ProjectData.ClearProjectError()
				num = 2
				Dim file As File = fileSystem.GetFile(FileName)
				Dim text2 As String = ""
				result = True
				Dim text3 As String = Support.Format(roll, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				modMain.UpdateRollInfoFileForRefilm(text3, FileName, Index)
				If modDeclares.SystemData.UseLogFile Then
					text3 = Support.Format(roll, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					modMain.UpdateRollInfoFile(text3, FileName)
					Dim num2 As Short = CShort(FileSystem.FreeFile())
					Dim flag As Boolean = False
					If Operators.CompareString(FileSystem.Dir(modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(roll) + ".txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
						flag = True
					End If
					If modDeclares.NEWPROTOCOLHEADER Then
						flag = True
						Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
						Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileStringW("SYSTEM", "NEWPROTOCOLHEADER", "0", lpFileName) > False)
						modDeclares.NEWPROTOCOLHEADER = False
					End If
					Dim num3 As Short
					Using streamWriter As StreamWriter = New StreamWriter(modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(roll) + ".txt", True, Encoding.Unicode)
						If modDeclares.SystemData.EXCELPROTOCOL Then
							num3 = CShort(FileSystem.FreeFile())
							FileSystem.FileOpen(CInt(num3), modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(roll) + ".xtxt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
						End If
						If flag Then
							Dim num4 As Integer = CInt((modMain.HeaderCount - 1S))
							For i As Integer = 0 To num4
								If modDeclares.SystemData.HeadersSel(i) Then
									Dim text4 As String = modMain.GiveIni(text, "frmFilmPreview", "lstHeader.0")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Rollennummer"
									End If
									If Operators.CompareString(modDeclares.SystemData.Headers(i), text4, False) = 0 Then
										streamWriter.WriteLine(text4 + "=" + Conversions.ToString(roll))
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstHeader.1")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Datum"
									End If
									If Operators.CompareString(modDeclares.SystemData.Headers(i), text4, False) = 0 Then
										streamWriter.WriteLine(text4 + "=" + Conversions.ToString(DateAndTime.Today))
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstHeader.2")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Datum/Uhrzeit"
									End If
									If Operators.CompareString(modDeclares.SystemData.Headers(i), text4, False) = 0 Then
										streamWriter.WriteLine(text4 + "=" + Conversions.ToString(DateAndTime.Now))
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstHeader.3")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Benutzer"
									End If
									If Operators.CompareString(modDeclares.SystemData.Headers(i), text4, False) = 0 Then
										Dim fixedLengthString2 As FixedLengthString = fixedLengthString
										Dim fixedLengthString3 As FixedLengthString = fixedLengthString2
										text3 = fixedLengthString2.Value
										Dim num5 As Integer = 512
										modDeclares.GetUserName(text3, num5)
										fixedLengthString3.Value = text3
										streamWriter.WriteLine(text4 + "=" + Strings.Left(fixedLengthString.Value, Strings.InStr(1, fixedLengthString.Value, vbNullChar, Microsoft.VisualBasic.CompareMethod.Binary) - 1))
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstHeader.4")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Computer"
									End If
									If Operators.CompareString(modDeclares.SystemData.Headers(i), text4, False) = 0 Then
										Dim fixedLengthString4 As FixedLengthString = fixedLengthString
										Dim fixedLengthString3 As FixedLengthString = fixedLengthString4
										text3 = fixedLengthString4.Value
										Dim num5 As Integer = 512
										modDeclares.GetComputerName(text3, num5)
										fixedLengthString3.Value = text3
										streamWriter.WriteLine(text4 + "=" + Strings.Left(fixedLengthString.Value, Strings.InStr(1, fixedLengthString.Value, vbNullChar, Microsoft.VisualBasic.CompareMethod.Binary) - 1))
									End If
								End If
							Next
						End If
						Dim flag3 As Boolean = False
						If err2 Then
							text3 = "TXT_ERROR_LOADING_DOCUMENT"
							text2 = modMain.GetText(text3)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Fehler beim Laden des Dokuments: "
							End If
							text2 = String.Concat(New String() { text2, "<", FileName, "(", Conversions.ToString(page), ")>" })
						Else
							Dim i As Integer = 0
							Do
								If modDeclares.SystemData.RecordsSel(i) Then
									If flag3 Then
										text2 += modDeclares.SystemData.Delimiter
									Else
										flag3 = True
									End If
									Dim text4 As String = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.0")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Dateiname"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										Dim text5 As String = FileName
										text5 = Strings.Mid(FileName, Strings.InStrRev(FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
										If modDeclares.SystemData.IgnoreChars Then
											text5 = Strings.Mid(text5, modDeclares.SystemData.IgnoreCharChount + 1)
										End If
										text2 += text5
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.1")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "voller Dateiname"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += FileName
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.2")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Dokumentengröße"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += docsize
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.3")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Dateierweiterung"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += Strings.Right(FileName, 3)
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.4")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "BLIP-Positionen"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += blip
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.5")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Lineare Frame Position"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += pos
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.6")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Dateigröße"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += Support.Format(RuntimeHelpers.GetObjectValue(file.Size), "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.7")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Änderungsdatum"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += Conversions.ToString(file.DateLastModified)
									End If
									text4 = modMain.GiveIni(text, "frmFilmPreview", "lstRecords.8")
									If Operators.CompareString(text4, "", False) = 0 Then
										text4 = "Seitennummer"
									End If
									If Operators.CompareString(modDeclares.SystemData.Records(i), text4, False) = 0 Then
										text2 += Conversions.ToString(page)
									End If
								End If
								i += 1
							Loop While i <= 8
							Dim text6 As String = String.Concat(New String() { FileName, ";", Conversions.ToString(page), ";", Conversions.ToString(modMain.ProtIndex) })
							modMain.ProtIndex += 1
							streamWriter.WriteLine(text2)
							If modDeclares.SystemData.EXCELPROTOCOL Then
								FileSystem.PrintLine(CInt(num3), New Object() { text6 })
							End If
						End If
						Operators.CompareString(text2, "", False)
						streamWriter.Close()
					End Using
					If modDeclares.SystemData.EXCELPROTOCOL Then
						FileSystem.FileClose(New Integer() { CInt(num3) })
					End If
				End If
				IL_896:
				GoTo IL_8D9
				IL_86C:
				Dim errObject As ErrObject = Information.Err()
				text3 = errObject.Description
				Dim num6 As Short = 0S
				Dim text7 As String = "file-converter"
				modMain.msgbox2(text3, num6, text7)
				errObject.Description = text3
				GoTo IL_896
				IL_898:
				num7 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_8AC:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num7 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_898
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_8D9:
			If num7 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E7A RID: 3706 RVA: 0x00090A70 File Offset: 0x0008EC70
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function AddErrorLine(ByRef roll As Integer, ByRef FileName As String, ByRef page As Integer, ByRef blip As String, ByRef pos As String, ByRef docsize As String, ByRef err1 As Boolean, ByRef errcode As Integer, ByRef errsrc As String) As Boolean
			Dim num As Integer
			Dim result As Boolean
			Dim num3 As Integer
			Dim obj As Object
			Try
				ProjectData.ClearProjectError()
				num = 2
				result = True
				If modDeclares.SystemData.UseLogFile Then
					' The following expression was wrapped in a checked-expression
					Dim num2 As Short = CShort(FileSystem.FreeFile())
					FileSystem.FileOpen(CInt(num2), modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(roll) + ".err", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
					If err1 Then
						Dim text As String = "TXT_ERROR_LOADING_DOCUMENT"
						Dim text2 As String = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Fehler beim Laden des Dokuments: "
						End If
						text2 = String.Concat(New String() { text2, "<", FileName, "(", Conversions.ToString(page), ")> Code=", Conversions.ToString(errcode), " SRC=", errsrc })
						If Operators.CompareString(text2, "", False) <> 0 Then
							FileSystem.PrintLine(CInt(num2), New Object() { text2 })
						End If
					End If
					FileSystem.FileClose(New Integer() { CInt(num2) })
					FileSystem.SetAttr(modDeclares.SystemData.LogfileName + "\" + Conversions.ToString(roll) + ".err", Microsoft.VisualBasic.FileAttribute.Normal)
				End If
				IL_144:
				GoTo IL_187
				IL_128:
				Interaction.MsgBox("AddErrorLine: " + Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_144
				IL_146:
				num3 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_15A:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num3 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_146
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_187:
			If num3 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E7B RID: 3707 RVA: 0x00090C2C File Offset: 0x0008EE2C
		Public Function UpdateRollInfoFile(ByRef roll As String, FileName As String) As Object
			Dim text As String = modDeclares.SystemData.LogfileName + "\" + roll + ".Ini"
			If Not File.Exists(text) Then
				Using streamWriter As StreamWriter = New StreamWriter(text, True, Encoding.Unicode)
					streamWriter.Write("[UNICODE]")
					streamWriter.Close()
				End Using
			End If
			If Operators.CompareString(modMain.GiveIniW(text, "INFO", "FIRSTFILE"), "", False) = 0 Then
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "FIRSTFILE", FileName, text) > False)
			End If
			Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "LASTFILE", FileName, text) > False)
			Dim text2 As String = "INFO"
			Dim text3 As String = "IMAGECOUNT"
			Dim lpString As String = Support.Format(modDeclares.GetPrivateProfileInt(text2, text3, 0, text) + 1, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileStringW("INFO", "IMAGECOUNT", lpString, text) > False)
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E7C RID: 3708 RVA: 0x00090D28 File Offset: 0x0008EF28
		Public Function GetDocCount(ByRef start As Integer) As Integer
			Dim num As Integer = 1
			Dim num2 As Integer = start + 1
			Dim imagecount As Integer = modDeclares.imagecount
			Dim num3 As Integer = num2
			While num3 <= imagecount AndAlso modDeclares.Images(num3).Level <= 1S
				num += 1
				num3 += 1
			End While
			Return num
		End Function

		' Token: 0x06000E7D RID: 3709 RVA: 0x00090D64 File Offset: 0x0008EF64
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub LogFaktor(ByRef X As String)
		End Sub

		' Token: 0x06000E7E RID: 3710 RVA: 0x00090D74 File Offset: 0x0008EF74
		Public Function CheckShutterAndMonitor() As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			If modDeclares.UseDebug Then
				result = True
			Else
				If modDeclares.SystemData.Trinamic Then
					MyProject.Forms.frmMonitorTest.Show()
					Application.DoEvents()
					modDeclares.Sleep(1000)
					Dim num As Short
					If Not modDeclares.UseDebug Then
						num = CShort(modTrinamic.GetTrinamicLichtSensor())
					Else
						num = 1000S
					End If
					MyProject.Forms.frmMonitorTest.Close()
					If num < modDeclares.SystemData.MonitorThreshold Then
						Dim text As String = "TXT_MONITOR_ERROR"
						Dim text2 As String = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Achtung, es konnte nicht festgestellt werden, ob die Belichtungseinheit korrekt arbeitet!" & vbCr & "Wollen Sie die Belichtungseinheit manuell überprüfen?"
						Else
							Dim str As String = text2
							Dim str2 As String = vbCr
							text = "TXT_MONITOR_ERROR2"
							text2 = str + str2 + modMain.GetText(text)
						End If
						Dim num2 As Short = 4S
						text = "file-converter"
						If modMain.msgbox2(text2, num2, text) <> 6S Then
							text = "TXT_EXPOSING_STOP"
							text2 = modMain.GetText(text)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Das Verfilmen kann nicht fortgesetzt werden!"
							End If
							num2 = 0S
							text = "file-converter"
							modMain.msgbox2(text2, num2, text)
							Return result
						End If
						text = "TXT_REMOVE_CAMERA"
						text2 = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Bitte entfernen Sie jetzt die Kameraeinheit!"
							text2 += vbCr & "Vorsicht, nach dem Bestätigen wird der Verschluss geöffnet!"
						Else
							Dim str3 As String = text2
							Dim str4 As String = vbCr
							text = "TXT_REMOVE_CAMERA2"
							text2 = str3 + str4 + modMain.GetText(text)
						End If
						num2 = 3S
						text = "file-converter"
						If modMain.msgbox2(text2, num2, text) = 2S Then
							text = "TXT_EXPOSING_STOP"
							text2 = modMain.GetText(text)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Das Verfilmen kann nicht fortgesetzt werden!"
							End If
							num2 = 0S
							text = "file-converter"
							modMain.msgbox2(text2, num2, text)
							Return result
						End If
						num2 = 2S
						Dim num3 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
						Dim num4 As Integer = 0
						Dim num5 As Integer = 0
						Dim num6 As Integer
						Dim num7 As Integer
						modMultiFly.FahreMotor(num2, num3, num6, num7, num4, num5, modDeclares.SystemData.VResolution)
						MyProject.Forms.frmMonitorTest.Show()
						Application.DoEvents()
						MyProject.Forms.frmManuellerMonitorTest.ShowDialog()
						MyProject.Forms.frmMonitorTest.Close()
						modSMCi.FahreVerschlussMotorAufNullpunkt()
						If MyProject.Forms.frmManuellerMonitorTest.GetRC() = 7S Then
							text = "TXT_MONITOR_SERVICE1"
							text2 = modMain.GetText(text)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Das Verfilmen kann nicht fortgesetzt werden, bitte den Service sofort informieren!"
							End If
							num2 = 0S
							text = "file-converter"
							modMain.msgbox2(text2, num2, text)
							Return result
						End If
						text = "TXT_MONITOR_SERVICE2"
						text2 = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Das Verfilmen kann fortgesetzt werden aber der Service sollte umgehend informiert werden!"
							text2 += vbCr & "Soll jetzt verfilmt werden?"
						Else
							Dim str5 As String = text2
							Dim str6 As String = vbCr
							text = "TXT_MONITOR_SERVICE3"
							text2 = str5 + str6 + modMain.GetText(text)
						End If
						num2 = 4S
						text = "file-converter"
						If modMain.msgbox2(text2, num2, text) = 7S Then
							Return result
						End If
						text = "TXT_INSERT_CAMERA"
						text2 = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Setzen Sie nun die Kameraeinheit wieder in das System ein, das Verfilmen wird dann gestartet."
						End If
						num2 = 3S
						text = "file-converter"
						If modMain.msgbox2(text2, num2, text) = 2S Then
							Return result
						End If
					End If
				End If
				result = True
			End If
			Return result
		End Function

		' Token: 0x06000E7F RID: 3711 RVA: 0x00091098 File Offset: 0x0008F298
		Public Function RemoveExtensionAndPath(ByRef fn As String) As String
			Dim text As String = fn
			Dim num As Short = CShort(Strings.InStrRev(fn, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary))
			If num > 0S Then
				text = Strings.Mid(fn, CInt((num + 1S)))
			End If
			If Strings.InStr(text, ".", Microsoft.VisualBasic.CompareMethod.Binary) <> 0 Then
				text = Strings.Left(text, Strings.InStrRev(text, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
			End If
			Return text
		End Function

		' Token: 0x06000E80 RID: 3712 RVA: 0x000910EC File Offset: 0x0008F2EC
		Public Function dmin(X As Double, y As Double) As Double
			Dim result As Double = X
			If y < X Then
				result = y
			End If
			Return result
		End Function

		' Token: 0x06000E81 RID: 3713 RVA: 0x00091104 File Offset: 0x0008F304
		Public Function GetNumberOfPagesInTIFF(file_name As String) As Long
			Dim result As Long
			Dim num As Integer
			Dim num5 As Integer
			Dim obj2 As Object
			Try
				Dim count As Integer = 12
				If Operators.CompareString(modMain.lastmptif, file_name, False) = 0 Then
					result = CLng(modMain.lastpcount)
				Else
					modMain.lastmptif = file_name
					ProjectData.ClearProjectError()
					num = 2
					If Operators.CompareString(Strings.Right(file_name, 3).ToUpper(), "JPG", False) = 0 Or Operators.CompareString(Strings.Right(file_name, 3).ToUpper(), "DUP", False) = 0 Then
						modMain.lastpcount = 1
						result = 1L
					Else
						Dim fileStream As FileStream = File.Open(file_name, FileMode.OpenOrCreate)
						Dim obj As Object = New Byte(12) {}
						fileStream.Read(CType(obj, Byte()), 0, count)
						Dim num2 As Long = Conversions.ToLong(Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 7 }, Nothing), 16777216))
						num2 = Conversions.ToLong(Operators.AddObject(num2, Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 6 }, Nothing), 65536)))
						num2 = Conversions.ToLong(Operators.AddObject(num2, Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 5 }, Nothing), 256)))
						num2 = Conversions.ToLong(Operators.AddObject(num2, NewLateBinding.LateIndexGet(obj, New Object() { 4 }, Nothing)))
						fileStream.Seek(num2, SeekOrigin.Begin)
						Dim num3 As Long = 0L
						While True
							num3 += 1L
							If num3 > 10000L Then
								Exit For
							End If
							fileStream.Read(CType(obj, Byte()), 0, 2)
							Dim num4 As Long = Conversions.ToLong(Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 1 }, Nothing), 256))
							num4 = Conversions.ToLong(Operators.AddObject(num4, NewLateBinding.LateIndexGet(obj, New Object() { 0 }, Nothing)))
							fileStream.Seek(num4 * 12L, SeekOrigin.Current)
							fileStream.Read(CType(obj, Byte()), 0, 4)
							num2 = Conversions.ToLong(Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 3 }, Nothing), 16777216))
							num2 = Conversions.ToLong(Operators.AddObject(num2, Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 2 }, Nothing), 65536)))
							num2 = Conversions.ToLong(Operators.AddObject(num2, Operators.MultiplyObject(NewLateBinding.LateIndexGet(obj, New Object() { 1 }, Nothing), 256)))
							num2 = Conversions.ToLong(Operators.AddObject(num2, NewLateBinding.LateIndexGet(obj, New Object() { 0 }, Nothing)))
							If num2 <> 0L Then
								fileStream.Seek(num2, SeekOrigin.Begin)
							End If
							If num2 = 0L Then
								GoTo Block_7
							End If
						End While
						fileStream.Close()
						result = -1L
						GoTo IL_317
						Block_7:
						fileStream.Close()
						modMain.lastpcount = CInt(num3)
						result = num3
					End If
				End If
				IL_317:
				GoTo IL_35A
				IL_305:
				Interaction.MsgBox(Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_317
				IL_319:
				num5 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_32D:
			Catch obj3 When endfilter(TypeOf obj2 Is Exception And num <> 0 And num5 = 0)
				Dim ex As Exception = CType(obj3, Exception)
				GoTo IL_319
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_35A:
			If num5 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x06000E82 RID: 3714 RVA: 0x00091490 File Offset: 0x0008F690
		Public Sub btnDARenderPageToString_Click()
		End Sub

		' Token: 0x06000E83 RID: 3715 RVA: 0x000914A0 File Offset: 0x0008F6A0
		Public Sub DeleteTempFiles()
			modMain.DeleteTempFiles(modMain.temppath)
		End Sub

		' Token: 0x06000E84 RID: 3716 RVA: 0x000914B8 File Offset: 0x0008F6B8
		Public Sub DeleteTempFiles(p As String)
			' The following expression was wrapped in a checked-statement
			If Directory.Exists(p) Then
				For Each path As String In Directory.GetFiles(p, "*.*", SearchOption.TopDirectoryOnly)
					Try
						File.Delete(path)
					Catch ex As Exception
						Dim num As Long = 1L
					End Try
				Next
				If Directory.GetFiles(p, "*.*", SearchOption.TopDirectoryOnly).Length > 0 Then
					Dim num As Long = 0L
					For Each path2 As String In Directory.GetFiles(p, "*.*", SearchOption.TopDirectoryOnly)
						num = 1L
						Do
							Try
								File.Delete(path2)
								Exit Try
							Catch ex2 As Exception
								modDeclares.Sleep(1000)
							End Try
							num += 1L
						Loop While num <= 5L
						If num = 6L Then
							Dim text As String = "Couldn't clear " + p
							Dim num2 As Short = 0S
							Dim text2 As String = "file-converter"
							modMain.msgbox2(text, num2, text2)
						End If
					Next
				End If
			End If
		End Sub

		' Token: 0x06000E85 RID: 3717 RVA: 0x000915C0 File Offset: 0x0008F7C0
		Public Sub DeleteMPTempFiles()
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				Dim mptifftemppath As String = modDeclares.SystemData.MPTIFFTEMPPATH
				IL_14:
				num2 = 3
				For Each path As String In Directory.GetFiles(mptifftemppath, "*.*", SearchOption.TopDirectoryOnly)
					IL_30:
					num2 = 4
					File.Delete(path)
					IL_39:
					num2 = 5
				Next
				IL_49:
				GoTo IL_B0
				IL_4B:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_71:
				GoTo IL_A5
				IL_73:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_83:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_73
			End Try
			IL_A5:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_B0:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000E86 RID: 3718 RVA: 0x00091698 File Offset: 0x0008F898
		Public Function CheckIfImageIsOnScreen() As Boolean
			' The following expression was wrapped in a checked-expression
			Return Not modDeclares.SystemData.CheckIfImageOnScreen OrElse Not modDeclares.SystemData.Trinamic OrElse CInt((CShort(modTrinamic.GetTrinamicLichtSensor()))) > modDeclares.SystemData.CheckIfImageOnScreenThreshold
		End Function

		' Token: 0x06000E87 RID: 3719 RVA: 0x000916E0 File Offset: 0x0008F8E0
		Private Function GetEncoderInfo(mimeType As String) As ImageCodecInfo
			Dim imageEncoders As ImageCodecInfo() = ImageCodecInfo.GetImageEncoders()
			For i As Integer = 0 To imageEncoders.Length - 1
				If Operators.CompareString(imageEncoders(i).MimeType, mimeType, False) = 0 Then
					Return imageEncoders(i)
				End If
			Next
			Return Nothing
		End Function

		' Token: 0x06000E88 RID: 3720 RVA: 0x0009171C File Offset: 0x0008F91C
		Public Sub SaveAsTiff(img As Image, f As String)
			Dim encoderInfo As Object = modMain.GetEncoderInfo("image/tiff")
			Dim compression As System.Drawing.Imaging.Encoder = System.Drawing.Imaging.Encoder.Compression
			Dim obj As Object = New EncoderParameters(1)
			Dim obj2 As Object = New EncoderParameter(compression, 6L)
			NewLateBinding.LateSet(obj, Nothing, "Param", New Object() { 0, obj2 }, Nothing, Nothing)
			img.Save(f, CType(encoderInfo, ImageCodecInfo), CType(obj, EncoderParameters))
		End Sub

		' Token: 0x06000E89 RID: 3721 RVA: 0x0009177C File Offset: 0x0008F97C
		Public Function FindMPTIFFs(path As String) As Long
			modMain.cntMPTIFFs = 0L
			Return modMain.rFindMPTIFFs(path)
		End Function

		' Token: 0x06000E8A RID: 3722 RVA: 0x00091798 File Offset: 0x0008F998
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function rFindMPTIFFs(path As String) As Long
			Dim text As String = FileSystem.Dir(path + "\*.*", Microsoft.VisualBasic.FileAttribute.Normal)
			Dim num As Long
			While Operators.CompareString(text, "", False) <> 0
				' The following expression was wrapped in a unchecked-expression
				If(If(-If(((Operators.CompareString(text, ".", False) <> 0 And Operators.CompareString(text, "..", False) <> 0) > False), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal), Microsoft.VisualBasic.FileAttribute.[ReadOnly], Microsoft.VisualBasic.FileAttribute.Normal) And (FileSystem.GetAttr(path + "\" + text) And Microsoft.VisualBasic.FileAttribute.Directory)) <= Microsoft.VisualBasic.FileAttribute.Normal AndAlso (Operators.CompareString(Strings.Right(text, 3).ToUpper(), "TIF", False) = 0 Or Operators.CompareString(Strings.Right(text, 4).ToUpper(), "TIFF", False) = 0) Then
					Dim numberOfPagesInTIFF As Long = modMain.GetNumberOfPagesInTIFF(path + "\" + text)
					If numberOfPagesInTIFF > 1L Then
						modMain.cntMPTIFFs += 1L
						modMain.MPTIFFs(CInt(modMain.cntMPTIFFs)) = path + "\" + text
						num += numberOfPagesInTIFF
					End If
				End If
				text = FileSystem.Dir()
			End While
			For Each path2 As String In Directory.GetDirectories(path)
				num += modMain.rFindMPTIFFs(path2)
			Next
			Return num
		End Function

		' Token: 0x06000E8B RID: 3723 RVA: 0x000918B4 File Offset: 0x0008FAB4
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function ConvertLogToExcel(infile As String, outfile As String) As Boolean
			Dim expression As String = ""
			Dim fileNameWithoutExtension As String = Path.GetFileNameWithoutExtension(infile)
			outfile = Path.GetDirectoryName(infile) + "\Roll " + fileNameWithoutExtension + " Index.xlsx"
			Dim result As Boolean = True
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), infile, OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
			FileSystem.Input(CInt(num), expression)
			Dim array As String() = Strings.Split(expression, ";", -1, Microsoft.VisualBasic.CompareMethod.Binary)
			Dim text As String = array(0)
			Dim num2 As Long = CLng(Convert.ToInt32(array(1)))
			Dim num3 As Long = CLng(Convert.ToInt32(array(2)))
			Dim num4 As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num4), "d:\temp\xlsx.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
			Dim text2 As String = outfile
			Dim xlworkbook As XLWorkbook = New XLWorkbook()
			Dim ixlworksheet As IXLWorksheet = xlworkbook.Worksheets.Add("Index")
			ixlworksheet.Column("A").Width = 35.0
			ixlworksheet.Column("B").Width = 20.0
			ixlworksheet.Column("C").Width = 20.0
			Dim num5 As Integer = 1
			Color.FromArgb(255, 192, 192, 192)
			Dim num8 As Long
			Dim num9 As Long
			While Not FileSystem.EOF(CInt(num))
				FileSystem.Input(CInt(num), expression)
				Dim array2 As String() = Strings.Split(expression, ";", -1, Microsoft.VisualBasic.CompareMethod.Binary)
				Dim text3 As String = array2(0)
				Dim num6 As Long
				Dim num7 As Long

					num6 = CLng(Convert.ToInt32(array2(1)))
					num7 = CLng(Convert.ToInt32(array2(2)))

				If Operators.CompareString(text, text3, False) = 0 Then
					num8 = num6
					num9 = num7
				Else
					FileSystem.PrintLine(CInt(num4), New Object() { String.Concat(New String() { Path.GetFileName(text), ";1;", fileNameWithoutExtension, ".", num3.ToString() }) })
					fileNameWithoutExtension + "." + num3.ToString()
					ixlworksheet.Cell("A" + num5.ToString()).Value = Path.GetFileName(text)
					ixlworksheet.Cell("B" + num5.ToString()).Value = "1"
					ixlworksheet.Cell("C" + num5.ToString()).SetDataType(0)
					ixlworksheet.Cell("C" + num5.ToString()).Style.Alignment.Horizontal = 7
					ixlworksheet.Cell("C" + num5.ToString()).Value = fileNameWithoutExtension + "-" + num3.ToString()
					ixlworksheet.Cell("A" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
					ixlworksheet.Cell("B" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
					ixlworksheet.Cell("C" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
					num5 += 1
					If num8 > 1L Then
						FileSystem.PrintLine(CInt(num4), New Object() { String.Concat(New String() { Path.GetFileName(text), ";", num8.ToString(), ";", fileNameWithoutExtension, "-", num9.ToString() }) })
						ixlworksheet.Cell("A" + num5.ToString()).Value = Path.GetFileName(text)
						ixlworksheet.Cell("B" + num5.ToString()).Value = num8.ToString()
						ixlworksheet.Cell("C" + num5.ToString()).SetDataType(0)
						ixlworksheet.Cell("C" + num5.ToString()).Value = fileNameWithoutExtension + "-" + num9.ToString()
						ixlworksheet.Cell("C" + num5.ToString()).Style.Alignment.Horizontal = 7
						num5 += 1
					End If
					text = text3
					num3 = num7
					num8 = 1L
				End If
			End While
			FileSystem.PrintLine(CInt(num4), New Object() { String.Concat(New String() { Path.GetFileName(text), ";1;", fileNameWithoutExtension, "-", num3.ToString() }) })
			Color.FromArgb(255, 255, 255, 255)
			ixlworksheet.Cell("A" + num5.ToString()).Value = Path.GetFileName(text)
			ixlworksheet.Cell("B" + num5.ToString()).Value = "1"
			ixlworksheet.Cell("C" + num5.ToString()).Style.Alignment.Horizontal = 7
			ixlworksheet.Cell("C" + num5.ToString()).SetDataType(0)
			ixlworksheet.Cell("C" + num5.ToString()).Value = fileNameWithoutExtension + "-" + num3.ToString()
			ixlworksheet.Cell("A" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
			ixlworksheet.Cell("B" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
			ixlworksheet.Cell("C" + num5.ToString()).Style.Fill.BackgroundColor = XLColor.LightGray
			ixlworksheet.Cell("C" + num5.ToString()).Style.Alignment.Horizontal = 7
			num5 += 1
			If num8 > 1L Then
				FileSystem.PrintLine(CInt(num4), New Object() { String.Concat(New String() { Path.GetFileName(text), ";", num8.ToString(), ";", fileNameWithoutExtension, "-", num9.ToString() }) })
				ixlworksheet.Cell("A" + num5.ToString()).Value = Path.GetFileName(text)
				ixlworksheet.Cell("B" + num5.ToString()).Value = num8.ToString()
				ixlworksheet.Cell("C" + num5.ToString()).SetDataType(0)
				ixlworksheet.Cell("C" + num5.ToString()).Style.Alignment.Horizontal = 7
				ixlworksheet.Cell("C" + num5.ToString()).Value = fileNameWithoutExtension + "-" + num9.ToString()
				num5 += 1
			End If
			xlworkbook.SaveAs(text2)
			FileSystem.FileClose(New Integer() { CInt(num) })
			FileSystem.FileClose(New Integer() { CInt(num4) })
			Return result
		End Function

		' Token: 0x06000E8C RID: 3724 RVA: 0x0009200C File Offset: 0x0009020C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub CreateAnnoFile(fname As String, sim As String, dup As String)
			Dim num As Integer = FileSystem.FreeFile()
			FileSystem.FileOpen(num, fname + ".anno", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
			FileSystem.PrintLine(num, New Object() { sim })
			FileSystem.PrintLine(num, New Object() { dup })
			FileSystem.FileClose(New Integer() { num })
		End Sub

		' Token: 0x040008CC RID: 2252
		Public ProtIndex As Integer = 1

		' Token: 0x040008CD RID: 2253
		Public mppages As Long

		' Token: 0x040008CE RID: 2254
		Public temppath As String

		' Token: 0x040008CF RID: 2255
		Public frmcomm1 As frmComm

		' Token: 0x040008D0 RID: 2256
		Public lib1 As PDFLibrary

		' Token: 0x040008D1 RID: 2257
		Public LastloadedRasterFile As String = Conversions.ToString(0)

		' Token: 0x040008D2 RID: 2258
		Public LastLoadedPDF As String

		' Token: 0x040008D3 RID: 2259
		Public LastLoadedPDFPage As Long

		' Token: 0x040008D4 RID: 2260
		Public CancelDuplex As Boolean = False

		' Token: 0x040008D5 RID: 2261
		Public CancelMPTIFF As Boolean = False

		' Token: 0x040008D6 RID: 2262
		Public DoCheckImage As Boolean

		' Token: 0x040008D7 RID: 2263
		Public CurFileNameLoaded As String

		' Token: 0x040008D8 RID: 2264
		Public CurPageLoaded As Integer

		' Token: 0x040008D9 RID: 2265
		Public PreCacheHandle As Integer

		' Token: 0x040008DA RID: 2266
		Public ForcePDFRenderer As Boolean = False

		' Token: 0x040008DB RID: 2267
		Public SelImage As Integer

		' Token: 0x040008DC RID: 2268
		Public HeaderCount As Short

		' Token: 0x040008DD RID: 2269
		Public RecordCount As Short

		' Token: 0x040008DE RID: 2270
		Public TrailerCount As Short

		' Token: 0x040008DF RID: 2271
		Public Headers As String() = New String(20) {}

		' Token: 0x040008E0 RID: 2272
		Public Records As String() = New String(20) {}

		' Token: 0x040008E1 RID: 2273
		Public Trailers As String() = New String(20) {}

		' Token: 0x040008E2 RID: 2274
		Public SiColor As Integer

		' Token: 0x040008E3 RID: 2275
		Public gl_im As Tiff = Nothing

		' Token: 0x040008E4 RID: 2276
		Public glImage As Image = Nothing

		' Token: 0x040008E5 RID: 2277
		Public glImage_clone As Image

		' Token: 0x040008E6 RID: 2278
		Public raster As Integer()

		' Token: 0x040008E7 RID: 2279
		Private codes As Long() = New Long(9) {}

		' Token: 0x040008E8 RID: 2280
		Private lastmptif As String = ""

		' Token: 0x040008E9 RID: 2281
		Private lastpcount As Integer

		' Token: 0x040008EA RID: 2282
		Private MPTIFFs As String() = New String(100) {}

		' Token: 0x040008EB RID: 2283
		Private cntMPTIFFs As Long
	End Module
End Namespace
