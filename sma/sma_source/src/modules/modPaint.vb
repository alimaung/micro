Imports System
Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Drawing.Imaging
Imports System.Runtime.CompilerServices
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000049 RID: 73
	Friend NotInheritable Module modPaint
		' Token: 0x06000EB0 RID: 3760 RVA: 0x00093534 File Offset: 0x00091734
		Public Function RepaintImageA(ByRef kopfindex As Short) As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000EB1 RID: 3761 RVA: 0x00093544 File Offset: 0x00091744
		Public Function RepaintImageAccusoft2(ByRef kopfindex As Short) As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000EB2 RID: 3762 RVA: 0x00093554 File Offset: 0x00091754
		Public Function RepaintImage(kopfindex As Integer) As Long
			Try
				Dim width As Integer = modMain.glImage.Width
			Catch ex As Exception
				Return 0L
			End Try
			MyProject.Forms.frmImage.ImagXpress1.Visible = True
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim num As Long = CLng(modDeclares.SystemData.Breite)
			Dim num2 As Long = CLng(modDeclares.SystemData.Hoehe)
			Dim num3 As Long = MyProject.Forms.frmImageXpress.IResX
			Dim num4 As Long = 1L
			Dim iresY As Long = MyProject.Forms.frmImageXpress.IResY
			Dim text2 As String
			If num3 = 0L Then
				If modDeclares.StandardDPI <> 0 Then
					num3 = CLng(modDeclares.StandardDPI)
				Else
					text2 = "TXT_NO_DPI"
					Dim text3 As String = modMain.GetText(text2)
					If Operators.CompareString(text3, "", False) = 0 Then
						text3 = "Die aktuelle Bilddatei enthält keine DPI-Information!" & vbCr & "Bitte geben Sie einen Standardwert ein, der für diese Datei und alle folgenden verwendet werden kann."
						text3 = Interaction.InputBox(text3, "200", "", -1, -1)
						If Versioned.IsNumeric(text3) Then
							' The following expression was wrapped in a checked-expression
							modDeclares.StandardDPI = CInt(Math.Round(Conversion.Val(text3)))
							num3 = CLng(modDeclares.StandardDPI)
						Else
							text2 = "TXT_NO_DEFAULT_TO_200"
							text3 = modMain.GetText(text2)
							If Operators.CompareString(text3, "", False) = 0 Then
								text3 = "Standard DPI wurde auf 200 gesetzt!"
								Dim num5 As Short = 0S
								text2 = "file-converter"
								modMain.msgbox2(text3, num5, text2)
								modDeclares.StandardDPI = 200
								num3 = CLng(modDeclares.StandardDPI)
							End If
						End If
					End If
				End If
			End If
			Dim num6 As Long = CLng(modMain.glImage.Width)
			Dim num7 As Long = CLng(modMain.glImage.Height)
			Dim num10 As Double
			Dim num12 As Long
			Dim result As Long
			modDeclares.Painted_Image_Width = CInt(num6)
			Dim num8 As Long = num2
			Dim num9 As Long = num
			num10 = CDbl(MyProject.Forms.frmImageXpress.IResX)
			Dim num11 As Long = MyProject.Forms.frmImageXpress.IWidth
			num12 = MyProject.Forms.frmImageXpress.IHeight
			num11 = num6
			num12 = num7
			Dim num17 As Double
			Dim num18 As Double
			Dim num36 As Long
			Dim num37 As Long
			If modDeclares.SystemData.OneToOneExposure Then
				Dim num13 As Double = CDbl(num9) / CDbl(num8)
				Dim num14 As Double = CDbl(num6) / CDbl(num7)
				Dim flag As Boolean = False
				If num13 > 1.0 And num14 > 1.0 Then
					flag = True
				End If
				If num13 < 1.0 And num14 < 1.0 Then
					flag = True
				End If
				Dim num15 As Integer
				If modDeclares.SystemData.portrait(kopfindex) Then
					num15 = 90
					If flag And modDeclares.SystemData.optLage Then
						num15 = 0
					End If
				Else
					num15 = 0
					If Not flag And modDeclares.SystemData.optLage Then
						num15 = 90
					End If
				End If
				If modDeclares.SystemData.FixRot = 3S Then
					num15 += 180
				End If
				If modDeclares.SystemData.FixRot = 2S Then
					num15 += 90
				End If
				If modDeclares.SystemData.FixRot = 4S Then
					num15 += 270
				End If
				If num15 <> 0 And num15 <> 360 Then
					If num15 = 90 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
					End If
					If num15 = 180 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate180FlipNone)
					End If
					If num15 = 270 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
					End If
				End If
				If num15 = 90 Or num15 = 270 Then
					Dim num16 As Long = num6
					num6 = num7
					num7 = num16
				End If
				num10 = CDbl(MyProject.Forms.frmImageXpress.IResX)
				If num10 = 0.0 Then
					num10 = 72.0
				End If
				num11 = MyProject.Forms.frmImageXpress.IWidth
				num12 = MyProject.Forms.frmImageXpress.IHeight
				num11 = num6
				num12 = num7
				Dim num27 As Double
				Dim num28 As Double

					If(modDeclares.SystemData.LandscapeA4Drehen And CDbl(num12) / CDbl(num11) < 1.0) AndAlso CDbl(num12) * 25.4 / num10 < 230.0 Then
						If modDeclares.SystemData.A4R Then
							modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
						Else
							text2 = "Rotate A4 90"
							modDeclares.OutputDebugString(text2)
							modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
						End If
						num11 = CLng(modMain.glImage.Width)
						num12 = CLng(modMain.glImage.Height)
						MyProject.Forms.frmImageXpress.IHeight = num12
						MyProject.Forms.frmImageXpress.IWidth = num11
						modDeclares.Painted_Image_Width = CInt(num11)
					End If
					If modDeclares.SystemData.PortaitA3Drehen AndAlso (CDbl(num12) * 25.4 / num10 > 400.0 And CDbl(num12) / CDbl(num11) > 1.0) Then
						If modDeclares.SystemData.A3R Then
							modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
						Else
							modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
						End If
						num11 = CLng(modMain.glImage.Width)
						num12 = CLng(modMain.glImage.Height)
						MyProject.Forms.frmImageXpress.IWidth = num11
						MyProject.Forms.frmImageXpress.IHeight = num12
						modDeclares.Painted_Image_Width = CInt(num11)
					End If
					If MyProject.Forms.frmImageXpress.IResX = 0L Then
						MyProject.Forms.frmImageXpress.IResX = 200L
					End If
					If MyProject.Forms.frmImageXpress.IResY = 0L Then
						MyProject.Forms.frmImageXpress.IResY = 200L
					End If
					num17 = CDbl(num11) / num10 * 25.4
					num18 = CDbl(num12) / num10 * 25.4
					Dim num19 As Double = modDeclares.SystemData.MonitorHeightOnFilm(kopfindex) * CDbl(modDeclares.SystemData.Breite) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.Factor
					Dim num20 As Double = modDeclares.SystemData.MonitorHeightOnFilm(kopfindex)
					Dim systemData As modDeclares.typSystem = modDeclares.SystemData
					num19 = modDeclares.SystemData.MonitorHeightOnFilm(kopfindex) * modDeclares.SystemData.Factor
					Dim num21 As Double = modDeclares.SystemData.MonitorHeightOnFilm(kopfindex) / CDbl(modDeclares.SystemData.Breite)
					Dim num22 As Double = CDbl(modDeclares.SystemData.Hoehe)
					Dim systemData2 As modDeclares.typSystem = modDeclares.SystemData
					Dim num23 As Double = modDeclares.SystemData.MonitorHeightOnFilm(kopfindex) * modDeclares.SystemData.Factor
					num19 = num23 * CDbl(modDeclares.SystemData.Breite) / CDbl(modDeclares.SystemData.Hoehe)
					Dim num24 As Double = num23 / num18
					Dim num25 As Double = num19 / num17
					If num25 < 1.0 Or num24 < 1.0 Then
						Dim num26 As Double = modMain.dmin(num25, num24)
						num25 /= num26
						num24 /= num26
					End If
					num27 = CDbl(modDeclares.SystemData.Breite) / num25
					num28 = CDbl(modDeclares.SystemData.Hoehe) / num24

				MyProject.Forms.frmImage.ImagXpress1.Width = CInt(Math.Round(num27 * 15.0))
				MyProject.Forms.frmImage.ImagXpress1.Height = CInt(Math.Round(num28 * 15.0))
				MyProject.Forms.frmImage.DestWidth = CLng(Math.Round(num27))
				MyProject.Forms.frmImage.DestHeight = CLng(Math.Round(num28))
			Else
				Dim num15 As Integer
				If Not modDeclares.SystemData.AutoAlign Then
					If modDeclares.SystemData.portrait(kopfindex) Then
						num15 = 90
					Else
						num15 = 0
					End If
					If modDeclares.SystemData.FixRot = 3S Then
						num15 += 180
					End If
					If modDeclares.SystemData.FixRot = 2S Then
						num15 += 90
					End If
					If modDeclares.SystemData.FixRot = 4S Then
						num15 += 270
					End If
				ElseIf modDeclares.ffrmFilmPreview.opt270.Checked Then
					num15 = 270
				Else
					num15 = 90
				End If
				If modDeclares.SystemData.AutoAlign Then
					Dim num29 As Double = CDbl(num8) / CDbl(num9)
					num17 = CDbl(modMain.glImage.Width)
					num18 = CDbl(modMain.glImage.Height)
					Dim num30 As Double = num17 / num18
					If modDeclares.glbOrientation Then
						If(num29 < 1.0 And num30 > 1.0) Or (num29 > 1.0 And num30 < 1.0) Then
							If modDeclares.ffrmFilmPreview.opt90.Checked Then
								num15 -= 90
							End If
							If modDeclares.ffrmFilmPreview.opt270.Checked Then
								num15 += 90
							End If
						End If
					ElseIf(num29 < 1.0 And num30 > 1.0) Or (num29 < 1.0 And num30 > 1.0) Then
						If modDeclares.ffrmFilmPreview.opt90.Checked Then
							num15 -= 90
						End If
						If modDeclares.ffrmFilmPreview.opt270.Checked Then
							num15 += 90
						End If
					End If
					If num15 Mod 360 = 0 AndAlso modDeclares.SystemData.AutoAlign180 Then
						num15 = 180
					End If
				End If
				Dim num31 As Integer = num15 Mod 360
				If num31 <= 90 Then
					If num31 <> 0 AndAlso num31 <> 90 Then
					End If
				ElseIf num31 <> 180 Then
				End If
				If num15 <> 0 And num15 <> 360 Then
					If num15 = 90 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
					End If
					If num15 = 180 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate180FlipNone)
					End If
					If num15 = 270 Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
					End If
				End If
				If num15 = 90 Or num15 = 270 Then
					Dim num32 As Long = num6
					num6 = num7
					num7 = num32
					num11 = num6
					num12 = num7
				End If
				If num3 = 0L Then
					num3 = 1L
					num4 = 96L
				End If
				If iresY = 0L Then
				End If
				Dim num33 As Double = CDbl(num6)
				Dim num34 As Double = CDbl(num7)
				Dim num35 As Double = num33 / num34
				If CDbl(MyProject.Forms.frmImage.Width) / CDbl(MyProject.Forms.frmImage.Height) > num35 Then
					' The following expression was wrapped in a unchecked-expression
					num36 = CLng(modDeclares.SystemData.Hoehe)
					num37 = CLng(Math.Round(num35 * CDbl(num36)))
				Else
					' The following expression was wrapped in a unchecked-expression
					num37 = CLng(modDeclares.SystemData.Breite)
					num36 = CLng(Math.Round(CDbl(num37) / num35))
				End If
				MyProject.Forms.frmImage.ImagXpress1.Height = CInt(num36)
				MyProject.Forms.frmImage.ImagXpress1.Width = CInt(num37)
				MyProject.Forms.frmImage.DestWidth = num37
				MyProject.Forms.frmImage.DestHeight = num36
				If modDeclares.SystemData.UseAmericanSizes Then
					Dim num38 As Double = CDbl(num6)
					If num38 < CDbl(num7) Then
						num38 = CDbl(num7)
					End If
					num38 /= CDbl(num3) / CDbl(num4)
					Dim num39 As Long = 1L
					While Not(num38 >= modDeclares.SystemData.ASizes(CInt(num39)).min And num38 < modDeclares.SystemData.ASizes(CInt(num39)).max)
						num39 += 1L
						If num39 > 5L Then
							IL_A96:
							Dim flag2 As Boolean = num15 = 0 Or num15 = 180 Or num15 = 360
							Dim flag3 As Boolean = False
							If num6 < num7 And num37 < num36 Then
								flag3 = True
							End If
							If num6 > num7 And num37 > num36 Then
								flag3 = True
							End If
							If flag3 Then
								num38 = CDbl(num37)
								num37 = num36
								num36 = CLng(Math.Round(num38))
							End If
							Dim num40 As Long
							MyProject.Forms.frmImage.ImagXpress1.Height = CInt(num40)
							Dim num41 As Long
							MyProject.Forms.frmImage.ImagXpress1.Width = CInt(num41)
							GoTo IL_B1C
						End If
					End While
					num37 = CLng(Math.Round(modDeclares.SystemData.ASizes(CInt(num39)).MonitorX))
					num36 = CLng(Math.Round(modDeclares.SystemData.ASizes(CInt(num39)).MonitorY))
					GoTo IL_A96
				End If
				IL_B1C:
				Dim num42 As Long = 0L
				Dim text4 As String = modMain.GiveIni(text, "SYSTEM", "displayxoffset")
				If Versioned.IsNumeric(text4) Then
					Dim num43 As Long = CLng(Math.Round(Conversion.Val(text4)))
				End If
				text4 = modMain.GiveIni(text, "SYSTEM", "displayyoffset")
				If Versioned.IsNumeric(text4) Then
					num42 = CLng(Math.Round(Conversion.Val(text4)))
				End If
				Dim rect As modDeclares.RECT
				rect.Top = CInt((CLng(rect.Top) + num42))
				rect.Bottom = CInt((CLng(rect.Bottom) + num42))
			End If
			If modDeclares.SystemData.UseAmericanSizes Then
				Dim num40 As Long
				Dim num41 As Long
				If modDeclares.glbOrientation Then
					num40 = num36
					num41 = num37
				Else
					num41 = num36
					num40 = num37
				End If
				MyProject.Forms.frmImage.ImagXpress1.Left = 0
				MyProject.Forms.frmImage.ImagXpress1.Height = CInt(num40)
				MyProject.Forms.frmImage.ImagXpress1.Width = CInt(num41)
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt((CLng(MyProject.Forms.frmImage.Height) - num40 - CLng(modDeclares.SystemData.y)))
			End If
			num17 = CDbl(num11)
			num18 = CDbl(num12)
			Dim num44 As Double = CDbl(MyProject.Forms.frmImage.DestWidth)
			Dim num45 As Double = CDbl(MyProject.Forms.frmImage.DestHeight)
			Dim num46 As Double = num17 / num44
			Dim num47 As Double = num18 / num45
			If modDeclares.glbOrientation Then
				result = CLng(Math.Round(num45))
			Else
				result = CLng(Math.Round(num44))
			End If
			If modDeclares.SystemData.UseAmericanSizes Then
				' The following expression was wrapped in a unchecked-expression
				MyProject.Forms.frmImage.ImagXpress1.Left = CInt(Math.Round(CDbl(MyProject.Forms.frmImage.Width) / 2.0 - CDbl(MyProject.Forms.frmImage.ImagXpress1.Width) / 2.0))
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt(Math.Round(CDbl(MyProject.Forms.frmImage.Height) / 2.0 - CDbl(MyProject.Forms.frmImage.ImagXpress1.Height) / 2.0))
			End If
			Dim num48 As Double = CDbl(num11) / CDbl(num12)
			Dim num49 As Double = CDbl(MyProject.Forms.frmImage.DestWidth) / CDbl(MyProject.Forms.frmImage.DestHeight)
			text2 = "P1"
			modMain.LogFaktor(text2)
			text2 = Conversion.Str(num48)
			modMain.LogFaktor(text2)
			text2 = Conversion.Str(num49)
			modMain.LogFaktor(text2)
			text2 = "frmImage.ImagXpress1.IHeight=" + Strings.Format(MyProject.Forms.frmImage.IHeight, "")
			modMain.LogFaktor(text2)
			text2 = "frmImage.ImagXpress1.IResX=" + Strings.Format(MyProject.Forms.frmImage.IResX, "")
			modMain.LogFaktor(text2)
			text2 = "MonitorHeightOnFilm=" + Strings.Format(modDeclares.SystemData.MonitorHeightOnFilm(kopfindex), "")
			modMain.LogFaktor(text2)
			text2 = String.Concat(New String() { "frmImage.ImagXpress1.Width=", Strings.Format(MyProject.Forms.frmImage.ImagXpress1.Width, ""), " (", Strings.Format(CDbl(MyProject.Forms.frmImage.ImagXpress1.Width) / 15.0, ""), ")" })
			modMain.LogFaktor(text2)
			text2 = "SystemData.Breite=" + Strings.Format(modDeclares.SystemData.Breite, "")
			modMain.LogFaktor(text2)
			modDeclares.film_faktor = CDbl(num12)
			modDeclares.film_faktor = CDbl(MyProject.Forms.frmImage.DestHeight)
			modDeclares.film_faktor = CDbl(num12) / num10 * 25.4
			modDeclares.film_faktor = CDbl(MyProject.Forms.frmImage.DestHeight) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.MonitorHeightOnFilm(kopfindex)
			modDeclares.film_faktor = CDbl(num12) / num10 * 25.4 / (CDbl(MyProject.Forms.frmImage.DestHeight) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.MonitorHeightOnFilm(kopfindex))
			text2 = Strings.Format(modDeclares.film_faktor, "")
			modMain.LogFaktor(text2)
			If modDeclares.SystemData.UseFrame Then
				MyProject.Forms.frmImage.ImagXpress1.Left = modDeclares.SystemData.FrameWidth
				MyProject.Forms.frmImage.ImagXpress1.Top = modDeclares.SystemData.FrameWidth
				Dim num50 As Integer
				Dim num51 As Integer
				num50 = CInt(MyProject.Forms.frmImage.DestWidth)
				num50 -= modDeclares.SystemData.FrameWidth * 2
				num51 = CInt(MyProject.Forms.frmImage.DestHeight)
				num51 -= modDeclares.SystemData.FrameWidth * 2
				MyProject.Forms.frmImage.DestWidth = CLng(num50)
				MyProject.Forms.frmImage.DestHeight = CLng(num51)
			End If
			MyProject.Forms.frmImage.ImagXpress1.Width = CInt(MyProject.Forms.frmImage.DestWidth)
			MyProject.Forms.frmImage.ImagXpress1.Height = CInt(MyProject.Forms.frmImage.DestHeight)
			If modDeclares.SystemData.optOben Then
				MyProject.Forms.frmImage.ImagXpress1.Top = 0
			End If
			If modDeclares.SystemData.optUnten Then
				' The following expression was wrapped in a unchecked-expression
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt((CLng(MyProject.Forms.frmImage.Height) - MyProject.Forms.frmImage.DestHeight))
			End If
			If modDeclares.SystemData.optCenter Then
				' The following expression was wrapped in a unchecked-expression
				Dim num52 As Integer = CInt(Math.Round(CDbl(MyProject.Forms.frmImage.Height) / 2.0 - CDbl(MyProject.Forms.frmImage.DestHeight) / 2.0))
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt(Math.Round(CDbl(MyProject.Forms.frmImage.Height) / 2.0 - CDbl(MyProject.Forms.frmImage.DestHeight) / 2.0))
			End If
			modMain.glImage = modPaint.ResizeImage(CType(modMain.glImage, Bitmap), CInt(MyProject.Forms.frmImage.DestWidth), CInt(MyProject.Forms.frmImage.DestHeight))
			MyProject.Forms.frmImage.ImagXpress1.Image = modMain.glImage
			Dim oneToOneExposure As Boolean = modDeclares.SystemData.OneToOneExposure
			Return result
		End Function

		' Token: 0x06000EB3 RID: 3763 RVA: 0x00094764 File Offset: 0x00092964
		Public Function ResizeImage(bmSource As Bitmap, TargetWidth As Integer, TargetHeight As Integer) As Bitmap
			Dim num As Integer
			Dim result As Bitmap
			Dim num3 As Integer
			Dim obj8 As Object
			Try
				ProjectData.ClearProjectError()
				num = 2
				Dim bitmap As Bitmap = New Bitmap(TargetWidth, TargetHeight, PixelFormat.Format32bppArgb)
				Dim obj As Object = CDbl(bmSource.Width) / CDbl(bmSource.Height)
				Dim left As Object = CDbl(bitmap.Width) / CDbl(bitmap.Height)
				Dim obj2 As Object = 0
				Dim obj3 As Object = 0
				Dim obj4 As Object = bitmap.Width
				Dim obj5 As Object = bitmap.Height
				If Not Operators.ConditionalCompareObjectEqual(left, obj, False) Then
					If Operators.ConditionalCompareObjectGreater(left, obj, False) Then
						obj4 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.MultiplyObject(obj, obj5) }, Nothing, Nothing, Nothing)))
						obj2 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.DivideObject(Operators.SubtractObject(bitmap.Width, obj4), 2) }, Nothing, Nothing, Nothing)))
						obj2 = 0
					Else
						obj5 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.MultiplyObject(Operators.DivideObject(1, obj), obj4) }, Nothing, Nothing, Nothing)))
						obj3 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.DivideObject(Operators.SubtractObject(bitmap.Height, obj5), 2) }, Nothing, Nothing, Nothing)))
						obj3 = Operators.SubtractObject(bitmap.Height, obj5)
						obj3 = 0
					End If
				End If
				Using obj6 As Object = Graphics.FromImage(bitmap)
					Dim obj7 As Object = obj6
					NewLateBinding.LateSetComplex(obj7, Nothing, "CompositingMode", New Object() { CompositingMode.SourceOver }, Nothing, Nothing, False, True)
					If(bmSource.Width < TargetWidth And bmSource.Height < TargetHeight) Or modDeclares.SystemData.A3A4Duplex Or modDeclares.SystemData.JPEGProcessor Then
						NewLateBinding.LateSetComplex(obj7, Nothing, "CompositingQuality", New Object() { CompositingQuality.HighSpeed }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "InterpolationMode", New Object() { InterpolationMode.NearestNeighbor }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "PixelOffsetMode", New Object() { PixelOffsetMode.HighSpeed }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "SmoothingMode", New Object() { SmoothingMode.HighSpeed }, Nothing, Nothing, False, True)
					Else
						NewLateBinding.LateSetComplex(obj7, Nothing, "CompositingQuality", New Object() { CompositingQuality.HighQuality }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "InterpolationMode", New Object() { InterpolationMode.HighQualityBicubic }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "PixelOffsetMode", New Object() { PixelOffsetMode.HighQuality }, Nothing, Nothing, False, True)
						NewLateBinding.LateSetComplex(obj7, Nothing, "SmoothingMode", New Object() { SmoothingMode.AntiAlias }, Nothing, Nothing, False, True)
					End If
					Dim instance As Object = obj7
					Dim type As Type = Nothing
					Dim memberName As String = "DrawImage"
					Dim array As Object() = New Object() { bmSource, obj2, obj3, obj4, obj5 }
					Dim array2 As Object() = array
					Dim argumentNames As String() = Nothing
					Dim typeArguments As Type() = Nothing
					Dim array3 As Boolean() = New Boolean() { True, True, True, True, True }
					Dim array4 As Boolean() = array3
					NewLateBinding.LateCall(instance, type, memberName, array, argumentNames, typeArguments, array3, True)
					If array4(0) Then
						bmSource = CType(Conversions.ChangeType(RuntimeHelpers.GetObjectValue(array2(0)), GetType(Bitmap)), Bitmap)
					End If
					If array4(1) Then
						obj2 = RuntimeHelpers.GetObjectValue(array2(1))
					End If
					If array4(2) Then
						obj3 = RuntimeHelpers.GetObjectValue(array2(2))
					End If
					If array4(3) Then
						obj4 = RuntimeHelpers.GetObjectValue(array2(3))
					End If
					If array4(4) Then
						obj5 = RuntimeHelpers.GetObjectValue(array2(4))
					End If
				End Using
				result = bitmap
				IL_433:
				GoTo IL_476
				IL_3F8:
				Dim text As String = "ResizeImage:" + Information.Err().Description + vbCrLf + Information.Err().Source
				Dim num2 As Short = 0S
				Dim text2 As String = "file-converter"
				modMain.msgbox2(text, num2, text2)
				GoTo IL_433
				IL_435:
				num3 = -1
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_449:
			Catch obj9 When endfilter(TypeOf obj8 Is Exception And num <> 0 And num3 = 0)
				Dim ex As Exception = CType(obj9, Exception)
				GoTo IL_435
			End Try
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_476:
			If num3 <> 0 Then
				ProjectData.ClearProjectError()
			End If
			Return result
		End Function

		' Token: 0x040008F1 RID: 2289
		Public LastIndex As Short

		' Token: 0x040008F2 RID: 2290
		Public pos As Integer
	End Module
End Namespace
