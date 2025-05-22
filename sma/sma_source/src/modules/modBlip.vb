Imports System
Imports fileconverter.My
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000042 RID: 66
	Friend NotInheritable Module modBLIP
		' Token: 0x06000D8A RID: 3466 RVA: 0x0006EB64 File Offset: 0x0006CD64
		Public Sub SetBlipSizes(ByRef doclevel As Short)
			If modDeclares.gllevel = 1 Then
				Dim num As Short = doclevel
				If num <> 1S Then
					If num = 2S Then
						Select Case modDeclares.SystemData.Blip2Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								End If
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								End If
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								End If
						End Select
					End If
				Else
					Select Case modDeclares.SystemData.Blip3Size
						Case 0S
							If modDeclares.glbOrientation Then
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
							Else
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
							End If
						Case 1S
							If modDeclares.glbOrientation Then
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
							Else
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
							End If
						Case 2S
							If modDeclares.glbOrientation Then
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
							Else
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
							End If
					End Select
				End If
			End If
			If modDeclares.gllevel = 2 Then
				Select Case doclevel
					Case 1S
						Select Case modDeclares.SystemData.Blip3Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								End If
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								End If
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								End If
						End Select
					Case 2S
						Select Case modDeclares.SystemData.Blip2Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								End If
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								End If
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								End If
						End Select
					Case 3S
						Select Case modDeclares.SystemData.Blip1Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								End If
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								End If
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
								Else
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								End If
						End Select
				End Select
			End If
			If modDeclares.gllevel = 3 Then
				Select Case doclevel
					Case 1S
						Select Case modDeclares.SystemData.Blip3Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								Return
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								Return
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
							Case Else
								Return
						End Select
					Case 2S
						Select Case modDeclares.SystemData.Blip2Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								Return
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								Return
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								Return
							Case Else
								Return
						End Select
					Case 3S
						Select Case modDeclares.SystemData.Blip1Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								Return
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								Return
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								Return
							Case Else
								Return
						End Select
					Case 4S
						Select Case modDeclares.SystemData.Blip1Size
							Case 0S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheKlein
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteKlein
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheKlein
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteKlein
								Return
							Case 1S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheMittel
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteMittel
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheMittel
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteMittel
								Return
							Case 2S
								If modDeclares.glbOrientation Then
									MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipHoeheGross
									MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipBreiteGross
									Return
								End If
								MyProject.Forms.frmBlipWin.ShpBLIP_.Width = modDeclares.SystemData.BlipHoeheGross
								MyProject.Forms.frmBlipWin.ShpBLIP_.Height = modDeclares.SystemData.BlipBreiteGross
								Return
							Case Else
								Return
						End Select
					Case Else
						Return
				End Select
			End If
		End Sub
	End Module
End Namespace
