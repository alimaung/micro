Imports System
Imports System.Runtime.CompilerServices
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200004E RID: 78
	Friend NotInheritable Module modTrinamic
		' Token: 0x06000ED9 RID: 3801 RVA: 0x00096858 File Offset: 0x00094A58
		Public Function SetStepperResolutionTrinamic(ByRef Motor_ As Short, ByRef Resolution As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 140S
			Dim num5 As Integer = CInt(Resolution)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDA RID: 3802 RVA: 0x0009689C File Offset: 0x00094A9C
		Public Function ResetTrinamic() As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 255S
			Dim num3 As Short = 0S
			Dim num4 As Short = 0S
			Dim num5 As Integer = 1234
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = True
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDB RID: 3803 RVA: 0x000968E4 File Offset: 0x00094AE4
		Public Function SetTargetSpeedTrinamic(ByRef Motor_ As Short, ByRef Speed As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 4S
			Dim num5 As Integer = CInt(Speed)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDC RID: 3804 RVA: 0x00096924 File Offset: 0x00094B24
		Public Function SetRefSpeedsTrinamic(ByRef Motor_ As Short, ByRef Speed1 As Short, ByRef Speed2 As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 194S
			Dim num5 As Integer = CInt(Speed1)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			num4 = 195S
			num5 = CInt(Speed2)
			num6 = CLng(num5)
			flag = False
			Dim num8 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag3 As Boolean = num8 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDD RID: 3805 RVA: 0x00096994 File Offset: 0x00094B94
		Public Function SetMaxCurrentTrinamic(ByRef Motor_ As Short, ByRef Current As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 6S
			Dim num5 As Integer = CInt(Current)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDE RID: 3806 RVA: 0x000969D4 File Offset: 0x00094BD4
		Public Function SetStandbyCurrentTrinamic(ByRef Motor_ As Short, ByRef Current As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 7S
			Dim num5 As Integer = CInt(Current)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EDF RID: 3807 RVA: 0x00096A14 File Offset: 0x00094C14
		Public Function SetMaximumAcclerationTrinamic(ByRef Motor_ As Short, ByRef Acceleration As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 5S
			Dim num5 As Integer = CInt(Acceleration)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EE0 RID: 3808 RVA: 0x00096A54 File Offset: 0x00094C54
		Public Function SetMaximumSpeedTrinamic(ByRef Motor_ As Short, Speed As Short, res As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 5S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 4S
			If num3 = 1S Then
				If res = 1S Then
					Speed = CShort(Math.Round(CDbl(Speed) / 4.0))
				End If
				If res = 2S Then
					Speed = CShort(Math.Round(CDbl(Speed) / 2.0))
				End If
				If res = 8S Then
					Speed *= 2S
				End If
			Else
				If res = 4S Then
					Speed = CShort(Math.Round(CDbl(Speed) / 2.0))
				End If
				If res = 2S Then
					Speed = CShort(Math.Round(CDbl(Speed) / 4.0))
				End If
				If res = 1S Then
					Speed = CShort(Math.Round(CDbl(Speed) / 8.0))
				End If
			End If
			Dim num5 As Integer = CInt(Speed)
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EE1 RID: 3809 RVA: 0x0001A972 File Offset: 0x00018B72
		Public Sub FahreMotorTrinamic(ByRef Motor As Short, ByRef Schritte As Short, ByRef Richtung As Short)
		End Sub

		' Token: 0x06000EE2 RID: 3810 RVA: 0x00096B1C File Offset: 0x00094D1C
		Public Function SendBinComandToTrinamic(ByRef Target As Short, ByRef Inst As Short, ByRef Motor As Short, ByRef Type1 As Short, ByRef Value As Long, Optional ByRef NoAnswer As Boolean = False) As Long
			Dim array As Byte() = New Byte(9) {}
			Dim num As Short
			Dim num2 As Short
			array(1) = CByte(Target)
			array(2) = CByte(Inst)
			array(3) = CByte(Type1)
			array(4) = CByte(Motor)
			array(5) = CByte(Math.Round(CDbl((Value And CLng((CULng(-16777216))))) / 65536.0 / 256.0))
			array(6) = CByte(Math.Round(CDbl((Value And 16711680L)) / 65536.0))
			array(7) = CByte(Math.Round(CDbl((Value And 65280L)) / 256.0))
			array(8) = CByte((Value And 255L))
			num = 0S
			num2 = 1S
			Do
				num += CShort(array(CInt(num2)))
				num2 += 1S
			Loop While num2 <= 8S
			array(9) = CByte((num And 255S))
			Return modTrinamic.SendBinToTrinamic(array, NoAnswer)
		End Function

		' Token: 0x06000EE3 RID: 3811 RVA: 0x00096BE8 File Offset: 0x00094DE8
		Public Function SendBinToTrinamic(ByRef cmd As Byte(), Optional ByRef NoAnswer As Boolean = False) As Long
			MyProject.Forms.frmComGuardian.lblToSend.Text = ""
			MyProject.Forms.frmComGuardian.lblReceived.Text = ""
			Dim result As Long
			If Not modDeclares.UseDebug Then
				Dim num As Short = 1S
				Do
					MyProject.Forms.frmComGuardian.lblToSend.Text = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(MyProject.Forms.frmComGuardian.lblToSend.Text, Interaction.IIf(cmd(CInt(num)) < 16, "0", "")), Conversion.Hex(cmd(CInt(num)))), " "))
					modMain.frmcomm1.MSCommTri.Write(cmd, CInt(num), 1)
					num += 1S
				Loop While num <= 9S
				If NoAnswer Then
					result = 0L
				Else
					Dim str As String = ""
					Dim num2 As Integer = modDeclares.GetTickCount()
					Dim i As Integer = 0
					Dim array As Byte() = New Byte(128) {}
					While i < 9
						Dim array2 As Byte() = New Byte(128) {}
						If modMain.frmcomm1.MSCommTri.BytesToRead > 0 Then
							modMain.frmcomm1.MSCommTri.Read(array2, 0, 1)
							Dim num3 As Short
							i += 1
							array(i) = array2(0)
							Dim text As String = array2.ToString()
							str += text
							num3 = CShort(Strings.Len(text))
							num = 1S
							While num <= num3
								num += 1S
							End While
						End If
						If modDeclares.GetTickCount() - num2 > 100000 Then
							Dim text2 As String = "Fehler erkannt!"
							Dim num4 As Short = 0S
							Dim text3 As String = "file-converter"
							modMain.msgbox2(text2, num4, text3)
							num2 = 0
						End If
					End While
					If(cmd(2) = 15 And cmd(4) = 1) Or (cmd(2) = 6 And cmd(3) = 3) Then
						' The following expression was wrapped in a checked-expression
						result = CLng((CInt(array(7)) * 256 + CInt(array(8))))
					Else
						result = CLng(CULng(array(8)))
					End If
					result = CLng((CInt(array(7)) * 256 + CInt(array(8))))
				End If
			End If
			Return result
		End Function

		' Token: 0x06000EE4 RID: 3812 RVA: 0x00096DCC File Offset: 0x00094FCC
		Public Sub VakuumAnTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 3S
			Dim num5 As Integer = 1
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EE5 RID: 3813 RVA: 0x00096E08 File Offset: 0x00095008
		Public Sub VakuumAusTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 3S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EE6 RID: 3814 RVA: 0x00096E44 File Offset: 0x00095044
		Public Sub LEDAnTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 0S
			Dim num5 As Integer = 1
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EE7 RID: 3815 RVA: 0x00096E80 File Offset: 0x00095080
		Public Sub LEDAusTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 0S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EE8 RID: 3816 RVA: 0x00096EBC File Offset: 0x000950BC
		Public Sub MagnetAnTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 7S
			Dim num5 As Integer = 1
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EE9 RID: 3817 RVA: 0x00096EF8 File Offset: 0x000950F8
		Public Sub MagnetAusTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 14S
			Dim num3 As Short = 2S
			Dim num4 As Short = 7S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EEA RID: 3818 RVA: 0x0001A972 File Offset: 0x00018B72
		Public Sub ButlerAnTrinamic()
		End Sub

		' Token: 0x06000EEB RID: 3819 RVA: 0x0001A972 File Offset: 0x00018B72
		Public Sub ButlerAusTrinamic()
		End Sub

		' Token: 0x06000EEC RID: 3820 RVA: 0x00096F34 File Offset: 0x00095134
		Public Function VakuumOKTrinamic() As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 15S
			Dim num3 As Short = 0S
			Dim num4 As Short = 1S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Short = CShort(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Return Conversions.ToBoolean(Interaction.IIf(num7 = 0S, True, False))
		End Function

		' Token: 0x06000EED RID: 3821 RVA: 0x00096F88 File Offset: 0x00095188
		Public Function DeckelGeschlossenTrinamic() As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 15S
			Dim num3 As Short = 0S
			Dim num4 As Short = 2S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Short = CShort(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Return Conversions.ToBoolean(Interaction.IIf(num7 = 1S, True, False))
		End Function

		' Token: 0x06000EEE RID: 3822 RVA: 0x00096FDC File Offset: 0x000951DC
		Public Function VerschlussIstAufNullpunktTrinamic() As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 15S
			Dim num3 As Short = 0S
			Dim num4 As Short = 3S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Short = CShort(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Return Conversions.ToBoolean(Interaction.IIf(num7 = 1S, True, False))
		End Function

		' Token: 0x06000EEF RID: 3823 RVA: 0x00097030 File Offset: 0x00095230
		Public Sub FahreVerschlussMotorAufNullpunktTrinamic()
			Dim num As Short = 1S
			Dim num2 As Short = 13S
			Dim num3 As Short = 0S
			Dim num4 As Short = 0S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Short = CShort(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Dim num8 As Short = num7
			num = 1S
			num2 = 13S
			num3 = 0S
			num4 = 2S
			num5 = 0
			Dim num9 As Integer = modDeclares.timeGetTime()
			Do
				' The following expression was wrapped in a unchecked-expression
				num6 = CLng(num5)
				flag = False
				Dim num10 As Short = CShort(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
				num5 = CInt(num6)
				num8 = num10
			Loop While modDeclares.timeGetTime() - num9 <= 2000 AndAlso num8 <> 0S
		End Sub

		' Token: 0x06000EF0 RID: 3824 RVA: 0x000970B4 File Offset: 0x000952B4
		Public Sub FahreVerschlussMotorTrinamic(Schritte As Integer, ByRef Freq As Integer, ByRef Richtung As Integer, ByRef Res As Integer)
			Dim num As Short = 0S
			modTrinamic.SetMaximumSpeedTrinamic(num, CShort(Freq), CShort(Res))
			Dim num2 As Short = 0S
			Dim num3 As Short = 4S
			Dim num4 As Short = 0S
			Dim num5 As Short = 1S
			If Res = 4 Then
				Schritte = CInt(Math.Round(CDbl(Schritte) / 2.0))
			End If
			If Res = 2 Then
				Schritte = CInt(Math.Round(CDbl(Schritte) / 4.0))
			End If
			If Res = 1 Then
				Schritte = CInt(Math.Round(CDbl(Schritte) / 8.0))
			End If
			Dim num6 As Integer = Schritte
			If modDeclares.SystemData.VerschlussRichtung = 1 Then
				num6 = 0 - Schritte
			End If
			Dim num7 As Long = CLng(num6)
			Dim flag As Boolean = False
			Dim num8 As Long = modTrinamic.SendBinComandToTrinamic(num2, num3, num4, num5, num7, flag)
			num6 = CInt(num7)
			Dim flag2 As Boolean = num8 <> 0L
		End Sub

		' Token: 0x06000EF1 RID: 3825 RVA: 0x00097160 File Offset: 0x00095360
		Public Function IsMotorRunningTrinamic(ByRef Motor_ As Short) As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 6S
			Dim num3 As Short = Motor_
			Dim num4 As Short = 3S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Return Conversions.ToBoolean(Interaction.IIf(num7 = 0L, False, True))
		End Function

		' Token: 0x06000EF2 RID: 3826 RVA: 0x000971B4 File Offset: 0x000953B4
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub FahreFilmMotorTrinamic(Schritte As Long, ByRef Freq As Integer, ByRef res As Integer)
			If modDeclares.SystemData.MotorProt Then
				Dim value As Object = FileSystem.FreeFile()
				FileSystem.FileOpen(Conversions.ToInteger(value), MyProject.Application.Info.DirectoryPath + "\Motor.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
				FileSystem.PrintLine(Conversions.ToInteger(value), New Object() { "Film-Motor: Schritte, " + Conversions.ToString(Schritte) })
				FileSystem.FileClose(New Integer() { Conversions.ToInteger(value) })
			End If
			Dim num As Short = 1S
			modTrinamic.SetMaximumSpeedTrinamic(num, CShort(Freq), CShort(res))
			Dim num2 As Short = 1S
			Dim num3 As Short = 4S
			Dim num4 As Short = 1S
			Dim num5 As Short = 1S
			If res = 1 Then
				Schritte = CLng(Math.Round(CDbl(Schritte) / 8.0))
			End If
			If res = 2 Then
				Schritte = CLng(Math.Round(CDbl(Schritte) / 4.0))
			End If
			If res = 4 Then
				Schritte = CLng(Math.Round(CDbl(Schritte) / 2.0))
			End If
			If res = 8 Then
				Schritte = Schritte
			End If
			Dim num6 As Long = Schritte
			Dim flag As Boolean = False
			Dim flag2 As Boolean = modTrinamic.SendBinComandToTrinamic(num2, num3, num4, num5, num6, flag) <> 0L
		End Sub

		' Token: 0x06000EF3 RID: 3827 RVA: 0x000972C4 File Offset: 0x000954C4
		Public Sub StopMotorTrinamic(ByRef Motor_ As Integer)
			Dim num As Short = 1S
			Dim num2 As Short = 3S
			Dim num3 As Short = CShort(Motor_)
			Dim num4 As Short = 0S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Dim flag2 As Boolean = num7 <> 0L
		End Sub

		' Token: 0x06000EF4 RID: 3828 RVA: 0x00097304 File Offset: 0x00095504
		Public Function SendIniDataToTrinamic(ByRef tri As modTrinamic.TrinamicInitdata) As Boolean
			Dim num As Short = 0S
			modTrinamic.SetMaxCurrentTrinamic(num, tri.M1_Fahrstrom)
			num = 1S
			modTrinamic.SetMaxCurrentTrinamic(num, tri.M2_Fahrstrom)
			num = 0S
			modTrinamic.SetStandbyCurrentTrinamic(num, tri.M1_Haltestrom)
			num = 1S
			modTrinamic.SetStandbyCurrentTrinamic(num, tri.M2_Haltestrom)
			num = 0S
			modTrinamic.SetMaximumAcclerationTrinamic(num, tri.M1_Beschleunigung)
			num = 1S
			modTrinamic.SetMaximumAcclerationTrinamic(num, tri.M2_Beschleunigung)
			num = 0S
			modTrinamic.SetRefSpeedsTrinamic(num, tri.ReferenceSpeed1, tri.ReferenceSpeed2)
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EF5 RID: 3829 RVA: 0x00097388 File Offset: 0x00095588
		Public Sub SetTrinamicData(ByRef tri As modTrinamic.TrinamicInitdata)
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\Trinamic.Ini"
			Dim text2 As String = "VERSCHLUSS"
			Dim text3 As String = "BESCHLEUNIGUNG"
			tri.M1_Beschleunigung = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 50, text))
			tri.M1_Kommentar = "Verschlussmotor"
			text3 = "VERSCHLUSS"
			text2 = "FAHRSTROM"
			tri.M1_Fahrstrom = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 50, text))
			text2 = "VERSCHLUSS"
			text3 = "HALTESTROM"
			tri.M1_Haltestrom = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 10, text))
			text3 = "VERSCHLUSS"
			text2 = "MIKROSTEPS"
			tri.M1_Mikrostepping = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 2, text))
			text2 = "VERSCHLUSS"
			text3 = "ReferenceSpeed1"
			tri.ReferenceSpeed1 = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 20, text))
			text3 = "VERSCHLUSS"
			text2 = "ReferenceSpeed2"
			tri.ReferenceSpeed2 = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 5, text))
			text2 = "FILM"
			text3 = "BESCHLEUNIGUNG"
			tri.M2_Beschleunigung = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 50, text))
			tri.M2_Kommentar = "Filmmotor"
			text3 = "FILM"
			text2 = "FAHRSTROM"
			tri.M2_Fahrstrom = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 50, text))
			text2 = "FILM"
			text3 = "HALTESTROM"
			tri.M2_Haltestrom = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 10, text))
			text3 = "FILM"
			text2 = "Beschleunigung"
			tri.M2_Beschleunigung = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 50, text))
		End Sub

		' Token: 0x06000EF6 RID: 3830 RVA: 0x00097504 File Offset: 0x00095704
		Public Function NullpunktStatusTrinamic() As Short
			Dim num As Short = 1S
			Dim num2 As Short = 13S
			Dim num3 As Short = 0S
			Dim num4 As Short = 2S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Integer = CInt(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Return CShort(num7)
		End Function

		' Token: 0x06000EF7 RID: 3831 RVA: 0x00097540 File Offset: 0x00095740
		Public Function GetTrinamicLichtSensor() As Long
			Dim num As Short = 1S
			Dim num2 As Short = 15S
			Dim num3 As Short = 1S
			Dim num4 As Short = 0S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Double = CDbl(modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag))
			num5 = CInt(num6)
			Return CLng(Math.Round(num7 / 8.0))
		End Function

		' Token: 0x06000EF8 RID: 3832 RVA: 0x0009758C File Offset: 0x0009578C
		Public Function TrinamicSupplyVoltageOK() As Boolean
			Dim num As Short = 1S
			Dim num2 As Short = 15S
			Dim num3 As Short = 1S
			Dim num4 As Short = 8S
			Dim num5 As Integer = 0
			Dim num6 As Long = CLng(num5)
			Dim flag As Boolean = False
			Dim num7 As Long = modTrinamic.SendBinComandToTrinamic(num, num2, num3, num4, num6, flag)
			num5 = CInt(num6)
			Return num7 > 200L
		End Function

		' Token: 0x040008F5 RID: 2293
		Public InitTrinamic As modTrinamic.TrinamicInitdata

		' Token: 0x0200010E RID: 270
		Public Structure TrinamicInitdata
			' Token: 0x04000ACA RID: 2762
			Public M1_Kommentar As String

			' Token: 0x04000ACB RID: 2763
			Public M1_Fahrstrom As Short

			' Token: 0x04000ACC RID: 2764
			Public M1_Haltestrom As Short

			' Token: 0x04000ACD RID: 2765
			Public M1_Mikrostepping As Short

			' Token: 0x04000ACE RID: 2766
			Public M1_Beschleunigung As Short

			' Token: 0x04000ACF RID: 2767
			Public ReferenceSpeed1 As Short

			' Token: 0x04000AD0 RID: 2768
			Public ReferenceSpeed2 As Short

			' Token: 0x04000AD1 RID: 2769
			Public M2_Kommentar As String

			' Token: 0x04000AD2 RID: 2770
			Public M2_Fahrstrom As Short

			' Token: 0x04000AD3 RID: 2771
			Public M2_Haltestrom As Short

			' Token: 0x04000AD4 RID: 2772
			Public M2_Mikrostepping As Short

			' Token: 0x04000AD5 RID: 2773
			Public M2_Beschleunigung As Short
		End Structure
	End Module
End Namespace
