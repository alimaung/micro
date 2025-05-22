Imports System
Imports System.Runtime.InteropServices
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200004A RID: 74
	Friend NotInheritable Module modProceses
		' Token: 0x06000EB4 RID: 3764
		Public Declare Ansi Function CreateToolhelp32Snapshot Lib "kernel32.dll" (dwFlags As Integer, th32ProcessID As Integer) As Integer

		' Token: 0x06000EB5 RID: 3765
		Public Declare Ansi Function Process32First Lib "kernel32.dll" (hSnapshot As Integer, ByRef lppe As modProceses.PROCESSENTRY32) As Integer

		' Token: 0x06000EB6 RID: 3766
		Public Declare Ansi Function Process32Next Lib "kernel32.dll" (hSnapshot As Integer, ByRef lppe As modProceses.PROCESSENTRY32) As Integer

		' Token: 0x06000EB7 RID: 3767 RVA: 0x00094C24 File Offset: 0x00092E24
		Public Sub KillOwnProcesses()
			Dim num As Integer = modProceses.CreateToolhelp32Snapshot(2, 0)
			Dim processentry As modProceses.PROCESSENTRY32
			processentry.dwSize = Strings.Len(processentry)
			Dim num2 As Integer = modProceses.Process32First(num, processentry)
			If num = -1 Then
				Return
			End If
			While num2 <> 0
				' The following expression was wrapped in a checked-expression
				If Operators.CompareString(Strings.Left(Strings.Left(New String(processentry.szExeFile), Strings.InStr(New String(processentry.szExeFile), vbNullChar, CompareMethod.Binary) - 1), 4), "file", False) = 0 Then
					Interaction.Shell("taskkill /F /T /PID " + Conversions.ToString(processentry.th32ProcessID), AppWinStyle.MinimizedFocus, False, -1)
				End If
				processentry.dwSize = Strings.Len(processentry)
				num2 = modProceses.Process32Next(num, processentry)
			End While
			modDeclares.CloseHandle(num)
		End Sub

		' Token: 0x040008F3 RID: 2291
		Public Const TH32CS_SNAPPROCESS As Integer = 2

		' Token: 0x0200010C RID: 268
		Public Structure PROCESSENTRY32
			' Token: 0x04000ABC RID: 2748
			Public dwSize As Integer

			' Token: 0x04000ABD RID: 2749
			Public cntUsage As Integer

			' Token: 0x04000ABE RID: 2750
			Public th32ProcessID As Integer

			' Token: 0x04000ABF RID: 2751
			Public th32DefaultHeapID As Integer

			' Token: 0x04000AC0 RID: 2752
			Public th32ModuleID As Integer

			' Token: 0x04000AC1 RID: 2753
			Public cntThreads As Integer

			' Token: 0x04000AC2 RID: 2754
			Public th32ParentProcessID As Integer

			' Token: 0x04000AC3 RID: 2755
			Public pcPriClassBase As Integer

			' Token: 0x04000AC4 RID: 2756
			Public dwFlags As Integer

			' Token: 0x04000AC5 RID: 2757
			<VBFixedString(260)>
			<MarshalAs(UnmanagedType.ByValArray, SizeConst := 260)>
			Public szExeFile As Char()
		End Structure
	End Module
End Namespace
