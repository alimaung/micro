Imports System
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200004B RID: 75
	Friend NotInheritable Module modSMCi
		' Token: 0x06000EB8 RID: 3768 RVA: 0x00094CD8 File Offset: 0x00092ED8
		Public Function GetSMCAnswer(ByRef Answer As String) As Boolean
			Dim result As Boolean = True
			Answer = ""
			Dim num As Integer = modDeclares.timeGetTime()
			While True
				Dim array As Char() = New Char(128) {}
				MyProject.Forms.frmComm.MSCommSMCi.Read(array, 0, 128)
				Dim length As Integer
				Answer += Strings.Left(New String(array), length)
				If modDeclares.timeGetTime() - num > 500 Then
					Exit For
				End If
				If Operators.CompareString(Strings.Right(Answer, 1), vbCr, False) = 0 Then
					Return result
				End If
			End While
			result = False
			Return result
		End Function

		' Token: 0x06000EB9 RID: 3769 RVA: 0x00094D58 File Offset: 0x00092F58
		Public Function SendSMC(ByRef cmd As String) As Object
			If modDeclares.SystemData.SMCI Then
				MyProject.Forms.frmComm.MSCommSMCi.Write(cmd + vbCr)
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000EBA RID: 3770 RVA: 0x00094D94 File Offset: 0x00092F94
		Public Function SetAusgang(ByRef Nr As Short, ByRef wert As Boolean, ByRef Controller As Short) As Boolean
			Dim result As Boolean = False
			Dim num As Integer
			If Nr = 1S Then
				num = 65536
			End If
			If Nr = 2S Then
				num = 131072
			End If
			If Nr = 3S Then
				num = 262144
			End If
			If modDeclares.SystemData.SMCI Then
				If wert Then
					modDeclares.SMCiAusgaenge(CInt(Controller)) = (modDeclares.SMCiAusgaenge(CInt(Controller)) Or num)
				Else
					modDeclares.SMCiAusgaenge(CInt(Controller)) = (modDeclares.SMCiAusgaenge(CInt(Controller)) And Not num)
				End If
				Dim text As String = "#" + Conversions.ToString(CInt(Controller)) + "Y" + Support.Format(modDeclares.SMCiAusgaenge(CInt(Controller)), "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				modSMCi.SendSMC(text)
				Dim text2 As String
				modSMCi.GetSMCAnswer(text2)
			End If
			Return result
		End Function

		' Token: 0x06000EBB RID: 3771 RVA: 0x00094E3C File Offset: 0x0009303C
		Public Function GetEingang(ByRef Nr As Short, ByRef Controller As Short) As Boolean
			Dim array As Boolean() = New Boolean(6) {}
			modSMCi.GetEingaenge(array, Controller)
			Return array(CInt(Nr))
		End Function

		' Token: 0x06000EBC RID: 3772 RVA: 0x00094E60 File Offset: 0x00093060
		Public Function GetEingaenge(ByRef eingaenge As Boolean(), ByRef Controller As Short) As Boolean
			Dim text As String = "#" + Support.Format(Controller, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "ZY"
			modSMCi.SendSMC(text)
			Dim str As String
			modSMCi.GetSMCAnswer(str)
			Dim num As Integer = CInt(Math.Round(Conversion.Val(Strings.Mid(str, 5))))
			Dim num2 As Integer = 1
			Dim num3 As Integer = 1
			Do
				If(num And num2) <> 0 Then
					eingaenge(num3) = True
				Else
					eingaenge(num3) = False
				End If
				num2 *= 2
				num3 += 1
			Loop While num3 <= 6
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EBD RID: 3773 RVA: 0x00094EE0 File Offset: 0x000930E0
		Public Sub FahreFilmMotor(ByRef Schritte As Long, ByRef Freq As Integer, res As Integer)
			If modDeclares.SystemData.Trinamic Then
				modTrinamic.FahreFilmMotorTrinamic(Schritte, Freq, res)
				Return
			End If
			Dim text As String = "#1y1"
			modSMCi.SendSMC(text)
			Dim text2 As String
			modSMCi.GetSMCAnswer(text2)
			text = "#1p1"
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#1s" + Support.Format(Schritte, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#1o" + Conversions.ToString(Freq)
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#1A"
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
		End Sub

		' Token: 0x06000EBE RID: 3774 RVA: 0x00094F98 File Offset: 0x00093198
		Public Sub FahreVerschlussMotor(ByRef Schritte As Integer, ByRef Freq As Integer, ByRef Richtung As Integer, ByRef res As Integer)
			If modDeclares.SystemData.Trinamic Then
				modTrinamic.FahreVerschlussMotorTrinamic(Schritte, Freq, Richtung, res)
				Return
			End If
			Dim text As String = "#2y1"
			modSMCi.SendSMC(text)
			Dim text2 As String
			modSMCi.GetSMCAnswer(text2)
			text = "#2p1"
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#2s" + Support.Format(Schritte, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#2d" + Support.Format(Richtung, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#2o" + Conversions.ToString(Freq)
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			text = "#2A"
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text2)
			Dim num As Short = 2S
			modSMCi.WaitMotorStopSMCi(num)
		End Sub

		' Token: 0x06000EBF RID: 3775 RVA: 0x00095088 File Offset: 0x00093288
		Public Function FahreVerschlussMotorAufNullpunkt() As Object
			If Not modSMCi.VerschlussIstAufNullpunktSMCi() Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.FahreVerschlussMotorAufNullpunktTrinamic()
				Else
					Dim text As String = "#2y1"
					modSMCi.SendSMC(text)
					Dim text2 As String
					modSMCi.GetSMCAnswer(text2)
					text = "#2s" + Support.Format(4000, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2p1"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2l8192"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2u100"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2o2000"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2A"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					Dim num As Short = 2S
					modSMCi.WaitMotorStopSMCi(num)
					text = "#2l16384"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
					text = "#2D0"
					modSMCi.SendSMC(text)
					modSMCi.GetSMCAnswer(text2)
				End If
			End If
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000EC0 RID: 3776 RVA: 0x000951A4 File Offset: 0x000933A4
		Public Function WaitMotorStopSMCi(ByRef Nr As Short) As Object
			Dim motorPosSMCi As Integer
			Dim motorPosSMCi2 As Integer
			Do
				motorPosSMCi = modSMCi.GetMotorPosSMCi(Nr)
				modDeclares.Sleep(50)
				motorPosSMCi2 = modSMCi.GetMotorPosSMCi(Nr)
			Loop While motorPosSMCi <> motorPosSMCi2
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000EC1 RID: 3777 RVA: 0x000951CC File Offset: 0x000933CC
		Public Function IsMotorRunningSMCi(ByRef Nr As Short) As Object
			Dim motorPosSMCi As Integer = modSMCi.GetMotorPosSMCi(Nr)
			modDeclares.Sleep(50)
			Dim motorPosSMCi2 As Integer = modSMCi.GetMotorPosSMCi(Nr)
			Dim result As Object
			If motorPosSMCi = motorPosSMCi2 Then
				result = False
			Else
				result = True
			End If
			Return result
		End Function

		' Token: 0x06000EC2 RID: 3778 RVA: 0x00095204 File Offset: 0x00093404
		Public Sub ResetMotorPosSMCi(ByRef Nr As Short)
			Dim text As String = "#" + Support.Format(Nr, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "D0"
			modSMCi.SendSMC(text)
			modSMCi.GetSMCAnswer(text)
		End Sub

		' Token: 0x06000EC3 RID: 3779 RVA: 0x00095244 File Offset: 0x00093444
		Public Function GetMotorPosSMCi(ByRef Nr As Short) As Integer
			Dim str As String = "#" + Support.Format(Nr, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "C"
			modSMCi.SendSMC(str)
			modSMCi.GetSMCAnswer(str)
			Return CInt(Math.Round(Conversion.Val(Strings.Mid(str, 3))))
		End Function

		' Token: 0x06000EC4 RID: 3780 RVA: 0x00095298 File Offset: 0x00093498
		Private Function MFY2Nanotec(ByRef Freq As Integer) As Integer
			Dim num As Double = CDbl(Freq)
			num = 1.0 / num * 10000.0
			num *= modDeclares.SystemData.NanoFactor
			Return CInt(Math.Round(num))
		End Function

		' Token: 0x06000EC5 RID: 3781 RVA: 0x000952D8 File Offset: 0x000934D8
		Public Function VakuumAnSMCi() As Boolean
			If modDeclares.SystemData.Trinamic Then
				modTrinamic.VakuumAnTrinamic()
			Else
				Dim num As Short = 3S
				Dim flag As Boolean = True
				Dim num2 As Short = 2S
				modSMCi.SetAusgang(num, flag, num2)
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EC6 RID: 3782 RVA: 0x0009530C File Offset: 0x0009350C
		Public Function VakuumAusSMCi() As Boolean
			If Not modDeclares.UseDebug Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.VakuumAusTrinamic()
				Else
					Dim num As Short = 3S
					Dim flag As Boolean = False
					Dim num2 As Short = 2S
					modSMCi.SetAusgang(num, flag, num2)
				End If
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EC7 RID: 3783 RVA: 0x00095348 File Offset: 0x00093548
		Public Function MagnetAnSMCi() As Boolean
			If modDeclares.SystemData.CheckVakuum Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.MagnetAnTrinamic()
				Else
					Dim num As Short = 1S
					Dim flag As Boolean = True
					Dim num2 As Short = 1S
					modSMCi.SetAusgang(num, flag, num2)
				End If
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EC8 RID: 3784 RVA: 0x00095388 File Offset: 0x00093588
		Public Function MagnetAusSMCi() As Boolean
			If modDeclares.SystemData.CheckVakuum Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.MagnetAusTrinamic()
				Else
					Dim num As Short = 1S
					Dim flag As Boolean = False
					Dim num2 As Short = 1S
					modSMCi.SetAusgang(num, flag, num2)
				End If
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000EC9 RID: 3785 RVA: 0x000953C8 File Offset: 0x000935C8
		Public Function LEDAnSMCi() As Boolean
			Dim result As Boolean = True
			If Not modDeclares.SystemData.SMCI And Not modDeclares.SystemData.Trinamic Then
				modDeclares.Outputs = modDeclares.Outputs Or 8
				Dim left As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(left)
				Dim num As Integer = 1
				left = modMultiFly.Comm_Read(num, False)
				If Operators.CompareString(left, "", False) = 0 Then
					result = False
				End If
			ElseIf modDeclares.SystemData.SMCI Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.LEDAnTrinamic()
				Else
					Dim num2 As Short = 1S
					Dim flag As Boolean = True
					Dim num3 As Short = 2S
					modSMCi.SetAusgang(num2, flag, num3)
				End If
			End If
			Return result
		End Function

		' Token: 0x06000ECA RID: 3786 RVA: 0x00095474 File Offset: 0x00093674
		Public Function LEDAusSMCi() As Boolean
			If Not modDeclares.SystemData.SMCI And Not modDeclares.SystemData.Trinamic Then
				modDeclares.Outputs = modDeclares.Outputs And -9
				Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
			ElseIf modDeclares.SystemData.SMCI Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.LEDAusTrinamic()
				Else
					Dim num2 As Short = 1S
					Dim flag As Boolean = False
					Dim num3 As Short = 2S
					modSMCi.SetAusgang(num2, flag, num3)
				End If
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000ECB RID: 3787 RVA: 0x00095510 File Offset: 0x00093710
		Public Function ButlerAnSMCi() As Boolean
			If modDeclares.SystemData.Trinamic Then
				modTrinamic.ButlerAnTrinamic()
			Else
				Dim num As Short = 2S
				Dim flag As Boolean = True
				Dim num2 As Short = 2S
				modSMCi.SetAusgang(num, flag, num2)
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000ECC RID: 3788 RVA: 0x00095544 File Offset: 0x00093744
		Public Function ButlerAusSMCi() As Boolean
			If modDeclares.SystemData.Trinamic Then
				modTrinamic.ButlerAusTrinamic()
			Else
				Dim num As Short = 2S
				Dim flag As Boolean = False
				Dim num2 As Short = 2S
				modSMCi.SetAusgang(num, flag, num2)
			End If
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000ECD RID: 3789 RVA: 0x00095578 File Offset: 0x00093778
		Public Function VerschlussAufNullpunktSMCi() As Boolean
			Dim num As Short = 2S
			Dim flag As Boolean = False
			Dim num2 As Short = 2S
			modSMCi.SetAusgang(num, flag, num2)
			Dim result As Boolean
			Return result
		End Function

		' Token: 0x06000ECE RID: 3790 RVA: 0x00095598 File Offset: 0x00093798
		Public Function VerschlussIstAufNullpunktSMCi() As Boolean
			Dim result As Boolean
			If modDeclares.SystemData.Trinamic Then
				result = modTrinamic.VerschlussIstAufNullpunktTrinamic()
			Else
				Dim num As Short = 2S
				Dim num2 As Short = 2S
				result = Not modSMCi.GetEingang(num, num2)
			End If
			Return result
		End Function

		' Token: 0x06000ECF RID: 3791 RVA: 0x000955CC File Offset: 0x000937CC
		Public Function VakuumOKSMCi() As Boolean
			Dim result As Boolean
			If modDeclares.SystemData.Trinamic Then
				result = modTrinamic.VakuumOKTrinamic()
			Else
				Dim num As Short = 3S
				Dim num2 As Short = 2S
				result = modSMCi.GetEingang(num, num2)
			End If
			Return result
		End Function

		' Token: 0x06000ED0 RID: 3792 RVA: 0x000955FC File Offset: 0x000937FC
		Public Function DeckelGeschlossenSMci() As Boolean
			Dim result As Boolean
			If modDeclares.SystemData.Trinamic Then
				If modDeclares.UseDebug Then
					result = True
				Else
					result = modTrinamic.DeckelGeschlossenTrinamic()
					result = modTrinamic.TrinamicSupplyVoltageOK()
				End If
			Else
				Dim num As Short = 3S
				Dim num2 As Short = 1S
				result = modSMCi.GetEingang(num, num2)
			End If
			Return result
		End Function
	End Module
End Namespace
