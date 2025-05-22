While True
    num97 -= 1S
    Dim num98 As Short
    If Not modMain.CheckIfImageIsOnScreen() Then
        text = "Image couldn't not be detected on Exposure-Monitor!"
        num98 = 2S
        value = "file-converter"
        Dim num99 As Integer = CInt(modMain.msgbox2(text, num98, value))
        If num99 = 4 Then
            GoTo IL_3F13
        End If
        If num99 = 3 Then
            value = "Stop exposure Process?"
            num98 = 1S
            text = "file-converter"
            If modMain.msgbox2(value, num98, text) = 1S Then
                modDeclares.DoCancel = True
            End If
        End If
    End If
    If Not Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn))) Then
        Exit For
    End If
    If num97 = 0S Then
        GoTo Block_251
    End If
    Dim operand As Object = False
    Dim retryFirstLevel As Short
    If modDeclares.SystemData.ExtendedVacuumHandling Then
        retryFirstLevel = modDeclares.SystemData.RetryFirstLevel
    End If
    num98 = retryFirstLevel
    Dim frmSkipImage As frmSkipImage

        For num100 As Short = 1S To num98
            If modDeclares.SystemData.SMCI Then
                modSMCi.VakuumAusSMCi()
                modSMCi.MagnetAusSMCi()
            End If
            modMultiFly.ClearOutputsMFY()
            modDeclares.Sleep(100)
            modMultiFly.VakuumPumpeAnMFY()
            modMultiFly.VakuumVentilAnMFY()
            If modDeclares.SystemData.SMCI Then
                modSMCi.VakuumAnSMCi()
            End If
            If modDeclares.SystemData.SMCI Then
                modSMCi.MagnetAnSMCi()
            End If
            If Conversions.ToBoolean(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn)) Then
                operand = True
                Exit For
            End If
        Next
        If Not Conversions.ToBoolean(Operators.NotObject(operand)) Then
            GoTo IL_49E8
        End If
        If modDeclares.SystemData.ExtendedVacuumHandling Then
            Dim lblFilmNr As Label = MyProject.Forms.frmFilming.lblFilmNr
            text = lblFilmNr.Text
            num29 = modDeclares.SystemData.RetrySecondLevel - CInt(num97)
            num76 = 2S
            modExpose.AddVacError(text, num29, num76, modDeclares.Images(i).DokumentName, modDeclares.Images(i).page, num7 - num9)
            lblFilmNr.Text = text
        End If
        MyProject.Forms.frmImage.Hide()
        frmSkipImage = New frmSkipImage()
        frmSkipImage.SetPosition()
        frmSkipImage.SetPortrait(modDeclares.SystemData.portrait(CInt(num2)))
        frmSkipImage.Show()
        Application.DoEvents()
        modDeclares.Sleep(modDeclares.SystemData.WaitAfterDraw)
        modSMCi.LEDAnSMCi()

    Dim num81 As Integer
    If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
        modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
        If modDeclares.SystemData.SmallShutter Then
            num = 1 - num
        End If
        If num22 = 0.0 Then
            num76 = 2S
            num29 = 0
            num81 = 0
            Dim flag17 As Boolean = modMultiFly.FahreMotor(num76, modDeclares.SystemData.belichtung, verschlussgeschw, num, num29, num81, modDeclares.SystemData.VResolution)
            While True
                num76 = 2S
                If Not modMultiFly.MotorIsRunning(num76) Then
                    Exit For
                End If
                Application.DoEvents()
            End While
        Else
            num76 = 2S
            num81 = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
            num29 = 0
            num77 = 0
            Dim flag17 As Boolean = modMultiFly.FahreMotor(num76, num81, verschlussgeschw, num, num29, num77, modDeclares.SystemData.VResolution)
            While True
                num76 = 2S
                If Not modMultiFly.MotorIsRunning(num76) Then
                    Exit For
                End If
                Application.DoEvents()
            End While
            modDeclares.Sleep(CInt(Math.Round(num22 * 1000.0)))
            num76 = 2S
            num77 = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
            num29 = 0
            num81 = 0
            flag17 = modMultiFly.FahreMotor(num76, num77, verschlussgeschw, num, num29, num81, modDeclares.SystemData.VResolution)
            While True
                num76 = 2S
                If Not modMultiFly.MotorIsRunning(num76) Then
                    Exit For
                End If
                Application.DoEvents()
            End While
        End If
    End If
    modSMCi.LEDAusSMCi()
    Dim exposeEndSymbols As Boolean = modExpose.ExposeEndSymbols
    frmSkipImage.Close()
    Application.DoEvents()
    If CInt(num3) = modDeclares.SystemData.schlitze - 1 Then
        text3 = ChrW(25) & "="
        If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
            Dim num101 As Short
            If modDeclares.SystemData.SMCI Then
                num101 = 0S
                If modSMCi.VerschlussIstAufNullpunktSMCi() Then
                    num101 = 1S
                End If
            Else
                modMultiFly.Comm_Send(text3)
                num81 = 0
                text3 = modMultiFly.Comm_Read(num81, True)
                num101 = CShort(Strings.Asc(text3))
            End If
            If(num101 And 1S) = 0S Then
                flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
                modMultiFly.VNullpunkt(flag, num2)
            End If
            num3 = 0S
        End If
    Else
        num3 += 1S
    End If
    modDeclares.Outputs = 0
    text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
    modMultiFly.Comm_Send(text3)
    num81 = 0
    text3 = modMultiFly.Comm_Read(num81, True)
    If modDeclares.SystemData.SMCI Then
        modSMCi.VakuumAusSMCi()
        modSMCi.MagnetAusSMCi()
    End If
    modDeclares.Sleep(500)
    Dim num102 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.VacSteps) * modDeclares.SystemData.schrittepromm(CInt(num2))))
    If Math.Abs(num5) >= 1.0 Then
        ' The following expression was wrapped in a unchecked-expression
        num102 = CInt(Math.Round(CDbl(num20) + 1.0 * num5 / Math.Abs(num5)))

            num5 -= 1.0 * num5 / Math.Abs(num5)

    End If
    If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
        modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
        value8 = num102
        num76 = 1S
        Dim num103 As Integer
        Dim right As Object
        num81 = Conversions.ToInteger(Operators.AddObject(num102 + num103, right))
        num29 = modMultiFly.GetSpeedFromSteps(num102, modDeclares.SystemData.filmspeed(CInt(num2)))
        num77 = 1
        num80 = 0
        num79 = 0
        If Not modMultiFly.FahreMotor(num76, num81, num29, num77, num80, num79, modDeclares.SystemData.FResolution(CInt(num2))) Then
            GoTo Block_273
        End If

            ' The following expression was wrapped in a checked-expression
            num9 -= Conversions.ToDouble(Operators.AddObject(num102 + num103, right)) / modDeclares.SystemData.schrittepromm(CInt(num2)) / 1000.0
            While True
                num76 = 1S
                If Not modMultiFly.MotorIsRunning(num76) Then
                    Exit For
                End If
                Application.DoEvents()
            End While

    End If
    num10 -= 1
    modMultiFly.VakuumPumpeAnMFY()
    modMultiFly.VakuumVentilAnMFY()
    If modDeclares.SystemData.SMCI Then
        modSMCi.VakuumAnSMCi()
    End If
    If modDeclares.SystemData.SMCI Then
        modSMCi.MagnetAnSMCi()
    End If
    MyProject.Forms.frmImage.Show()
    Application.DoEvents()
End While