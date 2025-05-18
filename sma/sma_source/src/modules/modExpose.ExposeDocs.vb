Public Sub ExposeDocs()
			New String(3) {}
			Dim fileSystemObject As FileSystemObject = New FileSystemObjectClass()
			Dim num As Integer
			If modDeclares.SystemData.SmallShutter Then
				num = CInt(modDeclares.SystemData.SmallShutterFirstDir)
			Else
				num = 1
			End If
			Dim smci As Boolean = modDeclares.SystemData.SMCI
			Dim text As String
			If modDeclares.SystemData.JPEGProcessor Then
				text = "taskkill /F /T /IM jpegaufbereiter.exe"
				modMonitorTest.ExecCmd(text)
			End If
			modMain.CheckShutterAndMonitor()
			modMultiFly.InitTable()
			modDeclares.Sleep(1000)
			Dim flag As Boolean = modDeclares.UseDebug Or modDeclares.CalcModus
			Dim num2 As Short
			modMultiFly.VNullpunkt(flag, num2)
			Dim num3 As Short = 0S
			modExpose.ExposeEndSymbols = False
			Dim num4 As Integer = 0
			Dim flag2 As Boolean = False
			Dim flag3 As Boolean = False
			If Directory.Exists(modDeclares.SystemData.PfadStartSymbole + "\TEMP") Then
				FileSystem.Kill(modDeclares.SystemData.PfadStartSymbole + "\TEMP\*.*")
			End If
			If Directory.Exists(modDeclares.SystemData.PfadEndSymbole + "\TEMP") Then
				FileSystem.Kill(modDeclares.SystemData.PfadEndSymbole + "\TEMP\*.*")
			End If
			If Directory.Exists(modDeclares.SystemData.PfadForsetzungsSymbole1 + "\TEMP") Then
				FileSystem.Kill(modDeclares.SystemData.PfadForsetzungsSymbole1 + "\TEMP\*.*")
			End If
			If Directory.Exists(modDeclares.SystemData.PfadForsetzungsSymbole2 + "\TEMP") Then
				FileSystem.Kill(modDeclares.SystemData.PfadForsetzungsSymbole2 + "\TEMP\*.*")
			End If
			modExpose.SetupStartAndEndSymbols()
			Dim num5 As Double = 0.0
			modDeclares.handle = -1L
			Dim num6 As Double
			If modDeclares.CalcModus Then
				modDeclares.SystemData.PDFReso = 50
				num6 = 0.0
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\CalcProt.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
					FileSystem.Kill(MyProject.Application.Info.DirectoryPath + "\CalcProt.txt")
				End If
			End If
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			modMain.LoadSystemData()
			Strings.InStrRev(modDeclares.glbImagePath, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary)
			Dim i As Integer = 0
			Dim num7 As Double
			Dim num8 As Integer
			Dim num9 As Double
			Dim num10 As Integer
			Dim num11 As Integer
			Dim value As String
			Dim num17 As Integer
			Dim num18 As Integer
			Dim text2 As String
			Dim num20 As Integer
			Dim verschlussgeschw As Integer
			Dim num22 As Double
			Do
				If Operators.CompareString(modDeclares.SystemData.kopfname(i), modDeclares.glbKopf, False) = 0 Then
					num2 = CShort(i)
				End If
				i += 1
			Loop While i <= 3
			text = modMain.GiveIni(lpFileName, "SYSTEM", "FILMLAENGE" + Conversions.ToString(CInt(num2)))
			num7 = Conversion.Val(modMain.KommazuPunkt(text)) - CDbl(modDeclares.SystemData.vorspann) / 100.0
			If Not Versioned.IsNumeric(modMain.GiveIni(lpFileName, "SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2)))) Then
				num8 = 0
			Else
				num8 = Conversions.ToInteger(modMain.GiveIni(lpFileName, "SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2))))
			End If
			If Versioned.IsNumeric(modMain.GiveIni(lpFileName, "SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)))) Then
				text = modMain.GiveIni(lpFileName, "SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)))
				num9 = Conversion.Val(modMain.KommazuPunkt(text))
			Else
				text = modMain.GiveIni(lpFileName, "SYSTEM", "FILmLAENGE" + Conversions.ToString(CInt(num2)))
				num9 = Conversion.Val(modMain.KommazuPunkt(text))
			End If
			If Versioned.IsNumeric(modMain.GiveIni(lpFileName, "SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)))) Then
				num10 = CInt(Math.Round(Conversion.Val(modMain.GiveIni(lpFileName, "SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2))))))
			Else
				num10 = CInt(Math.Round(Conversion.Val(modMain.GiveIni(lpFileName, "SYSTEM", "BELEGEPROFILM" + Conversions.ToString(CInt(num2))))))
			End If
			num11 = 0
			If Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(num2))), "1", False) = 0 Then
				flag2 = True
				Dim num12 As Integer = 0
				If modExpose.AnzStartSymbole > 0 AndAlso Not modDeclares.SystemData.NoSpecialSmybolesWhenContinuation Then
					num12 = modExpose.AnzStartSymbole
					modExpose.GesamtStartSymbole = CType(Utils.CopyArray(modExpose.GesamtStartSymbole, New String(num12 + 1 - 1) {}), String())
					Dim num13 As Integer = num12
					For j As Integer = 1 To num13
						modExpose.GesamtStartSymbole(j) = modExpose.StartSymbole(j)
					Next
				End If
				If modExpose.AnzFortsetzungsSymbole2 > 0 Then
					modExpose.GesamtStartSymbole = CType(Utils.CopyArray(modExpose.GesamtStartSymbole, New String(num12 + modExpose.AnzFortsetzungsSymbole2 + 1 - 1) {}), String())
					Dim num14 As Integer = num12 + 1
					Dim num15 As Integer = num12 + modExpose.AnzFortsetzungsSymbole2
					For j As Integer = num14 To num15
						modExpose.GesamtStartSymbole(j) = modExpose.FortsetzungsSymbole2(j - num12)
					Next
					num12 += modExpose.AnzFortsetzungsSymbole2
				End If
				If modDeclares.SystemData.UseStartFrame Then
					num11 = 1
				End If
				If modDeclares.SystemData.UseStartSymbole Then
					num11 += num12
				End If
				modExpose.AnzGesamtStartSymbole = num12
				text = modDeclares.ffrmFilmPreview.txtFilmNr.Text
				value = "1"
				modExpose.SetContinuationInfoFileForRefilm(text, value)
			Else
				num11 = 0
				If modDeclares.SystemData.UseAnno AndAlso modDeclares.SystemData.AnnoStyle = 4S AndAlso modDeclares.SystemData.LateAnnoNumbering Then
					If modDeclares.SystemData.UseStartFrame Then
						num11 = 1
					End If
					If modDeclares.SystemData.UseStartSymbole Then
						num11 += modExpose.GetNumberOfStartSymbols(modDeclares.SystemData.PfadStartSymbole, flag2)
					End If
				End If
			End If
			If modDeclares.CalcModus Then
				num9 = 1000000.0
			End If
			Dim str As String = "0"
			value = modMain.GiveIni(lpFileName, "SYSTEM", "freierestframes" + Conversions.ToString(CInt(num2)))
			Dim num16 As Integer = CInt(Math.Round(Conversion.Val(str + modMain.KommazuPunkt(value))))
			num17 = CInt(Math.Round(Conversion.Val(modDeclares.ffrmFilmPreview.txtFilmNr.Text)))
			modDeclares.SystemData.AnnoFontSize = 70S
			MyProject.Forms.frmFilming.lblFilmNr.Text = Conversions.ToString(num17)
			Dim flag4 As Boolean = False
			If Operators.ConditionalCompareObjectEqual(modDeclares.ffrmFilmPreview.cmdRefilm.Tag, "", False) Then
				num18 = -1
				Dim imagecount As Integer = modDeclares.imagecount
				i = 0
				While i <= imagecount
					If Operators.CompareString(modDeclares.Images(i).Name, modDeclares.ffrmFilmPreview.txtLastDocument.Text, False) = 0 And CDbl(modDeclares.Images(i).page) = Conversion.Val(modDeclares.ffrmFilmPreview.txtPage.Text) Then
						num18 = i
						flag4 = True
						Exit While
					End If
					i += 1
				End While
				If Not flag4 Then
					Dim imagecount2 As Integer = modDeclares.imagecount
					i = 0
					While i <= imagecount2
						If Operators.CompareString(Support.Format(modDeclares.Images(i).Name, "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(modDeclares.ffrmFilmPreview.txtLastDocument.Text, "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) > 0 Then
							num18 = i - 1
							flag4 = True
							Exit While
						End If
						If Operators.CompareString(Support.Format(modDeclares.Images(i).Name, "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(modDeclares.ffrmFilmPreview.txtLastDocument.Text, "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) = 0 And CDbl(modDeclares.Images(i).page) > Conversion.Val(modDeclares.ffrmFilmPreview.txtPage.Text) Then
							num18 = i - 1
							flag4 = True
							Exit While
						End If
						i += 1
					End While
				End If
			Else
				num18 = Conversions.ToInteger(modDeclares.ffrmFilmPreview.cmdRefilm.Tag)
				flag4 = True
			End If
			If Not flag4 Or num18 = modDeclares.imagecount Then
				value = "TXT_NO_DOCS"
				text2 = modMain.GetText(value)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "Keine zu verfilmenden Dokumente vorhanden!"
					text2 = "No Documents to be filmed!"
				End If
				Dim num19 As Short = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num19, value)
				modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
				MyProject.Forms.frmFilming.Close()
				Return
			End If
			num18 += 1
			If modDeclares.UseDebug Or modDeclares.CalcModus Then
				modDeclares.FW = "1.5"
			Else
				modDeclares.FW = modMultiFly.GetFirmware()
			End If
			num20 = CInt(Math.Round(modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2))))
			Dim num21 As Integer = modDeclares.SystemData.filmspeed(CInt(num2))
			verschlussgeschw = modDeclares.SystemData.verschlussgeschw
			num22 = modDeclares.SystemData.zusatzbelichtung / 1000.0
			If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
				modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
			End If
			modDeclares.Outputs = 0
			modDeclares.glbInsertFilmCanceled = False
			Dim smci2 As Boolean = modDeclares.SystemData.SMCI
			Dim k As Integer
			Dim text3 As String
			Dim num23 As Integer
			If(Not modDeclares.SystemData.CheckVakuum And Not modDeclares.UseDebug) AndAlso (modMultiFly.FilmEnde() And modDeclares.SystemData.CheckFilmEnde) Then
				value = "TXT_FILMENDE1"
				text2 = modMain.GetText(value)
				If Operators.CompareString(text2, "", False) <> 0 Then
					Dim str2 As String = text2
					Dim str3 As String = vbCr
					value = "TXT_FILMENDE2"
					text2 = str2 + str3 + modMain.GetText(value)
				Else
					text2 = "Filmende erkannt!" & vbCr & "Bitte nach Aufforderung einen neuen Film einlegen!"
				End If
				Dim num19 As Short = 0S
				value = "file-converter"
				modMain.msgbox2(text2, num19, value)
				modDeclares.ffrmFilmPreview.txtFilmNr.Text = Conversions.ToString(num17)
				If modDeclares.SystemData.FesteBelegzahlProFilm Then
					modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Conversions.ToString(num10)
				Else
					modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				End If
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
				modDeclares.Outputs = 0
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				num23 = 0
				text3 = modMultiFly.Comm_Read(num23, True)
				value = "TXT_EXPOSE_CANCELLED"
				text2 = modMain.GetText(value)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "Verfilmen wurde abgebrochen!"
					text2 = "Exposing stopped!"
				End If
				MyProject.Forms.frmFilming.Close()
				modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
				Return
			End If
			Dim flag5 As Boolean = False
			num23 = 0
			Dim num24 As Integer
			Dim num25 As Short
			Dim flag6 As Boolean
			Dim num32 As Integer
			If modExpose.EOFReached(num9, num10, num23) Then
				modSMCi.VakuumAusSMCi()
				Dim text4 As String = Application.StartupPath + "\EXTLOGS\" + MyProject.Forms.frmFilming.lblFilmNr.Text + ".txt"
				If File.Exists(text4) Then
					Interaction.Shell("notepad.exe " + text4, AppWinStyle.MaximizedFocus, False, -1)
				End If
				If modDeclares.SystemData.AutoRollInsert > 0S Then
					MyProject.Forms.frmFilmEinlegen.Show()
					Application.DoEvents()
					num24 = modDeclares.timeGetTime()
					Do
						Application.DoEvents()
					Loop While modDeclares.timeGetTime() - num24 <= CInt((modDeclares.SystemData.AutoRollInsert * 1000S))
					MyProject.Forms.frmFilmEinlegen.cmdStart_Enter(Nothing, New EventArgs())
				Else
					MyProject.Forms.frmFilmEinlegen.ShowDialog()
					MyProject.Forms.frmFilmEinlegen.Dispose()
				End If
				If Not modDeclares.UseDebug Then
					modSMCi.LEDAnSMCi()
				End If
				value = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				modExpose.AddTrailer(value)
				MyProject.Forms.frmGetFilmNo.txtFilmNo.Text = Conversions.ToString(num17 + 1)
				If modDeclares.SystemData.AutoRollInsert <> 0S Then
					MyProject.Forms.frmGetFilmNo.Show()
					Application.DoEvents()
					num24 = modDeclares.timeGetTime()
					Do
						Application.DoEvents()
					Loop While modDeclares.timeGetTime() - num24 <= CInt((modDeclares.SystemData.AutoRollInsert * 1000S))
					MyProject.Forms.frmGetFilmNo.Button1_Click(Nothing, New EventArgs())
				Else
					MyProject.Forms.frmGetFilmNo.ShowDialog()
					MyProject.Forms.frmGetFilmNo.Dispose()
				End If
				modMain.ProtIndex = 1
				modSMCi.VakuumAnSMCi()
				num17 = CInt(Math.Round(Conversion.Val(modDeclares.ffrmFilmPreview.txtFilmNr.Text)))
				modDeclares.Blip1Counter = 0
				modDeclares.Blip2Counter = 0
				modDeclares.Blip3Counter = 0
				Dim value2 As Object = num17
				modExpose.ClearLog(value2)
				num17 = Conversions.ToInteger(value2)
				num25 = CShort(FileSystem.FreeFile())
				FileSystem.FileOpen(CInt(num25), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
				FileSystem.PrintLine(CInt(num25), New Object() { num17 })
				FileSystem.FileClose(New Integer() { CInt(num25) })
				If modDeclares.SystemData.BayHStA Then
					flag6 = False
					Dim num26 As Short = CShort(FileSystem.FreeFile())
					FileSystem.FileOpen(CInt(num26), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
					FileSystem.Print(CInt(num26), New Object() { Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + ";" })
					If flag2 Then
						FileSystem.Print(CInt(num26), New Object() { "Y;" + Strings.Right(modDeclares.Images(i + modDeclares.SystemData.NumberOfRepetetionFrames).DokumentName, 5) + ";" })
					Else
						FileSystem.Print(CInt(num26), New Object() { "N;" })
					End If
					FileSystem.FileClose(New Integer() { CInt(num26) })
				End If
				MyProject.Forms.frmFilming.lblFilmNr.Text = Conversions.ToString(num17)
				k = If(-If((modDeclares.WritePrivateProfileString("SYSTEM", "FILMNO" + Conversions.ToString(CInt(num2)), modDeclares.ffrmFilmPreview.txtFilmNr.Text, lpFileName) > False), 1, 0), 1, 0)
				If modDeclares.glbInsertFilmCanceled Then
					value = "TXT_EXPOSE_CANCELLED"
					text2 = modMain.GetText(value)
					If Operators.CompareString(text2, "", False) = 0 Then
						text2 = "Verfilmen wurde abgebrochen!"
						text2 = "Exposing stopped!"
					End If
					Interaction.MsgBox(text2, MsgBoxStyle.OkOnly, Nothing)
					Return
				End If
				Dim num27 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.vorspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
				MyProject.Forms.frmFilmTransport.Show()
				MyProject.Forms.frmFilmTransport.Text = "Leader"
				Application.DoEvents()
				If Not modDeclares.UseDebug Then
					modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
					If modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteHoch()
					End If
					If modDeclares.SystemData.SMCI Then
						modSMCi.MagnetAusSMCi()
					End If
					Dim num19 As Short = 1S
					num23 = modMultiFly.GetSpeedFromSteps(num27, modDeclares.SystemData.filmspeed(CInt(num2)))
					Dim num28 As Integer = 1
					Dim num29 As Integer = 0
					Dim num30 As Integer = 0
					If Not modMultiFly.FahreMotor(num19, num27, num23, num28, num29, num30, modDeclares.SystemData.FResolution(CInt(num2))) Then
						MyProject.Forms.frmFilmTransport.Close()
						MyProject.Forms.frmFilming.Close()
						modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
						Return
					End If
					While True
						num19 = 1S
						If Not modMultiFly.MotorIsRunning(num19) Then
							Exit For
						End If
						Application.DoEvents()
					End While
					If modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteRunter()
					End If
				End If
				MyProject.Forms.frmFilmTransport.Close()
				Application.DoEvents()
				value = modMain.GiveIni(lpFileName, "SYSTEM", "FILMLAENGE" + Conversions.ToString(CInt(num2)))
				num9 = Conversion.Val(modMain.KommazuPunkt(value)) - CDbl(modDeclares.SystemData.vorspann) / 100.0
				num10 = modDeclares.SystemData.BelegeProFilm(CInt(num2))
				If flag2 Then
					num10 += modDeclares.SystemData.NumberOfRepetetionFrames
				End If
				Dim num31 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.filmlaenge(CInt(num2))) - CDbl(modDeclares.SystemData.vorspann) / 100.0 - CDbl(modDeclares.SystemData.nachspann) / 100.0))
				If modDeclares.SystemData.UseStartFrame Or modExpose.AnzGesamtStartSymbole > 0 Then
					flag5 = True
					num18 -= 1
					If modDeclares.SystemData.UseStartFrame Then
						num32 = 0
					ElseIf modExpose.AnzGesamtStartSymbole > 0 Then
						num32 = 1
					Else
						flag5 = False
						num18 += 1
					End If
				End If
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
				modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				num8 = 0
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2)), Conversion.Str(num8), lpFileName) > False), 1, 0)), 1, 0)
			End If
			If Not modDeclares.UseDebug Then
				If modDeclares.SystemData.CheckVakuum Then
					modDeclares.Outputs = modDeclares.Outputs Or 64
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					modMultiFly.Comm_Send(text3)
					Dim num30 As Integer = 0
					text3 = modMultiFly.Comm_Read(num30, True)
					modDeclares.Sleep(modDeclares.SystemData.VacuumOnDelay)
					If modDeclares.SystemData.SMCI Then
						modSMCi.VakuumAnSMCi()
					End If
				End If
				If Not modDeclares.CalcModus Then
					If Not modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteHoch()
					End If
					modSMCi.MagnetAnSMCi()
					If modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteRunter()
						Dim smci3 As Boolean = modDeclares.SystemData.SMCI
					End If
				End If
			End If
			num24 = modDeclares.GetTickCount()
			If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn))) Then
				modDeclares.Sleep(500)
				modDeclares.Outputs = modDeclares.Outputs And 223
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				Dim num30 As Integer = 0
				text3 = modMultiFly.Comm_Read(num30, True)
				modDeclares.Sleep(100)
				modDeclares.Outputs = modDeclares.Outputs Or 32
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				num30 = 0
				text3 = modMultiFly.Comm_Read(num30, True)
				If modDeclares.SystemData.SMCI Then
					modSMCi.VakuumAnSMCi()
				End If
				If modDeclares.SystemData.SMCI Then
					modSMCi.MagnetAnSMCi()
				End If
				If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn))) Then
					value = "TXT_NO_VACUUM"
					Dim text5 As String = modMain.GetText(value)
					Dim str4 As String = vbCr
					value = "TXT_END_EXPOSE"
					text2 = text5 + str4 + modMain.GetText(value)
					If Operators.CompareString(text2, vbCr, False) = 0 Then
						text2 = "Vakuum konnte nicht erzeugt werden!" & vbCr & "Verfilmen beenden?"
					End If
					If modDeclares.SystemData.SMCI Then
						modSMCi.VakuumAusSMCi()
						modSMCi.MagnetAusSMCi()
					End If
					modDeclares.Outputs = 0
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					modMultiFly.Comm_Send(text3)
					num30 = 0
					text3 = modMultiFly.Comm_Read(num30, True)
					Dim num19 As Short = 52S
					value = "file-converter"
					If modMain.msgbox2(text2, num19, value) = 6S Then
						modDeclares.Outputs = 0
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num30 = 0
						text3 = modMultiFly.Comm_Read(num30, True)
						modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
						MyProject.Forms.frmFilming.Close()
						Return
					End If
					If modDeclares.SystemData.CheckVakuum Then
						modDeclares.Outputs = modDeclares.Outputs Or 64
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num30 = 0
						text3 = modMultiFly.Comm_Read(num30, True)
						modDeclares.Sleep(modDeclares.SystemData.VacuumOnDelay)
						If modDeclares.SystemData.SMCI Then
							modSMCi.VakuumAnSMCi()
						End If
					End If
					If modDeclares.SystemData.SMCI Then
						modSMCi.MagnetAnSMCi()
					End If
					modDeclares.Outputs = modDeclares.Outputs Or 32
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					modMultiFly.Comm_Send(text3)
					num30 = 0
					text3 = modMultiFly.Comm_Read(num30, True)
				End If
			ElseIf Not modDeclares.SystemData.SMCI Then
				modDeclares.Outputs = modDeclares.Outputs Or 8
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
					modMultiFly.Comm_Send(text3)
					Dim num30 As Integer = 0
					text3 = modMultiFly.Comm_Read(num30, True)
				End If
			End If
			num3 = 0S
			modDeclares.finish = False
			i = num18
			If i > 0 AndAlso (modDeclares.Images(i).IsPDF And modDeclares.Images(i).page > 1) Then
				modMain.ForcePDFRenderer = True
			End If
			Dim flag7 As Boolean = False
			MyProject.Forms.frmImage.Show()
			Dim num33 As Short = 0S
			modMain.FreeBlockedMemory()
			Dim useAnno As Boolean = modDeclares.SystemData.UseAnno
			Dim useBlip As Boolean = modDeclares.SystemData.UseBlip
			Dim num34 As Short
			Dim tickCount As Integer
			If num34 = 0S Then
				tickCount = modDeclares.GetTickCount()
				num34 = 0S
			End If
			Dim fileSystemObject2 As FileSystemObject = New FileSystemObjectClass()
			If modDeclares.SystemData.JPEGProcessor Then
				lpFileName = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modMain.temppath = modMain.GiveIni(lpFileName, "SYSTEM", "RAMDRIVE")
				fileSystemObject2.DeleteFolder(modMain.temppath, False)
				Dim num35 As Short = 1S
				Do
					fileSystemObject2.CreateFolder(modMain.temppath)
					If fileSystemObject2.FolderExists(modMain.temppath) Then
						Exit Do
					End If
					modDeclares.Sleep(200)
					Application.DoEvents()
					num35 += 1S
				Loop While num35 <= 10S
				Dim text6 As String = MyProject.Application.Info.DirectoryPath + "\JPEGAufbereiter.exe "
				Dim text7 As String = String.Concat(New String() { MyProject.Application.Info.DirectoryPath, "\LastLoadedImageStructure.txt ", Support.Format(modDeclares.SystemData.Breite, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), " ", Support.Format(modDeclares.SystemData.Hoehe, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), " ", Conversions.ToString(i) })
				modMonitorTest.ExecCmdNoWait2(text6, text7)
				MyProject.Forms.frmJPEGAufbereiter.ShowDialog()
				MyProject.Forms.frmJPEGAufbereiter.Dispose()
			End If
			Dim fixedLengthString As FixedLengthString = New FixedLengthString(256)
			Dim fixedLengthString2 As FixedLengthString = New FixedLengthString(256)
			Dim fixedLengthString3 As FixedLengthString = New FixedLengthString(256)
			Dim str6 As String
			Dim num60 As Short
			Dim num76 As Short
			Dim num77 As Integer
			Dim num79 As Integer
			Dim num80 As Integer
			Dim num19 As Short
			Dim num89 As Integer
			While True
				Dim tickCount2 As Integer = modDeclares.GetTickCount()
				If num34 > 0S Then
					Dim num30 As Integer = CInt(Math.Round(Conversion.Val(MyProject.Forms.frmFilming.lblImages.Text)))
					Dim num29 As Integer = CInt(Math.Round(Conversion.Val(MyProject.Forms.frmFilming.lblAnzahlFrames.Text)))
					Dim num36 As Integer = modMain.min(num30, num29)
					MyProject.Forms.frmFilming.lblTimeRemaining.Text = Support.Format(CDbl(num36) * (CDbl((tickCount2 - tickCount)) / 1000.0 / CDbl(num34)) / 60.0, "#00 min", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				End If
				num34 += 1S
				If modDeclares.SystemData.SMCI AndAlso Not modSMCi.DeckelGeschlossenSMci() Then
					While Not modSMCi.DeckelGeschlossenSMci()
						value = "Lid is open!" & vbCrLf & "Please close the Lid first."
						num19 = 0S
						text = "file-converter"
						modMain.msgbox2(value, num19, text)
					End While
				End If
				If flag5 Or modExpose.ExposeEndSymbols Then
					modDeclares.SystemData.UseAnno = False
					modDeclares.SystemData.UseBlip = False
					MyProject.Forms.frmBlipWin.Hide()
					MyProject.Forms.frmAnnoWin.Hide()
				Else
					modDeclares.SystemData.UseAnno = useAnno
					modDeclares.SystemData.UseBlip = useBlip
					If modDeclares.SystemData.UseBlip Then
						MyProject.Forms.frmBlipWin.Show()
						Application.DoEvents()
					End If
					If modDeclares.SystemData.UseAnno Then
						MyProject.Forms.frmAnnoWin.Show()
						Application.DoEvents()
					End If
				End If
				If modDeclares.DoCancel And Not flag5 And Not flag7 Then
					If modDeclares.CalcModus Then
						text = "TXT_STOP_CALCULATION"
						text3 = modMain.GetText(text)
						If Operators.CompareString(text3, "", False) = 0 Then
							text3 = "Filmlängenberechnung wirklich beenden?"
						End If
					Else
						text = "TXT_STOP_EXPOSURE"
						text3 = modMain.GetText(text)
						If Operators.CompareString(text3, "", False) = 0 Then
							text3 = "Do you really want to stop the Exposure Process?"
						End If
					End If
					num19 = 4S
					text = "file-converter"
					If modMain.msgbox2(text3, num19, text) = 6S Then
						Exit For
					End If
					modDeclares.DoCancel = False
				End If
				Application.DoEvents()
				If Not modDeclares.finish Then
					Application.DoEvents()
					modDeclares.UseAccusoft = False
					If Not(flag5 Or modExpose.ExposeEndSymbols) AndAlso modDeclares.SystemData.UseAnno Then
						If modDeclares.SystemData.AnnoStyle = 4S Then
							Dim text8 As String = ""
							num23 = CInt(modDeclares.SystemData.AnnoLen)
							k = 1
							While k <= num23
								text8 += "0"
								k += 1
							End While
							If modDeclares.glbOrientation Then
								modDeclares.SystemData.Anno = Conversions.ToString(num8 + modDeclares.SystemData.AnnoStart - num11)
							Else
								modDeclares.SystemData.Anno = Conversions.ToString(num8 + modDeclares.SystemData.AnnoStart - num11)
							End If
							modDeclares.SystemData.Anno = Support.Format(modDeclares.SystemData.Anno, text8, FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						End If
						If modDeclares.SystemData.AnnoStyle = 3S Then
							If modDeclares.SystemData.Duplex Then
								Dim text9 As String = modDeclares.Images(i).DokumentName
								Dim text10 As String = ""
								Dim value3 As Object = FileSystem.FreeFile()
								text = modDeclares.Images(i).Name + ".anno"
								If modExpose.FileExists(text) Then
									FileSystem.FileOpen(Conversions.ToInteger(value3), modDeclares.Images(i).Name + ".anno", OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
									text9 = FileSystem.LineInput(Conversions.ToInteger(value3))
									text10 = FileSystem.LineInput(Conversions.ToInteger(value3))
									Dim num37 As Integer = Strings.InStrRev(text9, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary)
									If num37 > 0 Then
										text9 = Strings.Left(text9, num37 - 1)
									End If
									num37 = Strings.InStrRev(text10, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary)
									If num37 > 0 Then
										text10 = Strings.Left(text10, num37 - 1)
									End If
									FileSystem.FileClose(New Integer() { Conversions.ToInteger(value3) })
								End If
								If Not modDeclares.SystemData.SimDupFilenames Then
									modDeclares.SystemData.Anno = text9
								ElseIf modDeclares.SystemData.TwoLines Then
									modDeclares.SystemData.Anno = text9 + vbCrLf + text10
								Else
									modDeclares.SystemData.Anno = text9 + " + " + text10
								End If
							Else
								Dim text11 As String = modDeclares.Images(i).Name
								text11 = Strings.Mid(text11, Strings.InStrRev(text11, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
								modDeclares.SystemData.Anno = text11
								If Strings.InStrRev(modDeclares.SystemData.Anno, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) > 0 Then
									modDeclares.SystemData.Anno = Strings.Left(modDeclares.SystemData.Anno, Strings.InStrRev(modDeclares.SystemData.Anno, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
								End If
							End If
						End If
						Dim annoStyle As Short = modDeclares.SystemData.AnnoStyle
						If modDeclares.SystemData.AnnoStyle = 2S Then
							modDeclares.SystemData.Anno = modDeclares.Images(i).DokumentName
						End If
					End If
					modDeclares.SystemData.NumberOfInfoLines = 0
					Dim j As Integer
					Dim num29 As Integer
					Dim num40 As Integer
					Dim num43 As Integer
					Dim flag8 As Boolean
					Dim text12 As String
					Dim str5 As String
					Dim text13 As String
					Dim text14 As String
					Dim num51 As Integer
					Dim num53 As Integer
					Dim num54 As Integer
					Dim num57 As Integer
					Dim num59 As Integer
					Dim flag9 As Boolean
					Dim num63 As Integer
					Dim num64 As Integer
					If(flag7 OrElse flag5) Or modExpose.ExposeEndSymbols Then
						modDeclares.UseAccusoft = False
						If modDeclares.UseAccusoft Then
							If modDeclares.IG_image_is_validD(CInt(modDeclares.handle)) <> 0 Then
								modDeclares.IG_image_deleteD(CInt(modDeclares.handle))
							End If
							If flag5 Then
								If num32 > 0 Then
									Dim gesamtStartSymbole As String() = modExpose.GesamtStartSymbole
									Dim num38 As Integer = num32
									Dim num28 As Integer = CInt(modDeclares.handle)
									Dim num30 As Integer = 1
									modMain.FH_IG_load_file(gesamtStartSymbole(num38), num28, num30)
									modDeclares.handle = CLng(num28)
								End If
							Else
								text = MyProject.Application.Info.DirectoryPath + "\TrennBlatt.bmp"
								Dim num30 As Integer = CInt(modDeclares.handle)
								Dim num28 As Integer = 1
								modMain.FH_IG_load_file(text, num30, num28)
								modDeclares.handle = CLng(num30)
							End If
							If modExpose.ExposeEndSymbols Then
								Dim gesamtEndSymbole As String() = modExpose.GesamtEndSymbole
								Dim num39 As Integer = num4
								Dim num28 As Integer = CInt(modDeclares.handle)
								Dim num30 As Integer = 1
								modMain.FH_IG_load_file(gesamtEndSymbole(num39), num28, num30)
								modDeclares.handle = CLng(num28)
							End If
						Else
							If flag5 Then
								If num32 > 0 Then
									MyProject.Forms.frmImage.LoadFile(modExpose.GesamtStartSymbole(num32), 1L)
									MyProject.Forms.frmImage.ImagXpress1.Width = modDeclares.SystemData.Breite
									MyProject.Forms.frmImage.ImagXpress1.Height = modDeclares.SystemData.Hoehe
									MyProject.Forms.frmImage.ImagXpress1.Top = 0
									MyProject.Forms.frmImage.ImagXpress1.Left = 0
									modMain.glImage = modPaint.ResizeImage(CType(modMain.glImage, Bitmap), modDeclares.SystemData.Breite, modDeclares.SystemData.Hoehe)
									MyProject.Forms.frmImage.ImagXpress1.Image = modMain.glImage
									MyProject.Forms.frmImage.ImagXpress1.Visible = True
								End If
							Else
								MyProject.Forms.frmImage.LoadFile(MyProject.Application.Info.DirectoryPath + "\TrennBlatt.bmp", 1L)
							End If
							If modExpose.ExposeEndSymbols Then
								MyProject.Forms.frmImage.LoadFile(modExpose.GesamtEndSymbole(num4), 1L)
								MyProject.Forms.frmImage.ImagXpress1.Width = modDeclares.SystemData.Breite
								MyProject.Forms.frmImage.ImagXpress1.Height = modDeclares.SystemData.Hoehe
								MyProject.Forms.frmImage.ImagXpress1.Top = 0
								MyProject.Forms.frmImage.ImagXpress1.Left = 0
								modMain.glImage = modPaint.ResizeImage(CType(modMain.glImage, Bitmap), modDeclares.SystemData.Breite, modDeclares.SystemData.Hoehe)
								MyProject.Forms.frmImage.ImagXpress1.Image = modMain.glImage
								MyProject.Forms.frmImage.ImagXpress1.Visible = True
							End If
						End If
						If modDeclares.glbOrientation Then
							num40 = modDeclares.SystemData.Hoehe
							If modDeclares.SystemData.StepsImageToImage Then
								' The following expression was wrapped in a unchecked-expression
								num40 = CInt(Math.Round(CDbl(num40) * (modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) / CDbl(modDeclares.SystemData.Hoehe)) * modDeclares.SystemData.schrittepromm(CInt(num2)) + modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2))))
							End If
						Else
							num40 = modDeclares.SystemData.Breite
							If modDeclares.SystemData.StepsImageToImage Then
								' The following expression was wrapped in a unchecked-expression
								num40 = CInt(Math.Round(CDbl(num40) * (modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) / CDbl(modDeclares.SystemData.Hoehe)) * modDeclares.SystemData.schrittepromm(CInt(num2)) + modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2))))
							End If
						End If
					Else
						If modDeclares.SystemData.EnableInfoWindow Then
							modDeclares.SystemData.NumberOfInfoLines = modDeclares.GetNumberOfLines()
							Dim ptr As String() = modDeclares.SystemData.InfoLinesLeft
							modDeclares.SystemData.InfoLinesLeft = CType(Utils.CopyArray(ptr, New String(modDeclares.SystemData.NumberOfInfoLines + 1 - 1) {}), String())
							ptr = modDeclares.SystemData.InfoLinesCenter
							modDeclares.SystemData.InfoLinesCenter = CType(Utils.CopyArray(ptr, New String(modDeclares.SystemData.NumberOfInfoLines + 1 - 1) {}), String())
							ptr = modDeclares.SystemData.InfoLinesRight
							modDeclares.SystemData.InfoLinesRight = CType(Utils.CopyArray(ptr, New String(modDeclares.SystemData.NumberOfInfoLines + 1 - 1) {}), String())
							Dim num30 As Integer = modDeclares.SystemData.NumberOfInfoLines
							j = 1
							While j <= num30
								Dim line As Integer = j
								Dim pos As Integer = 1
								Dim images As modDeclares.typImage() = modDeclares.Images
								Dim num41 As Integer = i
								Dim images2 As modDeclares.typImage() = modDeclares.Images
								Dim num42 As Integer = i
								Dim globalFrameCounter As Integer = num8
								Dim fixedLengthString4 As FixedLengthString = fixedLengthString2
								Dim fixedLengthString5 As FixedLengthString = fixedLengthString4
								text = fixedLengthString4.Value
								Dim fixedLengthString6 As FixedLengthString = fixedLengthString
								Dim fixedLengthString7 As FixedLengthString = fixedLengthString6
								value = fixedLengthString6.Value
								Dim length As Integer
								Dim entry As Integer = modDeclares.GetEntry(line, pos, images(num41).Name, images2(num42).Name, globalFrameCounter, text, length, value)
								fixedLengthString7.Value = value
								fixedLengthString5.Value = text
								num43 = entry
								modDeclares.SystemData.InfoLinesLeft(j) = Strings.Left(fixedLengthString2.Value, length)
								Dim line2 As Integer = j
								Dim pos2 As Integer = 2
								Dim images3 As modDeclares.typImage() = modDeclares.Images
								Dim num44 As Integer = i
								Dim images4 As modDeclares.typImage() = modDeclares.Images
								Dim num45 As Integer = i
								Dim globalFrameCounter2 As Integer = num8
								Dim fixedLengthString8 As FixedLengthString = fixedLengthString2
								fixedLengthString7 = fixedLengthString8
								value = fixedLengthString8.Value
								Dim fixedLengthString9 As FixedLengthString = fixedLengthString
								fixedLengthString5 = fixedLengthString9
								text = fixedLengthString9.Value
								Dim entry2 As Integer = modDeclares.GetEntry(line2, pos2, images3(num44).Name, images4(num45).Name, globalFrameCounter2, value, length, text)
								fixedLengthString5.Value = text
								fixedLengthString7.Value = value
								num43 = entry2
								modDeclares.SystemData.InfoLinesCenter(j) = Strings.Left(fixedLengthString2.Value, length)
								Dim line3 As Integer = j
								Dim pos3 As Integer = 3
								Dim images5 As modDeclares.typImage() = modDeclares.Images
								Dim num46 As Integer = i
								Dim images6 As modDeclares.typImage() = modDeclares.Images
								Dim num47 As Integer = i
								Dim globalFrameCounter3 As Integer = num8
								Dim fixedLengthString10 As FixedLengthString = fixedLengthString2
								fixedLengthString5 = fixedLengthString10
								text = fixedLengthString10.Value
								Dim fixedLengthString11 As FixedLengthString = fixedLengthString
								fixedLengthString7 = fixedLengthString11
								value = fixedLengthString11.Value
								Dim entry3 As Integer = modDeclares.GetEntry(line3, pos3, images5(num46).Name, images6(num47).Name, globalFrameCounter3, text, length, value)
								fixedLengthString7.Value = value
								fixedLengthString5.Value = text
								num43 = entry3
								modDeclares.SystemData.InfoLinesRight(j) = Strings.Left(fixedLengthString2.Value, length)
								j += 1
							End While
						End If
						Dim useProzessor As Boolean = modDeclares.UseProzessor
						flag8 = False
						If modMain.IsUnicode(modDeclares.Images(i).Name) Then
							text12 = MyProject.Application.Info.DirectoryPath + "\X.IMG"
							If Operators.CompareString(Support.Format(Strings.Right(modDeclares.Images(i + modPaint.pos).Name, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
								text12 = MyProject.Application.Info.DirectoryPath + "\X.PDF"
							End If
							fileSystemObject.CopyFile(modDeclares.Images(i + modPaint.pos).Name, text12, True)
						Else
							text12 = modDeclares.Images(i).Name
						End If

							If modDeclares.Images(i).IsPDF Then
								If modDeclares.SystemData.USEDISPLAYSECTION Then
									If Operators.CompareString(modDeclares.SystemData.DISPLAY_PDF, "P", False) = 0 Then
										modDeclares.UseAccusoft = False
									Else
										modDeclares.UseAccusoft = True
									End If
								Else
									modDeclares.UseAccusoft = False
								End If
								If MyProject.Forms.frmImageXpress.OpenPDFDocumentAlt(text12, modDeclares.Images(i).page, modDeclares.SystemData.PDFReso, modMain.glImage) Then
									If MyProject.Forms.frmImage.IResX = 0L Then
										MyProject.Forms.frmImage.IResX = CLng(modDeclares.SystemData.PDFReso)
										MyProject.Forms.frmImage.IResY = CLng(modDeclares.SystemData.PDFReso)
									End If
									If MyProject.Forms.frmImage.IResX <> 0L And MyProject.Forms.frmImage.IResY <> 0L Then
										str5 = Support.Format(CDbl(MyProject.Forms.frmImage.IWidth) / CDbl(MyProject.Forms.frmImage.IResX) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "x" + Support.Format(CDbl(MyProject.Forms.frmImage.IHeight) / CDbl(MyProject.Forms.frmImage.IResY) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									Else
										str5 = ""
									End If
									If modDeclares.SystemData.UseAnno AndAlso modDeclares.SystemData.ShowDocSize Then
										num19 = modDeclares.SystemData.DocSizeFormat
										Select Case num19
											Case 0S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm"
											Case 1S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """ x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """"
											Case 2S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm"
										End Select
										If Operators.CompareString(modDeclares.SystemData.Anno, "", False) = 0 Then
											modDeclares.SystemData.Anno = text13
										Else
											modDeclares.SystemData.Anno = modDeclares.SystemData.Anno + " (" + text13 + ")"
										End If
									End If
								Else
									flag8 = True
									text14 = "PDF"
									MyProject.Forms.frmImage.LoadFile(MyProject.Application.Info.DirectoryPath + "/LoadError.jpg", 1L)
									str5 = ""
								End If
							Else
								If modDeclares.SystemData.JPEGProcessor Then
									str6 = text12
									text12 = modExpose.WaitForProcessor(text12, modDeclares.Images(i).page)
									If Operators.CompareString(text12, "", False) = 0 Then
										GoTo Block_155
									End If
								End If
								Dim at_DIB As modDeclares.AT_DIB
								If modDeclares.SystemData.USEDISPLAYSECTION Then
									Dim num48 As Integer
									If num48 = 8 And Not modDeclares.SystemData.UseAccuv16 Then
										modDeclares.UseAccusoft = False
									Else
										If Operators.CompareString(modDeclares.SystemData.DISPLAY_DEFAULT, "P", False) = 0 Then
											modDeclares.UseAccusoft = False
										Else
											modDeclares.UseAccusoft = True
										End If
										If at_DIB.biBitCount = 1S Then
											If Operators.CompareString(modDeclares.SystemData.DISPLAY_BPP1, "P", False) = 0 Then
												modDeclares.UseAccusoft = False
											Else
												modDeclares.UseAccusoft = True
											End If
										End If
										If at_DIB.biBitCount = 8S Then
											If Operators.CompareString(modDeclares.SystemData.DISPLAY_BPP8, "P", False) = 0 Then
												modDeclares.UseAccusoft = False
											Else
												modDeclares.UseAccusoft = True
											End If
										End If
										If at_DIB.biBitCount = 24S Then
											If Operators.CompareString(modDeclares.SystemData.DISPLAY_BPP24, "P", False) = 0 Then
												modDeclares.UseAccusoft = False
											Else
												modDeclares.UseAccusoft = True
											End If
										End If
									End If
									If modDeclares.UseAccusoft Then
										MyProject.Forms.frmImage.ImagXpress1.Visible = False
									End If
								ElseIf modDeclares.SystemData.HybridMode Then
									modDeclares.UseAccusoft = True
									MyProject.Forms.frmImage.ImagXpress1.Visible = False
									Dim num48 As Integer
									If num48 = 8 Then
										modDeclares.UseAccusoft = False
									End If
								ElseIf at_DIB.biBitCount = 24S And modDeclares.SystemData.FastColorExposure Then
									modDeclares.UseAccusoft = True
									MyProject.Forms.frmImage.ImagXpress1.Visible = False
								End If
								If modDeclares.UseAccusoft Then
									If Operators.CompareString(modMain.CurFileNameLoaded, text12, False) <> 0 Or modMain.CurPageLoaded <> modDeclares.Images(i).page Then
										' The following expression was wrapped in a checked-expression
										Dim num28 As Integer = CInt(modDeclares.handle)
										Dim num49 As Integer = modMain.FH_IG_load_file(text12, num28, modDeclares.Images(i).page)
										modDeclares.handle = CLng(num28)
										k = num49
									Else
										' The following expression was wrapped in a checked-expression
										modDeclares.IG_image_delete(CInt(modDeclares.handle))
										modDeclares.handle = CLng(modMain.PreCacheHandle)
										k = 0
									End If
									Dim num50 As Integer
									Dim num52 As Integer
									Dim num55 As Integer
									Dim num56 As Integer
									If k = 0 Then
										k = modDeclares.IG_image_resolution_getD(CInt(modDeclares.handle), num50, num51, num52, num53, num54)
										k = modDeclares.IG_image_dimensions_getD(CInt(modDeclares.handle), num55, num56, num57)
									Else
										flag8 = True
										Dim errorIndex As Integer = 0
										Dim value4 As String = fixedLengthString3.Value
										Dim sizeOfFileName As Integer = 256
										Dim num28 As Integer = 0
										num29 = 0
										Dim num58 As Integer
										modDeclares.IG_error_getD(errorIndex, value4, sizeOfFileName, num58, num59, num28, num29)
										text14 = "ACC"
										text = MyProject.Application.Info.DirectoryPath + "/LoadError.jpg"
										num29 = CInt(modDeclares.handle)
										num28 = 1
										modMain.FH_IG_load_file(text, num29, num28)
										modDeclares.handle = CLng(num29)
										str5 = ""
									End If
									If num50 <> 0 And num52 <> 0 Then
										' The following expression was wrapped in a checked-expression
										' The following expression was wrapped in a checked-expression
										str5 = Support.Format(CDbl((num55 * num51)) / CDbl(num50) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "x" + Support.Format(CDbl((num56 * num53)) / CDbl(num52) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									Else
										str5 = ""
									End If
									If modDeclares.SystemData.UseAnno AndAlso modDeclares.SystemData.ShowDocSize Then
										num60 = modDeclares.SystemData.DocSizeFormat
										Select Case num60
											Case 0S
												text13 = Support.Format(CDbl((num55 * num51)) / CDbl(num50) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm x " + Support.Format(CDbl((num56 * num53)) / CDbl(num52) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm"
											Case 1S
												text13 = Support.Format(CDbl((num55 * num51)) / CDbl(num50), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """ x " + Support.Format(CDbl((num56 * num53)) / CDbl(num52), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """"
											Case 2S
												text13 = Support.Format(CDbl((num55 * num51)) / CDbl(num50) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm x " + Support.Format(CDbl((num56 * num53)) / CDbl(num52) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm"
										End Select
										If Operators.CompareString(modDeclares.SystemData.Anno, "", False) = 0 Then
											modDeclares.SystemData.Anno = text13
										Else
											modDeclares.SystemData.Anno = modDeclares.SystemData.Anno + " (" + text13 + ")"
										End If
									End If
								Else
									If Operators.CompareString(Strings.Right(text12, 3), "tif", False) = 0 Then
									End If
									If(Operators.CompareString(modMain.CurFileNameLoaded, text12, False) <> 0 Or modMain.CurPageLoaded <> modDeclares.Images(i).page Or MyProject.Forms.frmImage.ImagWidth = 0L) OrElse flag9 Then
										modMain.CurFileNameLoaded = text12
										modMain.CurPageLoaded = modDeclares.Images(i).page
										MyProject.Forms.frmImageXpress.OpenRasterDocument(text12, modDeclares.Images(i).page)
										If i + 1 < modDeclares.imagecount AndAlso modDeclares.Images(i + 1).page = 1 Then
											Dim text15 As String = "cmd /c copy /b " + modDeclares.Images(i + 1).Name + " nul"
											modMonitorTest.ExecCmdNoWait(text15)
										End If
										Dim num61 As Integer = CInt(MyProject.Forms.frmImageXpress.IWidth)
										Dim num62 As Integer = CInt(MyProject.Forms.frmImageXpress.IHeight)
										If num61 > num62 Then
											num61 = num63
											num62 = num64
										End If
										Dim flag10 As Boolean = num62 > 7680 And num61 > 4800
										text = "==========================="
										modDeclares.OutputDebugString(text)
										text = "Geladen: " + text12
										modDeclares.OutputDebugString(text)
										text = "w=" + Conversions.ToString(num64)
										modDeclares.OutputDebugString(text)
										text = "h=" + Conversions.ToString(num63)
										modDeclares.OutputDebugString(text)
									End If
									Dim iresX As Long = MyProject.Forms.frmImageXpress.IResX
									If MyProject.Forms.frmImageXpress.IResX <> 0L And MyProject.Forms.frmImageXpress.IResY <> 0L Then
										str5 = Support.Format(CDbl(MyProject.Forms.frmImage.IWidth) / CDbl(MyProject.Forms.frmImage.IResX) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "x" + Support.Format(CDbl(MyProject.Forms.frmImage.IHeight) / CDbl(MyProject.Forms.frmImage.IResY) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
									Else
										str5 = ""
									End If
									text = "docsize=" + str5
									modDeclares.OutputDebugString(text)
									If modDeclares.SystemData.UseAnno AndAlso modDeclares.SystemData.ShowDocSize Then
										Select Case modDeclares.SystemData.DocSizeFormat
											Case 0S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY) * 25.4, "0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "mm"
											Case 1S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """ x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + """"
											Case 2S
												text13 = Support.Format(CDbl(MyProject.Forms.frmImageXpress.IWidth) / CDbl(MyProject.Forms.frmImageXpress.IResX) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm x " + Support.Format(CDbl(MyProject.Forms.frmImageXpress.IHeight) / CDbl(MyProject.Forms.frmImageXpress.IResY) * 25.4 / 10.0, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "cm"
										End Select
										If Operators.CompareString(modDeclares.SystemData.Anno, "", False) = 0 Then
											modDeclares.SystemData.Anno = text13
										Else
											modDeclares.SystemData.Anno = modDeclares.SystemData.Anno + " (" + text13 + ")"
										End If
									End If
								End If
							End If

					End If
					flag9 = False
					If Not(modDeclares.SystemData.DoSplit And Not flag5) Then
						GoTo IL_37A5
					End If
					j = 0
					Do
						j += 1
					Loop While j <= 8
					Dim num65 As Integer
					Dim num66 As Integer
					Dim num67 As Integer
					Dim num68 As Integer
					If modDeclares.SystemData.SplitCount = 4S Then
						If modDeclares.UseAccusoft Then
							k = modDeclares.IG_image_dimensions_getD(CInt(modDeclares.handle), num65, num66, num57)
							num67 = CInt(Math.Round(CDbl(num65) / 2.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
							num68 = CInt(Math.Round(CDbl(num66) / 2.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
						Else
							' The following expression was wrapped in a unchecked-expression
							num67 = CInt(Math.Round(CDbl(modMain.glImage.Width) / 2.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
							num68 = CInt(Math.Round(CDbl(modMain.glImage.Height) / 2.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
						End If
					ElseIf modDeclares.UseAccusoft Then
						k = modDeclares.IG_image_dimensions_getD(CInt(modDeclares.handle), num65, num66, num57)
						num67 = CInt(Math.Round(CDbl(num65) / 3.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
						num68 = CInt(Math.Round(CDbl(num66) / 3.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
					Else
						' The following expression was wrapped in a unchecked-expression
						num67 = CInt(Math.Round(CDbl(modMain.glImage.Width) / 3.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
						num68 = CInt(Math.Round(CDbl(modMain.glImage.Height) / 3.0 * (modDeclares.SystemData.SplitOversize / 100.0)))
					End If
					Dim flag11 As Boolean = False
					If modDeclares.UseAccusoft Then
						k = modDeclares.IG_image_dimensions_getD(CInt(modDeclares.handle), num65, num66, num57)
						Dim num69 As Integer
						Dim num70 As Integer
						k = modDeclares.IG_image_resolution_getD(CInt(modDeclares.handle), num69, num51, num70, num53, num54)
						If CDbl(num65) / (CDbl(num69) / CDbl(num51)) * 25.4 > CDbl(modDeclares.SystemData.SplitSizeX) Or CDbl(num66) / (CDbl(num70) / CDbl(num53)) * 25.4 > CDbl(modDeclares.SystemData.SplitSizeY) Then
							flag11 = True
						End If
					ElseIf CDbl((CSng(modMain.glImage.Width) / modMain.glImage.HorizontalResolution)) * 25.4 > CDbl(modDeclares.SystemData.SplitSizeX) Or CDbl((CSng(modMain.glImage.Height) / modMain.glImage.HorizontalResolution)) * 25.4 > CDbl(modDeclares.SystemData.SplitSizeY) Then
						flag11 = True
					End If
					If(i = -1 OrElse flag7 OrElse flag5) Or modExpose.ExposeEndSymbols Then
						flag11 = False
					End If
					If flag11 Then
						modMain.LastloadedRasterFile = ""
					End If
					Dim num71 As Double
					If(flag11 And num33 = 0S) AndAlso CInt(Math.Round((num9 - CDbl(modDeclares.SystemData.nachspann) / 100.0 - (num71 - CDbl(num43)) * modDeclares.SystemData.AutoTrailerLength) * 1000.0 * modDeclares.SystemData.schrittepromm(CInt(num2)) / CDbl(num20))) <= CInt((modDeclares.SystemData.SplitCount + 2S)) Then
						num9 = 0.0
					Else
						If flag11 Then
							modSplit.HandleSplit(num33, num67, num68, num65, num66)
							flag9 = True
							GoTo IL_37A5
						End If
						GoTo IL_37A5
					End If
					IL_6841:
					If modExpose.EOFReached(num9, num10, i) AndAlso i < modDeclares.imagecount Then
						Dim flag12 As Boolean = False
						If modDeclares.SystemData.FortsetzungsLevel = 1 Then
							flag12 = True
						ElseIf CInt(modDeclares.Images(i + 1).Level) < modDeclares.SystemData.FortsetzungsLevel Then
							flag12 = True
						End If
						If flag12 And Not flag2 Then
							flag2 = True
							If modDeclares.SystemData.UseStartFrame Then
								num11 = 1
							End If
							If modExpose.AnzStartSymbole > 0 AndAlso Not modDeclares.SystemData.NoSpecialSmybolesWhenContinuation Then
								num11 += modExpose.AnzStartSymbole
							End If
							If modExpose.AnzFortsetzungsSymbole2 > 0 Then
								num11 += modExpose.AnzFortsetzungsSymbole2
							End If
							flag3 = True
							If modDeclares.SystemData.BayHStA AndAlso Not flag6 Then
								Dim num26 As Short = CShort(FileSystem.FreeFile())
								FileSystem.FileOpen(CInt(num26), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
								FileSystem.PrintLine(CInt(num26), New Object() { "Y;" + Strings.Right(modDeclares.Images(i).Name, 15) })
								FileSystem.FileClose(New Integer() { CInt(num26) })
								flag6 = True
							End If
							If modDeclares.SystemData.DoRepeatFrames Then
								i -= modDeclares.SystemData.NumberOfRepetetionFrames
								If i < 0 Then
									i = 0
								End If
							End If
						ElseIf modDeclares.SystemData.BayHStA AndAlso Not flag6 Then
							Dim num26 As Short = CShort(FileSystem.FreeFile())
							FileSystem.FileOpen(CInt(num26), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
							FileSystem.PrintLine(CInt(num26), New Object() { "N;" + Strings.Right(modDeclares.Images(i).Name, 15) })
							FileSystem.FileClose(New Integer() { CInt(num26) })
							flag6 = True
						End If
					End If
					text2 = ""
					If i >= 0 Then
						text2 = modDeclares.Images(i).Name + vbCrLf + Support.Format(modDeclares.Images(i).page, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					End If
					Dim flag13 As Boolean

						If Not modDeclares.CalcModus Then
							If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
								FileSystem.Kill(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt")
							End If
							Using streamWriter As StreamWriter = New StreamWriter(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", True, Encoding.Unicode)
								streamWriter.Write(text2)
								streamWriter.Close()
							End Using
							Dim lpFileName2 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
							k = If((-If((modDeclares.WritePrivateProfileString("BLIPS", "Blip1Counter", modDeclares.Blip1Counter.ToString(), lpFileName2) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("BLIPS", "Blip2Counter", modDeclares.Blip2Counter.ToString(), lpFileName2) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("BLIPS", "Blip3Counter", modDeclares.Blip3Counter.ToString(), lpFileName2) > False), 1, 0)), 1, 0)
						End If
						Application.DoEvents()
						modDeclares.ffrmFilmPreview.txtLastDocument.Text = ""
						modDeclares.ffrmFilmPreview.txtPage.Text = ""
						If i >= 0 Then
							modDeclares.ffrmFilmPreview.txtLastDocument.Text = modDeclares.Images(i).Name
							modDeclares.ffrmFilmPreview.txtPage.Text = Conversions.ToString(modDeclares.Images(i).page)
						End If
						If Not(modExpose.AnzGesamtStartSymbole > 0 And num32 < modExpose.AnzGesamtStartSymbole) And Not flag13 Then
							flag5 = False
						End If

					If i > 0 AndAlso modDeclares.Images(i).Level > 1S Then
						Dim num72 As Integer = 1
						Dim num73 As Integer = i + 1
						num29 = modDeclares.imagecount
						Dim num74 As Integer = num73
						While num74 <= num29 AndAlso modDeclares.Images(num74).Level <= 1S
							num72 += 1
							num74 += 1
						End While
						num25 = CShort(FileSystem.FreeFile())
					End If
					text3 = Conversions.ToString(0)
					Dim value2 As Object
					Dim num75 As Double
					If modDeclares.SystemData.Autotrailer AndAlso num75 > modDeclares.SystemData.AutoTrailerDistance AndAlso ((flag11 And num33 = modDeclares.SystemData.SplitCount) Or Not flag11) Then
						MyProject.Forms.frmFilmTransport.Show()
						MyProject.Forms.frmFilmTransport.Text = "Auto Trailer"
						Application.DoEvents()
						value = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						modExpose.AddTrailer(value)
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
							num76 = 1S
							num77 = CInt(Math.Round(modDeclares.SystemData.AutoTrailerLength * modDeclares.SystemData.schrittepromm(CInt(num2)) * 1000.0))
							Dim num78 As Integer = CInt(Math.Round(modDeclares.SystemData.AutoTrailerLength * modDeclares.SystemData.schrittepromm(CInt(num2)) * 1000.0))
							num79 = modMultiFly.GetSpeedFromSteps(num78, modDeclares.SystemData.filmspeed(CInt(num2)))
							num80 = 1
							Dim num81 As Integer = 0
							Dim num82 As Integer = 0
							modMultiFly.FahreMotor(num76, num77, num79, num80, num81, num82, modDeclares.SystemData.FResolution(CInt(num2)))
							While True
								num76 = 1S
								If Not modMultiFly.MotorIsRunning(num76) Then
									Exit For
								End If
								Application.DoEvents()
							End While
						End If

							num9 -= modDeclares.SystemData.AutoTrailerLength
							If Not modDeclares.CalcModus Then
								k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
								k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
								k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
							Else
								num75 = 0.0
							End If
							MyProject.Forms.frmFilmTransport.Close()

						num17 += 1
						value2 = num17
						modExpose.ClearLog(value2)
						num17 = Conversions.ToInteger(value2)
						MyProject.Forms.frmFilming.lblFilmNr.Text = Conversions.ToString(num17)
						If Not modDeclares.CalcModus Then
							FileSystem.FileOpen(CInt(num25), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
							FileSystem.PrintLine(CInt(num25), New Object() { num17 })
							FileSystem.FileClose(New Integer() { CInt(num25) })
						End If
						modDeclares.ffrmFilmPreview.txtFilmNr.Text = Conversions.ToString(num17)
						If modDeclares.SystemData.TrailerInfoFrames Then
							flag5 = True
						End If
					End If
					If modDeclares.SystemData.CheckVakuum Then
						modDeclares.Outputs = modDeclares.Outputs Or 64
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						Dim num82 As Integer = 0
						text3 = modMultiFly.Comm_Read(num82, True)
						If modDeclares.SystemData.SMCI Then
							modSMCi.VakuumAnSMCi()
						End If
					End If
					If modDeclares.SystemData.SMCI Then
						modSMCi.MagnetAnSMCi()
					End If
					If Not modDeclares.SystemData.NeuerMagnet Then
						modDeclares.Outputs = modDeclares.Outputs Or 32
					End If
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
						modMultiFly.Comm_Send(text3)
						Dim num82 As Integer = 0
						text3 = modMultiFly.Comm_Read(num82, True)
					End If
					MyProject.Forms.frmFilming.lblImages.Text = Conversions.ToString(modDeclares.imagecount - i)
					num25 = CShort(FileSystem.FreeFile())
					text3 = Conversions.ToString(0)

						If modDeclares.CalcModus Then
							MyProject.Forms.frmFilming.lblRestframes.Text = Support.Format(1000000.0 - num9, "0.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							If num6 < 1000000.0 - num9 Then
								' The following expression was wrapped in a checked-expression
								Dim num83 As Short = CShort(FileSystem.FreeFile())
								FileSystem.FileOpen(CInt(num83), MyProject.Application.Info.DirectoryPath + "\CalcProt.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
								text3 = String.Concat(New String() { Support.Format(num6, "000.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "m : ", modDeclares.Images(i).DokumentName, "; ", Conversions.ToString(modDeclares.Images(i).page) })
								FileSystem.PrintLine(CInt(num83), New Object() { text3 })
								num6 += 1.0
								FileSystem.FileClose(New Integer() { CInt(num83) })
							End If
						Else
							Dim lblRestframes As Label = MyProject.Forms.frmFilming.lblRestframes
							value2 = 0
							Dim value5 As Object = num9
							Dim obj As Object = modMain.fmax(value2, value5)
							num9 = Conversions.ToDouble(value5)
							lblRestframes.Text = Support.Format(RuntimeHelpers.GetObjectValue(obj), "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						End If
						num71 = 0.0
						If modDeclares.SystemData.Autotrailer Then
							num71 = (CDbl(modDeclares.SystemData.filmlaenge(CInt(num2))) - CDbl(modDeclares.SystemData.vorspann) / 100.0 - CDbl(modDeclares.SystemData.nachspann) / 100.0) / (modDeclares.SystemData.AutoTrailerDistance + modDeclares.SystemData.AutoTrailerLength)
							num71 = CDbl((CShort(Math.Round(num71 + 0.5))))
						End If
						Dim num84 As Double = CDbl(modDeclares.SystemData.filmlaenge(CInt(num2)))
						Dim num85 As Double = CDbl(modDeclares.SystemData.vorspann) / 100.0
						Dim flag14 As Boolean = False
						num43 = 0
						If modDeclares.SystemData.Autotrailer Then
							While Not flag14
								If num84 - num85 - num9 > modDeclares.SystemData.AutoTrailerDistance Then
									' The following expression was wrapped in a checked-statement
									num43 += 1
									num84 -= modDeclares.SystemData.AutoTrailerDistance + modDeclares.SystemData.AutoTrailerLength
								Else
									flag14 = True
								End If
							End While
						End If

					If modDeclares.SystemData.StepsImageToImage Then
						' The following expression was wrapped in a unchecked-expression
						Dim num86 As Integer = CInt(Math.Round((num9 - CDbl(modDeclares.SystemData.nachspann) / 100.0 - (num71 - CDbl(num43)) * (modDeclares.SystemData.AutoTrailerDistance + modDeclares.SystemData.AutoTrailerLength)) * 1000.0 * modDeclares.SystemData.schrittepromm(CInt(num2)) / CDbl(num40)))
						If modDeclares.SystemData.FesteBelegzahlProFilm Then
							MyProject.Forms.frmFilming.lblAnzahlFrames.Text = Conversions.ToString(num10)
						ElseIf CDbl(num86) < Conversions.ToDouble(MyProject.Forms.frmFilming.lblAnzahlFrames.Text) Or Conversions.ToDouble(MyProject.Forms.frmFilming.lblAnzahlFrames.Text) <= 0.0 Then
							Dim lblAnzahlFrames As Label = MyProject.Forms.frmFilming.lblAnzahlFrames
							Dim value5 As Object = 0
							value2 = num86
							Dim value6 As Object = modMain.fmax(value5, value2)
							num86 = Conversions.ToInteger(value2)
							lblAnzahlFrames.Text = Conversions.ToString(value6)
						End If
					Else
						' The following expression was wrapped in a unchecked-expression
						Dim num86 As Integer = CInt(CShort(Math.Round((num9 - CDbl(modDeclares.SystemData.nachspann) / 100.0 - (num71 - CDbl(num43)) * modDeclares.SystemData.AutoTrailerLength) * 1000.0 * modDeclares.SystemData.schrittepromm(CInt(num2)) / CDbl(num20))))
						If modDeclares.SystemData.FesteBelegzahlProFilm Then
							MyProject.Forms.frmFilming.lblAnzahlFrames.Text = Conversions.ToString(num10)
						ElseIf CDbl(num86) < Conversions.ToDouble(MyProject.Forms.frmFilming.lblAnzahlFrames.Text) Or Conversions.ToDouble(MyProject.Forms.frmFilming.lblAnzahlFrames.Text) <= 0.0 Then
							Dim lblAnzahlFrames2 As Label = MyProject.Forms.frmFilming.lblAnzahlFrames
							value2 = 0
							Dim value5 As Object = num86
							Dim value7 As Object = modMain.fmax(value2, value5)
							num86 = Conversions.ToInteger(value5)
							lblAnzahlFrames2.Text = Conversions.ToString(value7)
						End If
					End If
					If i >= 0 Then
						MyProject.Forms.frmFilming.lblAktPage.Text = Conversions.ToString(modDeclares.Images(i).page)
						MyProject.Forms.frmFilming.lblFileName.Text = Strings.Right(modDeclares.Images(i).Name, Strings.Len(modDeclares.Images(i).Name) - Strings.InStrRev(modDeclares.Images(i).Name, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary))
						MyProject.Forms.frmFilming.lblFolder.Text = Strings.Left(modDeclares.Images(i).Name, Strings.InStrRev(modDeclares.Images(i).Name, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
						MyProject.Forms.frmFilming.lblAktDoc.Text = modDeclares.Images(i).DokumentName
					End If
					modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					Application.DoEvents()
					If Not modExpose.ExposeEndSymbols Then
						If modDeclares.SystemData.BaendeVollstaendigBelichten Then
							If i < modDeclares.imagecount Then
								If modDeclares.Images(i + 1).Level > 1S Then
									If modExpose.EOFReached(num9, num10, i) AndAlso modExpose.AnzGesamtEndSymbole > 0 Then
										modExpose.ExposeEndSymbols = True
										num4 = 0
									End If
								ElseIf modExpose.EOFReached(num9, num10, i) AndAlso modExpose.AnzGesamtEndSymbole > 0 Then
									modExpose.ExposeEndSymbols = True
									num4 = 0
								End If
							End If
						ElseIf modExpose.EOFReached(num9, num10, i) AndAlso modExpose.AnzGesamtEndSymbole > 0 Then
							modExpose.ExposeEndSymbols = True
							num4 = 0
						End If
					End If
					Dim flag15 As Boolean = False
					If modDeclares.SystemData.BaendeVollstaendigBelichten Then
						If i < modDeclares.imagecount Then
							If i > 0 And modDeclares.Images(i + 1).Level > 1S Then
								Dim num87 As Double = num9
								Dim num82 As Integer = i + 1
								If num87 - CDbl(modMain.GetDocumentCount(num82)) * modDeclares.SystemData.schrittweite / 1000.0 < CDbl(modDeclares.SystemData.nachspann) / 100.0 Then
									flag15 = True
									If modExpose.AnzGesamtEndSymbole > 0 Then
										flag15 = True
									End If
								End If
								If modExpose.EOFReached(num9, num10, i) Then
									flag15 = True
								End If
							ElseIf modExpose.EOFReached(num9, num10, i) Then
								flag15 = True
								If modExpose.AnzGesamtEndSymbole > 0 Then
									flag15 = True
								End If
							End If
						ElseIf Not modExpose.ExposeEndSymbols AndAlso modExpose.AnzGesamtEndSymbole > 0 Then
							modExpose.ExposeEndSymbols = True
							num4 = 0
						End If
					Else
						Dim num82 As Integer
						If((i = modDeclares.imagecount And Not flag11) Or ((i = modDeclares.imagecount AndAlso flag11) And num33 = modDeclares.SystemData.SplitCount)) AndAlso Not modExpose.ExposeEndSymbols AndAlso modExpose.AnzGesamtEndSymbole > 0 Then
							If modDeclares.SystemData.SMCI Then
								modSMCi.VakuumAusSMCi()
							Else
								modDeclares.Outputs = modDeclares.Outputs And 159
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num82 = 0
								text3 = modMultiFly.Comm_Read(num82, True)
							End If
							value = "TXT_ALL_FILMED1"
							Dim text16 As String = modMain.GetText(value)
							If Operators.CompareString(text16, "", False) = 0 Then
								text16 = "Alle Dokumente wurden verfilmt!" & vbCr & "Sollen jetzt die Endsymbole verfilmt werden?"
								text16 = "All documents have been exposed!" & vbCrLf & "Should the end symbols be exposed now?"
							Else
								text16 += vbCrLf
								Dim str7 As String = text16
								value = "TXT_ALL_FILMED2"
								text16 = str7 + modMain.GetText(value)
							End If
							Dim smci4 As Boolean = modDeclares.SystemData.SMCI
							num76 = 4S
							value = "file-converter"
							If modMain.msgbox2(text16, num76, value) = 6S Then
								If modDeclares.SystemData.SMCI Then
									modSMCi.VakuumAnSMCi()
								Else
									modDeclares.Outputs = modDeclares.Outputs Or 64
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num82 = 0
									text3 = modMultiFly.Comm_Read(num82, True)
									modDeclares.Sleep(modDeclares.SystemData.VacuumOnDelay)
									modDeclares.Outputs = modDeclares.Outputs Or 32
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num82 = 0
									text3 = modMultiFly.Comm_Read(num82, True)
								End If
								modExpose.ExposeEndSymbols = True
								num4 = 0
							End If
						End If
						num82 = 0
						If modExpose.EOFReached(num9, num10, num82) Then
							flag15 = True
						End If
					End If
					Dim flag16 As Boolean = modExpose.ExposeEndSymbols And num4 = modExpose.AnzGesamtEndSymbole
					If modExpose.ExposeEndSymbols And num4 = 0 Then
						Dim num12 As Integer = 0
						modExpose.AnzGesamtEndSymbole = 0
						If flag2 Then
							num12 = modExpose.AnzFortsetzungsSymbole1
							modExpose.GesamtEndSymbole = CType(Utils.CopyArray(modExpose.GesamtEndSymbole, New String(num12 + 1 - 1) {}), String())
							Dim num82 As Integer = num12
							j = 1
							While j <= num82
								modExpose.GesamtEndSymbole(j) = modExpose.FortsetzungsSymbole1(j)
								j += 1
							End While
							modExpose.AnzGesamtEndSymbole = num12
						End If
						If modExpose.AnzEndSymbole > 0 AndAlso (Not flag2 Or (flag2 And Not modDeclares.SystemData.NoSpecialSmybolesWhenContinuation)) Then
							modExpose.GesamtEndSymbole = CType(Utils.CopyArray(modExpose.GesamtEndSymbole, New String(num12 + modExpose.AnzEndSymbole + 1 - 1) {}), String())
							Dim num88 As Integer = num12 + 1
							Dim num81 As Integer = num12 + modExpose.AnzEndSymbole
							j = num88
							While j <= num81
								modExpose.GesamtEndSymbole(j) = modExpose.EndSymbole(j - num12)
								j += 1
							End While
							modExpose.AnzGesamtEndSymbole = num12 + modExpose.AnzEndSymbole
						End If
					End If
					Dim num27 As Integer
					If Not modExpose.ExposeEndSymbols Or (modExpose.ExposeEndSymbols And num4 = modExpose.AnzGesamtEndSymbole) Then
						If flag15 Then
							If Not modDeclares.UseDebug Then
								modDeclares.Outputs = modDeclares.Outputs And 223
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num80 = 0
								text3 = modMultiFly.Comm_Read(num80, True)
								modSMCi.VakuumAusSMCi()
								modSMCi.MagnetAusSMCi()
								If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOff(modDeclares.SystemData.VacuumOff))) Then
									If modDeclares.SystemData.SMCI Then
										modSMCi.VakuumAusSMCi()
										modSMCi.MagnetAusSMCi()
									End If
									modDeclares.Outputs = 0
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
									value = "TXT_ERR_VACUUM_OFF"
									text2 = modMain.GetText(value)
									If Operators.CompareString(text2, "", False) = 0 Then
										text2 = "Vakuum konnte nicht ausgeschaltet werden!"
									End If
									num76 = 0S
									value = "file-converter"
									modMain.msgbox2(text2, num76, value)
								Else
									modDeclares.Outputs = modDeclares.Outputs And -9
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
								End If
							End If
							text3 = Conversions.ToString(0)
							value = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							modExpose.AddTrailer(value)
							num89 = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
							MyProject.Forms.frmFilmTransport.Show()
							MyProject.Forms.frmFilmTransport.Text = "Trailer"
							If Not modDeclares.UseDebug Then
								modDeclares.Outputs = 0
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num80 = 0
								text3 = modMultiFly.Comm_Read(num80, True)
								Application.DoEvents()
								modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
								If modDeclares.SystemData.NeuerMagnet Then
									modDeclares.Outputs = modDeclares.Outputs Or 32
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
									modDeclares.Sleep(modDeclares.SystemData.MagnetDelay)
								End If
								num76 = 1S
								num80 = modMultiFly.GetSpeedFromSteps(num89, modDeclares.SystemData.filmspeed(CInt(num2)))
								num79 = 1
								num77 = 0
								Dim num78 As Integer = 0
								modMultiFly.FahreMotor(num76, num89, num80, num79, num77, num78, modDeclares.SystemData.FResolution(CInt(num2)))
								While True
									num76 = 1S
									If Not modMultiFly.MotorIsRunning(num76) Then
										Exit For
									End If
									Application.DoEvents()
								End While
								flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
								modMultiFly.VNullpunkt(flag, num2)
								num3 = 0S
								If modDeclares.SystemData.NeuerMagnet Then
									modDeclares.Outputs = modDeclares.Outputs And -33
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num78 = 0
									text3 = modMultiFly.Comm_Read(num78, True)
								End If
							End If
							MyProject.Forms.frmFilmTransport.Close()
							Application.DoEvents()

								num9 -= CDbl(modDeclares.SystemData.nachspann) / 100.0
								num10 = modDeclares.SystemData.BelegeProFilm(CInt(num2))
								If Not modDeclares.CalcModus Then
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
								End If
								modDeclares.glbInsertFilmCanceled = False
								Dim text4 As String = Application.StartupPath + "\EXTLOGS\" + MyProject.Forms.frmFilming.lblFilmNr.Text + ".txt"
								If File.Exists(text4) Then
									Interaction.Shell("notepad.exe " + text4, AppWinStyle.MaximizedFocus, False, -1)
								End If

							If modDeclares.SystemData.AutoRollInsert > 0S Then
								MyProject.Forms.frmFilmEinlegen.Show()
								Application.DoEvents()
								num24 = modDeclares.timeGetTime()
								Do
									Application.DoEvents()
								Loop While modDeclares.timeGetTime() - num24 <= CInt((modDeclares.SystemData.AutoRollInsert * 1000S))
								MyProject.Forms.frmFilmEinlegen.cmdStart_ClickEvent(Nothing, New EventArgs())
							Else
								MyProject.Forms.frmFilmEinlegen.ShowDialog()
								MyProject.Forms.frmFilmEinlegen.Dispose()
							End If
							modMain.ShowErrorFile(num17)
							Dim useDebug As Boolean = modDeclares.UseDebug
							If modDeclares.glbInsertFilmCanceled Then
								GoTo Block_492
							End If
							MyProject.Forms.frmGetFilmNo.txtFilmNo.Text = Conversions.ToString(num17 + 1)
							If modDeclares.SystemData.AutoRollInsert > 0S Then
								MyProject.Forms.frmGetFilmNo.Show()
								Application.DoEvents()
								num24 = modDeclares.timeGetTime()
								Do
									Application.DoEvents()
								Loop While modDeclares.timeGetTime() - num24 <= CInt((modDeclares.SystemData.AutoRollInsert * 1000S))
								MyProject.Forms.frmGetFilmNo.Button1_Click(Nothing, New EventArgs())
							Else
								MyProject.Forms.frmGetFilmNo.ShowDialog()
								MyProject.Forms.frmGetFilmNo.Dispose()
							End If
							modDeclares.Blip1Counter = 0
							modDeclares.Blip2Counter = 0
							modDeclares.Blip3Counter = 0
							num17 = CInt(Math.Round(Conversion.Val(modDeclares.ffrmFilmPreview.txtFilmNr.Text)))
							modMain.ProtIndex = 1
							Dim value5 As Object = num17
							modExpose.ClearLog(value5)
							num17 = Conversions.ToInteger(value5)
							FileSystem.FileOpen(CInt(num25), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
							FileSystem.PrintLine(CInt(num25), New Object() { num17 + 1 })
							FileSystem.FileClose(New Integer() { CInt(num25) })
							If modDeclares.SystemData.BayHStA Then
								Dim num26 As Short = CShort(FileSystem.FreeFile())
								FileSystem.FileOpen(CInt(num26), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
								FileSystem.Print(CInt(num26), New Object() { Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + ";" })
								flag6 = False
								If flag2 Then
									FileSystem.Print(CInt(num26), New Object() { "Y;" + Strings.Right(modDeclares.Images(i + modDeclares.SystemData.NumberOfRepetetionFrames).DokumentName, 5) + ";" })
								Else
									FileSystem.PrintLine(CInt(num26), New Object() { "N;" })
								End If
								FileSystem.FileClose(New Integer() { CInt(num26) })
							End If
							k = If(-If((modDeclares.WritePrivateProfileString("SYSTEM", "FILMNO" + Conversions.ToString(CInt(num2)), modDeclares.ffrmFilmPreview.txtFilmNr.Text, lpFileName) > False), 1, 0), 1, 0)
							num27 = CInt(Math.Round(CDbl(modDeclares.SystemData.vorspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
							MyProject.Forms.frmFilmTransport.Show()
							MyProject.Forms.frmFilmTransport.Text = "Leader"
							Application.DoEvents()
							If Not modDeclares.UseDebug Then
								modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
								Dim num78 As Integer
								If modDeclares.SystemData.NeuerMagnet Then
									modDeclares.Outputs = modDeclares.Outputs Or 32
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num78 = 0
									text3 = modMultiFly.Comm_Read(num78, True)
									modDeclares.Sleep(modDeclares.SystemData.MagnetDelay)
								End If
								num76 = 1S
								num78 = modMultiFly.GetSpeedFromSteps(num27, modDeclares.SystemData.filmspeed(CInt(num2)))
								num77 = 1
								num79 = 0
								num80 = 0
								modMultiFly.FahreMotor(num76, num27, num78, num77, num79, num80, modDeclares.SystemData.FResolution(CInt(num2)))
								While True
									num76 = 1S
									If Not modMultiFly.MotorIsRunning(num76) Then
										Exit For
									End If
									Application.DoEvents()
								End While
								If modDeclares.SystemData.NeuerMagnet Then
									modDeclares.Outputs = modDeclares.Outputs And -33
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
								End If
							End If
							MyProject.Forms.frmFilmTransport.Close()
							Application.DoEvents()
							If modDeclares.SystemData.UseStartFrame Or modExpose.AnzGesamtStartSymbole > 0 Then
								flag5 = True
								num18 -= 1
								If modDeclares.SystemData.UseStartFrame Then
									num32 = -1
									If modExpose.AnzGesamtStartSymbole <= 0 Then
										num32 = 0
									End If
								ElseIf modExpose.AnzGesamtStartSymbole > 0 Then
									num32 = 0
								Else
									flag5 = False
									num18 += 1
								End If
							End If
							value = modMain.GiveIni(lpFileName, "SYSTEM", "FILMLAENGE" + Conversions.ToString(CInt(num2)))
							num9 = Conversion.Val(modMain.KommazuPunkt(value)) - CDbl(modDeclares.SystemData.vorspann) / 100.0
							num10 = modDeclares.SystemData.BelegeProFilm(CInt(num2))
							If flag3 Then
								num10 += modDeclares.SystemData.NumberOfRepetetionFrames
							End If
							Dim num12 As Integer

								If Not modDeclares.CalcModus Then
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
								End If
								If Not modDeclares.UseDebug Then
									If modDeclares.SystemData.CheckVakuum Then
										modDeclares.Outputs = modDeclares.Outputs Or 64
										text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
										modMultiFly.Comm_Send(text3)
										num80 = 0
										text3 = modMultiFly.Comm_Read(num80, True)
										modDeclares.Sleep(modDeclares.SystemData.VacuumOnDelay)
										If modDeclares.SystemData.SMCI Then
											modSMCi.VakuumAnSMCi()
										End If
									End If
									modDeclares.Outputs = modDeclares.Outputs Or 32
									text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
									modSMCi.MagnetAnSMCi()
								End If
								MyProject.Forms.frmFilming.lblFilmNr.Text = Conversions.ToString(num17)
								FileSystem.FileOpen(CInt(num25), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
								FileSystem.PrintLine(CInt(num25), New Object() { num17 })
								FileSystem.FileClose(New Integer() { CInt(num25) })
								modDeclares.ffrmFilmPreview.txtFilmNr.Text = Conversions.ToString(num17)
								value = modMain.GiveIni(lpFileName, "SYSTEM", "FILMLAENGE" + Conversions.ToString(CInt(num2)))
								num9 = Conversion.Val(modMain.KommazuPunkt(value)) - CDbl(modDeclares.SystemData.vorspann) / 100.0
								num8 = 0
								If Not modDeclares.CalcModus Then
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
									k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2)), Conversion.Str(num8), lpFileName) > False), 1, 0)), 1, 0)
								End If
								modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
								If modDeclares.SystemData.UseStartFrame Or modExpose.AnzGesamtStartSymbole > 0 Then
									flag5 = True
								End If
								num12 = 0

							If modExpose.AnzStartSymbole > 0 AndAlso (Not flag2 Or Not modDeclares.SystemData.NoSpecialSmybolesWhenContinuation) Then
								num12 = modExpose.AnzStartSymbole
								modExpose.GesamtStartSymbole = CType(Utils.CopyArray(modExpose.GesamtStartSymbole, New String(num12 + 1 - 1) {}), String())
								num80 = num12
								j = 1
								While j <= num80
									modExpose.GesamtStartSymbole(j) = modExpose.StartSymbole(j)
									j += 1
								End While
							End If
							If flag2 AndAlso modExpose.AnzFortsetzungsSymbole2 > 0 Then
								modExpose.GesamtStartSymbole = CType(Utils.CopyArray(modExpose.GesamtStartSymbole, New String(num12 + modExpose.AnzFortsetzungsSymbole2 + 1 - 1) {}), String())
								Dim num90 As Integer = num12 + 1
								num79 = num12 + modExpose.AnzFortsetzungsSymbole2
								j = num90
								While j <= num79
									modExpose.GesamtStartSymbole(j) = modExpose.FortsetzungsSymbole2(j - num12)
									j += 1
								End While
								num12 += modExpose.AnzFortsetzungsSymbole2
							End If
							modExpose.AnzGesamtStartSymbole = num12
							value = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							text = "1"
							modExpose.SetContinuationInfoFileForRefilm(value, text)
						End If

							If flag2 Then
								k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(num2)), "1", lpFileName) > False), 1, 0)), 1, 0)
								modDeclares.ffrmFilmPreview.cmdFortsetzung.Tag = "1"
								Dim cmdFortsetzung As ButtonBase = modDeclares.ffrmFilmPreview.cmdFortsetzung
								text = "TXT_ROLL_IS_CONT"
								cmdFortsetzung.Text = modMain.GetText(text)
								If Operators.CompareString(modDeclares.ffrmFilmPreview.cmdFortsetzung.Text, "", False) = 0 Then
									modDeclares.ffrmFilmPreview.cmdFortsetzung.Text = "Rolle ist eine Fortsetzung"
								End If
							Else
								k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
								modDeclares.ffrmFilmPreview.cmdFortsetzung.Tag = "0"
								Dim cmdFortsetzung2 As ButtonBase = modDeclares.ffrmFilmPreview.cmdFortsetzung
								text = "TXT_ROLL_IS_NOT_CONT"
								cmdFortsetzung2.Text = modMain.GetText(text)
								If Operators.CompareString(modDeclares.ffrmFilmPreview.cmdFortsetzung.Text, "", False) = 0 Then
									modDeclares.ffrmFilmPreview.cmdFortsetzung.Text = "Rolle ist KEINE Fortsetzung"
								End If
							End If
							flag3 = False
							flag2 = False

					End If
					Dim num91 As Integer = i
					If Not(flag5 Or modExpose.ExposeEndSymbols) Then
						If flag7 Then
							i += 1
							flag7 = False
						Else
							If flag9 Then
								If num33 = modDeclares.SystemData.SplitCount Then
									num33 = 0S
								Else
									num33 += 1S
								End If
							End If
							If num33 = 0S Then
								If i < modDeclares.imagecount - 1 Then
									If modDeclares.Images(i + 1).Level > 1S Then
										Dim num72 As Integer = 1
										Dim num74 As Integer = i
										While num74 >= 1 AndAlso modDeclares.Images(num74).Level <= 1S
											num72 += 1
											num74 += -1
										End While
										num25 = CShort(FileSystem.FreeFile())
									End If
									If modDeclares.Images(i + 1).Level > 1S And modDeclares.SystemData.UseSeparateFrame Then
										flag7 = True
										Dim num92 As Double
										If modDeclares.SystemData.StepsImageToImage Then
											' The following expression was wrapped in a unchecked-expression
											num92 = CDbl(modDeclares.SystemData.Breite) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) + modDeclares.SystemData.schrittweite
										Else
											num92 = modDeclares.SystemData.schrittweite
										End If
										num77 = i + 1

											If CDbl(modMain.GetDocCount(num77)) * num92 / 1000.0 > num9 - CDbl(modDeclares.SystemData.nachspann) / 100.0 And num8 > 1 Then
												num9 = 0.0
												If Not modDeclares.CalcModus Then
													k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
													k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
												End If
											End If

									Else
										i += 1
									End If
								Else
									Dim num93 As Integer = 1
									Dim num94 As Integer = i
									While num94 >= 1 AndAlso modDeclares.Images(num94).Level <= 1S
										num93 += 1
										num94 += -1
									End While
									num25 = CShort(FileSystem.FreeFile())
									i += 1
								End If
							End If
						End If
					Else
						If flag5 Then
							If modExpose.AnzGesamtStartSymbole > 0 And Not flag13 Then
								If num32 < modExpose.AnzGesamtStartSymbole Then
									num32 += 1
								Else
									flag5 = False
									num32 = 0
									If i = -1 Then
										i = 0
									End If
								End If
							End If
						ElseIf Not modExpose.ExposeEndSymbols Then
							i += 1
						End If
						flag7 = False
					End If
					If i <> num91 AndAlso i <= modDeclares.imagecount AndAlso modMain.IsUnicode(modDeclares.Images(i).Name) AndAlso File.Exists(text12) Then
						FileSystem.Kill(text12)
					End If
					If Not modDeclares.SystemData.CheckVakuum AndAlso (modMultiFly.FilmEnde() And modDeclares.SystemData.CheckFilmEnde) Then
						GoTo Block_550
					End If
					If modExpose.ExposeEndSymbols Then
						num4 += 1
						If num4 > modExpose.AnzGesamtEndSymbole Then
							modExpose.ExposeEndSymbols = False
							If i = modDeclares.imagecount Then
								i += 1
							End If
						End If
					End If
					If i - 1 >= modPaint.pos And i - 1 <= modPaint.pos + 5 Then
						modDeclares.ffrmFilmPreview.SetShpFilmedBackColor(i - modPaint.pos - 1, ColorTranslator.FromOle(Information.RGB(255, 255, 255)))
					End If
					If i > modDeclares.imagecount Then
						GoTo IL_8F29
					End If
					Continue For
					IL_37A5:
					If modDeclares.SystemData.JPEGProcessor AndAlso ((flag11 And num33 = modDeclares.SystemData.SplitCount) Or Not flag11) AndAlso i > 0 Then
						lpFileName = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
						modMain.temppath = modMain.GiveIni(lpFileName, "SYSTEM", "RAMDRIVE")
						Dim text17 As String = modMain.temppath + "\" + Strings.Mid(modDeclares.Images(i - 1).Name, Strings.InStrRev(modDeclares.Images(i - 1).Name, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
						text17 = Strings.Left(text17, Strings.Len(text17) - 4) + "_" + Conversions.ToString(modDeclares.Images(i - 1).page) + ".tif"
						If File.Exists(text17) Then
							FileSystem.Kill(text17)
						End If
					End If
					If modDeclares.SystemData.Invers And Not(flag5 And num32 = 0) Then
						Dim num95 As Short = CShort(MyProject.Forms.frmImage.IResX)
						MyProject.Forms.frmImage.Negate()

							MyProject.Forms.frmImage.IResX = CLng(num95)
							MyProject.Forms.frmImage.IResY = CLng(num95)

					End If
					If Not flag5 Then
						modDeclares.SystemData.ShowAddRollFrame = False
					End If
					If flag5 And num32 = 0 And modDeclares.SystemData.UseStartFrame Then
						modDeclares.SystemData.ShowAddRollFrame = False
						If flag13 Then
							modDeclares.SystemData.ShowAddRollFrame = True
							MyProject.Forms.frmGetAddRollFrameLines.ShowDialog()
							flag13 = False
						Else
							modDeclares.SystemData.ShowAddRollFrame = False
							If modDeclares.SystemData.UseAddRollFrame Then
								flag13 = True
							End If
						End If
						If modDeclares.SystemData.EnableRollFrameExt Then
							Dim num96 As Integer = i
							If num96 > 0 AndAlso modDeclares.Images(num96).Level = 1S Then
								num96 += 1
							End If
							k = If(-If((modMain.GetFolderNamesThatFitOnFilm(modDeclares.Images, modDeclares.imagecount, num96, modDeclares.StartFolder, modDeclares.EndFolder, num2) > False), 1, 0), 1, 0)
							Dim str8 As String
							Dim str9 As String
							modMain.SplitNorwayFileName(modDeclares.Images(Conversions.ToInteger(Interaction.IIf(i < 0, 0, i))).DokumentName, str8, str9)
							modDeclares.SystemData.RollFrameExtLine1 = Support.Format(Strings.Left(str9, 1), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + Strings.Mid(str9, 2)
							modDeclares.SystemData.RollFrameExtLine2 = modMain.ConvertFolderToDate(modDeclares.StartFolder)
							If Operators.CompareString(modDeclares.SystemData.RollFrameExtLine2, "", False) <> 0 Then
								modDeclares.SystemData.RollFrameExtLine2 = modDeclares.SystemData.RollFrameExtLine2 + " -"
							End If
							modDeclares.SystemData.RollFrameExtLine3 = modMain.ConvertFolderToDate(modDeclares.EndFolder)
							modMain.SplitNorwayFileName(modDeclares.EndFolder, str8, str9)
							modDeclares.SystemData.RollFrameExtLine3 = modDeclares.SystemData.RollFrameExtLine3 + " " + Strings.Left(str8, 4)
						End If
						modDeclares.SystemData.UseAnno = False
						modDeclares.SystemData.UseBlip = False
						MyProject.Forms.frmImage.BackColor = ColorTranslator.FromOle(Information.RGB(255, 255, 255))
						Dim enableRollFrameExt As Boolean = modDeclares.SystemData.EnableRollFrameExt
						Dim text16 As String = Conversions.ToString(num17)
						While Strings.Len(text16) < modDeclares.SystemData.RollNoLen
							text16 = "0" + text16
						End While
						modDeclares.SystemData.RollenNr = modDeclares.SystemData.RollenNrPrefix + text16 + modDeclares.SystemData.RollenNrPostfix
						MyProject.Forms.frmImage.ImagXpress1.Visible = False
						MyProject.Forms.frmImage.Show()
						MyProject.Forms.frmImage.NoPaint = False
						MyProject.Forms.frmImage.Refresh()
						modDeclares.Sleep(modDeclares.SystemData.WaitAfterDraw)
						Application.DoEvents()
					Else
						modDeclares.SystemData.RollenNr = ""
						Dim useAccusoft As Boolean = modDeclares.UseAccusoft
						MyProject.Forms.frmImage.BackColor = ColorTranslator.FromOle(Information.RGB(0, 0, 0))
					End If
					If flag5 Then
						modDeclares.SystemData.Anno = ""
					End If
					If modExpose.ExposeEndSymbols Then
						modDeclares.SystemData.Anno = ""
					End If
					If modDeclares.SystemData.UseBlip Then
						If modDeclares.glbOrientation Then
							MyProject.Forms.frmBlipWin.ShpBLIP_.Width = CInt(Math.Round(Support.TwipsToPixelsX(CDbl((modDeclares.SystemData.BlipBreiteGross * 15)))))
						Else
							MyProject.Forms.frmBlipWin.ShpBLIP_.Height = CInt(Math.Round(Support.TwipsToPixelsY(CDbl((modDeclares.SystemData.BlipBreiteGross * 15)))))
						End If
						modBLIP.SetBlipSizes(modDeclares.Images(i).Level)
						If modDeclares.SystemData.AnnoStyle = 6S Then
							If i > 0 Then
								If modDeclares.Images(i).Level > modDeclares.Images(i - 1).Level Then
									If modDeclares.Images(i).Level = 2S Then
										modDeclares.Blip2Counter += 1
										modDeclares.Blip1Counter = 0
										modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip2Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
									End If
									If modDeclares.Images(i).Level = 3S Then
										modDeclares.Blip3Counter += 1
										modDeclares.Blip1Counter = 0
										modDeclares.Blip2Counter = 0
										modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip3Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
									End If
								Else
									modDeclares.Blip1Counter += 1
									modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip1Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
								End If
							Else
								Select Case modDeclares.Images(i).Level
									Case 1S
										modDeclares.Blip1Counter += 1
										modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip1Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
									Case 2S
										modDeclares.Blip2Counter += 1
										modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip2Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
									Case 3S
										modDeclares.Blip3Counter += 1
										modDeclares.SystemData.Anno = Strings.Format(modDeclares.Blip3Counter, New String("0"c, CInt(modDeclares.SystemData.AnnoBlipLen)))
								End Select
							End If
						End If
					End If
					modSMCi.LEDAusSMCi()
					If flag5 Or modExpose.ExposeEndSymbols Then
						modDeclares.SystemData.Anno = ""
					End If
					If(flag5 And num32 = 0) AndAlso modDeclares.UseDebug Then
						modDeclares.Sleep(modDeclares.SystemData.SIMULATIONDELAY)
					End If
					If Not(flag5 And num32 = 0) Then
						If flag5 Or modExpose.ExposeEndSymbols Then
							Dim systemData As modDeclares.typSystem = modDeclares.SystemData
							Dim systemData2 As modDeclares.typSystem = modDeclares.SystemData
						End If
						MyProject.Forms.frmBlipWin.Refresh()
						If i >= 0 Then
							text = modDeclares.Images(i).DokumentName
							modMain.LogFaktor(text)
							GoTo IL_3F13
						End If
						GoTo IL_3F13
					End If
					IL_4347:
					Dim num97 As Short = CShort(modDeclares.SystemData.RetrySecondLevel)
					Dim value8 As Object
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
					Dim num104 As Double
					While True
						IL_557A:
						modMain.EnterCore()
						If modDeclares.UseDebug Then
							text = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							modMain.UpdateRollInfoFileFrameCounter(text)
						End If
						modSMCi.LEDAnSMCi()
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
							If modDeclares.SystemData.SmallShutter Then
								num = 1 - num
							End If
							Dim flag17 As Boolean
							If num22 = 0.0 Then
								num76 = 2S
								num79 = 0
								num80 = 0
								flag17 = modMultiFly.FahreMotor(num76, modDeclares.SystemData.belichtung, verschlussgeschw, num, num79, num80, modDeclares.SystemData.VResolution)
								While True
									num76 = 2S
									If Not modMultiFly.MotorIsRunning(num76) Then
										Exit For
									End If
									Application.DoEvents()
								End While
							Else
								num76 = 2S
								num80 = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
								num79 = 0
								num77 = 0
								flag17 = modMultiFly.FahreMotor(num76, num80, verschlussgeschw, num, num79, num77, modDeclares.SystemData.VResolution)
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
								num79 = 0
								num80 = 0
								flag17 = modMultiFly.FahreMotor(num76, num77, verschlussgeschw, num, num79, num80, modDeclares.SystemData.VResolution)
								While True
									num76 = 2S
									If Not modMultiFly.MotorIsRunning(num76) Then
										Exit For
									End If
									Application.DoEvents()
								End While
							End If
							modSMCi.LEDAusSMCi()
							modDeclares.NoPaint = True
							MyProject.Forms.frmImage.ImagXpress1.Image = Nothing
							modMain.glImage.Dispose()
							text = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							modMain.UpdateRollInfoFileFrameCounter(text)
							If Not flag17 Then
								GoTo Block_318
							End If
						End If
						MyProject.Forms.frmImage.NoPaint = True
						MyProject.Forms.frmImage.Hide()
						If modDeclares.SystemData.UseAnno Then
							MyProject.Forms.frmAnnoWin.Hide()
						End If
						If modDeclares.SystemData.UseBlip Then
							MyProject.Forms.frmBlipWin.Hide()
						End If
						Application.DoEvents()
						If modDeclares.UseDebug Or modDeclares.CalcModus Then
							GoTo IL_58CB
						End If
						Dim value9 As Object
						While True
							num76 = 2S
							If Not modMultiFly.MotorIsRunning(num76) Then
								GoTo IL_58CB
							End If
							If Conversions.ToBoolean(value9) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						IL_62E4:
						If Not Conversions.ToBoolean(value9) Then
							Exit For
						End If
						modMain.ClearCoreErrorCondition()
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							modDeclares.Outputs = modDeclares.Outputs And 223
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num80 = 0
							text3 = modMultiFly.Comm_Read(num80, True)
						End If
						modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
						If modDeclares.SystemData.SmallShutter Then
							num76 = 2S
							num80 = 0
							num79 = 0
							num77 = CInt((1S - modDeclares.SystemData.SmallShutterFirstDir))
							num29 = 1
							Dim num81 As Integer = 1
							modMultiFly.FahreMotor(num76, num80, num79, num77, num29, num81, modDeclares.SystemData.VResolution)
						Else
							num76 = 2S
							Dim num81 As Integer = 0
							num29 = 0
							num77 = 1
							num79 = 1
							num80 = 1
							modMultiFly.FahreMotor(num76, num81, num29, num77, num79, num80, modDeclares.SystemData.VResolution)
						End If
						While True
							num76 = 2S
							If Not modMultiFly.MotorIsRunning(num76) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						Dim num102 As Integer = Conversions.ToInteger(value8)
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAusSMCi()
						End If
						If modDeclares.SystemData.NeuerMagnet Then
							modMultiFly.MagnetPlatteHoch()
						End If
						num76 = 1S
						num80 = modMultiFly.GetSpeedFromSteps(num102, modDeclares.SystemData.filmspeed(CInt(num2)))
						num79 = 1
						num77 = 0
						num29 = 0
						modMultiFly.FahreMotor(num76, num102, num80, num79, num77, num29, modDeclares.SystemData.FResolution(CInt(num2)))
						While True
							num76 = 1S
							If Not modMultiFly.MotorIsRunning(num76) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAnSMCi()
						End If
						If modDeclares.SystemData.NeuerMagnet Then
							modMultiFly.MagnetPlatteRunter()
							Continue For
						End If
						Continue For
						IL_58CB:
						Dim num101 As Short = If(-If((modMultiFly.VacuumOk() > False), 1S, 0S), 1S, 0S)
						If Conversions.ToBoolean(value9) Then
							GoTo IL_62E4
						End If
						If CInt(num3) = modDeclares.SystemData.schlitze - 1 Then
							text3 = ChrW(25) & "="
							If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
								If modDeclares.SystemData.SMCI Then
									num101 = 0S
									If modSMCi.VerschlussIstAufNullpunktSMCi() Then
										num101 = 1S
									End If
								Else
									modMultiFly.Comm_Send(text3)
									num80 = 0
									text3 = modMultiFly.Comm_Read(num80, True)
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
						If Conversions.ToBoolean(value9) Then
							GoTo IL_62E4
						End If
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							If modDeclares.SystemData.SMCI Then
								modSMCi.MagnetAusSMCi()
							Else
								modDeclares.Outputs = modDeclares.Outputs And 223
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num80 = 0
								text3 = modMultiFly.Comm_Read(num80, True)
							End If
						End If
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							num24 = modDeclares.GetTickCount()
							If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOff(modDeclares.SystemData.VacuumOff))) Then
								If modDeclares.SystemData.SMCI Then
									modSMCi.VakuumAusSMCi()
									modSMCi.MagnetAusSMCi()
								End If
								modDeclares.Outputs = 0
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num80 = 0
								text3 = modMultiFly.Comm_Read(num80, True)
								text = "TXT_ERR_VACUUM_OFF"
								text2 = modMain.GetText(text)
								If Operators.CompareString(text2, "", False) = 0 Then
									text2 = "Vakuum konnte nicht ausgeschaltet werden!"
								End If
								num76 = 0S
								text = "file-converter"
								modMain.msgbox2(text2, num76, text)
							ElseIf Not modDeclares.SystemData.SMCI Then
								modDeclares.Outputs = modDeclares.Outputs And -9
								text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
								modMultiFly.Comm_Send(text3)
								num80 = 0
								text3 = modMultiFly.Comm_Read(num80, True)
							End If
						End If
						If modDeclares.CurJob.Einzel Then
							modDeclares.Sleep(1000)
							If Interaction.MsgBox("Nächste Aufnahme?", MsgBoxStyle.YesNo, Nothing) <> MsgBoxResult.Yes Then
								modDeclares.finish = True
							End If
						End If
						If Not modDeclares.UseDebug Then
							Dim smci5 As Boolean = modDeclares.SystemData.SMCI
							If modDeclares.SystemData.NeuerMagnet Then
								modMultiFly.MagnetPlatteHoch()
							End If
						End If
						Dim num103 As Integer = 0
						num104 = num9
						If i < modDeclares.imagecount And num33 = 0S Then
							If modDeclares.Images(i + 1).Level = 3S And i >= 0 Then
								' The following expression was wrapped in a unchecked-expression
								num103 = CInt(Math.Round(modDeclares.SystemData.AddStepLevel3 * modDeclares.SystemData.schrittepromm(CInt(num2))))

									num9 -= modDeclares.SystemData.AddStepLevel3 / 1000.0

							End If
							If modDeclares.Images(i + 1).Level = 2S And i >= 0 Then
								' The following expression was wrapped in a unchecked-expression
								num103 = CInt(Math.Round(modDeclares.SystemData.AddStepLevel2 * modDeclares.SystemData.schrittepromm(CInt(num2))))

									num9 -= modDeclares.SystemData.AddStepLevel2 / 1000.0

							End If
							If flag5 Then
								num103 = 0
							End If
						End If
						Dim right As Object = 0
						modDeclares.Sleep(modDeclares.SystemData.AfterVacuumOff)
						If Not modDeclares.finish Then
							If(flag5 Or modExpose.ExposeEndSymbols) And modDeclares.SystemData.OneToOneExposure Then
								' The following expression was wrapped in a unchecked-expression
								num40 = CInt(Math.Round(CDbl(modDeclares.SystemData.Breite) * modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.schrittepromm(CInt(num2))))
								right = CDbl(modDeclares.SystemData.AddRollStartFrameSteps) + modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2))
							End If
							If modDeclares.SystemData.StepsImageToImage Then
								If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
									modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
									value8 = num40
									num76 = 1S
									num80 = Conversions.ToInteger(Operators.AddObject(num40 + num103, right))
									num79 = modMultiFly.GetSpeedFromSteps(num40, modDeclares.SystemData.filmspeed(CInt(num2)))
									num77 = 1
									num29 = 0
									Dim num81 As Integer = 0
									modMultiFly.FahreMotor(num76, num80, num79, num77, num29, num81, modDeclares.SystemData.FResolution(CInt(num2)))
									While True
										num76 = 1S
										If Not modMultiFly.MotorIsRunning(num76) Then
											Exit For
										End If
										Application.DoEvents()
									End While
								End If

									If Not flag5 Then
										num9 -= CDbl(num40) / modDeclares.SystemData.schrittepromm(CInt(num2)) / 1000.0
										If Not modDeclares.CalcModus Then
											k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
											k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
										End If
									End If
									num75 = Conversions.ToDouble("0" + modMain.GiveIni(lpFileName, "SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2))))
									num75 += CDbl(num40) / modDeclares.SystemData.schrittepromm(CInt(num2)) / 1000.0
									If Not modDeclares.CalcModus Then
										k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2)), Conversion.Str(num75), lpFileName) > False), 1, 0)), 1, 0)
									End If

							Else
								num102 = num20
								If Math.Abs(num5) >= 1.0 Then
									' The following expression was wrapped in a unchecked-expression
									num102 = CInt(Math.Round(CDbl(num20) + 1.0 * num5 / Math.Abs(num5)))

										num5 -= 1.0 * num5 / Math.Abs(num5)

								End If
								If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
									modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
									value8 = num102
									num76 = 1S
									Dim num81 As Integer = Conversions.ToInteger(Operators.AddObject(num102 + num103, right))
									num29 = modMultiFly.GetSpeedFromSteps(num102, modDeclares.SystemData.filmspeed(CInt(num2)))
									num77 = 1
									num79 = 0
									num80 = 0
									If Not modMultiFly.FahreMotor(num76, num81, num29, num77, num79, num80, modDeclares.SystemData.FResolution(CInt(num2))) Then
										GoTo Block_356
									End If
									While True
										num76 = 1S
										If Not modMultiFly.MotorIsRunning(num76) Then
											Exit For
										End If
										Application.DoEvents()
									End While
								End If

									num5 = num5 + modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2)) - CDbl(num102)
									If Not flag5 Then
										num9 -= CDbl(num20) / modDeclares.SystemData.schrittepromm(CInt(num2)) / 1000.0
										If Not modDeclares.CalcModus Then
											k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
											k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
										End If
									End If
									If Not modDeclares.CalcModus Then
										num75 = Conversions.ToDouble("0" + modMain.GiveIni(lpFileName, "SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2))))
									End If
									num75 += CDbl(num20) / modDeclares.SystemData.schrittepromm(CInt(num2)) / 1000.0
									If Not modDeclares.CalcModus Then
										k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2)), Conversion.Str(num75), lpFileName) > False), 1, 0)), 1, 0)
									End If

							End If
						End If
						modDeclares.Sleep(modDeclares.SystemData.AfterVacuumOn)
						If i < modDeclares.imagecount Then
							modMain.ReadFile(modDeclares.Images(i + 1).Name)
						End If
						If modDeclares.SystemData.PRECACHEIMAGES AndAlso i + 1 <= modDeclares.imagecount Then
							modMain.CurFileNameLoaded = modDeclares.Images(i + 1).Name
							modMain.CurPageLoaded = modDeclares.Images(i + 1).page
							If modDeclares.UseAccusoft Then
								k = modMain.FH_IG_load_file(modMain.CurFileNameLoaded, modMain.PreCacheHandle, modMain.CurPageLoaded)
							Else
								Dim num61 As Integer = num64
								Dim num62 As Integer = num63
								If num61 > num62 Then
									num61 = num63
									num62 = num64
								End If
								Dim flag18 As Boolean = num62 > 7680 And num61 > 4800
								MyProject.Forms.frmImage.LoadFile(modMain.CurFileNameLoaded, CLng(modMain.CurPageLoaded))
							End If
						End If
						While True
							num76 = 1S
							If Not modMultiFly.MotorIsRunning(num76) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						If Not flag5 And Not modExpose.ExposeEndSymbols Then
							num10 -= 1
						End If
						MyProject.Forms.frmFilming.lblExposedFrames.Text = Conversions.ToString(modDeclares.SystemData.BelegeProFilm(CInt(num2)) - num10)
						If modDeclares.UseDebug Then
							GoTo IL_62E4
						End If
						If modDeclares.SystemData.CheckVakuum Then
							modDeclares.Outputs = modDeclares.Outputs Or 64
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num80 = 0
							text3 = modMultiFly.Comm_Read(num80, True)
							If modDeclares.SystemData.SMCI Then
								modSMCi.VakuumAnSMCi()
							End If
						End If
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAnSMCi()
						End If
						modDeclares.Outputs = modDeclares.Outputs Or 32
						Dim smci6 As Boolean = modDeclares.SystemData.SMCI
						If modDeclares.SystemData.NeuerMagnet Then
							modMultiFly.MagnetPlatteRunter()
						End If
						If modDeclares.SystemData.SMCI Then
							GoTo IL_62E4
						End If
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
							modMultiFly.Comm_Send(text3)
							num80 = 0
							text3 = modMultiFly.Comm_Read(num80, True)
							GoTo IL_62E4
						End If
						GoTo IL_62E4
					End While
					Application.DoEvents()
					modMain.LeaveCore()
					If modDeclares.SystemData.BayHStA AndAlso i >= 0 AndAlso (modDeclares.Images(i).Level = 2S And Not flag5 And Not modExpose.ExposeEndSymbols) Then
						Dim num26 As Short = CShort(FileSystem.FreeFile())
						FileSystem.FileOpen(CInt(num26), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.TXT", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
						FileSystem.Print(CInt(num26), New Object() { Strings.Right(modDeclares.Images(i).DokumentName, 5) + ";" })
						FileSystem.FileClose(New Integer() { CInt(num26) })
					End If
					modDeclares.SystemData.Anno = ""
					num8 += 1
					Dim text18 As String
					Dim text19 As String

						If Not modDeclares.CalcModus Then
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2)), Conversion.Str(num8), lpFileName) > False), 1, 0)), 1, 0)
						End If
						If i >= 0 Then
							Using streamWriter2 As StreamWriter = New StreamWriter(MyProject.Application.Info.DirectoryPath + "\FILMLOGS\" + num17.ToString() + ".LOG", True, Encoding.Unicode)
								streamWriter2.Write(modDeclares.Images(i).Name + ":" + modDeclares.Images(i).page.ToString())
								streamWriter2.Close()
							End Using
						End If
						If i < 0 Then
							GoTo IL_6841
						End If
						text18 = Support.Format(num7 - num104, "0.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						text19 = String.Concat(New String() { Conversions.ToString(modDeclares.Images(i).Blip3Level), "-", Conversions.ToString(modDeclares.Images(i).Blip2Level), "-", Conversions.ToString(modDeclares.Images(i).Blip1Level) })

					If modDeclares.SystemData.StartBlipAtOne And modDeclares.gllevel > 1 Then
						text19 = String.Concat(New String() { Conversions.ToString(modDeclares.Images(i).Blip3Level), "-", Conversions.ToString(modDeclares.Images(i).Blip2Level), "-", Conversions.ToString(modDeclares.Images(i).Blip1Level + 1) })
					End If
					If Not(Not flag7 And Not flag5 And Not modExpose.ExposeEndSymbols) Then
						GoTo IL_6841
					End If
					If flag8 Then
						If Not modDeclares.CalcModus Then
							modMain.AddErrorLine(num17, modDeclares.Images(i).Name, modDeclares.Images(i).page, text19, text18, str5, flag8, num59, text14)
							If modDeclares.TESTMODE Then
								text = String.Concat(New String() { "Index=", Conversions.ToString(i), " Name=", modDeclares.Images(i).Name, " Page = ", Conversions.ToString(modDeclares.Images(i).page) })
								num76 = 0S
								value = "file-converter"
								modMain.msgbox2(text, num76, value)
							End If
						End If
						flag8 = False
						GoTo IL_6841
					End If
					If Not modDeclares.CalcModus Then
						modMain.AddProtLine(num17, modDeclares.Images(i).Name, modDeclares.Images(i).page, text19, text18, str5, flag8, i)
						GoTo IL_6841
					End If
					GoTo IL_6841
					IL_4A1E:
					modDeclares.Outputs = 0
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					modMultiFly.Comm_Send(text3)
					num79 = 0
					text3 = modMultiFly.Comm_Read(num79, True)
					modSMCi.LEDAnSMCi()
					modSMCi.VakuumAusSMCi()
					modSMCi.MagnetAusSMCi()
					If modDeclares.vacuum_stop Then
						GoTo Block_276
					End If
					If Not modDeclares.vacuum_trailer Then
						GoTo IL_557A
					End If
					MyProject.Forms.frmImage.Close()
					num89 = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
					Dim num105 As Integer = CInt(Math.Round(CDbl(num89) / CDbl(num20) + 1.0))
					i -= num105
					If i < 0 Then
						i = 0
					End If
					num9 = 0.0
					num10 = 0
					If Not modExpose.EOFReached(num9, num10, i) Then
						GoTo IL_557A
					End If
					modDeclares.Outputs = 0
					text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					modMultiFly.Comm_Send(text3)
					num79 = 0
					text3 = modMultiFly.Comm_Read(num79, True)
					If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOff(modDeclares.SystemData.VacuumOff))) Then
						If modDeclares.SystemData.SMCI Then
							modSMCi.VakuumAusSMCi()
							modSMCi.MagnetAusSMCi()
						End If
						modDeclares.Outputs = 0
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num79 = 0
						text3 = modMultiFly.Comm_Read(num79, True)
						text = "TXT_ERR_VACUUM_OFF"
						text2 = modMain.GetText(text)
						If Operators.CompareString(text2, "", False) = 0 Then
							text2 = "Vakuum konnte nicht ausgeschaltet werden!"
						End If
						num76 = 0S
						text = "file-converter"
						modMain.msgbox2(text2, num76, text)
					Else
						modDeclares.Outputs = modDeclares.Outputs And -9
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num79 = 0
						text3 = modMultiFly.Comm_Read(num79, True)
					End If
					text = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					modExpose.AddTrailer(text)
					num89 = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
					MyProject.Forms.frmFilmTransport.Show()
					MyProject.Forms.frmFilmTransport.Text = "Trailer"
					Application.DoEvents()
					modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
					If modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteHoch()
					End If
					If modDeclares.SystemData.SMCI Then
						modSMCi.MagnetAusSMCi()
					End If
					num76 = 1S
					num79 = modMultiFly.GetSpeedFromSteps(num89, modDeclares.SystemData.filmspeed(CInt(num2)))
					num80 = 1
					num77 = 0
					num29 = 0
					modMultiFly.FahreMotor(num76, num89, num79, num80, num77, num29, modDeclares.SystemData.FResolution(CInt(num2)))
					While True
						num76 = 1S
						If Not modMultiFly.MotorIsRunning(num76) Then
							Exit For
						End If
						Application.DoEvents()
					End While
					flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
					modMultiFly.VNullpunkt(flag, num2)
					num3 = 0S
					If modDeclares.SystemData.SMCI Then
						modSMCi.MagnetAnSMCi()
					End If
					If modDeclares.SystemData.NeuerMagnet Then
						modMultiFly.MagnetPlatteRunter()
					End If
					MyProject.Forms.frmFilmTransport.Close()
					Application.DoEvents()

						num9 -= CDbl(modDeclares.SystemData.nachspann) / 100.0
						If Not modDeclares.CalcModus Then
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
						End If
						modDeclares.glbInsertFilmCanceled = False
						modMain.ShowErrorFile(num17)
						Dim text4 As String = Application.StartupPath + "\EXTLOGS\" + MyProject.Forms.frmFilming.lblFilmNr.Text + ".txt"
						If File.Exists(text4) Then
							Interaction.Shell("notepad.exe " + text4, AppWinStyle.MaximizedFocus, False, -1)
						End If
						MyProject.Forms.frmFilmEinlegen.ShowDialog()
						MyProject.Forms.frmFilmEinlegen.Dispose()
						If modDeclares.glbInsertFilmCanceled Then
							GoTo Block_290
						End If

					MyProject.Forms.frmGetFilmNo.txtFilmNo.Text = Conversions.ToString(num17 + 1)
					MyProject.Forms.frmGetFilmNo.ShowDialog()
					MyProject.Forms.frmGetFilmNo.Dispose()
					num17 = CInt(Math.Round(Conversion.Val(modDeclares.ffrmFilmPreview.txtFilmNr.Text)))
					modDeclares.Blip1Counter = 0
					modDeclares.Blip2Counter = 0
					modDeclares.Blip3Counter = 0
					modMain.ProtIndex = 1
					value2 = num17
					modExpose.ClearLog(value2)
					num17 = Conversions.ToInteger(value2)
					k = If(-If((modDeclares.WritePrivateProfileString("SYSTEM", "FILMNO" + Conversions.ToString(CInt(num2)), modDeclares.ffrmFilmPreview.txtFilmNr.Text, lpFileName) > False), 1, 0), 1, 0)
					num27 = CInt(Math.Round(CDbl(modDeclares.SystemData.vorspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
					MyProject.Forms.frmFilmTransport.Show()
					MyProject.Forms.frmFilmTransport.Text = "Leader"
					Application.DoEvents()
					If Not modDeclares.UseDebug Then
						modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
						If modDeclares.SystemData.NeuerMagnet Then
							modMultiFly.MagnetPlatteHoch()
						End If
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAusSMCi()
						End If
						num76 = 1S
						num29 = modMultiFly.GetSpeedFromSteps(num27, modDeclares.SystemData.filmspeed(CInt(num2)))
						num77 = 1
						num80 = 0
						num79 = 0
						modMultiFly.FahreMotor(num76, num27, num29, num77, num80, num79, modDeclares.SystemData.FResolution(CInt(num2)))
						While True
							num76 = 1S
							If Not modMultiFly.MotorIsRunning(num76) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAnSMCi()
						End If
						If modDeclares.SystemData.NeuerMagnet Then
							modMultiFly.MagnetPlatteRunter()
						End If
					End If
					MyProject.Forms.frmFilmTransport.Close()
					Application.DoEvents()
					text = modMain.GiveIni(lpFileName, "SYSTEM", "FILMLAENGE" + Conversions.ToString(CInt(num2)))
					num9 = Conversion.Val(modMain.KommazuPunkt(text)) - CDbl(modDeclares.SystemData.vorspann) / 100.0
					num10 = modDeclares.SystemData.BelegeProFilm(CInt(num2))
					If Not modDeclares.UseDebug Then
						If modDeclares.SystemData.CheckVakuum Then
							modDeclares.Outputs = modDeclares.Outputs Or 64
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num79 = 0
							text3 = modMultiFly.Comm_Read(num79, True)
							modDeclares.Sleep(modDeclares.SystemData.VacuumOnDelay)
							If modDeclares.SystemData.SMCI Then
								modSMCi.VakuumAnSMCi()
							End If
						End If
						If modDeclares.SystemData.SMCI Then
							modSMCi.MagnetAnSMCi()
						End If
						modDeclares.Outputs = modDeclares.Outputs Or 32
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num79 = 0
						text3 = modMultiFly.Comm_Read(num79, True)
						If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn))) Then
							If modDeclares.SystemData.SMCI Then
								modSMCi.VakuumAusSMCi()
								modSMCi.MagnetAusSMCi()
							End If
							modDeclares.Outputs = 0
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num79 = 0
							text3 = modMultiFly.Comm_Read(num79, True)
							text = "TXT_ERR_VACUUM_ON"
							text2 = modMain.GetText(text)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Vakuum konnte nicht angeschaltet werden!"
							End If
							num76 = 0S
							text = "file-converter"
							modMain.msgbox2(text2, num76, text)
						Else
							modDeclares.Outputs = modDeclares.Outputs Or 8
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num79 = 0
							text3 = modMultiFly.Comm_Read(num79, True)
						End If
					End If
					num17 += 1
					value2 = num17
					modExpose.ClearLog(value2)
					num17 = Conversions.ToInteger(value2)
					MyProject.Forms.frmFilming.lblFilmNr.Text = Conversions.ToString(num17)
					FileSystem.FileOpen(CInt(num25), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
					FileSystem.PrintLine(CInt(num25), New Object() { num17 })
					FileSystem.FileClose(New Integer() { CInt(num25) })
					modDeclares.ffrmFilmPreview.txtFilmNr.Text = Conversions.ToString(num17)
					num8 = 0

						If Not modDeclares.CalcModus Then
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BENUTZTERTEILFILM" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
							k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(num2)), Conversion.Str(num8), lpFileName) > False), 1, 0)), 1, 0)
						End If
						If modDeclares.SystemData.FesteBelegzahlProFilm Then
							modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = "0"
						Else
							modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						End If
						If Not(modDeclares.SystemData.UseStartFrame Or modExpose.AnzGesamtStartSymbole > 0) Then
							GoTo IL_557A
						End If
						flag5 = True
						If modDeclares.SystemData.UseStartFrame Then
							num32 = 0
							GoTo IL_557A
						End If
						If modExpose.AnzGesamtStartSymbole > 0 Then
							num32 = 0
							GoTo IL_557A
						End If
						flag5 = False
						GoTo IL_557A
						IL_49E8:
						modDeclares.Outputs = 0
						text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						modMultiFly.Comm_Send(text3)
						num79 = 0
						text3 = modMultiFly.Comm_Read(num79, True)
						GoTo IL_4A1E
						Block_251:
						Dim extendedVacuumHandling As Boolean = modDeclares.SystemData.ExtendedVacuumHandling
						Dim frmVacuum As frmVacuum = New frmVacuum()
						frmVacuum.cmdContinue.Visible = False
						frmVacuum.cmdEmpty.Visible = False
						If modDeclares.SystemData.SMCI Then
							modSMCi.VakuumAusSMCi()
						Else
							modDeclares.Outputs = modDeclares.Outputs And 191
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num29 = 0
							text3 = modMultiFly.Comm_Read(num29, True)
						End If
						frmVacuum.ShowDialog()
						frmVacuum.Dispose()
						GoTo IL_4A1E
						IL_3F13:
						MyProject.Forms.frmImage.NoPaint = False

					If Not(flag5 Or modExpose.ExposeEndSymbols) Then
						num40 = CInt(modPaint.RepaintImage(CInt(num2)))
					Else
						MyProject.Forms.frmImage.ImagXpress1.Image = modMain.glImage
					End If
					MyProject.Forms.frmImage.NoPaint = True
					Try
						Dim width As Integer = MyProject.Forms.frmImage.ImagXpress1.Image.Width
						Dim width2 As Integer = modMain.glImage.Width
					Catch ex As Exception
						Interaction.MsgBox(ex.ToString(), MsgBoxStyle.OkOnly, Nothing)
					End Try
					If Information.IsNothing(modMain.glImage) Then
						MyProject.Forms.frmImage.NoPaint = True
					End If
					MyProject.Forms.frmImage.Show()
					If modDeclares.SystemData.AnnoStyle = 5S Then
						Dim num106 As Integer
						If i >= 0 Then
							If modDeclares.Images(i).IsPDF Then
								num106 = modDeclares.Painted_Image_Width
							Else
								num106 = CInt(MyProject.Forms.frmImageXpress.IWidth)
							End If
						Else
							num106 = CInt(MyProject.Forms.frmImageXpress.IWidth)
						End If
						modDeclares.film_faktor = modDeclares.film_faktor * CDbl(num106) / CDbl(modDeclares.Painted_Image_Width)
						Dim text8 As String = ""
						Dim num28 As Integer = CInt(modDeclares.SystemData.AnnoLen)
						k = 1
						While k <= num28
							text8 += "0"
							k += 1
						End While
						If i < 0 Then
							modDeclares.SystemData.Anno = ""
						Else
							modDeclares.SystemData.Anno = String.Concat(New String() { Support.Format(modDeclares.Images(i).count + 1, text8, FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), " | ", Support.Format(modDeclares.film_faktor, "##.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "x | ", modMain.RemoveExtensionAndPath(modDeclares.Images(i).DokumentName), " " })
						End If
						If modDeclares.SystemData.ShowDocSize Then
							modDeclares.SystemData.Anno = modDeclares.SystemData.Anno + "(" + text13 + ")"
						End If
						Dim useAnno2 As Boolean = modDeclares.SystemData.UseAnno
					End If
					Dim flag19 As Boolean = flag5 Or modExpose.ExposeEndSymbols
					MyProject.Forms.frmAnnoWin.Refresh()
					If modDeclares.SystemData.StepsImageToImage Or modDeclares.SystemData.StepsImageToImage Then
						' The following expression was wrapped in a unchecked-expression
						num40 = CInt(Math.Round(CDbl(num40) * modDeclares.SystemData.schrittepropixel(CInt(num2))))
						num40 += CInt(Math.Round(modDeclares.SystemData.schrittweite * modDeclares.SystemData.schrittepromm(CInt(num2))))
					End If
					If modDeclares.SystemData.EnableInfoWindow Then
						MyProject.Forms.frmInfoWin.Refresh()
					End If
					Application.DoEvents()
					If modDeclares.UseDebug Then
						modDeclares.Sleep(modDeclares.SystemData.SIMULATIONDELAY)
					End If
					If flag7 Then
						Dim nNumber As Short = 72S
						If modDeclares.SystemData.UseFrameNo Then
							Dim num107 As Double = 56.7 / CDbl(Support.TwipsPerPixelX())
							text = "Courier New"
							Dim logfont As modDeclares.LOGFONT
							modMain.WriteToArray(logfont.lfFaceName, text)
							logfont.lfWeight = 900
							logfont.lfEscapement = modDeclares.SystemData.Ausrichtung * 10
							logfont.lfHeight = 0 - modDeclares.MulDiv(CInt(nNumber), CInt(modDeclares.MonDPI), 72)
							Dim num108 As Integer = CInt(modDeclares.CreateFontIndirect(logfont))
							Dim num109 As Integer = CInt(modDeclares.SelectObject(CLng(MyProject.Forms.frmImage.CreateGraphics().GetHdc()), CLng(num108)))
							text2 = Support.Format(num8, "00000000", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							k = modDeclares.TextOut(CInt(MyProject.Forms.frmImage.CreateGraphics().GetHdc()), 125, 400, text2, Strings.Len(text2))

								modDeclares.SelectObject(CLng(MyProject.Forms.frmImage.CreateGraphics().GetHdc()), CLng(num109))
								modDeclares.DeleteObject(CLng(num108))

						End If
					End If
					If Not modDeclares.CalcModus AndAlso modDeclares.SystemData.PRECACHEIMAGES Then
						modDeclares.Sleep(modDeclares.SystemData.WaitAfterDraw)
					End If
					modDeclares.Sleep(modDeclares.SystemData.WaitAfterDraw)
					If Not modDeclares.SystemData.PRECACHEIMAGES Then
						Dim calcModus As Boolean = modDeclares.CalcModus
					End If
					Application.DoEvents()
					GoTo IL_4347
				End If
				GoTo IL_8F29
			End While
			MyProject.Forms.frmImage.Close()
			MyProject.Forms.frmAnnoWin.Close()
			MyProject.Forms.frmBlipWin.Close()
			If Not Information.IsNothing(modMain.glImage) Then
				modMain.glImage.Dispose()
			End If
			If Not Information.IsNothing(modMain.gl_im) Then
				modMain.gl_im.Close()
			End If
			Application.DoEvents()
			flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
			modMultiFly.VNullpunkt(flag, num2)
			num3 = 0S
			text = "TXT_TRAILER"
			text3 = modMain.GetText(text)
			If Operators.CompareString(text3, "", False) = 0 Then
				text3 = "Soll ein Nachspann abgefahren werden?"
			End If
			num19 = 4S
			text = "file-converter"
			If modMain.msgbox2(text3, num19, text) <> 6S Then
				GoTo IL_8F29
			End If
			modDeclares.Outputs = 0
			text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
				modMultiFly.Comm_Send(text3)
				Dim num29 As Integer = 0
				text3 = modMultiFly.Comm_Read(num29, True)
			End If
			If modDeclares.SystemData.SMCI Then
				modSMCi.VakuumAusSMCi()
			End If
			If modDeclares.SystemData.SMCI Then
				modSMCi.MagnetAusSMCi()
			End If
			If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOff(modDeclares.SystemData.VacuumOff))) Then
				If modDeclares.SystemData.SMCI Then
					modSMCi.VakuumAusSMCi()
					modSMCi.MagnetAusSMCi()
				End If
				modDeclares.Outputs = 0
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				Dim num29 As Integer = 0
				text3 = modMultiFly.Comm_Read(num29, True)
				text = "TXT_ERR_VACUUM_OFF"
				text2 = modMain.GetText(text)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "Vakuum konnte nicht ausgeschaltet werden!"
				End If
				num19 = 0S
				text = "file-converter"
				modMain.msgbox2(text2, num19, text)
			ElseIf Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
				modDeclares.Outputs = modDeclares.Outputs And -9
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				Dim num29 As Integer = 0
				text3 = modMultiFly.Comm_Read(num29, True)
			End If
			num89 = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
			MyProject.Forms.frmFilmTransport.Show()
			MyProject.Forms.frmFilmTransport.Text = "Trailer"
			Application.DoEvents()
			If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
				modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
				If modDeclares.SystemData.NeuerMagnet Then
					modMultiFly.MagnetPlatteHoch()
				End If
				If modDeclares.SystemData.SMCI Then
					modSMCi.MagnetAusSMCi()
				End If
				num19 = 1S
				Dim num29 As Integer = modMultiFly.GetSpeedFromSteps(num89, modDeclares.SystemData.filmspeed(CInt(num2)))
				Dim num30 As Integer = 1
				Dim num28 As Integer = 0
				num23 = 0
				modMultiFly.FahreMotor(num19, num89, num29, num30, num28, num23, modDeclares.SystemData.FResolution(CInt(num2)))
				While True
					num19 = 1S
					If Not modMultiFly.MotorIsRunning(num19) Then
						Exit For
					End If
					Application.DoEvents()
				End While
				flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
				modMultiFly.VNullpunkt(flag, num2)
				num3 = 0S
				Dim smci7 As Boolean = modDeclares.SystemData.SMCI
				If modDeclares.SystemData.NeuerMagnet Then
					modMultiFly.MagnetPlatteRunter()
				End If
			End If
			MyProject.Forms.frmFilmTransport.Close()
			Application.DoEvents()
			num9 -= CDbl(modDeclares.SystemData.nachspann) / 100.0
			If Not modDeclares.CalcModus Then
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
				GoTo IL_8F29
			End If
			GoTo IL_8F29
			Block_155:
			value = "Temporary Image of JPG Processor not found!" & vbCrLf + str6
			num60 = 0S
			text = "file-converter"
			modMain.msgbox2(value, num60, text)
			GoTo IL_8F29
			Block_273:
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			Return
			Block_276:
			modDeclares.Outputs = 0
			text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text3)
			num79 = 0
			text3 = modMultiFly.Comm_Read(num79, True)
			modSMCi.LEDAnSMCi()
			GoTo IL_8F29
			Block_290:
			If Not modDeclares.UseDebug Then
				modDeclares.Outputs = 0
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				Dim num29 As Integer = 0
				text3 = modMultiFly.Comm_Read(num29, True)
			End If
			text = "TXT_EXPOSE_CANCELLED"
			text2 = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Verfilmen wurde abgebrochen!"
				text2 = "Exposing stopped!"
			End If
			If Not modDeclares.CalcModus Then
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
			End If
			num76 = 0S
			text = "file-converter"
			modMain.msgbox2(text2, num76, text)
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			Return
			Block_318:
			text = "TXT_MOTOR_PROBLEM_EXPOSURE_STOP"
			text2 = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Ein Problem beim Fahren des Verschlussmotors ist aufgetreten! Bitte Motorparameter entsprechend ueberpruefen!"
			End If
			modDeclares.Outputs = 0
			text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text3)
			num80 = 0
			text3 = modMultiFly.Comm_Read(num80, True)
			If Not modDeclares.CalcModus Then
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
			End If
			num76 = 0S
			text = "file-converter"
			modMain.msgbox2(text2, num76, text)
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			Return
			Block_356:
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			Return
			Block_492:
			modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			If Not modDeclares.CalcModus Then
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
			End If
			If Not modDeclares.UseDebug Then
				modDeclares.Outputs = 0
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				If Not modDeclares.UseDebug Then
					modMultiFly.Comm_Send(text3)
					Dim num78 As Integer = 0
					text3 = modMultiFly.Comm_Read(num78, True)
				End If
			End If
			value = "TXT_EXPOSE_CANCELLED"
			text2 = modMain.GetText(value)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Verfilmen wurde abgebrochen!"
				text2 = "Exposing stopped!"
			End If
			num76 = 0S
			value = "file-converter"
			modMain.msgbox2(text2, num76, value)
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			If flag2 Then
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(num2)), "1", lpFileName) > False), 1, 0)), 1, 0)
				modDeclares.ffrmFilmPreview.cmdFortsetzung.Tag = "1"
				Dim cmdFortsetzung3 As ButtonBase = modDeclares.ffrmFilmPreview.cmdFortsetzung
				value = "TXT_ROLL_IS_CONT"
				cmdFortsetzung3.Text = modMain.GetText(value)
				If Operators.CompareString(modDeclares.ffrmFilmPreview.cmdFortsetzung.Text, "", False) = 0 Then
					MyProject.Forms.frmFilmPreview.cmdFortsetzung.Text = "Rolle ist eine Fortsetzung"
					Return
				End If
				Return
			Else
				k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(num2)), "0", lpFileName) > False), 1, 0)), 1, 0)
				modDeclares.ffrmFilmPreview.cmdFortsetzung.Tag = "0"
				Dim cmdFortsetzung4 As ButtonBase = modDeclares.ffrmFilmPreview.cmdFortsetzung
				value = "TXT_ROLL_IS_NOT_CONT"
				cmdFortsetzung4.Text = modMain.GetText(value)
				If Operators.CompareString(modDeclares.ffrmFilmPreview.cmdFortsetzung.Text, "", False) = 0 Then
					modDeclares.ffrmFilmPreview.cmdFortsetzung.Text = "Rolle ist KEINE Fortsetzung"
					Return
				End If
				Return
			End If
			Block_550:
			text = "TXT_FILMENDE1"
			text2 = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) <> 0 Then
				Dim str10 As String = text2
				Dim str11 As String = vbCr
				text = "TXT_FILMENDE2"
				text2 = str10 + str11 + modMain.GetText(text)
			Else
				text2 = "Filmende erkannt!" & vbCr & "Bitte nach Aufforderung einen neuen Film einlegen!"
			End If
			num76 = 0S
			text = "file-converter"
			modMain.msgbox2(text2, num76, text)
			modDeclares.ffrmFilmPreview.txtFilmNr.Text = Conversions.ToString(num17)
			modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
			k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(0), lpFileName) > False), 1, 0)), 1, 0)
			modDeclares.Outputs = 0
			text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
			modMultiFly.Comm_Send(text3)
			num77 = 0
			text3 = modMultiFly.Comm_Read(num77, True)
			text = "TXT_EXPOSE_CANCELLED"
			text2 = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Verfilmen wurde abgebrochen!"
				text2 = "Exposing stopped!"
			End If
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			Return
			IL_8F29:
			If modDeclares.SystemData.JPEGProcessor Then
				MyProject.Forms.frmFilming.lstInfo.Items.Add("Kill Process")
				MyProject.Forms.frmFilming.lstInfo.Refresh()
				text = "taskkill /F /T /IM jpegaufbereiter.exe"
				modMonitorTest.ExecCmd(text)
			End If
			MyProject.Forms.frmFilming.lstInfo.Items.Add("LEDAnSMCi")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			modSMCi.LEDAnSMCi()
			MyProject.Forms.frmImage.Close()
			MyProject.Forms.frmFilming.lstInfo.Items.Add("ShowErrorFile")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			modMain.ShowErrorFile(num17)
			MyProject.Forms.frmFilming.lstInfo.Items.Add("Clear PDF")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			MyProject.Forms.frmFilming.lstInfo.Items.Add("Vacuum Off")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
				If modDeclares.SystemData.SMCI Then
					modSMCi.VakuumAusSMCi()
					modSMCi.MagnetAusSMCi()
				End If
				modDeclares.Outputs = 0
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text3)
				num77 = 0
				text3 = modMultiFly.Comm_Read(num77, True)
			End If
			MyProject.Forms.frmFilming.lstInfo.Items.Add("Trailer")
			MyProject.Forms.frmFilming.lstInfo.Refresh()
			modDeclares.Sleep(500)
			If i > modDeclares.imagecount And Not modDeclares.CalcModus Then
				text = "TXT_TRAILER"
				text3 = modMain.GetText(text)
				If Operators.CompareString(text3, "", False) = 0 Then
					text3 = "Generate a Trailer?"
				End If
				num76 = 4S
				text = "file-converter"
				If modMain.msgbox2(text3, num76, text) = 6S Then
					text = Support.Format(num17, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					modExpose.AddTrailer(text)
					Dim num89 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
					MyProject.Forms.frmFilmTransport.Show()
					MyProject.Forms.frmFilmTransport.Text = "Trailer"
					Application.DoEvents()
					If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
						modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
						If modDeclares.SystemData.NeuerMagnet Then
							modDeclares.Outputs = modDeclares.Outputs Or 32
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num77 = 0
							text3 = modMultiFly.Comm_Read(num77, True)
							modDeclares.Sleep(modDeclares.SystemData.MagnetDelay)
						End If
						num76 = 1S
						num77 = modMultiFly.GetSpeedFromSteps(num89, modDeclares.SystemData.filmspeed(CInt(num2)))
						Dim num78 As Integer = 1
						Dim num110 As Integer = 0
						Dim num111 As Integer = 0
						modMultiFly.FahreMotor(num76, num89, num77, num78, num110, num111, modDeclares.SystemData.FResolution(CInt(num2)))
						While True
							num76 = 1S
							If Not modMultiFly.MotorIsRunning(num76) Then
								Exit For
							End If
							Application.DoEvents()
						End While
						flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
						modMultiFly.VNullpunkt(flag, num2)
						num3 = 0S
						If modDeclares.SystemData.NeuerMagnet Then
							modDeclares.Outputs = modDeclares.Outputs And -33
							text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
							modMultiFly.Comm_Send(text3)
							num111 = 0
							text3 = modMultiFly.Comm_Read(num111, True)
						End If
					End If
					MyProject.Forms.frmFilmTransport.Close()
					Application.DoEvents()
					num9 -= CDbl(modDeclares.SystemData.nachspann) / 100.0
					If Not modDeclares.CalcModus Then
						k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Conversion.Str(num9), lpFileName) > False), 1, 0)), 1, 0)
						k = If((-If((modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(num2)), Conversion.Str(num10), lpFileName) > False), 1, 0)), 1, 0)
					End If
					modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					If modDeclares.CalcModus Then
						MyProject.Forms.frmFilming.lblRestframes.Text = Support.Format(1000000.0 - num9, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					Else
						Dim lblRestframes2 As Label = MyProject.Forms.frmFilming.lblRestframes
						Dim value5 As Object = 0
						Dim value2 As Object = num9
						Dim obj2 As Object = modMain.fmax(value5, value2)
						num9 = Conversions.ToDouble(value2)
						lblRestframes2.Text = Support.Format(RuntimeHelpers.GetObjectValue(obj2), "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					End If
				End If
			End If
			If modDeclares.SystemData.CheckVakuum AndAlso modDeclares.SystemData.SMCI Then
				modSMCi.MagnetAusSMCi()
				modSMCi.VakuumAusSMCi()
			End If
			flag = (modDeclares.UseDebug Or modDeclares.CalcModus)
			modMultiFly.VNullpunkt(flag, num2)
			num3 = 0S
			modDeclares.ffrmFilmPreview.txtRestAufnahmen.Text = Support.Format(num9, "0#.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			MyProject.Forms.frmFilming.Close()
			modDeclares.ffrmFilmPreview.cmdCancel.Enabled = True
			modDeclares.ffrmFilmPreview.cmdRefilm.Tag = ""
			If Not modDeclares.SystemData.SMCI Then
				modDeclares.Outputs = modDeclares.Outputs Or 8
				text3 = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				If Not(modDeclares.UseDebug Or modDeclares.CalcModus) Then
					modMultiFly.Comm_Send(text3)
					Dim num111 As Integer = 0
					text3 = modMultiFly.Comm_Read(num111, True)
				End If
			End If
			MyProject.Forms.frmSMAMain.Activate()
			modMain.LastLoadedPDF = ""
			modMain.DeleteTempFiles(modDeclares.SystemData.PDFKONVERTERTEMP)
		End Sub