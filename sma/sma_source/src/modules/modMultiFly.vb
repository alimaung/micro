Imports System
Imports System.Runtime.CompilerServices
Imports System.Windows.Forms
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000048 RID: 72
	Friend NotInheritable Module modMultiFly
		' Token: 0x06000E98 RID: 3736 RVA: 0x00092324 File Offset: 0x00090524
		Public Function GetSpeedFromSteps(ByRef steps As Integer, ByRef speedo As Integer) As Integer
			Return speedo
		End Function

		' Token: 0x06000E99 RID: 3737 RVA: 0x00092338 File Offset: 0x00090538
		Public Function SetStepModeold(ByRef StepMode As Short) As Object
			If Operators.CompareString(modDeclares.FW, "1.0", False) <> 0 AndAlso Not modDeclares.SystemData.SMCI Then
				Dim num As Short = StepMode
				Dim str As String
				Select Case num
					Case 1S
						str = vbNullChar
					Case 2S
						str = "D"
					Case 3S
					Case 4S
						str = Conversions.ToString(Strings.Chr(136))
					Case Else
						If num = 8S Then
							str = Conversions.ToString(Strings.Chr(204))
						End If
				End Select
				Dim text As String = "&" + str
				modMultiFly.CleanBuffer()
				modMultiFly.Comm_Send(text)
				Dim num2 As Integer = 0
				text = modMultiFly.Comm_Read(num2, True)
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E9A RID: 3738 RVA: 0x000923E0 File Offset: 0x000905E0
		Public Function SetStepMode(ByRef StepMode1 As Short, ByRef StepMode2 As Short) As Object
			' The following expression was wrapped in a checked-statement
			If Operators.CompareString(modDeclares.FW, "1.0", False) <> 0 AndAlso Not modDeclares.SystemData.SMCI Then
				Dim num As Short = StepMode1
				Dim num2 As Short
				Dim str As String
				Select Case num
					Case 1S
						num2 = 0S
					Case 2S
						num2 = 4S
					Case 3S
					Case 4S
						str = Conversions.ToString(Strings.Chr(136))
						num2 = 8S
					Case Else
						If num = 8S Then
							str = Conversions.ToString(Strings.Chr(204))
							num2 = 12S
						End If
				End Select
				Dim num3 As Short = StepMode2
				Select Case num3
					Case 1S
						num2 += 0S
					Case 2S
						num2 += 64S
					Case 3S
					Case 4S
						str = Conversions.ToString(Strings.Chr(136))
						num2 += 128S
					Case Else
						If num3 = 8S Then
							str = Conversions.ToString(Strings.Chr(204))
							num2 += 192S
						End If
				End Select
				str = Conversions.ToString(Strings.Chr(CInt(num2)))
				Dim text As String = "&" + str
				modMultiFly.CleanBuffer()
				modMultiFly.Comm_Send(text)
				Dim num4 As Integer = 0
				text = modMultiFly.Comm_Read(num4, True)
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E9B RID: 3739 RVA: 0x00092518 File Offset: 0x00090718
		Public Function GetFirmware() As String
			Dim result As String
			If modDeclares.UseDebug Then
				result = "1.5"
			ElseIf modDeclares.SystemData.SMCI Then
				result = "1.5"
			Else
				Dim text As String = ChrW(17)
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 500
				text = modMultiFly.Comm_Read(num, True)
				If Operators.CompareString(text, "", False) <> 0 Then
					' The following expression was wrapped in a checked-expression
					' The following expression was wrapped in a unchecked-expression
					result = Conversions.ToString(Strings.Chr(CInt(Math.Round(CDbl(Strings.Asc(text)) / 16.0 + 48.0)))) + "." + Conversions.ToString(Strings.Chr(CInt((CShort((Strings.Asc(text) And 15)) + 48S))))
				Else
					result = ""
				End If
			End If
			Return result
		End Function

		' Token: 0x06000E9C RID: 3740 RVA: 0x000925D0 File Offset: 0x000907D0
		Public Function MotorIsRunning(ByRef Mot As Short) As Boolean
			' The following expression was wrapped in a checked-statement
			Dim result As Boolean
			If modDeclares.UseDebug Then
				result = False
			ElseIf modDeclares.SystemData.SMCI Then
				If modDeclares.SystemData.Trinamic Then
					Dim num As Short = 2S - Mot
					result = modTrinamic.IsMotorRunningTrinamic(num)
				Else
					result = Conversions.ToBoolean(modSMCi.IsMotorRunningSMCi(Mot))
				End If
			Else
				Dim [string] As String = ChrW(25) & ">"
				modMultiFly.CleanBuffer()
				modMultiFly.Comm_Send([string])
				Dim num2 As Integer = 0
				[string] = modMultiFly.Comm_Read(num2, True)
				Dim num3 As Short = CShort(Strings.Asc([string]))
				If Mot = 2S Then
					result = ((num3 And 1S) <> 0S)
				Else
					result = ((num3 And 16S) <> 0S)
				End If
			End If
			Return result
		End Function

		' Token: 0x06000E9D RID: 3741 RVA: 0x00092670 File Offset: 0x00090870
		Public Function WaitForVacuumOn(ByRef msecs As Integer) As Object
			Dim dateTime As DateTime = DateAndTime.Today
			Dim result As Object = True
			If Not(Not modDeclares.SystemData.CheckVakuum Or modDeclares.UseDebug Or modDeclares.CalcModus) AndAlso Not modMultiFly.VacuumOk() Then
				dateTime = DateAndTime.TimeOfDay
				Do
					modDeclares.Sleep(10)
					If modMultiFly.VacuumOk() Then
						Return result
					End If
				Loop While DateTime.FromOADate(DateAndTime.TimeOfDay.ToOADate() - dateTime.ToOADate()).ToOADate() * 24.0 * 60.0 * 60.0 * 1000.0 <= CDbl(msecs)
				result = False
			End If
			Return result
		End Function

		' Token: 0x06000E9E RID: 3742 RVA: 0x00092718 File Offset: 0x00090918
		Public Function WaitForVacuumOff(ByRef msecs As Integer) As Object
			Dim dateTime As DateTime = DateAndTime.Today
			Dim result As Object = True
			If Not(Not modDeclares.SystemData.CheckVakuum Or (modDeclares.UseDebug Or modDeclares.CalcModus)) AndAlso modMultiFly.VacuumOk() Then
				dateTime = DateAndTime.TimeOfDay
				Do
					modDeclares.Sleep(10)
					If Not modMultiFly.VacuumOk() Then
						Return result
					End If
				Loop While DateTime.FromOADate(DateAndTime.TimeOfDay.ToOADate() - dateTime.ToOADate()).ToOADate() * 24.0 * 60.0 * 60.0 * 1000.0 <= CDbl(msecs)
				result = False
			End If
			Return result
		End Function

		' Token: 0x06000E9F RID: 3743 RVA: 0x000927C0 File Offset: 0x000909C0
		Public Function VacuumOk() As Boolean
			Dim result As Boolean = True
			If Not(Not modDeclares.SystemData.CheckVakuum Or modDeclares.UseDebug) Then
				If modDeclares.SystemData.SMCI Then
					result = modSMCi.VakuumOKSMCi()
				Else
					Dim [string] As String = ChrW(25) & "="
					modMultiFly.Comm_Send([string])
					Dim num As Integer = 0
					[string] = modMultiFly.Comm_Read(num, True)
					result = ((CShort(Strings.Asc([string])) And 128S) = 0S)
				End If
			End If
			Return result
		End Function

		' Token: 0x06000EA0 RID: 3744 RVA: 0x00092828 File Offset: 0x00090A28
		Public Function FilmEnde() As Boolean
			Dim result As Boolean
			If modDeclares.CalcModus Then
				result = False
			ElseIf modDeclares.SystemData.SMCI Then
				result = False
			ElseIf modDeclares.UseDebug Then
				result = False
			Else
				Dim [string] As String = ChrW(25) & "="
				modMultiFly.Comm_Send([string])
				Dim num As Integer = 0
				[string] = modMultiFly.Comm_Read(num, True)
				result = ((Strings.Asc([string]) And 128) <> 0)
				If modDeclares.SystemData.NoHead Then
					result = False
				End If
			End If
			Return result
		End Function

		' Token: 0x06000EA1 RID: 3745 RVA: 0x0009289C File Offset: 0x00090A9C
		Public Function Comm_Send(ByRef s As String) As Object
			Dim array As Byte() = New Byte(128) {}
			If Not modDeclares.UseDebug AndAlso Not modDeclares.SystemData.SMCI Then
				Dim length As Integer = s.Length
				For i As Integer = 1 To length
					array(i) = CByte(Strings.Asc(Strings.Mid(s, i, 1)))
				Next
				modMain.frmcomm1.MSComm1.Write(array, 1, s.Length)
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000EA2 RID: 3746 RVA: 0x00092908 File Offset: 0x00090B08
		Public Function CleanBuffer() As String
			Dim array As Char() = New Char(128) {}
			If Not modDeclares.SystemData.SMCI AndAlso Not modDeclares.UseDebug AndAlso modMain.frmcomm1.MSComm1.BytesToRead > 0 Then
				Dim length As Integer = modMain.frmcomm1.MSComm1.Read(array, 0, 128)
				Strings.Left(New String(array), length)
			End If
			Dim result As String
			Return result
		End Function

		' Token: 0x06000EA3 RID: 3747 RVA: 0x0009296C File Offset: 0x00090B6C
		Public Function Comm_Read(ByRef timeout As Integer, Optional domsg As Boolean = True) As String
			' The following expression was wrapped in a checked-statement
			Dim result As String
			If Not modDeclares.UseDebug Then
				Dim timeOfDay As DateTime = DateAndTime.TimeOfDay
				If Not modDeclares.SystemData.SMCI Then
					If timeout = 0 Then
						timeout = 60
					End If
					Dim tickCount As Integer = modDeclares.GetTickCount()
					result = ""
					While modMain.frmcomm1.MSComm1.BytesToRead = 0
						Dim tickCount2 As Integer = modDeclares.GetTickCount()
						If CDbl((tickCount2 - tickCount)) / 1000.0 > CDbl(timeout) Then
							If domsg Then
								Dim text As String = String.Concat(New String() { "No communication to the file-converter motor module (timeout=", Conversions.ToString(timeout), ",time elapsed=", Conversions.ToString(CDbl((tickCount2 - tickCount)) / 1000.0), ")!" & vbCr & "Please check if all cables are connected, the file-converter is turned on and the lid is closed!" })
								Dim num As Short = 17S
								Dim text2 As String = "file-converter"
								modMain.msgbox2(text, num, text2)
							End If
							result = ""
							modDeclares.MFCommError = True
							If modDeclares.InCore Then
								modDeclares.ErrorInCore = True
								Return result
							End If
							Return result
						End If
					End While
					Dim array As Char() = New Char(128) {}
					Dim length As Integer = modMain.frmcomm1.MSComm1.Read(array, 0, 128)
					result = Strings.Left(New String(array), length)
				End If
			End If
			Return result
		End Function

		' Token: 0x06000EA4 RID: 3748 RVA: 0x00092A8C File Offset: 0x00090C8C
		Public Function StopMotor(ByRef Motor As Short) As Boolean
			If Not modDeclares.UseDebug Then
				Dim text As String
				If Motor = 1S Then
					text = "%"
				Else
					text = "$"
				End If
				modMultiFly.CleanBuffer()
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EA5 RID: 3749 RVA: 0x00092AD0 File Offset: 0x00090CD0
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function FahreMotor(ByRef Motor As Short, ByRef w As Integer, ByRef Speed As Integer, ByRef Richtung As Integer, ByRef Endschalter As Integer, ByRef Pol As Integer, ByRef res As Short) As Boolean
			Dim result As Boolean = True
			If modDeclares.SystemData.SMCI Then
				If Motor = 2S Then
					If w = 0 Then
						modSMCi.FahreVerschlussMotorAufNullpunkt()
					Else
						Dim num As Integer = CInt(res)
						modSMCi.FahreVerschlussMotor(w, Speed, Richtung, num)
						res = CShort(num)
					End If
				Else
					' The following expression was wrapped in a unchecked-expression
					Dim num2 As Long = CLng(w)
					modSMCi.FahreFilmMotor(num2, Speed, CInt(res))
					w = CInt(num2)
				End If
			Else
				Dim num3 As Integer = w * 2
				If res = 4S Then
					num3 = CInt(Math.Round(CDbl(num3) / 2.0))
				End If
				If res = 2S Then
					num3 = CInt(Math.Round(CDbl(num3) / 4.0))
				End If
				Dim text As String = Conversion.Hex(num3)
				While Strings.Len(text) < 6
					text = "0" + text
				End While
				Dim num4 As Integer = CInt(modMultiFly.GetSpTabAdr(CLng(Speed)))
				Dim num5 As Integer = 0
				If Richtung <> 0 Then
					num5 = num5 Or 128
				End If
				If Endschalter = 1 Then
					num5 = num5 Or 64
				End If
				If Pol = 1 Then
					num5 = num5 Or 32
				End If
				Dim text2 As String
				If Motor = 1S Then
					text2 = "!"
				Else
					text2 = " "
				End If
				text2 += Conversions.ToString(Strings.Chr(CInt(Math.Round(Conversion.Val("&h" + Strings.Right(text, 2))))))
				text = Strings.Left(text, 4)
				text2 += Conversions.ToString(Strings.Chr(CInt(Math.Round(Conversion.Val("&h" + Strings.Right(text, 2))))))
				text = Strings.Left(text, 2)
				text2 += Conversions.ToString(Strings.Chr(CInt(Math.Round(Conversion.Val("&h" + Strings.Right(text, 2))))))
				text2 += Conversions.ToString(Strings.Chr(num4 And 255))
				text2 += Conversions.ToString(Strings.Chr(CInt(Math.Round(CDbl((CShort((num4 And 65280)))) / 256.0 + CDbl(num5)))))
				text2 += Conversions.ToString(Strings.Chr(Speed And 255))
				text2 += Conversions.ToString(Strings.Chr(CInt(Math.Round(CDbl(CShort((Speed And 65280))) / 256.0))))
				Dim num6 As Integer = CInt(Math.Round(CDbl((60 * Speed)) / 1500.0 * CDbl(num3) / 451000.0 + 5.0))
				If num3 = 0 Then
					num6 = 5
				End If
				Dim num7 As Double = DateAndTime.TimeOfDay.ToOADate()
				modMultiFly.CleanBuffer()
				modMultiFly.Comm_Send(text2)
				Dim num As Integer = num6 * 1000
				text2 = modMultiFly.Comm_Read(num, True)
				If modDeclares.SystemData.MotorProt Then
					Dim num8 As Short = CShort(FileSystem.FreeFile())
					FileSystem.FileOpen(CInt(num8), MyProject.Application.Info.DirectoryPath + "\Motor.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
					FileSystem.PrintLine(CInt(num8), New Object() { String.Concat(New String() { "Motor ", Conversions.ToString(CInt(Motor)), ", ", Conversions.ToString(w), " Schritte, ", Conversions.ToString(Speed), " Speed, ", Conversions.ToString(CInt(res)), " Aufl., SpeedTabAdr =", Conversions.ToString(num4), ", rc=", Conversions.ToString(Strings.Asc(text2)) }) })
					FileSystem.FileClose(New Integer() { CInt(num8) })
				End If
				num = Strings.Asc(text2)
				If num <> 129 Then
					If num <> 130 Then
						DateAndTime.TimeOfDay.ToOADate()
						If Operators.CompareString(modDeclares.FW, "1.0", False) <> 0 Then
							If Motor = 1S Then
								text2 = "#"
							Else
								text2 = """"
							End If
							modMultiFly.CleanBuffer()
							modMultiFly.Comm_Send(text2)
							Dim num9 As Integer = num6 * 1000
							text2 = modMultiFly.Comm_Read(num9, True)
						End If
					Else
						Dim text3 As String = "TXT_MOTOR_ERR82"
						Dim text4 As String = modMain.GetText(text3)
						If Operators.CompareString(text4, "", False) = 0 Then
							text4 = "Weg zu klein für angestrebte Speed"
						End If
						text4 += vbCr
						text4 = text4 + "Motor = " + Conversions.ToString(CInt(Motor)) + vbCr
						text4 = text4 + "Steps = " + Conversions.ToString(w) + vbCr
						text4 = text4 + "Speed = " + Conversions.ToString(Speed) + vbCr
						text4 = text4 + "Reso = " + Conversions.ToString(CInt(res)) + vbCr
						text4 = text4 + "SpeedTabAdr = " + Conversions.ToString(num4) + vbCr
						Dim num10 As Short = 0S
						text3 = "file-converter"
						modMain.msgbox2(text4, num10, text3)
						result = False
					End If
				Else
					Dim text3 As String = "TXT_MOTOR_ERR81"
					Dim text4 As String = modMain.GetText(text3)
					If Operators.CompareString(text4, "", False) = 0 Then
						text4 = "Speed und SpeedTabAdr müssen korrelieren"
					End If
					text4 += vbCr
					text4 = text4 + "Motor = " + Conversions.ToString(CInt(Motor)) + vbCr
					text4 = text4 + "Steps = " + Conversions.ToString(w) + vbCr
					text4 = text4 + "Speed = " + Conversions.ToString(Speed) + vbCr
					text4 = text4 + "Reso = " + Conversions.ToString(CInt(res)) + vbCr
					text4 = text4 + "SpeedTabAdr = " + Conversions.ToString(num4) + vbCr
					result = False
					Dim num10 As Short = 0S
					text3 = "file-converter"
					modMain.msgbox2(text4, num10, text3)
				End If
			End If
			Return result
		End Function

		' Token: 0x06000EA6 RID: 3750 RVA: 0x00093068 File Offset: 0x00091268
		Public Sub VNullpunkt(ByRef debug1 As Boolean, ByRef kopfindex As Short)
			If Not debug1 Then
				If modDeclares.SystemData.SMCI Then
					modSMCi.FahreVerschlussMotorAufNullpunkt()
					While True
						Dim num As Short = 2S
						If Not modMultiFly.MotorIsRunning(num) Then
							Exit For
						End If
						Application.DoEvents()
					End While
					Return
				End If
				modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(kopfindex)))
				If modDeclares.SystemData.SmallShutter Then
					Dim num As Short = 2S
					Dim num2 As Integer = 0
					Dim num3 As Integer = 0
					Dim num4 As Integer = CInt((1S - modDeclares.SystemData.SmallShutterFirstDir))
					Dim num5 As Integer = 1
					Dim num6 As Integer = 1
					modMultiFly.FahreMotor(num, num2, num3, num4, num5, num6, modDeclares.SystemData.VResolution)
				Else
					Dim num As Short = 2S
					Dim num6 As Integer = 0
					Dim num5 As Integer = 0
					Dim num4 As Integer = 1
					Dim num3 As Integer = 1
					Dim num2 As Integer = 1
					modMultiFly.FahreMotor(num, num6, num5, num4, num3, num2, modDeclares.SystemData.VResolution)
				End If
				Dim timeOfDay As DateTime
				Do
					Dim num As Short = 2S
					If Not modMultiFly.MotorIsRunning(num) Then
						Exit Do
					End If
					Application.DoEvents()
					timeOfDay = DateAndTime.TimeOfDay
					modDeclares.Sleep(100)
				Loop While DateTime.FromOADate(DateAndTime.TimeOfDay.ToOADate() - timeOfDay.ToOADate()).ToOADate() * 24.0 * 60.0 * 60.0 * 1000.0 <= 2000.0
			End If
		End Sub

		' Token: 0x06000EA7 RID: 3751 RVA: 0x000931AC File Offset: 0x000913AC
		Public Sub MagnetPlatteHoch()
			If Not modDeclares.UseDebug AndAlso Not modDeclares.CalcModus AndAlso Not modDeclares.SystemData.SMCI Then
				modDeclares.Outputs = modDeclares.Outputs Or modDeclares.MagnetValue
				Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
				modDeclares.Sleep(modDeclares.SystemData.MagnetDelay)
			End If
		End Sub

		' Token: 0x06000EA8 RID: 3752 RVA: 0x00093220 File Offset: 0x00091420
		Public Sub MagnetPlatteRunter()
			If Not modDeclares.UseDebug AndAlso Not modDeclares.CalcModus AndAlso Not modDeclares.SystemData.SMCI Then
				modDeclares.Outputs = modDeclares.Outputs And Not modDeclares.MagnetValue
				Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
			End If
		End Sub

		' Token: 0x06000EA9 RID: 3753 RVA: 0x00093288 File Offset: 0x00091488
		Public Sub InitTable()
			Dim num As UInteger = 4294901760UI
			Dim num2 As UInteger = 81404UI
			Dim num3 As UShort = 4095US
			Dim num4 As UShort = CUShort((num3 << 3))
			Dim num5 As UShort = 2048US
			Dim num6 As UShort = 0US
			modMultiFly.SpeedTab(CInt(num6)) = CLng(CULng(num3))
			Dim b As Byte = 3
			While num3 > 500US
				' The following expression was wrapped in a checked-statement
				num6 += 1US
				If num6 > 8191US Then
					Exit While
				End If
				If(num3 And num5) = 0US Then
					' The following expression was wrapped in a unchecked-expression
					num5 = CUShort((CUInt(num5) >> 1))
					b += 1
					num4 = CUShort((num4 << 1))
				End If
				Dim num7 As UInteger = Convert.ToUInt32(Math.Floor(New Decimal(num / CUInt(num4))))
				Dim num8 As UInteger = CUInt(num4) * num2 >> CInt((CByte((b << 1)) + 16))
				Dim num9 As UInteger = CUInt((CULng(num) / CULng(CLng((CInt(Math.Round(num / CDbl(num4) + CUInt(num4) * num2 >> CInt((CByte((b << 1)) + 16)))))))))
				Dim num10 As UInteger = num7 + num8
				num4 = Convert.ToUInt16(Math.Floor(New Decimal(num / (num7 + num8))))
				num3 = CUShort((CUInt(num4) >> CInt((b And 15))))
				modMultiFly.SpeedTab(CInt(num6)) = CLng(CULng(num3))
			End While
		End Sub

		' Token: 0x06000EAA RID: 3754 RVA: 0x00093378 File Offset: 0x00091578
		Public Function GetSpTabAdr(Speed As Long) As Long
			' The following expression was wrapped in a checked-statement
			Dim result As Long
			If Speed = 0L Then
				result = 0L
			ElseIf Speed < 500L Or Speed > 4194L Then
				result = 0L
			Else
				Dim num As Long = 0L
				While Speed < modMultiFly.SpeedTab(CInt(num))
					num += 1L
					If num > 5999L Then
						Return 0L
					End If
				End While
				result = num
			End If
			Return result
		End Function

		' Token: 0x06000EAB RID: 3755 RVA: 0x000933CC File Offset: 0x000915CC
		Public Sub ClearOutputsMFY()
			modDeclares.Outputs = 0
			Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text)
			Dim num As Integer = 0
			text = modMultiFly.Comm_Read(num, True)
		End Sub

		' Token: 0x06000EAC RID: 3756 RVA: 0x0009340C File Offset: 0x0009160C
		Public Sub VakuumPumpeAnMFY()
			modDeclares.Outputs = modDeclares.Outputs Or 64
			Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text)
			Dim num As Integer = 0
			text = modMultiFly.Comm_Read(num, True)
		End Sub

		' Token: 0x06000EAD RID: 3757 RVA: 0x00093454 File Offset: 0x00091654
		Public Sub VakuumPumpeAusMFY()
			modDeclares.Outputs = modDeclares.Outputs And 191
			Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text)
			Dim num As Integer = 0
			text = modMultiFly.Comm_Read(num, True)
		End Sub

		' Token: 0x06000EAE RID: 3758 RVA: 0x000934A0 File Offset: 0x000916A0
		Public Sub VakuumVentilAnMFY()
			modDeclares.Outputs = modDeclares.Outputs Or 32
			Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text)
			Dim num As Integer = 0
			text = modMultiFly.Comm_Read(num, True)
		End Sub

		' Token: 0x06000EAF RID: 3759 RVA: 0x000934E8 File Offset: 0x000916E8
		Public Sub VakuumVentilAusMFY()
			modDeclares.Outputs = modDeclares.Outputs And 223
			Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text)
			Dim num As Integer = 0
			text = modMultiFly.Comm_Read(num, True)
		End Sub

		' Token: 0x040008F0 RID: 2288
		Private SpeedTab As Long() = New Long(8192) {}
	End Module
End Namespace
