Imports System
Imports System.Diagnostics
Imports System.Runtime.CompilerServices
Imports System.Runtime.InteropServices
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000047 RID: 71
	Friend NotInheritable Module modMonitorTest
		' Token: 0x06000E8D RID: 3725
		Public Declare Ansi Function ShellExecute Lib "shell32.dll" Alias "ShellExecuteA" (hwnd As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpOperation As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFile As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpParameters As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpDirectory As String, nShowCmd As Integer) As Integer

		' Token: 0x06000E8E RID: 3726
		Public Declare Ansi Function WaitForSingleObject Lib "kernel32" (hHandle As Integer, dwMilliseconds As Integer) As Integer

		' Token: 0x06000E8F RID: 3727
		Public Declare Ansi Function CreateProcessA Lib "kernel32" (lpApplicationName As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpCommandLine As String, lpProcessAttributes As Integer, lpThreadAttributes As Integer, bInheritHandles As Integer, dwCreationFlags As Integer, lpEnvironment As Integer, lpCurrentDirectory As Integer, ByRef lpStartupInfo As modMonitorTest.STARTUPINFO, ByRef lpProcessInformation As modMonitorTest.PROCESS_INFORMATION) As Integer

		' Token: 0x06000E90 RID: 3728
		Public Declare Ansi Function CreateProcessW Lib "kernel32" (lpApplicationName As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpCommandLine As String, lpProcessAttributes As Integer, lpThreadAttributes As Integer, bInheritHandles As Integer, dwCreationFlags As Integer, lpEnvironment As Integer, lpCurrentDirectory As Integer, ByRef lpStartupInfo As modMonitorTest.STARTUPINFO, ByRef lpProcessInformation As modMonitorTest.PROCESS_INFORMATION) As Integer

		' Token: 0x06000E91 RID: 3729
		Public Declare Ansi Function CloseHandle Lib "kernel32" (hObject As Integer) As Integer

		' Token: 0x06000E92 RID: 3730
		Public Declare Ansi Function GetExitCodeProcess Lib "kernel32" (hProcess As Integer, ByRef lpExitCode As Integer) As Integer

		' Token: 0x06000E93 RID: 3731 RVA: 0x00092064 File Offset: 0x00090264
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Function TestMonitor() As Boolean
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim result As Boolean = True
			If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\MonitorTest.Exe", FileAttribute.Normal), "", False) <> 0 Then
				Dim str As String = MyProject.Application.Info.DirectoryPath + "\MonitorTest.Exe"
				Dim num As Integer = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "FILMMONITORPIXEL_WIDTH"))))
				If num = 0 Then
					Dim text2 As String = "Missing parameter: FILMMONITORPIXEL_WIDTH" & vbCr & "For the Monitor Test you need to set up the fields FILMMONITORPIXEL_WIDTH and FILMMONITORPIXEL_HEIGHT in the [SYSTEM]-Section!"
					Dim num2 As Short = 0S
					Dim text3 As String = "file-converter"
					modMain.msgbox2(text2, num2, text3)
				Else
					Dim num3 As Integer = CInt(Math.Round(Conversion.Val("0" + modMain.GiveIni(text, "SYSTEM", "FILMMONITORPIXEL_HEIGHT"))))
					If num3 = 0 Then
						Dim text3 As String = "Missing parameter: FILMMONITORPIXEL_HEIGHT" & vbCr & "For the Monitor Test you need to set up the fields FILMMONITORPIXEL_WIDTH and FILMMONITORPIXEL_HEIGHT in the [SYSTEM]-Section!"
						Dim num2 As Short = 0S
						Dim text2 As String = "file-converter"
						modMain.msgbox2(text3, num2, text2)
					Else
						Dim str2 As String = Conversions.ToString(num) + " " + Conversions.ToString(num3)
						Dim text2 As String = str + " " + str2
						If modMonitorTest.ExecCmd(text2) = 0 Then
							result = False
						End If
					End If
				End If
			End If
			Return result
		End Function

		' Token: 0x06000E94 RID: 3732 RVA: 0x000921A0 File Offset: 0x000903A0
		Public Function ExecCmd(ByRef cmdline As String) As Integer
			Dim startupinfo As modMonitorTest.STARTUPINFO
			startupinfo.cb = Strings.Len(startupinfo)
			startupinfo.wShowWindow = 0S
			startupinfo.dwFlags = 1
			Dim process_INFORMATION As modMonitorTest.PROCESS_INFORMATION
			Dim result As Integer = modMonitorTest.CreateProcessA(0, cmdline, 0, 0, 1, 32, 0, 0, startupinfo, process_INFORMATION)
			result = modMonitorTest.WaitForSingleObject(process_INFORMATION.hProcess, 500)
			modMonitorTest.GetExitCodeProcess(process_INFORMATION.hProcess, result)
			modMonitorTest.CloseHandle(process_INFORMATION.hThread)
			modMonitorTest.CloseHandle(process_INFORMATION.hProcess)
			Return result
		End Function

		' Token: 0x06000E95 RID: 3733 RVA: 0x00092224 File Offset: 0x00090424
		Public Function ExecCmdNoWait(ByRef cmdline As String) As Integer
			Dim startupinfo As modMonitorTest.STARTUPINFO
			startupinfo.cb = Strings.Len(startupinfo)
			startupinfo.wShowWindow = 0S
			startupinfo.dwFlags = 1
			Dim process_INFORMATION As modMonitorTest.PROCESS_INFORMATION
			Dim result As Integer = modMonitorTest.CreateProcessW(0, cmdline, 0, 0, 1, 32, 0, 0, startupinfo, process_INFORMATION)
			Dim num As Long = CLng(modDeclares.GetLastError())
			modMonitorTest.CloseHandle(process_INFORMATION.hThread)
			modMonitorTest.CloseHandle(process_INFORMATION.hProcess)
			Return result
		End Function

		' Token: 0x06000E96 RID: 3734 RVA: 0x00092288 File Offset: 0x00090488
		Public Function ExecCmdNoWait2(ByRef cmdline As String, ByRef args As String) As Integer
			Dim processStartInfo As ProcessStartInfo = New ProcessStartInfo()
			processStartInfo.FileName = cmdline
			processStartInfo.Arguments = args
			processStartInfo.RedirectStandardOutput = True
			processStartInfo.RedirectStandardError = True
			processStartInfo.UseShellExecute = False
			processStartInfo.CreateNoWindow = True
			modMonitorTest.processTemp = New Process()
			modMonitorTest.processTemp.StartInfo = processStartInfo
			modMonitorTest.processTemp.EnableRaisingEvents = True
			Try
				modMonitorTest.processTemp.Start()
			Catch ex As Exception
				Throw
			End Try
			Dim result As Integer
			Return result
		End Function

		' Token: 0x040008EC RID: 2284
		Public Const NORMAL_PRIORITY_CLASS As Integer = 32

		' Token: 0x040008ED RID: 2285
		Public Const CREATE_UNICODE_ENVIRONMENT As Integer = 1024

		' Token: 0x040008EE RID: 2286
		Public Const INFINITE As Short = -1S

		' Token: 0x040008EF RID: 2287
		Private processTemp As Process

		' Token: 0x0200010A RID: 266
		Public Structure STARTUPINFO
			' Token: 0x04000AA6 RID: 2726
			Public cb As Integer

			' Token: 0x04000AA7 RID: 2727
			Public lpReserved As String

			' Token: 0x04000AA8 RID: 2728
			Public lpDesktop As String

			' Token: 0x04000AA9 RID: 2729
			Public lpTitle As String

			' Token: 0x04000AAA RID: 2730
			Public dwX As Integer

			' Token: 0x04000AAB RID: 2731
			Public dwY As Integer

			' Token: 0x04000AAC RID: 2732
			Public dwXSize As Integer

			' Token: 0x04000AAD RID: 2733
			Public dwYSize As Integer

			' Token: 0x04000AAE RID: 2734
			Public dwXCountChars As Integer

			' Token: 0x04000AAF RID: 2735
			Public dwYCountChars As Integer

			' Token: 0x04000AB0 RID: 2736
			Public dwFillAttribute As Integer

			' Token: 0x04000AB1 RID: 2737
			Public dwFlags As Integer

			' Token: 0x04000AB2 RID: 2738
			Public wShowWindow As Short

			' Token: 0x04000AB3 RID: 2739
			Public cbReserved2 As Short

			' Token: 0x04000AB4 RID: 2740
			Public lpReserved2 As Integer

			' Token: 0x04000AB5 RID: 2741
			Public hStdInput As Integer

			' Token: 0x04000AB6 RID: 2742
			Public hStdOutput As Integer

			' Token: 0x04000AB7 RID: 2743
			Public hStdError As Integer
		End Structure

		' Token: 0x0200010B RID: 267
		Public Structure PROCESS_INFORMATION
			' Token: 0x04000AB8 RID: 2744
			Public hProcess As Integer

			' Token: 0x04000AB9 RID: 2745
			Public hThread As Integer

			' Token: 0x04000ABA RID: 2746
			Public dwProcessID As Integer

			' Token: 0x04000ABB RID: 2747
			Public dwThreadID As Integer
		End Structure
	End Module
End Namespace
