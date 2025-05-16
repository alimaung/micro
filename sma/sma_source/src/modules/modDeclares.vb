Imports System
Imports System.Drawing
Imports System.Runtime.InteropServices
Imports System.Runtime.InteropServices.ComTypes
Imports System.Text
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000043 RID: 67
	Friend NotInheritable Module modDeclares
		' Token: 0x06000D8C RID: 3468
		Public Declare Unicode Function WritePrivateProfileString Lib "kernel32" (lpAppName As String, lpKeyName As String, lpString As String, lpFileName As String) As Boolean

		' Token: 0x06000D8D RID: 3469
		Public Declare Unicode Function WritePrivateProfileStringW Lib "kernel32" (lpAppName As String, lpKeyName As String, lpString As String, lpFileName As String) As Boolean

		' Token: 0x06000D8E RID: 3470
		Public Declare Unicode Function GetPrivateProfileStringW Lib "kernel32" (lpAppName As String, lpKeyName As String, lpDefault As String, lpReturnedString As StringBuilder, nSize As Integer, lpFileName As String) As Integer

		' Token: 0x06000D8F RID: 3471
		Public Declare Unicode Function GetPrivateProfileString Lib "kernel32" (lpAppName As String, lpKeyName As String, lpDefault As String, lpReturnedString As StringBuilder, nSize As Integer, lpFileName As String) As Integer

		' Token: 0x06000D90 RID: 3472
		Public Declare Ansi Function GetTickCount Lib "kernel32" () As Integer

		' Token: 0x06000D91 RID: 3473
		Public Declare Ansi Sub OutputDebugString Lib "kernel32" Alias "OutputDebugStringA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpOutputString As String)

		' Token: 0x06000D92 RID: 3474
		Public Declare Ansi Function IG_palette_get Lib "gearpd.DLL" (hIGear As Integer, ByRef Palette As modDeclares.AT_RGBQUAD) As Integer

		' Token: 0x06000D93 RID: 3475
		Public Declare Ansi Function IG_palette_load Lib "gearpd.DLL" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef FileName As String, ByRef Palette As modDeclares.AT_RGBQUAD, ByRef NumberOfEntries As Integer, ByRef ColorOrder As Integer, ByRef FileType As Integer) As Integer

		' Token: 0x06000D94 RID: 3476
		Public Declare Ansi Function IG_palette_save Lib "gearpd.DLL" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef FileName As String, ByRef Palette As modDeclares.AT_RGBQUAD, NumberOfEntries As Integer, FileType As Integer) As Integer

		' Token: 0x06000D95 RID: 3477
		Public Declare Ansi Function IG_palette_set Lib "gearpd.DLL" (hIGear As Integer, ByRef Palette As modDeclares.AT_RGBQUAD) As Integer

		' Token: 0x06000D96 RID: 3478
		Public Declare Ansi Function IG_image_DIB_palette_pntr_get Lib "gearpd.DLL" (hIGear As Integer, ByRef RGBQuadArray As Integer, ByRef NumberOfEntries As Integer) As Integer

		' Token: 0x06000D97 RID: 3479
		Public Declare Ansi Function IG_IP_merge Lib "gearpd.DLL" (hIGearDestination As Integer, hIGearSource As Integer, ByRef RectSource As modDeclares.AT_RECT, XPos As Integer, YPos As Integer, MergeOp As Integer) As Integer

		' Token: 0x06000D98 RID: 3480
		Public Declare Ansi Function IG_image_create_DIB Lib "gearpd.DLL" (Width As Integer, Height As Integer, BitsperPixel As Integer, DIBPointerValue As Integer, ByRef hIGear As Integer) As Integer

		' Token: 0x06000D99 RID: 3481
		Public Declare Ansi Function GetNumberOfLines Lib "GetInfos" () As Integer

		' Token: 0x06000D9A RID: 3482
		Public Declare Ansi Function GetEntry Lib "GetInfos" (line As Integer, pos As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef FileName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef PathName As String, GlobalFrameCounter As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef Entry As String, ByRef EntryLen As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef err_Renamed As String) As Integer

		' Token: 0x06000D9B RID: 3483
		Public Declare Ansi Function FillRect Lib "user32" (hdc As Integer, ByRef lpRect As modDeclares.RECT, hBrush As Integer) As Integer

		' Token: 0x06000D9C RID: 3484
		Public Declare Ansi Function TileWindows Lib "user32" (hwndParent As Integer, wHow As Integer, ByRef lpRect As modDeclares.RECT, cKids As Integer, ByRef lpKids As Integer) As Short

		' Token: 0x06000D9D RID: 3485
		Public Declare Ansi Function IG_image_DIB_bitmap_pntr_get Lib "GEAR32PD.DLL" (hIGear As Integer, ByRef PixelArray As Integer) As Integer

		' Token: 0x06000D9E RID: 3486
		Public Declare Ansi Function IG_load_file Lib "gearpd" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, ByRef handle As Integer) As Integer

		' Token: 0x06000D9F RID: 3487
		Public Declare Ansi Function IG_save_file Lib "gearpd" (hdl As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, typ As Integer) As Integer

		' Token: 0x06000DA0 RID: 3488
		Public Declare Ansi Function IG_load_FD Lib "gearpd" (fd As Integer, offset As Integer, page As Integer, dummy As Integer, ByRef handle As Integer) As Integer

		' Token: 0x06000DA1 RID: 3489
		Public Declare Ansi Function IG_image_dimensions_get Lib "gearpd" (handle As Integer, ByRef Width As Integer, ByRef Height As Integer, ByRef fp As Integer) As Integer

		' Token: 0x06000DA2 RID: 3490
		Public Declare Ansi Function IG_display_angle_set Lib "gearpd" (handle As Integer, w As Integer) As Integer

		' Token: 0x06000DA3 RID: 3491
		Public Declare Ansi Function IG_IP_rotate_multiple_90 Lib "gearpd" (handle As Integer, h As Integer) As Integer

		' Token: 0x06000DA4 RID: 3492
		Public Declare Ansi Function IG_device_rect_get Lib "gearpd" (handle As Integer, ByRef r As modDeclares.RECT) As Integer

		' Token: 0x06000DA5 RID: 3493
		Public Declare Ansi Function IG_image_is_valid Lib "gearpd" (handle As Integer) As Integer

		' Token: 0x06000DA6 RID: 3494
		Public Declare Ansi Function IG_image_delete Lib "gearpd" (handle As Integer) As Integer

		' Token: 0x06000DA7 RID: 3495
		Public Declare Ansi Function IG_image_resolution_get Lib "gearpd" (handle As Integer, ByRef lpXResNumerator As Integer, ByRef lpXResDenominator As Integer, ByRef lpYResNumerator As Integer, ByRef lpYResDenominator As Integer, ByRef lpUnits As Integer) As Integer

		' Token: 0x06000DA8 RID: 3496
		Public Declare Ansi Function IG_image_resolution_set Lib "gearpd" (handle As Integer, lpXResNumerator As Integer, lpXResDenominator As Integer, lpYResNumerator As Integer, lpYResDenominator As Integer, lpUnits As Integer) As Integer

		' Token: 0x06000DA9 RID: 3497
		Public Declare Ansi Function IG_IP_resize Lib "gearpd" (hIGear As Integer, new_width As Integer, new_height As Integer, interpolation As Integer) As Integer

		' Token: 0x06000DAA RID: 3498
		Public Declare Ansi Function IG_page_count_get Lib "gearpd" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, ByRef lpPageCount As Integer) As Integer

		' Token: 0x06000DAB RID: 3499
		Public Declare Ansi Function IG_image_duplicate Lib "gearpd" (hIGear As Integer, ByRef newhandle As Integer) As Integer

		' Token: 0x06000DAC RID: 3500
		Public Declare Ansi Function IG_IP_convert_to_gray Lib "gearpd" (handle As Integer) As Integer

		' Token: 0x06000DAD RID: 3501
		Public Declare Ansi Function IG_info_get Lib "gearpd" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, ByRef FileType As Integer, ByRef Compression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer

		' Token: 0x06000DAE RID: 3502
		Public Declare Ansi Function IG_info_get_FD Lib "gearpd" (fd As Integer, lOffset As Integer, nPageNum As Integer, ByRef lpFileType As Integer, ByRef lpCompression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer

		' Token: 0x06000DAF RID: 3503
		Public Declare Ansi Function IG_IP_crop Lib "gearpd" (hIGear As Integer, ByRef RECT As modDeclares.RECT) As Integer

		' Token: 0x06000DB0 RID: 3504
		Public Declare Ansi Function IG_dspl_scroll_get Lib "gearpd" (hIGear As Integer, dwGrpID As Integer, hwnd As Integer, ByRef lpnScrollMode As Integer, ByRef lpScrollInfo As Integer) As Integer

		' Token: 0x06000DB1 RID: 3505
		Public Declare Ansi Function IG_dspl_scroll_set Lib "gearpd" (hIGear As Integer, dwGrpID As Integer, hwnd As Integer, lpnScrollMode As Integer, nXPage As Integer, nYPage As Integer, ByRef lpScrollInfo As Integer) As Integer

		' Token: 0x06000DB2 RID: 3506
		Public Declare Ansi Sub IG_error_get Lib "gearpd" (ErrorIndex As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef FileName As String, SizeOfFileName As Integer, ByRef LineNumber As Integer, ByRef ErrorCode As Integer, ByRef ValueOne As Integer, ByRef ValueTwo As Integer)

		' Token: 0x06000DB3 RID: 3507
		Public Declare Ansi Function IG_error_check Lib "gearpd" () As Integer

		' Token: 0x06000DB4 RID: 3508
		Public Declare Ansi Function IG_IP_color_promote Lib "gearpd" (handle As Integer, mode As Integer) As Integer

		' Token: 0x06000DB5 RID: 3509
		Public Declare Ansi Function ShowScrollBar Lib "user32" (hwnd As Integer, wBar As Integer, bShow As Integer) As Integer

		' Token: 0x06000DB6 RID: 3510
		Public Declare Ansi Function GetClientRect Lib "user32" (hwnd As Integer, ByRef lpRect As modDeclares.RECT) As Integer

		' Token: 0x06000DB7 RID: 3511
		Public Declare Ansi Function GetDC Lib "user32" (hwnd As Integer) As Integer

		' Token: 0x06000DB8 RID: 3512
		Public Declare Ansi Function SetWindowPos Lib "user32" (hwnd As Integer, hWndInsertAfter As Integer, X As Integer, y As Integer, cx As Integer, cy As Integer, wFlags As Integer) As Integer

		' Token: 0x06000DB9 RID: 3513
		Public Declare Ansi Function LocalAlloc Lib "kernel32" (wFlags As Integer, wBytes As Integer) As Integer

		' Token: 0x06000DBA RID: 3514
		Public Declare Ansi Function GetWindowRect Lib "user32" (hwnd As Integer, ByRef lpRect As modDeclares.RECT) As Integer

		' Token: 0x06000DBB RID: 3515
		Public Declare Ansi Function ScreenToClient Lib "user32" (hwnd As Integer, ByRef lpPoint As modDeclares.POINTAPI) As Integer

		' Token: 0x06000DBC RID: 3516
		Public Declare Ansi Sub Sleep Lib "kernel32" (dwMilliseconds As Integer)

		' Token: 0x06000DBD RID: 3517
		Public Declare Ansi Function GetVolumeInformation Lib "kernel32" Alias "GetVolumeInformationA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpRootPathName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpVolumeNameBuffer As String, nVolumeNameSize As Integer, ByRef lpVolumeSerialNumber As Integer, ByRef lpMaximumComponentLength As Integer, ByRef lpFileSystemFlags As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileSystemNameBuffer As String, nFileSystemNameSize As Integer) As Integer

		' Token: 0x06000DBE RID: 3518
		Public Declare Ansi Function GetLastError Lib "kernel32" () As Integer

		' Token: 0x06000DBF RID: 3519
		Public Declare Ansi Function GetDiskFreeSpace Lib "kernel32" Alias "GetDiskFreeSpaceA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpRootPathName As String, ByRef lpSectorsPerCluster As Integer, ByRef lpBytesPerSector As Integer, ByRef lpNumberOfFreeClusters As Integer, ByRef lpTotalNumberOfClusters As Integer) As Integer

		' Token: 0x06000DC0 RID: 3520
		Public Declare Ansi Function ShowCursor Lib "user32" (bShow As Integer) As Integer

		' Token: 0x06000DC1 RID: 3521
		Public Declare Ansi Function TextOut Lib "gdi32" Alias "TextOutA" (hdc As Integer, X As Integer, y As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpString As String, nCount As Integer) As Integer

		' Token: 0x06000DC2 RID: 3522
		Public Declare Ansi Function TextOutW Lib "gdi32" (hdc As Integer, X As Integer, y As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpString As String, nCount As Integer) As Integer

		' Token: 0x06000DC3 RID: 3523
		Public Declare Ansi Function LocalFree Lib "kernel32" (hMem As Integer) As Integer

		' Token: 0x06000DC4 RID: 3524
		Public Declare Ansi Function SetCursorPos Lib "user32" (X As Integer, y As Integer) As Integer

		' Token: 0x06000DC5 RID: 3525
		Public Declare Ansi Function lopen Lib "kernel32" Alias "_lopen" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpPathName As String, iReadWrite As Integer) As Integer

		' Token: 0x06000DC6 RID: 3526
		Public Declare Ansi Function lclose Lib "kernel32" Alias "_lclose" (fd As Integer) As Integer

		' Token: 0x06000DC7 RID: 3527
		Public Declare Ansi Function ClientToScreen Lib "user32" (hwnd As Integer, ByRef lpPoint As modDeclares.POINTAPI) As Integer

		' Token: 0x06000DC8 RID: 3528
		Public Declare Ansi Function GetComputerName Lib "kernel32" Alias "GetComputerNameA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpBuffer As String, ByRef nSize As Integer) As Integer

		' Token: 0x06000DC9 RID: 3529
		Public Declare Ansi Function GetUserName Lib "advapi32.dll" Alias "GetUserNameA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpBuffer As String, ByRef nSize As Integer) As Integer

		' Token: 0x06000DCA RID: 3530
		Public Declare Ansi Function GetTextExtentPoint32 Lib "gdi32" Alias "GetTextExtentPoint32A" (hdc As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpsz As String, cbString As Integer, ByRef lpSize As modDeclares.Size) As Integer

		' Token: 0x06000DCB RID: 3531
		Public Declare Ansi Function GetPrivateProfileStringA Lib "kernel32" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpApplicationName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpKeyName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpDefault As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpReturnedString As String, nSize As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String) As Integer

		' Token: 0x06000DCC RID: 3532
		Public Declare Ansi Function GetPrivateProfileSection Lib "kernel32" Alias "GetPrivateProfileSectionA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpAppName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpReturnedString As String, nSize As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String) As Integer

		' Token: 0x06000DCD RID: 3533
		Public Declare Ansi Function GetPrivateProfileInt Lib "kernel32" Alias "GetPrivateProfileIntA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpApplicationName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpKeyName As String, nDefault As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String) As Integer

		' Token: 0x06000DCE RID: 3534
		Public Declare Ansi Function WritePrivateProfileSection Lib "kernel32" Alias "WritePrivateProfileSectionA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpAppName As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpString As String, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String) As Integer

		' Token: 0x06000DCF RID: 3535
		Public Declare Ansi Function GlobalFree Lib "kernel32" (hMem As Integer) As Integer

		' Token: 0x06000DD0 RID: 3536
		Public Declare Ansi Function CreateFontIndirect Lib "gdi32" Alias "CreateFontIndirectA" (ByRef lpLogFont As modDeclares.LOGFONT) As Long

		' Token: 0x06000DD1 RID: 3537
		Public Declare Ansi Function SelectObject Lib "gdi32" (hdc As Long, hObject As Long) As Long

		' Token: 0x06000DD2 RID: 3538
		Public Declare Ansi Function DeleteObject Lib "gdi32" (hObject As Long) As Long

		' Token: 0x06000DD3 RID: 3539
		Public Declare Ansi Function GetDeviceCaps Lib "gdi32" (hdc As Long, nIndex As Long) As Long

		' Token: 0x06000DD4 RID: 3540
		Public Declare Ansi Function GetStockObject Lib "gdi32" (nIndex As Integer) As Integer

		' Token: 0x06000DD5 RID: 3541
		Public Declare Ansi Function timeGetTime Lib "winmm.dll" () As Integer

		' Token: 0x06000DD6 RID: 3542
		Public Declare Ansi Function TestTIFF Lib "TIFFDLL" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef Datei As String, p1 As Integer, p2 As Integer) As Integer

		' Token: 0x06000DD7 RID: 3543
		Public Declare Ansi Function MulDiv Lib "kernel32" (nNumber As Integer, nNumerator As Integer, nDenominator As Integer) As Integer

		' Token: 0x06000DD8 RID: 3544
		Public Declare Ansi Function IG_dspl_layout_set Lib "gearpd" (handle As Integer, dwGrpID As Integer, nFlags As Integer, ByRef lpImageRect As modDeclares.RECT, ByRef lpDeviceRect As modDeclares.RECT, ByRef lpClipRect As modDeclares.RECT, nFitMode As Integer, nAlignMode As Integer, nAspectMode As Integer, dAspectValue As Double) As Integer

		' Token: 0x06000DD9 RID: 3545
		Public Declare Ansi Function IG_dspl_antialias_set Lib "gearpd" (handle As Integer, dwGrpID As Integer, nAliasFlags As Integer, nThreshold As Integer) As Integer

		' Token: 0x06000DDA RID: 3546
		Public Declare Ansi Function IG_dspl_image_draw Lib "gearpd" (hIGear As Integer, dwGrpID As Integer, hwnd As Integer, hdc As Integer, ByRef r As modDeclares.RECT) As Integer

		' Token: 0x06000DDB RID: 3547
		Public Declare Ansi Function IG_dspl_background_set Lib "gearpd" (handle As Integer, dwGrpID As Integer, mode As Integer, <MarshalAs(UnmanagedType.AnsiBStr)> ByRef color As String, brush As Long) As Integer

		' Token: 0x06000DDC RID: 3548
		Public Declare Ansi Function IG_IP_contrast_invert Lib "gearpd" (handle As Integer, r As Long, mode As Integer) As Integer

		' Token: 0x06000DDD RID: 3549
		Public Declare Ansi Function IG_dspl_orientation_set Lib "gearpd" (handle As Integer, grp As Integer, mode As Integer) As Integer

		' Token: 0x06000DDE RID: 3550
		Public Declare Ansi Sub PDFUnlock Lib "PegasusImaging.ActiveX.PdfXpress1.dll" Alias "UnlockControl" (pw1 As Integer, pw2 As Integer, pw3 As Integer, pw4 As Integer)

		' Token: 0x06000DDF RID: 3551
		Public Declare Ansi Sub ControlUnlock Lib "ImagXpr7" Alias "PS_Unlock" (pw1 As Integer, pw2 As Integer, pw3 As Integer, pw4 As Integer)

		' Token: 0x06000DE0 RID: 3552
		Public Declare Ansi Sub UnlockRuntime Lib "PegasusImaging.ActiveX.PdfXpress1.dll" Alias "UnlockControl" (pw1 As Integer, pw2 As Integer, pw3 As Integer, pw4 As Integer)

		' Token: 0x06000DE1 RID: 3553
		Public Declare Ansi Function CreatePen Lib "gdi32" (nPenStyle As Integer, nWidth As Integer, crColor As Integer) As Integer

		' Token: 0x06000DE2 RID: 3554
		Public Declare Ansi Function CreateBrushIndirect Lib "gdi32" (ByRef lpLogBrush As modDeclares.LOGBRUSH) As Integer

		' Token: 0x06000DE3 RID: 3555
		Public Declare Ansi Function Rectangle Lib "gdi32" (hdc As Integer, Left_Renamed As Integer, Top As Integer, Right_Renamed As Integer, Bottom As Integer) As Integer

		' Token: 0x06000DE4 RID: 3556
		Public Declare Ansi Function FindFirstFile Lib "kernel32" Alias "FindFirstFileA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String, ByRef lpFindFileData As modDeclares.WIN32_FIND_DATA) As Long

		' Token: 0x06000DE5 RID: 3557
		Public Declare Ansi Function FindNextFile Lib "kernel32.dll" Alias "FindNextFileA" (hFindFile As Long, ByRef lpFindFileData As modDeclares.WIN32_FIND_DATA) As Long

		' Token: 0x06000DE6 RID: 3558
		Public Declare Ansi Function FindFirstFileW Lib "kernel32" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String, ByRef lpFindFileData As modDeclares.WIN32_FIND_DATA) As Long

		' Token: 0x06000DE7 RID: 3559
		Public Declare Ansi Function FindNextFileW Lib "kernel32.dll" (hFindFile As Long, ByRef lpFindFileData As modDeclares.WIN32_FIND_DATA) As Long

		' Token: 0x06000DE8 RID: 3560
		Public Declare Ansi Function FindClose Lib "kernel32" (hFindFile As Long) As Integer

		' Token: 0x06000DE9 RID: 3561
		Public Declare Ansi Function GetFileTime Lib "kernel32.dll" (hFile As Integer, ByRef lpCreationTime As modDeclares.FILETIME, ByRef lpLastAccessTime As modDeclares.FILETIME, ByRef lpLastWriteTime As modDeclares.FILETIME) As Integer

		' Token: 0x06000DEA RID: 3562
		Public Declare Ansi Function CloseHandle Lib "kernel32" (hObject As Integer) As Integer

		' Token: 0x06000DEB RID: 3563
		Public Declare Ansi Function OpenFile Lib "kernel32" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String, ByRef lpReOpenBuff As modDeclares.OFSTRUCT, wStyle As Integer) As Integer

		' Token: 0x06000DEC RID: 3564
		Public Declare Ansi Function CreateFile Lib "kernel32" Alias "CreateFileA" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpFileName As String, dwDesiredAccess As Integer, dwShareMode As Integer, ByRef lpSecurityAttributes As modDeclares.SECURITY_ATTRIBUTES, dwCreationDisposition As Integer, dwFlagsAndAttributes As Integer, hTemplateFile As Integer) As Integer

		' Token: 0x06000DED RID: 3565
		Public Declare Ansi Function CompareFileTime Lib "kernel32" (ByRef lpFileTime1 As modDeclares.FILETIME, ByRef lpFileTime2 As modDeclares.FILETIME) As Integer

		' Token: 0x06000DEE RID: 3566
		Public Declare Ansi Function SetTextAlign Lib "gdi32" (hdc As Integer, wFlags As Integer) As Integer

		' Token: 0x06000DEF RID: 3567
		Public Declare Ansi Function HeapAlloc Lib "kernel32" (hHeap As Integer, dwFlags As Integer, dwBytes As Integer) As Integer

		' Token: 0x06000DF0 RID: 3568
		Public Declare Ansi Function GetProcessHeap Lib "kernel32" () As Integer

		' Token: 0x06000DF1 RID: 3569
		Public Declare Ansi Function HeapFree Lib "kernel32" (hHeap As Integer, dwFlags As Integer, ByRef lpMem As Long) As Integer

		' Token: 0x06000DF2 RID: 3570
		Public Declare Ansi Function HeapCreate Lib "kernel32" (flOptions As Integer, dwInitialSize As Integer, dwMaximumSize As Integer) As Integer

		' Token: 0x06000DF3 RID: 3571
		Public Declare Ansi Function HeapDestroy Lib "kernel32" (hHeap As Integer) As Integer

		' Token: 0x06000DF4 RID: 3572
		Public Declare Ansi Function HeapCompact Lib "kernel32" (hHeap As Integer, dwFlags As Integer) As Integer

		' Token: 0x06000DF5 RID: 3573
		Public Declare Ansi Function IG_dspl_image_calc Lib "igcore16d.dll" (handle As Integer, dwGrpID As Integer, hwnd As Integer, hdc As Integer, ByRef r As modDeclares.AT_RECT) As Integer

		' Token: 0x06000DF6 RID: 3574
		Public Declare Ansi Function IG_load_fileN Lib "igcore16d.dll" Alias "IG_load_file" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, ByRef handle As Integer) As Integer

		' Token: 0x06000DF7 RID: 3575
		Public Declare Ansi Sub IG_error_getN Lib "igcore16d.dll" Alias "IG_error_get" (ErrorIndex As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef FileName As String, SizeOfFileName As Integer, ByRef LineNumber As Integer, ByRef ErrorCode As Integer, ByRef ValueOne As Integer, ByRef ValueTwo As Integer)

		' Token: 0x06000DF8 RID: 3576
		Public Declare Ansi Function IG_lic_solution_name_set Lib "igcore16d.dll" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpSolutionName As String) As Integer

		' Token: 0x06000DF9 RID: 3577
		Public Declare Ansi Function IG_IP_contrast_invertN Lib "igcore16d.dll" Alias "IG_IP_contrast_invert" (handle As Integer, r As Long, mode As Integer) As Integer

		' Token: 0x06000DFA RID: 3578
		Public Declare Ansi Function IG_IP_rotate_multiple_90N Lib "igcore16d.dll" Alias "IG_IP_rotate_multiple_90" (handle As Integer, h As Integer) As Integer

		' Token: 0x06000DFB RID: 3579
		Public Declare Ansi Function IG_image_dimensions_getN Lib "igcore16d.dll" Alias "IG_image_dimensions_get" (handle As Integer, ByRef Width As Integer, ByRef Height As Integer, ByRef fp As Integer) As Integer

		' Token: 0x06000DFC RID: 3580
		Public Declare Ansi Function IG_image_deleteN Lib "igcore16d.dll" Alias "IG_image_delete" (handle As Integer) As Integer

		' Token: 0x06000DFD RID: 3581
		Public Declare Ansi Function IG_save_fileN Lib "igcore16d.dll" Alias "IG_save_file" (hdl As Integer, <MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, typ As Integer) As Integer

		' Token: 0x06000DFE RID: 3582
		Public Declare Ansi Function IG_IP_resizeN Lib "igcore16d.dll" Alias "IG_IP_resize" (hIGear As Integer, new_width As Integer, new_height As Integer, interpolation As Integer) As Integer

		' Token: 0x06000DFF RID: 3583
		Public Declare Ansi Function IG_error_checkN Lib "igcore16d.dll" Alias "IG_error_check" () As Integer

		' Token: 0x06000E00 RID: 3584
		Public Declare Ansi Function IG_load_FDN Lib "igcore16d.dll" Alias "IG_load_FD" (fd As Integer, offset As Integer, page As Integer, dummy As Integer, ByRef handle As Integer) As Integer

		' Token: 0x06000E01 RID: 3585
		Public Declare Ansi Function IG_info_getN Lib "igcore16d.dll" Alias "IG_info_get" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef fname As String, ByRef FileType As Integer, ByRef Compression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer

		' Token: 0x06000E02 RID: 3586
		Public Declare Ansi Function IG_image_resolution_getN Lib "igcore16d.dll" Alias "IG_image_resolution_get" (handle As Integer, ByRef lpXResNumerator As Integer, ByRef lpXResDenominator As Integer, ByRef lpYResNumerator As Integer, ByRef lpYResDenominator As Integer, ByRef lpUnits As Integer) As Integer

		' Token: 0x06000E03 RID: 3587
		Public Declare Ansi Function IG_image_is_validN Lib "igcore16d.dll" Alias "IG_image_is_valid" (handle As Integer) As Integer

		' Token: 0x06000E04 RID: 3588
		Public Declare Ansi Function IG_dspl_layout_setN Lib "igcore16d.dll" Alias "IG_dspl_layout_set" (handle As Integer, dwGrpID As Integer, nFlags As Integer, ByRef r1 As modDeclares.RECT, ByRef r2 As modDeclares.RECT, ByRef r3 As modDeclares.RECT, nFitMode As Integer, nAlignMode As Integer, nAspectMode As Integer, dAspectValue As Double) As Integer

		' Token: 0x06000E05 RID: 3589
		Public Declare Ansi Function IG_dspl_image_drawN Lib "igcore16d.dll" Alias "IG_dspl_image_draw" (hIGear As Integer, dwGrpID As Integer, hwnd As Integer, hdc As Integer, ByRef r As modDeclares.RECT) As Integer

		' Token: 0x06000E06 RID: 3590
		Public Declare Ansi Function IG_dspl_background_setN Lib "igcore16d.dll" Alias "IG_dspl_background_set" (handle As Integer, dwGrpID As Integer, mode As Integer, ByRef color As Long, brush As Long) As Integer

		' Token: 0x06000E07 RID: 3591
		Public Declare Ansi Function IG_info_get_FDN Lib "igcore16d.dll" Alias "IG_dspl_background_set" (fd As Integer, lOffset As Integer, nPageNum As Integer, ByRef lpFileType As Integer, ByRef lpCompression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer

		' Token: 0x06000E08 RID: 3592
		Public Declare Ansi Function IG_IP_cropN Lib "igcore16d.dll" Alias "IG_IP_crop" (hIGear As Integer, ByRef RECT As modDeclares.RECT) As Integer

		' Token: 0x06000E09 RID: 3593
		Public Declare Ansi Function IG_lic_OEM_license_key_set Lib "igcore16d.dll" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpLicenseKey As String) As Integer

		' Token: 0x06000E0A RID: 3594
		Public Declare Ansi Function IG_lic_solution_key_set Lib "igcore16d.dll" (dwKey1 As Integer, dwKey2 As Integer, dwKey3 As Integer, dwKey4 As Integer) As Integer

		' Token: 0x06000E0B RID: 3595
		Public Declare Ansi Function IG_comm_comp_attach Lib "igcore16d.dll" (<MarshalAs(UnmanagedType.VBByRefStr)> ByRef lpCompName As String) As Integer

		' Token: 0x06000E0C RID: 3596 RVA: 0x0006FB90 File Offset: 0x0006DD90
		Public Function IG_load_fileD(fname As String, ByRef handle As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_load_fileN(fname, handle)
			Else
				result = modDeclares.IG_load_file(fname, handle)
			End If
			Return result
		End Function

		' Token: 0x06000E0D RID: 3597 RVA: 0x0006FBC0 File Offset: 0x0006DDC0
		Public Function IG_error_getD(ErrorIndex As Integer, FileName As String, SizeOfFileName As Integer, ByRef LineNumber As Integer, ByRef ErrorCode As Integer, ByRef ValueOne As Integer, ByRef ValueTwo As Integer) As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				modDeclares.IG_error_getN(ErrorIndex, FileName, SizeOfFileName, LineNumber, ErrorCode, ValueOne, ValueTwo)
			Else
				modDeclares.IG_error_get(ErrorIndex, FileName, SizeOfFileName, LineNumber, ErrorCode, ValueOne, ValueTwo)
			End If
			Dim result As Integer
			Return result
		End Function

		' Token: 0x06000E0E RID: 3598 RVA: 0x0006FBFC File Offset: 0x0006DDFC
		Public Function IG_IP_contrast_invertD(handle As Integer, ByRef r As Integer, mode As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_IP_contrast_invertN(handle, CLng(r), mode)
			Else
				result = modDeclares.IG_IP_contrast_invert(handle, CLng(r), mode)
			End If
			Return result
		End Function

		' Token: 0x06000E0F RID: 3599 RVA: 0x0006FC30 File Offset: 0x0006DE30
		Public Function IG_IP_rotate_multiple_90D(handle As Integer, h As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_IP_rotate_multiple_90N(handle, h)
			Else
				result = modDeclares.IG_IP_rotate_multiple_90(handle, h)
			End If
			Return result
		End Function

		' Token: 0x06000E10 RID: 3600 RVA: 0x0006FC5C File Offset: 0x0006DE5C
		Public Function IG_image_dimensions_getD(handle As Integer, ByRef Width As Integer, ByRef Height As Integer, ByRef fp As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_image_dimensions_getN(handle, Width, Height, fp)
			Else
				result = modDeclares.IG_image_dimensions_get(handle, Width, Height, fp)
			End If
			Return result
		End Function

		' Token: 0x06000E11 RID: 3601 RVA: 0x0006FC8C File Offset: 0x0006DE8C
		Public Function IG_image_deleteD(handle As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_image_deleteN(handle)
			Else
				result = modDeclares.IG_image_delete(handle)
			End If
			Return result
		End Function

		' Token: 0x06000E12 RID: 3602 RVA: 0x0006FCB8 File Offset: 0x0006DEB8
		Public Function IG_save_fileD(hdl As Integer, fname As String, typ As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_save_fileN(hdl, fname, typ)
			Else
				result = modDeclares.IG_save_file(hdl, fname, typ)
			End If
			Return result
		End Function

		' Token: 0x06000E13 RID: 3603 RVA: 0x0006FCE8 File Offset: 0x0006DEE8
		Public Function IG_IP_resizeD(hIGear As Integer, new_width As Integer, new_height As Integer, interpolation As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_IP_resizeN(hIGear, new_width, new_height, interpolation)
			Else
				result = modDeclares.IG_IP_resize(hIGear, new_width, new_height, interpolation)
			End If
			Return result
		End Function

		' Token: 0x06000E14 RID: 3604 RVA: 0x0006FD18 File Offset: 0x0006DF18
		Public Function IG_error_checkD() As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_error_checkN()
			Else
				result = modDeclares.IG_error_check()
			End If
			Return result
		End Function

		' Token: 0x06000E15 RID: 3605 RVA: 0x0006FD40 File Offset: 0x0006DF40
		Public Function IG_load_FDD(fd As Integer, offset As Integer, page As Integer, dummy As Integer, ByRef handle As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_load_FDN(fd, offset, page, dummy, handle)
			Else
				result = modDeclares.IG_load_FD(fd, offset, page, dummy, handle)
			End If
			Return result
		End Function

		' Token: 0x06000E16 RID: 3606 RVA: 0x0006FD74 File Offset: 0x0006DF74
		Public Function IG_info_getD(fname As String, ByRef FileType As Integer, ByRef Compression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_info_getN(fname, FileType, Compression, BITMAPINFOHEADER)
			Else
				result = modDeclares.IG_info_get(fname, FileType, Compression, BITMAPINFOHEADER)
			End If
			Return result
		End Function

		' Token: 0x06000E17 RID: 3607 RVA: 0x0006FDA8 File Offset: 0x0006DFA8
		Public Function IG_image_resolution_getD(handle As Integer, ByRef lpXResNumerator As Integer, ByRef lpXResDenominator As Integer, ByRef lpYResNumerator As Integer, ByRef lpYResDenominator As Integer, ByRef lpUnits As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_image_resolution_getN(handle, lpXResNumerator, lpXResDenominator, lpYResNumerator, lpYResDenominator, lpUnits)
			Else
				result = modDeclares.IG_image_resolution_get(handle, lpXResNumerator, lpXResDenominator, lpYResNumerator, lpYResDenominator, lpUnits)
			End If
			Return result
		End Function

		' Token: 0x06000E18 RID: 3608 RVA: 0x0006FDE0 File Offset: 0x0006DFE0
		Public Function IG_image_is_validD(handle As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_image_is_validN(handle)
			Else
				result = modDeclares.IG_image_is_valid(handle)
			End If
			Return result
		End Function

		' Token: 0x06000E19 RID: 3609 RVA: 0x0006FE0C File Offset: 0x0006E00C
		Public Function IG_dspl_layout_setD(handle As Integer, dwGrpID As Integer, nFlags As Integer, ByRef r1 As modDeclares.RECT, ByRef r2 As modDeclares.RECT, ByRef r3 As modDeclares.RECT, nFitMode As Integer, nAlignMode As Integer, nAspectMode As Integer, dAspectValue As Double) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_dspl_layout_setN(handle, dwGrpID, nFlags, r1, r2, r3, nFitMode, nAlignMode, nAspectMode, dAspectValue)
			Else
				result = modDeclares.IG_dspl_layout_set(handle, dwGrpID, nFlags, r1, r2, r3, nFitMode, nAlignMode, nAspectMode, dAspectValue)
			End If
			Return result
		End Function

		' Token: 0x06000E1A RID: 3610 RVA: 0x0006FE54 File Offset: 0x0006E054
		Public Function IG_dspl_image_drawD(hIGear As Integer, dwGrpID As Integer, hwnd As Integer, hdc As Integer, ByRef r As modDeclares.RECT) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_dspl_image_drawN(hIGear, dwGrpID, hwnd, hdc, r)
			Else
				result = modDeclares.IG_dspl_image_draw(hIGear, dwGrpID, hwnd, hdc, r)
			End If
			Return result
		End Function

		' Token: 0x06000E1B RID: 3611 RVA: 0x0006FE88 File Offset: 0x0006E088
		Public Function IG_dspl_background_setD(handle As Integer, dwGrpID As Integer, mode As Integer, ByRef color As Integer, brush As Integer) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				Dim num As Long = CLng(color)
				Dim num2 As Integer = modDeclares.IG_dspl_background_setN(handle, dwGrpID, mode, num, CLng(brush))
				color = CInt(num)
				result = num2
			Else
				Dim value As String = Conversions.ToString(color)
				Dim num3 As Integer = modDeclares.IG_dspl_background_set(handle, dwGrpID, mode, value, CLng(brush))
				color = Conversions.ToInteger(value)
				result = num3
			End If
			Return result
		End Function

		' Token: 0x06000E1C RID: 3612 RVA: 0x0006FED8 File Offset: 0x0006E0D8
		Public Function IG_info_get_FDD(fd As Integer, lOffset As Integer, nPageNum As Integer, ByRef lpFileType As Integer, ByRef lpCompression As Integer, ByRef BITMAPINFOHEADER As modDeclares.AT_DIB) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_info_get_FDN(fd, lOffset, nPageNum, lpFileType, lpCompression, BITMAPINFOHEADER)
			Else
				result = modDeclares.IG_info_get_FD(fd, lOffset, nPageNum, lpFileType, lpCompression, BITMAPINFOHEADER)
			End If
			Return result
		End Function

		' Token: 0x06000E1D RID: 3613 RVA: 0x0006FF10 File Offset: 0x0006E110
		Public Function IG_IP_cropD(hIGear As Integer, ByRef RECT As modDeclares.RECT) As Integer
			Dim result As Integer
			If modDeclares.SystemData.UseAccuv16 Then
				result = modDeclares.IG_IP_cropN(hIGear, RECT)
			Else
				result = modDeclares.IG_IP_crop(hIGear, RECT)
			End If
			Return result
		End Function

		' Token: 0x040007D7 RID: 2007
		Public Const FT_JPEG As Long = 0L

		' Token: 0x040007D8 RID: 2008
		Public Const FT_TIFF_G4 As Long = 1L

		' Token: 0x040007D9 RID: 2009
		Public Const FT_BMT As Long = 2L

		' Token: 0x040007DA RID: 2010
		Public Const FT_TIFF As Long = 3L

		' Token: 0x040007DB RID: 2011
		Public SaveFileName As String

		' Token: 0x040007DC RID: 2012
		Public SaveFileType As Long

		' Token: 0x040007DD RID: 2013
		Public issma16 As Boolean

		' Token: 0x040007DE RID: 2014
		Public frmImageXpress As frmImageXpress

		' Token: 0x040007DF RID: 2015
		Public ffrmFilmPreview As frmFilmPreview

		' Token: 0x040007E0 RID: 2016
		Public Const LOGPIXELSX As Short = 88S

		' Token: 0x040007E1 RID: 2017
		Public gCancelRefSearch As Boolean

		' Token: 0x040007E2 RID: 2018
		Public UseDebug As Boolean

		' Token: 0x040007E3 RID: 2019
		Public CalcModus As Boolean

		' Token: 0x040007E4 RID: 2020
		Public ShowLib As Boolean

		' Token: 0x040007E5 RID: 2021
		Public rcfrmSelectRoll As String

		' Token: 0x040007E6 RID: 2022
		Public film_faktor As Double

		' Token: 0x040007E7 RID: 2023
		Public Painted_Image_Width As Integer

		' Token: 0x040007E8 RID: 2024
		Public FilmingActive As Boolean

		' Token: 0x040007E9 RID: 2025
		Public MonDPI As Long

		' Token: 0x040007EA RID: 2026
		Public StandardDPI As Integer

		' Token: 0x040007EB RID: 2027
		Public Const IG_PROMOTE_TO_4 As Short = 1S

		' Token: 0x040007EC RID: 2028
		Public Const IG_PROMOTE_TO_8 As Short = 2S

		' Token: 0x040007ED RID: 2029
		Public Const IG_PROMOTE_TO_24 As Short = 3S

		' Token: 0x040007EE RID: 2030
		Public Const IG_PROMOTE_TO_32 As Short = 32S

		' Token: 0x040007EF RID: 2031
		Public Const IG_ARITH_OVER As Short = 10S

		' Token: 0x040007F0 RID: 2032
		Public SMCiAusgaenge As Integer() = New Integer(2) {}

		' Token: 0x040007F1 RID: 2033
		Public DisablePDFRenderImageDelete As Boolean = True

		' Token: 0x040007F2 RID: 2034
		Public StartFolder As String

		' Token: 0x040007F3 RID: 2035
		Public EndFolder As String

		' Token: 0x040007F4 RID: 2036
		Public BlockedMemory As Integer

		' Token: 0x040007F5 RID: 2037
		Public BlockedMemorySize As Integer

		' Token: 0x040007F6 RID: 2038
		Public Outputs As Integer

		' Token: 0x040007F7 RID: 2039
		Public MagnetValue As Integer

		' Token: 0x040007F8 RID: 2040
		Public IsSMA As Boolean

		' Token: 0x040007F9 RID: 2041
		Public SMAVersion As Short

		' Token: 0x040007FA RID: 2042
		Public IsSI As Boolean

		' Token: 0x040007FB RID: 2043
		Public NEWPROTOCOLHEADER As Boolean = False

		' Token: 0x040007FC RID: 2044
		Public Const VersionStaude As String = "file-converter 16/35"

		' Token: 0x040007FD RID: 2045
		Public Const VersionSMA As String = "SMA 51"

		' Token: 0x040007FE RID: 2046
		Public Const VersionSMA57 As String = "SMA 57"

		' Token: 0x040007FF RID: 2047
		Public Const VersionNr As String = "6.00.00-99 (12.02.2025)"

		' Token: 0x04000800 RID: 2048
		Public Version As String

		' Token: 0x04000801 RID: 2049
		Public ErrorInCore As Boolean

		' Token: 0x04000802 RID: 2050
		Public InCore As Boolean

		' Token: 0x04000803 RID: 2051
		Public MFCommError As Boolean

		' Token: 0x04000804 RID: 2052
		Public frmcomm As frmComm = New frmComm()

		' Token: 0x04000805 RID: 2053
		Public Blip1Counter As Integer = 0

		' Token: 0x04000806 RID: 2054
		Public Blip2Counter As Integer = 0

		' Token: 0x04000807 RID: 2055
		Public Blip3Counter As Integer = 0

		' Token: 0x04000808 RID: 2056
		Public glImage2 As Image

		' Token: 0x04000809 RID: 2057
		Public Const IG_DSPL_HSCROLLBAR_DISABLE As Short = 2S

		' Token: 0x0400080A RID: 2058
		Public Const IG_DSPL_VSCROLLBAR_DISABLE As Short = 512S

		' Token: 0x0400080B RID: 2059
		Public Const IG_FORMAT_UNKNOWN As Short = 0S

		' Token: 0x0400080C RID: 2060
		Public Const IG_FORMAT_ATT As Short = 1S

		' Token: 0x0400080D RID: 2061
		Public Const IG_FORMAT_BMP As Short = 2S

		' Token: 0x0400080E RID: 2062
		Public Const IG_FORMAT_BRK As Short = 3S

		' Token: 0x0400080F RID: 2063
		Public Const IG_FORMAT_CAL As Short = 4S

		' Token: 0x04000810 RID: 2064
		Public Const IG_FORMAT_CLP As Short = 5S

		' Token: 0x04000811 RID: 2065
		Public Const IG_FORMAT_CIF As Short = 6S

		' Token: 0x04000812 RID: 2066
		Public Const IG_FORMAT_CUT As Short = 7S

		' Token: 0x04000813 RID: 2067
		Public Const IG_FORMAT_DCX As Short = 8S

		' Token: 0x04000814 RID: 2068
		Public Const IG_FORMAT_DIB As Short = 9S

		' Token: 0x04000815 RID: 2069
		Public Const IG_FORMAT_EPS As Short = 10S

		' Token: 0x04000816 RID: 2070
		Public Const IG_FORMAT_G3 As Short = 11S

		' Token: 0x04000817 RID: 2071
		Public Const IG_FORMAT_G4 As Short = 12S

		' Token: 0x04000818 RID: 2072
		Public Const IG_FORMAT_GEM As Short = 13S

		' Token: 0x04000819 RID: 2073
		Public Const IG_FORMAT_GIF As Short = 14S

		' Token: 0x0400081A RID: 2074
		Public Const IG_FORMAT_GX2 As Short = 15S

		' Token: 0x0400081B RID: 2075
		Public Const IG_FORMAT_ICA As Short = 16S

		' Token: 0x0400081C RID: 2076
		Public Const IG_FORMAT_ICO As Short = 17S

		' Token: 0x0400081D RID: 2077
		Public Const IG_FORMAT_IFF As Short = 18S

		' Token: 0x0400081E RID: 2078
		Public Const IG_FORMAT_IGF As Short = 19S

		' Token: 0x0400081F RID: 2079
		Public Const IG_FORMAT_IMT As Short = 20S

		' Token: 0x04000820 RID: 2080
		Public Const IG_FORMAT_JPG As Short = 21S

		' Token: 0x04000821 RID: 2081
		Public Const IG_FORMAT_KFX As Short = 22S

		' Token: 0x04000822 RID: 2082
		Public Const IG_FORMAT_LV As Short = 23S

		' Token: 0x04000823 RID: 2083
		Public Const IG_FORMAT_MAC As Short = 24S

		' Token: 0x04000824 RID: 2084
		Public Const IG_FORMAT_MSP As Short = 25S

		' Token: 0x04000825 RID: 2085
		Public Const IG_FORMAT_MOD As Short = 26S

		' Token: 0x04000826 RID: 2086
		Public Const IG_FORMAT_NCR As Short = 27S

		' Token: 0x04000827 RID: 2087
		Public Const IG_FORMAT_PBM As Short = 28S

		' Token: 0x04000828 RID: 2088
		Public Const IG_FORMAT_PCD As Short = 29S

		' Token: 0x04000829 RID: 2089
		Public Const IG_FORMAT_PCT As Short = 30S

		' Token: 0x0400082A RID: 2090
		Public Const IG_FORMAT_PCX As Short = 31S

		' Token: 0x0400082B RID: 2091
		Public Const IG_FORMAT_PGM As Short = 32S

		' Token: 0x0400082C RID: 2092
		Public Const IG_FORMAT_PNG As Short = 33S

		' Token: 0x0400082D RID: 2093
		Public Const IG_FORMAT_PNM As Short = 34S

		' Token: 0x0400082E RID: 2094
		Public Const IG_FORMAT_PPM As Short = 35S

		' Token: 0x0400082F RID: 2095
		Public Const IG_FORMAT_PSD As Short = 36S

		' Token: 0x04000830 RID: 2096
		Public Const IG_FORMAT_RAS As Short = 37S

		' Token: 0x04000831 RID: 2097
		Public Const IG_FORMAT_SGI As Short = 38S

		' Token: 0x04000832 RID: 2098
		Public Const IG_FORMAT_TGA As Short = 39S

		' Token: 0x04000833 RID: 2099
		Public Const IG_FORMAT_TIF As Short = 40S

		' Token: 0x04000834 RID: 2100
		Public Const IG_FORMAT_TXT As Short = 41S

		' Token: 0x04000835 RID: 2101
		Public Const IG_FORMAT_WPG As Short = 42S

		' Token: 0x04000836 RID: 2102
		Public Const IG_FORMAT_XBM As Short = 43S

		' Token: 0x04000837 RID: 2103
		Public Const IG_FORMAT_WMF As Short = 44S

		' Token: 0x04000838 RID: 2104
		Public Const IG_FORMAT_XPM As Short = 45S

		' Token: 0x04000839 RID: 2105
		Public Const IG_FORMAT_XRX As Short = 46S

		' Token: 0x0400083A RID: 2106
		Public Const IG_FORMAT_XWD As Short = 47S

		' Token: 0x0400083B RID: 2107
		Public Const IG_FORMAT_DCM As Short = 48S

		' Token: 0x0400083C RID: 2108
		Public Const IG_FORMAT_AFX As Short = 49S

		' Token: 0x0400083D RID: 2109
		Public Const IG_FORMAT_FPX As Short = 50S

		' Token: 0x0400083E RID: 2110
		Public Const IG_FORMAT_PJPEG As Short = 21S

		' Token: 0x0400083F RID: 2111
		Public Const IG_FORMAT_AVI As Short = 52S

		' Token: 0x04000840 RID: 2112
		Public Const IG_FORMAT_G32D As Short = 53S

		' Token: 0x04000841 RID: 2113
		Public Const IG_FORMAT_ABIC_BILEVEL As Short = 54S

		' Token: 0x04000842 RID: 2114
		Public Const IG_FORMAT_ABIC_CONCAT As Short = 55S

		' Token: 0x04000843 RID: 2115
		Public Const IG_FORMAT_PDF As Short = 56S

		' Token: 0x04000844 RID: 2116
		Public Const IG_FORMAT_JBIG As Short = 57S

		' Token: 0x04000845 RID: 2117
		Public Const IG_FORMAT_RAW As Short = 58S

		' Token: 0x04000846 RID: 2118
		Public Const IG_FORMAT_IMR As Short = 59S

		' Token: 0x04000847 RID: 2119
		Public Const IG_FORMAT_STX As Short = 60S

		' Token: 0x04000848 RID: 2120
		Public Const IG_COMPRESSION_NONE As Short = 0S

		' Token: 0x04000849 RID: 2121
		Public Const IG_COMPRESSION_PACKED_BITS As Short = 1S

		' Token: 0x0400084A RID: 2122
		Public Const IG_COMPRESSION_HUFFMAN As Short = 2S

		' Token: 0x0400084B RID: 2123
		Public Const IG_COMPRESSION_CCITT_G3 As Short = 3S

		' Token: 0x0400084C RID: 2124
		Public Const IG_COMPRESSION_CCITT_G4 As Short = 4S

		' Token: 0x0400084D RID: 2125
		Public Const IG_COMPRESSION_CCITT_G32D As Short = 5S

		' Token: 0x0400084E RID: 2126
		Public Const IG_COMPRESSION_JPEG As Short = 6S

		' Token: 0x0400084F RID: 2127
		Public Const IG_COMPRESSION_RLE As Short = 7S

		' Token: 0x04000850 RID: 2128
		Public Const IG_COMPRESSION_LZW As Short = 8S

		' Token: 0x04000851 RID: 2129
		Public Const IG_COMPRESSION_ABIC_BW As Short = 9S

		' Token: 0x04000852 RID: 2130
		Public Const IG_COMPRESSION_ABIC_GRAY As Short = 10S

		' Token: 0x04000853 RID: 2131
		Public Const IG_COMPRESSION_JBIG As Short = 11S

		' Token: 0x04000854 RID: 2132
		Public Const IG_COMPRESSION_FPX_SINCOLOR As Short = 12S

		' Token: 0x04000855 RID: 2133
		Public Const IG_COMPRESSION_FPX_NOCHANGE As Short = 13S

		' Token: 0x04000856 RID: 2134
		Public Const IG_COMPRESSION_DEFLATE As Short = 14S

		' Token: 0x04000857 RID: 2135
		Public Const IG_COMPRESSION_IBM_MMR As Short = 15S

		' Token: 0x04000858 RID: 2136
		Public Const IG_COMPRESSION_ABIC As Short = 16S

		' Token: 0x04000859 RID: 2137
		Public Const IG_COMPRESSION_PROGRESSIVE As Short = 17S

		' Token: 0x0400085A RID: 2138
		Public Const IG_SAVE_TIF_G4 As Boolean = True

		' Token: 0x0400085B RID: 2139
		Public Const IG_SAVE_JPG As Short = 21S

		' Token: 0x0400085C RID: 2140
		Public UserName As String

		' Token: 0x0400085D RID: 2141
		Public UserLevel As Short

		' Token: 0x0400085E RID: 2142
		Public frmNewJob_Name As String

		' Token: 0x0400085F RID: 2143
		Public frmNewJob_kopf As String

		' Token: 0x04000860 RID: 2144
		Public JobParms As modDeclares.typJob

		' Token: 0x04000861 RID: 2145
		Public ExtCount As Integer

		' Token: 0x04000862 RID: 2146
		Public Extensions As String() = New String(100) {}

		' Token: 0x04000863 RID: 2147
		Public Const NoDebug As Boolean = False

		' Token: 0x04000864 RID: 2148
		Public StopExposing As Boolean

		' Token: 0x04000865 RID: 2149
		Public SelRaster As String

		' Token: 0x04000866 RID: 2150
		Public SelTitle As String

		' Token: 0x04000867 RID: 2151
		Public SelJob As String

		' Token: 0x04000868 RID: 2152
		Public mdlFktSelectedDirectory As String

		' Token: 0x04000869 RID: 2153
		Public mdlFktSelectedFile As String

		' Token: 0x0400086A RID: 2154
		Public mdlFktSelectedDirectories As String()

		' Token: 0x0400086B RID: 2155
		Public mdlFktSelectedDirectoriesCount As Integer

		' Token: 0x0400086C RID: 2156
		Public fs As Short

		' Token: 0x0400086D RID: 2157
		Public TitelDaten As String() = New String(6) {}

		' Token: 0x0400086E RID: 2158
		Public MsgReturn As Integer

		' Token: 0x0400086F RID: 2159
		Public MsgDefault As Integer

		' Token: 0x04000870 RID: 2160
		Public NoPaint As Boolean

		' Token: 0x04000871 RID: 2161
		Public RT As String

		' Token: 0x04000872 RID: 2162
		Public dbName As String

		' Token: 0x04000873 RID: 2163
		Public errstring As String

		' Token: 0x04000874 RID: 2164
		Public LastRelease As DateTime

		' Token: 0x04000875 RID: 2165
		Public TESTMODE As Boolean

		' Token: 0x04000876 RID: 2166
		Public GlobalFrame As Short

		' Token: 0x04000877 RID: 2167
		Public PasswordEntered As String

		' Token: 0x04000878 RID: 2168
		Public ALIAS_WERT As Short

		' Token: 0x04000879 RID: 2169
		Public g_nAspectRatio As Integer

		' Token: 0x0400087A RID: 2170
		Public g_fCenter As Integer

		' Token: 0x0400087B RID: 2171
		Public g_rcZoom As modDeclares.RECT

		' Token: 0x0400087C RID: 2172
		Public g_nZoomLevel As Integer

		' Token: 0x0400087D RID: 2173
		Public handle As Long

		' Token: 0x0400087E RID: 2174
		Public ImgFile As String

		' Token: 0x0400087F RID: 2175
		Public Const HWND_TOPMOST As Short = -1S

		' Token: 0x04000880 RID: 2176
		Public Const HWND_TOP As Short = 0S

		' Token: 0x04000881 RID: 2177
		Public Const SWP_NOMOVE As Integer = 2

		' Token: 0x04000882 RID: 2178
		Public Const SWP_NOSIZE As Integer = 1

		' Token: 0x04000883 RID: 2179
		Public Const SWP_NOZORDER As Integer = 4

		' Token: 0x04000884 RID: 2180
		Public glbInsertFilmCanceled As Boolean

		' Token: 0x04000885 RID: 2181
		Public SystemData As modDeclares.typSystem = Nothing

		' Token: 0x04000886 RID: 2182
		Public CurJob As modDeclares.typJob

		' Token: 0x04000887 RID: 2183
		Public Const LF_FACESIZE As Short = 32S

		' Token: 0x04000888 RID: 2184
		Public Const MDITILE_VERTICAL As Integer = 0

		' Token: 0x04000889 RID: 2185
		Public Const FW_NORMAL As Short = 400S

		' Token: 0x0400088A RID: 2186
		Public stoptest As Boolean

		' Token: 0x0400088B RID: 2187
		Public Const loadquality As Short = 40S

		' Token: 0x0400088C RID: 2188
		Public UseProzessor As Boolean

		' Token: 0x0400088D RID: 2189
		Public frmLogin_User As String

		' Token: 0x0400088E RID: 2190
		Public frmLogin_Pwd As String

		' Token: 0x0400088F RID: 2191
		Public frmLogin_Level As Short

		' Token: 0x04000890 RID: 2192
		Public frmEditLogin_Login As String

		' Token: 0x04000891 RID: 2193
		Public frmEditLogin_Pwd As String

		' Token: 0x04000892 RID: 2194
		Public frmEditLogin_Level As Short

		' Token: 0x04000893 RID: 2195
		Public finish As Boolean

		' Token: 0x04000894 RID: 2196
		Public imagecount As Integer

		' Token: 0x04000895 RID: 2197
		Public handles_Renamed As Integer() = New Integer(6) {}

		' Token: 0x04000896 RID: 2198
		Public DEMOVERSION As Boolean

		' Token: 0x04000897 RID: 2199
		Public vacuum_stop As Boolean

		' Token: 0x04000898 RID: 2200
		Public vacuum_cont As Boolean

		' Token: 0x04000899 RID: 2201
		Public vacuum_trailer As Boolean

		' Token: 0x0400089A RID: 2202
		Public UpdateIsDisabled As Boolean

		' Token: 0x0400089B RID: 2203
		Public NO_PREVIEW As Boolean

		' Token: 0x0400089C RID: 2204
		Public NoImageUpdate As Boolean = False

		' Token: 0x0400089D RID: 2205
		Public DoCancel As Boolean

		' Token: 0x0400089E RID: 2206
		Public Increment As Double

		' Token: 0x0400089F RID: 2207
		Public Sec_Width As Integer

		' Token: 0x040008A0 RID: 2208
		Public Sec_Height As Integer

		' Token: 0x040008A1 RID: 2209
		Public glbImagePath As String

		' Token: 0x040008A2 RID: 2210
		Public glbTemplate As String

		' Token: 0x040008A3 RID: 2211
		Public glbKopf As String

		' Token: 0x040008A4 RID: 2212
		Public glbOrientation As Boolean

		' Token: 0x040008A5 RID: 2213
		Public gllevel As Integer

		' Token: 0x040008A6 RID: 2214
		Public UseAccusoft As Boolean

		' Token: 0x040008A7 RID: 2215
		Public FW As String

		' Token: 0x040008A8 RID: 2216
		Public Images As modDeclares.typImage()

		' Token: 0x040008A9 RID: 2217
		Public Const MAX_PATH As Short = 260S

		' Token: 0x040008AA RID: 2218
		Public Const OFS_MAXPATHNAME As Short = 128S

		' Token: 0x040008AB RID: 2219
		Public Const OF_READ As Integer = 0

		' Token: 0x040008AC RID: 2220
		Public Const GENERIC_READ As Integer = -2147483648

		' Token: 0x040008AD RID: 2221
		Public Const OPEN_EXISTING As Short = 3S

		' Token: 0x040008AE RID: 2222
		Public Const FILE_ATTRIBUTE_NORMAL As Integer = 128

		' Token: 0x040008AF RID: 2223
		Public Const FILE_SHARE_READ As Integer = 1

		' Token: 0x040008B0 RID: 2224
		Public Const TA_BASELINE As Short = 24S

		' Token: 0x040008B1 RID: 2225
		Public Const TA_BOTTOM As Short = 8S

		' Token: 0x040008B2 RID: 2226
		Public Const TA_CENTER As Short = 6S

		' Token: 0x040008B3 RID: 2227
		Public Const TA_LEFT As Short = 0S

		' Token: 0x040008B4 RID: 2228
		Public Const TA_NOUPDATECP As Short = 0S

		' Token: 0x040008B5 RID: 2229
		Public Const TA_RIGHT As Short = 2S

		' Token: 0x040008B6 RID: 2230
		Public Const TA_TOP As Short = 0S

		' Token: 0x040008B7 RID: 2231
		Public Const TA_UPDATECP As Short = 1S

		' Token: 0x040008B8 RID: 2232
		Public Const TA_MASK As Decimal = 31D

		' Token: 0x020000F5 RID: 245
		Public Enum IsFileResults
			' Token: 0x04000935 RID: 2357
			FILE_IN_USE = -1
			' Token: 0x04000936 RID: 2358
			FILE_FREE
			' Token: 0x04000937 RID: 2359
			FILE_DOESNT_EXIST = -999
		End Enum

		' Token: 0x020000F6 RID: 246
		Public Structure AT_RGBQUAD
			' Token: 0x04000938 RID: 2360
			Public rgbBlue As Byte

			' Token: 0x04000939 RID: 2361
			Public rgbGreen As Byte

			' Token: 0x0400093A RID: 2362
			Public rgbRed As Byte

			' Token: 0x0400093B RID: 2363
			Public rgbReserved As Byte
		End Structure

		' Token: 0x020000F7 RID: 247
		Public Structure AT_RECT
			' Token: 0x0400093C RID: 2364
			Public Left_Renamed As Integer

			' Token: 0x0400093D RID: 2365
			Public Top As Integer

			' Token: 0x0400093E RID: 2366
			Public Right_Renamed As Integer

			' Token: 0x0400093F RID: 2367
			Public Bottom As Integer
		End Structure

		' Token: 0x020000F8 RID: 248
		Public Structure AT_DIB
			' Token: 0x04000940 RID: 2368
			Public biSize As Integer

			' Token: 0x04000941 RID: 2369
			Public biWidth As Integer

			' Token: 0x04000942 RID: 2370
			Public biHeight As Integer

			' Token: 0x04000943 RID: 2371
			Public biPlanes As Short

			' Token: 0x04000944 RID: 2372
			Public biBitCount As Short

			' Token: 0x04000945 RID: 2373
			Public biCompression As Integer

			' Token: 0x04000946 RID: 2374
			Public biSizeImage As Integer

			' Token: 0x04000947 RID: 2375
			Public biXPelsPerMeter As Integer

			' Token: 0x04000948 RID: 2376
			Public biYPelsPerMeter As Integer

			' Token: 0x04000949 RID: 2377
			Public biClrUsed As Integer

			' Token: 0x0400094A RID: 2378
			Public biClrImportant As Integer
		End Structure

		' Token: 0x020000F9 RID: 249
		Public Structure typLayout
			' Token: 0x06001206 RID: 4614 RVA: 0x000985B6 File Offset: 0x000967B6
			Public Sub Initialize()
				Me.ShowTitle = New Boolean(6) {}
				Me.LenTitle = New Integer(6) {}
				Me.RightTitel = New Boolean(6) {}
			End Sub

			' Token: 0x0400094B RID: 2379
			<VBFixedArray(6)>
			Public ShowTitle As Boolean()

			' Token: 0x0400094C RID: 2380
			<VBFixedArray(6)>
			Public LenTitle As Integer()

			' Token: 0x0400094D RID: 2381
			<VBFixedArray(6)>
			Public RightTitel As Boolean()

			' Token: 0x0400094E RID: 2382
			Public FicheNoLeadingZeros As Boolean

			' Token: 0x0400094F RID: 2383
			Public Year4Digits As Boolean

			' Token: 0x04000950 RID: 2384
			Public FicheNoPos As Short

			' Token: 0x04000951 RID: 2385
			Public DateNoPos As Short

			' Token: 0x04000952 RID: 2386
			Public UserPos As Short

			' Token: 0x04000953 RID: 2387
			Public ShowLogo As Boolean

			' Token: 0x04000954 RID: 2388
			Public LogoLeft As Boolean

			' Token: 0x04000955 RID: 2389
			Public FontSize As Short

			' Token: 0x04000956 RID: 2390
			Public FontWeight As Short

			' Token: 0x04000957 RID: 2391
			Public LogoBitmap As String
		End Structure

		' Token: 0x020000FA RID: 250
		Public Structure typFicheInfo
			' Token: 0x04000958 RID: 2392
			Public DocID As Integer

			' Token: 0x04000959 RID: 2393
			Public FileName As Integer
		End Structure

		' Token: 0x020000FB RID: 251
		Public Structure LOGBRUSH
			' Token: 0x0400095A RID: 2394
			Public lbStyle As Integer

			' Token: 0x0400095B RID: 2395
			Public lbColor As Integer

			' Token: 0x0400095C RID: 2396
			Public lbHatch As Integer
		End Structure

		' Token: 0x020000FC RID: 252
		Public Structure Size
			' Token: 0x0400095D RID: 2397
			Public cx As Integer

			' Token: 0x0400095E RID: 2398
			Public cy As Integer
		End Structure

		' Token: 0x020000FD RID: 253
		Public Structure RECT
			' Token: 0x0400095F RID: 2399
			Public Left_Renamed As Integer

			' Token: 0x04000960 RID: 2400
			Public Top As Integer

			' Token: 0x04000961 RID: 2401
			Public Right_Renamed As Integer

			' Token: 0x04000962 RID: 2402
			Public Bottom As Integer
		End Structure

		' Token: 0x020000FE RID: 254
		Public Structure POINTAPI
			' Token: 0x04000963 RID: 2403
			Public X As Integer

			' Token: 0x04000964 RID: 2404
			Public y As Integer
		End Structure

		' Token: 0x020000FF RID: 255
		Public Structure typRaster
			' Token: 0x04000965 RID: 2405
			Public Nr As String

			' Token: 0x04000966 RID: 2406
			Public Name As String

			' Token: 0x04000967 RID: 2407
			Public spalten As Short

			' Token: 0x04000968 RID: 2408
			Public zeilen As Short

			' Token: 0x04000969 RID: 2409
			Public Hoehe As Double

			' Token: 0x0400096A RID: 2410
			Public Breite As Double

			' Token: 0x0400096B RID: 2411
			Public DiaX As Double

			' Token: 0x0400096C RID: 2412
			Public DiaY As Double

			' Token: 0x0400096D RID: 2413
			Public TitleX As Double

			' Token: 0x0400096E RID: 2414
			Public TitleY As Double

			' Token: 0x0400096F RID: 2415
			Public TitleX2 As Double

			' Token: 0x04000970 RID: 2416
			Public TitleY2 As Double

			' Token: 0x04000971 RID: 2417
			Public TitleHeight As Double

			' Token: 0x04000972 RID: 2418
			Public FicheNrX As Double
		End Structure

		' Token: 0x02000100 RID: 256
		Public Structure typJob
			' Token: 0x06001207 RID: 4615 RVA: 0x000985DC File Offset: 0x000967DC
			Public Sub Initialize()
				Me.Title.Initialize()
			End Sub

			' Token: 0x04000973 RID: 2419
			Public Name As String

			' Token: 0x04000974 RID: 2420
			Public BatchPath As String

			' Token: 0x04000975 RID: 2421
			Public ImportPath As String

			' Token: 0x04000976 RID: 2422
			Public MaxBreite As Double

			' Token: 0x04000977 RID: 2423
			Public MaxHoehe As Double

			' Token: 0x04000978 RID: 2424
			Public Ausrichtung As Integer

			' Token: 0x04000979 RID: 2425
			Public Raster As modDeclares.typRaster

			' Token: 0x0400097A RID: 2426
			Public Title As modDeclares.typLayout

			' Token: 0x0400097B RID: 2427
			Public filter_Renamed As String

			' Token: 0x0400097C RID: 2428
			Public ColorConvert As Boolean

			' Token: 0x0400097D RID: 2429
			Public Invert As Boolean

			' Token: 0x0400097E RID: 2430
			Public Einzel As Boolean

			' Token: 0x0400097F RID: 2431
			Public blip As Boolean

			' Token: 0x04000980 RID: 2432
			Public BlipBreite As Integer

			' Token: 0x04000981 RID: 2433
			Public BlipHoehe As Integer

			' Token: 0x04000982 RID: 2434
			Public BLIPXPos As Integer

			' Token: 0x04000983 RID: 2435
			Public BLIPYPos As Integer

			' Token: 0x04000984 RID: 2436
			Public kopf As String
		End Structure

		' Token: 0x02000101 RID: 257
		Public Structure typASize
			' Token: 0x04000985 RID: 2437
			Public Desc As String

			' Token: 0x04000986 RID: 2438
			Public min As Double

			' Token: 0x04000987 RID: 2439
			Public max As Double

			' Token: 0x04000988 RID: 2440
			Public MonitorX As Double

			' Token: 0x04000989 RID: 2441
			Public MonitorY As Double
		End Structure

		' Token: 0x02000102 RID: 258
		Public Structure typSystem
			' Token: 0x06001208 RID: 4616 RVA: 0x000985EC File Offset: 0x000967EC
			Public Sub Initialize()
				Me.filmspeed = New Integer(4) {}
				Me.kopfname = New String(4) {}
				Me.schrittepromm = New Double(4) {}
				Me.schrittepropixel = New Double(4) {}
				Me.filmlaenge = New Integer(4) {}
				Me.restframe = New Integer(4) {}
				Me.portrait = New Boolean(4) {}
				Me.restaufnahmen = New Integer(4) {}
				Me.restaufnahmenLS = New Integer(4) {}
				Me.MonitorHeightOnFilm = New Double(4) {}
				Me.BelegeProFilm = New Integer(4) {}
				Me.BelegeVerfuegbar = New Integer(4) {}
				Me.Headers = New String(5) {}
				Me.Trailers = New String(8) {}
				Me.Records = New String(8) {}
				Me.HeadersSel = New Boolean(5) {}
				Me.TrailerSel = New Boolean(8) {}
				Me.RecordsSel = New Boolean(8) {}
				Me.FResolution = New Short(4) {}
				Me.ASizes = New modDeclares.typASize(5) {}
				Me.AddRollFrameLinePos = New Integer(4) {}
				Me.AddRollFrameLines = New String(4) {}
			End Sub

			' Token: 0x0400098A RID: 2442
			Public EXCELPROTOCOL As Boolean

			' Token: 0x0400098B RID: 2443
			Public FastMPTIFF As Boolean

			' Token: 0x0400098C RID: 2444
			Public MPTIFFTEMPPATH As String

			' Token: 0x0400098D RID: 2445
			Public DUPLEXPROCS As Long

			' Token: 0x0400098E RID: 2446
			Public VacuumOn As Integer

			' Token: 0x0400098F RID: 2447
			Public VacuumOff As Integer

			' Token: 0x04000990 RID: 2448
			Public AfterVacuumOff As Integer

			' Token: 0x04000991 RID: 2449
			Public AfterVacuumOn As Integer

			' Token: 0x04000992 RID: 2450
			Public VacuumOnDelay As Integer

			' Token: 0x04000993 RID: 2451
			<VBFixedArray(4)>
			Public filmspeed As Integer()

			' Token: 0x04000994 RID: 2452
			Public vorspann As Integer

			' Token: 0x04000995 RID: 2453
			Public nachspann As Integer

			' Token: 0x04000996 RID: 2454
			Public belichtung As Integer

			' Token: 0x04000997 RID: 2455
			Public nullpunkt As Integer

			' Token: 0x04000998 RID: 2456
			Public schlitze As Integer

			' Token: 0x04000999 RID: 2457
			Public umdrehung As Integer

			' Token: 0x0400099A RID: 2458
			<VBFixedArray(4)>
			Public kopfname As String()

			' Token: 0x0400099B RID: 2459
			Public schrittweite As Double

			' Token: 0x0400099C RID: 2460
			<VBFixedArray(4)>
			Public schrittepromm As Double()

			' Token: 0x0400099D RID: 2461
			<VBFixedArray(4)>
			Public schrittepropixel As Double()

			' Token: 0x0400099E RID: 2462
			<VBFixedArray(4)>
			Public filmlaenge As Integer()

			' Token: 0x0400099F RID: 2463
			<VBFixedArray(4)>
			Public restframe As Integer()

			' Token: 0x040009A0 RID: 2464
			Public verschlussgeschw As Integer

			' Token: 0x040009A1 RID: 2465
			Public zusatzbelichtung As Double

			' Token: 0x040009A2 RID: 2466
			<VBFixedArray(4)>
			Public portrait As Boolean()

			' Token: 0x040009A3 RID: 2467
			<VBFixedArray(4)>
			Public restaufnahmen As Integer()

			' Token: 0x040009A4 RID: 2468
			<VBFixedArray(4)>
			Public restaufnahmenLS As Integer()

			' Token: 0x040009A5 RID: 2469
			<VBFixedArray(4)>
			Public MonitorHeightOnFilm As Double()

			' Token: 0x040009A6 RID: 2470
			Public FesteBelegzahlProFilm As Boolean

			' Token: 0x040009A7 RID: 2471
			<VBFixedArray(4)>
			Public BelegeProFilm As Integer()

			' Token: 0x040009A8 RID: 2472
			<VBFixedArray(4)>
			Public BelegeVerfuegbar As Integer()

			' Token: 0x040009A9 RID: 2473
			Public Hoehe As Integer

			' Token: 0x040009AA RID: 2474
			Public Breite As Integer

			' Token: 0x040009AB RID: 2475
			Public X As Integer

			' Token: 0x040009AC RID: 2476
			Public y As Integer

			' Token: 0x040009AD RID: 2477
			Public BlipBreite As Integer

			' Token: 0x040009AE RID: 2478
			Public BlipHoehe As Integer

			' Token: 0x040009AF RID: 2479
			Public BlipX As Integer

			' Token: 0x040009B0 RID: 2480
			Public BlipY As Integer

			' Token: 0x040009B1 RID: 2481
			Public InfoBreite As Integer

			' Token: 0x040009B2 RID: 2482
			Public InfoHoehe As Integer

			' Token: 0x040009B3 RID: 2483
			Public InfoX As Integer

			' Token: 0x040009B4 RID: 2484
			Public InfoY As Integer

			' Token: 0x040009B5 RID: 2485
			Public AutoAlign As Boolean

			' Token: 0x040009B6 RID: 2486
			Public DoLeftAuto As Boolean

			' Token: 0x040009B7 RID: 2487
			Public FixRot As Short

			' Token: 0x040009B8 RID: 2488
			Public Blip1Size As Short

			' Token: 0x040009B9 RID: 2489
			Public Blip2Size As Short

			' Token: 0x040009BA RID: 2490
			Public Blip3Size As Short

			' Token: 0x040009BB RID: 2491
			Public AutoAlign180 As Boolean

			' Token: 0x040009BC RID: 2492
			Public UseAnno As Boolean

			' Token: 0x040009BD RID: 2493
			Public IgnoreChars As Boolean

			' Token: 0x040009BE RID: 2494
			Public IgnoreCharChount As Integer

			' Token: 0x040009BF RID: 2495
			Public AnnoOverBlip As Boolean

			' Token: 0x040009C0 RID: 2496
			Public AnnoStyle As Short

			' Token: 0x040009C1 RID: 2497
			Public AnnoBlipLen As Short

			' Token: 0x040009C2 RID: 2498
			Public Ausrichtung As Integer

			' Token: 0x040009C3 RID: 2499
			Public AnnoX As Integer

			' Token: 0x040009C4 RID: 2500
			Public AnnoY As Integer

			' Token: 0x040009C5 RID: 2501
			Public Font As Integer

			' Token: 0x040009C6 RID: 2502
			Public Gewicht As Integer

			' Token: 0x040009C7 RID: 2503
			Public InfoTextAusrichtung As Integer

			' Token: 0x040009C8 RID: 2504
			Public InfoTextX As Integer

			' Token: 0x040009C9 RID: 2505
			Public InfoTextY As Integer

			' Token: 0x040009CA RID: 2506
			Public InfoTextFont As Integer

			' Token: 0x040009CB RID: 2507
			Public InfoTextGewicht As Integer

			' Token: 0x040009CC RID: 2508
			Public InfoText As String

			' Token: 0x040009CD RID: 2509
			Public AnnoWinX As Integer

			' Token: 0x040009CE RID: 2510
			Public AnnoWinY As Integer

			' Token: 0x040009CF RID: 2511
			Public AnnoWinBreite As Integer

			' Token: 0x040009D0 RID: 2512
			Public AnnoWinHoehe As Integer

			' Token: 0x040009D1 RID: 2513
			Public MultiSep As String

			' Token: 0x040009D2 RID: 2514
			Public AnnoStart As Integer

			' Token: 0x040009D3 RID: 2515
			Public AnnoLen As Short

			' Token: 0x040009D4 RID: 2516
			Public AnnoPrefix As String

			' Token: 0x040009D5 RID: 2517
			Public AnnoLeadingZeros As Boolean

			' Token: 0x040009D6 RID: 2518
			Public Anno As String

			' Token: 0x040009D7 RID: 2519
			Public AnnoFontSize As Short

			' Token: 0x040009D8 RID: 2520
			Public ShowDocSize As Boolean

			' Token: 0x040009D9 RID: 2521
			Public DocSizeFormat As Short

			' Token: 0x040009DA RID: 2522
			Public UseBlip As Boolean

			' Token: 0x040009DB RID: 2523
			Public OnePagePDFs As Boolean

			' Token: 0x040009DC RID: 2524
			Public OnePageTIFFs As Boolean

			' Token: 0x040009DD RID: 2525
			Public BlipBreiteGross As Integer

			' Token: 0x040009DE RID: 2526
			Public BlipBreiteKlein As Integer

			' Token: 0x040009DF RID: 2527
			Public BlipBreiteMittel As Integer

			' Token: 0x040009E0 RID: 2528
			Public BlipHoeheGross As Integer

			' Token: 0x040009E1 RID: 2529
			Public BlipHoeheKlein As Integer

			' Token: 0x040009E2 RID: 2530
			Public BlipHoeheMittel As Integer

			' Token: 0x040009E3 RID: 2531
			Public StartBlipAtOne As Boolean

			' Token: 0x040009E4 RID: 2532
			Public UseStartFrame As Boolean

			' Token: 0x040009E5 RID: 2533
			Public UseEndFrame As Boolean

			' Token: 0x040009E6 RID: 2534
			Public UseSeparateFrame As Boolean

			' Token: 0x040009E7 RID: 2535
			Public UseFrameNo As Boolean

			' Token: 0x040009E8 RID: 2536
			Public Invers As Boolean

			' Token: 0x040009E9 RID: 2537
			Public UseFrame As Boolean

			' Token: 0x040009EA RID: 2538
			Public DoSplit As Boolean

			' Token: 0x040009EB RID: 2539
			Public SplitSizeX As Integer

			' Token: 0x040009EC RID: 2540
			Public SplitSizeY As Integer

			' Token: 0x040009ED RID: 2541
			Public SplitCount As Short

			' Token: 0x040009EE RID: 2542
			Public SplitOversize As Double

			' Token: 0x040009EF RID: 2543
			Public PDFReso As Integer

			' Token: 0x040009F0 RID: 2544
			Public StepsImageToImage As Boolean

			' Token: 0x040009F1 RID: 2545
			Public OneToOneExposure As Boolean

			' Token: 0x040009F2 RID: 2546
			Public Factor As Double

			' Token: 0x040009F3 RID: 2547
			Public Tolerance As Double

			' Token: 0x040009F4 RID: 2548
			Public SplitLicenseOK As Boolean

			' Token: 0x040009F5 RID: 2549
			Public HybridMode As Boolean

			' Token: 0x040009F6 RID: 2550
			Public FastColorExposure As Boolean

			' Token: 0x040009F7 RID: 2551
			Public UseLogFile As Boolean

			' Token: 0x040009F8 RID: 2552
			Public LogfileName As String

			' Token: 0x040009F9 RID: 2553
			Public Delimiter As String

			' Token: 0x040009FA RID: 2554
			<VBFixedArray(5)>
			Public Headers As String()

			' Token: 0x040009FB RID: 2555
			Public Trailers As String()

			' Token: 0x040009FC RID: 2556
			<VBFixedArray(8)>
			Public Records As String()

			' Token: 0x040009FD RID: 2557
			<VBFixedArray(5)>
			Public HeadersSel As Boolean()

			' Token: 0x040009FE RID: 2558
			Public TrailerSel As Boolean()

			' Token: 0x040009FF RID: 2559
			<VBFixedArray(8)>
			Public RecordsSel As Boolean()

			' Token: 0x04000A00 RID: 2560
			Public Autotrailer As Boolean

			' Token: 0x04000A01 RID: 2561
			Public AutoTrailerDistance As Double

			' Token: 0x04000A02 RID: 2562
			Public AutoTrailerLength As Double

			' Token: 0x04000A03 RID: 2563
			Public CheckVakuum As Boolean

			' Token: 0x04000A04 RID: 2564
			Public CheckFilmEnde As Boolean

			' Token: 0x04000A05 RID: 2565
			Public VResolution As Short

			' Token: 0x04000A06 RID: 2566
			<VBFixedArray(4)>
			Public FResolution As Short()

			' Token: 0x04000A07 RID: 2567
			Public TrailerInfoFrames As Boolean

			' Token: 0x04000A08 RID: 2568
			Public NoHead As Boolean

			' Token: 0x04000A09 RID: 2569
			Public UseUnicode As Boolean

			' Token: 0x04000A0A RID: 2570
			Public WaitAfterDraw As Integer

			' Token: 0x04000A0B RID: 2571
			Public MotorProt As Boolean

			' Token: 0x04000A0C RID: 2572
			Public UseAmericanSizes As Boolean

			' Token: 0x04000A0D RID: 2573
			<VBFixedArray(5)>
			Public ASizes As modDeclares.typASize()

			' Token: 0x04000A0E RID: 2574
			Public ShowWindowBorder As Boolean

			' Token: 0x04000A0F RID: 2575
			Public DoDirSort As Boolean

			' Token: 0x04000A10 RID: 2576
			Public Verschlussmotorgradzahl As Double

			' Token: 0x04000A11 RID: 2577
			Public BaendeVollstaendigBelichten As Boolean

			' Token: 0x04000A12 RID: 2578
			Public UseStartSymbole As Boolean

			' Token: 0x04000A13 RID: 2579
			Public UseEndSymbole As Boolean

			' Token: 0x04000A14 RID: 2580
			Public PfadStartSymbole As String

			' Token: 0x04000A15 RID: 2581
			Public PfadEndSymbole As String

			' Token: 0x04000A16 RID: 2582
			Public UseForsetzungsSymbole1 As Boolean

			' Token: 0x04000A17 RID: 2583
			Public UseForsetzungsSymbole2 As Boolean

			' Token: 0x04000A18 RID: 2584
			Public PfadForsetzungsSymbole1 As String

			' Token: 0x04000A19 RID: 2585
			Public PfadForsetzungsSymbole2 As String

			' Token: 0x04000A1A RID: 2586
			Public FortsetzungsLevel As Integer

			' Token: 0x04000A1B RID: 2587
			Public RollenNr As String

			' Token: 0x04000A1C RID: 2588
			Public kopfindex As Short

			' Token: 0x04000A1D RID: 2589
			Public RollenNrFont As Integer

			' Token: 0x04000A1E RID: 2590
			Public RollenNrPrefix As String

			' Token: 0x04000A1F RID: 2591
			Public RollenNrPostfix As String

			' Token: 0x04000A20 RID: 2592
			Public RollNoLen As Integer

			' Token: 0x04000A21 RID: 2593
			Public DoRepeatFrames As Boolean

			' Token: 0x04000A22 RID: 2594
			Public NumberOfRepetetionFrames As Integer

			' Token: 0x04000A23 RID: 2595
			Public NoSpecialSmybolesWhenContinuation As Boolean

			' Token: 0x04000A24 RID: 2596
			Public EnableInfoWindow As Boolean

			' Token: 0x04000A25 RID: 2597
			Public NumberOfInfoLines As Integer

			' Token: 0x04000A26 RID: 2598
			Public InfoLinesLeft As String()

			' Token: 0x04000A27 RID: 2599
			Public InfoLinesCenter As String()

			' Token: 0x04000A28 RID: 2600
			Public InfoLinesRight As String()

			' Token: 0x04000A29 RID: 2601
			Public EnableRollFrameExt As Boolean

			' Token: 0x04000A2A RID: 2602
			Public RollFrameExtOrientation As Integer

			' Token: 0x04000A2B RID: 2603
			Public RollFrameExtFontSize As Integer

			' Token: 0x04000A2C RID: 2604
			Public RollFrameExtLinePos1 As Integer

			' Token: 0x04000A2D RID: 2605
			Public RollFrameExtLinePos2 As Integer

			' Token: 0x04000A2E RID: 2606
			Public RollFrameExtLinePos3 As Integer

			' Token: 0x04000A2F RID: 2607
			Public RollFrameExtLine1 As String

			' Token: 0x04000A30 RID: 2608
			Public RollFrameExtLine2 As String

			' Token: 0x04000A31 RID: 2609
			Public RollFrameExtLine3 As String

			' Token: 0x04000A32 RID: 2610
			Public NeuerMagnet As Boolean

			' Token: 0x04000A33 RID: 2611
			Public MagnetDelay As Integer

			' Token: 0x04000A34 RID: 2612
			Public SIMULATIONDELAY As Integer

			' Token: 0x04000A35 RID: 2613
			Public USEDISPLAYSECTION As Boolean

			' Token: 0x04000A36 RID: 2614
			Public DISPLAY_DEFAULT As String

			' Token: 0x04000A37 RID: 2615
			Public DISPLAY_PDF As String

			' Token: 0x04000A38 RID: 2616
			Public DISPLAY_BPP1 As String

			' Token: 0x04000A39 RID: 2617
			Public DISPLAY_BPP8 As String

			' Token: 0x04000A3A RID: 2618
			Public DISPLAY_BPP24 As String

			' Token: 0x04000A3B RID: 2619
			Public BACKCOLOR As Integer

			' Token: 0x04000A3C RID: 2620
			Public AddStepLevel2 As Double

			' Token: 0x04000A3D RID: 2621
			Public AddStepLevel3 As Double

			' Token: 0x04000A3E RID: 2622
			Public UseAddRollFrame As Boolean

			' Token: 0x04000A3F RID: 2623
			<VBFixedArray(4)>
			Public AddRollFrameLinePos As Integer()

			' Token: 0x04000A40 RID: 2624
			<VBFixedArray(4)>
			Public AddRollFrameLines As String()

			' Token: 0x04000A41 RID: 2625
			Public AddRollFrameFontSize As Integer

			' Token: 0x04000A42 RID: 2626
			Public AddRollFrameInputLen As Integer

			' Token: 0x04000A43 RID: 2627
			Public ShowAddRollFrame As Boolean

			' Token: 0x04000A44 RID: 2628
			Public ShowLastData As Boolean

			' Token: 0x04000A45 RID: 2629
			Public BayHStA As Boolean

			' Token: 0x04000A46 RID: 2630
			Public UseAccuv16 As Boolean

			' Token: 0x04000A47 RID: 2631
			Public PortaitA3Drehen As Boolean

			' Token: 0x04000A48 RID: 2632
			Public LandscapeA4Drehen As Boolean

			' Token: 0x04000A49 RID: 2633
			Public A4R As Boolean

			' Token: 0x04000A4A RID: 2634
			Public A4L As Boolean

			' Token: 0x04000A4B RID: 2635
			Public A3R As Boolean

			' Token: 0x04000A4C RID: 2636
			Public A3L As Boolean

			' Token: 0x04000A4D RID: 2637
			Public SMCI As Boolean

			' Token: 0x04000A4E RID: 2638
			Public PRECACHEIMAGES As Boolean

			' Token: 0x04000A4F RID: 2639
			Public PRECACHEIMAGESSTAGEII As Boolean

			' Token: 0x04000A50 RID: 2640
			Public NanoFactor As Double

			' Token: 0x04000A51 RID: 2641
			Public A3A4Duplex As Boolean

			' Token: 0x04000A52 RID: 2642
			Public SchritteVolleUmdrehung As Integer

			' Token: 0x04000A53 RID: 2643
			Public AddRollStartFrameSteps As Integer

			' Token: 0x04000A54 RID: 2644
			Public UseDebenu As Boolean

			' Token: 0x04000A55 RID: 2645
			Public UsePdf2Img As Boolean

			' Token: 0x04000A56 RID: 2646
			Public PDF2IMGTEMPFOLDER As String

			' Token: 0x04000A57 RID: 2647
			Public DebenuLic As String

			' Token: 0x04000A58 RID: 2648
			Public SmallShutter As Boolean

			' Token: 0x04000A59 RID: 2649
			Public SmallShutterFirstDir As Short

			' Token: 0x04000A5A RID: 2650
			Public UseArduino As Boolean

			' Token: 0x04000A5B RID: 2651
			Public optOben As Boolean

			' Token: 0x04000A5C RID: 2652
			Public optUnten As Boolean

			' Token: 0x04000A5D RID: 2653
			Public optCenter As Boolean

			' Token: 0x04000A5E RID: 2654
			Public optLage As Boolean

			' Token: 0x04000A5F RID: 2655
			Public LateAnnoNumbering As Boolean

			' Token: 0x04000A60 RID: 2656
			Public Trinamic As Boolean

			' Token: 0x04000A61 RID: 2657
			Public AutoRollInsert As Short

			' Token: 0x04000A62 RID: 2658
			Public JPEGProcessor As Boolean

			' Token: 0x04000A63 RID: 2659
			Public MonitorThreshold As Short

			' Token: 0x04000A64 RID: 2660
			Public ExtendedVacuumHandling As Boolean

			' Token: 0x04000A65 RID: 2661
			Public VacErrorFile As String

			' Token: 0x04000A66 RID: 2662
			Public RetryFirstLevel As Short

			' Token: 0x04000A67 RID: 2663
			Public VacSteps As Integer

			' Token: 0x04000A68 RID: 2664
			Public RetrySecondLevel As Integer

			' Token: 0x04000A69 RID: 2665
			Public FrameWidth As Integer

			' Token: 0x04000A6A RID: 2666
			Public WhiteFrame As Boolean

			' Token: 0x04000A6B RID: 2667
			Public CheckIfImageOnScreen As Boolean

			' Token: 0x04000A6C RID: 2668
			Public CheckIfImageOnScreenThreshold As Integer

			' Token: 0x04000A6D RID: 2669
			Public VerschlussRichtung As Integer

			' Token: 0x04000A6E RID: 2670
			Public Duplex As Boolean

			' Token: 0x04000A6F RID: 2671
			Public SimDupFilenames As Boolean

			' Token: 0x04000A70 RID: 2672
			Public TwoLines As Boolean

			' Token: 0x04000A71 RID: 2673
			Public PDFKONVERTER As String

			' Token: 0x04000A72 RID: 2674
			Public PDFKONVERTERTEMP As String
		End Structure

		' Token: 0x02000103 RID: 259
		Public Structure LOGFONT
			' Token: 0x06001209 RID: 4617 RVA: 0x00098705 File Offset: 0x00096905
			Public Sub Initialize()
				Me.lfFaceName = New Byte(32) {}
			End Sub

			' Token: 0x04000A73 RID: 2675
			Public lfHeight As Integer

			' Token: 0x04000A74 RID: 2676
			Public lfWidth As Integer

			' Token: 0x04000A75 RID: 2677
			Public lfEscapement As Integer

			' Token: 0x04000A76 RID: 2678
			Public lfOrientation As Integer

			' Token: 0x04000A77 RID: 2679
			Public lfWeight As Integer

			' Token: 0x04000A78 RID: 2680
			Public lfItalic As Byte

			' Token: 0x04000A79 RID: 2681
			Public lfUnderline As Byte

			' Token: 0x04000A7A RID: 2682
			Public lfStrikeOut As Byte

			' Token: 0x04000A7B RID: 2683
			Public lfCharSet As Byte

			' Token: 0x04000A7C RID: 2684
			Public lfOutPrecision As Byte

			' Token: 0x04000A7D RID: 2685
			Public lfClipPrecision As Byte

			' Token: 0x04000A7E RID: 2686
			Public lfQuality As Byte

			' Token: 0x04000A7F RID: 2687
			Public lfPitchAndFamily As Byte

			' Token: 0x04000A80 RID: 2688
			<VBFixedArray(32)>
			Public lfFaceName As Byte()
		End Structure

		' Token: 0x02000104 RID: 260
		Public Structure SECURITY_ATTRIBUTES
			' Token: 0x04000A81 RID: 2689
			Public nLength As Integer

			' Token: 0x04000A82 RID: 2690
			Public lpSecurityDescriptor As Integer

			' Token: 0x04000A83 RID: 2691
			Public bInheritHandle As Integer
		End Structure

		' Token: 0x02000105 RID: 261
		Public Structure typImage
			' Token: 0x04000A84 RID: 2692
			Public Name As String

			' Token: 0x04000A85 RID: 2693
			Public NameSaved As String

			' Token: 0x04000A86 RID: 2694
			Public IsPDF As Boolean

			' Token: 0x04000A87 RID: 2695
			Public Level As Short

			' Token: 0x04000A88 RID: 2696
			Public count As Integer

			' Token: 0x04000A89 RID: 2697
			Public page As Integer

			' Token: 0x04000A8A RID: 2698
			Public DokumentName As String

			' Token: 0x04000A8B RID: 2699
			Public Blip1Level As Integer

			' Token: 0x04000A8C RID: 2700
			Public Blip2Level As Integer

			' Token: 0x04000A8D RID: 2701
			Public Blip3Level As Integer

			' Token: 0x04000A8E RID: 2702
			Public Width As Double

			' Token: 0x04000A8F RID: 2703
			Public Height As Double

			' Token: 0x04000A90 RID: 2704
			Public RendererStarted As Boolean

			' Token: 0x04000A91 RID: 2705
			Public PageCount As Long
		End Structure

		' Token: 0x02000106 RID: 262
		Public Structure FILETIME
			' Token: 0x04000A92 RID: 2706
			Public dwLowDateTime As Integer

			' Token: 0x04000A93 RID: 2707
			Public dwHighDateTime As Integer
		End Structure

		' Token: 0x02000107 RID: 263
		Public Structure WIN32_FIND_DATA
			' Token: 0x04000A94 RID: 2708
			Public dwFileAttributes As UInteger

			' Token: 0x04000A95 RID: 2709
			Public ftCreationTime As System.Runtime.InteropServices.ComTypes.FILETIME

			' Token: 0x04000A96 RID: 2710
			Public ftLastAccessTime As System.Runtime.InteropServices.ComTypes.FILETIME

			' Token: 0x04000A97 RID: 2711
			Public ftLastWriteTime As System.Runtime.InteropServices.ComTypes.FILETIME

			' Token: 0x04000A98 RID: 2712
			Public nFileSizeHigh As UInteger

			' Token: 0x04000A99 RID: 2713
			Public nFileSizeLow As UInteger

			' Token: 0x04000A9A RID: 2714
			Public dwReserved0 As UInteger

			' Token: 0x04000A9B RID: 2715
			Public dwReserved1 As UInteger

			' Token: 0x04000A9C RID: 2716
			<MarshalAs(UnmanagedType.ByValTStr, SizeConst := 260)>
			Public cFileName As String

			' Token: 0x04000A9D RID: 2717
			<MarshalAs(UnmanagedType.ByValTStr, SizeConst := 14)>
			Public cAlternateFileName As String
		End Structure

		' Token: 0x02000108 RID: 264
		Public Structure CLIENTCREATESTRUCT
			' Token: 0x04000A9E RID: 2718
			Public hWindowMenu As Integer

			' Token: 0x04000A9F RID: 2719
			Public idFirstChild As Integer
		End Structure

		' Token: 0x02000109 RID: 265
		Public Structure OFSTRUCT
			' Token: 0x0600120A RID: 4618 RVA: 0x00098714 File Offset: 0x00096914
			Public Sub Initialize()
				Me.szPathName = New Byte(128) {}
			End Sub

			' Token: 0x04000AA0 RID: 2720
			Public cBytes As Byte

			' Token: 0x04000AA1 RID: 2721
			Public fFixedDisk As Byte

			' Token: 0x04000AA2 RID: 2722
			Public nErrCode As Short

			' Token: 0x04000AA3 RID: 2723
			Public Reserved1 As Short

			' Token: 0x04000AA4 RID: 2724
			Public Reserved2 As Short

			' Token: 0x04000AA5 RID: 2725
			<VBFixedArray(128)>
			Public szPathName As Byte()
		End Structure
	End Module
End Namespace
