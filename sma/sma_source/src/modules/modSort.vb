Imports System
Imports System.Runtime.InteropServices
Imports System.Windows.Forms
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200004C RID: 76
	Friend NotInheritable Module modSort
		' Token: 0x06000ED2 RID: 3794
		Public Declare Unicode Function StrCmpLogicalW Lib "shlwapi" (x As String, y As String) As Integer

		' Token: 0x06000ED3 RID: 3795 RVA: 0x00095658 File Offset: 0x00093858
		Public Sub SortStrings(ByRef str_Renamed As String(), ByRef Count As Integer, ByRef style As modSort.SortStyles, ByRef UpSort As Boolean, ByRef ShowState As Boolean)
			Dim text As String
			If ShowState Then
				text = MyProject.Forms.frmCheckImages.Text
			End If
			Dim array As String(,) = New String(Count + 1 - 1, 20) {}
			modSort.CreateSortTags()
			If style = modSort.SortStyles.StyleExplorer Then
				Dim num As Integer = Count - 1
				For i As Integer = 0 To num
					Dim num2 As Integer = i + 1
					Dim num3 As Integer = Count
					For j As Integer = num2 To num3
						Dim x As String = str_Renamed(i)
						Dim y As String = str_Renamed(j)
						If modSort.StrCmpLogicalW(x, y) > 0 Then
							Dim text2 As String = str_Renamed(i)
							str_Renamed(i) = str_Renamed(j)
							str_Renamed(j) = text2
						End If
					Next
				Next
				Return
			End If
			If style = modSort.SortStyles.StyleXP Then
				modSort.GenerateSortFields(str_Renamed, array, Count)
				Dim num4 As Integer = 1
				Do
					Dim text3 As String = "Datenträger wird analysiert (XP-Sort Subfeld " + Conversions.ToString(num4) + ")"
					MyProject.Forms.frmCheckImages.lblInfo.Text = text3
					Application.DoEvents()
					Dim k As Integer = 1
					Dim num5 As Integer = k + 1
					If num5 <= Count Then
						While k < Count
							Do
								Dim num6 As Integer = num4 - 1
								For l As Integer = 1 To num6
									If Operators.CompareString(Support.Format(array(k, l), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), Support.Format(array(num5, l), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) <> 0 Then
										GoTo IL_12B
									End If
								Next
								num5 += 1
							Loop While num5 <= Count
							IL_12B:
							num5 -= 1
							If num5 > k Then
								Dim num7 As Integer = k
								Dim num8 As Integer = num5 - 1
								For i As Integer = num7 To num8
									If ShowState Then
										MyProject.Forms.frmCheckImages.Text = text + " : " + Support.Format(CDbl((i * 100)) / CDbl((Count - 1)), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "%"
									End If
									Dim num9 As Integer = i + 1
									Dim num10 As Integer = num5
									For j As Integer = num9 To num10
										If UpSort Then
											Dim text4 As String = Support.Format(array(i, num4), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
											Dim text5 As String = Support.Format(array(j, num4), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
											If modSort.StrCmp(text4, text5) = 1S Then
												Dim num11 As Integer = 1
												Dim text2 As String
												Do
													text2 = array(i, num11)
													array(i, num11) = array(j, num11)
													array(j, num11) = text2
													num11 += 1
												Loop While num11 <= 20
												text2 = str_Renamed(i)
												str_Renamed(i) = str_Renamed(j)
												str_Renamed(j) = text2
											End If
										Else
											Dim text5 As String = Support.Format(array(i, num4), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
											Dim text4 As String = Support.Format(array(j, num4), "<", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
											If modSort.StrCmp(text5, text4) = -1S Then
												Dim num11 As Integer = 1
												Dim text2 As String
												Do
													text2 = array(i, num11)
													array(i, num11) = array(j, num11)
													array(j, num11) = text2
													num11 += 1
												Loop While num11 <= 20
												text2 = str_Renamed(i)
												str_Renamed(i) = str_Renamed(j)
												str_Renamed(j) = text2
											End If
										End If
									Next
								Next
							End If
							k = num5 + 1
							num5 = k + 1
						End While
					End If
					num4 += 1
				Loop While num4 <= 20
				Return
			End If
			Dim num12 As Integer = Count - 1
			For i As Integer = 1 To num12
				If ShowState Then
					MyProject.Forms.frmCheckImages.Text = text + " : " + Support.Format(CDbl((i * 100)) / CDbl((Count - 1)), "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + "%"
					Application.DoEvents()
				End If
				Dim num13 As Integer = i + 1
				Dim num14 As Integer = Count
				For j As Integer = num13 To num14
					If UpSort Then
						If String.Compare(str_Renamed(i), str_Renamed(j)) = 1 Then
							Dim text2 As String = str_Renamed(i)
							str_Renamed(i) = str_Renamed(j)
							str_Renamed(j) = text2
						End If
					ElseIf String.Compare(str_Renamed(i), str_Renamed(j)) = -1 Then
						Dim text2 As String = str_Renamed(i)
						str_Renamed(i) = str_Renamed(j)
						str_Renamed(j) = text2
					End If
				Next
			Next
		End Sub

		' Token: 0x06000ED4 RID: 3796 RVA: 0x00095A18 File Offset: 0x00093C18
		Private Sub GenerateSortFields(ByRef str_Renamed As String(), ByRef SortFields As String(,), ByRef Count As Integer)
			Dim array As String() = New String(20) {}
			Dim num As Integer = Count
			For i As Integer = 1 To num
				modSort.SplitToSubFields(str_Renamed(i), array)
				Dim num2 As Integer = 1
				Do
					SortFields(i, num2) = array(num2)
					num2 += 1
				Loop While num2 <= 20
			Next
		End Sub

		' Token: 0x06000ED5 RID: 3797 RVA: 0x00095A64 File Offset: 0x00093C64
		Private Sub SplitToSubFields(ByRef str_Renamed As String, ByRef Fields As String())
			Dim flag As Boolean = False
			Dim num As Integer = 1
			Dim num2 As Integer = 1
			Do
				Fields(num2) = ""
				num2 += 1
			Loop While num2 <= 20
			Dim text As String = Strings.Left(str_Renamed, 1)
			Dim num3 As Integer = 1
			Dim flag2 As Boolean = Not(Strings.Asc(text) < 48 Or Strings.Asc(text) > 57)
			Do
				If flag2 Then
					If Strings.Asc(text) < 48 Or Strings.Asc(text) > 57 Then
						flag2 = False
						Fields(num3) = New String("0"c, 50 - Strings.Len(Fields(num3))) + Fields(num3)
						num3 += 1
					Else
						flag2 = True
					End If
				ElseIf Strings.Asc(text) < 48 Or Strings.Asc(text) > 57 Then
					flag2 = False
				Else
					flag2 = True
					num3 += 1
				End If
				Fields(num3) += text
				num += 1
				If num > Strings.Len(str_Renamed) Then
					If flag2 Then
						Fields(num3) = New String("0"c, 50 - Strings.Len(Fields(num3))) + Fields(num3)
					End If
					flag = True
				Else
					text = Strings.Mid(str_Renamed, num, 1)
				End If
			Loop While Not flag
		End Sub

		' Token: 0x06000ED6 RID: 3798 RVA: 0x00095B7C File Offset: 0x00093D7C
		Private Function CreateSortTags() As Object
			modSort.SortTags(39) = 1S
			modSort.SortTags(45) = 2S
			modSort.SortTags(59) = 3S
			modSort.SortTags(94) = 4S
			modSort.SortTags(95) = 5S
			modSort.SortTags(96) = 6S
			modSort.SortTags(Strings.Asc("´")) = 7S
			modSort.SortTags(61) = 8S
			modSort.SortTags(Strings.Asc("°")) = 9S
			modSort.SortTags(32) = 0S
			Dim num As Short = 65S
			Do
				modSort.SortTags(CInt(num)) = num
				num += 1S
			Loop While num <= 90S
			num = 97S
			Do
				modSort.SortTags(CInt(num)) = num
				num += 1S
			Loop While num <= 122S
			num = 48S
			Do
				modSort.SortTags(CInt(num)) = num
				num += 1S
			Loop While num <= 57S
			Dim result As Object
			Return result
		End Function

		' Token: 0x06000ED7 RID: 3799 RVA: 0x00095C34 File Offset: 0x00093E34
		Private Function StrCmp(ByRef a As String, ByRef b As String) As Short
			Dim num2 As Short
			Dim num3 As Short
			Dim num As Short = CShort(Strings.Len(a))
			If CInt(num) > Strings.Len(b) Then
				num = CShort(Strings.Len(b))
			End If
			num2 = num
			num3 = 1S
			Dim result As Short
			While num3 <= num2
				If modSort.SortTags(Strings.Asc(Strings.Mid(a, CInt(num3), 1))) > modSort.SortTags(Strings.Asc(Strings.Mid(b, CInt(num3), 1))) Then
					result = 1S
				Else
					If modSort.SortTags(Strings.Asc(Strings.Mid(a, CInt(num3), 1))) >= modSort.SortTags(Strings.Asc(Strings.Mid(b, CInt(num3), 1))) Then
						num3 += 1S
						Continue While
					End If
					result = -1S
				End If
				Return result
			End While
			If Strings.Len(a) = Strings.Len(b) Then
				result = 0S
			End If
			If Strings.Len(a) > Strings.Len(b) Then
				result = 1S
			End If
			If Strings.Len(a) < Strings.Len(b) Then
				Return -1S
			End If
			Return result
		End Function

		' Token: 0x040008F4 RID: 2292
		Private SortTags As Short() = New Short(256) {}

		' Token: 0x0200010D RID: 269
		Public Enum SortStyles
			' Token: 0x04000AC7 RID: 2759
			StyleXP = 1
			' Token: 0x04000AC8 RID: 2760
			Style2000
			' Token: 0x04000AC9 RID: 2761
			StyleExplorer
		End Enum
	End Module
End Namespace
