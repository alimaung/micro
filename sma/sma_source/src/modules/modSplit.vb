Imports System
Imports fileconverter.My
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200004D RID: 77
	Friend NotInheritable Module modSplit
		' Token: 0x06000ED8 RID: 3800 RVA: 0x00095D00 File Offset: 0x00093F00
		Public Sub HandleSplit(ByRef splitindex As Short, ByRef dx As Integer, ByRef dy As Integer, ByRef cropw As Integer, ByRef croph As Integer)
			If modDeclares.SystemData.SplitCount = 4S Then
				Dim obj As Object = CDbl(modMain.glImage.Width) / 2.0 + CDbl(dx)
				Dim obj2 As Object = CDbl(modMain.glImage.Height) / 2.0 + CDbl(dy)
				Select Case splitindex
					Case 0S
						Dim counter As Object
						Dim loopObj As Object
						If ObjectFlowControl.ForLoopControl.ForLoopInitObj(counter, 0, 8, 1, loopObj, counter) Then
							While ObjectFlowControl.ForLoopControl.ForNextCheckObj(counter, loopObj, counter)
							End While
							Return
						End If
					Case 1S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = 0
							rect.Right_Renamed = CInt(Math.Round(CDbl(cropw) / 2.0 + CDbl(dx)))
							rect.Top = 0
							rect.Bottom = CInt(Math.Round(CDbl(croph) / 2.0 + CDbl(dy)))
							Dim obj3 As Object = modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(0L, 0L, Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 2S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl(cropw) / 2.0 - CDbl(dx)))
							rect.Right_Renamed = cropw
							rect.Top = 0
							rect.Bottom = CInt(Math.Round(CDbl(croph) / 2.0 + CDbl(dy)))
							Dim obj4 As Object = modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl(modMain.glImage.Width) / 2.0 - CDbl(dx))), 0L, Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 3S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = 0
							rect.Right_Renamed = CInt(Math.Round(CDbl(cropw) / 2.0 + CDbl(dx)))
							rect.Top = CInt(Math.Round(CDbl(croph) / 2.0 - CDbl(dy)))
							rect.Bottom = croph
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(0L, CLng(Math.Round(CDbl(modMain.glImage.Height) / 2.0 - CDbl(dy))), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 4S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl(cropw) / 2.0 - CDbl(dx)))
							rect.Right_Renamed = cropw
							rect.Top = CInt(Math.Round(CDbl(croph) / 2.0 - CDbl(dy)))
							rect.Bottom = croph
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl(modMain.glImage.Width) / 2.0 - CDbl(dx))), CLng(Math.Round(CDbl(modMain.glImage.Height) / 2.0 - CDbl(dy))), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case Else
						Return
				End Select
			Else
				Dim obj As Object
				Dim obj2 As Object
				If modDeclares.UseAccusoft Then
					obj = CDbl(cropw) / 3.0 + CDbl(dx)
					obj2 = CDbl(croph) / 3.0 + CDbl(dy)
				Else
					obj = CDbl(modMain.glImage.Width) / 3.0 + CDbl(dx)
					obj2 = CDbl(modMain.glImage.Height) / 3.0 + CDbl(dy)
				End If
				Select Case splitindex
					Case 0S
						Dim counter As Object
						Dim loopObj2 As Object
						If ObjectFlowControl.ForLoopControl.ForLoopInitObj(counter, 0, 8, 1, loopObj2, counter) Then
							While ObjectFlowControl.ForLoopControl.ForNextCheckObj(counter, loopObj2, counter)
							End While
							Return
						End If
					Case 1S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = 0
							rect.Right_Renamed = Conversions.ToInteger(obj)
							rect.Top = 0
							rect.Bottom = Conversions.ToInteger(obj2)
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(0L, 0L, Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 2S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl(cropw) / 3.0 - CDbl(dx) / 2.0))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = 0
							rect.Bottom = Conversions.ToInteger(obj2)
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl(modMain.glImage.Width) / 3.0 - CDbl(dx) / 2.0)), 0L, Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 3S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl((cropw * 2)) / 3.0 - CDbl(dx)))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = 0
							rect.Bottom = Conversions.ToInteger(obj2)
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl((modMain.glImage.Width * 2)) / 3.0 - CDbl(dx))), 0L, Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 4S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = 0
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl(croph) / 3.0 - CDbl(dy) / 2.0))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(0L, CLng(Math.Round(CDbl(modMain.glImage.Height) / 3.0 - CDbl(dy) / 2.0)), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 5S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl(cropw) / 3.0 - CDbl(dx) / 2.0))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl(croph) / 3.0 - CDbl(dy) / 2.0))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl(modMain.glImage.Width) / 3.0 - CDbl(dx) / 2.0)), CLng(Math.Round(CDbl(modMain.glImage.Height) / 3.0 - CDbl(dy) / 2.0)), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 6S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl((cropw * 2)) / 3.0 - CDbl(dx)))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl(croph) / 3.0 - CDbl(dy) / 2.0))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl((modMain.glImage.Width * 2)) / 3.0 - CDbl(dx))), CLng(Math.Round(CDbl(modMain.glImage.Height) / 3.0 - CDbl(dy) / 2.0)), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 7S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = 0
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl((croph * 2)) / 3.0 - CDbl(dy)))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(0L, CLng(Math.Round(CDbl((modMain.glImage.Height * 2)) / 3.0 - CDbl(dy))), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 8S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl(cropw) / 3.0 - CDbl(dx) / 2.0))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl((croph * 2)) / 3.0 - CDbl(dy)))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl(modMain.glImage.Width) / 3.0 - CDbl(dx) / 2.0)), CLng(Math.Round(CDbl((modMain.glImage.Height * 2)) / 3.0 - CDbl(dy))), Conversions.ToLong(obj), Conversions.ToLong(obj2))
						Return
					Case 9S
						If modDeclares.UseAccusoft Then
							Dim rect As modDeclares.RECT
							rect.Left_Renamed = CInt(Math.Round(CDbl((cropw * 2)) / 3.0 - CDbl(dx)))
							rect.Right_Renamed = Conversions.ToInteger(Operators.AddObject(rect.Left_Renamed, obj))
							rect.Top = CInt(Math.Round(CDbl((croph * 2)) / 3.0 - CDbl(dy)))
							rect.Bottom = Conversions.ToInteger(Operators.AddObject(rect.Top, obj2))
							modDeclares.IG_IP_cropD(CInt(modDeclares.handle), rect)
							Return
						End If
						MyProject.Forms.frmImage.Crop(CLng(Math.Round(CDbl((modMain.glImage.Width * 2)) / 3.0 - CDbl(dx))), CLng(Math.Round(CDbl((modMain.glImage.Height * 2)) / 3.0 - CDbl(dy))), Conversions.ToLong(obj), Conversions.ToLong(obj2))
					Case Else
						Return
				End Select
			End If
		End Sub
	End Module
End Namespace
