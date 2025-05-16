Imports System
Imports System.Runtime.CompilerServices
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000045 RID: 69
	Friend NotInheritable Module modLicense
		' Token: 0x06000E2D RID: 3629 RVA: 0x0007B280 File Offset: 0x00079480
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function CheckLicense() As Boolean
			modLicense.LicFile = New Object() { 0, 147, 171, 234, 7, 214, 232, 93, 118, 117, 134, 88, 68, 13, 250, 143, 40, 10, 77, 245, 22, 28, 194, 210, 7, 232, 185, 24, 252, 254, 211, 239, 65, 14, 87, 151, 238, 84, 212, 111, 180, 88, 9, 81, 214, 218, 2, 34, 118, 12, 130, 166, 18, 250, 168, 152, 78, 80, 205, 249, 243, 61, 173, 169, 57, 176, 200, 54, 66, 206, 7, 240, 230, 157, 162, 70, 181, 2, 65, 77, 59, 234, 97, 156, 126, 203, 248, 96, 205, 78, 93, 171, 188, 70, 99, 16, 107, 228, 197, 110, 9, 47, 199, 9, 149, 174, 26, 222, 234, 104, 255, 57, 253, 14, 175, 128, 97, 118, 250, 82, 13, 76, 48, 213, 95, 4, 61, 75, 97, 19, 24, 231, 74, 94, 93, 223, 72, 242, 57, 195, 124, 246, 134, 13, 71, 222, 55, 248, 195, 227, 246, 150, 149, 176, 13, 30, 226, 93, 131, 131, 160, 161, 135, 74, 16, 67, 17, 156, 135, 209, 198, 155, 115, 149, 29, 241, 158, 197, 191, 176, 173, 249, 53, 86, 237, 227, 189, 47, 80, 59, 124, 223, 177, 248, 218, 63, 96, 197, 43, 104, 218, 179, 138, 14, 216, 44, 11, 16, 140, 40, 17, 76, 39, 163, 251, 184, 158, 78, 8, 174, 174, 133, 113, 136, 30, 129, 219, 109, 68, 206, 241, 106, 202, 1, 78, 197, 178, 162, 153, 142, 152, 112, 243, 118, 55, 198, 149, 228, 47, 88, 181, 70, 6, 35, 170, 165, 108, 162, 81, 125, 194, 70, 175, 203, 222, 33, 215, 103, 10, 225, 15, 148, 74, 6, 46, 213, 231, 75, 73, 4, 41, 104, 142, 157, 94, 252, 111, 95, 37, 197, 4, 23, 229, 19, 170, 178, 158, 124, 240, 157, 229, 208, 180, 76, 43, 80, 138, 19, 62, 27, 94, 61, 18, 232, 89, 92, 192, 250, 8, 222, 207, 81, 186, 225, 179, 30, 43, 73, 147, 122, 96, 15, 80, 87, 210, 219, 194, 182, 206, 213, 69, 28, 29, 185, 116, 63, 223, 43, 52, 5, 188, 73, 244, 174, 63, 134, 52, 80, 122, 181, 69, 131, 238, 100, 79, 94, 175, 108, 151, 163, 196, 198, 3, 55, 204, 160, 214, 212, 231, 176, 192, 3, 212, 200, 28, 68, 88, 171, 112, 143, 222, 32, 58, 0, 100, 69, 235, 205, 149, 37, 51, 125, 50, 140, 127, 84, 183, 26, 192, 18, 60, 150, 111, 220, 153, 133, 206, 123, 205, 251, 112, 196, 160, 177, 251, 87, 136, 89, 45, 141, 201, 46, 30, 171, 225, 207, 195, 92, 36, 78, 187, 94, 162, 131, 71, 123, 81, 165, 146, 186, 104, 29, 59, 215, 9, 146, 18, 241, 35, 73, 28, 132, 150, 176, 221, 150, 153, 56, 215, 53, 90, 100, 79, 33, 227, 32, 79, 197, 69, 83, 240, 108, 238, 183, 217, 177, 95, 232, 4, 56, 252, 188, 192, 155, 67, 211, 252, 167, 34, 111, 194, 200, 161, 133, 2, 195, 199, 20, 145, 163, 188, 181, 113, 245, 43, 115, 83, 57, 234, 221, 90, 144, 221, 91, 34, 186, 24, 190, 2, 69, 67, 27, 141, 254, 67, 216, 94, 172, 23, 8, 21, 253, 255, 243, 156, 193, 227, 249, 176, 86, 243, 154, 157, 100, 140, 205, 73, 202, 92, 154, 116, 215, 197, 228, 62, 190, 134, 134, 233, 68, 152, 162, 225, 188, 87, 55, 249, 54, 225, 240, 248, 242, 195, 68, 85, 27, 210, 187, 62, 177, 88, 142, 221, 199, 113, 115, 223, 239, 179, 183, 46, 243, 21, 141, 255, 198, 10, 166, 18, 186, 236, 2, 52, 243, 160, 5, 8, 29, 120, 205, 8, 89, 84, 195, 197, 124, 13, 112, 119, 123, 19, 146, 179, 34, 84, 112, 119, 6, 96, 106, 108, 185, 203, 212, 107, 68, 211, 5, 64, 209, 68, 170, 174, 168, 151, 97, 180, 94, 97, 131, 15, 74, 235, 65, 0, 56, 31, 241, 79, 96, 163, 171, 144, 152, 72, 17, 165, 201, 164, 107, 132, 161, 253, 250, 59, 136, 107, 142, 49, 213, 55, 83, 174, 65, 134, 232, 157, 156, 60, 187, 145, 190, 26, 144, 7, 193, 41, 94, 234, 110, 91, 95, 93, 244, 111, 103, 180, 223, 23, 117, 195, 73, 85, 136, 92, 75, 43, 179, 19, 183, 115, 116, 68, 10, 12, 66, 88, 154, 54, 101, 67, 24, 63, 11, 81, 51, 96, 151, 35, 152, 225, 60, 244, 35, 132, 203, 34, 79, 33, 201, 232, 242, 142, 197, 113, 40, 193, 232, 11, 141, 57, 206, 183, 175, 153, 148, 234, 195, 150, 51, 143, 151, 21, 12, 76, 200, 140, 195, 7, 54, 177, 81, 167, 180, 83, 85, 31, 3, 131, 171, 168, 1, 248, 65, 79, 30, 177, 37, 176, 16, 220, 225, 1, 199, 247, 12, 82, 164, 53, 26, 19, 229, 36, 116, 213, 101, 139, 205, 86, 130, 153, 179, 184, 94, 61, 100, 18, 74, 207, 227, 42, 127, 249, 76, 127, 16, 209, 101, 142, 28, 71, 117, 78, 72, 191, 89, 252, 108, 254, 212, 31, 141, 75, 39, 194, 12, 205, 225, 8, 29, 59, 249, 223, 121, 180, 27, 20, 88, 236, 62, 136, 153, 137, 127, 192, 68, 204, 41, 164, 51, 116, 20, 128, 12, 223, 48, 79, 114, 115, 97, 57, 125, 61, 141, 90, 103, 214, 243, 197, 136, 142, 192, 200, 132, 196, 221, 115, 194, 148, 12, 83, 33, 181, 50, 131, 231, 161, 244, 230, 250, 245, 137, 174, 83, 28, 199, 33, 175, 40, 129, 156, 136, 1, 19, 215, 68, 192, 58, 108, 171, 93, 40, 147, 158, 136, 215, 48, 7, 213, 158, 16, 12, 30, 4, 110, 135, 33, 209, 187, 187, 112, 106, 160, 64, 138, 94, 61, 64, 69, 60, 180, 229, 112, 167, 235, 19, 183, 173, 141, 82, 198, 85, 83, 14, 177, 119, 129, 2, 148, 208, 179, 241, 118, 86, 217, 152, 116, 201, 129, 225, 27, 139, 85, 90, 21, 177, 227, 229, 8, 90, 164, 177, 187, 64, 57 }
			Dim array As Byte() = New Byte(1024) {}
			Dim pathName As String = MyProject.Application.Info.DirectoryPath + "\fileconverter.lic"
			Dim flag As Boolean
			If Operators.CompareString(FileSystem.Dir(pathName, FileAttribute.Normal), "", False) = 0 Then
				flag = False
			Else
				modLicense.ReadLicense(pathName, array)
				flag = True
				Dim num As Short = 1S
				Do
					If Operators.ConditionalCompareObjectNotEqual(array(CInt(num)), modLicense.LicFile(CInt(num)), False) Then
						flag = False
					End If
					num += 1S
				Loop While num <= 1024S
				If Not flag Then
					flag = False
					Dim str As String = Support.Format(DateAndTime.Today, "ddmmyyyy", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
					Dim num2 As Short = Conversions.ToShort(Strings.Mid(str, 1, 2))
					Dim num3 As Short = Conversions.ToShort(Strings.Mid(str, 3, 2))
					Dim num4 As Short = Conversions.ToShort(Strings.Mid(str, 5, 4))
					Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
					Dim text2 As String = modMain.GiveIni(text, "SYSTEM", "FIRMWARE")
					If Operators.CompareString(text2, "", False) <> 0 Then
						Dim text3 As String = ""
						Dim num5 As Short = CShort(Strings.Len(text2))
						num = 1S
						While num <= num5
							' The following expression was wrapped in a checked-expression
							text3 += Conversions.ToString(Strings.Chr(Strings.Asc(Strings.Mid(text2, CInt(num), 1)) - 20))
							num += 1S
						End While
						Dim num6 As Short = Conversions.ToShort(Strings.Mid(text3, 1, 2))
						Dim num7 As Short = Conversions.ToShort(Strings.Mid(text3, 3, 2))
						Dim num8 As Short = Conversions.ToShort(Strings.Mid(text3, 5, 4))
						Dim str2 As String = Support.Format(DateAndTime.Today, "ddmmyyyy", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
						num2 = Conversions.ToShort(Strings.Mid(str2, 1, 2))
						num3 = Conversions.ToShort(Strings.Mid(str2, 3, 2))
						num4 = Conversions.ToShort(Strings.Mid(str2, 5, 4))
						If num4 < num8 Then
							flag = False
						ElseIf num4 = num8 And num3 < num7 Then
							flag = False
						ElseIf num4 = num8 And num3 = num7 And num2 < num6 Then
							flag = False
						Else
							flag = True
							If num4 - 2000S >= CShort(array(5)) AndAlso Not(num4 - 2000S = CShort(array(5)) And num3 < CShort(array(3))) AndAlso Not(num4 - 2000S = CShort(array(5)) And num3 = CShort(array(3)) And num2 <= CShort(array(1))) Then
								flag = False
								modLicense.WriteLastStarted()
							End If
						End If
					End If
				End If
			End If
			Return flag
		End Function

		' Token: 0x06000E2E RID: 3630 RVA: 0x0007F14C File Offset: 0x0007D34C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Function ReadLicenseTest() As Object
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), "c:\fileconverter.lic", OpenMode.Random, OpenAccess.[Default], OpenShare.[Default], 1)
			Dim num2 As Short = 1S
			Do
				Dim b As Byte
				FileSystem.FileGet(CInt(num), b, -1L)
				Dim num3 As Short = num2 Mod 100S
				num2 += 1S
			Loop While num2 <= 1024S
			FileSystem.FileClose(New Integer() { CInt(num) })
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E2F RID: 3631 RVA: 0x0007F1A0 File Offset: 0x0007D3A0
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Function ReadLicense(ByRef fname As String, ByRef c As Byte()) As Object
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), fname, OpenMode.Random, OpenAccess.[Default], OpenShare.[Default], 1)
			Dim num2 As Short = 1S
			Do
				FileSystem.FileGet(CInt(num), c(CInt(num2)), -1L)
				num2 += 1S
			Loop While num2 <= 1024S
			FileSystem.FileClose(New Integer() { CInt(num) })
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000E30 RID: 3632 RVA: 0x0007F1F0 File Offset: 0x0007D3F0
		Public Sub WriteLastStarted()
			Dim text As String = Support.Format(DateAndTime.Today, "ddmmyyyy", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			Dim text2 As String = ""
			Dim text3 As String = text
			Dim num As Short = CShort(Strings.Len(text3))
			For num2 As Short = 1S To num
				' The following expression was wrapped in a checked-expression
				text2 += Conversions.ToString(Strings.Chr(Strings.Asc(Strings.Mid(text3, CInt(num2), 1)) + 20))
			Next
			modDeclares.WritePrivateProfileString("SYSTEM", "FIRMWARE", text2, MyProject.Application.Info.DirectoryPath + "\docufile.ini")
		End Sub

		' Token: 0x06000E31 RID: 3633 RVA: 0x0007F27C File Offset: 0x0007D47C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub SetLicDate(ByRef tag As String, ByRef monat As String, ByRef jahr As String)
			modLicense.LicFile = New Object() { 0, 147, 171, 234, 7, 214, 232, 93, 118, 117, 134, 88, 68, 13, 250, 143, 40, 10, 77, 245, 22, 28, 194, 210, 7, 232, 185, 24, 252, 254, 211, 239, 65, 14, 87, 151, 238, 84, 212, 111, 180, 88, 9, 81, 214, 218, 2, 34, 118, 12, 130, 166, 18, 250, 168, 152, 78, 80, 205, 249, 243, 61, 173, 169, 57, 176, 200, 54, 66, 206, 7, 240, 230, 157, 162, 70, 181, 2, 65, 77, 59, 234, 97, 156, 126, 203, 248, 96, 205, 78, 93, 171, 188, 70, 99, 16, 107, 228, 197, 110, 9, 47, 199, 9, 149, 174, 26, 222, 234, 104, 255, 57, 253, 14, 175, 128, 97, 118, 250, 82, 13, 76, 48, 213, 95, 4, 61, 75, 97, 19, 24, 231, 74, 94, 93, 223, 72, 242, 57, 195, 124, 246, 134, 13, 71, 222, 55, 248, 195, 227, 246, 150, 149, 176, 13, 30, 226, 93, 131, 131, 160, 161, 135, 74, 16, 67, 17, 156, 135, 209, 198, 155, 115, 149, 29, 241, 158, 197, 191, 176, 173, 249, 53, 86, 237, 227, 189, 47, 80, 59, 124, 223, 177, 248, 218, 63, 96, 197, 43, 104, 218, 179, 138, 14, 216, 44, 11, 16, 140, 40, 17, 76, 39, 163, 251, 184, 158, 78, 8, 174, 174, 133, 113, 136, 30, 129, 219, 109, 68, 206, 241, 106, 202, 1, 78, 197, 178, 162, 153, 142, 152, 112, 243, 118, 55, 198, 149, 228, 47, 88, 181, 70, 6, 35, 170, 165, 108, 162, 81, 125, 194, 70, 175, 203, 222, 33, 215, 103, 10, 225, 15, 148, 74, 6, 46, 213, 231, 75, 73, 4, 41, 104, 142, 157, 94, 252, 111, 95, 37, 197, 4, 23, 229, 19, 170, 178, 158, 124, 240, 157, 229, 208, 180, 76, 43, 80, 138, 19, 62, 27, 94, 61, 18, 232, 89, 92, 192, 250, 8, 222, 207, 81, 186, 225, 179, 30, 43, 73, 147, 122, 96, 15, 80, 87, 210, 219, 194, 182, 206, 213, 69, 28, 29, 185, 116, 63, 223, 43, 52, 5, 188, 73, 244, 174, 63, 134, 52, 80, 122, 181, 69, 131, 238, 100, 79, 94, 175, 108, 151, 163, 196, 198, 3, 55, 204, 160, 214, 212, 231, 176, 192, 3, 212, 200, 28, 68, 88, 171, 112, 143, 222, 32, 58, 0, 100, 69, 235, 205, 149, 37, 51, 125, 50, 140, 127, 84, 183, 26, 192, 18, 60, 150, 111, 220, 153, 133, 206, 123, 205, 251, 112, 196, 160, 177, 251, 87, 136, 89, 45, 141, 201, 46, 30, 171, 225, 207, 195, 92, 36, 78, 187, 94, 162, 131, 71, 123, 81, 165, 146, 186, 104, 29, 59, 215, 9, 146, 18, 241, 35, 73, 28, 132, 150, 176, 221, 150, 153, 56, 215, 53, 90, 100, 79, 33, 227, 32, 79, 197, 69, 83, 240, 108, 238, 183, 217, 177, 95, 232, 4, 56, 252, 188, 192, 155, 67, 211, 252, 167, 34, 111, 194, 200, 161, 133, 2, 195, 199, 20, 145, 163, 188, 181, 113, 245, 43, 115, 83, 57, 234, 221, 90, 144, 221, 91, 34, 186, 24, 190, 2, 69, 67, 27, 141, 254, 67, 216, 94, 172, 23, 8, 21, 253, 255, 243, 156, 193, 227, 249, 176, 86, 243, 154, 157, 100, 140, 205, 73, 202, 92, 154, 116, 215, 197, 228, 62, 190, 134, 134, 233, 68, 152, 162, 225, 188, 87, 55, 249, 54, 225, 240, 248, 242, 195, 68, 85, 27, 210, 187, 62, 177, 88, 142, 221, 199, 113, 115, 223, 239, 179, 183, 46, 243, 21, 141, 255, 198, 10, 166, 18, 186, 236, 2, 52, 243, 160, 5, 8, 29, 120, 205, 8, 89, 84, 195, 197, 124, 13, 112, 119, 123, 19, 146, 179, 34, 84, 112, 119, 6, 96, 106, 108, 185, 203, 212, 107, 68, 211, 5, 64, 209, 68, 170, 174, 168, 151, 97, 180, 94, 97, 131, 15, 74, 235, 65, 0, 56, 31, 241, 79, 96, 163, 171, 144, 152, 72, 17, 165, 201, 164, 107, 132, 161, 253, 250, 59, 136, 107, 142, 49, 213, 55, 83, 174, 65, 134, 232, 157, 156, 60, 187, 145, 190, 26, 144, 7, 193, 41, 94, 234, 110, 91, 95, 93, 244, 111, 103, 180, 223, 23, 117, 195, 73, 85, 136, 92, 75, 43, 179, 19, 183, 115, 116, 68, 10, 12, 66, 88, 154, 54, 101, 67, 24, 63, 11, 81, 51, 96, 151, 35, 152, 225, 60, 244, 35, 132, 203, 34, 79, 33, 201, 232, 242, 142, 197, 113, 40, 193, 232, 11, 141, 57, 206, 183, 175, 153, 148, 234, 195, 150, 51, 143, 151, 21, 12, 76, 200, 140, 195, 7, 54, 177, 81, 167, 180, 83, 85, 31, 3, 131, 171, 168, 1, 248, 65, 79, 30, 177, 37, 176, 16, 220, 225, 1, 199, 247, 12, 82, 164, 53, 26, 19, 229, 36, 116, 213, 101, 139, 205, 86, 130, 153, 179, 184, 94, 61, 100, 18, 74, 207, 227, 42, 127, 249, 76, 127, 16, 209, 101, 142, 28, 71, 117, 78, 72, 191, 89, 252, 108, 254, 212, 31, 141, 75, 39, 194, 12, 205, 225, 8, 29, 59, 249, 223, 121, 180, 27, 20, 88, 236, 62, 136, 153, 137, 127, 192, 68, 204, 41, 164, 51, 116, 20, 128, 12, 223, 48, 79, 114, 115, 97, 57, 125, 61, 141, 90, 103, 214, 243, 197, 136, 142, 192, 200, 132, 196, 221, 115, 194, 148, 12, 83, 33, 181, 50, 131, 231, 161, 244, 230, 250, 245, 137, 174, 83, 28, 199, 33, 175, 40, 129, 156, 136, 1, 19, 215, 68, 192, 58, 108, 171, 93, 40, 147, 158, 136, 215, 48, 7, 213, 158, 16, 12, 30, 4, 110, 135, 33, 209, 187, 187, 112, 106, 160, 64, 138, 94, 61, 64, 69, 60, 180, 229, 112, 167, 235, 19, 183, 173, 141, 82, 198, 85, 83, 14, 177, 119, 129, 2, 148, 208, 179, 241, 118, 86, 217, 152, 116, 201, 129, 225, 27, 139, 85, 90, 21, 177, 227, 229, 8, 90, 164, 177, 187, 64, 57 }
			Dim num As Short
			Dim num2 As Short
			modLicense.LicFile(1) = CByte(Math.Round(Conversion.Val(tag)))
			modLicense.LicFile(3) = CByte(Math.Round(Conversion.Val(monat)))
			modLicense.LicFile(5) = CByte(Math.Round(Conversion.Val(jahr) - 2000.0))
			num = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num), MyProject.Application.Info.DirectoryPath + "\fileconverter.lic", OpenMode.Random, OpenAccess.[Default], OpenShare.[Default], 1)
			num2 = 1S
			Do
				Dim value As Byte = Conversions.ToByte(modLicense.LicFile(CInt(num2)))
				FileSystem.FilePut(CInt(num), value, -1L)
				num2 += 1S
			Loop While num2 <= 1024S
			FileSystem.FileClose(New Integer() { CInt(num) })
		End Sub

		' Token: 0x040008C8 RID: 2248
		Private LicFile As Object()

		' Token: 0x040008C9 RID: 2249
		Private Const PosTag As Short = 1S

		' Token: 0x040008CA RID: 2250
		Private Const PosMonat As Short = 3S

		' Token: 0x040008CB RID: 2251
		Private Const PosJahr As Short = 5S
	End Module
End Namespace
