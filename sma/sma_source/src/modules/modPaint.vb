' Module: modPaint
' Purpose: Handles image manipulation, resizing, and display operations for the file converter application.
' This module provides functionality for repainting images with various transformations including rotation,
' DPI adjustments, and size calculations for different paper formats (A3/A4).

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
		' Module-level variables to track state
		Public LastIndex As Short  ' Tracks the last processed image index
		Public pos As Integer      ' Current position in processing

		' Token: 0x06000EB0 RID: 3760 RVA: 0x00093534 File Offset: 0x00091734
		''' <summary>
		''' Legacy function stub for Accusoft image repainting.
		''' </summary>
		''' <param name="kopfindex">Index of the image header to process</param>
		''' <returns>Integer status code</returns>
		Public Function RepaintImageA(ByRef kopfindex As Short) As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000EB1 RID: 3761 RVA: 0x00093544 File Offset: 0x00091744
		''' <summary>
		''' Legacy function stub for Accusoft version 2 image repainting.
		''' </summary>
		''' <param name="kopfindex">Index of the image header to process</param>
		''' <returns>Integer status code</returns>
		Public Function RepaintImageAccusoft2(ByRef kopfindex As Short) As Integer
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000EB2 RID: 3762 RVA: 0x00093554 File Offset: 0x00091754
		''' <summary>
		''' Main image repainting function that handles image transformations and display.
		''' Processes image rotation, DPI settings, and size calculations based on system settings.
		''' </summary>
		''' <param name="kopfindex">Index of the image header to process</param>
		''' <returns>Long value indicating the processed image dimension</returns>
		Public Function RepaintImage(kopfindex As Integer) As Long
			Try
				' Validate image exists and get initial width
				Dim width As Integer = modMain.glImage.Width
			Catch ex As Exception
				Return 0L
			End Try

			' Make image control visible
			MyProject.Forms.frmImage.ImagXpress1.Visible = True

			' Initialize configuration and dimensions
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim num As Long = CLng(modDeclares.SystemData.Breite)      ' Width from system data
			Dim num2 As Long = CLng(modDeclares.SystemData.Hoehe)      ' Height from system data
			
			' Get resolution settings
			Dim num3 As Long = MyProject.Forms.frmImageXpress.IResX    ' X resolution
			Dim num4 As Long = 1L                                      ' Default scale factor
			Dim iresY As Long = MyProject.Forms.frmImageXpress.IResY   ' Y resolution

			' Handle DPI resolution settings
			Dim text2 As String
			If num3 = 0L Then
				' If no DPI is set, try to use standard DPI or prompt user
				If modDeclares.StandardDPI <> 0 Then
					num3 = CLng(modDeclares.StandardDPI)
				Else
					' Prompt user for DPI input if no standard is set
					text2 = "TXT_NO_DPI"
					Dim text3 As String = modMain.GetText(text2)
					If Operators.CompareString(text3, "", False) = 0 Then
						text3 = "Die aktuelle Bilddatei enthält keine DPI-Information!" & vbCr & "Bitte geben Sie einen Standardwert ein, der für diese Datei und alle folgenden verwendet werden kann."
						text3 = Interaction.InputBox(text3, "200", "", -1, -1)
						If Versioned.IsNumeric(text3) Then
							' Set user-provided DPI value
							modDeclares.StandardDPI = CInt(Math.Round(Conversion.Val(text3)))
							num3 = CLng(modDeclares.StandardDPI)
						Else
							' Default to 200 DPI if no valid input
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

			' Store current image dimensions
			Dim num6 As Long = CLng(modMain.glImage.Width)             ' Current image width
			Dim num7 As Long = CLng(modMain.glImage.Height)            ' Current image height
			modDeclares.Painted_Image_Width = CInt(num6)               ' Store painted width for reference

			' Calculate aspect ratios and prepare for transformations
			Dim num8 As Long = num2                                    ' Target height
			Dim num9 As Long = num                                     ' Target width
			Dim num10 As Double
			Dim num11 As Long = num6                                   ' Working width
			Dim num12 As Long = num7                                   ' Working height

			' Handle one-to-one exposure mode
			If modDeclares.SystemData.OneToOneExposure Then
				' Calculate aspect ratios for source and target
				Dim num13 As Double = CDbl(num9) / CDbl(num8)         ' Target aspect ratio
				Dim num14 As Double = CDbl(num6) / CDbl(num7)         ' Source aspect ratio
				
				' Determine if orientations match
				Dim flag As Boolean = False
				If (num13 > 1.0 And num14 > 1.0) Or (num13 < 1.0 And num14 < 1.0) Then
					flag = True
				End If

				' Determine rotation angle based on portrait/landscape orientation
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

				' Apply additional rotation based on fixed rotation settings
				If modDeclares.SystemData.FixRot = 3S Then
					num15 += 180    ' 180-degree rotation
				End If
				If modDeclares.SystemData.FixRot = 2S Then
					num15 += 90     ' 90-degree rotation
				End If
				If modDeclares.SystemData.FixRot = 4S Then
					num15 += 270    ' 270-degree rotation
				End If

				' Perform the actual image rotation if needed
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

				' Update dimensions if image was rotated 90 or 270 degrees
				If num15 = 90 Or num15 = 270 Then
					Dim num16 As Long = num6
					num6 = num7        ' Swap width and height
					num7 = num16
				End If

				' Set resolution and default to 72 DPI if not specified
				num10 = CDbl(MyProject.Forms.frmImageXpress.IResX)
				If num10 = 0.0 Then
					num10 = 72.0
				End If

				' Update image dimensions after rotation
				num11 = MyProject.Forms.frmImageXpress.IWidth
				num12 = MyProject.Forms.frmImageXpress.IHeight
				num11 = num6
				num12 = num7

				' Handle special cases for A4 landscape rotation
				If (modDeclares.SystemData.LandscapeA4Drehen And CDbl(num12) / CDbl(num11) < 1.0) AndAlso CDbl(num12) * 25.4 / num10 < 230.0 Then
					' Rotate A4 landscape images based on settings
					If modDeclares.SystemData.A4R Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
					Else
						text2 = "Rotate A4 90"
						modDeclares.OutputDebugString(text2)
						modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
					End If

					' Update dimensions after A4 rotation
					num11 = CLng(modMain.glImage.Width)
					num12 = CLng(modMain.glImage.Height)
					MyProject.Forms.frmImageXpress.IHeight = num12
					MyProject.Forms.frmImageXpress.IWidth = num11
					modDeclares.Painted_Image_Width = CInt(num11)
				End If

				' Handle special cases for A3 portrait rotation
				If modDeclares.SystemData.PortaitA3Drehen AndAlso (CDbl(num12) * 25.4 / num10 > 400.0 And CDbl(num12) / CDbl(num11) > 1.0) Then
					' Rotate A3 portrait images based on settings
					If modDeclares.SystemData.A3R Then
						modMain.glImage.RotateFlip(RotateFlipType.Rotate90FlipNone)
					Else
						modMain.glImage.RotateFlip(RotateFlipType.Rotate270FlipNone)
					End If

					' Update dimensions after A3 rotation
					num11 = CLng(modMain.glImage.Width)
					num12 = CLng(modMain.glImage.Height)
					MyProject.Forms.frmImageXpress.IWidth = num11
					MyProject.Forms.frmImageXpress.IHeight = num12
					modDeclares.Painted_Image_Width = CInt(num11)
				End If

				' Handle DPI resolution settings
				Dim num17 As Double = CDbl(num11) / num10 * 25.4
				Dim num18 As Double = CDbl(num12) / num10 * 25.4
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
				Dim num27 As Double = CDbl(modDeclares.SystemData.Breite) / num25
				Dim num28 As Double = CDbl(modDeclares.SystemData.Hoehe) / num24

				' Calculate final dimensions based on system data and scaling factors
				MyProject.Forms.frmImage.ImagXpress1.Width = CInt(Math.Round(num27 * 15.0))
				MyProject.Forms.frmImage.ImagXpress1.Height = CInt(Math.Round(num28 * 15.0))
				MyProject.Forms.frmImage.DestWidth = CLng(Math.Round(num27))
				MyProject.Forms.frmImage.DestHeight = CLng(Math.Round(num28))
			Else
				' Handle auto-alignment mode
				Dim num15 As Integer
				If Not modDeclares.SystemData.AutoAlign Then
					' Set rotation based on portrait/landscape orientation
					If modDeclares.SystemData.portrait(kopfindex) Then
						num15 = 90
					Else
						num15 = 0
					End If
					
					' Apply fixed rotation settings
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

				' Apply auto-alignment adjustments if enabled
				If modDeclares.SystemData.AutoAlign Then
					' Calculate aspect ratios
					Dim num29 As Double = CDbl(num8) / CDbl(num9)
					num17 = CDbl(modMain.glImage.Width)
					num18 = CDbl(modMain.glImage.Height)
					Dim num30 As Double = num17 / num18

					' Adjust rotation based on orientation and aspect ratios
					If modDeclares.glbOrientation Then
						If (num29 < 1.0 And num30 > 1.0) Or (num29 > 1.0 And num30 < 1.0) Then
							If modDeclares.ffrmFilmPreview.opt90.Checked Then
								num15 -= 90
							End If
							If modDeclares.ffrmFilmPreview.opt270.Checked Then
								num15 += 90
							End If
						End If
					End If

					' Apply 180-degree rotation if needed
					If num15 Mod 360 = 0 AndAlso modDeclares.SystemData.AutoAlign180 Then
						num15 = 180
					End If
				End If

				' Apply the calculated rotation
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

				' Update dimensions after rotation if needed
				If num15 = 90 Or num15 = 270 Then
					Dim num32 As Long = num6
					num6 = num7
					num7 = num32
					num11 = num6
					num12 = num7
				End If

				' Set default resolution if not specified
				If num3 = 0L Then
					num3 = 1L
					num4 = 96L
				End If

				' Calculate final dimensions based on aspect ratio
				Dim num33 As Double = CDbl(num6)
				Dim num34 As Double = CDbl(num7)
				Dim num35 As Double = num33 / num34

				' Adjust dimensions to fit display area while maintaining aspect ratio
				If CDbl(MyProject.Forms.frmImage.Width) / CDbl(MyProject.Forms.frmImage.Height) > num35 Then
					num36 = CLng(modDeclares.SystemData.Hoehe)
					num37 = CLng(Math.Round(num35 * CDbl(num36)))
				Else
					num37 = CLng(modDeclares.SystemData.Breite)
					num36 = CLng(Math.Round(CDbl(num37) / num35))
				End If

				' Set final dimensions
				MyProject.Forms.frmImage.ImagXpress1.Height = CInt(num36)
				MyProject.Forms.frmImage.ImagXpress1.Width = CInt(num37)
				MyProject.Forms.frmImage.DestWidth = num37
				MyProject.Forms.frmImage.DestHeight = num36

				' Handle American paper sizes if enabled
				If modDeclares.SystemData.UseAmericanSizes Then
					' Calculate dimensions based on American paper sizes
					Dim num38 As Double = CDbl(num6)
					If num38 < CDbl(num7) Then
						num38 = CDbl(num7)
					End If
					num38 /= CDbl(num3) / CDbl(num4)

					' Find matching paper size
					Dim num39 As Long = 1L
					While Not(num38 >= modDeclares.SystemData.ASizes(CInt(num39)).min And num38 < modDeclares.SystemData.ASizes(CInt(num39)).max)
						num39 += 1L
						If num39 > 5L Then
							Exit While
						End If
					End While

					' Apply American size dimensions
					num37 = CLng(Math.Round(modDeclares.SystemData.ASizes(CInt(num39)).MonitorX))
					num36 = CLng(Math.Round(modDeclares.SystemData.ASizes(CInt(num39)).MonitorY))
				End If
			End If

			' Apply frame if enabled
			If modDeclares.SystemData.UseFrame Then
				MyProject.Forms.frmImage.ImagXpress1.Left = modDeclares.SystemData.FrameWidth
				MyProject.Forms.frmImage.ImagXpress1.Top = modDeclares.SystemData.FrameWidth
				
				' Adjust dimensions for frame width
				Dim num50 As Integer = CInt(MyProject.Forms.frmImage.DestWidth)
				num50 -= modDeclares.SystemData.FrameWidth * 2
				Dim num51 As Integer = CInt(MyProject.Forms.frmImage.DestHeight)
				num51 -= modDeclares.SystemData.FrameWidth * 2
				MyProject.Forms.frmImage.DestWidth = CLng(num50)
				MyProject.Forms.frmImage.DestHeight = CLng(num51)
			End If

			' Set final image control dimensions
			MyProject.Forms.frmImage.ImagXpress1.Width = CInt(MyProject.Forms.frmImage.DestWidth)
			MyProject.Forms.frmImage.ImagXpress1.Height = CInt(MyProject.Forms.frmImage.DestHeight)

			' Position image based on alignment settings
			If modDeclares.SystemData.optOben Then
				MyProject.Forms.frmImage.ImagXpress1.Top = 0
			End If
			If modDeclares.SystemData.optUnten Then
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt((CLng(MyProject.Forms.frmImage.Height) - MyProject.Forms.frmImage.DestHeight))
			End If
			If modDeclares.SystemData.optCenter Then
				MyProject.Forms.frmImage.ImagXpress1.Top = CInt(Math.Round(CDbl(MyProject.Forms.frmImage.Height) / 2.0 - CDbl(MyProject.Forms.frmImage.DestHeight) / 2.0))
			End If

			' Resize and update the image
			modMain.glImage = modPaint.ResizeImage(CType(modMain.glImage, Bitmap), CInt(MyProject.Forms.frmImage.DestWidth), CInt(MyProject.Forms.frmImage.DestHeight))
			MyProject.Forms.frmImage.ImagXpress1.Image = modMain.glImage

			Dim oneToOneExposure As Boolean = modDeclares.SystemData.OneToOneExposure
			Return CLng(Math.Round(MyProject.Forms.frmImage.DestHeight))
		End Function

		' Token: 0x06000EB3 RID: 3763 RVA: 0x00094764 File Offset: 0x00092964
		''' <summary>
		''' Resizes a bitmap image to specified dimensions while maintaining quality settings based on size changes.
		''' Handles different quality settings for upscaling vs downscaling and special cases like A3/A4 duplex.
		''' </summary>
		''' <param name="bmSource">Source bitmap to resize</param>
		''' <param name="TargetWidth">Desired width in pixels</param>
		''' <param name="TargetHeight">Desired height in pixels</param>
		''' <returns>Resized bitmap</returns>
		Public Function ResizeImage(bmSource As Bitmap, TargetWidth As Integer, TargetHeight As Integer) As Bitmap
			Try
				' Create new bitmap with target dimensions
				Dim bitmap As Bitmap = New Bitmap(TargetWidth, TargetHeight, PixelFormat.Format32bppArgb)

				' Calculate aspect ratios
				Dim sourceAspect As Double = CDbl(bmSource.Width) / CDbl(bmSource.Height)
				Dim targetAspect As Double = CDbl(bitmap.Width) / CDbl(bitmap.Height)

				' Initialize drawing coordinates
				Dim drawX As Integer = 0
				Dim drawY As Integer = 0
				Dim drawWidth As Integer = bitmap.Width
				Dim drawHeight As Integer = bitmap.Height

				' Adjust dimensions to maintain aspect ratio if needed
				If targetAspect <> sourceAspect Then
					If targetAspect > sourceAspect Then
						' Target is wider than source - adjust width
						drawWidth = Convert.ToInt32(drawHeight * sourceAspect)
						drawX = (bitmap.Width - drawWidth) \ 2
					Else
						' Target is taller than source - adjust height
						drawHeight = Convert.ToInt32(drawWidth / sourceAspect)
						drawY = (bitmap.Height - drawHeight) \ 2
					End If
				End If

				' Create graphics object for drawing
				Using graphics As Graphics = Graphics.FromImage(bitmap)
					' Set compositing mode for overlay
					graphics.CompositingMode = CompositingMode.SourceOver

					' Set quality settings based on resize operation
					If (bmSource.Width < TargetWidth And bmSource.Height < TargetHeight) Or _
					   modDeclares.SystemData.A3A4Duplex Or _
					   modDeclares.SystemData.JPEGProcessor Then
						' Use high speed settings for upscaling or special cases
						graphics.CompositingQuality = CompositingQuality.HighSpeed
						graphics.InterpolationMode = InterpolationMode.NearestNeighbor
						graphics.PixelOffsetMode = PixelOffsetMode.HighSpeed
						graphics.SmoothingMode = SmoothingMode.HighSpeed
					Else
						' Use high quality settings for downscaling
						graphics.CompositingQuality = CompositingQuality.HighQuality
						graphics.InterpolationMode = InterpolationMode.HighQualityBicubic
						graphics.PixelOffsetMode = PixelOffsetMode.HighQuality
						graphics.SmoothingMode = SmoothingMode.AntiAlias
					End If

					' Draw the resized image
					graphics.DrawImage(bmSource, drawX, drawY, drawWidth, drawHeight)
				End Using

				Return bitmap

			Catch ex As Exception
				' Log error and show message
				Dim errorMsg As String = "ResizeImage:" + ex.Description + vbCrLf + ex.Source
				modMain.msgbox2(errorMsg, 0, "file-converter")
				Return Nothing
			End Try
		End Function
	End Module
End Namespace
