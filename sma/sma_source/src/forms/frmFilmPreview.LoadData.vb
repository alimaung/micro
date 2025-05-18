Private Sub LoadData(ByRef Name_Renamed As String)
	Dim num4 As Integer
	Dim num12 As Integer
	Dim obj As Object
	Try
		IL_00:
		Dim num As Integer = 1
		Dim text As String = Name_Renamed
		IL_05:
		num = 2
		If Operators.CompareString(Support.Format(Strings.Right(Name_Renamed, 4), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), ".TPL", False) = 0 Then
			GoTo IL_36
		End If
		IL_28:
		num = 3
		text += ".TPL"
		IL_36:
		num = 4
		text = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + text
		IL_53:
		num = 5
		Me.chkDuplex.CheckState = CheckState.Unchecked
		IL_61:
		num = 6
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "DUPLEX"), "1", False) <> 0 Then
			GoTo IL_8F
		End If
		IL_81:
		num = 7
		Me.chkDuplex.CheckState = CheckState.Checked
		IL_8F:
		num = 8
		Me.chkSimDupFilenames.Checked = False
		IL_9D:
		num = 9
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "SimDupFilenames"), "1", False) <> 0 Then
			GoTo IL_CD
		End If
		IL_BE:
		num = 10
		Me.chkSimDupFilenames.Checked = True
		IL_CD:
		num = 11
		Me.chkTwoLines.Checked = False
		IL_DC:
		num = 12
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "TwoLines"), "1", False) <> 0 Then
			GoTo IL_10C
		End If
		IL_FD:
		num = 13
		Me.chkTwoLines.Checked = True
		IL_10C:
		num = 14
		Dim text2 As String = modMain.GiveIni(text, "TEMPLATE", "AddRollStartFrameSteps")
		IL_122:
		num = 15
		If Not Versioned.IsNumeric(text2) Then
			GoTo IL_140
		End If
		IL_12E:
		num = 16
		Me.txtAddRollStartFrameSteps.Text = text2
		GoTo IL_153
		IL_140:
		num = 18
		Me.txtAddRollStartFrameSteps.Text = "0"
		IL_153:
		num = 19
		Me.chkLateStart.CheckState = CheckState.Unchecked
		IL_162:
		num = 20
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "LateStart"), "1", False) <> 0 Then
			GoTo IL_192
		End If
		IL_183:
		num = 21
		Me.chkLateStart.CheckState = CheckState.Checked
		IL_192:
		num = 22
		Me.txtMaxDuplex.Text = modMain.GiveIni(text, "TEMPLATE", "MaxDUPLEX")
		IL_1B1:
		num = 23
		Me.txtDuplexDist.Text = modMain.GiveIni(text, "TEMPLATE", "DUPLEXDISTANCE")
		IL_1D0:
		num = 24
		Me.chkSmallLeft.CheckState = CheckState.Unchecked
		IL_1DF:
		num = 25
		Me.chkBigLeft.CheckState = CheckState.Unchecked
		IL_1EE:
		num = 26
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "SMALLLEFT"), "1", False) <> 0 Then
			GoTo IL_21E
		End If
		IL_20F:
		num = 27
		Me.chkSmallLeft.CheckState = CheckState.Checked
		IL_21E:
		num = 28
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "BIGLEFT"), "1", False) <> 0 Then
			GoTo IL_24E
		End If
		IL_23F:
		num = 29
		Me.chkBigLeft.CheckState = CheckState.Checked
		IL_24E:
		num = 30
		Me.chkJPEG.CheckState = CheckState.Unchecked
		IL_25D:
		num = 31
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "JPEGProcessor"), "1", False) <> 0 Then
			GoTo IL_28D
		End If
		IL_27E:
		num = 32
		Me.chkJPEG.CheckState = CheckState.Checked
		IL_28D:
		num = 33
		Me.optLagerichtig.CheckState = CheckState.Unchecked
		IL_29C:
		num = 34
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "LAGERICHTIG"), "1", False) <> 0 Then
			GoTo IL_2CC
		End If
		IL_2BD:
		num = 35
		Me.optLagerichtig.CheckState = CheckState.Checked
		IL_2CC:
		num = 36
		Me.chkA4LSDrehen.CheckState = CheckState.Unchecked
		IL_2DB:
		num = 37
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "A4LSDREHEN"), "1", False) <> 0 Then
			GoTo IL_30B
		End If
		IL_2FC:
		num = 38
		Me.chkA4LSDrehen.CheckState = CheckState.Checked
		IL_30B:
		num = 39
		Me.optOben.Checked = False
		IL_31A:
		num = 40
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "optOben"), "1", False) <> 0 Then
			GoTo IL_34A
		End If
		IL_33B:
		num = 41
		Me.optOben.Checked = True
		IL_34A:
		num = 42
		Me.optUnten.Checked = False
		IL_359:
		num = 43
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "optUnten"), "1", False) <> 0 Then
			GoTo IL_389
		End If
		IL_37A:
		num = 44
		Me.optUnten.Checked = True
		IL_389:
		num = 45
		Me.optCenter.Checked = False
		IL_398:
		num = 46
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "optCenter"), "1", False) <> 0 Then
			GoTo IL_3C8
		End If
		IL_3B9:
		num = 47
		Me.optCenter.Checked = True
		IL_3C8:
		num = 48
		Me.chkA3PortraitDrehen.CheckState = CheckState.Unchecked
		IL_3D7:
		num = 49
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "A3PORTRAITDREHEN"), "1", False) <> 0 Then
			GoTo IL_407
		End If
		IL_3F8:
		num = 50
		Me.chkA3PortraitDrehen.CheckState = CheckState.Checked
		IL_407:
		num = 51
		Me.optRA3.Checked = False
		IL_416:
		num = 52
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "RA3"), "1", False) <> 0 Then
			GoTo IL_446
		End If
		IL_437:
		num = 53
		Me.optRA3.Checked = True
		IL_446:
		num = 54
		Me.optRA4.Checked = False
		IL_455:
		num = 55
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "RA4"), "1", False) <> 0 Then
			GoTo IL_485
		End If
		IL_476:
		num = 56
		Me.optRA4.Checked = True
		IL_485:
		num = 57
		Me.optLA3.Checked = False
		IL_494:
		num = 58
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "LA3"), "1", False) <> 0 Then
			GoTo IL_4C4
		End If
		IL_4B5:
		num = 59
		Me.optLA3.Checked = True
		IL_4C4:
		num = 60
		Me.optLA4.Checked = False
		IL_4D3:
		num = 61
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "LA4"), "1", False) <> 0 Then
			GoTo IL_503
		End If
		IL_4F4:
		num = 62
		Me.optLA4.Checked = True
		IL_503:
		num = 63
		text2 = modMain.GiveIni(text, "TEMPLATE", "FesteBelegzahlProFilm")
		IL_519:
		num = 64
		If Operators.CompareString(text2, "1", False) <> 0 Then
			GoTo IL_54A
		End If
		IL_52B:
		num = 65
		Me.chkFesteBelegzahl.CheckState = CheckState.Checked
		IL_53A:
		num = 66
		modDeclares.SystemData.FesteBelegzahlProFilm = True
		GoTo IL_567
		IL_54A:
		num = 68
		Me.chkFesteBelegzahl.CheckState = CheckState.Unchecked
		IL_559:
		num = 69
		modDeclares.SystemData.FesteBelegzahlProFilm = False
		IL_567:
		num = 70
		Me.chkAddRollFrame.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "EnableAddRollFrame"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_5AA:
		num = 71
		Me.chkAddRollFrameInput.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AddRollFrameInput"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_5ED:
		num = 72
		Me.txtAddRollFrameSize.Text = modMain.GiveIni(text, "TEMPLATE", "AddRollFrameFontSize")
		IL_60C:
		num = 73
		Me.txtAddRollFrameLen.Text = modMain.GiveIni(text, "TEMPLATE", "AddRollFrameLen")
		IL_62B:
		num = 74
		Dim num2 As Short = 1S
		Do
			IL_631:
			num = 75
			num2 += 1S
		Loop While num2 <= 4S
		IL_640:
		num = 76
		Me.txtAddStepLevel2.Text = modMain.GiveIni(text, "TEMPLATE", "AddStepLevel2")
		IL_65F:
		num = 77
		Me.txtAddStepLevel3.Text = modMain.GiveIni(text, "TEMPLATE", "AddStepLevel3")
		IL_67E:
		num = 78
		Me.txtRollNoPrefix.Text = modMain.GiveIni(text, "TEMPLATE", "RollNoPrefix")
		IL_69D:
		num = 79
		Me.txtRollNoPostfix.Text = modMain.GiveIni(text, "TEMPLATE", "RollNoPostfix")
		IL_6BC:
		num = 80
		Me.txtRollNoSize.Text = modMain.GiveIni(text, "TEMPLATE", "RollNoSize")
		IL_6DB:
		num = 81
		Me.txtRollNoLen.Text = modMain.GiveIni(text, "TEMPLATE", "RollNoLen")
		IL_6FA:
		num = 82
		Me.chkBaende.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "BaendeVollstaendigBelichten"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_73D:
		num = 83
		Me.chkFramesWiederholen.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "FramesWiederholen"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_780:
		num = 84
		Me.txtFramesWiederholen.Text = modMain.GiveIni(text, "TEMPLATE", "FramesWiederholenAnzahl")
		IL_79F:
		num = 85
		Me.chkZusatzStartSymbole.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "ZusatzStartSymbole"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_7E2:
		num = 86
		Me.lblPfadStartSymbole.Text = modMain.GiveIni(text, "TEMPLATE", "PfadZusatzStartSymbole")
		IL_801:
		num = 87
		Me.chkRollewirdfortgesetzt.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "FortsetzungsSymbole1"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_844:
		num = 88
		Me.lblPfadFortsetzungsSymbole1.Text = modMain.GiveIni(text, "TEMPLATE", "PfadFortsetzungsSymbole1")
		IL_863:
		num = 89
		Dim text3 As String
		Dim num3 As Integer = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "TEMPLATE", "FortsetzungsLevel")) - 1.0))
		IL_898:
		num = 90
		If num3 <> -1 Then
			GoTo IL_8A6
		End If
		IL_8A0:
		num = 91
		num3 = 0
		IL_8A6:
		num = 92
		Me.cmbFortsetzungsLevel.SelectedIndex = num3
		IL_8B6:
		num = 93
		Me.chkRolleistFortsetzung.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "FortsetzungsSymbole2"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_8F9:
		num = 94
		Me.lblPfadFortsetzungsSymbole2.Text = modMain.GiveIni(text, "TEMPLATE", "PfadFortsetzungsSymbole2")
		IL_918:
		num = 95
		Me.chkZusatzEndSymbole.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "ZusatzEndSymbole"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_95B:
		num = 96
		Me.lblPfadEndSymbole.Text = modMain.GiveIni(text, "TEMPLATE", "PfadZusatzEndSymbole")
		IL_97A:
		num = 97
		Me.chkNoSpecialSmybolesWhenContinuation.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "NoSpecialSmybolesWhenContinuation"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_9BD:
		num = 98
		Me.cmbPDFReso.Text = modMain.GiveIni(text, "TEMPLATE", "PDFRESO")
		IL_9DC:
		num = 99
		Me.chkBlip.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "BLIP"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_A1F:
		num = 100
		Me.chkStartBlipAtOne.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "StartBlipAtOne"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_A62:
		num = 101
		Me.chkAutoAlign.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AUTOALIGN"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_AA5:
		num = 102
		Me.chkAutoAlign180.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AutoAlign180"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_AE8:
		num = 103
		Me.chkRollEndFrame.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "RollEndFrame"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_B2B:
		num = 104
		text3 = modMain.GiveIni(text, "TEMPLATE", "AUTOORIENTATION")
		IL_B41:
		num = 105
		If Operators.CompareString(text3, "90", False) <> 0 Then
			GoTo IL_B64
		End If
		IL_B53:
		num = 106
		Me.opt90.Checked = True
		GoTo IL_B73
		IL_B64:
		num = 108
		Me.opt270.Checked = True
		IL_B73:
		num = 109
		text3 = modMain.GiveIni(text, "TEMPLATE", "ROTATION")
		IL_B89:
		num = 110
		If Operators.CompareString(text3, "90", False) <> 0 Then
			GoTo IL_BAA
		End If
		IL_B9B:
		num = 111
		Me.optFest90.Checked = True
		IL_BAA:
		num = 112
		If Operators.CompareString(text3, "180", False) <> 0 Then
			GoTo IL_BCB
		End If
		IL_BBC:
		num = 113
		Me.optFest180.Checked = True
		IL_BCB:
		num = 114
		If Operators.CompareString(text3, "270", False) <> 0 Then
			GoTo IL_BEC
		End If
		IL_BDD:
		num = 115
		Me.optFest270.Checked = True
		IL_BEC:
		num = 116
		If Operators.CompareString(text3, "0", False) <> 0 Then
			GoTo IL_C0D
		End If
		IL_BFE:
		num = 117
		Me.optFest0.Checked = True
		IL_C0D:
		num = 118
		Me.chkAnnotation.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "ANNOTATION"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_C50:
		num = 119
		Me.chkIgnoreChars.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "IgnoreChars"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_C93:
		num = 120
		Me.txtIgnoreCharsCount.Text = modMain.GiveIni(text, "TEMPLATE", "IgnoreCharsCount")
		IL_CB2:
		num = 121
		Me.chkTrailerInfoFrames.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "TrailerInfoFrames"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_CF5:
		num = 122
		Me.chkStartFrame.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "STARTFRAME"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_D38:
		num = 123
		Me.chkUseIndex.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "UseIndex"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_D7B:
		num = 124
		Me.chkShowSize.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "ShowSize"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_DBE:
		num = 125
		Me.cmbPapierGroesse.SelectedIndex = -1
		IL_DCD:
		num = 126
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "Papiergroesseformat"), "", False) = 0 Then
			GoTo IL_E18
		End If
		IL_DEE:
		num = 127
		Me.cmbPapierGroesse.SelectedIndex = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "Papiergroesseformat"))))
		IL_E18:
		num = 128
		Me.chkSeparateFrame.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "SEPARATIONFRAME"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_E5E:
		num = 129
		Me.chkInvers.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "INVERS"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_EA4:
		num = 130
		Me.chkFrame.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "USEFRAME"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_EEA:
		num = 131
		Me.radWhiteFrame.Checked = False
		IL_EFC:
		num = 132
		Me.radBlackFrame.Checked = False
		IL_F0E:
		num = 133
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "optWeisserRahmen_0"), "1", False) <> 0 Then
			GoTo IL_F44
		End If
		IL_F32:
		num = 134
		Me.radWhiteFrame.Checked = True
		IL_F44:
		num = 135
		If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "optWeisserRahmen_1"), "1", False) <> 0 Then
			GoTo IL_F7A
		End If
		IL_F68:
		num = 136
		Me.radBlackFrame.Checked = True
		IL_F7A:
		num = 137
		Me.txtFrameWidth.Text = modMain.GiveIni(text, "TEMPLATE", "txtRahmendicke")
		IL_F9C:
		num = 138
		Me.optNebenBlip.Checked = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "POSITION"), "1", False) = 0, True, False))
		IL_FE2:
		num = 139
		Me.optUeberBlip.Checked = Not Me.optNebenBlip.Checked
		IL_1001:
		num = 140
		Me.chkUseFrameNo.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "UseFrameNo"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_1047:
		num = 141
		text3 = modMain.GiveIni(text, "TEMPLATE", "FORMAT")
		IL_1060:
		num = 142
		If Operators.CompareString(text3, "0", False) <> 0 Then
			GoTo IL_1087
		End If
		IL_1075:
		num = 143
		Me.optNamen.Checked = True
		IL_1087:
		num = 144
		If Operators.CompareString(text3, "1", False) <> 0 Then
			GoTo IL_10AE
		End If
		IL_109C:
		num = 145
		Me.optNummer.Checked = True
		IL_10AE:
		num = 146
		If Operators.CompareString(text3, "3", False) <> 0 Then
			GoTo IL_10D5
		End If
		IL_10C3:
		num = 147
		Me.optMulti.Checked = True
		IL_10D5:
		num = 148
		If Operators.CompareString(text3, "4", False) <> 0 Then
			GoTo IL_10FC
		End If
		IL_10EA:
		num = 149
		Me.optNummer.Checked = True
		IL_10FC:
		num = 150
		If Operators.CompareString(text3, "5", False) <> 0 Then
			GoTo IL_1123
		End If
		IL_1111:
		num = 151
		Me.optDreiTeilig.Checked = True
		IL_1123:
		num = 152
		If Operators.CompareString(text3, "6", False) <> 0 Then
			GoTo IL_116C
		End If
		IL_1138:
		num = 153
		Me.optBlipAnno.Checked = True
		IL_114A:
		num = 154
		Me.txtAnnoBlipLen.Text = modMain.GiveIni(text, "TEMPLATE", "AnnoBlipLen")
		IL_116C:
		num = 155
		Me.txtStart.Text = modMain.GiveIni(text, "TEMPLATE", "START")
		IL_118E:
		num = 156
		Me.txtLen.Text = modMain.GiveIni(text, "TEMPLATE", "LAENGE")
		IL_11B0:
		num = 157
		Me.cmbBlipLevel1.SelectedIndex = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "BLIPLEVEL1"))))
		IL_11DD:
		num = 158
		Me.cmbBlipLevel2.SelectedIndex = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "BLIPLEVEL2"))))
		IL_120A:
		num = 159
		Me.cmbBlipLevel3.SelectedIndex = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "BLIPLEVEL3"))))
		IL_1237:
		ProjectData.ClearProjectError()
		num4 = 1
		IL_123E:
		num = 161
		Me.chkSplit.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "DOSPLIT"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_1284:
		num = 162
		Me.cmbMaxDocumentSize.SelectedIndex = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text, "TEMPLATE", "SIZE-FORMAT"))))
		IL_12B1:
		num = 163
		Me.txtSplitBreite.Text = modMain.GiveIni(text, "TEMPLATE", "SIZE-X")
		IL_12D3:
		num = 164
		Me.txtSplitLaenge.Text = modMain.GiveIni(text, "TEMPLATE", "SIZE-Y")
		IL_12F5:
		num = 165
		Me.cmbSplitCount.Text = modMain.GiveIni(text, "TEMPLATE", "SPLIT-COUNT")
		IL_1317:
		num = 166
		Me.txtOverSize.Text = modMain.GiveIni(text, "TEMPLATE", "SPLIT-OVERSIZE")
		IL_1339:
		num = 167
		IL_133F:
		num = 168
		Me.cmbPDFReso.Text = modMain.GiveIni(text, "TEMPLATE", "PDFRESO")
		IL_1361:
		num = 169
		num2 = 0S
		Do
			IL_136A:
			num = 170
			num2 += 1S
		Loop While num2 <= 1S
		IL_137C:
		num = 171
		Me._txtBlipBreiteGross_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipBreiteGross0")
		IL_139E:
		num = 172
		Me._txtBlipBreiteKlein_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipBreiteKlein0")
		IL_13C0:
		num = 173
		Me._txtBlipBreiteMittel_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipBreiteMittel0")
		IL_13E2:
		num = 174
		Me._txtBlipHoeheGross_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipHoeheGross0")
		IL_1404:
		num = 175
		Me._txtBlipHoeheKlein_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipHoeheKlein0")
		IL_1426:
		num = 176
		Me._txtBlipHoeheMittel_0.Text = modMain.GiveIni(text, "TEMPLATE", "BlipHoeheMittel0")
		IL_1448:
		num = 177
		Me.txtQuerHoehe.Text = modMain.GiveIni(text, "TEMPLATE", "QuerHoehe")
		IL_146A:
		num = 178
		Me.txtQuerBreite.Text = modMain.GiveIni(text, "TEMPLATE", "QuerBreite")
		IL_148C:
		num = 179
		Me.txtQuerX.Text = modMain.GiveIni(text, "TEMPLATE", "QuerX")
		IL_14AE:
		num = 180
		Me.txtQuerY.Text = modMain.GiveIni(text, "TEMPLATE", "QuerY")
		IL_14D0:
		num = 181
		Me.txtQuerBlipBreite.Text = modMain.GiveIni(text, "TEMPLATE", "QuerBlipBreite")
		IL_14F2:
		num = 182
		Me.txtQuerBlipHoehe.Text = modMain.GiveIni(text, "TEMPLATE", "QuerBlipHoehe")
		IL_1514:
		num = 183
		Me.txtQuerBlipX.Text = modMain.GiveIni(text, "TEMPLATE", "QuerBlipX")
		IL_1536:
		num = 184
		Me.txtQuerBlipY.Text = modMain.GiveIni(text, "TEMPLATE", "QuerBlipY")
		IL_1558:
		num = 185
		Me.txtInfoHoehe.Text = modMain.GiveIni(text, "TEMPLATE", "InfoHoehe")
		IL_157A:
		num = 186
		Me.txtInfoBreite.Text = modMain.GiveIni(text, "TEMPLATE", "InfoBreite")
		IL_159C:
		num = 187
		Me.txtInfoX.Text = modMain.GiveIni(text, "TEMPLATE", "InfoX")
		IL_15BE:
		num = 188
		Me.txtInfoY.Text = modMain.GiveIni(text, "TEMPLATE", "InfoY")
		IL_15E0:
		num = 189
		Me.txtAnnoHoehe.Text = modMain.GiveIni(text, "TEMPLATE", "AnnoHoehe")
		IL_1602:
		num = 190
		Me.txtAnnoBreite.Text = modMain.GiveIni(text, "TEMPLATE", "AnnoBreite")
		IL_1624:
		num = 191
		Me.txtAnnoX.Text = modMain.GiveIni(text, "TEMPLATE", "AnnoX")
		IL_1646:
		num = 192
		Me.txtAnnoY.Text = modMain.GiveIni(text, "TEMPLATE", "AnnoY")
		IL_1668:
		num = 193
		Me.txtQuerAusrichtung.Text = modMain.GiveIni(text, "TEMPLATE", "QuerAusrichtung")
		IL_168A:
		num = 194
		Me.txtQuerAnnoX.Text = modMain.GiveIni(text, "TEMPLATE", "QuerAnnoX")
		IL_16AC:
		num = 195
		Me.txtQuerAnnoY.Text = modMain.GiveIni(text, "TEMPLATE", "QuerAnnoY")
		IL_16CE:
		num = 196
		Me.txtQuerFont.Text = modMain.GiveIni(text, "TEMPLATE", "QuerFont")
		IL_16F0:
		num = 197
		Me.txtQuerGewicht.Text = modMain.GiveIni(text, "TEMPLATE", "QuerGewicht")
		IL_1712:
		num = 198
		Me.txtInfoTextAusrichtung.Text = modMain.GiveIni(text, "TEMPLATE", "InfoTextAusrichtung")
		IL_1734:
		num = 199
		Me.txtInfoTextX.Text = modMain.GiveIni(text, "TEMPLATE", "InfoTextX")
		IL_1756:
		num = 200
		Me.txtInfoTextY.Text = modMain.GiveIni(text, "TEMPLATE", "InfoTextY")
		IL_1778:
		num = 201
		Me.txtInfoTextFont.Text = modMain.GiveIni(text, "TEMPLATE", "InfoTextFont")
		IL_179A:
		num = 202
		Me.txtInfoTextGewicht.Text = modMain.GiveIni(text, "TEMPLATE", "InfoTextGewicht")
		IL_17BC:
		num = 203
		Me.txtSchritte.Text = modMain.GiveIni(text, "TEMPLATE", "Schrittweite")
		IL_17DE:
		num = 204
		Me._txtVerschluss_0.Text = modMain.GiveIni(text, "TEMPLATE", "VerschlussGeschw")
		IL_1800:
		num = 205
		Me.txtZusatzBelichtung.Text = modMain.GiveIni(text, "TEMPLATE", "ZusatzBelichtung")
		IL_1822:
		num = 206
		Me.chkAutoTrailer.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AutoTrailer"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_1868:
		num = 207
		Me.txtAutoTrailerDistance.Text = modMain.GiveIni(text, "TEMPLATE", "AutoTrailerDistance")
		IL_188A:
		num = 208
		Me.txtAutoTrailerLength.Text = modMain.GiveIni(text, "TEMPLATE", "AutoTrailerLength")
		IL_18AC:
		num = 209
		Me.chkStepsImageToImage.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "StepsImageToImage"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_18F2:
		num = 210
		Me.chkOneToOne.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "OneToOneExposure"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_1938:
		num = 211
		Me.txtFactor.Text = modMain.GiveIni(text, "TEMPLATE", "OneToOneFactor")
		IL_195A:
		num = 212
		Me.txtToleranz.Text = modMain.GiveIni(text, "TEMPLATE", "Toleranz")
		IL_197C:
		num = 213
		Me.txtSchritte.Text = modMain.GiveIni(text, "TEMPLATE", "Schrittweite")
		IL_199E:
		num = 214
		Me.txtZusatzBelichtung.Text = modMain.GiveIni(text, "TEMPLATE", "ZusatzBelichtung")
		IL_19C0:
		num = 215
		Me.txtSchritteBelichtung.Text = modMain.GiveIni(text, "TEMPLATE", "BELICHTUNG")
		IL_19E2:
		num = 216
		If Not Versioned.IsNumeric(Me.txtSchritteBelichtung.Text) Then
			GoTo IL_1A1B
		End If
		IL_19FA:
		num = 217
		Conversion.Val(Me.txtSchritteBelichtung.Text)
		IL_1A1B:
		num = 218
		Me.chkNoPreview.CheckState = CType(Conversions.ToInteger(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "NoPreview"), "1", False) = 0, CheckState.Checked, CheckState.Unchecked)), CheckState)
		IL_1A61:
		num = 219
		Me.cmbKopf.Text = modMain.GiveIni(text, "TEMPLATE", "CAMERAHEAD")
		IL_1A83:
		ProjectData.ClearProjectError()
		num4 = 1
		IL_1A8A:
		num = 222
		Me.chkUseLogFile.CheckState = CheckState.Unchecked
		IL_1A9C:
		num = 223
		text3 = modMain.GiveIni(text, "TEMPLATE", "USELOGFILE")
		IL_1AB5:
		num = 224
		If Operators.CompareString(text3, "1", False) <> 0 Then
			GoTo IL_1ADC
		End If
		IL_1ACA:
		num = 225
		Me.chkUseLogFile.CheckState = CheckState.Checked
		IL_1ADC:
		num = 226
		Me.lblLogFile.Text = modMain.GiveIni(text, "TEMPLATE", "LOGFILEPATH")
		IL_1AFE:
		num = 227
		Me.cmbDelimiter.Text = modMain.GiveIni(text, "TEMPLATE", "DELIMITER")
		IL_1B20:
		num = 228
		text3 = modMain.GiveIni(text, "TEMPLATE", "HEADER0")
		IL_1B39:
		num = 229
		Dim num5 As Short = modMain.HeaderCount - 1S
		num2 = 0S
		While num2 <= num5
			IL_1B4E:
			num = 230
			text3 = modMain.GiveIni(text, "TEMPLATE", "HEADER" + Conversions.ToString(CInt(num2)))
			IL_1B73:
			num = 231
			If Versioned.IsNumeric(text3) Then
				IL_1B82:
				num = 232
				Me.lstHeader.Items(CInt(num2)) = modMain.Headers(CInt(Math.Round(Conversion.Val(text3))))
			End If
			IL_1BAD:
			num = 233
			num2 += 1S
		End While
		IL_1BC0:
		num = 234
		Dim num6 As Short = modMain.TrailerCount - 1S
		num2 = 0S
		While num2 <= num6
			IL_1BD5:
			num = 235
			text3 = modMain.GiveIni(text, "TEMPLATE", "TRAILER" + Conversions.ToString(CInt(num2)))
			IL_1BFA:
			num = 236
			If Versioned.IsNumeric(text3) Then
				IL_1C09:
				num = 237
				Me.lstTrailer.Items(CInt(num2)) = modMain.Trailers(CInt(Math.Round(Conversion.Val(text3))))
			End If
			IL_1C34:
			num = 238
			num2 += 1S
		End While
		IL_1C47:
		num = 239
		Dim num7 As Short = modMain.RecordCount - 1S
		num2 = 0S
		While num2 <= num7
			IL_1C5C:
			num = 240
			text3 = modMain.GiveIni(text, "TEMPLATE", "RECORDS" + Conversions.ToString(CInt(num2)))
			IL_1C81:
			num = 241
			If Versioned.IsNumeric(text3) Then
				IL_1C90:
				num = 242
				Me.lstRecords.Items(CInt(num2)) = modMain.Records(CInt(Math.Round(Conversion.Val(text3))))
			End If
			IL_1CBB:
			num = 243
			num2 += 1S
		End While
		IL_1CCE:
		num = 244
		Dim num8 As Short = modMain.HeaderCount - 1S
		num2 = 0S
		While num2 <= num8
			IL_1CE3:
			num = 245
			text3 = modMain.GiveIni(text, "TEMPLATE", "HEADERSEL" + Conversions.ToString(CInt(num2)))
			IL_1D08:
			num = 246
			If Operators.CompareString(text3, "1", False) = 0 Then
				IL_1D1D:
				num = 247
				Me.lstHeader.SetItemChecked(CInt(num2), True)
			End If
			IL_1D31:
			num = 248
			num2 += 1S
		End While
		IL_1D44:
		num = 249
		Dim num9 As Short = modMain.RecordCount - 1S
		num2 = 0S
		While num2 <= num9
			IL_1D59:
			num = 250
			text3 = modMain.GiveIni(text, "TEMPLATE", "RECORDSSEL" + Conversions.ToString(CInt(num2)))
			IL_1D7E:
			num = 251
			If Operators.CompareString(text3, "1", False) = 0 Then
				IL_1D93:
				num = 252
				Me.lstRecords.SetItemChecked(CInt(num2), True)
			End If
			IL_1DA7:
			num = 253
			num2 += 1S
		End While
		IL_1DBA:
		num = 254
		Dim num10 As Short = modMain.TrailerCount - 1S
		num2 = 0S
		While num2 <= num10
			IL_1DCF:
			num = 255
			text3 = modMain.GiveIni(text, "TEMPLATE", "TRAILERSEL" + Conversions.ToString(CInt(num2)))
			IL_1DF4:
			num = 256
			If Operators.CompareString(text3, "1", False) = 0 Then
				IL_1E09:
				num = 257
				Me.lstTrailer.SetItemChecked(CInt(num2), True)
			End If
			IL_1E1D:
			num = 258
			num2 += 1S
		End While
		IL_1E30:
		num = 259
		Dim text4 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
		IL_1E51:
		num = 260
		num2 = 0S
		Dim value As Integer
		Do
			IL_1E5A:
			num = 261
			If Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num2)), modDeclares.glbKopf, False) = 0 Then
				IL_1E7A:
				num = 262
				value = CInt(num2)
			End If
			IL_1E84:
			num = 263
			num2 += 1S
		Loop While num2 <= 3S
		IL_1E96:
		num = 264
		Me.ToolTip1.SetToolTip(Me.lblPos, modMain.GetRollCountInfo(value))
		IL_1EB4:
		num = 265
		Dim text5 As String = "SYSTEM"
		Dim text6 As String = "CONTINUEROLL" + Conversions.ToString(value)
		If modDeclares.GetPrivateProfileInt(text5, text6, 0, text4) <> 1 Then
			GoTo IL_1F51
		End If
		IL_1EE3:
		num = 266
		Dim cmdFortsetzung As ButtonBase = Me.cmdFortsetzung
		text6 = "TXT_ROLL_IS_CONT"
		cmdFortsetzung.Text = modMain.GetText(text6)
		IL_1F02:
		num = 267
		Me.cmdFortsetzung.Tag = "1"
		IL_1F18:
		num = 268
		If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) <> 0 Then
			GoTo IL_1FBA
		End If
		IL_1F39:
		num = 269
		Me.cmdFortsetzung.Text = "Rolle ist eine Fortsetzung"
		GoTo IL_1FBA
		IL_1F51:
		num = 271
		Dim cmdFortsetzung2 As ButtonBase = Me.cmdFortsetzung
		text6 = "TXT_ROLL_IS_NOT_CONT"
		cmdFortsetzung2.Text = modMain.GetText(text6)
		IL_1F70:
		num = 272
		Me.cmdFortsetzung.Tag = "0"
		IL_1F86:
		num = 273
		If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) <> 0 Then
			GoTo IL_1FBA
		End If
		IL_1FA4:
		num = 274
		Me.cmdFortsetzung.Text = "Rolle ist KEINE Fortsetzung"
		IL_1FBA:
		GoTo IL_2458
		IL_1FBF:
		Dim num11 As Integer = num12 + 1
		num12 = 0
		switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num11)
		IL_2419:
		GoTo IL_244D
		IL_241B:
		num12 = num
		switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num4)
		IL_242B:
	Catch obj2 When endfilter(TypeOf obj Is Exception And num4 <> 0 And num12 = 0)
		Dim ex As Exception = CType(obj2, Exception)
		GoTo IL_241B
	End Try
	IL_244D:
	Throw ProjectData.CreateProjectError(-2146828237)
	IL_2458:
	If num12 <> 0 Then
		ProjectData.ClearProjectError()
	End If
End Sub