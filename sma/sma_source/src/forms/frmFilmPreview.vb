Imports System
Imports System.ComponentModel
Imports System.Diagnostics
Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Drawing.Imaging
Imports System.IO
Imports System.Runtime.CompilerServices
Imports System.Text
Imports System.Windows.Forms
Imports fileconverter.My
Imports fileconverter.My.Resources
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices
Imports Microsoft.WindowsAPICodePack.Shell
Imports Scripting

Namespace fileconverter
	' Token: 0x02000018 RID: 24
	<DesignerGenerated()>
	Friend Class frmFilmPreview
		Inherits Form

		' Token: 0x060004F1 RID: 1265 RVA: 0x00020D51 File Offset: 0x0001EF51
		<DebuggerNonUserCode()>
		Public Sub New()
			AddHandler MyBase.Load, AddressOf Me.frmFilmPreview_Load
			AddHandler MyBase.FormClosed, AddressOf Me.frmFilmPreview_FormClosed
			Me.InitializeComponent()
		End Sub

		' Token: 0x060004F2 RID: 1266 RVA: 0x00020D83 File Offset: 0x0001EF83
		<DebuggerNonUserCode()>
		Protected Overrides Sub Dispose(Disposing As Boolean)
			If Disposing AndAlso Me.components IsNot Nothing Then
				Me.components.Dispose()
			End If
			MyBase.Dispose(Disposing)
		End Sub

		' Token: 0x1700006E RID: 110
		' (get) Token: 0x060004F3 RID: 1267 RVA: 0x00020DA2 File Offset: 0x0001EFA2
		' (set) Token: 0x060004F4 RID: 1268 RVA: 0x00020DAA File Offset: 0x0001EFAA
		Public Overridable Property txtFilmNrAufFilm As TextBox

		' Token: 0x1700006F RID: 111
		' (get) Token: 0x060004F5 RID: 1269 RVA: 0x00020DB3 File Offset: 0x0001EFB3
		' (set) Token: 0x060004F6 RID: 1270 RVA: 0x00020DBC File Offset: 0x0001EFBC
		Public Overridable Property cmdFortsetzung As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdFortsetzung
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdFortsetzung_Click
				Dim cmdFortsetzung As Button = Me._cmdFortsetzung
				If cmdFortsetzung IsNot Nothing Then
					RemoveHandler cmdFortsetzung.Click, value2
				End If
				Me._cmdFortsetzung = value
				cmdFortsetzung = Me._cmdFortsetzung
				If cmdFortsetzung IsNot Nothing Then
					AddHandler cmdFortsetzung.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000070 RID: 112
		' (get) Token: 0x060004F7 RID: 1271 RVA: 0x00020DFF File Offset: 0x0001EFFF
		' (set) Token: 0x060004F8 RID: 1272 RVA: 0x00020E08 File Offset: 0x0001F008
		Public Overridable Property cmdRefilm As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdRefilm
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdRefilm_Click
				Dim cmdRefilm As Button = Me._cmdRefilm
				If cmdRefilm IsNot Nothing Then
					RemoveHandler cmdRefilm.Click, value2
				End If
				Me._cmdRefilm = value
				cmdRefilm = Me._cmdRefilm
				If cmdRefilm IsNot Nothing Then
					AddHandler cmdRefilm.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000071 RID: 113
		' (get) Token: 0x060004F9 RID: 1273 RVA: 0x00020E4B File Offset: 0x0001F04B
		' (set) Token: 0x060004FA RID: 1274 RVA: 0x00020E54 File Offset: 0x0001F054
		Public Overridable Property cmdCalcSpace As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdCalcSpace
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdCalcSpace_Click
				Dim cmdCalcSpace As Button = Me._cmdCalcSpace
				If cmdCalcSpace IsNot Nothing Then
					RemoveHandler cmdCalcSpace.Click, value2
				End If
				Me._cmdCalcSpace = value
				cmdCalcSpace = Me._cmdCalcSpace
				If cmdCalcSpace IsNot Nothing Then
					AddHandler cmdCalcSpace.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000072 RID: 114
		' (get) Token: 0x060004FB RID: 1275 RVA: 0x00020E97 File Offset: 0x0001F097
		' (set) Token: 0x060004FC RID: 1276 RVA: 0x00020EA0 File Offset: 0x0001F0A0
		Public Overridable Property cmdAbspulen As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdAbspulen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdAbspulen_Click
				Dim cmdAbspulen As Button = Me._cmdAbspulen
				If cmdAbspulen IsNot Nothing Then
					RemoveHandler cmdAbspulen.Click, value2
				End If
				Me._cmdAbspulen = value
				cmdAbspulen = Me._cmdAbspulen
				If cmdAbspulen IsNot Nothing Then
					AddHandler cmdAbspulen.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000073 RID: 115
		' (get) Token: 0x060004FD RID: 1277 RVA: 0x00020EE3 File Offset: 0x0001F0E3
		' (set) Token: 0x060004FE RID: 1278 RVA: 0x00020EEC File Offset: 0x0001F0EC
		Public Overridable Property cmdVorspann As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdVorspann
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdVorspann_Click
				Dim cmdVorspann As Button = Me._cmdVorspann
				If cmdVorspann IsNot Nothing Then
					RemoveHandler cmdVorspann.Click, value2
				End If
				Me._cmdVorspann = value
				cmdVorspann = Me._cmdVorspann
				If cmdVorspann IsNot Nothing Then
					AddHandler cmdVorspann.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000074 RID: 116
		' (get) Token: 0x060004FF RID: 1279 RVA: 0x00020F2F File Offset: 0x0001F12F
		' (set) Token: 0x06000500 RID: 1280 RVA: 0x00020F37 File Offset: 0x0001F137
		Public Overridable Property cmbKopf As ComboBox

		' Token: 0x17000075 RID: 117
		' (get) Token: 0x06000501 RID: 1281 RVA: 0x00020F40 File Offset: 0x0001F140
		' (set) Token: 0x06000502 RID: 1282 RVA: 0x00020F48 File Offset: 0x0001F148
		Public Overridable Property _Picture1_6 As PictureBox

		' Token: 0x17000076 RID: 118
		' (get) Token: 0x06000503 RID: 1283 RVA: 0x00020F51 File Offset: 0x0001F151
		' (set) Token: 0x06000504 RID: 1284 RVA: 0x00020F5C File Offset: 0x0001F15C
		Public Overridable Property chkNoPreview As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkNoPreview
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkNoPreview_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkNoPreview_CheckedChanged
				Dim chkNoPreview As CheckBox = Me._chkNoPreview
				If chkNoPreview IsNot Nothing Then
					RemoveHandler chkNoPreview.CheckStateChanged, value2
					RemoveHandler chkNoPreview.CheckedChanged, value3
				End If
				Me._chkNoPreview = value
				chkNoPreview = Me._chkNoPreview
				If chkNoPreview IsNot Nothing Then
					AddHandler chkNoPreview.CheckStateChanged, value2
					AddHandler chkNoPreview.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x17000077 RID: 119
		' (get) Token: 0x06000505 RID: 1285 RVA: 0x00020FBA File Offset: 0x0001F1BA
		' (set) Token: 0x06000506 RID: 1286 RVA: 0x00020FC4 File Offset: 0x0001F1C4
		Public Overridable Property _Picture1_5 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_5
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_5_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_5_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_5
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_5 = value
				_Picture1_ = Me.__Picture1_5
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x17000078 RID: 120
		' (get) Token: 0x06000507 RID: 1287 RVA: 0x00021022 File Offset: 0x0001F222
		' (set) Token: 0x06000508 RID: 1288 RVA: 0x0002102C File Offset: 0x0001F22C
		Public Overridable Property _Picture1_4 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_4
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_4_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_4_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_4
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_4 = value
				_Picture1_ = Me.__Picture1_4
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x17000079 RID: 121
		' (get) Token: 0x06000509 RID: 1289 RVA: 0x0002108A File Offset: 0x0001F28A
		' (set) Token: 0x0600050A RID: 1290 RVA: 0x00021094 File Offset: 0x0001F294
		Public Overridable Property _Picture1_3 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_3_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_3_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_3
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_3 = value
				_Picture1_ = Me.__Picture1_3
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x1700007A RID: 122
		' (get) Token: 0x0600050B RID: 1291 RVA: 0x000210F2 File Offset: 0x0001F2F2
		' (set) Token: 0x0600050C RID: 1292 RVA: 0x000210FC File Offset: 0x0001F2FC
		Public Overridable Property _Picture1_2 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_2
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_2_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_2_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_2
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_2 = value
				_Picture1_ = Me.__Picture1_2
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x1700007B RID: 123
		' (get) Token: 0x0600050D RID: 1293 RVA: 0x0002115A File Offset: 0x0001F35A
		' (set) Token: 0x0600050E RID: 1294 RVA: 0x00021164 File Offset: 0x0001F364
		Public Overridable Property _Picture1_1 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_1_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_1_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_1
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_1 = value
				_Picture1_ = Me.__Picture1_1
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x1700007C RID: 124
		' (get) Token: 0x0600050F RID: 1295 RVA: 0x000211C2 File Offset: 0x0001F3C2
		' (set) Token: 0x06000510 RID: 1296 RVA: 0x000211CC File Offset: 0x0001F3CC
		Public Overridable Property _Picture1_0 As PictureBox
			<CompilerGenerated()>
			Get
				Return Me.__Picture1_0
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As PictureBox)
				Dim value2 As EventHandler = AddressOf Me._Picture1_0_Click
				Dim value3 As EventHandler = AddressOf Me._Picture1_0_DoubleClick
				Dim _Picture1_ As PictureBox = Me.__Picture1_0
				If _Picture1_ IsNot Nothing Then
					RemoveHandler _Picture1_.Click, value2
					RemoveHandler _Picture1_.DoubleClick, value3
				End If
				Me.__Picture1_0 = value
				_Picture1_ = Me.__Picture1_0
				If _Picture1_ IsNot Nothing Then
					AddHandler _Picture1_.Click, value2
					AddHandler _Picture1_.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x1700007D RID: 125
		' (get) Token: 0x06000511 RID: 1297 RVA: 0x0002122A File Offset: 0x0001F42A
		' (set) Token: 0x06000512 RID: 1298 RVA: 0x00021232 File Offset: 0x0001F432
		Public Overridable Property _Label_0 As Label

		' Token: 0x1700007E RID: 126
		' (get) Token: 0x06000513 RID: 1299 RVA: 0x0002123B File Offset: 0x0001F43B
		' (set) Token: 0x06000514 RID: 1300 RVA: 0x00021243 File Offset: 0x0001F443
		Public Overridable Property _Label_6 As Label

		' Token: 0x1700007F RID: 127
		' (get) Token: 0x06000515 RID: 1301 RVA: 0x0002124C File Offset: 0x0001F44C
		' (set) Token: 0x06000516 RID: 1302 RVA: 0x00021254 File Offset: 0x0001F454
		Public Overridable Property _Label_9 As Label

		' Token: 0x17000080 RID: 128
		' (get) Token: 0x06000517 RID: 1303 RVA: 0x0002125D File Offset: 0x0001F45D
		' (set) Token: 0x06000518 RID: 1304 RVA: 0x00021265 File Offset: 0x0001F465
		Public Overridable Property _Label_10 As Label

		' Token: 0x17000081 RID: 129
		' (get) Token: 0x06000519 RID: 1305 RVA: 0x0002126E File Offset: 0x0001F46E
		' (set) Token: 0x0600051A RID: 1306 RVA: 0x00021278 File Offset: 0x0001F478
		Public Overridable Property chkAutoAlign180 As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkAutoAlign180
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkAutoAlign180_CheckStateChanged
				Dim chkAutoAlign As CheckBox = Me._chkAutoAlign180
				If chkAutoAlign IsNot Nothing Then
					RemoveHandler chkAutoAlign.CheckStateChanged, value2
				End If
				Me._chkAutoAlign180 = value
				chkAutoAlign = Me._chkAutoAlign180
				If chkAutoAlign IsNot Nothing Then
					AddHandler chkAutoAlign.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000082 RID: 130
		' (get) Token: 0x0600051B RID: 1307 RVA: 0x000212BB File Offset: 0x0001F4BB
		' (set) Token: 0x0600051C RID: 1308 RVA: 0x000212C4 File Offset: 0x0001F4C4
		Public Overridable Property opt270 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._opt270
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.opt270_CheckedChanged
				Dim opt As RadioButton = Me._opt270
				If opt IsNot Nothing Then
					RemoveHandler opt.CheckedChanged, value2
				End If
				Me._opt270 = value
				opt = Me._opt270
				If opt IsNot Nothing Then
					AddHandler opt.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000083 RID: 131
		' (get) Token: 0x0600051D RID: 1309 RVA: 0x00021307 File Offset: 0x0001F507
		' (set) Token: 0x0600051E RID: 1310 RVA: 0x00021310 File Offset: 0x0001F510
		Public Overridable Property opt90 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._opt90
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.opt90_CheckedChanged
				Dim opt As RadioButton = Me._opt90
				If opt IsNot Nothing Then
					RemoveHandler opt.CheckedChanged, value2
				End If
				Me._opt90 = value
				opt = Me._opt90
				If opt IsNot Nothing Then
					AddHandler opt.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000084 RID: 132
		' (get) Token: 0x0600051F RID: 1311 RVA: 0x00021353 File Offset: 0x0001F553
		' (set) Token: 0x06000520 RID: 1312 RVA: 0x0002135B File Offset: 0x0001F55B
		Public Overridable Property frbAusrichtung As GroupBox

		' Token: 0x17000085 RID: 133
		' (get) Token: 0x06000521 RID: 1313 RVA: 0x00021364 File Offset: 0x0001F564
		' (set) Token: 0x06000522 RID: 1314 RVA: 0x0002136C File Offset: 0x0001F56C
		Public Overridable Property optFest90 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optFest90
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optFest90_CheckedChanged
				Dim optFest As RadioButton = Me._optFest90
				If optFest IsNot Nothing Then
					RemoveHandler optFest.CheckedChanged, value2
				End If
				Me._optFest90 = value
				optFest = Me._optFest90
				If optFest IsNot Nothing Then
					AddHandler optFest.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000086 RID: 134
		' (get) Token: 0x06000523 RID: 1315 RVA: 0x000213AF File Offset: 0x0001F5AF
		' (set) Token: 0x06000524 RID: 1316 RVA: 0x000213B8 File Offset: 0x0001F5B8
		Public Overridable Property optFest270 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optFest270
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optFest270_CheckedChanged
				Dim optFest As RadioButton = Me._optFest270
				If optFest IsNot Nothing Then
					RemoveHandler optFest.CheckedChanged, value2
				End If
				Me._optFest270 = value
				optFest = Me._optFest270
				If optFest IsNot Nothing Then
					AddHandler optFest.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000087 RID: 135
		' (get) Token: 0x06000525 RID: 1317 RVA: 0x000213FB File Offset: 0x0001F5FB
		' (set) Token: 0x06000526 RID: 1318 RVA: 0x00021404 File Offset: 0x0001F604
		Public Overridable Property optFest180 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optFest180
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optFest180_CheckedChanged
				Dim optFest As RadioButton = Me._optFest180
				If optFest IsNot Nothing Then
					RemoveHandler optFest.CheckedChanged, value2
				End If
				Me._optFest180 = value
				optFest = Me._optFest180
				If optFest IsNot Nothing Then
					AddHandler optFest.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000088 RID: 136
		' (get) Token: 0x06000527 RID: 1319 RVA: 0x00021447 File Offset: 0x0001F647
		' (set) Token: 0x06000528 RID: 1320 RVA: 0x00021450 File Offset: 0x0001F650
		Public Overridable Property optFest0 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optFest0
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optFest0_CheckedChanged
				Dim optFest As RadioButton = Me._optFest0
				If optFest IsNot Nothing Then
					RemoveHandler optFest.CheckedChanged, value2
				End If
				Me._optFest0 = value
				optFest = Me._optFest0
				If optFest IsNot Nothing Then
					AddHandler optFest.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000089 RID: 137
		' (get) Token: 0x06000529 RID: 1321 RVA: 0x00021493 File Offset: 0x0001F693
		' (set) Token: 0x0600052A RID: 1322 RVA: 0x0002149B File Offset: 0x0001F69B
		Public Overridable Property Frame1 As GroupBox

		' Token: 0x1700008A RID: 138
		' (get) Token: 0x0600052B RID: 1323 RVA: 0x000214A4 File Offset: 0x0001F6A4
		' (set) Token: 0x0600052C RID: 1324 RVA: 0x000214AC File Offset: 0x0001F6AC
		Public Overridable Property chkAutoAlign As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkAutoAlign
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkAutoAlign_CheckStateChanged
				Dim chkAutoAlign As CheckBox = Me._chkAutoAlign
				If chkAutoAlign IsNot Nothing Then
					RemoveHandler chkAutoAlign.CheckStateChanged, value2
				End If
				Me._chkAutoAlign = value
				chkAutoAlign = Me._chkAutoAlign
				If chkAutoAlign IsNot Nothing Then
					AddHandler chkAutoAlign.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700008B RID: 139
		' (get) Token: 0x0600052D RID: 1325 RVA: 0x000214EF File Offset: 0x0001F6EF
		' (set) Token: 0x0600052E RID: 1326 RVA: 0x000214F8 File Offset: 0x0001F6F8
		Public Overridable Property optLagerichtig As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._optLagerichtig
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.optLagerichtig_CheckStateChanged
				Dim optLagerichtig As CheckBox = Me._optLagerichtig
				If optLagerichtig IsNot Nothing Then
					RemoveHandler optLagerichtig.CheckStateChanged, value2
				End If
				Me._optLagerichtig = value
				optLagerichtig = Me._optLagerichtig
				If optLagerichtig IsNot Nothing Then
					AddHandler optLagerichtig.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700008C RID: 140
		' (get) Token: 0x0600052F RID: 1327 RVA: 0x0002153B File Offset: 0x0001F73B
		' (set) Token: 0x06000530 RID: 1328 RVA: 0x00021544 File Offset: 0x0001F744
		Public Overridable Property chkA3PortraitDrehen As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkA3PortraitDrehen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkA3PortraitDrehen_CheckStateChanged
				Dim chkA3PortraitDrehen As CheckBox = Me._chkA3PortraitDrehen
				If chkA3PortraitDrehen IsNot Nothing Then
					RemoveHandler chkA3PortraitDrehen.CheckStateChanged, value2
				End If
				Me._chkA3PortraitDrehen = value
				chkA3PortraitDrehen = Me._chkA3PortraitDrehen
				If chkA3PortraitDrehen IsNot Nothing Then
					AddHandler chkA3PortraitDrehen.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700008D RID: 141
		' (get) Token: 0x06000531 RID: 1329 RVA: 0x00021587 File Offset: 0x0001F787
		' (set) Token: 0x06000532 RID: 1330 RVA: 0x00021590 File Offset: 0x0001F790
		Public Overridable Property chkA4LSDrehen As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkA4LSDrehen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkA4LSDrehen_CheckStateChanged
				Dim chkA4LSDrehen As CheckBox = Me._chkA4LSDrehen
				If chkA4LSDrehen IsNot Nothing Then
					RemoveHandler chkA4LSDrehen.CheckStateChanged, value2
				End If
				Me._chkA4LSDrehen = value
				chkA4LSDrehen = Me._chkA4LSDrehen
				If chkA4LSDrehen IsNot Nothing Then
					AddHandler chkA4LSDrehen.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700008E RID: 142
		' (get) Token: 0x06000533 RID: 1331 RVA: 0x000215D3 File Offset: 0x0001F7D3
		' (set) Token: 0x06000534 RID: 1332 RVA: 0x000215DC File Offset: 0x0001F7DC
		Public Overridable Property optLA3 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optLA3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optLA3_CheckedChanged
				Dim optLA As RadioButton = Me._optLA3
				If optLA IsNot Nothing Then
					RemoveHandler optLA.CheckedChanged, value2
				End If
				Me._optLA3 = value
				optLA = Me._optLA3
				If optLA IsNot Nothing Then
					AddHandler optLA.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700008F RID: 143
		' (get) Token: 0x06000535 RID: 1333 RVA: 0x0002161F File Offset: 0x0001F81F
		' (set) Token: 0x06000536 RID: 1334 RVA: 0x00021628 File Offset: 0x0001F828
		Public Overridable Property optRA3 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optRA3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optRA3_CheckedChanged
				Dim optRA As RadioButton = Me._optRA3
				If optRA IsNot Nothing Then
					RemoveHandler optRA.CheckedChanged, value2
				End If
				Me._optRA3 = value
				optRA = Me._optRA3
				If optRA IsNot Nothing Then
					AddHandler optRA.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000090 RID: 144
		' (get) Token: 0x06000537 RID: 1335 RVA: 0x0002166B File Offset: 0x0001F86B
		' (set) Token: 0x06000538 RID: 1336 RVA: 0x00021673 File Offset: 0x0001F873
		Public Overridable Property Frame15 As Panel

		' Token: 0x17000091 RID: 145
		' (get) Token: 0x06000539 RID: 1337 RVA: 0x0002167C File Offset: 0x0001F87C
		' (set) Token: 0x0600053A RID: 1338 RVA: 0x00021684 File Offset: 0x0001F884
		Public Overridable Property optLA4 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optLA4
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optLA4_CheckedChanged
				Dim optLA As RadioButton = Me._optLA4
				If optLA IsNot Nothing Then
					RemoveHandler optLA.CheckedChanged, value2
				End If
				Me._optLA4 = value
				optLA = Me._optLA4
				If optLA IsNot Nothing Then
					AddHandler optLA.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000092 RID: 146
		' (get) Token: 0x0600053B RID: 1339 RVA: 0x000216C7 File Offset: 0x0001F8C7
		' (set) Token: 0x0600053C RID: 1340 RVA: 0x000216D0 File Offset: 0x0001F8D0
		Public Overridable Property optRA4 As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optRA4
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optRA4_CheckedChanged
				Dim optRA As RadioButton = Me._optRA4
				If optRA IsNot Nothing Then
					RemoveHandler optRA.CheckedChanged, value2
				End If
				Me._optRA4 = value
				optRA = Me._optRA4
				If optRA IsNot Nothing Then
					AddHandler optRA.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000093 RID: 147
		' (get) Token: 0x0600053D RID: 1341 RVA: 0x00021713 File Offset: 0x0001F913
		' (set) Token: 0x0600053E RID: 1342 RVA: 0x0002171B File Offset: 0x0001F91B
		Public Overridable Property Frame14 As Panel

		' Token: 0x17000094 RID: 148
		' (get) Token: 0x0600053F RID: 1343 RVA: 0x00021724 File Offset: 0x0001F924
		' (set) Token: 0x06000540 RID: 1344 RVA: 0x0002172C File Offset: 0x0001F92C
		Public Overridable Property chkOneToOne As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkOneToOne
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkOneToOne_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkOneToOne_CheckedChanged
				Dim chkOneToOne As CheckBox = Me._chkOneToOne
				If chkOneToOne IsNot Nothing Then
					RemoveHandler chkOneToOne.CheckStateChanged, value2
					RemoveHandler chkOneToOne.CheckedChanged, value3
				End If
				Me._chkOneToOne = value
				chkOneToOne = Me._chkOneToOne
				If chkOneToOne IsNot Nothing Then
					AddHandler chkOneToOne.CheckStateChanged, value2
					AddHandler chkOneToOne.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x17000095 RID: 149
		' (get) Token: 0x06000541 RID: 1345 RVA: 0x0002178A File Offset: 0x0001F98A
		' (set) Token: 0x06000542 RID: 1346 RVA: 0x00021794 File Offset: 0x0001F994
		Public Overridable Property txtFactor As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtFactor
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtFactor_TextChanged
				Dim value3 As KeyPressEventHandler = AddressOf Me.txtFactor_KeyPress
				Dim txtFactor As TextBox = Me._txtFactor
				If txtFactor IsNot Nothing Then
					RemoveHandler txtFactor.TextChanged, value2
					RemoveHandler txtFactor.KeyPress, value3
				End If
				Me._txtFactor = value
				txtFactor = Me._txtFactor
				If txtFactor IsNot Nothing Then
					AddHandler txtFactor.TextChanged, value2
					AddHandler txtFactor.KeyPress, value3
				End If
			End Set
		End Property

		' Token: 0x17000096 RID: 150
		' (get) Token: 0x06000543 RID: 1347 RVA: 0x000217F2 File Offset: 0x0001F9F2
		' (set) Token: 0x06000544 RID: 1348 RVA: 0x000217FC File Offset: 0x0001F9FC
		Public Overridable Property txtToleranz As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtToleranz
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtToleranz_TextChanged
				Dim value3 As KeyPressEventHandler = AddressOf Me.txtToleranz_KeyPress
				Dim txtToleranz As TextBox = Me._txtToleranz
				If txtToleranz IsNot Nothing Then
					RemoveHandler txtToleranz.TextChanged, value2
					RemoveHandler txtToleranz.KeyPress, value3
				End If
				Me._txtToleranz = value
				txtToleranz = Me._txtToleranz
				If txtToleranz IsNot Nothing Then
					AddHandler txtToleranz.TextChanged, value2
					AddHandler txtToleranz.KeyPress, value3
				End If
			End Set
		End Property

		' Token: 0x17000097 RID: 151
		' (get) Token: 0x06000545 RID: 1349 RVA: 0x0002185A File Offset: 0x0001FA5A
		' (set) Token: 0x06000546 RID: 1350 RVA: 0x00021862 File Offset: 0x0001FA62
		Public Overridable Property _Label_33 As Label

		' Token: 0x17000098 RID: 152
		' (get) Token: 0x06000547 RID: 1351 RVA: 0x0002186B File Offset: 0x0001FA6B
		' (set) Token: 0x06000548 RID: 1352 RVA: 0x00021873 File Offset: 0x0001FA73
		Public Overridable Property _Label_32 As Label

		' Token: 0x17000099 RID: 153
		' (get) Token: 0x06000549 RID: 1353 RVA: 0x0002187C File Offset: 0x0001FA7C
		' (set) Token: 0x0600054A RID: 1354 RVA: 0x00021884 File Offset: 0x0001FA84
		Public Overridable Property _label__5 As Label

		' Token: 0x1700009A RID: 154
		' (get) Token: 0x0600054B RID: 1355 RVA: 0x0002188D File Offset: 0x0001FA8D
		' (set) Token: 0x0600054C RID: 1356 RVA: 0x00021898 File Offset: 0x0001FA98
		Public Overridable Property Frame9 As GroupBox
			<CompilerGenerated()>
			Get
				Return Me._Frame9
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As GroupBox)
				Dim value2 As EventHandler = AddressOf Me.Frame9_Enter
				Dim frame As GroupBox = Me._Frame9
				If frame IsNot Nothing Then
					RemoveHandler frame.Enter, value2
				End If
				Me._Frame9 = value
				frame = Me._Frame9
				If frame IsNot Nothing Then
					AddHandler frame.Enter, value2
				End If
			End Set
		End Property

		' Token: 0x1700009B RID: 155
		' (get) Token: 0x0600054D RID: 1357 RVA: 0x000218DB File Offset: 0x0001FADB
		' (set) Token: 0x0600054E RID: 1358 RVA: 0x000218E4 File Offset: 0x0001FAE4
		Public Overridable Property chkDuplex As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkDuplex
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkDuplex_CheckStateChanged
				Dim chkDuplex As CheckBox = Me._chkDuplex
				If chkDuplex IsNot Nothing Then
					RemoveHandler chkDuplex.CheckStateChanged, value2
				End If
				Me._chkDuplex = value
				chkDuplex = Me._chkDuplex
				If chkDuplex IsNot Nothing Then
					AddHandler chkDuplex.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700009C RID: 156
		' (get) Token: 0x0600054F RID: 1359 RVA: 0x00021927 File Offset: 0x0001FB27
		' (set) Token: 0x06000550 RID: 1360 RVA: 0x0002192F File Offset: 0x0001FB2F
		Public Overridable Property txtMaxDuplex As TextBox

		' Token: 0x1700009D RID: 157
		' (get) Token: 0x06000551 RID: 1361 RVA: 0x00021938 File Offset: 0x0001FB38
		' (set) Token: 0x06000552 RID: 1362 RVA: 0x00021940 File Offset: 0x0001FB40
		Public Overridable Property txtDuplexDist As TextBox

		' Token: 0x1700009E RID: 158
		' (get) Token: 0x06000553 RID: 1363 RVA: 0x00021949 File Offset: 0x0001FB49
		' (set) Token: 0x06000554 RID: 1364 RVA: 0x00021951 File Offset: 0x0001FB51
		Public Overridable Property chkSmallLeft As CheckBox

		' Token: 0x1700009F RID: 159
		' (get) Token: 0x06000555 RID: 1365 RVA: 0x0002195A File Offset: 0x0001FB5A
		' (set) Token: 0x06000556 RID: 1366 RVA: 0x00021962 File Offset: 0x0001FB62
		Public Overridable Property chkBigLeft As CheckBox

		' Token: 0x170000A0 RID: 160
		' (get) Token: 0x06000557 RID: 1367 RVA: 0x0002196B File Offset: 0x0001FB6B
		' (set) Token: 0x06000558 RID: 1368 RVA: 0x00021974 File Offset: 0x0001FB74
		Public Overridable Property optOben As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optOben
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optOben_CheckedChanged
				Dim optOben As RadioButton = Me._optOben
				If optOben IsNot Nothing Then
					RemoveHandler optOben.CheckedChanged, value2
				End If
				Me._optOben = value
				optOben = Me._optOben
				If optOben IsNot Nothing Then
					AddHandler optOben.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000A1 RID: 161
		' (get) Token: 0x06000559 RID: 1369 RVA: 0x000219B7 File Offset: 0x0001FBB7
		' (set) Token: 0x0600055A RID: 1370 RVA: 0x000219C0 File Offset: 0x0001FBC0
		Public Overridable Property optUnten As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optUnten
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optUnten_CheckedChanged
				Dim optUnten As RadioButton = Me._optUnten
				If optUnten IsNot Nothing Then
					RemoveHandler optUnten.CheckedChanged, value2
				End If
				Me._optUnten = value
				optUnten = Me._optUnten
				If optUnten IsNot Nothing Then
					AddHandler optUnten.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000A2 RID: 162
		' (get) Token: 0x0600055B RID: 1371 RVA: 0x00021A03 File Offset: 0x0001FC03
		' (set) Token: 0x0600055C RID: 1372 RVA: 0x00021A0C File Offset: 0x0001FC0C
		Public Overridable Property optCenter As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optCenter
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optCenter_CheckedChanged
				Dim optCenter As RadioButton = Me._optCenter
				If optCenter IsNot Nothing Then
					RemoveHandler optCenter.CheckedChanged, value2
				End If
				Me._optCenter = value
				optCenter = Me._optCenter
				If optCenter IsNot Nothing Then
					AddHandler optCenter.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000A3 RID: 163
		' (get) Token: 0x0600055D RID: 1373 RVA: 0x00021A4F File Offset: 0x0001FC4F
		' (set) Token: 0x0600055E RID: 1374 RVA: 0x00021A57 File Offset: 0x0001FC57
		Public Overridable Property Frame3 As GroupBox

		' Token: 0x170000A4 RID: 164
		' (get) Token: 0x0600055F RID: 1375 RVA: 0x00021A60 File Offset: 0x0001FC60
		' (set) Token: 0x06000560 RID: 1376 RVA: 0x00021A68 File Offset: 0x0001FC68
		Public Overridable Property _tabSettings_TabPage0 As TabPage

		' Token: 0x170000A5 RID: 165
		' (get) Token: 0x06000561 RID: 1377 RVA: 0x00021A71 File Offset: 0x0001FC71
		' (set) Token: 0x06000562 RID: 1378 RVA: 0x00021A79 File Offset: 0x0001FC79
		Public Overridable Property _chk1PAgePDFs_1 As CheckBox

		' Token: 0x170000A6 RID: 166
		' (get) Token: 0x06000563 RID: 1379 RVA: 0x00021A82 File Offset: 0x0001FC82
		' (set) Token: 0x06000564 RID: 1380 RVA: 0x00021A8C File Offset: 0x0001FC8C
		Public Overridable Property _chk1PAgePDFs_0 As CheckBox
			<CompilerGenerated()>
			Get
				Return Me.__chk1PAgePDFs_0
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me._chk1PAgePDFs_0_CheckedChanged
				Dim _chk1PAgePDFs_ As CheckBox = Me.__chk1PAgePDFs_0
				If _chk1PAgePDFs_ IsNot Nothing Then
					RemoveHandler _chk1PAgePDFs_.CheckedChanged, value2
				End If
				Me.__chk1PAgePDFs_0 = value
				_chk1PAgePDFs_ = Me.__chk1PAgePDFs_0
				If _chk1PAgePDFs_ IsNot Nothing Then
					AddHandler _chk1PAgePDFs_.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000A7 RID: 167
		' (get) Token: 0x06000565 RID: 1381 RVA: 0x00021ACF File Offset: 0x0001FCCF
		' (set) Token: 0x06000566 RID: 1382 RVA: 0x00021AD7 File Offset: 0x0001FCD7
		Public Overridable Property _txtBlipHoeheGross_0 As TextBox

		' Token: 0x170000A8 RID: 168
		' (get) Token: 0x06000567 RID: 1383 RVA: 0x00021AE0 File Offset: 0x0001FCE0
		' (set) Token: 0x06000568 RID: 1384 RVA: 0x00021AE8 File Offset: 0x0001FCE8
		Public Overridable Property _txtBlipHoeheMittel_0 As TextBox

		' Token: 0x170000A9 RID: 169
		' (get) Token: 0x06000569 RID: 1385 RVA: 0x00021AF1 File Offset: 0x0001FCF1
		' (set) Token: 0x0600056A RID: 1386 RVA: 0x00021AF9 File Offset: 0x0001FCF9
		Public Overridable Property _txtBlipHoeheKlein_0 As TextBox

		' Token: 0x170000AA RID: 170
		' (get) Token: 0x0600056B RID: 1387 RVA: 0x00021B02 File Offset: 0x0001FD02
		' (set) Token: 0x0600056C RID: 1388 RVA: 0x00021B0A File Offset: 0x0001FD0A
		Public Overridable Property _txtBlipBreiteKlein_0 As TextBox

		' Token: 0x170000AB RID: 171
		' (get) Token: 0x0600056D RID: 1389 RVA: 0x00021B13 File Offset: 0x0001FD13
		' (set) Token: 0x0600056E RID: 1390 RVA: 0x00021B1B File Offset: 0x0001FD1B
		Public Overridable Property _txtBlipBreiteMittel_0 As TextBox

		' Token: 0x170000AC RID: 172
		' (get) Token: 0x0600056F RID: 1391 RVA: 0x00021B24 File Offset: 0x0001FD24
		' (set) Token: 0x06000570 RID: 1392 RVA: 0x00021B2C File Offset: 0x0001FD2C
		Public Overridable Property _txtBlipBreiteGross_0 As TextBox

		' Token: 0x170000AD RID: 173
		' (get) Token: 0x06000571 RID: 1393 RVA: 0x00021B35 File Offset: 0x0001FD35
		' (set) Token: 0x06000572 RID: 1394 RVA: 0x00021B3D File Offset: 0x0001FD3D
		Public Overridable Property _Label19_3 As Label

		' Token: 0x170000AE RID: 174
		' (get) Token: 0x06000573 RID: 1395 RVA: 0x00021B46 File Offset: 0x0001FD46
		' (set) Token: 0x06000574 RID: 1396 RVA: 0x00021B4E File Offset: 0x0001FD4E
		Public Overridable Property _Label19_2 As Label

		' Token: 0x170000AF RID: 175
		' (get) Token: 0x06000575 RID: 1397 RVA: 0x00021B57 File Offset: 0x0001FD57
		' (set) Token: 0x06000576 RID: 1398 RVA: 0x00021B5F File Offset: 0x0001FD5F
		Public Overridable Property _label__19 As Label

		' Token: 0x170000B0 RID: 176
		' (get) Token: 0x06000577 RID: 1399 RVA: 0x00021B68 File Offset: 0x0001FD68
		' (set) Token: 0x06000578 RID: 1400 RVA: 0x00021B70 File Offset: 0x0001FD70
		Public Overridable Property Label56 As Label

		' Token: 0x170000B1 RID: 177
		' (get) Token: 0x06000579 RID: 1401 RVA: 0x00021B79 File Offset: 0x0001FD79
		' (set) Token: 0x0600057A RID: 1402 RVA: 0x00021B81 File Offset: 0x0001FD81
		Public Overridable Property Label57 As Label

		' Token: 0x170000B2 RID: 178
		' (get) Token: 0x0600057B RID: 1403 RVA: 0x00021B8A File Offset: 0x0001FD8A
		' (set) Token: 0x0600057C RID: 1404 RVA: 0x00021B92 File Offset: 0x0001FD92
		Public Overridable Property Label58 As Label

		' Token: 0x170000B3 RID: 179
		' (get) Token: 0x0600057D RID: 1405 RVA: 0x00021B9B File Offset: 0x0001FD9B
		' (set) Token: 0x0600057E RID: 1406 RVA: 0x00021BA3 File Offset: 0x0001FDA3
		Public Overridable Property Label59 As Label

		' Token: 0x170000B4 RID: 180
		' (get) Token: 0x0600057F RID: 1407 RVA: 0x00021BAC File Offset: 0x0001FDAC
		' (set) Token: 0x06000580 RID: 1408 RVA: 0x00021BB4 File Offset: 0x0001FDB4
		Public Overridable Property _Label1_4 As Label

		' Token: 0x170000B5 RID: 181
		' (get) Token: 0x06000581 RID: 1409 RVA: 0x00021BBD File Offset: 0x0001FDBD
		' (set) Token: 0x06000582 RID: 1410 RVA: 0x00021BC5 File Offset: 0x0001FDC5
		Public Overridable Property Frame8 As GroupBox

		' Token: 0x170000B6 RID: 182
		' (get) Token: 0x06000583 RID: 1411 RVA: 0x00021BCE File Offset: 0x0001FDCE
		' (set) Token: 0x06000584 RID: 1412 RVA: 0x00021BD8 File Offset: 0x0001FDD8
		Public Overridable Property optUeberBlip As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optUeberBlip
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optUeberBlip_CheckedChanged
				Dim optUeberBlip As RadioButton = Me._optUeberBlip
				If optUeberBlip IsNot Nothing Then
					RemoveHandler optUeberBlip.CheckedChanged, value2
				End If
				Me._optUeberBlip = value
				optUeberBlip = Me._optUeberBlip
				If optUeberBlip IsNot Nothing Then
					AddHandler optUeberBlip.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000B7 RID: 183
		' (get) Token: 0x06000585 RID: 1413 RVA: 0x00021C1B File Offset: 0x0001FE1B
		' (set) Token: 0x06000586 RID: 1414 RVA: 0x00021C24 File Offset: 0x0001FE24
		Public Overridable Property optNebenBlip As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optNebenBlip
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optNebenBlip_CheckedChanged
				Dim optNebenBlip As RadioButton = Me._optNebenBlip
				If optNebenBlip IsNot Nothing Then
					RemoveHandler optNebenBlip.CheckedChanged, value2
				End If
				Me._optNebenBlip = value
				optNebenBlip = Me._optNebenBlip
				If optNebenBlip IsNot Nothing Then
					AddHandler optNebenBlip.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000B8 RID: 184
		' (get) Token: 0x06000587 RID: 1415 RVA: 0x00021C67 File Offset: 0x0001FE67
		' (set) Token: 0x06000588 RID: 1416 RVA: 0x00021C6F File Offset: 0x0001FE6F
		Public Overridable Property frmPosition As GroupBox

		' Token: 0x170000B9 RID: 185
		' (get) Token: 0x06000589 RID: 1417 RVA: 0x00021C78 File Offset: 0x0001FE78
		' (set) Token: 0x0600058A RID: 1418 RVA: 0x00021C80 File Offset: 0x0001FE80
		Public Overridable Property cmbBlipLevel1 As ComboBox
			<CompilerGenerated()>
			Get
				Return Me._cmbBlipLevel1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ComboBox)
				Dim value2 As EventHandler = AddressOf Me.cmbBlipLevel1_SelectedIndexChanged
				Dim cmbBlipLevel As ComboBox = Me._cmbBlipLevel1
				If cmbBlipLevel IsNot Nothing Then
					RemoveHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
				Me._cmbBlipLevel1 = value
				cmbBlipLevel = Me._cmbBlipLevel1
				If cmbBlipLevel IsNot Nothing Then
					AddHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000BA RID: 186
		' (get) Token: 0x0600058B RID: 1419 RVA: 0x00021CC3 File Offset: 0x0001FEC3
		' (set) Token: 0x0600058C RID: 1420 RVA: 0x00021CCC File Offset: 0x0001FECC
		Public Overridable Property cmbBlipLevel2 As ComboBox
			<CompilerGenerated()>
			Get
				Return Me._cmbBlipLevel2
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ComboBox)
				Dim value2 As EventHandler = AddressOf Me.cmbBlipLevel2_SelectedIndexChanged
				Dim cmbBlipLevel As ComboBox = Me._cmbBlipLevel2
				If cmbBlipLevel IsNot Nothing Then
					RemoveHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
				Me._cmbBlipLevel2 = value
				cmbBlipLevel = Me._cmbBlipLevel2
				If cmbBlipLevel IsNot Nothing Then
					AddHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000BB RID: 187
		' (get) Token: 0x0600058D RID: 1421 RVA: 0x00021D0F File Offset: 0x0001FF0F
		' (set) Token: 0x0600058E RID: 1422 RVA: 0x00021D18 File Offset: 0x0001FF18
		Public Overridable Property cmbBlipLevel3 As ComboBox
			<CompilerGenerated()>
			Get
				Return Me._cmbBlipLevel3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ComboBox)
				Dim value2 As EventHandler = AddressOf Me.cmbBlipLevel3_SelectedIndexChanged
				Dim cmbBlipLevel As ComboBox = Me._cmbBlipLevel3
				If cmbBlipLevel IsNot Nothing Then
					RemoveHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
				Me._cmbBlipLevel3 = value
				cmbBlipLevel = Me._cmbBlipLevel3
				If cmbBlipLevel IsNot Nothing Then
					AddHandler cmbBlipLevel.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000BC RID: 188
		' (get) Token: 0x0600058F RID: 1423 RVA: 0x00021D5B File Offset: 0x0001FF5B
		' (set) Token: 0x06000590 RID: 1424 RVA: 0x00021D63 File Offset: 0x0001FF63
		Public Overridable Property _label__23 As Label

		' Token: 0x170000BD RID: 189
		' (get) Token: 0x06000591 RID: 1425 RVA: 0x00021D6C File Offset: 0x0001FF6C
		' (set) Token: 0x06000592 RID: 1426 RVA: 0x00021D74 File Offset: 0x0001FF74
		Public Overridable Property _label__24 As Label

		' Token: 0x170000BE RID: 190
		' (get) Token: 0x06000593 RID: 1427 RVA: 0x00021D7D File Offset: 0x0001FF7D
		' (set) Token: 0x06000594 RID: 1428 RVA: 0x00021D85 File Offset: 0x0001FF85
		Public Overridable Property _label__25 As Label

		' Token: 0x170000BF RID: 191
		' (get) Token: 0x06000595 RID: 1429 RVA: 0x00021D8E File Offset: 0x0001FF8E
		' (set) Token: 0x06000596 RID: 1430 RVA: 0x00021D96 File Offset: 0x0001FF96
		Public Overridable Property Frame2 As GroupBox

		' Token: 0x170000C0 RID: 192
		' (get) Token: 0x06000597 RID: 1431 RVA: 0x00021D9F File Offset: 0x0001FF9F
		' (set) Token: 0x06000598 RID: 1432 RVA: 0x00021DA8 File Offset: 0x0001FFA8
		Public Overridable Property chkBlip As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkBlip
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkBLIP_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkBlip_CheckedChanged
				Dim chkBlip As CheckBox = Me._chkBlip
				If chkBlip IsNot Nothing Then
					RemoveHandler chkBlip.CheckStateChanged, value2
					RemoveHandler chkBlip.CheckedChanged, value3
				End If
				Me._chkBlip = value
				chkBlip = Me._chkBlip
				If chkBlip IsNot Nothing Then
					AddHandler chkBlip.CheckStateChanged, value2
					AddHandler chkBlip.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x170000C1 RID: 193
		' (get) Token: 0x06000599 RID: 1433 RVA: 0x00021E06 File Offset: 0x00020006
		' (set) Token: 0x0600059A RID: 1434 RVA: 0x00021E0E File Offset: 0x0002000E
		Public Overridable Property _tabSettings_TabPage1 As TabPage

		' Token: 0x170000C2 RID: 194
		' (get) Token: 0x0600059B RID: 1435 RVA: 0x00021E17 File Offset: 0x00020017
		' (set) Token: 0x0600059C RID: 1436 RVA: 0x00021E20 File Offset: 0x00020020
		Public Overridable Property chkAnnotation As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkAnnotation
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkAnnotation_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkAnnotation_CheckedChanged
				Dim chkAnnotation As CheckBox = Me._chkAnnotation
				If chkAnnotation IsNot Nothing Then
					RemoveHandler chkAnnotation.CheckStateChanged, value2
					RemoveHandler chkAnnotation.CheckedChanged, value3
				End If
				Me._chkAnnotation = value
				chkAnnotation = Me._chkAnnotation
				If chkAnnotation IsNot Nothing Then
					AddHandler chkAnnotation.CheckStateChanged, value2
					AddHandler chkAnnotation.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x170000C3 RID: 195
		' (get) Token: 0x0600059D RID: 1437 RVA: 0x00021E7E File Offset: 0x0002007E
		' (set) Token: 0x0600059E RID: 1438 RVA: 0x00021E88 File Offset: 0x00020088
		Public Overridable Property _tabSettings_TabPage2 As TabPage
			<CompilerGenerated()>
			Get
				Return Me.__tabSettings_TabPage2
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TabPage)
				Dim value2 As EventHandler = AddressOf Me._tabSettings_TabPage2_Click
				Dim _tabSettings_TabPage As TabPage = Me.__tabSettings_TabPage2
				If _tabSettings_TabPage IsNot Nothing Then
					RemoveHandler _tabSettings_TabPage.Click, value2
				End If
				Me.__tabSettings_TabPage2 = value
				_tabSettings_TabPage = Me.__tabSettings_TabPage2
				If _tabSettings_TabPage IsNot Nothing Then
					AddHandler _tabSettings_TabPage.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170000C4 RID: 196
		' (get) Token: 0x0600059F RID: 1439 RVA: 0x00021ECB File Offset: 0x000200CB
		' (set) Token: 0x060005A0 RID: 1440 RVA: 0x00021ED3 File Offset: 0x000200D3
		Public Overridable Property lblPfadStartSymbole As Label

		' Token: 0x170000C5 RID: 197
		' (get) Token: 0x060005A1 RID: 1441 RVA: 0x00021EDC File Offset: 0x000200DC
		' (set) Token: 0x060005A2 RID: 1442 RVA: 0x00021EE4 File Offset: 0x000200E4
		Public Overridable Property Label75 As Label

		' Token: 0x170000C6 RID: 198
		' (get) Token: 0x060005A3 RID: 1443 RVA: 0x00021EED File Offset: 0x000200ED
		' (set) Token: 0x060005A4 RID: 1444 RVA: 0x00021EF5 File Offset: 0x000200F5
		Public Overridable Property Label76 As Label

		' Token: 0x170000C7 RID: 199
		' (get) Token: 0x060005A5 RID: 1445 RVA: 0x00021EFE File Offset: 0x000200FE
		' (set) Token: 0x060005A6 RID: 1446 RVA: 0x00021F06 File Offset: 0x00020106
		Public Overridable Property Label77 As Label

		' Token: 0x170000C8 RID: 200
		' (get) Token: 0x060005A7 RID: 1447 RVA: 0x00021F0F File Offset: 0x0002010F
		' (set) Token: 0x060005A8 RID: 1448 RVA: 0x00021F17 File Offset: 0x00020117
		Public Overridable Property Label78 As Label

		' Token: 0x170000C9 RID: 201
		' (get) Token: 0x060005A9 RID: 1449 RVA: 0x00021F20 File Offset: 0x00020120
		' (set) Token: 0x060005AA RID: 1450 RVA: 0x00021F28 File Offset: 0x00020128
		Public Overridable Property Label29 As Label

		' Token: 0x170000CA RID: 202
		' (get) Token: 0x060005AB RID: 1451 RVA: 0x00021F31 File Offset: 0x00020131
		' (set) Token: 0x060005AC RID: 1452 RVA: 0x00021F3C File Offset: 0x0002013C
		Public Overridable Property Label31 As Label
			<CompilerGenerated()>
			Get
				Return Me._Label31
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Label)
				Dim value2 As EventHandler = AddressOf Me.Label31_Click
				Dim label As Label = Me._Label31
				If label IsNot Nothing Then
					RemoveHandler label.Click, value2
				End If
				Me._Label31 = value
				label = Me._Label31
				If label IsNot Nothing Then
					AddHandler label.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170000CB RID: 203
		' (get) Token: 0x060005AD RID: 1453 RVA: 0x00021F7F File Offset: 0x0002017F
		' (set) Token: 0x060005AE RID: 1454 RVA: 0x00021F87 File Offset: 0x00020187
		Public Overridable Property Label9 As Label

		' Token: 0x170000CC RID: 204
		' (get) Token: 0x060005AF RID: 1455 RVA: 0x00021F90 File Offset: 0x00020190
		' (set) Token: 0x060005B0 RID: 1456 RVA: 0x00021F98 File Offset: 0x00020198
		Public Overridable Property chkStartFrame As CheckBox

		' Token: 0x170000CD RID: 205
		' (get) Token: 0x060005B1 RID: 1457 RVA: 0x00021FA1 File Offset: 0x000201A1
		' (set) Token: 0x060005B2 RID: 1458 RVA: 0x00021FA9 File Offset: 0x000201A9
		Public Overridable Property chkZusatzStartSymbole As CheckBox

		' Token: 0x170000CE RID: 206
		' (get) Token: 0x060005B3 RID: 1459 RVA: 0x00021FB2 File Offset: 0x000201B2
		' (set) Token: 0x060005B4 RID: 1460 RVA: 0x00021FBA File Offset: 0x000201BA
		Public Overridable Property txtRollNoSize As TextBox

		' Token: 0x170000CF RID: 207
		' (get) Token: 0x060005B5 RID: 1461 RVA: 0x00021FC3 File Offset: 0x000201C3
		' (set) Token: 0x060005B6 RID: 1462 RVA: 0x00021FCC File Offset: 0x000201CC
		Public Overridable Property txtRollNoPrefix As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtRollNoPrefix
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtRollNoPrefix_TextChanged
				Dim txtRollNoPrefix As TextBox = Me._txtRollNoPrefix
				If txtRollNoPrefix IsNot Nothing Then
					RemoveHandler txtRollNoPrefix.TextChanged, value2
				End If
				Me._txtRollNoPrefix = value
				txtRollNoPrefix = Me._txtRollNoPrefix
				If txtRollNoPrefix IsNot Nothing Then
					AddHandler txtRollNoPrefix.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000D0 RID: 208
		' (get) Token: 0x060005B7 RID: 1463 RVA: 0x0002200F File Offset: 0x0002020F
		' (set) Token: 0x060005B8 RID: 1464 RVA: 0x00022018 File Offset: 0x00020218
		Public Overridable Property txtRollNoPostfix As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtRollNoPostfix
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtRollNoPostfix_TextChanged
				Dim txtRollNoPostfix As TextBox = Me._txtRollNoPostfix
				If txtRollNoPostfix IsNot Nothing Then
					RemoveHandler txtRollNoPostfix.TextChanged, value2
				End If
				Me._txtRollNoPostfix = value
				txtRollNoPostfix = Me._txtRollNoPostfix
				If txtRollNoPostfix IsNot Nothing Then
					AddHandler txtRollNoPostfix.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000D1 RID: 209
		' (get) Token: 0x060005B9 RID: 1465 RVA: 0x0002205B File Offset: 0x0002025B
		' (set) Token: 0x060005BA RID: 1466 RVA: 0x00022064 File Offset: 0x00020264
		Public Overridable Property txtRollNoLen As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtRollNoLen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtRollNoLen_TextChanged
				Dim txtRollNoLen As TextBox = Me._txtRollNoLen
				If txtRollNoLen IsNot Nothing Then
					RemoveHandler txtRollNoLen.TextChanged, value2
				End If
				Me._txtRollNoLen = value
				txtRollNoLen = Me._txtRollNoLen
				If txtRollNoLen IsNot Nothing Then
					AddHandler txtRollNoLen.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000D2 RID: 210
		' (get) Token: 0x060005BB RID: 1467 RVA: 0x000220A7 File Offset: 0x000202A7
		' (set) Token: 0x060005BC RID: 1468 RVA: 0x000220AF File Offset: 0x000202AF
		Public Overridable Property chkAddRollFrame As CheckBox

		' Token: 0x170000D3 RID: 211
		' (get) Token: 0x060005BD RID: 1469 RVA: 0x000220B8 File Offset: 0x000202B8
		' (set) Token: 0x060005BE RID: 1470 RVA: 0x000220C0 File Offset: 0x000202C0
		Public Overridable Property txtAddRollFrameSize As TextBox

		' Token: 0x170000D4 RID: 212
		' (get) Token: 0x060005BF RID: 1471 RVA: 0x000220C9 File Offset: 0x000202C9
		' (set) Token: 0x060005C0 RID: 1472 RVA: 0x000220D1 File Offset: 0x000202D1
		Public Overridable Property txtAddRollFrameLen As TextBox

		' Token: 0x170000D5 RID: 213
		' (get) Token: 0x060005C1 RID: 1473 RVA: 0x000220DA File Offset: 0x000202DA
		' (set) Token: 0x060005C2 RID: 1474 RVA: 0x000220E2 File Offset: 0x000202E2
		Public Overridable Property chkAddRollFrameInput As CheckBox

		' Token: 0x170000D6 RID: 214
		' (get) Token: 0x060005C3 RID: 1475 RVA: 0x000220EB File Offset: 0x000202EB
		' (set) Token: 0x060005C4 RID: 1476 RVA: 0x000220F3 File Offset: 0x000202F3
		Public Overridable Property _txtAddRollInfoPos_4 As TextBox

		' Token: 0x170000D7 RID: 215
		' (get) Token: 0x060005C5 RID: 1477 RVA: 0x000220FC File Offset: 0x000202FC
		' (set) Token: 0x060005C6 RID: 1478 RVA: 0x00022104 File Offset: 0x00020304
		Public Overridable Property _txtAddRollInfoPos_3 As TextBox

		' Token: 0x170000D8 RID: 216
		' (get) Token: 0x060005C7 RID: 1479 RVA: 0x0002210D File Offset: 0x0002030D
		' (set) Token: 0x060005C8 RID: 1480 RVA: 0x00022115 File Offset: 0x00020315
		Public Overridable Property _txtAddRollInfoPos_2 As TextBox

		' Token: 0x170000D9 RID: 217
		' (get) Token: 0x060005C9 RID: 1481 RVA: 0x0002211E File Offset: 0x0002031E
		' (set) Token: 0x060005CA RID: 1482 RVA: 0x00022126 File Offset: 0x00020326
		Public Overridable Property _txtAddRollInfoPos_1 As TextBox

		' Token: 0x170000DA RID: 218
		' (get) Token: 0x060005CB RID: 1483 RVA: 0x0002212F File Offset: 0x0002032F
		' (set) Token: 0x060005CC RID: 1484 RVA: 0x00022137 File Offset: 0x00020337
		Public Overridable Property Frame12 As GroupBox

		' Token: 0x170000DB RID: 219
		' (get) Token: 0x060005CD RID: 1485 RVA: 0x00022140 File Offset: 0x00020340
		' (set) Token: 0x060005CE RID: 1486 RVA: 0x00022148 File Offset: 0x00020348
		Public Overridable Property txtAddRollStartFrameSteps As TextBox

		' Token: 0x170000DC RID: 220
		' (get) Token: 0x060005CF RID: 1487 RVA: 0x00022151 File Offset: 0x00020351
		' (set) Token: 0x060005D0 RID: 1488 RVA: 0x00022159 File Offset: 0x00020359
		Public Overridable Property _tabFrames_TabPage0 As TabPage

		' Token: 0x170000DD RID: 221
		' (get) Token: 0x060005D1 RID: 1489 RVA: 0x00022162 File Offset: 0x00020362
		' (set) Token: 0x060005D2 RID: 1490 RVA: 0x0002216A File Offset: 0x0002036A
		Public Overridable Property chkSeparateFrame As CheckBox

		' Token: 0x170000DE RID: 222
		' (get) Token: 0x060005D3 RID: 1491 RVA: 0x00022173 File Offset: 0x00020373
		' (set) Token: 0x060005D4 RID: 1492 RVA: 0x0002217B File Offset: 0x0002037B
		Public Overridable Property chkUseFrameNo As CheckBox

		' Token: 0x170000DF RID: 223
		' (get) Token: 0x060005D5 RID: 1493 RVA: 0x00022184 File Offset: 0x00020384
		' (set) Token: 0x060005D6 RID: 1494 RVA: 0x0002218C File Offset: 0x0002038C
		Public Overridable Property _tabFrames_TabPage1 As TabPage

		' Token: 0x170000E0 RID: 224
		' (get) Token: 0x060005D7 RID: 1495 RVA: 0x00022195 File Offset: 0x00020395
		' (set) Token: 0x060005D8 RID: 1496 RVA: 0x0002219D File Offset: 0x0002039D
		Public Overridable Property cmbFortsetzungsLevel As ComboBox

		' Token: 0x170000E1 RID: 225
		' (get) Token: 0x060005D9 RID: 1497 RVA: 0x000221A6 File Offset: 0x000203A6
		' (set) Token: 0x060005DA RID: 1498 RVA: 0x000221AE File Offset: 0x000203AE
		Public Overridable Property chkNoSpecialSmybolesWhenContinuation As CheckBox

		' Token: 0x170000E2 RID: 226
		' (get) Token: 0x060005DB RID: 1499 RVA: 0x000221B7 File Offset: 0x000203B7
		' (set) Token: 0x060005DC RID: 1500 RVA: 0x000221BF File Offset: 0x000203BF
		Public Overridable Property txtFramesWiederholen As TextBox

		' Token: 0x170000E3 RID: 227
		' (get) Token: 0x060005DD RID: 1501 RVA: 0x000221C8 File Offset: 0x000203C8
		' (set) Token: 0x060005DE RID: 1502 RVA: 0x000221D0 File Offset: 0x000203D0
		Public Overridable Property chkFramesWiederholen As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkFramesWiederholen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkFramesWiederholen_CheckStateChanged
				Dim chkFramesWiederholen As CheckBox = Me._chkFramesWiederholen
				If chkFramesWiederholen IsNot Nothing Then
					RemoveHandler chkFramesWiederholen.CheckStateChanged, value2
				End If
				Me._chkFramesWiederholen = value
				chkFramesWiederholen = Me._chkFramesWiederholen
				If chkFramesWiederholen IsNot Nothing Then
					AddHandler chkFramesWiederholen.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000E4 RID: 228
		' (get) Token: 0x060005DF RID: 1503 RVA: 0x00022213 File Offset: 0x00020413
		' (set) Token: 0x060005E0 RID: 1504 RVA: 0x0002221C File Offset: 0x0002041C
		Public Overridable Property chkRolleistFortsetzung As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkRolleistFortsetzung
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkRolleistFortsetzung_CheckStateChanged
				Dim chkRolleistFortsetzung As CheckBox = Me._chkRolleistFortsetzung
				If chkRolleistFortsetzung IsNot Nothing Then
					RemoveHandler chkRolleistFortsetzung.CheckStateChanged, value2
				End If
				Me._chkRolleistFortsetzung = value
				chkRolleistFortsetzung = Me._chkRolleistFortsetzung
				If chkRolleistFortsetzung IsNot Nothing Then
					AddHandler chkRolleistFortsetzung.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000E5 RID: 229
		' (get) Token: 0x060005E1 RID: 1505 RVA: 0x0002225F File Offset: 0x0002045F
		' (set) Token: 0x060005E2 RID: 1506 RVA: 0x00022268 File Offset: 0x00020468
		Public Overridable Property chkRollewirdfortgesetzt As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkRollewirdfortgesetzt
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkRollewirdfortgesetzt_CheckStateChanged
				Dim chkRollewirdfortgesetzt As CheckBox = Me._chkRollewirdfortgesetzt
				If chkRollewirdfortgesetzt IsNot Nothing Then
					RemoveHandler chkRollewirdfortgesetzt.CheckStateChanged, value2
				End If
				Me._chkRollewirdfortgesetzt = value
				chkRollewirdfortgesetzt = Me._chkRollewirdfortgesetzt
				If chkRollewirdfortgesetzt IsNot Nothing Then
					AddHandler chkRollewirdfortgesetzt.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170000E6 RID: 230
		' (get) Token: 0x060005E3 RID: 1507 RVA: 0x000222AB File Offset: 0x000204AB
		' (set) Token: 0x060005E4 RID: 1508 RVA: 0x000222B3 File Offset: 0x000204B3
		Public Overridable Property chkBaende As CheckBox

		' Token: 0x170000E7 RID: 231
		' (get) Token: 0x060005E5 RID: 1509 RVA: 0x000222BC File Offset: 0x000204BC
		' (set) Token: 0x060005E6 RID: 1510 RVA: 0x000222C4 File Offset: 0x000204C4
		Public Overridable Property _label__6 As Label

		' Token: 0x170000E8 RID: 232
		' (get) Token: 0x060005E7 RID: 1511 RVA: 0x000222CD File Offset: 0x000204CD
		' (set) Token: 0x060005E8 RID: 1512 RVA: 0x000222D5 File Offset: 0x000204D5
		Public Overridable Property lblPfadFortsetzungsSymbole2 As Label

		' Token: 0x170000E9 RID: 233
		' (get) Token: 0x060005E9 RID: 1513 RVA: 0x000222DE File Offset: 0x000204DE
		' (set) Token: 0x060005EA RID: 1514 RVA: 0x000222E6 File Offset: 0x000204E6
		Public Overridable Property lblPfadFortsetzungsSymbole1 As Label

		' Token: 0x170000EA RID: 234
		' (get) Token: 0x060005EB RID: 1515 RVA: 0x000222EF File Offset: 0x000204EF
		' (set) Token: 0x060005EC RID: 1516 RVA: 0x000222F7 File Offset: 0x000204F7
		Public Overridable Property _tabFrames_TabPage2 As TabPage

		' Token: 0x170000EB RID: 235
		' (get) Token: 0x060005ED RID: 1517 RVA: 0x00022300 File Offset: 0x00020500
		' (set) Token: 0x060005EE RID: 1518 RVA: 0x00022308 File Offset: 0x00020508
		Public Overridable Property chkRollEndFrame As CheckBox

		' Token: 0x170000EC RID: 236
		' (get) Token: 0x060005EF RID: 1519 RVA: 0x00022311 File Offset: 0x00020511
		' (set) Token: 0x060005F0 RID: 1520 RVA: 0x00022319 File Offset: 0x00020519
		Public Overridable Property chkUseIndex As CheckBox

		' Token: 0x170000ED RID: 237
		' (get) Token: 0x060005F1 RID: 1521 RVA: 0x00022322 File Offset: 0x00020522
		' (set) Token: 0x060005F2 RID: 1522 RVA: 0x0002232A File Offset: 0x0002052A
		Public Overridable Property chkZusatzEndSymbole As CheckBox

		' Token: 0x170000EE RID: 238
		' (get) Token: 0x060005F3 RID: 1523 RVA: 0x00022333 File Offset: 0x00020533
		' (set) Token: 0x060005F4 RID: 1524 RVA: 0x0002233B File Offset: 0x0002053B
		Public Overridable Property lblPfadEndSymbole As Label

		' Token: 0x170000EF RID: 239
		' (get) Token: 0x060005F5 RID: 1525 RVA: 0x00022344 File Offset: 0x00020544
		' (set) Token: 0x060005F6 RID: 1526 RVA: 0x0002234C File Offset: 0x0002054C
		Public Overridable Property _tabFrames_TabPage3 As TabPage

		' Token: 0x170000F0 RID: 240
		' (get) Token: 0x060005F7 RID: 1527 RVA: 0x00022355 File Offset: 0x00020555
		' (set) Token: 0x060005F8 RID: 1528 RVA: 0x0002235D File Offset: 0x0002055D
		Public Overridable Property tabFrames As TabControl

		' Token: 0x170000F1 RID: 241
		' (get) Token: 0x060005F9 RID: 1529 RVA: 0x00022366 File Offset: 0x00020566
		' (set) Token: 0x060005FA RID: 1530 RVA: 0x00022370 File Offset: 0x00020570
		Public Overridable Property _tabSettings_TabPage3 As TabPage
			<CompilerGenerated()>
			Get
				Return Me.__tabSettings_TabPage3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TabPage)
				Dim value2 As EventHandler = AddressOf Me._tabSettings_TabPage3_Click
				Dim _tabSettings_TabPage As TabPage = Me.__tabSettings_TabPage3
				If _tabSettings_TabPage IsNot Nothing Then
					RemoveHandler _tabSettings_TabPage.Click, value2
				End If
				Me.__tabSettings_TabPage3 = value
				_tabSettings_TabPage = Me.__tabSettings_TabPage3
				If _tabSettings_TabPage IsNot Nothing Then
					AddHandler _tabSettings_TabPage.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170000F2 RID: 242
		' (get) Token: 0x060005FB RID: 1531 RVA: 0x000223B3 File Offset: 0x000205B3
		' (set) Token: 0x060005FC RID: 1532 RVA: 0x000223BB File Offset: 0x000205BB
		Public Overridable Property txtAnnoX As TextBox

		' Token: 0x170000F3 RID: 243
		' (get) Token: 0x060005FD RID: 1533 RVA: 0x000223C4 File Offset: 0x000205C4
		' (set) Token: 0x060005FE RID: 1534 RVA: 0x000223CC File Offset: 0x000205CC
		Public Overridable Property txtAnnoY As TextBox

		' Token: 0x170000F4 RID: 244
		' (get) Token: 0x060005FF RID: 1535 RVA: 0x000223D5 File Offset: 0x000205D5
		' (set) Token: 0x06000600 RID: 1536 RVA: 0x000223DD File Offset: 0x000205DD
		Public Overridable Property txtAnnoBreite As TextBox

		' Token: 0x170000F5 RID: 245
		' (get) Token: 0x06000601 RID: 1537 RVA: 0x000223E6 File Offset: 0x000205E6
		' (set) Token: 0x06000602 RID: 1538 RVA: 0x000223EE File Offset: 0x000205EE
		Public Overridable Property txtAnnoHoehe As TextBox

		' Token: 0x170000F6 RID: 246
		' (get) Token: 0x06000603 RID: 1539 RVA: 0x000223F7 File Offset: 0x000205F7
		' (set) Token: 0x06000604 RID: 1540 RVA: 0x000223FF File Offset: 0x000205FF
		Public Overridable Property _label__22 As Label

		' Token: 0x170000F7 RID: 247
		' (get) Token: 0x06000605 RID: 1541 RVA: 0x00022408 File Offset: 0x00020608
		' (set) Token: 0x06000606 RID: 1542 RVA: 0x00022410 File Offset: 0x00020610
		Public Overridable Property _label__21 As Label

		' Token: 0x170000F8 RID: 248
		' (get) Token: 0x06000607 RID: 1543 RVA: 0x00022419 File Offset: 0x00020619
		' (set) Token: 0x06000608 RID: 1544 RVA: 0x00022421 File Offset: 0x00020621
		Public Overridable Property _label38_2 As Label

		' Token: 0x170000F9 RID: 249
		' (get) Token: 0x06000609 RID: 1545 RVA: 0x0002242A File Offset: 0x0002062A
		' (set) Token: 0x0600060A RID: 1546 RVA: 0x00022432 File Offset: 0x00020632
		Public Overridable Property _label38_0 As Label

		' Token: 0x170000FA RID: 250
		' (get) Token: 0x0600060B RID: 1547 RVA: 0x0002243B File Offset: 0x0002063B
		' (set) Token: 0x0600060C RID: 1548 RVA: 0x00022443 File Offset: 0x00020643
		Public Overridable Property _label38_1 As Label

		' Token: 0x170000FB RID: 251
		' (get) Token: 0x0600060D RID: 1549 RVA: 0x0002244C File Offset: 0x0002064C
		' (set) Token: 0x0600060E RID: 1550 RVA: 0x00022454 File Offset: 0x00020654
		Public Overridable Property _label38_21 As Label

		' Token: 0x170000FC RID: 252
		' (get) Token: 0x0600060F RID: 1551 RVA: 0x0002245D File Offset: 0x0002065D
		' (set) Token: 0x06000610 RID: 1552 RVA: 0x00022465 File Offset: 0x00020665
		Public Overridable Property _Frame__2 As GroupBox

		' Token: 0x170000FD RID: 253
		' (get) Token: 0x06000611 RID: 1553 RVA: 0x0002246E File Offset: 0x0002066E
		' (set) Token: 0x06000612 RID: 1554 RVA: 0x00022476 File Offset: 0x00020676
		Public Overridable Property Text1 As TextBox

		' Token: 0x170000FE RID: 254
		' (get) Token: 0x06000613 RID: 1555 RVA: 0x0002247F File Offset: 0x0002067F
		' (set) Token: 0x06000614 RID: 1556 RVA: 0x00022487 File Offset: 0x00020687
		Public Overridable Property txtInfoTextAusrichtung As TextBox

		' Token: 0x170000FF RID: 255
		' (get) Token: 0x06000615 RID: 1557 RVA: 0x00022490 File Offset: 0x00020690
		' (set) Token: 0x06000616 RID: 1558 RVA: 0x00022498 File Offset: 0x00020698
		Public Overridable Property txtInfoTextX As TextBox

		' Token: 0x17000100 RID: 256
		' (get) Token: 0x06000617 RID: 1559 RVA: 0x000224A1 File Offset: 0x000206A1
		' (set) Token: 0x06000618 RID: 1560 RVA: 0x000224A9 File Offset: 0x000206A9
		Public Overridable Property txtInfoTextY As TextBox

		' Token: 0x17000101 RID: 257
		' (get) Token: 0x06000619 RID: 1561 RVA: 0x000224B2 File Offset: 0x000206B2
		' (set) Token: 0x0600061A RID: 1562 RVA: 0x000224BA File Offset: 0x000206BA
		Public Overridable Property txtInfoTextFont As TextBox

		' Token: 0x17000102 RID: 258
		' (get) Token: 0x0600061B RID: 1563 RVA: 0x000224C3 File Offset: 0x000206C3
		' (set) Token: 0x0600061C RID: 1564 RVA: 0x000224CB File Offset: 0x000206CB
		Public Overridable Property txtInfoTextGewicht As TextBox

		' Token: 0x17000103 RID: 259
		' (get) Token: 0x0600061D RID: 1565 RVA: 0x000224D4 File Offset: 0x000206D4
		' (set) Token: 0x0600061E RID: 1566 RVA: 0x000224DC File Offset: 0x000206DC
		Public Overridable Property Label80 As Label

		' Token: 0x17000104 RID: 260
		' (get) Token: 0x0600061F RID: 1567 RVA: 0x000224E5 File Offset: 0x000206E5
		' (set) Token: 0x06000620 RID: 1568 RVA: 0x000224ED File Offset: 0x000206ED
		Public Overridable Property _Label_12 As Label

		' Token: 0x17000105 RID: 261
		' (get) Token: 0x06000621 RID: 1569 RVA: 0x000224F6 File Offset: 0x000206F6
		' (set) Token: 0x06000622 RID: 1570 RVA: 0x000224FE File Offset: 0x000206FE
		Public Overridable Property _Label_8 As Label

		' Token: 0x17000106 RID: 262
		' (get) Token: 0x06000623 RID: 1571 RVA: 0x00022507 File Offset: 0x00020707
		' (set) Token: 0x06000624 RID: 1572 RVA: 0x0002250F File Offset: 0x0002070F
		Public Overridable Property Label65 As Label

		' Token: 0x17000107 RID: 263
		' (get) Token: 0x06000625 RID: 1573 RVA: 0x00022518 File Offset: 0x00020718
		' (set) Token: 0x06000626 RID: 1574 RVA: 0x00022520 File Offset: 0x00020720
		Public Overridable Property _label__14 As Label

		' Token: 0x17000108 RID: 264
		' (get) Token: 0x06000627 RID: 1575 RVA: 0x00022529 File Offset: 0x00020729
		' (set) Token: 0x06000628 RID: 1576 RVA: 0x00022531 File Offset: 0x00020731
		Public Overridable Property _label__15 As Label

		' Token: 0x17000109 RID: 265
		' (get) Token: 0x06000629 RID: 1577 RVA: 0x0002253A File Offset: 0x0002073A
		' (set) Token: 0x0600062A RID: 1578 RVA: 0x00022542 File Offset: 0x00020742
		Public Overridable Property Label55 As Label

		' Token: 0x1700010A RID: 266
		' (get) Token: 0x0600062B RID: 1579 RVA: 0x0002254B File Offset: 0x0002074B
		' (set) Token: 0x0600062C RID: 1580 RVA: 0x00022553 File Offset: 0x00020753
		Public Overridable Property Label54 As Label

		' Token: 0x1700010B RID: 267
		' (get) Token: 0x0600062D RID: 1581 RVA: 0x0002255C File Offset: 0x0002075C
		' (set) Token: 0x0600062E RID: 1582 RVA: 0x00022564 File Offset: 0x00020764
		Public Overridable Property _Frame__5 As GroupBox

		' Token: 0x1700010C RID: 268
		' (get) Token: 0x0600062F RID: 1583 RVA: 0x0002256D File Offset: 0x0002076D
		' (set) Token: 0x06000630 RID: 1584 RVA: 0x00022575 File Offset: 0x00020775
		Public Overridable Property txtInfoHoehe As TextBox

		' Token: 0x1700010D RID: 269
		' (get) Token: 0x06000631 RID: 1585 RVA: 0x0002257E File Offset: 0x0002077E
		' (set) Token: 0x06000632 RID: 1586 RVA: 0x00022586 File Offset: 0x00020786
		Public Overridable Property txtInfoBreite As TextBox

		' Token: 0x1700010E RID: 270
		' (get) Token: 0x06000633 RID: 1587 RVA: 0x0002258F File Offset: 0x0002078F
		' (set) Token: 0x06000634 RID: 1588 RVA: 0x00022597 File Offset: 0x00020797
		Public Overridable Property txtInfoY As TextBox

		' Token: 0x1700010F RID: 271
		' (get) Token: 0x06000635 RID: 1589 RVA: 0x000225A0 File Offset: 0x000207A0
		' (set) Token: 0x06000636 RID: 1590 RVA: 0x000225A8 File Offset: 0x000207A8
		Public Overridable Property txtInfoX As TextBox

		' Token: 0x17000110 RID: 272
		' (get) Token: 0x06000637 RID: 1591 RVA: 0x000225B1 File Offset: 0x000207B1
		' (set) Token: 0x06000638 RID: 1592 RVA: 0x000225B9 File Offset: 0x000207B9
		Public Overridable Property _label__3 As Label

		' Token: 0x17000111 RID: 273
		' (get) Token: 0x06000639 RID: 1593 RVA: 0x000225C2 File Offset: 0x000207C2
		' (set) Token: 0x0600063A RID: 1594 RVA: 0x000225CA File Offset: 0x000207CA
		Public Overridable Property _Label_52 As Label

		' Token: 0x17000112 RID: 274
		' (get) Token: 0x0600063B RID: 1595 RVA: 0x000225D3 File Offset: 0x000207D3
		' (set) Token: 0x0600063C RID: 1596 RVA: 0x000225DB File Offset: 0x000207DB
		Public Overridable Property _Label_49 As Label

		' Token: 0x17000113 RID: 275
		' (get) Token: 0x0600063D RID: 1597 RVA: 0x000225E4 File Offset: 0x000207E4
		' (set) Token: 0x0600063E RID: 1598 RVA: 0x000225EC File Offset: 0x000207EC
		Public Overridable Property _label__4 As Label

		' Token: 0x17000114 RID: 276
		' (get) Token: 0x0600063F RID: 1599 RVA: 0x000225F5 File Offset: 0x000207F5
		' (set) Token: 0x06000640 RID: 1600 RVA: 0x000225FD File Offset: 0x000207FD
		Public Overridable Property _label__13 As Label

		' Token: 0x17000115 RID: 277
		' (get) Token: 0x06000641 RID: 1601 RVA: 0x00022606 File Offset: 0x00020806
		' (set) Token: 0x06000642 RID: 1602 RVA: 0x0002260E File Offset: 0x0002080E
		Public Overridable Property _label__12 As Label

		' Token: 0x17000116 RID: 278
		' (get) Token: 0x06000643 RID: 1603 RVA: 0x00022617 File Offset: 0x00020817
		' (set) Token: 0x06000644 RID: 1604 RVA: 0x0002261F File Offset: 0x0002081F
		Public Overridable Property _Frame__3 As GroupBox

		' Token: 0x17000117 RID: 279
		' (get) Token: 0x06000645 RID: 1605 RVA: 0x00022628 File Offset: 0x00020828
		' (set) Token: 0x06000646 RID: 1606 RVA: 0x00022630 File Offset: 0x00020830
		Public Overridable Property txtQuerGewicht As TextBox

		' Token: 0x17000118 RID: 280
		' (get) Token: 0x06000647 RID: 1607 RVA: 0x00022639 File Offset: 0x00020839
		' (set) Token: 0x06000648 RID: 1608 RVA: 0x00022641 File Offset: 0x00020841
		Public Overridable Property txtQuerFont As TextBox

		' Token: 0x17000119 RID: 281
		' (get) Token: 0x06000649 RID: 1609 RVA: 0x0002264A File Offset: 0x0002084A
		' (set) Token: 0x0600064A RID: 1610 RVA: 0x00022652 File Offset: 0x00020852
		Public Overridable Property txtQuerAnnoY As TextBox

		' Token: 0x1700011A RID: 282
		' (get) Token: 0x0600064B RID: 1611 RVA: 0x0002265B File Offset: 0x0002085B
		' (set) Token: 0x0600064C RID: 1612 RVA: 0x00022663 File Offset: 0x00020863
		Public Overridable Property txtQuerAnnoX As TextBox

		' Token: 0x1700011B RID: 283
		' (get) Token: 0x0600064D RID: 1613 RVA: 0x0002266C File Offset: 0x0002086C
		' (set) Token: 0x0600064E RID: 1614 RVA: 0x00022674 File Offset: 0x00020874
		Public Overridable Property txtQuerAusrichtung As TextBox

		' Token: 0x1700011C RID: 284
		' (get) Token: 0x0600064F RID: 1615 RVA: 0x0002267D File Offset: 0x0002087D
		' (set) Token: 0x06000650 RID: 1616 RVA: 0x00022685 File Offset: 0x00020885
		Public Overridable Property Label73 As Label

		' Token: 0x1700011D RID: 285
		' (get) Token: 0x06000651 RID: 1617 RVA: 0x0002268E File Offset: 0x0002088E
		' (set) Token: 0x06000652 RID: 1618 RVA: 0x00022696 File Offset: 0x00020896
		Public Overridable Property Label72 As Label

		' Token: 0x1700011E RID: 286
		' (get) Token: 0x06000653 RID: 1619 RVA: 0x0002269F File Offset: 0x0002089F
		' (set) Token: 0x06000654 RID: 1620 RVA: 0x000226A7 File Offset: 0x000208A7
		Public Overridable Property _label__16 As Label

		' Token: 0x1700011F RID: 287
		' (get) Token: 0x06000655 RID: 1621 RVA: 0x000226B0 File Offset: 0x000208B0
		' (set) Token: 0x06000656 RID: 1622 RVA: 0x000226B8 File Offset: 0x000208B8
		Public Overridable Property _label__17 As Label

		' Token: 0x17000120 RID: 288
		' (get) Token: 0x06000657 RID: 1623 RVA: 0x000226C1 File Offset: 0x000208C1
		' (set) Token: 0x06000658 RID: 1624 RVA: 0x000226C9 File Offset: 0x000208C9
		Public Overridable Property Label69 As Label

		' Token: 0x17000121 RID: 289
		' (get) Token: 0x06000659 RID: 1625 RVA: 0x000226D2 File Offset: 0x000208D2
		' (set) Token: 0x0600065A RID: 1626 RVA: 0x000226DA File Offset: 0x000208DA
		Public Overridable Property _Label_7 As Label

		' Token: 0x17000122 RID: 290
		' (get) Token: 0x0600065B RID: 1627 RVA: 0x000226E3 File Offset: 0x000208E3
		' (set) Token: 0x0600065C RID: 1628 RVA: 0x000226EB File Offset: 0x000208EB
		Public Overridable Property _Label_11 As Label

		' Token: 0x17000123 RID: 291
		' (get) Token: 0x0600065D RID: 1629 RVA: 0x000226F4 File Offset: 0x000208F4
		' (set) Token: 0x0600065E RID: 1630 RVA: 0x000226FC File Offset: 0x000208FC
		Public Overridable Property _Frame__4 As GroupBox

		' Token: 0x17000124 RID: 292
		' (get) Token: 0x0600065F RID: 1631 RVA: 0x00022705 File Offset: 0x00020905
		' (set) Token: 0x06000660 RID: 1632 RVA: 0x0002270D File Offset: 0x0002090D
		Public Overridable Property txtQuerBlipX As TextBox

		' Token: 0x17000125 RID: 293
		' (get) Token: 0x06000661 RID: 1633 RVA: 0x00022716 File Offset: 0x00020916
		' (set) Token: 0x06000662 RID: 1634 RVA: 0x00022720 File Offset: 0x00020920
		Public Overridable Property txtQuerBlipY As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtQuerBlipY
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtQuerBlipY_TextChanged
				Dim txtQuerBlipY As TextBox = Me._txtQuerBlipY
				If txtQuerBlipY IsNot Nothing Then
					RemoveHandler txtQuerBlipY.TextChanged, value2
				End If
				Me._txtQuerBlipY = value
				txtQuerBlipY = Me._txtQuerBlipY
				If txtQuerBlipY IsNot Nothing Then
					AddHandler txtQuerBlipY.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000126 RID: 294
		' (get) Token: 0x06000663 RID: 1635 RVA: 0x00022763 File Offset: 0x00020963
		' (set) Token: 0x06000664 RID: 1636 RVA: 0x0002276C File Offset: 0x0002096C
		Public Overridable Property txtQuerBlipBreite As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtQuerBlipBreite
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtQuerBlipBreite_TextChanged
				Dim txtQuerBlipBreite As TextBox = Me._txtQuerBlipBreite
				If txtQuerBlipBreite IsNot Nothing Then
					RemoveHandler txtQuerBlipBreite.TextChanged, value2
				End If
				Me._txtQuerBlipBreite = value
				txtQuerBlipBreite = Me._txtQuerBlipBreite
				If txtQuerBlipBreite IsNot Nothing Then
					AddHandler txtQuerBlipBreite.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000127 RID: 295
		' (get) Token: 0x06000665 RID: 1637 RVA: 0x000227AF File Offset: 0x000209AF
		' (set) Token: 0x06000666 RID: 1638 RVA: 0x000227B8 File Offset: 0x000209B8
		Public Overridable Property txtQuerBlipHoehe As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtQuerBlipHoehe
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtQuerBlipHoehe_TextChanged
				Dim txtQuerBlipHoehe As TextBox = Me._txtQuerBlipHoehe
				If txtQuerBlipHoehe IsNot Nothing Then
					RemoveHandler txtQuerBlipHoehe.TextChanged, value2
				End If
				Me._txtQuerBlipHoehe = value
				txtQuerBlipHoehe = Me._txtQuerBlipHoehe
				If txtQuerBlipHoehe IsNot Nothing Then
					AddHandler txtQuerBlipHoehe.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000128 RID: 296
		' (get) Token: 0x06000667 RID: 1639 RVA: 0x000227FB File Offset: 0x000209FB
		' (set) Token: 0x06000668 RID: 1640 RVA: 0x00022803 File Offset: 0x00020A03
		Public Overridable Property _label__10 As Label

		' Token: 0x17000129 RID: 297
		' (get) Token: 0x06000669 RID: 1641 RVA: 0x0002280C File Offset: 0x00020A0C
		' (set) Token: 0x0600066A RID: 1642 RVA: 0x00022814 File Offset: 0x00020A14
		Public Overridable Property _label__11 As Label

		' Token: 0x1700012A RID: 298
		' (get) Token: 0x0600066B RID: 1643 RVA: 0x0002281D File Offset: 0x00020A1D
		' (set) Token: 0x0600066C RID: 1644 RVA: 0x00022825 File Offset: 0x00020A25
		Public Overridable Property _label__2 As Label

		' Token: 0x1700012B RID: 299
		' (get) Token: 0x0600066D RID: 1645 RVA: 0x0002282E File Offset: 0x00020A2E
		' (set) Token: 0x0600066E RID: 1646 RVA: 0x00022836 File Offset: 0x00020A36
		Public Overridable Property _Label_61 As Label

		' Token: 0x1700012C RID: 300
		' (get) Token: 0x0600066F RID: 1647 RVA: 0x0002283F File Offset: 0x00020A3F
		' (set) Token: 0x06000670 RID: 1648 RVA: 0x00022847 File Offset: 0x00020A47
		Public Overridable Property _Label_60 As Label

		' Token: 0x1700012D RID: 301
		' (get) Token: 0x06000671 RID: 1649 RVA: 0x00022850 File Offset: 0x00020A50
		' (set) Token: 0x06000672 RID: 1650 RVA: 0x00022858 File Offset: 0x00020A58
		Public Overridable Property _label__1 As Label

		' Token: 0x1700012E RID: 302
		' (get) Token: 0x06000673 RID: 1651 RVA: 0x00022861 File Offset: 0x00020A61
		' (set) Token: 0x06000674 RID: 1652 RVA: 0x00022869 File Offset: 0x00020A69
		Public Overridable Property _Frame__1 As GroupBox

		' Token: 0x1700012F RID: 303
		' (get) Token: 0x06000675 RID: 1653 RVA: 0x00022872 File Offset: 0x00020A72
		' (set) Token: 0x06000676 RID: 1654 RVA: 0x0002287A File Offset: 0x00020A7A
		Public Overridable Property txtQuerBreite As TextBox

		' Token: 0x17000130 RID: 304
		' (get) Token: 0x06000677 RID: 1655 RVA: 0x00022883 File Offset: 0x00020A83
		' (set) Token: 0x06000678 RID: 1656 RVA: 0x0002288B File Offset: 0x00020A8B
		Public Overridable Property txtQuerHoehe As TextBox

		' Token: 0x17000131 RID: 305
		' (get) Token: 0x06000679 RID: 1657 RVA: 0x00022894 File Offset: 0x00020A94
		' (set) Token: 0x0600067A RID: 1658 RVA: 0x0002289C File Offset: 0x00020A9C
		Public Overridable Property txtQuerX As TextBox

		' Token: 0x17000132 RID: 306
		' (get) Token: 0x0600067B RID: 1659 RVA: 0x000228A5 File Offset: 0x00020AA5
		' (set) Token: 0x0600067C RID: 1660 RVA: 0x000228AD File Offset: 0x00020AAD
		Public Overridable Property txtQuerY As TextBox

		' Token: 0x17000133 RID: 307
		' (get) Token: 0x0600067D RID: 1661 RVA: 0x000228B6 File Offset: 0x00020AB6
		' (set) Token: 0x0600067E RID: 1662 RVA: 0x000228BE File Offset: 0x00020ABE
		Public Overridable Property _label__0 As Label

		' Token: 0x17000134 RID: 308
		' (get) Token: 0x0600067F RID: 1663 RVA: 0x000228C7 File Offset: 0x00020AC7
		' (set) Token: 0x06000680 RID: 1664 RVA: 0x000228CF File Offset: 0x00020ACF
		Public Overridable Property _Label_51 As Label

		' Token: 0x17000135 RID: 309
		' (get) Token: 0x06000681 RID: 1665 RVA: 0x000228D8 File Offset: 0x00020AD8
		' (set) Token: 0x06000682 RID: 1666 RVA: 0x000228E0 File Offset: 0x00020AE0
		Public Overridable Property _Label_50 As Label

		' Token: 0x17000136 RID: 310
		' (get) Token: 0x06000683 RID: 1667 RVA: 0x000228E9 File Offset: 0x00020AE9
		' (set) Token: 0x06000684 RID: 1668 RVA: 0x000228F1 File Offset: 0x00020AF1
		Public Overridable Property _label__44 As Label

		' Token: 0x17000137 RID: 311
		' (get) Token: 0x06000685 RID: 1669 RVA: 0x000228FA File Offset: 0x00020AFA
		' (set) Token: 0x06000686 RID: 1670 RVA: 0x00022902 File Offset: 0x00020B02
		Public Overridable Property _label__8 As Label

		' Token: 0x17000138 RID: 312
		' (get) Token: 0x06000687 RID: 1671 RVA: 0x0002290B File Offset: 0x00020B0B
		' (set) Token: 0x06000688 RID: 1672 RVA: 0x00022913 File Offset: 0x00020B13
		Public Overridable Property _label__9 As Label

		' Token: 0x17000139 RID: 313
		' (get) Token: 0x06000689 RID: 1673 RVA: 0x0002291C File Offset: 0x00020B1C
		' (set) Token: 0x0600068A RID: 1674 RVA: 0x00022924 File Offset: 0x00020B24
		Public Overridable Property _Frame__0 As GroupBox

		' Token: 0x1700013A RID: 314
		' (get) Token: 0x0600068B RID: 1675 RVA: 0x0002292D File Offset: 0x00020B2D
		' (set) Token: 0x0600068C RID: 1676 RVA: 0x00022935 File Offset: 0x00020B35
		Public Overridable Property _tabSettings_TabPage4 As TabPage

		' Token: 0x1700013B RID: 315
		' (get) Token: 0x0600068D RID: 1677 RVA: 0x0002293E File Offset: 0x00020B3E
		' (set) Token: 0x0600068E RID: 1678 RVA: 0x00022946 File Offset: 0x00020B46
		Public Overridable Property Label2 As Label

		' Token: 0x1700013C RID: 316
		' (get) Token: 0x0600068F RID: 1679 RVA: 0x0002294F File Offset: 0x00020B4F
		' (set) Token: 0x06000690 RID: 1680 RVA: 0x00022957 File Offset: 0x00020B57
		Public Overridable Property Label17 As Label

		' Token: 0x1700013D RID: 317
		' (get) Token: 0x06000691 RID: 1681 RVA: 0x00022960 File Offset: 0x00020B60
		' (set) Token: 0x06000692 RID: 1682 RVA: 0x00022968 File Offset: 0x00020B68
		Public Overridable Property Label18 As Label

		' Token: 0x1700013E RID: 318
		' (get) Token: 0x06000693 RID: 1683 RVA: 0x00022971 File Offset: 0x00020B71
		' (set) Token: 0x06000694 RID: 1684 RVA: 0x00022979 File Offset: 0x00020B79
		Public Overridable Property _Label19_0 As Label

		' Token: 0x1700013F RID: 319
		' (get) Token: 0x06000695 RID: 1685 RVA: 0x00022982 File Offset: 0x00020B82
		' (set) Token: 0x06000696 RID: 1686 RVA: 0x0002298A File Offset: 0x00020B8A
		Public Overridable Property Label20 As Label

		' Token: 0x17000140 RID: 320
		' (get) Token: 0x06000697 RID: 1687 RVA: 0x00022993 File Offset: 0x00020B93
		' (set) Token: 0x06000698 RID: 1688 RVA: 0x0002299B File Offset: 0x00020B9B
		Public Overridable Property Label28 As Label

		' Token: 0x17000141 RID: 321
		' (get) Token: 0x06000699 RID: 1689 RVA: 0x000229A4 File Offset: 0x00020BA4
		' (set) Token: 0x0600069A RID: 1690 RVA: 0x000229AC File Offset: 0x00020BAC
		Public Overridable Property _label__29 As Label

		' Token: 0x17000142 RID: 322
		' (get) Token: 0x0600069B RID: 1691 RVA: 0x000229B5 File Offset: 0x00020BB5
		' (set) Token: 0x0600069C RID: 1692 RVA: 0x000229BD File Offset: 0x00020BBD
		Public Overridable Property chkSplit As CheckBox

		' Token: 0x17000143 RID: 323
		' (get) Token: 0x0600069D RID: 1693 RVA: 0x000229C6 File Offset: 0x00020BC6
		' (set) Token: 0x0600069E RID: 1694 RVA: 0x000229D0 File Offset: 0x00020BD0
		Public Overridable Property cmbMaxDocumentSize As ComboBox
			<CompilerGenerated()>
			Get
				Return Me._cmbMaxDocumentSize
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ComboBox)
				Dim value2 As EventHandler = AddressOf Me.cmbMaxDocumentSize_SelectedIndexChanged
				Dim cmbMaxDocumentSize As ComboBox = Me._cmbMaxDocumentSize
				If cmbMaxDocumentSize IsNot Nothing Then
					RemoveHandler cmbMaxDocumentSize.SelectedIndexChanged, value2
				End If
				Me._cmbMaxDocumentSize = value
				cmbMaxDocumentSize = Me._cmbMaxDocumentSize
				If cmbMaxDocumentSize IsNot Nothing Then
					AddHandler cmbMaxDocumentSize.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000144 RID: 324
		' (get) Token: 0x0600069F RID: 1695 RVA: 0x00022A13 File Offset: 0x00020C13
		' (set) Token: 0x060006A0 RID: 1696 RVA: 0x00022A1B File Offset: 0x00020C1B
		Public Overridable Property txtSplitBreite As TextBox

		' Token: 0x17000145 RID: 325
		' (get) Token: 0x060006A1 RID: 1697 RVA: 0x00022A24 File Offset: 0x00020C24
		' (set) Token: 0x060006A2 RID: 1698 RVA: 0x00022A2C File Offset: 0x00020C2C
		Public Overridable Property txtSplitLaenge As TextBox

		' Token: 0x17000146 RID: 326
		' (get) Token: 0x060006A3 RID: 1699 RVA: 0x00022A35 File Offset: 0x00020C35
		' (set) Token: 0x060006A4 RID: 1700 RVA: 0x00022A3D File Offset: 0x00020C3D
		Public Overridable Property cmbSplitCount As ComboBox

		' Token: 0x17000147 RID: 327
		' (get) Token: 0x060006A5 RID: 1701 RVA: 0x00022A46 File Offset: 0x00020C46
		' (set) Token: 0x060006A6 RID: 1702 RVA: 0x00022A4E File Offset: 0x00020C4E
		Public Overridable Property txtOverSize As TextBox

		' Token: 0x17000148 RID: 328
		' (get) Token: 0x060006A7 RID: 1703 RVA: 0x00022A57 File Offset: 0x00020C57
		' (set) Token: 0x060006A8 RID: 1704 RVA: 0x00022A5F File Offset: 0x00020C5F
		Public Overridable Property _tabSettings_TabPage5 As TabPage

		' Token: 0x17000149 RID: 329
		' (get) Token: 0x060006A9 RID: 1705 RVA: 0x00022A68 File Offset: 0x00020C68
		' (set) Token: 0x060006AA RID: 1706 RVA: 0x00022A70 File Offset: 0x00020C70
		Public Overridable Property _txtVerschluss_1 As TextBox

		' Token: 0x1700014A RID: 330
		' (get) Token: 0x060006AB RID: 1707 RVA: 0x00022A79 File Offset: 0x00020C79
		' (set) Token: 0x060006AC RID: 1708 RVA: 0x00022A84 File Offset: 0x00020C84
		Public Overridable Property chkFesteBelegzahl As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkFesteBelegzahl
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkFesteBelegzahl_CheckStateChanged
				Dim chkFesteBelegzahl As CheckBox = Me._chkFesteBelegzahl
				If chkFesteBelegzahl IsNot Nothing Then
					RemoveHandler chkFesteBelegzahl.CheckStateChanged, value2
				End If
				Me._chkFesteBelegzahl = value
				chkFesteBelegzahl = Me._chkFesteBelegzahl
				If chkFesteBelegzahl IsNot Nothing Then
					AddHandler chkFesteBelegzahl.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700014B RID: 331
		' (get) Token: 0x060006AD RID: 1709 RVA: 0x00022AC7 File Offset: 0x00020CC7
		' (set) Token: 0x060006AE RID: 1710 RVA: 0x00022ACF File Offset: 0x00020CCF
		Public Overridable Property txtAddStepLevel3 As TextBox

		' Token: 0x1700014C RID: 332
		' (get) Token: 0x060006AF RID: 1711 RVA: 0x00022AD8 File Offset: 0x00020CD8
		' (set) Token: 0x060006B0 RID: 1712 RVA: 0x00022AE0 File Offset: 0x00020CE0
		Public Overridable Property txtAddStepLevel2 As TextBox

		' Token: 0x1700014D RID: 333
		' (get) Token: 0x060006B1 RID: 1713 RVA: 0x00022AE9 File Offset: 0x00020CE9
		' (set) Token: 0x060006B2 RID: 1714 RVA: 0x00022AF1 File Offset: 0x00020CF1
		Public Overridable Property chkTrailerInfoFrames As CheckBox

		' Token: 0x1700014E RID: 334
		' (get) Token: 0x060006B3 RID: 1715 RVA: 0x00022AFA File Offset: 0x00020CFA
		' (set) Token: 0x060006B4 RID: 1716 RVA: 0x00022B02 File Offset: 0x00020D02
		Public Overridable Property chkAutoTrailer As CheckBox

		' Token: 0x1700014F RID: 335
		' (get) Token: 0x060006B5 RID: 1717 RVA: 0x00022B0B File Offset: 0x00020D0B
		' (set) Token: 0x060006B6 RID: 1718 RVA: 0x00022B13 File Offset: 0x00020D13
		Public Overridable Property txtAutoTrailerDistance As TextBox

		' Token: 0x17000150 RID: 336
		' (get) Token: 0x060006B7 RID: 1719 RVA: 0x00022B1C File Offset: 0x00020D1C
		' (set) Token: 0x060006B8 RID: 1720 RVA: 0x00022B24 File Offset: 0x00020D24
		Public Overridable Property txtAutoTrailerLength As TextBox

		' Token: 0x17000151 RID: 337
		' (get) Token: 0x060006B9 RID: 1721 RVA: 0x00022B2D File Offset: 0x00020D2D
		' (set) Token: 0x060006BA RID: 1722 RVA: 0x00022B35 File Offset: 0x00020D35
		Public Overridable Property _label__38 As Label

		' Token: 0x17000152 RID: 338
		' (get) Token: 0x060006BB RID: 1723 RVA: 0x00022B3E File Offset: 0x00020D3E
		' (set) Token: 0x060006BC RID: 1724 RVA: 0x00022B46 File Offset: 0x00020D46
		Public Overridable Property _label__39 As Label

		' Token: 0x17000153 RID: 339
		' (get) Token: 0x060006BD RID: 1725 RVA: 0x00022B4F File Offset: 0x00020D4F
		' (set) Token: 0x060006BE RID: 1726 RVA: 0x00022B57 File Offset: 0x00020D57
		Public Overridable Property Label40 As Label

		' Token: 0x17000154 RID: 340
		' (get) Token: 0x060006BF RID: 1727 RVA: 0x00022B60 File Offset: 0x00020D60
		' (set) Token: 0x060006C0 RID: 1728 RVA: 0x00022B68 File Offset: 0x00020D68
		Public Overridable Property Label41 As Label

		' Token: 0x17000155 RID: 341
		' (get) Token: 0x060006C1 RID: 1729 RVA: 0x00022B71 File Offset: 0x00020D71
		' (set) Token: 0x060006C2 RID: 1730 RVA: 0x00022B79 File Offset: 0x00020D79
		Public Overridable Property Frame7 As GroupBox

		' Token: 0x17000156 RID: 342
		' (get) Token: 0x060006C3 RID: 1731 RVA: 0x00022B82 File Offset: 0x00020D82
		' (set) Token: 0x060006C4 RID: 1732 RVA: 0x00022B8C File Offset: 0x00020D8C
		Public Overridable Property txtSchritteBelichtung As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtSchritteBelichtung
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtSchritteBelichtung_TextChanged
				Dim txtSchritteBelichtung As TextBox = Me._txtSchritteBelichtung
				If txtSchritteBelichtung IsNot Nothing Then
					RemoveHandler txtSchritteBelichtung.TextChanged, value2
				End If
				Me._txtSchritteBelichtung = value
				txtSchritteBelichtung = Me._txtSchritteBelichtung
				If txtSchritteBelichtung IsNot Nothing Then
					AddHandler txtSchritteBelichtung.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000157 RID: 343
		' (get) Token: 0x060006C5 RID: 1733 RVA: 0x00022BCF File Offset: 0x00020DCF
		' (set) Token: 0x060006C6 RID: 1734 RVA: 0x00022BD8 File Offset: 0x00020DD8
		Public Overridable Property chkStepsImageToImage As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkStepsImageToImage
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkStepsImageToImage_CheckStateChanged
				Dim chkStepsImageToImage As CheckBox = Me._chkStepsImageToImage
				If chkStepsImageToImage IsNot Nothing Then
					RemoveHandler chkStepsImageToImage.CheckStateChanged, value2
				End If
				Me._chkStepsImageToImage = value
				chkStepsImageToImage = Me._chkStepsImageToImage
				If chkStepsImageToImage IsNot Nothing Then
					AddHandler chkStepsImageToImage.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000158 RID: 344
		' (get) Token: 0x060006C7 RID: 1735 RVA: 0x00022C1B File Offset: 0x00020E1B
		' (set) Token: 0x060006C8 RID: 1736 RVA: 0x00022C24 File Offset: 0x00020E24
		Public Overridable Property txtSchritte As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtSchritte
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtSchritte_Leave
				Dim txtSchritte As TextBox = Me._txtSchritte
				If txtSchritte IsNot Nothing Then
					RemoveHandler txtSchritte.Leave, value2
				End If
				Me._txtSchritte = value
				txtSchritte = Me._txtSchritte
				If txtSchritte IsNot Nothing Then
					AddHandler txtSchritte.Leave, value2
				End If
			End Set
		End Property

		' Token: 0x17000159 RID: 345
		' (get) Token: 0x060006C9 RID: 1737 RVA: 0x00022C67 File Offset: 0x00020E67
		' (set) Token: 0x060006CA RID: 1738 RVA: 0x00022C6F File Offset: 0x00020E6F
		Public Overridable Property _txtVerschluss_0 As TextBox

		' Token: 0x1700015A RID: 346
		' (get) Token: 0x060006CB RID: 1739 RVA: 0x00022C78 File Offset: 0x00020E78
		' (set) Token: 0x060006CC RID: 1740 RVA: 0x00022C80 File Offset: 0x00020E80
		Public Overridable Property txtZusatzBelichtung As TextBox

		' Token: 0x1700015B RID: 347
		' (get) Token: 0x060006CD RID: 1741 RVA: 0x00022C89 File Offset: 0x00020E89
		' (set) Token: 0x060006CE RID: 1742 RVA: 0x00022C91 File Offset: 0x00020E91
		Public Overridable Property _Label96_4 As Label

		' Token: 0x1700015C RID: 348
		' (get) Token: 0x060006CF RID: 1743 RVA: 0x00022C9A File Offset: 0x00020E9A
		' (set) Token: 0x060006D0 RID: 1744 RVA: 0x00022CA2 File Offset: 0x00020EA2
		Public Overridable Property _label__20 As Label

		' Token: 0x1700015D RID: 349
		' (get) Token: 0x060006D1 RID: 1745 RVA: 0x00022CAB File Offset: 0x00020EAB
		' (set) Token: 0x060006D2 RID: 1746 RVA: 0x00022CB3 File Offset: 0x00020EB3
		Public Overridable Property Label22 As Label

		' Token: 0x1700015E RID: 350
		' (get) Token: 0x060006D3 RID: 1747 RVA: 0x00022CBC File Offset: 0x00020EBC
		' (set) Token: 0x060006D4 RID: 1748 RVA: 0x00022CC4 File Offset: 0x00020EC4
		Public Overridable Property _label__18 As Label

		' Token: 0x1700015F RID: 351
		' (get) Token: 0x060006D5 RID: 1749 RVA: 0x00022CCD File Offset: 0x00020ECD
		' (set) Token: 0x060006D6 RID: 1750 RVA: 0x00022CD5 File Offset: 0x00020ED5
		Public Overridable Property Label8 As Label

		' Token: 0x17000160 RID: 352
		' (get) Token: 0x060006D7 RID: 1751 RVA: 0x00022CDE File Offset: 0x00020EDE
		' (set) Token: 0x060006D8 RID: 1752 RVA: 0x00022CE6 File Offset: 0x00020EE6
		Public Overridable Property Image1 As PictureBox

		' Token: 0x17000161 RID: 353
		' (get) Token: 0x060006D9 RID: 1753 RVA: 0x00022CEF File Offset: 0x00020EEF
		' (set) Token: 0x060006DA RID: 1754 RVA: 0x00022CF7 File Offset: 0x00020EF7
		Public Overridable Property Label35 As Label

		' Token: 0x17000162 RID: 354
		' (get) Token: 0x060006DB RID: 1755 RVA: 0x00022D00 File Offset: 0x00020F00
		' (set) Token: 0x060006DC RID: 1756 RVA: 0x00022D08 File Offset: 0x00020F08
		Public Overridable Property _label__31 As Label

		' Token: 0x17000163 RID: 355
		' (get) Token: 0x060006DD RID: 1757 RVA: 0x00022D11 File Offset: 0x00020F11
		' (set) Token: 0x060006DE RID: 1758 RVA: 0x00022D19 File Offset: 0x00020F19
		Public Overridable Property Label30 As Label

		' Token: 0x17000164 RID: 356
		' (get) Token: 0x060006DF RID: 1759 RVA: 0x00022D22 File Offset: 0x00020F22
		' (set) Token: 0x060006E0 RID: 1760 RVA: 0x00022D2A File Offset: 0x00020F2A
		Public Overridable Property Label26 As Label

		' Token: 0x17000165 RID: 357
		' (get) Token: 0x060006E1 RID: 1761 RVA: 0x00022D33 File Offset: 0x00020F33
		' (set) Token: 0x060006E2 RID: 1762 RVA: 0x00022D3B File Offset: 0x00020F3B
		Public Overridable Property Label25 As Label

		' Token: 0x17000166 RID: 358
		' (get) Token: 0x060006E3 RID: 1763 RVA: 0x00022D44 File Offset: 0x00020F44
		' (set) Token: 0x060006E4 RID: 1764 RVA: 0x00022D4C File Offset: 0x00020F4C
		Public Overridable Property _label__46 As Label

		' Token: 0x17000167 RID: 359
		' (get) Token: 0x060006E5 RID: 1765 RVA: 0x00022D55 File Offset: 0x00020F55
		' (set) Token: 0x060006E6 RID: 1766 RVA: 0x00022D5D File Offset: 0x00020F5D
		Public Overridable Property Shape5 As Panel

		' Token: 0x17000168 RID: 360
		' (get) Token: 0x060006E7 RID: 1767 RVA: 0x00022D66 File Offset: 0x00020F66
		' (set) Token: 0x060006E8 RID: 1768 RVA: 0x00022D6E File Offset: 0x00020F6E
		Public Overridable Property _tabSettings_TabPage6 As TabPage

		' Token: 0x17000169 RID: 361
		' (get) Token: 0x060006E9 RID: 1769 RVA: 0x00022D77 File Offset: 0x00020F77
		' (set) Token: 0x060006EA RID: 1770 RVA: 0x00022D7F File Offset: 0x00020F7F
		Public Overridable Property chkJPEG As CheckBox

		' Token: 0x1700016A RID: 362
		' (get) Token: 0x060006EB RID: 1771 RVA: 0x00022D88 File Offset: 0x00020F88
		' (set) Token: 0x060006EC RID: 1772 RVA: 0x00022D90 File Offset: 0x00020F90
		Public Overridable Property cmbPDFReso As ComboBox

		' Token: 0x1700016B RID: 363
		' (get) Token: 0x060006ED RID: 1773 RVA: 0x00022D99 File Offset: 0x00020F99
		' (set) Token: 0x060006EE RID: 1774 RVA: 0x00022DA1 File Offset: 0x00020FA1
		Public Overridable Property Label42 As Label

		' Token: 0x1700016C RID: 364
		' (get) Token: 0x060006EF RID: 1775 RVA: 0x00022DAA File Offset: 0x00020FAA
		' (set) Token: 0x060006F0 RID: 1776 RVA: 0x00022DB2 File Offset: 0x00020FB2
		Public Overridable Property Label27 As Label

		' Token: 0x1700016D RID: 365
		' (get) Token: 0x060006F1 RID: 1777 RVA: 0x00022DBB File Offset: 0x00020FBB
		' (set) Token: 0x060006F2 RID: 1778 RVA: 0x00022DC3 File Offset: 0x00020FC3
		Public Overridable Property Label94 As Label

		' Token: 0x1700016E RID: 366
		' (get) Token: 0x060006F3 RID: 1779 RVA: 0x00022DCC File Offset: 0x00020FCC
		' (set) Token: 0x060006F4 RID: 1780 RVA: 0x00022DD4 File Offset: 0x00020FD4
		Public Overridable Property _tabSettings_TabPage7 As TabPage

		' Token: 0x1700016F RID: 367
		' (get) Token: 0x060006F5 RID: 1781 RVA: 0x00022DDD File Offset: 0x00020FDD
		' (set) Token: 0x060006F6 RID: 1782 RVA: 0x00022DE8 File Offset: 0x00020FE8
		Public Overridable Property chkFrame As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkFrame
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkFrame_CheckedChanged
				Dim chkFrame As CheckBox = Me._chkFrame
				If chkFrame IsNot Nothing Then
					RemoveHandler chkFrame.CheckedChanged, value2
				End If
				Me._chkFrame = value
				chkFrame = Me._chkFrame
				If chkFrame IsNot Nothing Then
					AddHandler chkFrame.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000170 RID: 368
		' (get) Token: 0x060006F7 RID: 1783 RVA: 0x00022E2B File Offset: 0x0002102B
		' (set) Token: 0x060006F8 RID: 1784 RVA: 0x00022E34 File Offset: 0x00021034
		Public Overridable Property chkInvers As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkInvers
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkInvers_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkInvers_CheckedChanged
				Dim chkInvers As CheckBox = Me._chkInvers
				If chkInvers IsNot Nothing Then
					RemoveHandler chkInvers.CheckStateChanged, value2
					RemoveHandler chkInvers.CheckedChanged, value3
				End If
				Me._chkInvers = value
				chkInvers = Me._chkInvers
				If chkInvers IsNot Nothing Then
					AddHandler chkInvers.CheckStateChanged, value2
					AddHandler chkInvers.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x17000171 RID: 369
		' (get) Token: 0x060006F9 RID: 1785 RVA: 0x00022E92 File Offset: 0x00021092
		' (set) Token: 0x060006FA RID: 1786 RVA: 0x00022E9A File Offset: 0x0002109A
		Public Overridable Property Frame4 As GroupBox

		' Token: 0x17000172 RID: 370
		' (get) Token: 0x060006FB RID: 1787 RVA: 0x00022EA3 File Offset: 0x000210A3
		' (set) Token: 0x060006FC RID: 1788 RVA: 0x00022EAB File Offset: 0x000210AB
		Public Overridable Property _tabSettings_TabPage8 As TabPage

		' Token: 0x17000173 RID: 371
		' (get) Token: 0x060006FD RID: 1789 RVA: 0x00022EB4 File Offset: 0x000210B4
		' (set) Token: 0x060006FE RID: 1790 RVA: 0x00022EBC File Offset: 0x000210BC
		Public Overridable Property lstTrailer As CheckedListBox

		' Token: 0x17000174 RID: 372
		' (get) Token: 0x060006FF RID: 1791 RVA: 0x00022EC5 File Offset: 0x000210C5
		' (set) Token: 0x06000700 RID: 1792 RVA: 0x00022ED0 File Offset: 0x000210D0
		Public Overridable Property cmdClearLogPath As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdClearLogPath
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdClearLogPath_Click
				Dim cmdClearLogPath As Button = Me._cmdClearLogPath
				If cmdClearLogPath IsNot Nothing Then
					RemoveHandler cmdClearLogPath.Click, value2
				End If
				Me._cmdClearLogPath = value
				cmdClearLogPath = Me._cmdClearLogPath
				If cmdClearLogPath IsNot Nothing Then
					AddHandler cmdClearLogPath.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000175 RID: 373
		' (get) Token: 0x06000701 RID: 1793 RVA: 0x00022F13 File Offset: 0x00021113
		' (set) Token: 0x06000702 RID: 1794 RVA: 0x00022F1C File Offset: 0x0002111C
		Public Overridable Property lstRecords As CheckedListBox
			<CompilerGenerated()>
			Get
				Return Me._lstRecords
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckedListBox)
				Dim value2 As EventHandler = AddressOf Me.lstRecords_SelectedIndexChanged
				Dim lstRecords As CheckedListBox = Me._lstRecords
				If lstRecords IsNot Nothing Then
					RemoveHandler lstRecords.SelectedIndexChanged, value2
				End If
				Me._lstRecords = value
				lstRecords = Me._lstRecords
				If lstRecords IsNot Nothing Then
					AddHandler lstRecords.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000176 RID: 374
		' (get) Token: 0x06000703 RID: 1795 RVA: 0x00022F5F File Offset: 0x0002115F
		' (set) Token: 0x06000704 RID: 1796 RVA: 0x00022F67 File Offset: 0x00021167
		Public Overridable Property lstHeader As CheckedListBox

		' Token: 0x17000177 RID: 375
		' (get) Token: 0x06000705 RID: 1797 RVA: 0x00022F70 File Offset: 0x00021170
		' (set) Token: 0x06000706 RID: 1798 RVA: 0x00022F78 File Offset: 0x00021178
		Public Overridable Property cmbDelimiter As ComboBox

		' Token: 0x17000178 RID: 376
		' (get) Token: 0x06000707 RID: 1799 RVA: 0x00022F81 File Offset: 0x00021181
		' (set) Token: 0x06000708 RID: 1800 RVA: 0x00022F8C File Offset: 0x0002118C
		Public Overridable Property cmdSetLogPath As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdSetLogPath
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdSetLogPath_Click
				Dim cmdSetLogPath As Button = Me._cmdSetLogPath
				If cmdSetLogPath IsNot Nothing Then
					RemoveHandler cmdSetLogPath.Click, value2
				End If
				Me._cmdSetLogPath = value
				cmdSetLogPath = Me._cmdSetLogPath
				If cmdSetLogPath IsNot Nothing Then
					AddHandler cmdSetLogPath.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000179 RID: 377
		' (get) Token: 0x06000709 RID: 1801 RVA: 0x00022FCF File Offset: 0x000211CF
		' (set) Token: 0x0600070A RID: 1802 RVA: 0x00022FD7 File Offset: 0x000211D7
		Public Overridable Property chkUseLogFile As CheckBox

		' Token: 0x1700017A RID: 378
		' (get) Token: 0x0600070B RID: 1803 RVA: 0x00022FE0 File Offset: 0x000211E0
		' (set) Token: 0x0600070C RID: 1804 RVA: 0x00022FE8 File Offset: 0x000211E8
		Public Overridable Property _Label_2 As Label

		' Token: 0x1700017B RID: 379
		' (get) Token: 0x0600070D RID: 1805 RVA: 0x00022FF1 File Offset: 0x000211F1
		' (set) Token: 0x0600070E RID: 1806 RVA: 0x00022FF9 File Offset: 0x000211F9
		Public Overridable Property lblLogFile As Label

		' Token: 0x1700017C RID: 380
		' (get) Token: 0x0600070F RID: 1807 RVA: 0x00023002 File Offset: 0x00021202
		' (set) Token: 0x06000710 RID: 1808 RVA: 0x0002300A File Offset: 0x0002120A
		Public Overridable Property _Label_1 As Label

		' Token: 0x1700017D RID: 381
		' (get) Token: 0x06000711 RID: 1809 RVA: 0x00023013 File Offset: 0x00021213
		' (set) Token: 0x06000712 RID: 1810 RVA: 0x0002301B File Offset: 0x0002121B
		Public Overridable Property _Label_3 As Label

		' Token: 0x1700017E RID: 382
		' (get) Token: 0x06000713 RID: 1811 RVA: 0x00023024 File Offset: 0x00021224
		' (set) Token: 0x06000714 RID: 1812 RVA: 0x0002302C File Offset: 0x0002122C
		Public Overridable Property _Label_4 As Label

		' Token: 0x1700017F RID: 383
		' (get) Token: 0x06000715 RID: 1813 RVA: 0x00023035 File Offset: 0x00021235
		' (set) Token: 0x06000716 RID: 1814 RVA: 0x0002303D File Offset: 0x0002123D
		Public Overridable Property _Label_5 As Label

		' Token: 0x17000180 RID: 384
		' (get) Token: 0x06000717 RID: 1815 RVA: 0x00023046 File Offset: 0x00021246
		' (set) Token: 0x06000718 RID: 1816 RVA: 0x0002304E File Offset: 0x0002124E
		Public Overridable Property _tabSettings_TabPage9 As TabPage

		' Token: 0x17000181 RID: 385
		' (get) Token: 0x06000719 RID: 1817 RVA: 0x00023057 File Offset: 0x00021257
		' (set) Token: 0x0600071A RID: 1818 RVA: 0x0002305F File Offset: 0x0002125F
		Public Overridable Property Image2 As PictureBox

		' Token: 0x17000182 RID: 386
		' (get) Token: 0x0600071B RID: 1819 RVA: 0x00023068 File Offset: 0x00021268
		' (set) Token: 0x0600071C RID: 1820 RVA: 0x00023070 File Offset: 0x00021270
		Public Overridable Property Shape4 As Panel

		' Token: 0x17000183 RID: 387
		' (get) Token: 0x0600071D RID: 1821 RVA: 0x00023079 File Offset: 0x00021279
		' (set) Token: 0x0600071E RID: 1822 RVA: 0x00023081 File Offset: 0x00021281
		Public Overridable Property _tabSettings_TabPage10 As TabPage

		' Token: 0x17000184 RID: 388
		' (get) Token: 0x0600071F RID: 1823 RVA: 0x0002308A File Offset: 0x0002128A
		' (set) Token: 0x06000720 RID: 1824 RVA: 0x00023092 File Offset: 0x00021292
		Public Overridable Property tabSettings As TabControl

		' Token: 0x17000185 RID: 389
		' (get) Token: 0x06000721 RID: 1825 RVA: 0x0002309B File Offset: 0x0002129B
		' (set) Token: 0x06000722 RID: 1826 RVA: 0x000230A4 File Offset: 0x000212A4
		Public Overridable Property cmdNeu As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdNeu
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdNeu_Click
				Dim cmdNeu As Button = Me._cmdNeu
				If cmdNeu IsNot Nothing Then
					RemoveHandler cmdNeu.Click, value2
				End If
				Me._cmdNeu = value
				cmdNeu = Me._cmdNeu
				If cmdNeu IsNot Nothing Then
					AddHandler cmdNeu.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000186 RID: 390
		' (get) Token: 0x06000723 RID: 1827 RVA: 0x000230E7 File Offset: 0x000212E7
		' (set) Token: 0x06000724 RID: 1828 RVA: 0x000230F0 File Offset: 0x000212F0
		Public Overridable Property txtFilmNr As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtFilmNr
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtFilmNr_TextChanged
				Dim txtFilmNr As TextBox = Me._txtFilmNr
				If txtFilmNr IsNot Nothing Then
					RemoveHandler txtFilmNr.TextChanged, value2
				End If
				Me._txtFilmNr = value
				txtFilmNr = Me._txtFilmNr
				If txtFilmNr IsNot Nothing Then
					AddHandler txtFilmNr.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000187 RID: 391
		' (get) Token: 0x06000725 RID: 1829 RVA: 0x00023133 File Offset: 0x00021333
		' (set) Token: 0x06000726 RID: 1830 RVA: 0x0002313B File Offset: 0x0002133B
		Public Overridable Property txtPage As TextBox

		' Token: 0x17000188 RID: 392
		' (get) Token: 0x06000727 RID: 1831 RVA: 0x00023144 File Offset: 0x00021344
		' (set) Token: 0x06000728 RID: 1832 RVA: 0x0002314C File Offset: 0x0002134C
		Public Overridable Property cmdNewRoll As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdNewRoll
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdNewRoll_Click
				Dim cmdNewRoll As Button = Me._cmdNewRoll
				If cmdNewRoll IsNot Nothing Then
					RemoveHandler cmdNewRoll.Click, value2
				End If
				Me._cmdNewRoll = value
				cmdNewRoll = Me._cmdNewRoll
				If cmdNewRoll IsNot Nothing Then
					AddHandler cmdNewRoll.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000189 RID: 393
		' (get) Token: 0x06000729 RID: 1833 RVA: 0x0002318F File Offset: 0x0002138F
		' (set) Token: 0x0600072A RID: 1834 RVA: 0x00023197 File Offset: 0x00021397
		Public Overridable Property txtRestAufnahmen As TextBox

		' Token: 0x1700018A RID: 394
		' (get) Token: 0x0600072B RID: 1835 RVA: 0x000231A0 File Offset: 0x000213A0
		' (set) Token: 0x0600072C RID: 1836 RVA: 0x000231A8 File Offset: 0x000213A8
		Public Overridable Property cmbTemplate As ComboBox
			<CompilerGenerated()>
			Get
				Return Me._cmbTemplate
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ComboBox)
				Dim value2 As EventHandler = AddressOf Me.cmbTemplate_SelectedIndexChanged
				Dim cmbTemplate As ComboBox = Me._cmbTemplate
				If cmbTemplate IsNot Nothing Then
					RemoveHandler cmbTemplate.SelectedIndexChanged, value2
				End If
				Me._cmbTemplate = value
				cmbTemplate = Me._cmbTemplate
				If cmbTemplate IsNot Nothing Then
					AddHandler cmbTemplate.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700018B RID: 395
		' (get) Token: 0x0600072D RID: 1837 RVA: 0x000231EB File Offset: 0x000213EB
		' (set) Token: 0x0600072E RID: 1838 RVA: 0x000231F3 File Offset: 0x000213F3
		Public Overridable Property _Label1_8 As Label

		' Token: 0x1700018C RID: 396
		' (get) Token: 0x0600072F RID: 1839 RVA: 0x000231FC File Offset: 0x000213FC
		' (set) Token: 0x06000730 RID: 1840 RVA: 0x00023204 File Offset: 0x00021404
		Public Overridable Property _Label1_7 As Label

		' Token: 0x1700018D RID: 397
		' (get) Token: 0x06000731 RID: 1841 RVA: 0x0002320D File Offset: 0x0002140D
		' (set) Token: 0x06000732 RID: 1842 RVA: 0x00023215 File Offset: 0x00021415
		Public Overridable Property Label34 As Label

		' Token: 0x1700018E RID: 398
		' (get) Token: 0x06000733 RID: 1843 RVA: 0x0002321E File Offset: 0x0002141E
		' (set) Token: 0x06000734 RID: 1844 RVA: 0x00023228 File Offset: 0x00021428
		Public Overridable Property txtLastDocument As TextBox
			<CompilerGenerated()>
			Get
				Return Me._txtLastDocument
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtLastDocument_Change
				Dim txtLastDocument As TextBox = Me._txtLastDocument
				If txtLastDocument IsNot Nothing Then
					RemoveHandler txtLastDocument.TextChanged, value2
				End If
				Me._txtLastDocument = value
				txtLastDocument = Me._txtLastDocument
				If txtLastDocument IsNot Nothing Then
					AddHandler txtLastDocument.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700018F RID: 399
		' (get) Token: 0x06000735 RID: 1845 RVA: 0x0002326B File Offset: 0x0002146B
		' (set) Token: 0x06000736 RID: 1846 RVA: 0x00023273 File Offset: 0x00021473
		Public Overridable Property _Label1_1 As Label

		' Token: 0x17000190 RID: 400
		' (get) Token: 0x06000737 RID: 1847 RVA: 0x0002327C File Offset: 0x0002147C
		' (set) Token: 0x06000738 RID: 1848 RVA: 0x00023284 File Offset: 0x00021484
		Public Overridable Property _Label1_3 As Label

		' Token: 0x17000191 RID: 401
		' (get) Token: 0x06000739 RID: 1849 RVA: 0x0002328D File Offset: 0x0002148D
		' (set) Token: 0x0600073A RID: 1850 RVA: 0x00023295 File Offset: 0x00021495
		Public Overridable Property _Label1_2 As Label

		' Token: 0x17000192 RID: 402
		' (get) Token: 0x0600073B RID: 1851 RVA: 0x0002329E File Offset: 0x0002149E
		' (set) Token: 0x0600073C RID: 1852 RVA: 0x000232A6 File Offset: 0x000214A6
		Public Overridable Property Label15 As Label

		' Token: 0x17000193 RID: 403
		' (get) Token: 0x0600073D RID: 1853 RVA: 0x000232AF File Offset: 0x000214AF
		' (set) Token: 0x0600073E RID: 1854 RVA: 0x000232B7 File Offset: 0x000214B7
		Public Overridable Property _ShpFilmed_5 As Panel

		' Token: 0x17000194 RID: 404
		' (get) Token: 0x0600073F RID: 1855 RVA: 0x000232C0 File Offset: 0x000214C0
		' (set) Token: 0x06000740 RID: 1856 RVA: 0x000232C8 File Offset: 0x000214C8
		Public Overridable Property _ShpFilmed_4 As Panel

		' Token: 0x17000195 RID: 405
		' (get) Token: 0x06000741 RID: 1857 RVA: 0x000232D1 File Offset: 0x000214D1
		' (set) Token: 0x06000742 RID: 1858 RVA: 0x000232D9 File Offset: 0x000214D9
		Public Overridable Property _ShpFilmed_3 As Panel

		' Token: 0x17000196 RID: 406
		' (get) Token: 0x06000743 RID: 1859 RVA: 0x000232E2 File Offset: 0x000214E2
		' (set) Token: 0x06000744 RID: 1860 RVA: 0x000232EA File Offset: 0x000214EA
		Public Overridable Property _ShpFilmed_2 As Panel

		' Token: 0x17000197 RID: 407
		' (get) Token: 0x06000745 RID: 1861 RVA: 0x000232F3 File Offset: 0x000214F3
		' (set) Token: 0x06000746 RID: 1862 RVA: 0x000232FB File Offset: 0x000214FB
		Public Overridable Property _ShpFilmed_1 As Panel

		' Token: 0x17000198 RID: 408
		' (get) Token: 0x06000747 RID: 1863 RVA: 0x00023304 File Offset: 0x00021504
		' (set) Token: 0x06000748 RID: 1864 RVA: 0x0002330C File Offset: 0x0002150C
		Public Overridable Property _ShpFilmed_0 As Panel

		' Token: 0x17000199 RID: 409
		' (get) Token: 0x06000749 RID: 1865 RVA: 0x00023315 File Offset: 0x00021515
		' (set) Token: 0x0600074A RID: 1866 RVA: 0x0002331D File Offset: 0x0002151D
		Public Overridable Property _Label1_5 As Label

		' Token: 0x1700019A RID: 410
		' (get) Token: 0x0600074B RID: 1867 RVA: 0x00023326 File Offset: 0x00021526
		' (set) Token: 0x0600074C RID: 1868 RVA: 0x0002332E File Offset: 0x0002152E
		Public Overridable Property _Label13_0 As Label

		' Token: 0x1700019B RID: 411
		' (get) Token: 0x0600074D RID: 1869 RVA: 0x00023337 File Offset: 0x00021537
		' (set) Token: 0x0600074E RID: 1870 RVA: 0x00023340 File Offset: 0x00021540
		Public Overridable Property lblLevel As Label
			<CompilerGenerated()>
			Get
				Return Me._lblLevel
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Label)
				Dim value2 As EventHandler = AddressOf Me.lblLevel_Click
				Dim lblLevel As Label = Me._lblLevel
				If lblLevel IsNot Nothing Then
					RemoveHandler lblLevel.Click, value2
				End If
				Me._lblLevel = value
				lblLevel = Me._lblLevel
				If lblLevel IsNot Nothing Then
					AddHandler lblLevel.Click, value2
				End If
			End Set
		End Property

		' Token: 0x1700019C RID: 412
		' (get) Token: 0x0600074F RID: 1871 RVA: 0x00023383 File Offset: 0x00021583
		' (set) Token: 0x06000750 RID: 1872 RVA: 0x0002338B File Offset: 0x0002158B
		Public Overridable Property _label__7 As Label

		' Token: 0x1700019D RID: 413
		' (get) Token: 0x06000751 RID: 1873 RVA: 0x00023394 File Offset: 0x00021594
		' (set) Token: 0x06000752 RID: 1874 RVA: 0x0002339C File Offset: 0x0002159C
		Public Overridable Property Label7 As Label

		' Token: 0x1700019E RID: 414
		' (get) Token: 0x06000753 RID: 1875 RVA: 0x000233A5 File Offset: 0x000215A5
		' (set) Token: 0x06000754 RID: 1876 RVA: 0x000233AD File Offset: 0x000215AD
		Public Overridable Property _Label1_6 As Label

		' Token: 0x1700019F RID: 415
		' (get) Token: 0x06000755 RID: 1877 RVA: 0x000233B6 File Offset: 0x000215B6
		' (set) Token: 0x06000756 RID: 1878 RVA: 0x000233BE File Offset: 0x000215BE
		Public Overridable Property _ShpBLIP_5 As Panel

		' Token: 0x170001A0 RID: 416
		' (get) Token: 0x06000757 RID: 1879 RVA: 0x000233C7 File Offset: 0x000215C7
		' (set) Token: 0x06000758 RID: 1880 RVA: 0x000233CF File Offset: 0x000215CF
		Public Overridable Property _ShpBLIP_4 As Panel

		' Token: 0x170001A1 RID: 417
		' (get) Token: 0x06000759 RID: 1881 RVA: 0x000233D8 File Offset: 0x000215D8
		' (set) Token: 0x0600075A RID: 1882 RVA: 0x000233E0 File Offset: 0x000215E0
		Public Overridable Property _ShpBLIP_3 As Panel

		' Token: 0x170001A2 RID: 418
		' (get) Token: 0x0600075B RID: 1883 RVA: 0x000233E9 File Offset: 0x000215E9
		' (set) Token: 0x0600075C RID: 1884 RVA: 0x000233F1 File Offset: 0x000215F1
		Public Overridable Property _ShpBLIP_2 As Panel

		' Token: 0x170001A3 RID: 419
		' (get) Token: 0x0600075D RID: 1885 RVA: 0x000233FA File Offset: 0x000215FA
		' (set) Token: 0x0600075E RID: 1886 RVA: 0x00023402 File Offset: 0x00021602
		Public Overridable Property _ShpBLIP_1 As Panel

		' Token: 0x170001A4 RID: 420
		' (get) Token: 0x0600075F RID: 1887 RVA: 0x0002340B File Offset: 0x0002160B
		' (set) Token: 0x06000760 RID: 1888 RVA: 0x00023413 File Offset: 0x00021613
		Public Overridable Property _ShpBLIP_0 As Panel

		' Token: 0x170001A5 RID: 421
		' (get) Token: 0x06000761 RID: 1889 RVA: 0x0002341C File Offset: 0x0002161C
		' (set) Token: 0x06000762 RID: 1890 RVA: 0x00023424 File Offset: 0x00021624
		Public Overridable Property lblPos As Label
			<CompilerGenerated()>
			Get
				Return Me._lblPos
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Label)
				Dim value2 As EventHandler = AddressOf Me.lblPos_Click
				Dim value3 As EventHandler = AddressOf Me.lblPos_DoubleClick
				Dim lblPos As Label = Me._lblPos
				If lblPos IsNot Nothing Then
					RemoveHandler lblPos.Click, value2
					RemoveHandler lblPos.DoubleClick, value3
				End If
				Me._lblPos = value
				lblPos = Me._lblPos
				If lblPos IsNot Nothing Then
					AddHandler lblPos.Click, value2
					AddHandler lblPos.DoubleClick, value3
				End If
			End Set
		End Property

		' Token: 0x170001A6 RID: 422
		' (get) Token: 0x06000763 RID: 1891 RVA: 0x00023482 File Offset: 0x00021682
		' (set) Token: 0x06000764 RID: 1892 RVA: 0x0002348A File Offset: 0x0002168A
		Public Overridable Property _Label1_0 As Label

		' Token: 0x170001A7 RID: 423
		' (get) Token: 0x06000765 RID: 1893 RVA: 0x00023493 File Offset: 0x00021693
		' (set) Token: 0x06000766 RID: 1894 RVA: 0x0002349C File Offset: 0x0002169C
		Public Overridable Property Shape1 As Panel
			<CompilerGenerated()>
			Get
				Return Me._Shape1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Panel)
				Dim value2 As EventHandler = AddressOf Me.Shape1_Click
				Dim shape As Panel = Me._Shape1
				If shape IsNot Nothing Then
					RemoveHandler shape.Click, value2
				End If
				Me._Shape1 = value
				shape = Me._Shape1
				If shape IsNot Nothing Then
					AddHandler shape.Click, value2
				End If
			End Set
		End Property

		' Token: 0x06000767 RID: 1895 RVA: 0x000234E0 File Offset: 0x000216E0
		<DebuggerStepThrough()>
		Private Sub InitializeComponent()
			Me.components = New Container()
			Dim componentResourceManager As ComponentResourceManager = New ComponentResourceManager(GetType(frmFilmPreview))
			Me.ToolTip1 = New ToolTip(Me.components)
			Me.txtFactor = New TextBox()
			Me.txtMaxDuplex = New TextBox()
			Me._chk1PAgePDFs_1 = New CheckBox()
			Me._chk1PAgePDFs_0 = New CheckBox()
			Me.txtInfoTextGewicht = New TextBox()
			Me.txtQuerGewicht = New TextBox()
			Me.txtFrameWidth = New TextBox()
			Me.txtAnnoBlipLen = New TextBox()
			Me.txtIgnoreCharsCount = New TextBox()
			Me.txtLen = New TextBox()
			Me.Shape4 = New Panel()
			Me.Shape5 = New Panel()
			Me._ShpFilmed_5 = New Panel()
			Me._ShpFilmed_4 = New Panel()
			Me._ShpFilmed_3 = New Panel()
			Me._ShpFilmed_2 = New Panel()
			Me._ShpFilmed_1 = New Panel()
			Me._ShpFilmed_0 = New Panel()
			Me._ShpBLIP_5 = New Panel()
			Me._ShpBLIP_4 = New Panel()
			Me._ShpBLIP_3 = New Panel()
			Me._ShpBLIP_2 = New Panel()
			Me._ShpBLIP_1 = New Panel()
			Me._ShpBLIP_0 = New Panel()
			Me.Shape1 = New Panel()
			Me.txtFilmNrAufFilm = New TextBox()
			Me.cmdFortsetzung = New Button()
			Me.cmdRefilm = New Button()
			Me.cmdCalcSpace = New Button()
			Me.cmdAbspulen = New Button()
			Me.cmdVorspann = New Button()
			Me.cmbKopf = New ComboBox()
			Me._Picture1_6 = New PictureBox()
			Me.chkNoPreview = New CheckBox()
			Me._Picture1_5 = New PictureBox()
			Me._Picture1_4 = New PictureBox()
			Me._Picture1_3 = New PictureBox()
			Me._Picture1_2 = New PictureBox()
			Me._Picture1_1 = New PictureBox()
			Me._Picture1_0 = New PictureBox()
			Me.tabSettings = New TabControl()
			Me._tabSettings_TabPage0 = New TabPage()
			Me._Label_0 = New Label()
			Me._Label_6 = New Label()
			Me._Label_9 = New Label()
			Me._Label_10 = New Label()
			Me.frbAusrichtung = New GroupBox()
			Me.chkAutoAlign180 = New CheckBox()
			Me.opt270 = New RadioButton()
			Me.opt90 = New RadioButton()
			Me.Frame1 = New GroupBox()
			Me.optFest90 = New RadioButton()
			Me.optFest270 = New RadioButton()
			Me.optFest180 = New RadioButton()
			Me.optFest0 = New RadioButton()
			Me.chkAutoAlign = New CheckBox()
			Me.Frame9 = New GroupBox()
			Me.optLagerichtig = New CheckBox()
			Me.chkA3PortraitDrehen = New CheckBox()
			Me.chkA4LSDrehen = New CheckBox()
			Me.Frame15 = New Panel()
			Me.optLA3 = New RadioButton()
			Me.optRA3 = New RadioButton()
			Me.Frame14 = New Panel()
			Me.optLA4 = New RadioButton()
			Me.optRA4 = New RadioButton()
			Me.chkOneToOne = New CheckBox()
			Me.txtToleranz = New TextBox()
			Me._Label_33 = New Label()
			Me._Label_32 = New Label()
			Me._label__5 = New Label()
			Me.chkDuplex = New CheckBox()
			Me.txtDuplexDist = New TextBox()
			Me.chkSmallLeft = New CheckBox()
			Me.chkBigLeft = New CheckBox()
			Me.Frame3 = New GroupBox()
			Me.optOben = New RadioButton()
			Me.optUnten = New RadioButton()
			Me.optCenter = New RadioButton()
			Me._tabSettings_TabPage1 = New TabPage()
			Me.chkStartBlipAtOne = New CheckBox()
			Me.Frame8 = New GroupBox()
			Me._txtBlipHoeheGross_0 = New TextBox()
			Me._txtBlipHoeheMittel_0 = New TextBox()
			Me._txtBlipHoeheKlein_0 = New TextBox()
			Me._txtBlipBreiteKlein_0 = New TextBox()
			Me._txtBlipBreiteMittel_0 = New TextBox()
			Me._txtBlipBreiteGross_0 = New TextBox()
			Me._Label19_3 = New Label()
			Me._Label19_2 = New Label()
			Me._label__19 = New Label()
			Me.Label56 = New Label()
			Me.Label57 = New Label()
			Me.Label58 = New Label()
			Me.Label59 = New Label()
			Me._Label1_4 = New Label()
			Me.frmPosition = New GroupBox()
			Me.optUeberBlip = New RadioButton()
			Me.optNebenBlip = New RadioButton()
			Me.Frame2 = New GroupBox()
			Me.cmbBlipLevel1 = New ComboBox()
			Me.cmbBlipLevel2 = New ComboBox()
			Me.cmbBlipLevel3 = New ComboBox()
			Me._label__23 = New Label()
			Me._label__24 = New Label()
			Me._label__25 = New Label()
			Me.chkBlip = New CheckBox()
			Me._tabSettings_TabPage2 = New TabPage()
			Me.frbFormat = New GroupBox()
			Me.chkTwoLines = New CheckBox()
			Me.chkSimDupFilenames = New CheckBox()
			Me.Label3 = New Label()
			Me.optBlipAnno = New RadioButton()
			Me.Label6 = New Label()
			Me.chkIgnoreChars = New CheckBox()
			Me.optDreiTeilig = New RadioButton()
			Me.chkLateStart = New CheckBox()
			Me.cmbPapierGroesse = New ComboBox()
			Me.chkShowSize = New CheckBox()
			Me.optNamen = New RadioButton()
			Me.optNummer = New RadioButton()
			Me.txtStart = New TextBox()
			Me.optMulti = New RadioButton()
			Me.Label5 = New Label()
			Me.Label4 = New Label()
			Me.chkAnnotation = New CheckBox()
			Me._tabSettings_TabPage3 = New TabPage()
			Me.tabFrames = New TabControl()
			Me._tabFrames_TabPage0 = New TabPage()
			Me.Button1 = New Button()
			Me.lblPfadStartSymbole = New Label()
			Me.Label75 = New Label()
			Me.Label76 = New Label()
			Me.Label77 = New Label()
			Me.Label78 = New Label()
			Me.Label29 = New Label()
			Me.Label31 = New Label()
			Me.Label9 = New Label()
			Me.chkStartFrame = New CheckBox()
			Me.chkZusatzStartSymbole = New CheckBox()
			Me.txtRollNoSize = New TextBox()
			Me.txtRollNoPrefix = New TextBox()
			Me.txtRollNoPostfix = New TextBox()
			Me.txtRollNoLen = New TextBox()
			Me.chkAddRollFrame = New CheckBox()
			Me.txtAddRollFrameSize = New TextBox()
			Me.txtAddRollFrameLen = New TextBox()
			Me.chkAddRollFrameInput = New CheckBox()
			Me.Frame12 = New GroupBox()
			Me._txtAddRollInfoPos_4 = New TextBox()
			Me._txtAddRollInfoPos_3 = New TextBox()
			Me._txtAddRollInfoPos_2 = New TextBox()
			Me._txtAddRollInfoPos_1 = New TextBox()
			Me.txtAddRollStartFrameSteps = New TextBox()
			Me._tabFrames_TabPage1 = New TabPage()
			Me.chkSeparateFrame = New CheckBox()
			Me.chkUseFrameNo = New CheckBox()
			Me._tabFrames_TabPage2 = New TabPage()
			Me.Button3 = New Button()
			Me.Button2 = New Button()
			Me.cmbFortsetzungsLevel = New ComboBox()
			Me.chkNoSpecialSmybolesWhenContinuation = New CheckBox()
			Me.txtFramesWiederholen = New TextBox()
			Me.chkFramesWiederholen = New CheckBox()
			Me.chkRolleistFortsetzung = New CheckBox()
			Me.chkRollewirdfortgesetzt = New CheckBox()
			Me.chkBaende = New CheckBox()
			Me._label__6 = New Label()
			Me.lblPfadFortsetzungsSymbole2 = New Label()
			Me.lblPfadFortsetzungsSymbole1 = New Label()
			Me._tabFrames_TabPage3 = New TabPage()
			Me.cmdPfadEndSymbole = New Button()
			Me.chkRollEndFrame = New CheckBox()
			Me.chkUseIndex = New CheckBox()
			Me.chkZusatzEndSymbole = New CheckBox()
			Me.lblPfadEndSymbole = New Label()
			Me._tabSettings_TabPage4 = New TabPage()
			Me.cmdTestPortrait = New Button()
			Me._Frame__2 = New GroupBox()
			Me.txtAnnoX = New TextBox()
			Me.txtAnnoY = New TextBox()
			Me.txtAnnoBreite = New TextBox()
			Me.txtAnnoHoehe = New TextBox()
			Me._label__22 = New Label()
			Me._label__21 = New Label()
			Me._label38_2 = New Label()
			Me._label38_0 = New Label()
			Me._label38_1 = New Label()
			Me._label38_21 = New Label()
			Me._Frame__5 = New GroupBox()
			Me.Text1 = New TextBox()
			Me.txtInfoTextAusrichtung = New TextBox()
			Me.txtInfoTextX = New TextBox()
			Me.txtInfoTextY = New TextBox()
			Me.txtInfoTextFont = New TextBox()
			Me.Label80 = New Label()
			Me._Label_12 = New Label()
			Me._Label_8 = New Label()
			Me.Label65 = New Label()
			Me._label__14 = New Label()
			Me._label__15 = New Label()
			Me.Label55 = New Label()
			Me.Label54 = New Label()
			Me._Frame__3 = New GroupBox()
			Me.txtInfoHoehe = New TextBox()
			Me.txtInfoBreite = New TextBox()
			Me.txtInfoY = New TextBox()
			Me.txtInfoX = New TextBox()
			Me._label__3 = New Label()
			Me._Label_52 = New Label()
			Me._Label_49 = New Label()
			Me._label__4 = New Label()
			Me._label__13 = New Label()
			Me._label__12 = New Label()
			Me._Frame__4 = New GroupBox()
			Me.txtQuerFont = New TextBox()
			Me.txtQuerAnnoY = New TextBox()
			Me.txtQuerAnnoX = New TextBox()
			Me.txtQuerAusrichtung = New TextBox()
			Me.Label73 = New Label()
			Me.Label72 = New Label()
			Me._label__16 = New Label()
			Me._label__17 = New Label()
			Me.Label69 = New Label()
			Me._Label_7 = New Label()
			Me._Label_11 = New Label()
			Me._Frame__1 = New GroupBox()
			Me.txtQuerBlipX = New TextBox()
			Me.txtQuerBlipY = New TextBox()
			Me.txtQuerBlipBreite = New TextBox()
			Me.txtQuerBlipHoehe = New TextBox()
			Me._label__10 = New Label()
			Me._label__11 = New Label()
			Me._label__2 = New Label()
			Me._Label_61 = New Label()
			Me._Label_60 = New Label()
			Me._label__1 = New Label()
			Me._Frame__0 = New GroupBox()
			Me.txtQuerBreite = New TextBox()
			Me.txtQuerHoehe = New TextBox()
			Me.txtQuerX = New TextBox()
			Me.txtQuerY = New TextBox()
			Me._label__0 = New Label()
			Me._Label_51 = New Label()
			Me._Label_50 = New Label()
			Me._label__44 = New Label()
			Me._label__8 = New Label()
			Me._label__9 = New Label()
			Me._tabSettings_TabPage5 = New TabPage()
			Me.Label10 = New Label()
			Me.Label2 = New Label()
			Me.Label17 = New Label()
			Me.Label18 = New Label()
			Me._Label19_0 = New Label()
			Me.Label20 = New Label()
			Me.Label28 = New Label()
			Me._label__29 = New Label()
			Me.chkSplit = New CheckBox()
			Me.cmbMaxDocumentSize = New ComboBox()
			Me.txtSplitBreite = New TextBox()
			Me.txtSplitLaenge = New TextBox()
			Me.cmbSplitCount = New ComboBox()
			Me.txtOverSize = New TextBox()
			Me._tabSettings_TabPage6 = New TabPage()
			Me._txtVerschluss_1 = New TextBox()
			Me.chkFesteBelegzahl = New CheckBox()
			Me.txtAddStepLevel3 = New TextBox()
			Me.txtAddStepLevel2 = New TextBox()
			Me.Frame7 = New GroupBox()
			Me.chkTrailerInfoFrames = New CheckBox()
			Me.chkAutoTrailer = New CheckBox()
			Me.txtAutoTrailerDistance = New TextBox()
			Me.txtAutoTrailerLength = New TextBox()
			Me._label__38 = New Label()
			Me._label__39 = New Label()
			Me.Label40 = New Label()
			Me.Label41 = New Label()
			Me.txtSchritteBelichtung = New TextBox()
			Me.chkStepsImageToImage = New CheckBox()
			Me.txtSchritte = New TextBox()
			Me._txtVerschluss_0 = New TextBox()
			Me.txtZusatzBelichtung = New TextBox()
			Me._Label96_4 = New Label()
			Me._label__20 = New Label()
			Me.Label22 = New Label()
			Me._label__18 = New Label()
			Me.Label8 = New Label()
			Me.Image1 = New PictureBox()
			Me.Label35 = New Label()
			Me._label__31 = New Label()
			Me.Label30 = New Label()
			Me.Label26 = New Label()
			Me.Label25 = New Label()
			Me._label__46 = New Label()
			Me._tabSettings_TabPage7 = New TabPage()
			Me.chkJPEG = New CheckBox()
			Me.cmbPDFReso = New ComboBox()
			Me.Label42 = New Label()
			Me.Label27 = New Label()
			Me.Label94 = New Label()
			Me._tabSettings_TabPage8 = New TabPage()
			Me.Frame4 = New GroupBox()
			Me.radBlackFrame = New RadioButton()
			Me.radWhiteFrame = New RadioButton()
			Me.Label1 = New Label()
			Me.chkFrame = New CheckBox()
			Me.chkInvers = New CheckBox()
			Me._tabSettings_TabPage9 = New TabPage()
			Me.cmdDownRecords = New Button()
			Me.cmdTrailerDown = New Button()
			Me.cmdHeaderDown = New Button()
			Me.cmdHeaderUp = New Button()
			Me.cmdTrailerUp = New Button()
			Me.cmdUpRecords = New Button()
			Me.lstTrailer = New CheckedListBox()
			Me.cmdClearLogPath = New Button()
			Me.lstRecords = New CheckedListBox()
			Me.lstHeader = New CheckedListBox()
			Me.cmbDelimiter = New ComboBox()
			Me.cmdSetLogPath = New Button()
			Me.chkUseLogFile = New CheckBox()
			Me._Label_2 = New Label()
			Me.lblLogFile = New Label()
			Me._Label_1 = New Label()
			Me._Label_3 = New Label()
			Me._Label_4 = New Label()
			Me._Label_5 = New Label()
			Me._tabSettings_TabPage10 = New TabPage()
			Me.Image2 = New PictureBox()
			Me.cmdNeu = New Button()
			Me.txtFilmNr = New TextBox()
			Me.txtPage = New TextBox()
			Me.cmdNewRoll = New Button()
			Me.txtRestAufnahmen = New TextBox()
			Me.cmbTemplate = New ComboBox()
			Me._Label1_8 = New Label()
			Me._Label1_7 = New Label()
			Me.Label34 = New Label()
			Me.txtLastDocument = New TextBox()
			Me._Label1_1 = New Label()
			Me._Label1_3 = New Label()
			Me._Label1_2 = New Label()
			Me.Label15 = New Label()
			Me._Label1_5 = New Label()
			Me._Label13_0 = New Label()
			Me.lblLevel = New Label()
			Me._label__7 = New Label()
			Me.Label7 = New Label()
			Me._Label1_6 = New Label()
			Me.lblPos = New Label()
			Me._Label1_0 = New Label()
			Me._lblAnno_0 = New Label()
			Me._lblAnno_1 = New Label()
			Me._lblAnno_2 = New Label()
			Me._lblAnno_3 = New Label()
			Me._lblAnno_4 = New Label()
			Me._lblAnno_5 = New Label()
			Me.cmdStart = New Button()
			Me.cmdCancel = New Button()
			Me.cmdNewTemplate = New Button()
			Me.cmdSaveTemplate = New Button()
			Me.cmdSetLastDoc = New Button()
			Me.cmdFirst = New Button()
			Me.cmdPagePrevious = New Button()
			Me.cmdPrevious = New Button()
			Me.cmdNext = New Button()
			Me.cmdPageNext = New Button()
			Me.cmdLast = New Button()
			Me.OpenFileDialog1 = New OpenFileDialog()
			CType(Me._Picture1_6, ISupportInitialize).BeginInit()
			CType(Me._Picture1_5, ISupportInitialize).BeginInit()
			CType(Me._Picture1_4, ISupportInitialize).BeginInit()
			CType(Me._Picture1_3, ISupportInitialize).BeginInit()
			CType(Me._Picture1_2, ISupportInitialize).BeginInit()
			CType(Me._Picture1_1, ISupportInitialize).BeginInit()
			CType(Me._Picture1_0, ISupportInitialize).BeginInit()
			Me.tabSettings.SuspendLayout()
			Me._tabSettings_TabPage0.SuspendLayout()
			Me.frbAusrichtung.SuspendLayout()
			Me.Frame1.SuspendLayout()
			Me.Frame9.SuspendLayout()
			Me.Frame15.SuspendLayout()
			Me.Frame14.SuspendLayout()
			Me.Frame3.SuspendLayout()
			Me._tabSettings_TabPage1.SuspendLayout()
			Me.Frame8.SuspendLayout()
			Me.frmPosition.SuspendLayout()
			Me.Frame2.SuspendLayout()
			Me._tabSettings_TabPage2.SuspendLayout()
			Me.frbFormat.SuspendLayout()
			Me._tabSettings_TabPage3.SuspendLayout()
			Me.tabFrames.SuspendLayout()
			Me._tabFrames_TabPage0.SuspendLayout()
			Me.Frame12.SuspendLayout()
			Me._tabFrames_TabPage1.SuspendLayout()
			Me._tabFrames_TabPage2.SuspendLayout()
			Me._tabFrames_TabPage3.SuspendLayout()
			Me._tabSettings_TabPage4.SuspendLayout()
			Me._Frame__2.SuspendLayout()
			Me._Frame__5.SuspendLayout()
			Me._Frame__3.SuspendLayout()
			Me._Frame__4.SuspendLayout()
			Me._Frame__1.SuspendLayout()
			Me._Frame__0.SuspendLayout()
			Me._tabSettings_TabPage5.SuspendLayout()
			Me._tabSettings_TabPage6.SuspendLayout()
			Me.Frame7.SuspendLayout()
			CType(Me.Image1, ISupportInitialize).BeginInit()
			Me._tabSettings_TabPage7.SuspendLayout()
			Me._tabSettings_TabPage8.SuspendLayout()
			Me.Frame4.SuspendLayout()
			Me._tabSettings_TabPage9.SuspendLayout()
			Me._tabSettings_TabPage10.SuspendLayout()
			CType(Me.Image2, ISupportInitialize).BeginInit()
			MyBase.SuspendLayout()
			Me.txtFactor.AcceptsReturn = True
			Me.txtFactor.BackColor = SystemColors.Window
			Me.txtFactor.Cursor = Cursors.IBeam
			Me.txtFactor.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtFactor.ForeColor = SystemColors.WindowText
			Me.txtFactor.Location = New Point(228, 48)
			Me.txtFactor.MaxLength = 0
			Me.txtFactor.Name = "txtFactor"
			Me.txtFactor.RightToLeft = RightToLeft.No
			Me.txtFactor.Size = New Size(46, 22)
			Me.txtFactor.TabIndex = 191
			Me.txtFactor.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtFactor, "Scales Image Pixels at 400 DPI to monitor pixel")
			Me.txtMaxDuplex.AcceptsReturn = True
			Me.txtMaxDuplex.BackColor = SystemColors.Window
			Me.txtMaxDuplex.Cursor = Cursors.IBeam
			Me.txtMaxDuplex.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtMaxDuplex.ForeColor = SystemColors.WindowText
			Me.txtMaxDuplex.Location = New Point(139, 208)
			Me.txtMaxDuplex.MaxLength = 0
			Me.txtMaxDuplex.Name = "txtMaxDuplex"
			Me.txtMaxDuplex.RightToLeft = RightToLeft.No
			Me.txtMaxDuplex.Size = New Size(49, 22)
			Me.txtMaxDuplex.TabIndex = 304
			Me.txtMaxDuplex.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtMaxDuplex, "definiert den höchsten Wert der längeren Seite, die noch als A4  behandelt wird")
			Me._chk1PAgePDFs_1.BackColor = SystemColors.Control
			Me._chk1PAgePDFs_1.Cursor = Cursors.[Default]
			Me._chk1PAgePDFs_1.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._chk1PAgePDFs_1.ForeColor = SystemColors.ControlText
			Me._chk1PAgePDFs_1.Location = New Point(16, 230)
			Me._chk1PAgePDFs_1.Name = "_chk1PAgePDFs_1"
			Me._chk1PAgePDFs_1.RightToLeft = RightToLeft.No
			Me._chk1PAgePDFs_1.Size = New Size(505, 25)
			Me._chk1PAgePDFs_1.TabIndex = 324
			Me._chk1PAgePDFs_1.Text = "TIFFs containing only one page represent Level 2 Documents"
			Me.ToolTip1.SetToolTip(Me._chk1PAgePDFs_1, "Einseitge PDF-Dateien werden wie mehrseitge PDFs behandelt, d.h. es wird ein BLIP-Wechsel durchgeführt.")
			Me._chk1PAgePDFs_1.UseVisualStyleBackColor = False
			Me._chk1PAgePDFs_0.BackColor = SystemColors.Control
			Me._chk1PAgePDFs_0.Cursor = Cursors.[Default]
			Me._chk1PAgePDFs_0.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._chk1PAgePDFs_0.ForeColor = SystemColors.ControlText
			Me._chk1PAgePDFs_0.Location = New Point(16, 194)
			Me._chk1PAgePDFs_0.Name = "_chk1PAgePDFs_0"
			Me._chk1PAgePDFs_0.RightToLeft = RightToLeft.No
			Me._chk1PAgePDFs_0.Size = New Size(505, 25)
			Me._chk1PAgePDFs_0.TabIndex = 323
			Me._chk1PAgePDFs_0.Text = "PDFs containing only one page represent Level 2 Documents"
			Me.ToolTip1.SetToolTip(Me._chk1PAgePDFs_0, "Einseitge PDF-Dateien werden wie mehrseitge PDFs behandelt, d.h. es wird ein BLIP-Wechsel durchgeführt.")
			Me._chk1PAgePDFs_0.UseVisualStyleBackColor = False
			Me.txtInfoTextGewicht.AcceptsReturn = True
			Me.txtInfoTextGewicht.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtInfoTextGewicht.Cursor = Cursors.IBeam
			Me.txtInfoTextGewicht.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoTextGewicht.ForeColor = SystemColors.WindowText
			Me.txtInfoTextGewicht.Location = New Point(360, 60)
			Me.txtInfoTextGewicht.MaxLength = 0
			Me.txtInfoTextGewicht.Name = "txtInfoTextGewicht"
			Me.txtInfoTextGewicht.RightToLeft = RightToLeft.No
			Me.txtInfoTextGewicht.Size = New Size(45, 21)
			Me.txtInfoTextGewicht.TabIndex = 231
			Me.txtInfoTextGewicht.Text = "0"
			Me.txtInfoTextGewicht.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtInfoTextGewicht, "Werte: 100-900")
			Me.txtQuerGewicht.AcceptsReturn = True
			Me.txtQuerGewicht.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtQuerGewicht.Cursor = Cursors.IBeam
			Me.txtQuerGewicht.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerGewicht.ForeColor = SystemColors.WindowText
			Me.txtQuerGewicht.Location = New Point(320, 57)
			Me.txtQuerGewicht.MaxLength = 0
			Me.txtQuerGewicht.Name = "txtQuerGewicht"
			Me.txtQuerGewicht.RightToLeft = RightToLeft.No
			Me.txtQuerGewicht.Size = New Size(45, 21)
			Me.txtQuerGewicht.TabIndex = 147
			Me.txtQuerGewicht.Text = "0"
			Me.txtQuerGewicht.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtQuerGewicht, "Werte: 100-900")
			Me.txtFrameWidth.AcceptsReturn = True
			Me.txtFrameWidth.BackColor = SystemColors.Window
			Me.txtFrameWidth.Cursor = Cursors.IBeam
			Me.txtFrameWidth.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtFrameWidth.ForeColor = SystemColors.WindowText
			Me.txtFrameWidth.Location = New Point(157, 115)
			Me.txtFrameWidth.MaxLength = 0
			Me.txtFrameWidth.Name = "txtFrameWidth"
			Me.txtFrameWidth.RightToLeft = RightToLeft.No
			Me.txtFrameWidth.Size = New Size(34, 22)
			Me.txtFrameWidth.TabIndex = 306
			Me.txtFrameWidth.Text = "5"
			Me.txtFrameWidth.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtFrameWidth, "definiert den höchsten Wert der längeren Seite, die noch als A4  behandelt wird")
			Me.txtAnnoBlipLen.AcceptsReturn = True
			Me.txtAnnoBlipLen.BackColor = SystemColors.Window
			Me.txtAnnoBlipLen.Cursor = Cursors.IBeam
			Me.txtAnnoBlipLen.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtAnnoBlipLen.ForeColor = SystemColors.WindowText
			Me.txtAnnoBlipLen.Location = New Point(501, 100)
			Me.txtAnnoBlipLen.MaxLength = 0
			Me.txtAnnoBlipLen.Name = "txtAnnoBlipLen"
			Me.txtAnnoBlipLen.Size = New Size(73, 22)
			Me.txtAnnoBlipLen.TabIndex = 327
			Me.txtAnnoBlipLen.Text = "4"
			Me.txtAnnoBlipLen.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtAnnoBlipLen, "Number of leading characters of the filenames that are removed during annotations and protocol creation")
			Me.txtIgnoreCharsCount.AcceptsReturn = True
			Me.txtIgnoreCharsCount.BackColor = SystemColors.Window
			Me.txtIgnoreCharsCount.Cursor = Cursors.IBeam
			Me.txtIgnoreCharsCount.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtIgnoreCharsCount.ForeColor = SystemColors.WindowText
			Me.txtIgnoreCharsCount.Location = New Point(690, 166)
			Me.txtIgnoreCharsCount.MaxLength = 0
			Me.txtIgnoreCharsCount.Name = "txtIgnoreCharsCount"
			Me.txtIgnoreCharsCount.Size = New Size(73, 22)
			Me.txtIgnoreCharsCount.TabIndex = 324
			Me.txtIgnoreCharsCount.Text = "0"
			Me.txtIgnoreCharsCount.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtIgnoreCharsCount, "Number of leading characters of the filenames that are removed during annotations and protocol creation")
			Me.txtIgnoreCharsCount.Visible = False
			Me.txtLen.AcceptsReturn = True
			Me.txtLen.BackColor = SystemColors.Window
			Me.txtLen.Cursor = Cursors.IBeam
			Me.txtLen.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtLen.ForeColor = SystemColors.WindowText
			Me.txtLen.Location = New Point(501, 64)
			Me.txtLen.MaxLength = 0
			Me.txtLen.Name = "txtLen"
			Me.txtLen.RightToLeft = RightToLeft.No
			Me.txtLen.Size = New Size(73, 22)
			Me.txtLen.TabIndex = 51
			Me.txtLen.TextAlign = HorizontalAlignment.Right
			Me.ToolTip1.SetToolTip(Me.txtLen, "Länge der Teil-Annotation eines Levels z.B. 3 liefer 001.003.002 für 3-Level Indexing")
			Me.Shape4.BackColor = Color.Black
			Me.Shape4.Location = New Point(0, 24)
			Me.Shape4.Name = "Shape4"
			Me.Shape4.Size = New Size(921, 305)
			Me.Shape4.TabIndex = 0
			Me.Shape5.BackColor = Color.FromArgb(224, 224, 224)
			Me.Shape5.Location = New Point(8, 126)
			Me.Shape5.Name = "Shape5"
			Me.Shape5.Size = New Size(353, 59)
			Me.Shape5.TabIndex = 0
			Me._ShpFilmed_5.BackColor = Color.Red
			Me._ShpFilmed_5.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_5.Location = New Point(764, 30)
			Me._ShpFilmed_5.Name = "_ShpFilmed_5"
			Me._ShpFilmed_5.Size = New Size(12, 12)
			Me._ShpFilmed_5.TabIndex = 0
			Me._ShpFilmed_4.BackColor = Color.Red
			Me._ShpFilmed_4.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_4.Location = New Point(616, 30)
			Me._ShpFilmed_4.Name = "_ShpFilmed_4"
			Me._ShpFilmed_4.Size = New Size(12, 12)
			Me._ShpFilmed_4.TabIndex = 0
			Me._ShpFilmed_3.BackColor = Color.Red
			Me._ShpFilmed_3.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_3.Location = New Point(468, 30)
			Me._ShpFilmed_3.Name = "_ShpFilmed_3"
			Me._ShpFilmed_3.Size = New Size(12, 12)
			Me._ShpFilmed_3.TabIndex = 0
			Me._ShpFilmed_2.BackColor = Color.Red
			Me._ShpFilmed_2.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_2.Location = New Point(320, 30)
			Me._ShpFilmed_2.Name = "_ShpFilmed_2"
			Me._ShpFilmed_2.Size = New Size(12, 12)
			Me._ShpFilmed_2.TabIndex = 0
			Me._ShpFilmed_1.BackColor = Color.Red
			Me._ShpFilmed_1.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_1.Location = New Point(172, 30)
			Me._ShpFilmed_1.Name = "_ShpFilmed_1"
			Me._ShpFilmed_1.Size = New Size(12, 12)
			Me._ShpFilmed_1.TabIndex = 0
			Me._ShpFilmed_0.BackColor = Color.Red
			Me._ShpFilmed_0.BorderStyle = BorderStyle.Fixed3D
			Me._ShpFilmed_0.Location = New Point(24, 30)
			Me._ShpFilmed_0.Name = "_ShpFilmed_0"
			Me._ShpFilmed_0.Size = New Size(12, 12)
			Me._ShpFilmed_0.TabIndex = 0
			Me._ShpBLIP_5.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_5.Location = New Point(764, 140)
			Me._ShpBLIP_5.Name = "_ShpBLIP_5"
			Me._ShpBLIP_5.Size = New Size(14, 21)
			Me._ShpBLIP_5.TabIndex = 0
			Me._ShpBLIP_4.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_4.Location = New Point(616, 140)
			Me._ShpBLIP_4.Name = "_ShpBLIP_4"
			Me._ShpBLIP_4.Size = New Size(14, 21)
			Me._ShpBLIP_4.TabIndex = 0
			Me._ShpBLIP_3.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_3.Location = New Point(468, 140)
			Me._ShpBLIP_3.Name = "_ShpBLIP_3"
			Me._ShpBLIP_3.Size = New Size(14, 21)
			Me._ShpBLIP_3.TabIndex = 0
			Me._ShpBLIP_2.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_2.Location = New Point(320, 140)
			Me._ShpBLIP_2.Name = "_ShpBLIP_2"
			Me._ShpBLIP_2.Size = New Size(14, 21)
			Me._ShpBLIP_2.TabIndex = 0
			Me._ShpBLIP_1.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_1.Location = New Point(172, 140)
			Me._ShpBLIP_1.Name = "_ShpBLIP_1"
			Me._ShpBLIP_1.Size = New Size(14, 21)
			Me._ShpBLIP_1.TabIndex = 0
			Me._ShpBLIP_0.BackColor = Color.FromArgb(64, 64, 64)
			Me._ShpBLIP_0.Location = New Point(24, 140)
			Me._ShpBLIP_0.Name = "_ShpBLIP_0"
			Me._ShpBLIP_0.Size = New Size(14, 21)
			Me._ShpBLIP_0.TabIndex = 0
			Me.Shape1.BackColor = SystemColors.Window
			Me.Shape1.Location = New Point(12, 28)
			Me.Shape1.Name = "Shape1"
			Me.Shape1.Size = New Size(905, 133)
			Me.Shape1.TabIndex = 0
			Me.txtFilmNrAufFilm.AcceptsReturn = True
			Me.txtFilmNrAufFilm.BackColor = SystemColors.Window
			Me.txtFilmNrAufFilm.Cursor = Cursors.IBeam
			Me.txtFilmNrAufFilm.ForeColor = Color.Red
			Me.txtFilmNrAufFilm.Location = New Point(198, 304)
			Me.txtFilmNrAufFilm.MaxLength = 0
			Me.txtFilmNrAufFilm.Name = "txtFilmNrAufFilm"
			Me.txtFilmNrAufFilm.[ReadOnly] = True
			Me.txtFilmNrAufFilm.RightToLeft = RightToLeft.No
			Me.txtFilmNrAufFilm.Size = New Size(163, 20)
			Me.txtFilmNrAufFilm.TabIndex = 331
			Me.txtFilmNrAufFilm.TextAlign = HorizontalAlignment.Right
			Me.cmdFortsetzung.BackColor = SystemColors.Control
			Me.cmdFortsetzung.Cursor = Cursors.[Default]
			Me.cmdFortsetzung.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdFortsetzung.ForeColor = SystemColors.ControlText
			Me.cmdFortsetzung.Location = New Point(196, 216)
			Me.cmdFortsetzung.Name = "cmdFortsetzung"
			Me.cmdFortsetzung.RightToLeft = RightToLeft.No
			Me.cmdFortsetzung.Size = New Size(177, 57)
			Me.cmdFortsetzung.TabIndex = 294
			Me.cmdFortsetzung.Text = "Roll is NOT a Coninuation"
			Me.cmdFortsetzung.UseVisualStyleBackColor = False
			Me.cmdRefilm.BackColor = SystemColors.Control
			Me.cmdRefilm.Cursor = Cursors.[Default]
			Me.cmdRefilm.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdRefilm.ForeColor = SystemColors.ControlText
			Me.cmdRefilm.Location = New Point(384, 336)
			Me.cmdRefilm.Name = "cmdRefilm"
			Me.cmdRefilm.RightToLeft = RightToLeft.No
			Me.cmdRefilm.Size = New Size(157, 49)
			Me.cmdRefilm.TabIndex = 279
			Me.cmdRefilm.Text = "Reexpose a single Roll"
			Me.cmdRefilm.UseVisualStyleBackColor = False
			Me.cmdCalcSpace.BackColor = SystemColors.Control
			Me.cmdCalcSpace.Cursor = Cursors.[Default]
			Me.cmdCalcSpace.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdCalcSpace.ForeColor = SystemColors.ControlText
			Me.cmdCalcSpace.Location = New Point(747, 393)
			Me.cmdCalcSpace.Name = "cmdCalcSpace"
			Me.cmdCalcSpace.RightToLeft = RightToLeft.No
			Me.cmdCalcSpace.Size = New Size(156, 52)
			Me.cmdCalcSpace.TabIndex = 202
			Me.cmdCalcSpace.Text = "Filmbedarf berechnen"
			Me.cmdCalcSpace.UseVisualStyleBackColor = False
			Me.cmdCalcSpace.Visible = False
			Me.cmdAbspulen.BackColor = SystemColors.Control
			Me.cmdAbspulen.Cursor = Cursors.[Default]
			Me.cmdAbspulen.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdAbspulen.ForeColor = SystemColors.ControlText
			Me.cmdAbspulen.Location = New Point(552, 280)
			Me.cmdAbspulen.Name = "cmdAbspulen"
			Me.cmdAbspulen.RightToLeft = RightToLeft.No
			Me.cmdAbspulen.Size = New Size(157, 49)
			Me.cmdAbspulen.TabIndex = 171
			Me.cmdAbspulen.Text = "Wind Film Roll"
			Me.cmdAbspulen.UseVisualStyleBackColor = False
			Me.cmdVorspann.BackColor = SystemColors.Control
			Me.cmdVorspann.Cursor = Cursors.[Default]
			Me.cmdVorspann.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdVorspann.ForeColor = SystemColors.ControlText
			Me.cmdVorspann.Location = New Point(384, 280)
			Me.cmdVorspann.Name = "cmdVorspann"
			Me.cmdVorspann.RightToLeft = RightToLeft.No
			Me.cmdVorspann.Size = New Size(157, 49)
			Me.cmdVorspann.TabIndex = 156
			Me.cmdVorspann.Text = "Make Trailer"
			Me.cmdVorspann.UseVisualStyleBackColor = False
			Me.cmbKopf.BackColor = SystemColors.Window
			Me.cmbKopf.Cursor = Cursors.[Default]
			Me.cmbKopf.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbKopf.Font = New Font("Arial", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmbKopf.ForeColor = SystemColors.WindowText
			Me.cmbKopf.Location = New Point(88, 375)
			Me.cmbKopf.Name = "cmbKopf"
			Me.cmbKopf.RightToLeft = RightToLeft.No
			Me.cmbKopf.Size = New Size(285, 24)
			Me.cmbKopf.TabIndex = 125
			Me._Picture1_6.BackColor = SystemColors.Control
			Me._Picture1_6.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_6.Cursor = Cursors.[Default]
			Me._Picture1_6.ForeColor = SystemColors.ControlText
			Me._Picture1_6.Location = New Point(940, 40)
			Me._Picture1_6.Name = "_Picture1_6"
			Me._Picture1_6.RightToLeft = RightToLeft.No
			Me._Picture1_6.Size = New Size(129, 89)
			Me._Picture1_6.TabIndex = 74
			Me._Picture1_6.TabStop = False
			Me._Picture1_6.Visible = False
			Me.chkNoPreview.BackColor = SystemColors.Control
			Me.chkNoPreview.Checked = True
			Me.chkNoPreview.CheckState = CheckState.Checked
			Me.chkNoPreview.Cursor = Cursors.[Default]
			Me.chkNoPreview.Font = New Font("Arial", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.chkNoPreview.ForeColor = SystemColors.ControlText
			Me.chkNoPreview.Location = New Point(736, 167)
			Me.chkNoPreview.Name = "chkNoPreview"
			Me.chkNoPreview.RightToLeft = RightToLeft.No
			Me.chkNoPreview.Size = New Size(164, 33)
			Me.chkNoPreview.TabIndex = 73
			Me.chkNoPreview.Text = "deactivate miniatures"
			Me.chkNoPreview.UseVisualStyleBackColor = False
			Me._Picture1_5.BackColor = Color.Black
			Me._Picture1_5.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_5.Cursor = Cursors.[Default]
			Me._Picture1_5.ForeColor = SystemColors.ControlText
			Me._Picture1_5.Location = New Point(764, 44)
			Me._Picture1_5.Name = "_Picture1_5"
			Me._Picture1_5.RightToLeft = RightToLeft.No
			Me._Picture1_5.Size = New Size(129, 89)
			Me._Picture1_5.TabIndex = 72
			Me._Picture1_5.TabStop = False
			Me._Picture1_4.BackColor = Color.Black
			Me._Picture1_4.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_4.Cursor = Cursors.[Default]
			Me._Picture1_4.ForeColor = SystemColors.ControlText
			Me._Picture1_4.Location = New Point(616, 44)
			Me._Picture1_4.Name = "_Picture1_4"
			Me._Picture1_4.RightToLeft = RightToLeft.No
			Me._Picture1_4.Size = New Size(129, 89)
			Me._Picture1_4.TabIndex = 71
			Me._Picture1_4.TabStop = False
			Me._Picture1_3.BackColor = Color.Black
			Me._Picture1_3.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_3.Cursor = Cursors.[Default]
			Me._Picture1_3.ForeColor = SystemColors.ControlText
			Me._Picture1_3.Location = New Point(468, 44)
			Me._Picture1_3.Name = "_Picture1_3"
			Me._Picture1_3.RightToLeft = RightToLeft.No
			Me._Picture1_3.Size = New Size(129, 89)
			Me._Picture1_3.TabIndex = 70
			Me._Picture1_3.TabStop = False
			Me._Picture1_2.BackColor = Color.Black
			Me._Picture1_2.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_2.Cursor = Cursors.[Default]
			Me._Picture1_2.ForeColor = SystemColors.ControlText
			Me._Picture1_2.Location = New Point(320, 44)
			Me._Picture1_2.Name = "_Picture1_2"
			Me._Picture1_2.RightToLeft = RightToLeft.No
			Me._Picture1_2.Size = New Size(129, 89)
			Me._Picture1_2.TabIndex = 69
			Me._Picture1_2.TabStop = False
			Me._Picture1_1.BackColor = Color.Black
			Me._Picture1_1.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_1.Cursor = Cursors.[Default]
			Me._Picture1_1.ForeColor = SystemColors.ControlText
			Me._Picture1_1.Location = New Point(172, 44)
			Me._Picture1_1.Name = "_Picture1_1"
			Me._Picture1_1.RightToLeft = RightToLeft.No
			Me._Picture1_1.Size = New Size(129, 89)
			Me._Picture1_1.TabIndex = 68
			Me._Picture1_1.TabStop = False
			Me._Picture1_0.BackColor = Color.Black
			Me._Picture1_0.BorderStyle = BorderStyle.Fixed3D
			Me._Picture1_0.Cursor = Cursors.[Default]
			Me._Picture1_0.ForeColor = SystemColors.ControlText
			Me._Picture1_0.Location = New Point(24, 44)
			Me._Picture1_0.Name = "_Picture1_0"
			Me._Picture1_0.RightToLeft = RightToLeft.No
			Me._Picture1_0.Size = New Size(129, 89)
			Me._Picture1_0.TabIndex = 67
			Me._Picture1_0.TabStop = False
			Me.tabSettings.Anchor = (AnchorStyles.Bottom Or AnchorStyles.Left Or AnchorStyles.Right)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage0)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage1)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage2)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage3)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage4)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage5)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage6)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage7)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage8)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage9)
			Me.tabSettings.Controls.Add(Me._tabSettings_TabPage10)
			Me.tabSettings.Font = New Font("Microsoft Sans Serif", 11.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.tabSettings.ItemSize = New Size(75, 30)
			Me.tabSettings.Location = New Point(0, 463)
			Me.tabSettings.Name = "tabSettings"
			Me.tabSettings.Padding = New Point(12, 3)
			Me.tabSettings.SelectedIndex = 2
			Me.tabSettings.Size = New Size(921, 306)
			Me.tabSettings.TabIndex = 26
			Me._tabSettings_TabPage0.Controls.Add(Me._Label_0)
			Me._tabSettings_TabPage0.Controls.Add(Me._Label_6)
			Me._tabSettings_TabPage0.Controls.Add(Me._Label_9)
			Me._tabSettings_TabPage0.Controls.Add(Me._Label_10)
			Me._tabSettings_TabPage0.Controls.Add(Me.frbAusrichtung)
			Me._tabSettings_TabPage0.Controls.Add(Me.Frame1)
			Me._tabSettings_TabPage0.Controls.Add(Me.chkAutoAlign)
			Me._tabSettings_TabPage0.Controls.Add(Me.Frame9)
			Me._tabSettings_TabPage0.Controls.Add(Me.chkDuplex)
			Me._tabSettings_TabPage0.Controls.Add(Me.txtMaxDuplex)
			Me._tabSettings_TabPage0.Controls.Add(Me.txtDuplexDist)
			Me._tabSettings_TabPage0.Controls.Add(Me.chkSmallLeft)
			Me._tabSettings_TabPage0.Controls.Add(Me.chkBigLeft)
			Me._tabSettings_TabPage0.Controls.Add(Me.Frame3)
			Me._tabSettings_TabPage0.Font = New Font("Arial", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._tabSettings_TabPage0.Location = New Point(4, 34)
			Me._tabSettings_TabPage0.Name = "_tabSettings_TabPage0"
			Me._tabSettings_TabPage0.Size = New Size(913, 268)
			Me._tabSettings_TabPage0.TabIndex = 0
			Me._tabSettings_TabPage0.Text = "Alignment"
			Me._Label_0.BackColor = SystemColors.Control
			Me._Label_0.Cursor = Cursors.[Default]
			Me._Label_0.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label_0.ForeColor = SystemColors.ControlText
			Me._Label_0.Location = New Point(95, 212)
			Me._Label_0.Name = "_Label_0"
			Me._Label_0.RightToLeft = RightToLeft.No
			Me._Label_0.Size = New Size(40, 13)
			Me._Label_0.TabIndex = 305
			Me._Label_0.Text = "Limit"
			Me._Label_6.BackColor = SystemColors.Control
			Me._Label_6.Cursor = Cursors.[Default]
			Me._Label_6.Font = New Font("Arial", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._Label_6.ForeColor = SystemColors.ControlText
			Me._Label_6.Location = New Point(195, 212)
			Me._Label_6.Name = "_Label_6"
			Me._Label_6.RightToLeft = RightToLeft.No
			Me._Label_6.Size = New Size(28, 13)
			Me._Label_6.TabIndex = 306
			Me._Label_6.Text = "mm"
			Me._Label_9.BackColor = SystemColors.Control
			Me._Label_9.Cursor = Cursors.[Default]
			Me._Label_9.Font = New Font("Arial", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._Label_9.ForeColor = SystemColors.ControlText
			Me._Label_9.Location = New Point(195, 236)
			Me._Label_9.Name = "_Label_9"
			Me._Label_9.RightToLeft = RightToLeft.No
			Me._Label_9.Size = New Size(28, 13)
			Me._Label_9.TabIndex = 308
			Me._Label_9.Text = "mm"
			Me._Label_10.BackColor = SystemColors.Control
			Me._Label_10.Cursor = Cursors.[Default]
			Me._Label_10.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label_10.ForeColor = SystemColors.ControlText
			Me._Label_10.Location = New Point(95, 236)
			Me._Label_10.Name = "_Label_10"
			Me._Label_10.RightToLeft = RightToLeft.No
			Me._Label_10.Size = New Size(42, 13)
			Me._Label_10.TabIndex = 309
			Me._Label_10.Text = "Dist."
			Me.frbAusrichtung.BackColor = SystemColors.Control
			Me.frbAusrichtung.Controls.Add(Me.chkAutoAlign180)
			Me.frbAusrichtung.Controls.Add(Me.opt270)
			Me.frbAusrichtung.Controls.Add(Me.opt90)
			Me.frbAusrichtung.Font = New Font("Microsoft Sans Serif", 9F)
			Me.frbAusrichtung.ForeColor = SystemColors.ControlText
			Me.frbAusrichtung.Location = New Point(12, 49)
			Me.frbAusrichtung.Name = "frbAusrichtung"
			Me.frbAusrichtung.Padding = New Padding(0)
			Me.frbAusrichtung.RightToLeft = RightToLeft.No
			Me.frbAusrichtung.Size = New Size(449, 92)
			Me.frbAusrichtung.TabIndex = 27
			Me.frbAusrichtung.TabStop = False
			Me.frbAusrichtung.Text = "Automatic Alignment Rotation"
			Me.chkAutoAlign180.BackColor = SystemColors.Control
			Me.chkAutoAlign180.Cursor = Cursors.[Default]
			Me.chkAutoAlign180.ForeColor = SystemColors.ControlText
			Me.chkAutoAlign180.Location = New Point(12, 52)
			Me.chkAutoAlign180.Name = "chkAutoAlign180"
			Me.chkAutoAlign180.RightToLeft = RightToLeft.No
			Me.chkAutoAlign180.Size = New Size(409, 29)
			Me.chkAutoAlign180.TabIndex = 203
			Me.chkAutoAlign180.Text = "Rotate Documents which don't need auto-alignment by 180°"
			Me.chkAutoAlign180.UseVisualStyleBackColor = False
			Me.opt270.BackColor = SystemColors.Control
			Me.opt270.Cursor = Cursors.[Default]
			Me.opt270.Font = New Font("Microsoft Sans Serif", 9F)
			Me.opt270.ForeColor = SystemColors.ControlText
			Me.opt270.Location = New Point(199, 24)
			Me.opt270.Name = "opt270"
			Me.opt270.RightToLeft = RightToLeft.No
			Me.opt270.Size = New Size(222, 22)
			Me.opt270.TabIndex = 29
			Me.opt270.TabStop = True
			Me.opt270.Text = "90° counter clockwise"
			Me.opt270.UseVisualStyleBackColor = False
			Me.opt90.BackColor = SystemColors.Control
			Me.opt90.Cursor = Cursors.[Default]
			Me.opt90.Font = New Font("Microsoft Sans Serif", 9F)
			Me.opt90.ForeColor = SystemColors.ControlText
			Me.opt90.Location = New Point(12, 24)
			Me.opt90.Name = "opt90"
			Me.opt90.RightToLeft = RightToLeft.No
			Me.opt90.Size = New Size(181, 22)
			Me.opt90.TabIndex = 28
			Me.opt90.TabStop = True
			Me.opt90.Text = "90° clockwise"
			Me.opt90.UseVisualStyleBackColor = False
			Me.Frame1.BackColor = SystemColors.Control
			Me.Frame1.Controls.Add(Me.optFest90)
			Me.Frame1.Controls.Add(Me.optFest270)
			Me.Frame1.Controls.Add(Me.optFest180)
			Me.Frame1.Controls.Add(Me.optFest0)
			Me.Frame1.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Frame1.ForeColor = SystemColors.ControlText
			Me.Frame1.Location = New Point(12, 144)
			Me.Frame1.Name = "Frame1"
			Me.Frame1.Padding = New Padding(0)
			Me.Frame1.RightToLeft = RightToLeft.No
			Me.Frame1.Size = New Size(449, 57)
			Me.Frame1.TabIndex = 30
			Me.Frame1.TabStop = False
			Me.Frame1.Text = "Fix Alignment"
			Me.optFest90.BackColor = SystemColors.Control
			Me.optFest90.Cursor = Cursors.[Default]
			Me.optFest90.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.optFest90.ForeColor = SystemColors.ControlText
			Me.optFest90.Location = New Point(9, 26)
			Me.optFest90.Name = "optFest90"
			Me.optFest90.RightToLeft = RightToLeft.No
			Me.optFest90.Size = New Size(144, 19)
			Me.optFest90.TabIndex = 34
			Me.optFest90.TabStop = True
			Me.optFest90.Text = "90° clockwise"
			Me.optFest90.UseVisualStyleBackColor = False
			Me.optFest270.BackColor = SystemColors.Control
			Me.optFest270.Cursor = Cursors.[Default]
			Me.optFest270.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.optFest270.ForeColor = SystemColors.ControlText
			Me.optFest270.Location = New Point(161, 25)
			Me.optFest270.Name = "optFest270"
			Me.optFest270.RightToLeft = RightToLeft.No
			Me.optFest270.Size = New Size(134, 19)
			Me.optFest270.TabIndex = 33
			Me.optFest270.TabStop = True
			Me.optFest270.Text = "90° counter clockwise"
			Me.optFest270.UseVisualStyleBackColor = False
			Me.optFest180.BackColor = SystemColors.Control
			Me.optFest180.Cursor = Cursors.[Default]
			Me.optFest180.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.optFest180.ForeColor = SystemColors.ControlText
			Me.optFest180.Location = New Point(307, 27)
			Me.optFest180.Name = "optFest180"
			Me.optFest180.RightToLeft = RightToLeft.No
			Me.optFest180.Size = New Size(73, 17)
			Me.optFest180.TabIndex = 32
			Me.optFest180.TabStop = True
			Me.optFest180.Text = "180°"
			Me.optFest180.UseVisualStyleBackColor = False
			Me.optFest0.BackColor = SystemColors.Control
			Me.optFest0.Cursor = Cursors.[Default]
			Me.optFest0.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.optFest0.ForeColor = SystemColors.ControlText
			Me.optFest0.Location = New Point(386, 26)
			Me.optFest0.Name = "optFest0"
			Me.optFest0.RightToLeft = RightToLeft.No
			Me.optFest0.Size = New Size(60, 19)
			Me.optFest0.TabIndex = 31
			Me.optFest0.TabStop = True
			Me.optFest0.Text = "w/o"
			Me.optFest0.UseVisualStyleBackColor = False
			Me.chkAutoAlign.BackColor = SystemColors.Control
			Me.chkAutoAlign.Cursor = Cursors.[Default]
			Me.chkAutoAlign.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.chkAutoAlign.ForeColor = SystemColors.ControlText
			Me.chkAutoAlign.Location = New Point(20, 17)
			Me.chkAutoAlign.Name = "chkAutoAlign"
			Me.chkAutoAlign.RightToLeft = RightToLeft.No
			Me.chkAutoAlign.Size = New Size(213, 21)
			Me.chkAutoAlign.TabIndex = 61
			Me.chkAutoAlign.Text = "Automatic Alignment"
			Me.chkAutoAlign.UseVisualStyleBackColor = False
			Me.Frame9.BackColor = SystemColors.Control
			Me.Frame9.Controls.Add(Me.optLagerichtig)
			Me.Frame9.Controls.Add(Me.chkA3PortraitDrehen)
			Me.Frame9.Controls.Add(Me.chkA4LSDrehen)
			Me.Frame9.Controls.Add(Me.Frame15)
			Me.Frame9.Controls.Add(Me.Frame14)
			Me.Frame9.Controls.Add(Me.chkOneToOne)
			Me.Frame9.Controls.Add(Me.txtFactor)
			Me.Frame9.Controls.Add(Me.txtToleranz)
			Me.Frame9.Controls.Add(Me._Label_33)
			Me.Frame9.Controls.Add(Me._Label_32)
			Me.Frame9.Controls.Add(Me._label__5)
			Me.Frame9.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Frame9.ForeColor = SystemColors.ControlText
			Me.Frame9.Location = New Point(468, 17)
			Me.Frame9.Name = "Frame9"
			Me.Frame9.Padding = New Padding(0)
			Me.Frame9.RightToLeft = RightToLeft.No
			Me.Frame9.Size = New Size(297, 249)
			Me.Frame9.TabIndex = 189
			Me.Frame9.TabStop = False
			Me.Frame9.Text = "1:1 Exposure (for Landscape Heads only)"
			Me.optLagerichtig.BackColor = SystemColors.Control
			Me.optLagerichtig.Cursor = Cursors.[Default]
			Me.optLagerichtig.ForeColor = SystemColors.ControlText
			Me.optLagerichtig.Location = New Point(24, 115)
			Me.optLagerichtig.Name = "optLagerichtig"
			Me.optLagerichtig.RightToLeft = RightToLeft.No
			Me.optLagerichtig.Size = New Size(265, 25)
			Me.optLagerichtig.TabIndex = 319
			Me.optLagerichtig.Text = "Optimal Alignment has Priority"
			Me.optLagerichtig.UseVisualStyleBackColor = False
			Me.optLagerichtig.Visible = False
			Me.chkA3PortraitDrehen.BackColor = SystemColors.Control
			Me.chkA3PortraitDrehen.Cursor = Cursors.[Default]
			Me.chkA3PortraitDrehen.ForeColor = SystemColors.ControlText
			Me.chkA3PortraitDrehen.Location = New Point(24, 159)
			Me.chkA3PortraitDrehen.Name = "chkA3PortraitDrehen"
			Me.chkA3PortraitDrehen.RightToLeft = RightToLeft.No
			Me.chkA3PortraitDrehen.Size = New Size(170, 25)
			Me.chkA3PortraitDrehen.TabIndex = 302
			Me.chkA3PortraitDrehen.Text = "Rotate A3 Portrait"
			Me.chkA3PortraitDrehen.UseVisualStyleBackColor = False
			Me.chkA4LSDrehen.BackColor = SystemColors.Control
			Me.chkA4LSDrehen.Cursor = Cursors.[Default]
			Me.chkA4LSDrehen.ForeColor = SystemColors.ControlText
			Me.chkA4LSDrehen.Location = New Point(24, 206)
			Me.chkA4LSDrehen.Name = "chkA4LSDrehen"
			Me.chkA4LSDrehen.RightToLeft = RightToLeft.No
			Me.chkA4LSDrehen.Size = New Size(170, 25)
			Me.chkA4LSDrehen.TabIndex = 301
			Me.chkA4LSDrehen.Text = "Rotate A4 Landscape"
			Me.chkA4LSDrehen.UseVisualStyleBackColor = False
			Me.Frame15.BackColor = SystemColors.Control
			Me.Frame15.Controls.Add(Me.optLA3)
			Me.Frame15.Controls.Add(Me.optRA3)
			Me.Frame15.Cursor = Cursors.[Default]
			Me.Frame15.ForeColor = SystemColors.ControlText
			Me.Frame15.Location = New Point(196, 154)
			Me.Frame15.Name = "Frame15"
			Me.Frame15.RightToLeft = RightToLeft.No
			Me.Frame15.Size = New Size(98, 36)
			Me.Frame15.TabIndex = 298
			Me.optLA3.Appearance = Appearance.Button
			Me.optLA3.BackColor = SystemColors.Control
			Me.optLA3.Cursor = Cursors.[Default]
			Me.optLA3.FlatAppearance.CheckedBackColor = Color.Red
			Me.optLA3.FlatStyle = FlatStyle.Flat
			Me.optLA3.ForeColor = SystemColors.ControlText
			Me.optLA3.Image = CType(componentResourceManager.GetObject("optLA3.Image"), Image)
			Me.optLA3.Location = New Point(50, 2)
			Me.optLA3.Name = "optLA3"
			Me.optLA3.RightToLeft = RightToLeft.No
			Me.optLA3.Size = New Size(43, 33)
			Me.optLA3.TabIndex = 300
			Me.optLA3.TabStop = True
			Me.optLA3.TextAlign = ContentAlignment.BottomCenter
			Me.optLA3.UseVisualStyleBackColor = False
			Me.optRA3.Appearance = Appearance.Button
			Me.optRA3.BackColor = SystemColors.Control
			Me.optRA3.Cursor = Cursors.[Default]
			Me.optRA3.FlatAppearance.CheckedBackColor = Color.Red
			Me.optRA3.FlatStyle = FlatStyle.Flat
			Me.optRA3.ForeColor = SystemColors.ControlText
			Me.optRA3.Image = CType(componentResourceManager.GetObject("optRA3.Image"), Image)
			Me.optRA3.Location = New Point(3, 2)
			Me.optRA3.Name = "optRA3"
			Me.optRA3.RightToLeft = RightToLeft.No
			Me.optRA3.Size = New Size(43, 33)
			Me.optRA3.TabIndex = 299
			Me.optRA3.TabStop = True
			Me.optRA3.TextAlign = ContentAlignment.BottomCenter
			Me.optRA3.UseVisualStyleBackColor = False
			Me.Frame14.BackColor = SystemColors.Control
			Me.Frame14.Controls.Add(Me.optLA4)
			Me.Frame14.Controls.Add(Me.optRA4)
			Me.Frame14.Cursor = Cursors.[Default]
			Me.Frame14.ForeColor = SystemColors.ControlText
			Me.Frame14.Location = New Point(196, 201)
			Me.Frame14.Name = "Frame14"
			Me.Frame14.RightToLeft = RightToLeft.No
			Me.Frame14.Size = New Size(98, 36)
			Me.Frame14.TabIndex = 295
			Me.optLA4.Appearance = Appearance.Button
			Me.optLA4.BackColor = SystemColors.Control
			Me.optLA4.Cursor = Cursors.[Default]
			Me.optLA4.FlatAppearance.CheckedBackColor = Color.Red
			Me.optLA4.FlatStyle = FlatStyle.Flat
			Me.optLA4.ForeColor = SystemColors.ControlText
			Me.optLA4.Image = CType(componentResourceManager.GetObject("optLA4.Image"), Image)
			Me.optLA4.Location = New Point(50, 2)
			Me.optLA4.Name = "optLA4"
			Me.optLA4.RightToLeft = RightToLeft.No
			Me.optLA4.Size = New Size(43, 33)
			Me.optLA4.TabIndex = 297
			Me.optLA4.TabStop = True
			Me.optLA4.TextAlign = ContentAlignment.BottomCenter
			Me.optLA4.UseVisualStyleBackColor = False
			Me.optRA4.Appearance = Appearance.Button
			Me.optRA4.BackColor = SystemColors.Control
			Me.optRA4.Cursor = Cursors.[Default]
			Me.optRA4.FlatAppearance.CheckedBackColor = Color.Red
			Me.optRA4.FlatStyle = FlatStyle.Flat
			Me.optRA4.ForeColor = SystemColors.ControlText
			Me.optRA4.Image = CType(componentResourceManager.GetObject("optRA4.Image"), Image)
			Me.optRA4.Location = New Point(3, 2)
			Me.optRA4.Name = "optRA4"
			Me.optRA4.RightToLeft = RightToLeft.No
			Me.optRA4.Size = New Size(43, 33)
			Me.optRA4.TabIndex = 296
			Me.optRA4.TabStop = True
			Me.optRA4.TextAlign = ContentAlignment.BottomCenter
			Me.optRA4.UseVisualStyleBackColor = False
			Me.chkOneToOne.BackColor = SystemColors.Control
			Me.chkOneToOne.Cursor = Cursors.[Default]
			Me.chkOneToOne.ForeColor = SystemColors.ControlText
			Me.chkOneToOne.Location = New Point(24, 24)
			Me.chkOneToOne.Name = "chkOneToOne"
			Me.chkOneToOne.RightToLeft = RightToLeft.No
			Me.chkOneToOne.Size = New Size(213, 21)
			Me.chkOneToOne.TabIndex = 192
			Me.chkOneToOne.Text = "Use 1:1 Exposure"
			Me.chkOneToOne.UseVisualStyleBackColor = False
			Me.txtToleranz.AcceptsReturn = True
			Me.txtToleranz.BackColor = SystemColors.Window
			Me.txtToleranz.Cursor = Cursors.IBeam
			Me.txtToleranz.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtToleranz.ForeColor = SystemColors.WindowText
			Me.txtToleranz.Location = New Point(228, 80)
			Me.txtToleranz.MaxLength = 0
			Me.txtToleranz.Name = "txtToleranz"
			Me.txtToleranz.RightToLeft = RightToLeft.No
			Me.txtToleranz.Size = New Size(46, 22)
			Me.txtToleranz.TabIndex = 190
			Me.txtToleranz.TextAlign = HorizontalAlignment.Right
			Me._Label_33.BackColor = SystemColors.Control
			Me._Label_33.Cursor = Cursors.[Default]
			Me._Label_33.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label_33.ForeColor = SystemColors.ControlText
			Me._Label_33.Location = New Point(22, 54)
			Me._Label_33.Name = "_Label_33"
			Me._Label_33.RightToLeft = RightToLeft.No
			Me._Label_33.Size = New Size(141, 20)
			Me._Label_33.TabIndex = 195
			Me._Label_33.Text = "Reduction Factor"
			Me._Label_32.BackColor = SystemColors.Control
			Me._Label_32.Cursor = Cursors.[Default]
			Me._Label_32.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label_32.ForeColor = SystemColors.ControlText
			Me._Label_32.Location = New Point(22, 84)
			Me._Label_32.Name = "_Label_32"
			Me._Label_32.RightToLeft = RightToLeft.No
			Me._Label_32.Size = New Size(197, 17)
			Me._Label_32.TabIndex = 194
			Me._Label_32.Text = "Tolerance for Formular Limit"
			Me._label__5.BackColor = SystemColors.Control
			Me._label__5.Cursor = Cursors.[Default]
			Me._label__5.Font = New Font("Arial", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._label__5.ForeColor = SystemColors.ControlText
			Me._label__5.Location = New Point(278, 84)
			Me._label__5.Name = "_label__5"
			Me._label__5.RightToLeft = RightToLeft.No
			Me._label__5.Size = New Size(17, 13)
			Me._label__5.TabIndex = 193
			Me._label__5.Text = "%"
			Me.chkDuplex.BackColor = SystemColors.Control
			Me.chkDuplex.Cursor = Cursors.[Default]
			Me.chkDuplex.Font = New Font("Microsoft Sans Serif", 9F)
			Me.chkDuplex.ForeColor = SystemColors.ControlText
			Me.chkDuplex.Location = New Point(16, 206)
			Me.chkDuplex.Name = "chkDuplex"
			Me.chkDuplex.RightToLeft = RightToLeft.No
			Me.chkDuplex.Size = New Size(102, 45)
			Me.chkDuplex.TabIndex = 303
			Me.chkDuplex.Text = "Duplex Expose"
			Me.chkDuplex.UseVisualStyleBackColor = False
			Me.txtDuplexDist.AcceptsReturn = True
			Me.txtDuplexDist.BackColor = SystemColors.Window
			Me.txtDuplexDist.Cursor = Cursors.IBeam
			Me.txtDuplexDist.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtDuplexDist.ForeColor = SystemColors.WindowText
			Me.txtDuplexDist.Location = New Point(139, 232)
			Me.txtDuplexDist.MaxLength = 0
			Me.txtDuplexDist.Name = "txtDuplexDist"
			Me.txtDuplexDist.RightToLeft = RightToLeft.No
			Me.txtDuplexDist.Size = New Size(49, 22)
			Me.txtDuplexDist.TabIndex = 307
			Me.txtDuplexDist.TextAlign = HorizontalAlignment.Right
			Me.chkSmallLeft.BackColor = SystemColors.Control
			Me.chkSmallLeft.Cursor = Cursors.[Default]
			Me.chkSmallLeft.Font = New Font("Microsoft Sans Serif", 9F)
			Me.chkSmallLeft.ForeColor = SystemColors.ControlText
			Me.chkSmallLeft.Location = New Point(229, 208)
			Me.chkSmallLeft.Name = "chkSmallLeft"
			Me.chkSmallLeft.RightToLeft = RightToLeft.No
			Me.chkSmallLeft.Size = New Size(229, 25)
			Me.chkSmallLeft.TabIndex = 310
			Me.chkSmallLeft.Text = "Rotate small Docs CCW"
			Me.chkSmallLeft.UseVisualStyleBackColor = False
			Me.chkBigLeft.BackColor = SystemColors.Control
			Me.chkBigLeft.Cursor = Cursors.[Default]
			Me.chkBigLeft.Font = New Font("Microsoft Sans Serif", 9F)
			Me.chkBigLeft.ForeColor = SystemColors.ControlText
			Me.chkBigLeft.Location = New Point(229, 232)
			Me.chkBigLeft.Name = "chkBigLeft"
			Me.chkBigLeft.RightToLeft = RightToLeft.No
			Me.chkBigLeft.Size = New Size(233, 25)
			Me.chkBigLeft.TabIndex = 311
			Me.chkBigLeft.Text = "Rotate large Docs CW"
			Me.chkBigLeft.UseVisualStyleBackColor = False
			Me.chkBigLeft.Visible = False
			Me.Frame3.BackColor = SystemColors.Control
			Me.Frame3.Controls.Add(Me.optOben)
			Me.Frame3.Controls.Add(Me.optUnten)
			Me.Frame3.Controls.Add(Me.optCenter)
			Me.Frame3.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Frame3.ForeColor = SystemColors.ControlText
			Me.Frame3.Location = New Point(768, 17)
			Me.Frame3.Name = "Frame3"
			Me.Frame3.Padding = New Padding(0)
			Me.Frame3.RightToLeft = RightToLeft.No
			Me.Frame3.Size = New Size(125, 255)
			Me.Frame3.TabIndex = 315
			Me.Frame3.TabStop = False
			Me.Frame3.Text = "Alignment"
			Me.optOben.BackColor = SystemColors.Control
			Me.optOben.Cursor = Cursors.[Default]
			Me.optOben.ForeColor = SystemColors.ControlText
			Me.optOben.Location = New Point(26, 53)
			Me.optOben.Name = "optOben"
			Me.optOben.RightToLeft = RightToLeft.No
			Me.optOben.Size = New Size(71, 21)
			Me.optOben.TabIndex = 318
			Me.optOben.TabStop = True
			Me.optOben.Text = "Top"
			Me.optOben.UseVisualStyleBackColor = False
			Me.optUnten.BackColor = SystemColors.Control
			Me.optUnten.Cursor = Cursors.[Default]
			Me.optUnten.ForeColor = SystemColors.ControlText
			Me.optUnten.Location = New Point(26, 120)
			Me.optUnten.Name = "optUnten"
			Me.optUnten.RightToLeft = RightToLeft.No
			Me.optUnten.Size = New Size(71, 21)
			Me.optUnten.TabIndex = 317
			Me.optUnten.TabStop = True
			Me.optUnten.Text = "Bottom"
			Me.optUnten.UseVisualStyleBackColor = False
			Me.optCenter.BackColor = SystemColors.Control
			Me.optCenter.Cursor = Cursors.[Default]
			Me.optCenter.ForeColor = SystemColors.ControlText
			Me.optCenter.Location = New Point(26, 183)
			Me.optCenter.Name = "optCenter"
			Me.optCenter.RightToLeft = RightToLeft.No
			Me.optCenter.Size = New Size(71, 21)
			Me.optCenter.TabIndex = 316
			Me.optCenter.TabStop = True
			Me.optCenter.Text = "Middle"
			Me.optCenter.UseVisualStyleBackColor = False
			Me._tabSettings_TabPage1.Controls.Add(Me.chkStartBlipAtOne)
			Me._tabSettings_TabPage1.Controls.Add(Me._chk1PAgePDFs_1)
			Me._tabSettings_TabPage1.Controls.Add(Me._chk1PAgePDFs_0)
			Me._tabSettings_TabPage1.Controls.Add(Me.Frame8)
			Me._tabSettings_TabPage1.Controls.Add(Me.frmPosition)
			Me._tabSettings_TabPage1.Controls.Add(Me.Frame2)
			Me._tabSettings_TabPage1.Controls.Add(Me.chkBlip)
			Me._tabSettings_TabPage1.Location = New Point(4, 34)
			Me._tabSettings_TabPage1.Name = "_tabSettings_TabPage1"
			Me._tabSettings_TabPage1.Size = New Size(913, 268)
			Me._tabSettings_TabPage1.TabIndex = 1
			Me._tabSettings_TabPage1.Text = "BLIP"
			Me.chkStartBlipAtOne.BackColor = SystemColors.Control
			Me.chkStartBlipAtOne.Cursor = Cursors.[Default]
			Me.chkStartBlipAtOne.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.chkStartBlipAtOne.ForeColor = SystemColors.ControlText
			Me.chkStartBlipAtOne.Location = New Point(171, 24)
			Me.chkStartBlipAtOne.Name = "chkStartBlipAtOne"
			Me.chkStartBlipAtOne.RightToLeft = RightToLeft.No
			Me.chkStartBlipAtOne.Size = New Size(718, 25)
			Me.chkStartBlipAtOne.TabIndex = 325
			Me.chkStartBlipAtOne.Text = "Level 3 Blips 3 do start at 1 in the protocol"
			Me.chkStartBlipAtOne.UseVisualStyleBackColor = False
			Me.Frame8.BackColor = SystemColors.Control
			Me.Frame8.Controls.Add(Me._txtBlipHoeheGross_0)
			Me.Frame8.Controls.Add(Me._txtBlipHoeheMittel_0)
			Me.Frame8.Controls.Add(Me._txtBlipHoeheKlein_0)
			Me.Frame8.Controls.Add(Me._txtBlipBreiteKlein_0)
			Me.Frame8.Controls.Add(Me._txtBlipBreiteMittel_0)
			Me.Frame8.Controls.Add(Me._txtBlipBreiteGross_0)
			Me.Frame8.Controls.Add(Me._Label19_3)
			Me.Frame8.Controls.Add(Me._Label19_2)
			Me.Frame8.Controls.Add(Me._label__19)
			Me.Frame8.Controls.Add(Me.Label56)
			Me.Frame8.Controls.Add(Me.Label57)
			Me.Frame8.Controls.Add(Me.Label58)
			Me.Frame8.Controls.Add(Me.Label59)
			Me.Frame8.Controls.Add(Me._Label1_4)
			Me.Frame8.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Frame8.ForeColor = SystemColors.ControlText
			Me.Frame8.Location = New Point(334, 64)
			Me.Frame8.Name = "Frame8"
			Me.Frame8.Padding = New Padding(0)
			Me.Frame8.RightToLeft = RightToLeft.No
			Me.Frame8.Size = New Size(257, 124)
			Me.Frame8.TabIndex = 103
			Me.Frame8.TabStop = False
			Me.Frame8.Text = "BLIP Sizes"
			Me._txtBlipHoeheGross_0.AcceptsReturn = True
			Me._txtBlipHoeheGross_0.BackColor = Color.FromArgb(255, 255, 128)
			Me._txtBlipHoeheGross_0.Cursor = Cursors.IBeam
			Me._txtBlipHoeheGross_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipHoeheGross_0.ForeColor = SystemColors.WindowText
			Me._txtBlipHoeheGross_0.Location = New Point(136, 40)
			Me._txtBlipHoeheGross_0.MaxLength = 0
			Me._txtBlipHoeheGross_0.Name = "_txtBlipHoeheGross_0"
			Me._txtBlipHoeheGross_0.RightToLeft = RightToLeft.No
			Me._txtBlipHoeheGross_0.Size = New Size(49, 22)
			Me._txtBlipHoeheGross_0.TabIndex = 109
			Me._txtBlipHoeheGross_0.Text = "0"
			Me._txtBlipHoeheGross_0.TextAlign = HorizontalAlignment.Right
			Me._txtBlipHoeheMittel_0.AcceptsReturn = True
			Me._txtBlipHoeheMittel_0.BackColor = SystemColors.Window
			Me._txtBlipHoeheMittel_0.Cursor = Cursors.IBeam
			Me._txtBlipHoeheMittel_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipHoeheMittel_0.ForeColor = SystemColors.WindowText
			Me._txtBlipHoeheMittel_0.Location = New Point(136, 68)
			Me._txtBlipHoeheMittel_0.MaxLength = 0
			Me._txtBlipHoeheMittel_0.Name = "_txtBlipHoeheMittel_0"
			Me._txtBlipHoeheMittel_0.RightToLeft = RightToLeft.No
			Me._txtBlipHoeheMittel_0.Size = New Size(49, 22)
			Me._txtBlipHoeheMittel_0.TabIndex = 108
			Me._txtBlipHoeheMittel_0.Text = "0"
			Me._txtBlipHoeheMittel_0.TextAlign = HorizontalAlignment.Right
			Me._txtBlipHoeheKlein_0.AcceptsReturn = True
			Me._txtBlipHoeheKlein_0.BackColor = SystemColors.Window
			Me._txtBlipHoeheKlein_0.Cursor = Cursors.IBeam
			Me._txtBlipHoeheKlein_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipHoeheKlein_0.ForeColor = SystemColors.WindowText
			Me._txtBlipHoeheKlein_0.Location = New Point(136, 95)
			Me._txtBlipHoeheKlein_0.MaxLength = 0
			Me._txtBlipHoeheKlein_0.Name = "_txtBlipHoeheKlein_0"
			Me._txtBlipHoeheKlein_0.RightToLeft = RightToLeft.No
			Me._txtBlipHoeheKlein_0.Size = New Size(49, 22)
			Me._txtBlipHoeheKlein_0.TabIndex = 107
			Me._txtBlipHoeheKlein_0.Text = "0"
			Me._txtBlipHoeheKlein_0.TextAlign = HorizontalAlignment.Right
			Me._txtBlipBreiteKlein_0.AcceptsReturn = True
			Me._txtBlipBreiteKlein_0.BackColor = SystemColors.Window
			Me._txtBlipBreiteKlein_0.Cursor = Cursors.IBeam
			Me._txtBlipBreiteKlein_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipBreiteKlein_0.ForeColor = SystemColors.WindowText
			Me._txtBlipBreiteKlein_0.Location = New Point(65, 95)
			Me._txtBlipBreiteKlein_0.MaxLength = 0
			Me._txtBlipBreiteKlein_0.Name = "_txtBlipBreiteKlein_0"
			Me._txtBlipBreiteKlein_0.RightToLeft = RightToLeft.No
			Me._txtBlipBreiteKlein_0.Size = New Size(49, 22)
			Me._txtBlipBreiteKlein_0.TabIndex = 106
			Me._txtBlipBreiteKlein_0.Text = "0"
			Me._txtBlipBreiteKlein_0.TextAlign = HorizontalAlignment.Right
			Me._txtBlipBreiteMittel_0.AcceptsReturn = True
			Me._txtBlipBreiteMittel_0.BackColor = SystemColors.Window
			Me._txtBlipBreiteMittel_0.Cursor = Cursors.IBeam
			Me._txtBlipBreiteMittel_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipBreiteMittel_0.ForeColor = SystemColors.WindowText
			Me._txtBlipBreiteMittel_0.Location = New Point(65, 68)
			Me._txtBlipBreiteMittel_0.MaxLength = 0
			Me._txtBlipBreiteMittel_0.Name = "_txtBlipBreiteMittel_0"
			Me._txtBlipBreiteMittel_0.RightToLeft = RightToLeft.No
			Me._txtBlipBreiteMittel_0.Size = New Size(49, 22)
			Me._txtBlipBreiteMittel_0.TabIndex = 105
			Me._txtBlipBreiteMittel_0.Text = "0"
			Me._txtBlipBreiteMittel_0.TextAlign = HorizontalAlignment.Right
			Me._txtBlipBreiteGross_0.AcceptsReturn = True
			Me._txtBlipBreiteGross_0.BackColor = Color.FromArgb(255, 255, 128)
			Me._txtBlipBreiteGross_0.Cursor = Cursors.IBeam
			Me._txtBlipBreiteGross_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtBlipBreiteGross_0.ForeColor = SystemColors.WindowText
			Me._txtBlipBreiteGross_0.Location = New Point(65, 40)
			Me._txtBlipBreiteGross_0.MaxLength = 0
			Me._txtBlipBreiteGross_0.Name = "_txtBlipBreiteGross_0"
			Me._txtBlipBreiteGross_0.RightToLeft = RightToLeft.No
			Me._txtBlipBreiteGross_0.Size = New Size(49, 22)
			Me._txtBlipBreiteGross_0.TabIndex = 104
			Me._txtBlipBreiteGross_0.Text = "0"
			Me._txtBlipBreiteGross_0.TextAlign = HorizontalAlignment.Right
			Me._Label19_3.BackColor = SystemColors.Control
			Me._Label19_3.Cursor = Cursors.[Default]
			Me._Label19_3.ForeColor = SystemColors.ControlText
			Me._Label19_3.Location = New Point(188, 101)
			Me._Label19_3.Name = "_Label19_3"
			Me._Label19_3.RightToLeft = RightToLeft.No
			Me._Label19_3.Size = New Size(34, 13)
			Me._Label19_3.TabIndex = 121
			Me._Label19_3.Text = "mm"
			Me._Label19_2.BackColor = SystemColors.Control
			Me._Label19_2.Cursor = Cursors.[Default]
			Me._Label19_2.ForeColor = SystemColors.ControlText
			Me._Label19_2.Location = New Point(188, 72)
			Me._Label19_2.Name = "_Label19_2"
			Me._Label19_2.RightToLeft = RightToLeft.No
			Me._Label19_2.Size = New Size(34, 13)
			Me._Label19_2.TabIndex = 120
			Me._Label19_2.Text = "mm"
			Me._label__19.BackColor = SystemColors.Control
			Me._label__19.Cursor = Cursors.[Default]
			Me._label__19.ForeColor = SystemColors.ControlText
			Me._label__19.Location = New Point(188, 44)
			Me._label__19.Name = "_label__19"
			Me._label__19.RightToLeft = RightToLeft.No
			Me._label__19.Size = New Size(34, 13)
			Me._label__19.TabIndex = 119
			Me._label__19.Text = "mm"
			Me.Label56.BackColor = SystemColors.Control
			Me.Label56.Cursor = Cursors.[Default]
			Me.Label56.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label56.ForeColor = SystemColors.ControlText
			Me.Label56.Location = New Point(136, 22)
			Me.Label56.Name = "Label56"
			Me.Label56.RightToLeft = RightToLeft.No
			Me.Label56.Size = New Size(49, 19)
			Me.Label56.TabIndex = 114
			Me.Label56.Text = "Height"
			Me.Label56.TextAlign = ContentAlignment.TopCenter
			Me.Label57.BackColor = SystemColors.Control
			Me.Label57.Cursor = Cursors.[Default]
			Me.Label57.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label57.ForeColor = SystemColors.ControlText
			Me.Label57.Location = New Point(65, 21)
			Me.Label57.Name = "Label57"
			Me.Label57.RightToLeft = RightToLeft.No
			Me.Label57.Size = New Size(49, 16)
			Me.Label57.TabIndex = 113
			Me.Label57.Text = "Width"
			Me.Label57.TextAlign = ContentAlignment.TopCenter
			Me.Label58.BackColor = SystemColors.Control
			Me.Label58.Cursor = Cursors.[Default]
			Me.Label58.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label58.ForeColor = SystemColors.ControlText
			Me.Label58.Location = New Point(8, 95)
			Me.Label58.Name = "Label58"
			Me.Label58.RightToLeft = RightToLeft.No
			Me.Label58.Size = New Size(41, 17)
			Me.Label58.TabIndex = 112
			Me.Label58.Text = "small"
			Me.Label59.BackColor = SystemColors.Control
			Me.Label59.Cursor = Cursors.[Default]
			Me.Label59.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label59.ForeColor = SystemColors.ControlText
			Me.Label59.Location = New Point(8, 68)
			Me.Label59.Name = "Label59"
			Me.Label59.RightToLeft = RightToLeft.No
			Me.Label59.Size = New Size(54, 17)
			Me.Label59.TabIndex = 111
			Me.Label59.Text = "medium"
			Me._Label1_4.BackColor = SystemColors.Control
			Me._Label1_4.Cursor = Cursors.[Default]
			Me._Label1_4.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label1_4.ForeColor = SystemColors.ControlText
			Me._Label1_4.Location = New Point(8, 40)
			Me._Label1_4.Name = "_Label1_4"
			Me._Label1_4.RightToLeft = RightToLeft.No
			Me._Label1_4.Size = New Size(41, 17)
			Me._Label1_4.TabIndex = 110
			Me._Label1_4.Text = "large"
			Me.frmPosition.BackColor = SystemColors.Control
			Me.frmPosition.Controls.Add(Me.optUeberBlip)
			Me.frmPosition.Controls.Add(Me.optNebenBlip)
			Me.frmPosition.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.frmPosition.ForeColor = SystemColors.ControlText
			Me.frmPosition.Location = New Point(12, 127)
			Me.frmPosition.Name = "frmPosition"
			Me.frmPosition.Padding = New Padding(0)
			Me.frmPosition.RightToLeft = RightToLeft.No
			Me.frmPosition.Size = New Size(285, 58)
			Me.frmPosition.TabIndex = 43
			Me.frmPosition.TabStop = False
			Me.frmPosition.Text = "Position"
			Me.frmPosition.Visible = False
			Me.optUeberBlip.BackColor = SystemColors.Control
			Me.optUeberBlip.Cursor = Cursors.[Default]
			Me.optUeberBlip.ForeColor = SystemColors.ControlText
			Me.optUeberBlip.Location = New Point(160, 26)
			Me.optUeberBlip.Name = "optUeberBlip"
			Me.optUeberBlip.RightToLeft = RightToLeft.No
			Me.optUeberBlip.Size = New Size(109, 17)
			Me.optUeberBlip.TabIndex = 45
			Me.optUeberBlip.TabStop = True
			Me.optUeberBlip.Text = "above BLIP"
			Me.optUeberBlip.UseVisualStyleBackColor = False
			Me.optNebenBlip.BackColor = SystemColors.Control
			Me.optNebenBlip.Checked = True
			Me.optNebenBlip.Cursor = Cursors.[Default]
			Me.optNebenBlip.ForeColor = SystemColors.ControlText
			Me.optNebenBlip.Location = New Point(32, 26)
			Me.optNebenBlip.Name = "optNebenBlip"
			Me.optNebenBlip.RightToLeft = RightToLeft.No
			Me.optNebenBlip.Size = New Size(121, 17)
			Me.optNebenBlip.TabIndex = 44
			Me.optNebenBlip.TabStop = True
			Me.optNebenBlip.Text = "beside BLIP"
			Me.optNebenBlip.UseVisualStyleBackColor = False
			Me.Frame2.BackColor = SystemColors.Control
			Me.Frame2.Controls.Add(Me.cmbBlipLevel1)
			Me.Frame2.Controls.Add(Me.cmbBlipLevel2)
			Me.Frame2.Controls.Add(Me.cmbBlipLevel3)
			Me.Frame2.Controls.Add(Me._label__23)
			Me.Frame2.Controls.Add(Me._label__24)
			Me.Frame2.Controls.Add(Me._label__25)
			Me.Frame2.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.Frame2.ForeColor = SystemColors.ControlText
			Me.Frame2.Location = New Point(12, 64)
			Me.Frame2.Name = "Frame2"
			Me.Frame2.Padding = New Padding(0)
			Me.Frame2.RightToLeft = RightToLeft.No
			Me.Frame2.Size = New Size(318, 53)
			Me.Frame2.TabIndex = 36
			Me.Frame2.TabStop = False
			Me.Frame2.Text = "BLIP-Format"
			Me.cmbBlipLevel1.BackColor = SystemColors.Window
			Me.cmbBlipLevel1.Cursor = Cursors.[Default]
			Me.cmbBlipLevel1.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbBlipLevel1.ForeColor = SystemColors.WindowText
			Me.cmbBlipLevel1.Items.AddRange(New Object() { "small", "medium", "large" })
			Me.cmbBlipLevel1.Location = New Point(22, 22)
			Me.cmbBlipLevel1.Name = "cmbBlipLevel1"
			Me.cmbBlipLevel1.RightToLeft = RightToLeft.No
			Me.cmbBlipLevel1.Size = New Size(75, 24)
			Me.cmbBlipLevel1.TabIndex = 39
			Me.cmbBlipLevel2.BackColor = SystemColors.Window
			Me.cmbBlipLevel2.Cursor = Cursors.[Default]
			Me.cmbBlipLevel2.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbBlipLevel2.ForeColor = SystemColors.WindowText
			Me.cmbBlipLevel2.Items.AddRange(New Object() { "small", "medium", "large" })
			Me.cmbBlipLevel2.Location = New Point(126, 22)
			Me.cmbBlipLevel2.Name = "cmbBlipLevel2"
			Me.cmbBlipLevel2.RightToLeft = RightToLeft.No
			Me.cmbBlipLevel2.Size = New Size(75, 24)
			Me.cmbBlipLevel2.TabIndex = 38
			Me.cmbBlipLevel3.BackColor = SystemColors.Window
			Me.cmbBlipLevel3.Cursor = Cursors.[Default]
			Me.cmbBlipLevel3.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbBlipLevel3.ForeColor = SystemColors.WindowText
			Me.cmbBlipLevel3.Items.AddRange(New Object() { "small", "medium", "large" })
			Me.cmbBlipLevel3.Location = New Point(229, 22)
			Me.cmbBlipLevel3.Name = "cmbBlipLevel3"
			Me.cmbBlipLevel3.RightToLeft = RightToLeft.No
			Me.cmbBlipLevel3.Size = New Size(75, 24)
			Me.cmbBlipLevel3.TabIndex = 37
			Me._label__23.BackColor = SystemColors.Control
			Me._label__23.Cursor = Cursors.[Default]
			Me._label__23.ForeColor = SystemColors.ControlText
			Me._label__23.Location = New Point(11, 24)
			Me._label__23.Name = "_label__23"
			Me._label__23.RightToLeft = RightToLeft.No
			Me._label__23.Size = New Size(13, 17)
			Me._label__23.TabIndex = 42
			Me._label__23.Text = "I"
			Me._label__24.BackColor = SystemColors.Control
			Me._label__24.Cursor = Cursors.[Default]
			Me._label__24.ForeColor = SystemColors.ControlText
			Me._label__24.Location = New Point(112, 24)
			Me._label__24.Name = "_label__24"
			Me._label__24.RightToLeft = RightToLeft.No
			Me._label__24.Size = New Size(22, 17)
			Me._label__24.TabIndex = 41
			Me._label__24.Text = "II"
			Me._label__25.BackColor = SystemColors.Control
			Me._label__25.Cursor = Cursors.[Default]
			Me._label__25.ForeColor = SystemColors.ControlText
			Me._label__25.Location = New Point(213, 24)
			Me._label__25.Name = "_label__25"
			Me._label__25.RightToLeft = RightToLeft.No
			Me._label__25.Size = New Size(23, 17)
			Me._label__25.TabIndex = 40
			Me._label__25.Text = "III"
			Me.chkBlip.BackColor = SystemColors.Control
			Me.chkBlip.Cursor = Cursors.[Default]
			Me.chkBlip.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.chkBlip.ForeColor = SystemColors.ControlText
			Me.chkBlip.Location = New Point(23, 24)
			Me.chkBlip.Name = "chkBlip"
			Me.chkBlip.RightToLeft = RightToLeft.No
			Me.chkBlip.Size = New Size(126, 25)
			Me.chkBlip.TabIndex = 35
			Me.chkBlip.Text = "Use Page BLIP"
			Me.chkBlip.UseVisualStyleBackColor = False
			Me._tabSettings_TabPage2.Controls.Add(Me.frbFormat)
			Me._tabSettings_TabPage2.Controls.Add(Me.chkAnnotation)
			Me._tabSettings_TabPage2.Location = New Point(4, 34)
			Me._tabSettings_TabPage2.Name = "_tabSettings_TabPage2"
			Me._tabSettings_TabPage2.Size = New Size(913, 268)
			Me._tabSettings_TabPage2.TabIndex = 2
			Me._tabSettings_TabPage2.Text = "Annotation"
			Me.frbFormat.BackColor = SystemColors.Control
			Me.frbFormat.Controls.Add(Me.chkTwoLines)
			Me.frbFormat.Controls.Add(Me.chkSimDupFilenames)
			Me.frbFormat.Controls.Add(Me.txtAnnoBlipLen)
			Me.frbFormat.Controls.Add(Me.Label3)
			Me.frbFormat.Controls.Add(Me.optBlipAnno)
			Me.frbFormat.Controls.Add(Me.txtIgnoreCharsCount)
			Me.frbFormat.Controls.Add(Me.Label6)
			Me.frbFormat.Controls.Add(Me.chkIgnoreChars)
			Me.frbFormat.Controls.Add(Me.optDreiTeilig)
			Me.frbFormat.Controls.Add(Me.chkLateStart)
			Me.frbFormat.Controls.Add(Me.cmbPapierGroesse)
			Me.frbFormat.Controls.Add(Me.chkShowSize)
			Me.frbFormat.Controls.Add(Me.optNamen)
			Me.frbFormat.Controls.Add(Me.optNummer)
			Me.frbFormat.Controls.Add(Me.txtStart)
			Me.frbFormat.Controls.Add(Me.txtLen)
			Me.frbFormat.Controls.Add(Me.optMulti)
			Me.frbFormat.Controls.Add(Me.Label5)
			Me.frbFormat.Controls.Add(Me.Label4)
			Me.frbFormat.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.frbFormat.ForeColor = SystemColors.ControlText
			Me.frbFormat.Location = New Point(16, 59)
			Me.frbFormat.Name = "frbFormat"
			Me.frbFormat.Padding = New Padding(0)
			Me.frbFormat.RightToLeft = RightToLeft.No
			Me.frbFormat.Size = New Size(865, 197)
			Me.frbFormat.TabIndex = 48
			Me.frbFormat.TabStop = False
			Me.frbFormat.Text = "Annotation Format"
			Me.chkTwoLines.BackColor = SystemColors.Control
			Me.chkTwoLines.Cursor = Cursors.[Default]
			Me.chkTwoLines.ForeColor = SystemColors.ControlText
			Me.chkTwoLines.Location = New Point(447, 27)
			Me.chkTwoLines.Name = "chkTwoLines"
			Me.chkTwoLines.Size = New Size(259, 21)
			Me.chkTwoLines.TabIndex = 330
			Me.chkTwoLines.Text = "Two Line Text Annotation"
			Me.chkTwoLines.UseVisualStyleBackColor = False
			Me.chkSimDupFilenames.BackColor = SystemColors.Control
			Me.chkSimDupFilenames.Cursor = Cursors.[Default]
			Me.chkSimDupFilenames.ForeColor = SystemColors.ControlText
			Me.chkSimDupFilenames.Location = New Point(237, 26)
			Me.chkSimDupFilenames.Name = "chkSimDupFilenames"
			Me.chkSimDupFilenames.RightToLeft = RightToLeft.No
			Me.chkSimDupFilenames.Size = New Size(215, 21)
			Me.chkSimDupFilenames.TabIndex = 329
			Me.chkSimDupFilenames.Text = "Simplex + Duplex Filenames"
			Me.chkSimDupFilenames.UseVisualStyleBackColor = False
			Me.Label3.BackColor = SystemColors.Control
			Me.Label3.Cursor = Cursors.[Default]
			Me.Label3.ForeColor = SystemColors.ControlText
			Me.Label3.Location = New Point(435, 100)
			Me.Label3.Name = "Label3"
			Me.Label3.Size = New Size(54, 17)
			Me.Label3.TabIndex = 328
			Me.Label3.Text = "Length"
			Me.Label3.TextAlign = ContentAlignment.MiddleRight
			Me.optBlipAnno.BackColor = SystemColors.Control
			Me.optBlipAnno.Cursor = Cursors.[Default]
			Me.optBlipAnno.ForeColor = SystemColors.ControlText
			Me.optBlipAnno.Location = New Point(234, 100)
			Me.optBlipAnno.Name = "optBlipAnno"
			Me.optBlipAnno.RightToLeft = RightToLeft.No
			Me.optBlipAnno.Size = New Size(105, 22)
			Me.optBlipAnno.TabIndex = 326
			Me.optBlipAnno.TabStop = True
			Me.optBlipAnno.Text = "Blip-Index"
			Me.optBlipAnno.UseVisualStyleBackColor = False
			Me.Label6.BackColor = SystemColors.Control
			Me.Label6.Cursor = Cursors.[Default]
			Me.Label6.ForeColor = SystemColors.ControlText
			Me.Label6.Location = New Point(627, 168)
			Me.Label6.Name = "Label6"
			Me.Label6.Size = New Size(54, 17)
			Me.Label6.TabIndex = 325
			Me.Label6.Text = "Count"
			Me.Label6.TextAlign = ContentAlignment.MiddleRight
			Me.Label6.Visible = False
			Me.chkIgnoreChars.BackColor = SystemColors.Control
			Me.chkIgnoreChars.Cursor = Cursors.[Default]
			Me.chkIgnoreChars.ForeColor = SystemColors.ControlText
			Me.chkIgnoreChars.Location = New Point(631, 123)
			Me.chkIgnoreChars.Name = "chkIgnoreChars"
			Me.chkIgnoreChars.RightToLeft = RightToLeft.No
			Me.chkIgnoreChars.Size = New Size(177, 37)
			Me.chkIgnoreChars.TabIndex = 323
			Me.chkIgnoreChars.Text = "Ignore leading characters in filenames"
			Me.chkIgnoreChars.UseVisualStyleBackColor = False
			Me.chkIgnoreChars.Visible = False
			Me.optDreiTeilig.BackColor = SystemColors.Control
			Me.optDreiTeilig.Cursor = Cursors.[Default]
			Me.optDreiTeilig.ForeColor = SystemColors.ControlText
			Me.optDreiTeilig.Location = New Point(15, 100)
			Me.optDreiTeilig.Name = "optDreiTeilig"
			Me.optDreiTeilig.RightToLeft = RightToLeft.No
			Me.optDreiTeilig.Size = New Size(152, 22)
			Me.optDreiTeilig.TabIndex = 322
			Me.optDreiTeilig.TabStop = True
			Me.optDreiTeilig.Text = "Nr  |  Factor  |  Name"
			Me.optDreiTeilig.UseVisualStyleBackColor = False
			Me.chkLateStart.BackColor = SystemColors.Control
			Me.chkLateStart.Cursor = Cursors.[Default]
			Me.chkLateStart.ForeColor = SystemColors.ControlText
			Me.chkLateStart.Location = New Point(16, 171)
			Me.chkLateStart.Name = "chkLateStart"
			Me.chkLateStart.RightToLeft = RightToLeft.No
			Me.chkLateStart.Size = New Size(261, 21)
			Me.chkLateStart.TabIndex = 320
			Me.chkLateStart.Text = "Don't count Start Symbols"
			Me.chkLateStart.UseVisualStyleBackColor = False
			Me.cmbPapierGroesse.BackColor = SystemColors.Window
			Me.cmbPapierGroesse.Cursor = Cursors.[Default]
			Me.cmbPapierGroesse.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbPapierGroesse.Enabled = False
			Me.cmbPapierGroesse.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmbPapierGroesse.ForeColor = SystemColors.WindowText
			Me.cmbPapierGroesse.Items.AddRange(New Object() { "(mm x mm)", "("" x "")", "(cm x cm)" })
			Me.cmbPapierGroesse.Location = New Point(323, 140)
			Me.cmbPapierGroesse.Name = "cmbPapierGroesse"
			Me.cmbPapierGroesse.RightToLeft = RightToLeft.No
			Me.cmbPapierGroesse.Size = New Size(105, 23)
			Me.cmbPapierGroesse.TabIndex = 196
			Me.chkShowSize.BackColor = SystemColors.Control
			Me.chkShowSize.Cursor = Cursors.[Default]
			Me.chkShowSize.ForeColor = SystemColors.ControlText
			Me.chkShowSize.Location = New Point(16, 139)
			Me.chkShowSize.Name = "chkShowSize"
			Me.chkShowSize.RightToLeft = RightToLeft.No
			Me.chkShowSize.Size = New Size(364, 21)
			Me.chkShowSize.TabIndex = 66
			Me.chkShowSize.Text = "Use the Paper Size (in mm) as Annotation"
			Me.chkShowSize.UseVisualStyleBackColor = False
			Me.optNamen.BackColor = SystemColors.Control
			Me.optNamen.Cursor = Cursors.[Default]
			Me.optNamen.ForeColor = SystemColors.ControlText
			Me.optNamen.Location = New Point(15, 26)
			Me.optNamen.Name = "optNamen"
			Me.optNamen.RightToLeft = RightToLeft.No
			Me.optNamen.Size = New Size(112, 22)
			Me.optNamen.TabIndex = 55
			Me.optNamen.TabStop = True
			Me.optNamen.Text = "File Names"
			Me.optNamen.UseVisualStyleBackColor = False
			Me.optNummer.BackColor = SystemColors.Control
			Me.optNummer.Cursor = Cursors.[Default]
			Me.optNummer.ForeColor = SystemColors.ControlText
			Me.optNummer.Location = New Point(15, 63)
			Me.optNummer.Name = "optNummer"
			Me.optNummer.RightToLeft = RightToLeft.No
			Me.optNummer.Size = New Size(220, 22)
			Me.optNummer.TabIndex = 54
			Me.optNummer.TabStop = True
			Me.optNummer.Text = "Numbers"
			Me.optNummer.UseVisualStyleBackColor = False
			Me.txtStart.AcceptsReturn = True
			Me.txtStart.BackColor = SystemColors.Window
			Me.txtStart.Cursor = Cursors.IBeam
			Me.txtStart.Enabled = False
			Me.txtStart.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold)
			Me.txtStart.ForeColor = SystemColors.WindowText
			Me.txtStart.Location = New Point(278, 64)
			Me.txtStart.MaxLength = 0
			Me.txtStart.Name = "txtStart"
			Me.txtStart.RightToLeft = RightToLeft.No
			Me.txtStart.Size = New Size(73, 22)
			Me.txtStart.TabIndex = 52
			Me.txtStart.TextAlign = HorizontalAlignment.Right
			Me.optMulti.BackColor = SystemColors.Control
			Me.optMulti.Cursor = Cursors.[Default]
			Me.optMulti.Enabled = False
			Me.optMulti.ForeColor = SystemColors.ControlText
			Me.optMulti.Location = New Point(480, 117)
			Me.optMulti.Name = "optMulti"
			Me.optMulti.RightToLeft = RightToLeft.No
			Me.optMulti.Size = New Size(159, 33)
			Me.optMulti.TabIndex = 48
			Me.optMulti.TabStop = True
			Me.optMulti.Text = "Multi-Level Annotation"
			Me.optMulti.UseVisualStyleBackColor = False
			Me.optMulti.Visible = False
			Me.Label5.BackColor = SystemColors.Control
			Me.Label5.Cursor = Cursors.[Default]
			Me.Label5.Enabled = False
			Me.Label5.ForeColor = SystemColors.ControlText
			Me.Label5.Location = New Point(213, 64)
			Me.Label5.Name = "Label5"
			Me.Label5.RightToLeft = RightToLeft.No
			Me.Label5.Size = New Size(51, 17)
			Me.Label5.TabIndex = 59
			Me.Label5.Text = "Start"
			Me.Label5.TextAlign = ContentAlignment.MiddleRight
			Me.Label4.BackColor = SystemColors.Control
			Me.Label4.Cursor = Cursors.[Default]
			Me.Label4.ForeColor = SystemColors.ControlText
			Me.Label4.Location = New Point(435, 63)
			Me.Label4.Name = "Label4"
			Me.Label4.RightToLeft = RightToLeft.No
			Me.Label4.Size = New Size(54, 17)
			Me.Label4.TabIndex = 58
			Me.Label4.Text = "Length"
			Me.Label4.TextAlign = ContentAlignment.MiddleRight
			Me.chkAnnotation.BackColor = SystemColors.Control
			Me.chkAnnotation.Cursor = Cursors.[Default]
			Me.chkAnnotation.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.chkAnnotation.ForeColor = SystemColors.ControlText
			Me.chkAnnotation.Location = New Point(17, 22)
			Me.chkAnnotation.Name = "chkAnnotation"
			Me.chkAnnotation.RightToLeft = RightToLeft.No
			Me.chkAnnotation.Size = New Size(198, 21)
			Me.chkAnnotation.TabIndex = 46
			Me.chkAnnotation.Text = "Use Annoations"
			Me.chkAnnotation.UseVisualStyleBackColor = False
			Me._tabSettings_TabPage3.Controls.Add(Me.tabFrames)
			Me._tabSettings_TabPage3.Location = New Point(4, 34)
			Me._tabSettings_TabPage3.Name = "_tabSettings_TabPage3"
			Me._tabSettings_TabPage3.Size = New Size(913, 268)
			Me._tabSettings_TabPage3.TabIndex = 3
			Me._tabSettings_TabPage3.Text = "Info-Frames"
			Me.tabFrames.Controls.Add(Me._tabFrames_TabPage0)
			Me.tabFrames.Controls.Add(Me._tabFrames_TabPage1)
			Me.tabFrames.Controls.Add(Me._tabFrames_TabPage2)
			Me.tabFrames.Controls.Add(Me._tabFrames_TabPage3)
			Me.tabFrames.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.tabFrames.ItemSize = New Size(42, 20)
			Me.tabFrames.Location = New Point(8, 11)
			Me.tabFrames.Name = "tabFrames"
			Me.tabFrames.SelectedIndex = 0
			Me.tabFrames.Size = New Size(864, 242)
			Me.tabFrames.TabIndex = 62
			Me._tabFrames_TabPage0.Controls.Add(Me.Button1)
			Me._tabFrames_TabPage0.Controls.Add(Me.lblPfadStartSymbole)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label75)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label76)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label77)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label78)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label29)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label31)
			Me._tabFrames_TabPage0.Controls.Add(Me.Label9)
			Me._tabFrames_TabPage0.Controls.Add(Me.chkStartFrame)
			Me._tabFrames_TabPage0.Controls.Add(Me.chkZusatzStartSymbole)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtRollNoSize)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtRollNoPrefix)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtRollNoPostfix)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtRollNoLen)
			Me._tabFrames_TabPage0.Controls.Add(Me.chkAddRollFrame)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtAddRollFrameSize)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtAddRollFrameLen)
			Me._tabFrames_TabPage0.Controls.Add(Me.chkAddRollFrameInput)
			Me._tabFrames_TabPage0.Controls.Add(Me.Frame12)
			Me._tabFrames_TabPage0.Controls.Add(Me.txtAddRollStartFrameSteps)
			Me._tabFrames_TabPage0.Location = New Point(4, 24)
			Me._tabFrames_TabPage0.Name = "_tabFrames_TabPage0"
			Me._tabFrames_TabPage0.Size = New Size(856, 214)
			Me._tabFrames_TabPage0.TabIndex = 0
			Me._tabFrames_TabPage0.Text = "Roll Start"
			Me.Button1.Location = New Point(516, 133)
			Me.Button1.Name = "Button1"
			Me.Button1.Size = New Size(42, 30)
			Me.Button1.TabIndex = 315
			Me.Button1.Text = "..."
			Me.Button1.UseVisualStyleBackColor = True
			Me.lblPfadStartSymbole.BackColor = SystemColors.Control
			Me.lblPfadStartSymbole.BorderStyle = BorderStyle.Fixed3D
			Me.lblPfadStartSymbole.Cursor = Cursors.[Default]
			Me.lblPfadStartSymbole.Font = New Font("Microsoft Sans Serif", 8.25F)
			Me.lblPfadStartSymbole.ForeColor = SystemColors.ControlText
			Me.lblPfadStartSymbole.Location = New Point(24, 135)
			Me.lblPfadStartSymbole.Name = "lblPfadStartSymbole"
			Me.lblPfadStartSymbole.RightToLeft = RightToLeft.No
			Me.lblPfadStartSymbole.Size = New Size(486, 25)
			Me.lblPfadStartSymbole.TabIndex = 205
			Me.Label75.BackColor = SystemColors.Control
			Me.Label75.Cursor = Cursors.[Default]
			Me.Label75.ForeColor = SystemColors.ControlText
			Me.Label75.Location = New Point(139, 22)
			Me.Label75.Name = "Label75"
			Me.Label75.RightToLeft = RightToLeft.No
			Me.Label75.Size = New Size(93, 17)
			Me.Label75.TabIndex = 243
			Me.Label75.Text = "Font Size"
			Me.Label75.TextAlign = ContentAlignment.MiddleRight
			Me.Label76.BackColor = SystemColors.Control
			Me.Label76.Cursor = Cursors.[Default]
			Me.Label76.ForeColor = SystemColors.ControlText
			Me.Label76.Location = New Point(414, 22)
			Me.Label76.Name = "Label76"
			Me.Label76.RightToLeft = RightToLeft.No
			Me.Label76.Size = New Size(57, 17)
			Me.Label76.TabIndex = 248
			Me.Label76.Text = "Prefix"
			Me.Label76.TextAlign = ContentAlignment.MiddleRight
			Me.Label77.BackColor = SystemColors.Control
			Me.Label77.Cursor = Cursors.[Default]
			Me.Label77.ForeColor = SystemColors.ControlText
			Me.Label77.Location = New Point(558, 22)
			Me.Label77.Name = "Label77"
			Me.Label77.RightToLeft = RightToLeft.No
			Me.Label77.Size = New Size(58, 17)
			Me.Label77.TabIndex = 250
			Me.Label77.Text = "Postfix"
			Me.Label77.TextAlign = ContentAlignment.MiddleRight
			Me.Label78.BackColor = SystemColors.Control
			Me.Label78.Cursor = Cursors.[Default]
			Me.Label78.ForeColor = SystemColors.ControlText
			Me.Label78.Location = New Point(297, 22)
			Me.Label78.Name = "Label78"
			Me.Label78.RightToLeft = RightToLeft.No
			Me.Label78.Size = New Size(49, 17)
			Me.Label78.TabIndex = 252
			Me.Label78.Text = "Length"
			Me.Label78.TextAlign = ContentAlignment.MiddleRight
			Me.Label29.BackColor = SystemColors.Control
			Me.Label29.Cursor = Cursors.[Default]
			Me.Label29.ForeColor = SystemColors.ControlText
			Me.Label29.Location = New Point(295, 72)
			Me.Label29.Name = "Label29"
			Me.Label29.RightToLeft = RightToLeft.No
			Me.Label29.Size = New Size(49, 17)
			Me.Label29.TabIndex = 270
			Me.Label29.Text = "Size"
			Me.Label29.TextAlign = ContentAlignment.MiddleRight
			Me.Label31.BackColor = SystemColors.Control
			Me.Label31.Cursor = Cursors.[Default]
			Me.Label31.ForeColor = SystemColors.ControlText
			Me.Label31.Location = New Point(141, 72)
			Me.Label31.Name = "Label31"
			Me.Label31.RightToLeft = RightToLeft.No
			Me.Label31.Size = New Size(84, 17)
			Me.Label31.TabIndex = 272
			Me.Label31.Text = "max. Length"
			Me.Label31.TextAlign = ContentAlignment.MiddleRight
			Me.Label9.BackColor = SystemColors.Control
			Me.Label9.Cursor = Cursors.[Default]
			Me.Label9.ForeColor = SystemColors.ControlText
			Me.Label9.Location = New Point(8, 174)
			Me.Label9.Name = "Label9"
			Me.Label9.RightToLeft = RightToLeft.No
			Me.Label9.Size = New Size(133, 22)
			Me.Label9.TabIndex = 314
			Me.Label9.Text = "add Motor Steps"
			Me.Label9.TextAlign = ContentAlignment.MiddleRight
			Me.chkStartFrame.BackColor = SystemColors.Control
			Me.chkStartFrame.Cursor = Cursors.[Default]
			Me.chkStartFrame.ForeColor = SystemColors.ControlText
			Me.chkStartFrame.Location = New Point(24, 22)
			Me.chkStartFrame.Name = "chkStartFrame"
			Me.chkStartFrame.RightToLeft = RightToLeft.No
			Me.chkStartFrame.Size = New Size(145, 17)
			Me.chkStartFrame.TabIndex = 63
			Me.chkStartFrame.Text = "Roll Start Frame"
			Me.chkStartFrame.UseVisualStyleBackColor = False
			Me.chkZusatzStartSymbole.BackColor = SystemColors.Control
			Me.chkZusatzStartSymbole.Cursor = Cursors.[Default]
			Me.chkZusatzStartSymbole.ForeColor = SystemColors.ControlText
			Me.chkZusatzStartSymbole.Location = New Point(24, 112)
			Me.chkZusatzStartSymbole.Name = "chkZusatzStartSymbole"
			Me.chkZusatzStartSymbole.RightToLeft = RightToLeft.No
			Me.chkZusatzStartSymbole.Size = New Size(201, 20)
			Me.chkZusatzStartSymbole.TabIndex = 204
			Me.chkZusatzStartSymbole.Text = "add Roll Start Symbols"
			Me.chkZusatzStartSymbole.UseVisualStyleBackColor = False
			Me.txtRollNoSize.AcceptsReturn = True
			Me.txtRollNoSize.BackColor = SystemColors.Window
			Me.txtRollNoSize.Cursor = Cursors.IBeam
			Me.txtRollNoSize.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtRollNoSize.ForeColor = SystemColors.WindowText
			Me.txtRollNoSize.Location = New Point(238, 20)
			Me.txtRollNoSize.MaxLength = 0
			Me.txtRollNoSize.Name = "txtRollNoSize"
			Me.txtRollNoSize.RightToLeft = RightToLeft.No
			Me.txtRollNoSize.Size = New Size(41, 22)
			Me.txtRollNoSize.TabIndex = 244
			Me.txtRollNoPrefix.AcceptsReturn = True
			Me.txtRollNoPrefix.BackColor = SystemColors.Window
			Me.txtRollNoPrefix.Cursor = Cursors.IBeam
			Me.txtRollNoPrefix.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtRollNoPrefix.ForeColor = SystemColors.WindowText
			Me.txtRollNoPrefix.Location = New Point(484, 20)
			Me.txtRollNoPrefix.MaxLength = 0
			Me.txtRollNoPrefix.Name = "txtRollNoPrefix"
			Me.txtRollNoPrefix.RightToLeft = RightToLeft.No
			Me.txtRollNoPrefix.Size = New Size(61, 22)
			Me.txtRollNoPrefix.TabIndex = 247
			Me.txtRollNoPostfix.AcceptsReturn = True
			Me.txtRollNoPostfix.BackColor = SystemColors.Window
			Me.txtRollNoPostfix.Cursor = Cursors.IBeam
			Me.txtRollNoPostfix.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtRollNoPostfix.ForeColor = SystemColors.WindowText
			Me.txtRollNoPostfix.Location = New Point(624, 20)
			Me.txtRollNoPostfix.MaxLength = 0
			Me.txtRollNoPostfix.Name = "txtRollNoPostfix"
			Me.txtRollNoPostfix.RightToLeft = RightToLeft.No
			Me.txtRollNoPostfix.Size = New Size(61, 22)
			Me.txtRollNoPostfix.TabIndex = 249
			Me.txtRollNoLen.AcceptsReturn = True
			Me.txtRollNoLen.BackColor = SystemColors.Window
			Me.txtRollNoLen.Cursor = Cursors.IBeam
			Me.txtRollNoLen.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtRollNoLen.ForeColor = SystemColors.WindowText
			Me.txtRollNoLen.Location = New Point(359, 20)
			Me.txtRollNoLen.MaxLength = 0
			Me.txtRollNoLen.Name = "txtRollNoLen"
			Me.txtRollNoLen.RightToLeft = RightToLeft.No
			Me.txtRollNoLen.Size = New Size(41, 22)
			Me.txtRollNoLen.TabIndex = 251
			Me.chkAddRollFrame.BackColor = SystemColors.Control
			Me.chkAddRollFrame.Cursor = Cursors.[Default]
			Me.chkAddRollFrame.ForeColor = SystemColors.ControlText
			Me.chkAddRollFrame.Location = New Point(24, 68)
			Me.chkAddRollFrame.Name = "chkAddRollFrame"
			Me.chkAddRollFrame.RightToLeft = RightToLeft.No
			Me.chkAddRollFrame.Size = New Size(97, 17)
			Me.chkAddRollFrame.TabIndex = 268
			Me.chkAddRollFrame.Text = "man. Index"
			Me.chkAddRollFrame.UseVisualStyleBackColor = False
			Me.txtAddRollFrameSize.AcceptsReturn = True
			Me.txtAddRollFrameSize.BackColor = SystemColors.Window
			Me.txtAddRollFrameSize.Cursor = Cursors.IBeam
			Me.txtAddRollFrameSize.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAddRollFrameSize.ForeColor = SystemColors.WindowText
			Me.txtAddRollFrameSize.Location = New Point(359, 69)
			Me.txtAddRollFrameSize.MaxLength = 0
			Me.txtAddRollFrameSize.Name = "txtAddRollFrameSize"
			Me.txtAddRollFrameSize.RightToLeft = RightToLeft.No
			Me.txtAddRollFrameSize.Size = New Size(41, 22)
			Me.txtAddRollFrameSize.TabIndex = 269
			Me.txtAddRollFrameLen.AcceptsReturn = True
			Me.txtAddRollFrameLen.BackColor = SystemColors.Window
			Me.txtAddRollFrameLen.Cursor = Cursors.IBeam
			Me.txtAddRollFrameLen.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAddRollFrameLen.ForeColor = SystemColors.WindowText
			Me.txtAddRollFrameLen.Location = New Point(238, 69)
			Me.txtAddRollFrameLen.MaxLength = 0
			Me.txtAddRollFrameLen.Name = "txtAddRollFrameLen"
			Me.txtAddRollFrameLen.RightToLeft = RightToLeft.No
			Me.txtAddRollFrameLen.Size = New Size(41, 22)
			Me.txtAddRollFrameLen.TabIndex = 271
			Me.chkAddRollFrameInput.BackColor = SystemColors.Control
			Me.chkAddRollFrameInput.Cursor = Cursors.[Default]
			Me.chkAddRollFrameInput.ForeColor = SystemColors.ControlText
			Me.chkAddRollFrameInput.Location = New Point(432, 74)
			Me.chkAddRollFrameInput.Name = "chkAddRollFrameInput"
			Me.chkAddRollFrameInput.RightToLeft = RightToLeft.No
			Me.chkAddRollFrameInput.Size = New Size(127, 20)
			Me.chkAddRollFrameInput.TabIndex = 273
			Me.chkAddRollFrameInput.Text = "Show last Input"
			Me.chkAddRollFrameInput.UseVisualStyleBackColor = False
			Me.Frame12.BackColor = SystemColors.Control
			Me.Frame12.Controls.Add(Me._txtAddRollInfoPos_4)
			Me.Frame12.Controls.Add(Me._txtAddRollInfoPos_3)
			Me.Frame12.Controls.Add(Me._txtAddRollInfoPos_2)
			Me.Frame12.Controls.Add(Me._txtAddRollInfoPos_1)
			Me.Frame12.ForeColor = SystemColors.ControlText
			Me.Frame12.Location = New Point(597, 58)
			Me.Frame12.Name = "Frame12"
			Me.Frame12.Padding = New Padding(0)
			Me.Frame12.RightToLeft = RightToLeft.No
			Me.Frame12.Size = New Size(117, 126)
			Me.Frame12.TabIndex = 274
			Me.Frame12.TabStop = False
			Me.Frame12.Text = "Positions Index"
			Me._txtAddRollInfoPos_4.AcceptsReturn = True
			Me._txtAddRollInfoPos_4.BackColor = SystemColors.Window
			Me._txtAddRollInfoPos_4.Cursor = Cursors.IBeam
			Me._txtAddRollInfoPos_4.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtAddRollInfoPos_4.ForeColor = SystemColors.WindowText
			Me._txtAddRollInfoPos_4.Location = New Point(26, 100)
			Me._txtAddRollInfoPos_4.MaxLength = 0
			Me._txtAddRollInfoPos_4.Name = "_txtAddRollInfoPos_4"
			Me._txtAddRollInfoPos_4.RightToLeft = RightToLeft.No
			Me._txtAddRollInfoPos_4.Size = New Size(61, 22)
			Me._txtAddRollInfoPos_4.TabIndex = 278
			Me._txtAddRollInfoPos_3.AcceptsReturn = True
			Me._txtAddRollInfoPos_3.BackColor = SystemColors.Window
			Me._txtAddRollInfoPos_3.Cursor = Cursors.IBeam
			Me._txtAddRollInfoPos_3.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtAddRollInfoPos_3.ForeColor = SystemColors.WindowText
			Me._txtAddRollInfoPos_3.Location = New Point(26, 72)
			Me._txtAddRollInfoPos_3.MaxLength = 0
			Me._txtAddRollInfoPos_3.Name = "_txtAddRollInfoPos_3"
			Me._txtAddRollInfoPos_3.RightToLeft = RightToLeft.No
			Me._txtAddRollInfoPos_3.Size = New Size(61, 22)
			Me._txtAddRollInfoPos_3.TabIndex = 277
			Me._txtAddRollInfoPos_2.AcceptsReturn = True
			Me._txtAddRollInfoPos_2.BackColor = SystemColors.Window
			Me._txtAddRollInfoPos_2.Cursor = Cursors.IBeam
			Me._txtAddRollInfoPos_2.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtAddRollInfoPos_2.ForeColor = SystemColors.WindowText
			Me._txtAddRollInfoPos_2.Location = New Point(26, 44)
			Me._txtAddRollInfoPos_2.MaxLength = 0
			Me._txtAddRollInfoPos_2.Name = "_txtAddRollInfoPos_2"
			Me._txtAddRollInfoPos_2.RightToLeft = RightToLeft.No
			Me._txtAddRollInfoPos_2.Size = New Size(61, 22)
			Me._txtAddRollInfoPos_2.TabIndex = 276
			Me._txtAddRollInfoPos_1.AcceptsReturn = True
			Me._txtAddRollInfoPos_1.BackColor = SystemColors.Window
			Me._txtAddRollInfoPos_1.Cursor = Cursors.IBeam
			Me._txtAddRollInfoPos_1.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtAddRollInfoPos_1.ForeColor = SystemColors.WindowText
			Me._txtAddRollInfoPos_1.Location = New Point(26, 18)
			Me._txtAddRollInfoPos_1.MaxLength = 0
			Me._txtAddRollInfoPos_1.Name = "_txtAddRollInfoPos_1"
			Me._txtAddRollInfoPos_1.RightToLeft = RightToLeft.No
			Me._txtAddRollInfoPos_1.Size = New Size(61, 22)
			Me._txtAddRollInfoPos_1.TabIndex = 275
			Me.txtAddRollStartFrameSteps.AcceptsReturn = True
			Me.txtAddRollStartFrameSteps.BackColor = SystemColors.Window
			Me.txtAddRollStartFrameSteps.Cursor = Cursors.IBeam
			Me.txtAddRollStartFrameSteps.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAddRollStartFrameSteps.ForeColor = SystemColors.WindowText
			Me.txtAddRollStartFrameSteps.Location = New Point(147, 174)
			Me.txtAddRollStartFrameSteps.MaxLength = 0
			Me.txtAddRollStartFrameSteps.Name = "txtAddRollStartFrameSteps"
			Me.txtAddRollStartFrameSteps.RightToLeft = RightToLeft.No
			Me.txtAddRollStartFrameSteps.Size = New Size(61, 22)
			Me.txtAddRollStartFrameSteps.TabIndex = 313
			Me.txtAddRollStartFrameSteps.TextAlign = HorizontalAlignment.Right
			Me._tabFrames_TabPage1.Controls.Add(Me.chkSeparateFrame)
			Me._tabFrames_TabPage1.Controls.Add(Me.chkUseFrameNo)
			Me._tabFrames_TabPage1.Location = New Point(4, 24)
			Me._tabFrames_TabPage1.Name = "_tabFrames_TabPage1"
			Me._tabFrames_TabPage1.Size = New Size(856, 214)
			Me._tabFrames_TabPage1.TabIndex = 1
			Me._tabFrames_TabPage1.Text = "Separator Frame"
			Me.chkSeparateFrame.BackColor = SystemColors.Control
			Me.chkSeparateFrame.Cursor = Cursors.[Default]
			Me.chkSeparateFrame.ForeColor = SystemColors.ControlText
			Me.chkSeparateFrame.Location = New Point(24, 47)
			Me.chkSeparateFrame.Name = "chkSeparateFrame"
			Me.chkSeparateFrame.RightToLeft = RightToLeft.No
			Me.chkSeparateFrame.Size = New Size(128, 21)
			Me.chkSeparateFrame.TabIndex = 65
			Me.chkSeparateFrame.Text = "Separator Frame"
			Me.chkSeparateFrame.UseVisualStyleBackColor = False
			Me.chkUseFrameNo.BackColor = SystemColors.Control
			Me.chkUseFrameNo.Cursor = Cursors.[Default]
			Me.chkUseFrameNo.ForeColor = SystemColors.ControlText
			Me.chkUseFrameNo.Location = New Point(24, 84)
			Me.chkUseFrameNo.Name = "chkUseFrameNo"
			Me.chkUseFrameNo.RightToLeft = RightToLeft.No
			Me.chkUseFrameNo.Size = New Size(197, 27)
			Me.chkUseFrameNo.TabIndex = 64
			Me.chkUseFrameNo.Text = "Expose Frame No."
			Me.chkUseFrameNo.UseVisualStyleBackColor = False
			Me._tabFrames_TabPage2.Controls.Add(Me.Button3)
			Me._tabFrames_TabPage2.Controls.Add(Me.Button2)
			Me._tabFrames_TabPage2.Controls.Add(Me.cmbFortsetzungsLevel)
			Me._tabFrames_TabPage2.Controls.Add(Me.chkNoSpecialSmybolesWhenContinuation)
			Me._tabFrames_TabPage2.Controls.Add(Me.txtFramesWiederholen)
			Me._tabFrames_TabPage2.Controls.Add(Me.chkFramesWiederholen)
			Me._tabFrames_TabPage2.Controls.Add(Me.chkRolleistFortsetzung)
			Me._tabFrames_TabPage2.Controls.Add(Me.chkRollewirdfortgesetzt)
			Me._tabFrames_TabPage2.Controls.Add(Me.chkBaende)
			Me._tabFrames_TabPage2.Controls.Add(Me._label__6)
			Me._tabFrames_TabPage2.Controls.Add(Me.lblPfadFortsetzungsSymbole2)
			Me._tabFrames_TabPage2.Controls.Add(Me.lblPfadFortsetzungsSymbole1)
			Me._tabFrames_TabPage2.Location = New Point(4, 24)
			Me._tabFrames_TabPage2.Name = "_tabFrames_TabPage2"
			Me._tabFrames_TabPage2.Size = New Size(856, 214)
			Me._tabFrames_TabPage2.TabIndex = 2
			Me._tabFrames_TabPage2.Text = "Continuation Rolls"
			Me.Button3.Location = New Point(657, 83)
			Me.Button3.Name = "Button3"
			Me.Button3.Size = New Size(42, 30)
			Me.Button3.TabIndex = 317
			Me.Button3.Text = "..."
			Me.Button3.UseVisualStyleBackColor = True
			Me.Button2.Location = New Point(657, 45)
			Me.Button2.Name = "Button2"
			Me.Button2.Size = New Size(42, 30)
			Me.Button2.TabIndex = 316
			Me.Button2.Text = "..."
			Me.Button2.UseVisualStyleBackColor = True
			Me.cmbFortsetzungsLevel.BackColor = SystemColors.Window
			Me.cmbFortsetzungsLevel.Cursor = Cursors.[Default]
			Me.cmbFortsetzungsLevel.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbFortsetzungsLevel.ForeColor = SystemColors.WindowText
			Me.cmbFortsetzungsLevel.Items.AddRange(New Object() { "Level 1", "Level 2", "Level 3" })
			Me.cmbFortsetzungsLevel.Location = New Point(487, 126)
			Me.cmbFortsetzungsLevel.Name = "cmbFortsetzungsLevel"
			Me.cmbFortsetzungsLevel.RightToLeft = RightToLeft.No
			Me.cmbFortsetzungsLevel.Size = New Size(120, 24)
			Me.cmbFortsetzungsLevel.TabIndex = 260
			Me.chkNoSpecialSmybolesWhenContinuation.BackColor = SystemColors.Control
			Me.chkNoSpecialSmybolesWhenContinuation.Cursor = Cursors.[Default]
			Me.chkNoSpecialSmybolesWhenContinuation.ForeColor = SystemColors.ControlText
			Me.chkNoSpecialSmybolesWhenContinuation.Location = New Point(16, 166)
			Me.chkNoSpecialSmybolesWhenContinuation.Name = "chkNoSpecialSmybolesWhenContinuation"
			Me.chkNoSpecialSmybolesWhenContinuation.RightToLeft = RightToLeft.No
			Me.chkNoSpecialSmybolesWhenContinuation.Size = New Size(400, 24)
			Me.chkNoSpecialSmybolesWhenContinuation.TabIndex = 253
			Me.chkNoSpecialSmybolesWhenContinuation.Text = "Continuation symbols replace roll start and end frames"
			Me.chkNoSpecialSmybolesWhenContinuation.UseVisualStyleBackColor = False
			Me.txtFramesWiederholen.AcceptsReturn = True
			Me.txtFramesWiederholen.BackColor = SystemColors.Window
			Me.txtFramesWiederholen.Cursor = Cursors.IBeam
			Me.txtFramesWiederholen.ForeColor = SystemColors.WindowText
			Me.txtFramesWiederholen.Location = New Point(255, 124)
			Me.txtFramesWiederholen.MaxLength = 0
			Me.txtFramesWiederholen.Name = "txtFramesWiederholen"
			Me.txtFramesWiederholen.RightToLeft = RightToLeft.No
			Me.txtFramesWiederholen.Size = New Size(41, 22)
			Me.txtFramesWiederholen.TabIndex = 246
			Me.txtFramesWiederholen.TextAlign = HorizontalAlignment.Right
			Me.chkFramesWiederholen.BackColor = SystemColors.Control
			Me.chkFramesWiederholen.Cursor = Cursors.[Default]
			Me.chkFramesWiederholen.ForeColor = SystemColors.ControlText
			Me.chkFramesWiederholen.Location = New Point(16, 128)
			Me.chkFramesWiederholen.Name = "chkFramesWiederholen"
			Me.chkFramesWiederholen.RightToLeft = RightToLeft.No
			Me.chkFramesWiederholen.Size = New Size(206, 22)
			Me.chkFramesWiederholen.TabIndex = 245
			Me.chkFramesWiederholen.Text = "# of frames to be repeated"
			Me.chkFramesWiederholen.UseVisualStyleBackColor = False
			Me.chkRolleistFortsetzung.BackColor = SystemColors.Control
			Me.chkRolleistFortsetzung.Cursor = Cursors.[Default]
			Me.chkRolleistFortsetzung.ForeColor = SystemColors.ControlText
			Me.chkRolleistFortsetzung.Location = New Point(16, 89)
			Me.chkRolleistFortsetzung.Name = "chkRolleistFortsetzung"
			Me.chkRolleistFortsetzung.RightToLeft = RightToLeft.No
			Me.chkRolleistFortsetzung.Size = New Size(233, 24)
			Me.chkRolleistFortsetzung.TabIndex = 217
			Me.chkRolleistFortsetzung.Text = "Roll is a continuation"
			Me.chkRolleistFortsetzung.UseVisualStyleBackColor = False
			Me.chkRollewirdfortgesetzt.BackColor = SystemColors.Control
			Me.chkRollewirdfortgesetzt.Cursor = Cursors.[Default]
			Me.chkRollewirdfortgesetzt.ForeColor = SystemColors.ControlText
			Me.chkRollewirdfortgesetzt.Location = New Point(16, 53)
			Me.chkRollewirdfortgesetzt.Name = "chkRollewirdfortgesetzt"
			Me.chkRollewirdfortgesetzt.RightToLeft = RightToLeft.No
			Me.chkRollewirdfortgesetzt.Size = New Size(237, 22)
			Me.chkRollewirdfortgesetzt.TabIndex = 214
			Me.chkRollewirdfortgesetzt.Text = " will be continued"
			Me.chkRollewirdfortgesetzt.UseVisualStyleBackColor = False
			Me.chkBaende.BackColor = SystemColors.Control
			Me.chkBaende.Cursor = Cursors.[Default]
			Me.chkBaende.ForeColor = SystemColors.ControlText
			Me.chkBaende.Location = New Point(16, 14)
			Me.chkBaende.Name = "chkBaende"
			Me.chkBaende.RightToLeft = RightToLeft.No
			Me.chkBaende.Size = New Size(329, 25)
			Me.chkBaende.TabIndex = 212
			Me.chkBaende.Text = "don't split volumes"
			Me.chkBaende.UseVisualStyleBackColor = False
			Me._label__6.BackColor = SystemColors.Control
			Me._label__6.Cursor = Cursors.[Default]
			Me._label__6.ForeColor = SystemColors.ControlText
			Me._label__6.Location = New Point(318, 128)
			Me._label__6.Name = "_label__6"
			Me._label__6.RightToLeft = RightToLeft.No
			Me._label__6.Size = New Size(163, 17)
			Me._label__6.TabIndex = 261
			Me._label__6.Text = "apply continuation at"
			Me.lblPfadFortsetzungsSymbole2.BackColor = SystemColors.Control
			Me.lblPfadFortsetzungsSymbole2.BorderStyle = BorderStyle.Fixed3D
			Me.lblPfadFortsetzungsSymbole2.Cursor = Cursors.[Default]
			Me.lblPfadFortsetzungsSymbole2.Font = New Font("Microsoft Sans Serif", 8.25F)
			Me.lblPfadFortsetzungsSymbole2.ForeColor = SystemColors.ControlText
			Me.lblPfadFortsetzungsSymbole2.Location = New Point(255, 83)
			Me.lblPfadFortsetzungsSymbole2.Name = "lblPfadFortsetzungsSymbole2"
			Me.lblPfadFortsetzungsSymbole2.RightToLeft = RightToLeft.No
			Me.lblPfadFortsetzungsSymbole2.Size = New Size(381, 25)
			Me.lblPfadFortsetzungsSymbole2.TabIndex = 218
			Me.lblPfadFortsetzungsSymbole1.BackColor = SystemColors.Control
			Me.lblPfadFortsetzungsSymbole1.BorderStyle = BorderStyle.Fixed3D
			Me.lblPfadFortsetzungsSymbole1.Cursor = Cursors.[Default]
			Me.lblPfadFortsetzungsSymbole1.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.lblPfadFortsetzungsSymbole1.ForeColor = SystemColors.ControlText
			Me.lblPfadFortsetzungsSymbole1.Location = New Point(255, 46)
			Me.lblPfadFortsetzungsSymbole1.Name = "lblPfadFortsetzungsSymbole1"
			Me.lblPfadFortsetzungsSymbole1.RightToLeft = RightToLeft.No
			Me.lblPfadFortsetzungsSymbole1.Size = New Size(381, 25)
			Me.lblPfadFortsetzungsSymbole1.TabIndex = 215
			Me._tabFrames_TabPage3.Controls.Add(Me.cmdPfadEndSymbole)
			Me._tabFrames_TabPage3.Controls.Add(Me.chkRollEndFrame)
			Me._tabFrames_TabPage3.Controls.Add(Me.chkUseIndex)
			Me._tabFrames_TabPage3.Controls.Add(Me.chkZusatzEndSymbole)
			Me._tabFrames_TabPage3.Controls.Add(Me.lblPfadEndSymbole)
			Me._tabFrames_TabPage3.Location = New Point(4, 24)
			Me._tabFrames_TabPage3.Name = "_tabFrames_TabPage3"
			Me._tabFrames_TabPage3.Size = New Size(856, 214)
			Me._tabFrames_TabPage3.TabIndex = 3
			Me._tabFrames_TabPage3.Text = "Roll End"
			Me.cmdPfadEndSymbole.Location = New Point(658, 86)
			Me.cmdPfadEndSymbole.Name = "cmdPfadEndSymbole"
			Me.cmdPfadEndSymbole.Size = New Size(42, 30)
			Me.cmdPfadEndSymbole.TabIndex = 316
			Me.cmdPfadEndSymbole.Text = "..."
			Me.cmdPfadEndSymbole.UseVisualStyleBackColor = True
			Me.chkRollEndFrame.BackColor = SystemColors.Control
			Me.chkRollEndFrame.Cursor = Cursors.[Default]
			Me.chkRollEndFrame.Enabled = False
			Me.chkRollEndFrame.ForeColor = SystemColors.ControlText
			Me.chkRollEndFrame.Location = New Point(8, 64)
			Me.chkRollEndFrame.Name = "chkRollEndFrame"
			Me.chkRollEndFrame.RightToLeft = RightToLeft.No
			Me.chkRollEndFrame.Size = New Size(189, 17)
			Me.chkRollEndFrame.TabIndex = 209
			Me.chkRollEndFrame.Text = "Roll End Frame"
			Me.chkRollEndFrame.UseVisualStyleBackColor = False
			Me.chkUseIndex.BackColor = SystemColors.Control
			Me.chkUseIndex.Cursor = Cursors.[Default]
			Me.chkUseIndex.Enabled = False
			Me.chkUseIndex.ForeColor = SystemColors.ControlText
			Me.chkUseIndex.Location = New Point(8, 32)
			Me.chkUseIndex.Name = "chkUseIndex"
			Me.chkUseIndex.RightToLeft = RightToLeft.No
			Me.chkUseIndex.Size = New Size(113, 17)
			Me.chkUseIndex.TabIndex = 208
			Me.chkUseIndex.Text = "Index"
			Me.chkUseIndex.UseVisualStyleBackColor = False
			Me.chkZusatzEndSymbole.BackColor = SystemColors.Control
			Me.chkZusatzEndSymbole.Cursor = Cursors.[Default]
			Me.chkZusatzEndSymbole.ForeColor = SystemColors.ControlText
			Me.chkZusatzEndSymbole.Location = New Point(8, 94)
			Me.chkZusatzEndSymbole.Name = "chkZusatzEndSymbole"
			Me.chkZusatzEndSymbole.RightToLeft = RightToLeft.No
			Me.chkZusatzEndSymbole.Size = New Size(195, 17)
			Me.chkZusatzEndSymbole.TabIndex = 207
			Me.chkZusatzEndSymbole.Text = "add. Roll End Symbols"
			Me.chkZusatzEndSymbole.UseVisualStyleBackColor = False
			Me.lblPfadEndSymbole.BackColor = SystemColors.Control
			Me.lblPfadEndSymbole.BorderStyle = BorderStyle.Fixed3D
			Me.lblPfadEndSymbole.Cursor = Cursors.[Default]
			Me.lblPfadEndSymbole.Font = New Font("Microsoft Sans Serif", 8.25F)
			Me.lblPfadEndSymbole.ForeColor = SystemColors.ControlText
			Me.lblPfadEndSymbole.Location = New Point(219, 90)
			Me.lblPfadEndSymbole.Name = "lblPfadEndSymbole"
			Me.lblPfadEndSymbole.RightToLeft = RightToLeft.No
			Me.lblPfadEndSymbole.Size = New Size(433, 25)
			Me.lblPfadEndSymbole.TabIndex = 211
			Me._tabSettings_TabPage4.Controls.Add(Me.cmdTestPortrait)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__2)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__5)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__3)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__4)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__1)
			Me._tabSettings_TabPage4.Controls.Add(Me._Frame__0)
			Me._tabSettings_TabPage4.Location = New Point(4, 34)
			Me._tabSettings_TabPage4.Name = "_tabSettings_TabPage4"
			Me._tabSettings_TabPage4.Size = New Size(913, 268)
			Me._tabSettings_TabPage4.TabIndex = 4
			Me._tabSettings_TabPage4.Text = "Windows"
			Me.cmdTestPortrait.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.cmdTestPortrait.Location = New Point(27, 25)
			Me.cmdTestPortrait.Name = "cmdTestPortrait"
			Me.cmdTestPortrait.Size = New Size(51, 21)
			Me.cmdTestPortrait.TabIndex = 282
			Me.cmdTestPortrait.Text = "Test"
			Me.cmdTestPortrait.UseVisualStyleBackColor = True
			Me._Frame__2.BackColor = SystemColors.Control
			Me._Frame__2.Controls.Add(Me.txtAnnoX)
			Me._Frame__2.Controls.Add(Me.txtAnnoY)
			Me._Frame__2.Controls.Add(Me.txtAnnoBreite)
			Me._Frame__2.Controls.Add(Me.txtAnnoHoehe)
			Me._Frame__2.Controls.Add(Me._label__22)
			Me._Frame__2.Controls.Add(Me._label__21)
			Me._Frame__2.Controls.Add(Me._label38_2)
			Me._Frame__2.Controls.Add(Me._label38_0)
			Me._Frame__2.Controls.Add(Me._label38_1)
			Me._Frame__2.Controls.Add(Me._label38_21)
			Me._Frame__2.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Frame__2.ForeColor = SystemColors.ControlText
			Me._Frame__2.Location = New Point(444, 52)
			Me._Frame__2.Name = "_Frame__2"
			Me._Frame__2.Padding = New Padding(0)
			Me._Frame__2.RightToLeft = RightToLeft.No
			Me._Frame__2.Size = New Size(220, 109)
			Me._Frame__2.TabIndex = 281
			Me._Frame__2.TabStop = False
			Me._Frame__2.Text = "Annotation Window"
			Me.txtAnnoX.AcceptsReturn = True
			Me.txtAnnoX.BackColor = Color.FromArgb(255, 128, 128)
			Me.txtAnnoX.Cursor = Cursors.IBeam
			Me.txtAnnoX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAnnoX.ForeColor = SystemColors.WindowText
			Me.txtAnnoX.Location = New Point(8, 84)
			Me.txtAnnoX.MaxLength = 0
			Me.txtAnnoX.Name = "txtAnnoX"
			Me.txtAnnoX.RightToLeft = RightToLeft.No
			Me.txtAnnoX.Size = New Size(65, 21)
			Me.txtAnnoX.TabIndex = 285
			Me.txtAnnoX.Text = "0"
			Me.txtAnnoX.TextAlign = HorizontalAlignment.Right
			Me.txtAnnoY.AcceptsReturn = True
			Me.txtAnnoY.BackColor = Color.FromArgb(255, 128, 128)
			Me.txtAnnoY.Cursor = Cursors.IBeam
			Me.txtAnnoY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAnnoY.ForeColor = SystemColors.WindowText
			Me.txtAnnoY.Location = New Point(96, 84)
			Me.txtAnnoY.MaxLength = 0
			Me.txtAnnoY.Name = "txtAnnoY"
			Me.txtAnnoY.RightToLeft = RightToLeft.No
			Me.txtAnnoY.Size = New Size(65, 21)
			Me.txtAnnoY.TabIndex = 284
			Me.txtAnnoY.Text = "0"
			Me.txtAnnoY.TextAlign = HorizontalAlignment.Right
			Me.txtAnnoBreite.AcceptsReturn = True
			Me.txtAnnoBreite.BackColor = Color.FromArgb(255, 128, 128)
			Me.txtAnnoBreite.Cursor = Cursors.IBeam
			Me.txtAnnoBreite.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAnnoBreite.ForeColor = SystemColors.WindowText
			Me.txtAnnoBreite.Location = New Point(8, 40)
			Me.txtAnnoBreite.MaxLength = 0
			Me.txtAnnoBreite.Name = "txtAnnoBreite"
			Me.txtAnnoBreite.RightToLeft = RightToLeft.No
			Me.txtAnnoBreite.Size = New Size(65, 21)
			Me.txtAnnoBreite.TabIndex = 283
			Me.txtAnnoBreite.Text = "0"
			Me.txtAnnoBreite.TextAlign = HorizontalAlignment.Right
			Me.txtAnnoHoehe.AcceptsReturn = True
			Me.txtAnnoHoehe.BackColor = Color.FromArgb(255, 128, 128)
			Me.txtAnnoHoehe.Cursor = Cursors.IBeam
			Me.txtAnnoHoehe.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAnnoHoehe.ForeColor = SystemColors.WindowText
			Me.txtAnnoHoehe.Location = New Point(96, 40)
			Me.txtAnnoHoehe.MaxLength = 0
			Me.txtAnnoHoehe.Name = "txtAnnoHoehe"
			Me.txtAnnoHoehe.RightToLeft = RightToLeft.No
			Me.txtAnnoHoehe.Size = New Size(65, 21)
			Me.txtAnnoHoehe.TabIndex = 282
			Me.txtAnnoHoehe.Text = "0"
			Me.txtAnnoHoehe.TextAlign = HorizontalAlignment.Right
			Me._label__22.BackColor = SystemColors.Control
			Me._label__22.Cursor = Cursors.[Default]
			Me._label__22.ForeColor = Color.Black
			Me._label__22.Location = New Point(94, 68)
			Me._label__22.Name = "_label__22"
			Me._label__22.RightToLeft = RightToLeft.No
			Me._label__22.Size = New Size(69, 17)
			Me._label__22.TabIndex = 291
			Me._label__22.Text = "y"
			Me._label__22.TextAlign = ContentAlignment.TopCenter
			Me._label__21.BackColor = SystemColors.Control
			Me._label__21.Cursor = Cursors.[Default]
			Me._label__21.ForeColor = Color.Black
			Me._label__21.Location = New Point(6, 68)
			Me._label__21.Name = "_label__21"
			Me._label__21.RightToLeft = RightToLeft.No
			Me._label__21.Size = New Size(69, 17)
			Me._label__21.TabIndex = 290
			Me._label__21.Text = "x"
			Me._label__21.TextAlign = ContentAlignment.TopCenter
			Me._label38_2.BackColor = SystemColors.Control
			Me._label38_2.Cursor = Cursors.[Default]
			Me._label38_2.ForeColor = SystemColors.ControlText
			Me._label38_2.Location = New Point(172, 84)
			Me._label38_2.Name = "_label38_2"
			Me._label38_2.RightToLeft = RightToLeft.No
			Me._label38_2.Size = New Size(32, 17)
			Me._label38_2.TabIndex = 289
			Me._label38_2.Text = "pels"
			Me._label38_0.BackColor = SystemColors.Control
			Me._label38_0.Cursor = Cursors.[Default]
			Me._label38_0.ForeColor = Color.Black
			Me._label38_0.Location = New Point(6, 24)
			Me._label38_0.Name = "_label38_0"
			Me._label38_0.RightToLeft = RightToLeft.No
			Me._label38_0.Size = New Size(69, 17)
			Me._label38_0.TabIndex = 288
			Me._label38_0.Text = "Width"
			Me._label38_0.TextAlign = ContentAlignment.TopCenter
			Me._label38_1.BackColor = SystemColors.Control
			Me._label38_1.Cursor = Cursors.[Default]
			Me._label38_1.ForeColor = Color.Black
			Me._label38_1.Location = New Point(94, 24)
			Me._label38_1.Name = "_label38_1"
			Me._label38_1.RightToLeft = RightToLeft.No
			Me._label38_1.Size = New Size(69, 21)
			Me._label38_1.TabIndex = 287
			Me._label38_1.Text = "Height"
			Me._label38_1.TextAlign = ContentAlignment.TopCenter
			Me._label38_21.BackColor = SystemColors.Control
			Me._label38_21.Cursor = Cursors.[Default]
			Me._label38_21.ForeColor = SystemColors.ControlText
			Me._label38_21.Location = New Point(172, 42)
			Me._label38_21.Name = "_label38_21"
			Me._label38_21.RightToLeft = RightToLeft.No
			Me._label38_21.Size = New Size(32, 17)
			Me._label38_21.TabIndex = 286
			Me._label38_21.Text = "pels"
			Me._Frame__5.BackColor = SystemColors.Control
			Me._Frame__5.Controls.Add(Me.Text1)
			Me._Frame__5.Controls.Add(Me.txtInfoTextAusrichtung)
			Me._Frame__5.Controls.Add(Me.txtInfoTextX)
			Me._Frame__5.Controls.Add(Me.txtInfoTextY)
			Me._Frame__5.Controls.Add(Me.txtInfoTextFont)
			Me._Frame__5.Controls.Add(Me.txtInfoTextGewicht)
			Me._Frame__5.Controls.Add(Me.Label80)
			Me._Frame__5.Controls.Add(Me._Label_12)
			Me._Frame__5.Controls.Add(Me._Label_8)
			Me._Frame__5.Controls.Add(Me.Label65)
			Me._Frame__5.Controls.Add(Me._label__14)
			Me._Frame__5.Controls.Add(Me._label__15)
			Me._Frame__5.Controls.Add(Me.Label55)
			Me._Frame__5.Controls.Add(Me.Label54)
			Me._Frame__5.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Frame__5.ForeColor = SystemColors.ControlText
			Me._Frame__5.Location = New Point(444, 160)
			Me._Frame__5.Name = "_Frame__5"
			Me._Frame__5.Padding = New Padding(0)
			Me._Frame__5.RightToLeft = RightToLeft.No
			Me._Frame__5.Size = New Size(451, 91)
			Me._Frame__5.TabIndex = 230
			Me._Frame__5.TabStop = False
			Me._Frame__5.Text = "Info"
			Me.Text1.AcceptsReturn = True
			Me.Text1.BackColor = Color.FromArgb(128, 128, 255)
			Me.Text1.Cursor = Cursors.IBeam
			Me.Text1.Enabled = False
			Me.Text1.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.Text1.ForeColor = SystemColors.WindowText
			Me.Text1.Location = New Point(360, 28)
			Me.Text1.MaxLength = 0
			Me.Text1.Name = "Text1"
			Me.Text1.RightToLeft = RightToLeft.No
			Me.Text1.Size = New Size(45, 21)
			Me.Text1.TabIndex = 258
			Me.Text1.Text = "0"
			Me.Text1.TextAlign = HorizontalAlignment.Right
			Me.txtInfoTextAusrichtung.AcceptsReturn = True
			Me.txtInfoTextAusrichtung.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtInfoTextAusrichtung.Cursor = Cursors.IBeam
			Me.txtInfoTextAusrichtung.Enabled = False
			Me.txtInfoTextAusrichtung.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoTextAusrichtung.ForeColor = SystemColors.WindowText
			Me.txtInfoTextAusrichtung.Location = New Point(92, 28)
			Me.txtInfoTextAusrichtung.MaxLength = 0
			Me.txtInfoTextAusrichtung.Name = "txtInfoTextAusrichtung"
			Me.txtInfoTextAusrichtung.RightToLeft = RightToLeft.No
			Me.txtInfoTextAusrichtung.Size = New Size(45, 21)
			Me.txtInfoTextAusrichtung.TabIndex = 235
			Me.txtInfoTextAusrichtung.Text = "0"
			Me.txtInfoTextAusrichtung.TextAlign = HorizontalAlignment.Right
			Me.txtInfoTextX.AcceptsReturn = True
			Me.txtInfoTextX.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtInfoTextX.Cursor = Cursors.IBeam
			Me.txtInfoTextX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoTextX.ForeColor = SystemColors.WindowText
			Me.txtInfoTextX.Location = New Point(92, 60)
			Me.txtInfoTextX.MaxLength = 0
			Me.txtInfoTextX.Name = "txtInfoTextX"
			Me.txtInfoTextX.RightToLeft = RightToLeft.No
			Me.txtInfoTextX.Size = New Size(45, 21)
			Me.txtInfoTextX.TabIndex = 234
			Me.txtInfoTextX.Text = "0"
			Me.txtInfoTextX.TextAlign = HorizontalAlignment.Right
			Me.txtInfoTextY.AcceptsReturn = True
			Me.txtInfoTextY.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtInfoTextY.Cursor = Cursors.IBeam
			Me.txtInfoTextY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoTextY.ForeColor = SystemColors.WindowText
			Me.txtInfoTextY.Location = New Point(210, 60)
			Me.txtInfoTextY.MaxLength = 0
			Me.txtInfoTextY.Name = "txtInfoTextY"
			Me.txtInfoTextY.RightToLeft = RightToLeft.No
			Me.txtInfoTextY.Size = New Size(45, 21)
			Me.txtInfoTextY.TabIndex = 233
			Me.txtInfoTextY.Text = "0"
			Me.txtInfoTextY.TextAlign = HorizontalAlignment.Right
			Me.txtInfoTextFont.AcceptsReturn = True
			Me.txtInfoTextFont.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtInfoTextFont.Cursor = Cursors.IBeam
			Me.txtInfoTextFont.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoTextFont.ForeColor = SystemColors.WindowText
			Me.txtInfoTextFont.Location = New Point(210, 28)
			Me.txtInfoTextFont.MaxLength = 0
			Me.txtInfoTextFont.Name = "txtInfoTextFont"
			Me.txtInfoTextFont.RightToLeft = RightToLeft.No
			Me.txtInfoTextFont.Size = New Size(45, 21)
			Me.txtInfoTextFont.TabIndex = 232
			Me.txtInfoTextFont.Text = "0"
			Me.txtInfoTextFont.TextAlign = HorizontalAlignment.Right
			Me.Label80.BackColor = SystemColors.Control
			Me.Label80.Cursor = Cursors.[Default]
			Me.Label80.ForeColor = SystemColors.ControlText
			Me.Label80.Location = New Point(272, 28)
			Me.Label80.Name = "Label80"
			Me.Label80.RightToLeft = RightToLeft.No
			Me.Label80.Size = New Size(82, 17)
			Me.Label80.TabIndex = 259
			Me.Label80.Text = "Line Space"
			Me.Label80.TextAlign = ContentAlignment.MiddleRight
			Me._Label_12.BackColor = SystemColors.Control
			Me._Label_12.Cursor = Cursors.[Default]
			Me._Label_12.ForeColor = SystemColors.ControlText
			Me._Label_12.Location = New Point(4, 30)
			Me._Label_12.Name = "_Label_12"
			Me._Label_12.RightToLeft = RightToLeft.No
			Me._Label_12.Size = New Size(81, 17)
			Me._Label_12.TabIndex = 242
			Me._Label_12.Text = "Orientation"
			Me._Label_8.BackColor = SystemColors.Control
			Me._Label_8.Cursor = Cursors.[Default]
			Me._Label_8.ForeColor = SystemColors.ControlText
			Me._Label_8.Location = New Point(137, 29)
			Me._Label_8.Name = "_Label_8"
			Me._Label_8.RightToLeft = RightToLeft.No
			Me._Label_8.Size = New Size(17, 17)
			Me._Label_8.TabIndex = 241
			Me._Label_8.Text = "°"
			Me.Label65.BackColor = SystemColors.Control
			Me.Label65.Cursor = Cursors.[Default]
			Me.Label65.ForeColor = SystemColors.ControlText
			Me.Label65.Location = New Point(4, 60)
			Me.Label65.Name = "Label65"
			Me.Label65.RightToLeft = RightToLeft.No
			Me.Label65.Size = New Size(62, 17)
			Me.Label65.TabIndex = 240
			Me.Label65.Text = "Position"
			Me._label__14.BackColor = SystemColors.Control
			Me._label__14.Cursor = Cursors.[Default]
			Me._label__14.ForeColor = SystemColors.ControlText
			Me._label__14.Location = New Point(78, 61)
			Me._label__14.Name = "_label__14"
			Me._label__14.RightToLeft = RightToLeft.No
			Me._label__14.Size = New Size(13, 13)
			Me._label__14.TabIndex = 239
			Me._label__14.Text = "x"
			Me._label__15.BackColor = SystemColors.Control
			Me._label__15.Cursor = Cursors.[Default]
			Me._label__15.ForeColor = SystemColors.ControlText
			Me._label__15.Location = New Point(193, 61)
			Me._label__15.Name = "_label__15"
			Me._label__15.RightToLeft = RightToLeft.No
			Me._label__15.Size = New Size(13, 25)
			Me._label__15.TabIndex = 238
			Me._label__15.Text = "y"
			Me.Label55.BackColor = SystemColors.Control
			Me.Label55.Cursor = Cursors.[Default]
			Me.Label55.ForeColor = SystemColors.ControlText
			Me.Label55.Location = New Point(156, 27)
			Me.Label55.Name = "Label55"
			Me.Label55.RightToLeft = RightToLeft.No
			Me.Label55.Size = New Size(52, 17)
			Me.Label55.TabIndex = 237
			Me.Label55.Text = "Size"
			Me.Label55.TextAlign = ContentAlignment.MiddleRight
			Me.Label54.BackColor = SystemColors.Control
			Me.Label54.Cursor = Cursors.[Default]
			Me.Label54.ForeColor = SystemColors.ControlText
			Me.Label54.Location = New Point(288, 61)
			Me.Label54.Name = "Label54"
			Me.Label54.RightToLeft = RightToLeft.No
			Me.Label54.Size = New Size(61, 17)
			Me.Label54.TabIndex = 236
			Me.Label54.Text = "Weight"
			Me.Label54.TextAlign = ContentAlignment.MiddleRight
			Me._Frame__3.BackColor = SystemColors.Control
			Me._Frame__3.Controls.Add(Me.txtInfoHoehe)
			Me._Frame__3.Controls.Add(Me.txtInfoBreite)
			Me._Frame__3.Controls.Add(Me.txtInfoY)
			Me._Frame__3.Controls.Add(Me.txtInfoX)
			Me._Frame__3.Controls.Add(Me._label__3)
			Me._Frame__3.Controls.Add(Me._Label_52)
			Me._Frame__3.Controls.Add(Me._Label_49)
			Me._Frame__3.Controls.Add(Me._label__4)
			Me._Frame__3.Controls.Add(Me._label__13)
			Me._Frame__3.Controls.Add(Me._label__12)
			Me._Frame__3.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Frame__3.ForeColor = SystemColors.ControlText
			Me._Frame__3.Location = New Point(671, 52)
			Me._Frame__3.Name = "_Frame__3"
			Me._Frame__3.Padding = New Padding(0)
			Me._Frame__3.RightToLeft = RightToLeft.No
			Me._Frame__3.Size = New Size(223, 109)
			Me._Frame__3.TabIndex = 219
			Me._Frame__3.TabStop = False
			Me._Frame__3.Text = "Info Window"
			Me.txtInfoHoehe.AcceptsReturn = True
			Me.txtInfoHoehe.BackColor = Color.FromArgb(128, 255, 255)
			Me.txtInfoHoehe.Cursor = Cursors.IBeam
			Me.txtInfoHoehe.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoHoehe.ForeColor = SystemColors.WindowText
			Me.txtInfoHoehe.Location = New Point(92, 40)
			Me.txtInfoHoehe.MaxLength = 0
			Me.txtInfoHoehe.Name = "txtInfoHoehe"
			Me.txtInfoHoehe.RightToLeft = RightToLeft.No
			Me.txtInfoHoehe.Size = New Size(65, 21)
			Me.txtInfoHoehe.TabIndex = 223
			Me.txtInfoHoehe.Text = "0"
			Me.txtInfoHoehe.TextAlign = HorizontalAlignment.Right
			Me.txtInfoBreite.AcceptsReturn = True
			Me.txtInfoBreite.BackColor = Color.FromArgb(128, 255, 255)
			Me.txtInfoBreite.Cursor = Cursors.IBeam
			Me.txtInfoBreite.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoBreite.ForeColor = SystemColors.WindowText
			Me.txtInfoBreite.Location = New Point(8, 40)
			Me.txtInfoBreite.MaxLength = 0
			Me.txtInfoBreite.Name = "txtInfoBreite"
			Me.txtInfoBreite.RightToLeft = RightToLeft.No
			Me.txtInfoBreite.Size = New Size(65, 21)
			Me.txtInfoBreite.TabIndex = 222
			Me.txtInfoBreite.Text = "0"
			Me.txtInfoBreite.TextAlign = HorizontalAlignment.Right
			Me.txtInfoY.AcceptsReturn = True
			Me.txtInfoY.BackColor = Color.FromArgb(128, 255, 255)
			Me.txtInfoY.Cursor = Cursors.IBeam
			Me.txtInfoY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoY.ForeColor = SystemColors.WindowText
			Me.txtInfoY.Location = New Point(92, 84)
			Me.txtInfoY.MaxLength = 0
			Me.txtInfoY.Name = "txtInfoY"
			Me.txtInfoY.RightToLeft = RightToLeft.No
			Me.txtInfoY.Size = New Size(65, 21)
			Me.txtInfoY.TabIndex = 221
			Me.txtInfoY.Text = "0"
			Me.txtInfoY.TextAlign = HorizontalAlignment.Right
			Me.txtInfoX.AcceptsReturn = True
			Me.txtInfoX.BackColor = Color.FromArgb(128, 255, 255)
			Me.txtInfoX.Cursor = Cursors.IBeam
			Me.txtInfoX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtInfoX.ForeColor = SystemColors.WindowText
			Me.txtInfoX.Location = New Point(8, 84)
			Me.txtInfoX.MaxLength = 0
			Me.txtInfoX.Name = "txtInfoX"
			Me.txtInfoX.RightToLeft = RightToLeft.No
			Me.txtInfoX.Size = New Size(65, 21)
			Me.txtInfoX.TabIndex = 220
			Me.txtInfoX.Text = "0"
			Me.txtInfoX.TextAlign = HorizontalAlignment.Right
			Me._label__3.BackColor = SystemColors.Control
			Me._label__3.Cursor = Cursors.[Default]
			Me._label__3.ForeColor = SystemColors.ControlText
			Me._label__3.Location = New Point(172, 42)
			Me._label__3.Name = "_label__3"
			Me._label__3.RightToLeft = RightToLeft.No
			Me._label__3.Size = New Size(39, 17)
			Me._label__3.TabIndex = 229
			Me._label__3.Text = "pels"
			Me._Label_52.BackColor = SystemColors.Control
			Me._Label_52.Cursor = Cursors.[Default]
			Me._Label_52.ForeColor = Color.Black
			Me._Label_52.Location = New Point(90, 24)
			Me._Label_52.Name = "_Label_52"
			Me._Label_52.RightToLeft = RightToLeft.No
			Me._Label_52.Size = New Size(69, 21)
			Me._Label_52.TabIndex = 228
			Me._Label_52.Text = "Height"
			Me._Label_52.TextAlign = ContentAlignment.TopCenter
			Me._Label_49.BackColor = SystemColors.Control
			Me._Label_49.Cursor = Cursors.[Default]
			Me._Label_49.ForeColor = Color.Black
			Me._Label_49.Location = New Point(6, 24)
			Me._Label_49.Name = "_Label_49"
			Me._Label_49.RightToLeft = RightToLeft.No
			Me._Label_49.Size = New Size(69, 17)
			Me._Label_49.TabIndex = 227
			Me._Label_49.Text = "Width"
			Me._Label_49.TextAlign = ContentAlignment.TopCenter
			Me._label__4.BackColor = SystemColors.Control
			Me._label__4.Cursor = Cursors.[Default]
			Me._label__4.ForeColor = SystemColors.ControlText
			Me._label__4.Location = New Point(172, 86)
			Me._label__4.Name = "_label__4"
			Me._label__4.RightToLeft = RightToLeft.No
			Me._label__4.Size = New Size(39, 17)
			Me._label__4.TabIndex = 226
			Me._label__4.Text = "pels"
			Me._label__13.BackColor = SystemColors.Control
			Me._label__13.Cursor = Cursors.[Default]
			Me._label__13.ForeColor = Color.Black
			Me._label__13.Location = New Point(92, 68)
			Me._label__13.Name = "_label__13"
			Me._label__13.RightToLeft = RightToLeft.No
			Me._label__13.Size = New Size(69, 21)
			Me._label__13.TabIndex = 225
			Me._label__13.Text = "y"
			Me._label__13.TextAlign = ContentAlignment.TopCenter
			Me._label__12.BackColor = SystemColors.Control
			Me._label__12.Cursor = Cursors.[Default]
			Me._label__12.ForeColor = Color.Black
			Me._label__12.Location = New Point(6, 68)
			Me._label__12.Name = "_label__12"
			Me._label__12.RightToLeft = RightToLeft.No
			Me._label__12.Size = New Size(69, 17)
			Me._label__12.TabIndex = 224
			Me._label__12.Text = "x"
			Me._label__12.TextAlign = ContentAlignment.TopCenter
			Me._Frame__4.BackColor = SystemColors.Control
			Me._Frame__4.Controls.Add(Me.txtQuerGewicht)
			Me._Frame__4.Controls.Add(Me.txtQuerFont)
			Me._Frame__4.Controls.Add(Me.txtQuerAnnoY)
			Me._Frame__4.Controls.Add(Me.txtQuerAnnoX)
			Me._Frame__4.Controls.Add(Me.txtQuerAusrichtung)
			Me._Frame__4.Controls.Add(Me.Label73)
			Me._Frame__4.Controls.Add(Me.Label72)
			Me._Frame__4.Controls.Add(Me._label__16)
			Me._Frame__4.Controls.Add(Me._label__17)
			Me._Frame__4.Controls.Add(Me.Label69)
			Me._Frame__4.Controls.Add(Me._Label_7)
			Me._Frame__4.Controls.Add(Me._Label_11)
			Me._Frame__4.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Frame__4.ForeColor = SystemColors.ControlText
			Me._Frame__4.Location = New Point(12, 160)
			Me._Frame__4.Name = "_Frame__4"
			Me._Frame__4.Padding = New Padding(0)
			Me._Frame__4.RightToLeft = RightToLeft.No
			Me._Frame__4.Size = New Size(425, 91)
			Me._Frame__4.TabIndex = 131
			Me._Frame__4.TabStop = False
			Me._Frame__4.Text = "Annotation"
			Me.txtQuerFont.AcceptsReturn = True
			Me.txtQuerFont.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtQuerFont.Cursor = Cursors.IBeam
			Me.txtQuerFont.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerFont.ForeColor = SystemColors.WindowText
			Me.txtQuerFont.Location = New Point(320, 25)
			Me.txtQuerFont.MaxLength = 0
			Me.txtQuerFont.Name = "txtQuerFont"
			Me.txtQuerFont.RightToLeft = RightToLeft.No
			Me.txtQuerFont.Size = New Size(45, 21)
			Me.txtQuerFont.TabIndex = 146
			Me.txtQuerFont.Text = "0"
			Me.txtQuerFont.TextAlign = HorizontalAlignment.Right
			Me.txtQuerAnnoY.AcceptsReturn = True
			Me.txtQuerAnnoY.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtQuerAnnoY.Cursor = Cursors.IBeam
			Me.txtQuerAnnoY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerAnnoY.ForeColor = SystemColors.WindowText
			Me.txtQuerAnnoY.Location = New Point(164, 57)
			Me.txtQuerAnnoY.MaxLength = 0
			Me.txtQuerAnnoY.Name = "txtQuerAnnoY"
			Me.txtQuerAnnoY.RightToLeft = RightToLeft.No
			Me.txtQuerAnnoY.Size = New Size(45, 21)
			Me.txtQuerAnnoY.TabIndex = 145
			Me.txtQuerAnnoY.Text = "0"
			Me.txtQuerAnnoY.TextAlign = HorizontalAlignment.Right
			Me.txtQuerAnnoX.AcceptsReturn = True
			Me.txtQuerAnnoX.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtQuerAnnoX.Cursor = Cursors.IBeam
			Me.txtQuerAnnoX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerAnnoX.ForeColor = SystemColors.WindowText
			Me.txtQuerAnnoX.Location = New Point(92, 57)
			Me.txtQuerAnnoX.MaxLength = 0
			Me.txtQuerAnnoX.Name = "txtQuerAnnoX"
			Me.txtQuerAnnoX.RightToLeft = RightToLeft.No
			Me.txtQuerAnnoX.Size = New Size(45, 21)
			Me.txtQuerAnnoX.TabIndex = 144
			Me.txtQuerAnnoX.Text = "0"
			Me.txtQuerAnnoX.TextAlign = HorizontalAlignment.Right
			Me.txtQuerAusrichtung.AcceptsReturn = True
			Me.txtQuerAusrichtung.BackColor = Color.FromArgb(128, 128, 255)
			Me.txtQuerAusrichtung.Cursor = Cursors.IBeam
			Me.txtQuerAusrichtung.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerAusrichtung.ForeColor = SystemColors.WindowText
			Me.txtQuerAusrichtung.Location = New Point(92, 25)
			Me.txtQuerAusrichtung.MaxLength = 0
			Me.txtQuerAusrichtung.Name = "txtQuerAusrichtung"
			Me.txtQuerAusrichtung.RightToLeft = RightToLeft.No
			Me.txtQuerAusrichtung.Size = New Size(45, 21)
			Me.txtQuerAusrichtung.TabIndex = 143
			Me.txtQuerAusrichtung.Text = "0"
			Me.txtQuerAusrichtung.TextAlign = HorizontalAlignment.Right
			Me.Label73.BackColor = SystemColors.Control
			Me.Label73.Cursor = Cursors.[Default]
			Me.Label73.ForeColor = SystemColors.ControlText
			Me.Label73.Location = New Point(242, 57)
			Me.Label73.Name = "Label73"
			Me.Label73.RightToLeft = RightToLeft.No
			Me.Label73.Size = New Size(69, 17)
			Me.Label73.TabIndex = 154
			Me.Label73.Text = "Weight"
			Me.Label73.TextAlign = ContentAlignment.MiddleRight
			Me.Label72.BackColor = SystemColors.Control
			Me.Label72.Cursor = Cursors.[Default]
			Me.Label72.ForeColor = SystemColors.ControlText
			Me.Label72.Location = New Point(225, 26)
			Me.Label72.Name = "Label72"
			Me.Label72.RightToLeft = RightToLeft.No
			Me.Label72.Size = New Size(89, 17)
			Me.Label72.TabIndex = 153
			Me.Label72.Text = "Size"
			Me.Label72.TextAlign = ContentAlignment.MiddleRight
			Me._label__16.BackColor = SystemColors.Control
			Me._label__16.Cursor = Cursors.[Default]
			Me._label__16.ForeColor = SystemColors.ControlText
			Me._label__16.Location = New Point(152, 58)
			Me._label__16.Name = "_label__16"
			Me._label__16.RightToLeft = RightToLeft.No
			Me._label__16.Size = New Size(13, 21)
			Me._label__16.TabIndex = 152
			Me._label__16.Text = "y"
			Me._label__16.TextAlign = ContentAlignment.TopCenter
			Me._label__17.BackColor = SystemColors.Control
			Me._label__17.Cursor = Cursors.[Default]
			Me._label__17.ForeColor = SystemColors.ControlText
			Me._label__17.Location = New Point(76, 58)
			Me._label__17.Name = "_label__17"
			Me._label__17.RightToLeft = RightToLeft.No
			Me._label__17.Size = New Size(13, 13)
			Me._label__17.TabIndex = 151
			Me._label__17.Text = "x"
			Me.Label69.BackColor = SystemColors.Control
			Me.Label69.Cursor = Cursors.[Default]
			Me.Label69.ForeColor = SystemColors.ControlText
			Me.Label69.Location = New Point(4, 59)
			Me.Label69.Name = "Label69"
			Me.Label69.RightToLeft = RightToLeft.No
			Me.Label69.Size = New Size(62, 17)
			Me.Label69.TabIndex = 150
			Me.Label69.Text = "Position"
			Me._Label_7.BackColor = SystemColors.Control
			Me._Label_7.Cursor = Cursors.[Default]
			Me._Label_7.ForeColor = SystemColors.ControlText
			Me._Label_7.Location = New Point(140, 25)
			Me._Label_7.Name = "_Label_7"
			Me._Label_7.RightToLeft = RightToLeft.No
			Me._Label_7.Size = New Size(25, 25)
			Me._Label_7.TabIndex = 149
			Me._Label_7.Text = "°"
			Me._Label_11.BackColor = SystemColors.Control
			Me._Label_11.Cursor = Cursors.[Default]
			Me._Label_11.ForeColor = SystemColors.ControlText
			Me._Label_11.Location = New Point(4, 27)
			Me._Label_11.Name = "_Label_11"
			Me._Label_11.RightToLeft = RightToLeft.No
			Me._Label_11.Size = New Size(81, 17)
			Me._Label_11.TabIndex = 148
			Me._Label_11.Text = "Orientation"
			Me._Frame__1.BackColor = SystemColors.Control
			Me._Frame__1.Controls.Add(Me.txtQuerBlipX)
			Me._Frame__1.Controls.Add(Me.txtQuerBlipY)
			Me._Frame__1.Controls.Add(Me.txtQuerBlipBreite)
			Me._Frame__1.Controls.Add(Me.txtQuerBlipHoehe)
			Me._Frame__1.Controls.Add(Me._label__10)
			Me._Frame__1.Controls.Add(Me._label__11)
			Me._Frame__1.Controls.Add(Me._label__2)
			Me._Frame__1.Controls.Add(Me._Label_61)
			Me._Frame__1.Controls.Add(Me._Label_60)
			Me._Frame__1.Controls.Add(Me._label__1)
			Me._Frame__1.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Frame__1.ForeColor = SystemColors.ControlText
			Me._Frame__1.Location = New Point(229, 52)
			Me._Frame__1.Name = "_Frame__1"
			Me._Frame__1.Padding = New Padding(0)
			Me._Frame__1.RightToLeft = RightToLeft.No
			Me._Frame__1.Size = New Size(208, 109)
			Me._Frame__1.TabIndex = 130
			Me._Frame__1.TabStop = False
			Me._Frame__1.Text = "BLIP Window"
			Me.txtQuerBlipX.AcceptsReturn = True
			Me.txtQuerBlipX.BackColor = Color.FromArgb(255, 255, 128)
			Me.txtQuerBlipX.Cursor = Cursors.IBeam
			Me.txtQuerBlipX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerBlipX.ForeColor = SystemColors.WindowText
			Me.txtQuerBlipX.Location = New Point(8, 84)
			Me.txtQuerBlipX.MaxLength = 0
			Me.txtQuerBlipX.Name = "txtQuerBlipX"
			Me.txtQuerBlipX.RightToLeft = RightToLeft.No
			Me.txtQuerBlipX.Size = New Size(65, 21)
			Me.txtQuerBlipX.TabIndex = 136
			Me.txtQuerBlipX.Text = "0"
			Me.txtQuerBlipX.TextAlign = HorizontalAlignment.Right
			Me.txtQuerBlipY.AcceptsReturn = True
			Me.txtQuerBlipY.BackColor = Color.FromArgb(255, 255, 128)
			Me.txtQuerBlipY.Cursor = Cursors.IBeam
			Me.txtQuerBlipY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerBlipY.ForeColor = SystemColors.WindowText
			Me.txtQuerBlipY.Location = New Point(92, 84)
			Me.txtQuerBlipY.MaxLength = 0
			Me.txtQuerBlipY.Name = "txtQuerBlipY"
			Me.txtQuerBlipY.RightToLeft = RightToLeft.No
			Me.txtQuerBlipY.Size = New Size(65, 21)
			Me.txtQuerBlipY.TabIndex = 135
			Me.txtQuerBlipY.Text = "0"
			Me.txtQuerBlipY.TextAlign = HorizontalAlignment.Right
			Me.txtQuerBlipBreite.AcceptsReturn = True
			Me.txtQuerBlipBreite.BackColor = Color.FromArgb(255, 255, 128)
			Me.txtQuerBlipBreite.Cursor = Cursors.IBeam
			Me.txtQuerBlipBreite.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerBlipBreite.ForeColor = SystemColors.WindowText
			Me.txtQuerBlipBreite.Location = New Point(7, 40)
			Me.txtQuerBlipBreite.MaxLength = 0
			Me.txtQuerBlipBreite.Name = "txtQuerBlipBreite"
			Me.txtQuerBlipBreite.RightToLeft = RightToLeft.No
			Me.txtQuerBlipBreite.Size = New Size(65, 21)
			Me.txtQuerBlipBreite.TabIndex = 134
			Me.txtQuerBlipBreite.Text = "0"
			Me.txtQuerBlipBreite.TextAlign = HorizontalAlignment.Right
			Me.txtQuerBlipHoehe.AcceptsReturn = True
			Me.txtQuerBlipHoehe.BackColor = Color.FromArgb(255, 255, 128)
			Me.txtQuerBlipHoehe.Cursor = Cursors.IBeam
			Me.txtQuerBlipHoehe.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerBlipHoehe.ForeColor = SystemColors.WindowText
			Me.txtQuerBlipHoehe.Location = New Point(92, 40)
			Me.txtQuerBlipHoehe.MaxLength = 0
			Me.txtQuerBlipHoehe.Name = "txtQuerBlipHoehe"
			Me.txtQuerBlipHoehe.RightToLeft = RightToLeft.No
			Me.txtQuerBlipHoehe.Size = New Size(65, 21)
			Me.txtQuerBlipHoehe.TabIndex = 133
			Me.txtQuerBlipHoehe.Text = "0"
			Me.txtQuerBlipHoehe.TextAlign = HorizontalAlignment.Right
			Me._label__10.BackColor = SystemColors.Control
			Me._label__10.Cursor = Cursors.[Default]
			Me._label__10.ForeColor = Color.Black
			Me._label__10.Location = New Point(6, 68)
			Me._label__10.Name = "_label__10"
			Me._label__10.RightToLeft = RightToLeft.No
			Me._label__10.Size = New Size(69, 17)
			Me._label__10.TabIndex = 142
			Me._label__10.Text = "x"
			Me._label__10.TextAlign = ContentAlignment.TopCenter
			Me._label__11.BackColor = SystemColors.Control
			Me._label__11.Cursor = Cursors.[Default]
			Me._label__11.ForeColor = Color.Black
			Me._label__11.Location = New Point(92, 68)
			Me._label__11.Name = "_label__11"
			Me._label__11.RightToLeft = RightToLeft.No
			Me._label__11.Size = New Size(69, 21)
			Me._label__11.TabIndex = 141
			Me._label__11.Text = "y"
			Me._label__11.TextAlign = ContentAlignment.TopCenter
			Me._label__2.BackColor = SystemColors.Control
			Me._label__2.Cursor = Cursors.[Default]
			Me._label__2.ForeColor = SystemColors.ControlText
			Me._label__2.Location = New Point(172, 86)
			Me._label__2.Name = "_label__2"
			Me._label__2.RightToLeft = RightToLeft.No
			Me._label__2.Size = New Size(33, 17)
			Me._label__2.TabIndex = 140
			Me._label__2.Text = "pels"
			Me._Label_61.BackColor = SystemColors.Control
			Me._Label_61.Cursor = Cursors.[Default]
			Me._Label_61.ForeColor = Color.Black
			Me._Label_61.Location = New Point(6, 24)
			Me._Label_61.Name = "_Label_61"
			Me._Label_61.RightToLeft = RightToLeft.No
			Me._Label_61.Size = New Size(69, 17)
			Me._Label_61.TabIndex = 139
			Me._Label_61.Text = "Width"
			Me._Label_61.TextAlign = ContentAlignment.TopCenter
			Me._Label_60.BackColor = SystemColors.Control
			Me._Label_60.Cursor = Cursors.[Default]
			Me._Label_60.ForeColor = Color.Black
			Me._Label_60.Location = New Point(90, 24)
			Me._Label_60.Name = "_Label_60"
			Me._Label_60.RightToLeft = RightToLeft.No
			Me._Label_60.Size = New Size(69, 21)
			Me._Label_60.TabIndex = 138
			Me._Label_60.Text = "Height"
			Me._Label_60.TextAlign = ContentAlignment.TopCenter
			Me._label__1.BackColor = SystemColors.Control
			Me._label__1.Cursor = Cursors.[Default]
			Me._label__1.ForeColor = SystemColors.ControlText
			Me._label__1.Location = New Point(172, 42)
			Me._label__1.Name = "_label__1"
			Me._label__1.RightToLeft = RightToLeft.No
			Me._label__1.Size = New Size(33, 17)
			Me._label__1.TabIndex = 137
			Me._label__1.Text = "pels"
			Me._Frame__0.BackColor = SystemColors.Control
			Me._Frame__0.Controls.Add(Me.txtQuerBreite)
			Me._Frame__0.Controls.Add(Me.txtQuerHoehe)
			Me._Frame__0.Controls.Add(Me.txtQuerX)
			Me._Frame__0.Controls.Add(Me.txtQuerY)
			Me._Frame__0.Controls.Add(Me._label__0)
			Me._Frame__0.Controls.Add(Me._Label_51)
			Me._Frame__0.Controls.Add(Me._Label_50)
			Me._Frame__0.Controls.Add(Me._label__44)
			Me._Frame__0.Controls.Add(Me._label__8)
			Me._Frame__0.Controls.Add(Me._label__9)
			Me._Frame__0.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._Frame__0.ForeColor = SystemColors.ControlText
			Me._Frame__0.Location = New Point(12, 52)
			Me._Frame__0.Name = "_Frame__0"
			Me._Frame__0.Padding = New Padding(0)
			Me._Frame__0.RightToLeft = RightToLeft.No
			Me._Frame__0.Size = New Size(211, 109)
			Me._Frame__0.TabIndex = 85
			Me._Frame__0.TabStop = False
			Me._Frame__0.Text = "Image Window"
			Me.txtQuerBreite.AcceptsReturn = True
			Me.txtQuerBreite.BackColor = Color.FromArgb(128, 255, 128)
			Me.txtQuerBreite.Cursor = Cursors.IBeam
			Me.txtQuerBreite.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerBreite.ForeColor = SystemColors.WindowText
			Me.txtQuerBreite.Location = New Point(8, 40)
			Me.txtQuerBreite.MaxLength = 0
			Me.txtQuerBreite.Name = "txtQuerBreite"
			Me.txtQuerBreite.RightToLeft = RightToLeft.No
			Me.txtQuerBreite.Size = New Size(65, 21)
			Me.txtQuerBreite.TabIndex = 89
			Me.txtQuerBreite.Text = "0"
			Me.txtQuerBreite.TextAlign = HorizontalAlignment.Right
			Me.txtQuerHoehe.AcceptsReturn = True
			Me.txtQuerHoehe.BackColor = Color.FromArgb(128, 255, 128)
			Me.txtQuerHoehe.Cursor = Cursors.IBeam
			Me.txtQuerHoehe.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerHoehe.ForeColor = SystemColors.WindowText
			Me.txtQuerHoehe.Location = New Point(96, 40)
			Me.txtQuerHoehe.MaxLength = 0
			Me.txtQuerHoehe.Name = "txtQuerHoehe"
			Me.txtQuerHoehe.RightToLeft = RightToLeft.No
			Me.txtQuerHoehe.Size = New Size(65, 21)
			Me.txtQuerHoehe.TabIndex = 88
			Me.txtQuerHoehe.Text = "0"
			Me.txtQuerHoehe.TextAlign = HorizontalAlignment.Right
			Me.txtQuerX.AcceptsReturn = True
			Me.txtQuerX.BackColor = Color.FromArgb(128, 255, 128)
			Me.txtQuerX.Cursor = Cursors.IBeam
			Me.txtQuerX.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerX.ForeColor = SystemColors.WindowText
			Me.txtQuerX.Location = New Point(8, 84)
			Me.txtQuerX.MaxLength = 0
			Me.txtQuerX.Name = "txtQuerX"
			Me.txtQuerX.RightToLeft = RightToLeft.No
			Me.txtQuerX.Size = New Size(65, 21)
			Me.txtQuerX.TabIndex = 87
			Me.txtQuerX.Text = "0"
			Me.txtQuerX.TextAlign = HorizontalAlignment.Right
			Me.txtQuerY.AcceptsReturn = True
			Me.txtQuerY.BackColor = Color.FromArgb(128, 255, 128)
			Me.txtQuerY.Cursor = Cursors.IBeam
			Me.txtQuerY.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtQuerY.ForeColor = SystemColors.WindowText
			Me.txtQuerY.Location = New Point(96, 84)
			Me.txtQuerY.MaxLength = 0
			Me.txtQuerY.Name = "txtQuerY"
			Me.txtQuerY.RightToLeft = RightToLeft.No
			Me.txtQuerY.Size = New Size(65, 21)
			Me.txtQuerY.TabIndex = 86
			Me.txtQuerY.Text = "0"
			Me.txtQuerY.TextAlign = HorizontalAlignment.Right
			Me._label__0.BackColor = SystemColors.Control
			Me._label__0.Cursor = Cursors.[Default]
			Me._label__0.ForeColor = SystemColors.ControlText
			Me._label__0.Location = New Point(176, 84)
			Me._label__0.Name = "_label__0"
			Me._label__0.RightToLeft = RightToLeft.No
			Me._label__0.Size = New Size(32, 21)
			Me._label__0.TabIndex = 155
			Me._label__0.Text = "pels"
			Me._Label_51.BackColor = SystemColors.Control
			Me._Label_51.Cursor = Cursors.[Default]
			Me._Label_51.ForeColor = SystemColors.ControlText
			Me._Label_51.Location = New Point(94, 24)
			Me._Label_51.Name = "_Label_51"
			Me._Label_51.RightToLeft = RightToLeft.No
			Me._Label_51.Size = New Size(69, 17)
			Me._Label_51.TabIndex = 94
			Me._Label_51.Text = "Height"
			Me._Label_51.TextAlign = ContentAlignment.TopCenter
			Me._Label_50.BackColor = SystemColors.Control
			Me._Label_50.Cursor = Cursors.[Default]
			Me._Label_50.ForeColor = SystemColors.ControlText
			Me._Label_50.Location = New Point(6, 24)
			Me._Label_50.Name = "_Label_50"
			Me._Label_50.RightToLeft = RightToLeft.No
			Me._Label_50.Size = New Size(69, 17)
			Me._Label_50.TabIndex = 93
			Me._Label_50.Text = "Width"
			Me._Label_50.TextAlign = ContentAlignment.TopCenter
			Me._label__44.BackColor = SystemColors.Control
			Me._label__44.Cursor = Cursors.[Default]
			Me._label__44.ForeColor = SystemColors.ControlText
			Me._label__44.Location = New Point(176, 44)
			Me._label__44.Name = "_label__44"
			Me._label__44.RightToLeft = RightToLeft.No
			Me._label__44.Size = New Size(32, 21)
			Me._label__44.TabIndex = 92
			Me._label__44.Text = "pels"
			Me._label__8.BackColor = SystemColors.Control
			Me._label__8.Cursor = Cursors.[Default]
			Me._label__8.ForeColor = SystemColors.ControlText
			Me._label__8.Location = New Point(6, 68)
			Me._label__8.Name = "_label__8"
			Me._label__8.RightToLeft = RightToLeft.No
			Me._label__8.Size = New Size(69, 17)
			Me._label__8.TabIndex = 91
			Me._label__8.Text = "x"
			Me._label__8.TextAlign = ContentAlignment.TopCenter
			Me._label__9.BackColor = SystemColors.Control
			Me._label__9.Cursor = Cursors.[Default]
			Me._label__9.ForeColor = SystemColors.ControlText
			Me._label__9.Location = New Point(94, 68)
			Me._label__9.Name = "_label__9"
			Me._label__9.RightToLeft = RightToLeft.No
			Me._label__9.Size = New Size(69, 17)
			Me._label__9.TabIndex = 90
			Me._label__9.Text = "y"
			Me._label__9.TextAlign = ContentAlignment.TopCenter
			Me._tabSettings_TabPage5.Controls.Add(Me.Label10)
			Me._tabSettings_TabPage5.Controls.Add(Me.Label2)
			Me._tabSettings_TabPage5.Controls.Add(Me.Label17)
			Me._tabSettings_TabPage5.Controls.Add(Me.Label18)
			Me._tabSettings_TabPage5.Controls.Add(Me._Label19_0)
			Me._tabSettings_TabPage5.Controls.Add(Me.Label20)
			Me._tabSettings_TabPage5.Controls.Add(Me.Label28)
			Me._tabSettings_TabPage5.Controls.Add(Me._label__29)
			Me._tabSettings_TabPage5.Controls.Add(Me.chkSplit)
			Me._tabSettings_TabPage5.Controls.Add(Me.cmbMaxDocumentSize)
			Me._tabSettings_TabPage5.Controls.Add(Me.txtSplitBreite)
			Me._tabSettings_TabPage5.Controls.Add(Me.txtSplitLaenge)
			Me._tabSettings_TabPage5.Controls.Add(Me.cmbSplitCount)
			Me._tabSettings_TabPage5.Controls.Add(Me.txtOverSize)
			Me._tabSettings_TabPage5.Location = New Point(4, 34)
			Me._tabSettings_TabPage5.Name = "_tabSettings_TabPage5"
			Me._tabSettings_TabPage5.Size = New Size(913, 268)
			Me._tabSettings_TabPage5.TabIndex = 5
			Me._tabSettings_TabPage5.Text = "Split"
			Me.Label10.BackColor = SystemColors.Control
			Me.Label10.Cursor = Cursors.[Default]
			Me.Label10.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label10.ForeColor = SystemColors.ControlText
			Me.Label10.Location = New Point(416, 127)
			Me.Label10.Name = "Label10"
			Me.Label10.RightToLeft = RightToLeft.No
			Me.Label10.Size = New Size(42, 19)
			Me.Label10.TabIndex = 119
			Me.Label10.Text = "mm"
			Me.Label2.BackColor = SystemColors.Control
			Me.Label2.Cursor = Cursors.[Default]
			Me.Label2.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label2.ForeColor = SystemColors.ControlText
			Me.Label2.Location = New Point(32, 72)
			Me.Label2.Name = "Label2"
			Me.Label2.RightToLeft = RightToLeft.No
			Me.Label2.Size = New Size(233, 17)
			Me.Label2.TabIndex = 76
			Me.Label2.Text = "Minimal Document Size being split"
			Me.Label17.BackColor = SystemColors.Control
			Me.Label17.Cursor = Cursors.[Default]
			Me.Label17.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label17.ForeColor = SystemColors.ControlText
			Me.Label17.Location = New Point(13, 126)
			Me.Label17.Name = "Label17"
			Me.Label17.RightToLeft = RightToLeft.No
			Me.Label17.Size = New Size(81, 17)
			Me.Label17.TabIndex = 80
			Me.Label17.Text = "Width"
			Me.Label17.TextAlign = ContentAlignment.TopCenter
			Me.Label18.BackColor = SystemColors.Control
			Me.Label18.Cursor = Cursors.[Default]
			Me.Label18.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label18.ForeColor = SystemColors.ControlText
			Me.Label18.Location = New Point(250, 126)
			Me.Label18.Name = "Label18"
			Me.Label18.RightToLeft = RightToLeft.No
			Me.Label18.Size = New Size(81, 17)
			Me.Label18.TabIndex = 81
			Me.Label18.Text = "Length"
			Me.Label18.TextAlign = ContentAlignment.TopCenter
			Me._Label19_0.BackColor = SystemColors.Control
			Me._Label19_0.Cursor = Cursors.[Default]
			Me._Label19_0.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label19_0.ForeColor = SystemColors.ControlText
			Me._Label19_0.Location = New Point(179, 127)
			Me._Label19_0.Name = "_Label19_0"
			Me._Label19_0.RightToLeft = RightToLeft.No
			Me._Label19_0.Size = New Size(42, 19)
			Me._Label19_0.TabIndex = 82
			Me._Label19_0.Text = "mm"
			Me.Label20.BackColor = SystemColors.Control
			Me.Label20.Cursor = Cursors.[Default]
			Me.Label20.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label20.ForeColor = SystemColors.ControlText
			Me.Label20.Location = New Point(32, 180)
			Me.Label20.Name = "Label20"
			Me.Label20.RightToLeft = RightToLeft.No
			Me.Label20.Size = New Size(225, 15)
			Me.Label20.TabIndex = 84
			Me.Label20.Text = "Slit Count"
			Me.Label28.BackColor = SystemColors.Control
			Me.Label28.Cursor = Cursors.[Default]
			Me.Label28.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label28.ForeColor = SystemColors.ControlText
			Me.Label28.Location = New Point(32, 220)
			Me.Label28.Name = "Label28"
			Me.Label28.RightToLeft = RightToLeft.No
			Me.Label28.Size = New Size(225, 18)
			Me.Label28.TabIndex = 117
			Me.Label28.Text = "Split Tile Oversize"
			Me._label__29.BackColor = SystemColors.Control
			Me._label__29.Cursor = Cursors.[Default]
			Me._label__29.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._label__29.ForeColor = SystemColors.ControlText
			Me._label__29.Location = New Point(356, 220)
			Me._label__29.Name = "_label__29"
			Me._label__29.RightToLeft = RightToLeft.No
			Me._label__29.Size = New Size(17, 13)
			Me._label__29.TabIndex = 118
			Me._label__29.Text = "%"
			Me.chkSplit.BackColor = SystemColors.Control
			Me.chkSplit.Cursor = Cursors.[Default]
			Me.chkSplit.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.chkSplit.ForeColor = SystemColors.ControlText
			Me.chkSplit.Location = New Point(34, 33)
			Me.chkSplit.Name = "chkSplit"
			Me.chkSplit.RightToLeft = RightToLeft.No
			Me.chkSplit.Size = New Size(444, 22)
			Me.chkSplit.TabIndex = 75
			Me.chkSplit.Text = "Split Large Documents in multiple Frames"
			Me.chkSplit.UseVisualStyleBackColor = False
			Me.cmbMaxDocumentSize.BackColor = SystemColors.Window
			Me.cmbMaxDocumentSize.Cursor = Cursors.[Default]
			Me.cmbMaxDocumentSize.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbMaxDocumentSize.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmbMaxDocumentSize.ForeColor = SystemColors.WindowText
			Me.cmbMaxDocumentSize.Items.AddRange(New Object() { "A4", "A3", "A2", "A1", "A0", "benutzerdefiniert" })
			Me.cmbMaxDocumentSize.Location = New Point(271, 70)
			Me.cmbMaxDocumentSize.Name = "cmbMaxDocumentSize"
			Me.cmbMaxDocumentSize.RightToLeft = RightToLeft.No
			Me.cmbMaxDocumentSize.Size = New Size(185, 24)
			Me.cmbMaxDocumentSize.TabIndex = 77
			Me.txtSplitBreite.AcceptsReturn = True
			Me.txtSplitBreite.BackColor = SystemColors.Window
			Me.txtSplitBreite.Cursor = Cursors.IBeam
			Me.txtSplitBreite.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtSplitBreite.ForeColor = SystemColors.WindowText
			Me.txtSplitBreite.Location = New Point(94, 125)
			Me.txtSplitBreite.MaxLength = 0
			Me.txtSplitBreite.Name = "txtSplitBreite"
			Me.txtSplitBreite.RightToLeft = RightToLeft.No
			Me.txtSplitBreite.Size = New Size(81, 22)
			Me.txtSplitBreite.TabIndex = 78
			Me.txtSplitBreite.TextAlign = HorizontalAlignment.Right
			Me.txtSplitLaenge.AcceptsReturn = True
			Me.txtSplitLaenge.BackColor = SystemColors.Window
			Me.txtSplitLaenge.Cursor = Cursors.IBeam
			Me.txtSplitLaenge.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtSplitLaenge.ForeColor = SystemColors.WindowText
			Me.txtSplitLaenge.Location = New Point(331, 125)
			Me.txtSplitLaenge.MaxLength = 0
			Me.txtSplitLaenge.Name = "txtSplitLaenge"
			Me.txtSplitLaenge.RightToLeft = RightToLeft.No
			Me.txtSplitLaenge.Size = New Size(81, 22)
			Me.txtSplitLaenge.TabIndex = 79
			Me.txtSplitLaenge.TextAlign = HorizontalAlignment.Right
			Me.cmbSplitCount.BackColor = SystemColors.Window
			Me.cmbSplitCount.Cursor = Cursors.[Default]
			Me.cmbSplitCount.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbSplitCount.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmbSplitCount.ForeColor = SystemColors.WindowText
			Me.cmbSplitCount.Items.AddRange(New Object() { "4", "9" })
			Me.cmbSplitCount.Location = New Point(269, 180)
			Me.cmbSplitCount.Name = "cmbSplitCount"
			Me.cmbSplitCount.RightToLeft = RightToLeft.No
			Me.cmbSplitCount.Size = New Size(185, 24)
			Me.cmbSplitCount.TabIndex = 83
			Me.txtOverSize.AcceptsReturn = True
			Me.txtOverSize.BackColor = SystemColors.Window
			Me.txtOverSize.Cursor = Cursors.IBeam
			Me.txtOverSize.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtOverSize.ForeColor = SystemColors.WindowText
			Me.txtOverSize.Location = New Point(268, 216)
			Me.txtOverSize.MaxLength = 0
			Me.txtOverSize.Name = "txtOverSize"
			Me.txtOverSize.RightToLeft = RightToLeft.No
			Me.txtOverSize.Size = New Size(81, 22)
			Me.txtOverSize.TabIndex = 116
			Me.txtOverSize.Text = "10"
			Me.txtOverSize.TextAlign = HorizontalAlignment.Right
			Me._tabSettings_TabPage6.Controls.Add(Me._txtVerschluss_1)
			Me._tabSettings_TabPage6.Controls.Add(Me.chkFesteBelegzahl)
			Me._tabSettings_TabPage6.Controls.Add(Me.txtAddStepLevel3)
			Me._tabSettings_TabPage6.Controls.Add(Me.txtAddStepLevel2)
			Me._tabSettings_TabPage6.Controls.Add(Me.Frame7)
			Me._tabSettings_TabPage6.Controls.Add(Me.txtSchritteBelichtung)
			Me._tabSettings_TabPage6.Controls.Add(Me.chkStepsImageToImage)
			Me._tabSettings_TabPage6.Controls.Add(Me.txtSchritte)
			Me._tabSettings_TabPage6.Controls.Add(Me._txtVerschluss_0)
			Me._tabSettings_TabPage6.Controls.Add(Me.txtZusatzBelichtung)
			Me._tabSettings_TabPage6.Controls.Add(Me._Label96_4)
			Me._tabSettings_TabPage6.Controls.Add(Me._label__20)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label22)
			Me._tabSettings_TabPage6.Controls.Add(Me._label__18)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label8)
			Me._tabSettings_TabPage6.Controls.Add(Me.Image1)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label35)
			Me._tabSettings_TabPage6.Controls.Add(Me._label__31)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label30)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label26)
			Me._tabSettings_TabPage6.Controls.Add(Me.Label25)
			Me._tabSettings_TabPage6.Controls.Add(Me._label__46)
			Me._tabSettings_TabPage6.Location = New Point(4, 34)
			Me._tabSettings_TabPage6.Name = "_tabSettings_TabPage6"
			Me._tabSettings_TabPage6.Size = New Size(913, 268)
			Me._tabSettings_TabPage6.TabIndex = 6
			Me._tabSettings_TabPage6.Text = "Steps"
			Me._txtVerschluss_1.AcceptsReturn = True
			Me._txtVerschluss_1.BackColor = Color.FromArgb(224, 224, 224)
			Me._txtVerschluss_1.BorderStyle = BorderStyle.FixedSingle
			Me._txtVerschluss_1.Cursor = Cursors.IBeam
			Me._txtVerschluss_1.Enabled = False
			Me._txtVerschluss_1.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtVerschluss_1.ForeColor = SystemColors.WindowText
			Me._txtVerschluss_1.Location = New Point(290, 160)
			Me._txtVerschluss_1.MaxLength = 0
			Me._txtVerschluss_1.Multiline = True
			Me._txtVerschluss_1.Name = "_txtVerschluss_1"
			Me._txtVerschluss_1.[ReadOnly] = True
			Me._txtVerschluss_1.RightToLeft = RightToLeft.No
			Me._txtVerschluss_1.Size = New Size(73, 22)
			Me._txtVerschluss_1.TabIndex = 334
			Me._txtVerschluss_1.TextAlign = HorizontalAlignment.Right
			Me.chkFesteBelegzahl.BackColor = SystemColors.Control
			Me.chkFesteBelegzahl.CheckAlign = ContentAlignment.MiddleRight
			Me.chkFesteBelegzahl.Cursor = Cursors.[Default]
			Me.chkFesteBelegzahl.Font = New Font("Microsoft Sans Serif", 9F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.chkFesteBelegzahl.ForeColor = SystemColors.ControlText
			Me.chkFesteBelegzahl.Location = New Point(16, 32)
			Me.chkFesteBelegzahl.Name = "chkFesteBelegzahl"
			Me.chkFesteBelegzahl.RightToLeft = RightToLeft.No
			Me.chkFesteBelegzahl.Size = New Size(289, 25)
			Me.chkFesteBelegzahl.TabIndex = 280
			Me.chkFesteBelegzahl.Text = "Expose a fix Number of Pages per Roll"
			Me.chkFesteBelegzahl.UseVisualStyleBackColor = False
			Me.txtAddStepLevel3.AcceptsReturn = True
			Me.txtAddStepLevel3.BackColor = SystemColors.Window
			Me.txtAddStepLevel3.Cursor = Cursors.IBeam
			Me.txtAddStepLevel3.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAddStepLevel3.ForeColor = SystemColors.WindowText
			Me.txtAddStepLevel3.Location = New Point(664, 99)
			Me.txtAddStepLevel3.MaxLength = 0
			Me.txtAddStepLevel3.Multiline = True
			Me.txtAddStepLevel3.Name = "txtAddStepLevel3"
			Me.txtAddStepLevel3.RightToLeft = RightToLeft.No
			Me.txtAddStepLevel3.Size = New Size(73, 22)
			Me.txtAddStepLevel3.TabIndex = 265
			Me.txtAddStepLevel3.TextAlign = HorizontalAlignment.Right
			Me.txtAddStepLevel2.AcceptsReturn = True
			Me.txtAddStepLevel2.BackColor = SystemColors.Window
			Me.txtAddStepLevel2.Cursor = Cursors.IBeam
			Me.txtAddStepLevel2.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAddStepLevel2.ForeColor = SystemColors.WindowText
			Me.txtAddStepLevel2.Location = New Point(290, 96)
			Me.txtAddStepLevel2.MaxLength = 0
			Me.txtAddStepLevel2.Multiline = True
			Me.txtAddStepLevel2.Name = "txtAddStepLevel2"
			Me.txtAddStepLevel2.RightToLeft = RightToLeft.No
			Me.txtAddStepLevel2.Size = New Size(73, 22)
			Me.txtAddStepLevel2.TabIndex = 262
			Me.txtAddStepLevel2.TextAlign = HorizontalAlignment.Right
			Me.Frame7.BackColor = SystemColors.Control
			Me.Frame7.Controls.Add(Me.chkTrailerInfoFrames)
			Me.Frame7.Controls.Add(Me.chkAutoTrailer)
			Me.Frame7.Controls.Add(Me.txtAutoTrailerDistance)
			Me.Frame7.Controls.Add(Me.txtAutoTrailerLength)
			Me.Frame7.Controls.Add(Me._label__38)
			Me.Frame7.Controls.Add(Me._label__39)
			Me.Frame7.Controls.Add(Me.Label40)
			Me.Frame7.Controls.Add(Me.Label41)
			Me.Frame7.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Frame7.ForeColor = SystemColors.ControlText
			Me.Frame7.Location = New Point(402, 128)
			Me.Frame7.Name = "Frame7"
			Me.Frame7.Padding = New Padding(0)
			Me.Frame7.RightToLeft = RightToLeft.No
			Me.Frame7.Size = New Size(372, 124)
			Me.Frame7.TabIndex = 180
			Me.Frame7.TabStop = False
			Me.Frame7.Text = "Autotrailer"
			Me.chkTrailerInfoFrames.BackColor = SystemColors.Control
			Me.chkTrailerInfoFrames.Cursor = Cursors.[Default]
			Me.chkTrailerInfoFrames.ForeColor = SystemColors.ControlText
			Me.chkTrailerInfoFrames.Location = New Point(30, 91)
			Me.chkTrailerInfoFrames.Name = "chkTrailerInfoFrames"
			Me.chkTrailerInfoFrames.RightToLeft = RightToLeft.No
			Me.chkTrailerInfoFrames.Size = New Size(323, 17)
			Me.chkTrailerInfoFrames.TabIndex = 188
			Me.chkTrailerInfoFrames.Text = "Use Start and End Frames after Autotrailers"
			Me.chkTrailerInfoFrames.UseVisualStyleBackColor = False
			Me.chkAutoTrailer.BackColor = SystemColors.Control
			Me.chkAutoTrailer.Cursor = Cursors.[Default]
			Me.chkAutoTrailer.ForeColor = SystemColors.ControlText
			Me.chkAutoTrailer.Location = New Point(30, 24)
			Me.chkAutoTrailer.Name = "chkAutoTrailer"
			Me.chkAutoTrailer.RightToLeft = RightToLeft.No
			Me.chkAutoTrailer.Size = New Size(17, 17)
			Me.chkAutoTrailer.TabIndex = 183
			Me.chkAutoTrailer.UseVisualStyleBackColor = False
			Me.txtAutoTrailerDistance.AcceptsReturn = True
			Me.txtAutoTrailerDistance.BackColor = SystemColors.Window
			Me.txtAutoTrailerDistance.Cursor = Cursors.IBeam
			Me.txtAutoTrailerDistance.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAutoTrailerDistance.ForeColor = SystemColors.WindowText
			Me.txtAutoTrailerDistance.Location = New Point(262, 16)
			Me.txtAutoTrailerDistance.MaxLength = 0
			Me.txtAutoTrailerDistance.Multiline = True
			Me.txtAutoTrailerDistance.Name = "txtAutoTrailerDistance"
			Me.txtAutoTrailerDistance.RightToLeft = RightToLeft.No
			Me.txtAutoTrailerDistance.Size = New Size(73, 22)
			Me.txtAutoTrailerDistance.TabIndex = 182
			Me.txtAutoTrailerDistance.TextAlign = HorizontalAlignment.Right
			Me.txtAutoTrailerLength.AcceptsReturn = True
			Me.txtAutoTrailerLength.BackColor = SystemColors.Window
			Me.txtAutoTrailerLength.Cursor = Cursors.IBeam
			Me.txtAutoTrailerLength.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtAutoTrailerLength.ForeColor = SystemColors.WindowText
			Me.txtAutoTrailerLength.Location = New Point(262, 48)
			Me.txtAutoTrailerLength.MaxLength = 0
			Me.txtAutoTrailerLength.Multiline = True
			Me.txtAutoTrailerLength.Name = "txtAutoTrailerLength"
			Me.txtAutoTrailerLength.RightToLeft = RightToLeft.No
			Me.txtAutoTrailerLength.Size = New Size(73, 22)
			Me.txtAutoTrailerLength.TabIndex = 181
			Me.txtAutoTrailerLength.TextAlign = HorizontalAlignment.Right
			Me._label__38.BackColor = SystemColors.Control
			Me._label__38.Cursor = Cursors.[Default]
			Me._label__38.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__38.ForeColor = SystemColors.ControlText
			Me._label__38.Location = New Point(320, 23)
			Me._label__38.Name = "_label__38"
			Me._label__38.RightToLeft = RightToLeft.No
			Me._label__38.Size = New Size(33, 19)
			Me._label__38.TabIndex = 187
			Me._label__38.Text = "m"
			Me._label__39.BackColor = SystemColors.Control
			Me._label__39.Cursor = Cursors.[Default]
			Me._label__39.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__39.ForeColor = SystemColors.ControlText
			Me._label__39.Location = New Point(320, 53)
			Me._label__39.Name = "_label__39"
			Me._label__39.RightToLeft = RightToLeft.No
			Me._label__39.Size = New Size(33, 19)
			Me._label__39.TabIndex = 186
			Me._label__39.Text = "m"
			Me.Label40.BackColor = SystemColors.Control
			Me.Label40.Cursor = Cursors.[Default]
			Me.Label40.ForeColor = SystemColors.ControlText
			Me.Label40.Location = New Point(138, 53)
			Me.Label40.Name = "Label40"
			Me.Label40.RightToLeft = RightToLeft.No
			Me.Label40.Size = New Size(117, 19)
			Me.Label40.TabIndex = 185
			Me.Label40.Text = "Trailer Length"
			Me.Label40.TextAlign = ContentAlignment.TopRight
			Me.Label41.BackColor = SystemColors.Control
			Me.Label41.Cursor = Cursors.[Default]
			Me.Label41.ForeColor = SystemColors.ControlText
			Me.Label41.Location = New Point(53, 24)
			Me.Label41.Name = "Label41"
			Me.Label41.RightToLeft = RightToLeft.No
			Me.Label41.Size = New Size(207, 17)
			Me.Label41.TabIndex = 184
			Me.Label41.Text = "Insert a Trailer automatically each"
			Me.txtSchritteBelichtung.AcceptsReturn = True
			Me.txtSchritteBelichtung.BackColor = SystemColors.Window
			Me.txtSchritteBelichtung.Cursor = Cursors.IBeam
			Me.txtSchritteBelichtung.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtSchritteBelichtung.ForeColor = SystemColors.WindowText
			Me.txtSchritteBelichtung.Location = New Point(290, 224)
			Me.txtSchritteBelichtung.MaxLength = 0
			Me.txtSchritteBelichtung.Multiline = True
			Me.txtSchritteBelichtung.Name = "txtSchritteBelichtung"
			Me.txtSchritteBelichtung.RightToLeft = RightToLeft.No
			Me.txtSchritteBelichtung.Size = New Size(73, 22)
			Me.txtSchritteBelichtung.TabIndex = 123
			Me.txtSchritteBelichtung.TextAlign = HorizontalAlignment.Right
			Me.chkStepsImageToImage.BackColor = SystemColors.Control
			Me.chkStepsImageToImage.Cursor = Cursors.[Default]
			Me.chkStepsImageToImage.Font = New Font("Microsoft Sans Serif", 9F)
			Me.chkStepsImageToImage.ForeColor = SystemColors.ControlText
			Me.chkStepsImageToImage.Location = New Point(458, 70)
			Me.chkStepsImageToImage.Name = "chkStepsImageToImage"
			Me.chkStepsImageToImage.RightToLeft = RightToLeft.No
			Me.chkStepsImageToImage.Size = New Size(336, 17)
			Me.chkStepsImageToImage.TabIndex = 122
			Me.chkStepsImageToImage.Text = "Distance between Images on Film"
			Me.chkStepsImageToImage.UseVisualStyleBackColor = False
			Me.txtSchritte.AcceptsReturn = True
			Me.txtSchritte.BackColor = SystemColors.Window
			Me.txtSchritte.Cursor = Cursors.IBeam
			Me.txtSchritte.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtSchritte.ForeColor = SystemColors.WindowText
			Me.txtSchritte.Location = New Point(290, 64)
			Me.txtSchritte.MaxLength = 0
			Me.txtSchritte.Multiline = True
			Me.txtSchritte.Name = "txtSchritte"
			Me.txtSchritte.RightToLeft = RightToLeft.No
			Me.txtSchritte.Size = New Size(73, 22)
			Me.txtSchritte.TabIndex = 97
			Me.txtSchritte.TextAlign = HorizontalAlignment.Right
			Me._txtVerschluss_0.AcceptsReturn = True
			Me._txtVerschluss_0.BackColor = SystemColors.Window
			Me._txtVerschluss_0.Cursor = Cursors.IBeam
			Me._txtVerschluss_0.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._txtVerschluss_0.ForeColor = SystemColors.WindowText
			Me._txtVerschluss_0.Location = New Point(290, 128)
			Me._txtVerschluss_0.MaxLength = 0
			Me._txtVerschluss_0.Multiline = True
			Me._txtVerschluss_0.Name = "_txtVerschluss_0"
			Me._txtVerschluss_0.RightToLeft = RightToLeft.No
			Me._txtVerschluss_0.Size = New Size(73, 22)
			Me._txtVerschluss_0.TabIndex = 96
			Me._txtVerschluss_0.TextAlign = HorizontalAlignment.Right
			Me.txtZusatzBelichtung.AcceptsReturn = True
			Me.txtZusatzBelichtung.BackColor = SystemColors.Window
			Me.txtZusatzBelichtung.Cursor = Cursors.IBeam
			Me.txtZusatzBelichtung.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.txtZusatzBelichtung.ForeColor = SystemColors.WindowText
			Me.txtZusatzBelichtung.Location = New Point(290, 192)
			Me.txtZusatzBelichtung.MaxLength = 0
			Me.txtZusatzBelichtung.Multiline = True
			Me.txtZusatzBelichtung.Name = "txtZusatzBelichtung"
			Me.txtZusatzBelichtung.RightToLeft = RightToLeft.No
			Me.txtZusatzBelichtung.Size = New Size(73, 22)
			Me.txtZusatzBelichtung.TabIndex = 95
			Me.txtZusatzBelichtung.TextAlign = HorizontalAlignment.Right
			Me._Label96_4.BackColor = Color.Transparent
			Me._Label96_4.Cursor = Cursors.[Default]
			Me._Label96_4.Font = New Font("Microsoft Sans Serif", 9F)
			Me._Label96_4.ForeColor = SystemColors.ControlText
			Me._Label96_4.Location = New Point(370, 163)
			Me._Label96_4.Name = "_Label96_4"
			Me._Label96_4.RightToLeft = RightToLeft.No
			Me._Label96_4.Size = New Size(25, 17)
			Me._Label96_4.TabIndex = 312
			Me._Label96_4.Text = "Hz"
			Me._Label96_4.Visible = False
			Me._label__20.BackColor = SystemColors.Control
			Me._label__20.Cursor = Cursors.[Default]
			Me._label__20.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__20.ForeColor = SystemColors.ControlText
			Me._label__20.Location = New Point(742, 102)
			Me._label__20.Name = "_label__20"
			Me._label__20.RightToLeft = RightToLeft.No
			Me._label__20.Size = New Size(33, 17)
			Me._label__20.TabIndex = 267
			Me._label__20.Text = "mm"
			Me.Label22.BackColor = SystemColors.Control
			Me.Label22.Cursor = Cursors.[Default]
			Me.Label22.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label22.ForeColor = SystemColors.ControlText
			Me.Label22.Location = New Point(404, 101)
			Me.Label22.Name = "Label22"
			Me.Label22.RightToLeft = RightToLeft.No
			Me.Label22.Size = New Size(225, 19)
			Me.Label22.TabIndex = 266
			Me.Label22.Text = "Add. Steps for new Volume (Level 3)"
			Me._label__18.BackColor = SystemColors.Control
			Me._label__18.Cursor = Cursors.[Default]
			Me._label__18.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__18.ForeColor = SystemColors.ControlText
			Me._label__18.Location = New Point(370, 98)
			Me._label__18.Name = "_label__18"
			Me._label__18.RightToLeft = RightToLeft.No
			Me._label__18.Size = New Size(34, 17)
			Me._label__18.TabIndex = 264
			Me._label__18.Text = "mm"
			Me.Label8.BackColor = SystemColors.Control
			Me.Label8.Cursor = Cursors.[Default]
			Me.Label8.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label8.ForeColor = SystemColors.ControlText
			Me.Label8.Location = New Point(16, 101)
			Me.Label8.Name = "Label8"
			Me.Label8.RightToLeft = RightToLeft.No
			Me.Label8.Size = New Size(246, 19)
			Me.Label8.TabIndex = 263
			Me.Label8.Text = "Add. Steps for new Document (Level 2)"
			Me.Image1.Cursor = Cursors.[Default]
			Me.Image1.Image = CType(componentResourceManager.GetObject("Image1.Image"), Image)
			Me.Image1.Location = New Point(402, 62)
			Me.Image1.Name = "Image1"
			Me.Image1.Size = New Size(32, 32)
			Me.Image1.TabIndex = 335
			Me.Image1.TabStop = False
			Me.Label35.BackColor = SystemColors.Control
			Me.Label35.Cursor = Cursors.[Default]
			Me.Label35.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label35.ForeColor = SystemColors.ControlText
			Me.Label35.Location = New Point(16, 228)
			Me.Label35.Name = "Label35"
			Me.Label35.RightToLeft = RightToLeft.No
			Me.Label35.Size = New Size(233, 19)
			Me.Label35.TabIndex = 124
			Me.Label35.Text = "Number of Exposures"
			Me._label__31.BackColor = SystemColors.Control
			Me._label__31.Cursor = Cursors.[Default]
			Me._label__31.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__31.ForeColor = SystemColors.ControlText
			Me._label__31.Location = New Point(370, 66)
			Me._label__31.Name = "_label__31"
			Me._label__31.RightToLeft = RightToLeft.No
			Me._label__31.Size = New Size(33, 17)
			Me._label__31.TabIndex = 102
			Me._label__31.Text = "mm"
			Me.Label30.BackColor = SystemColors.Control
			Me.Label30.Cursor = Cursors.[Default]
			Me.Label30.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label30.ForeColor = SystemColors.ControlText
			Me.Label30.Location = New Point(16, 69)
			Me.Label30.Name = "Label30"
			Me.Label30.RightToLeft = RightToLeft.No
			Me.Label30.Size = New Size(185, 19)
			Me.Label30.TabIndex = 101
			Me.Label30.Text = "Frame Distane"
			Me.Label26.BackColor = Color.Transparent
			Me.Label26.Cursor = Cursors.[Default]
			Me.Label26.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label26.ForeColor = SystemColors.ControlText
			Me.Label26.Location = New Point(16, 131)
			Me.Label26.Name = "Label26"
			Me.Label26.RightToLeft = RightToLeft.No
			Me.Label26.Size = New Size(225, 19)
			Me.Label26.TabIndex = 100
			Me.Label26.Text = "Shutter Speed"
			Me.Label25.BackColor = SystemColors.Control
			Me.Label25.Cursor = Cursors.[Default]
			Me.Label25.Font = New Font("Microsoft Sans Serif", 9F)
			Me.Label25.ForeColor = SystemColors.ControlText
			Me.Label25.Location = New Point(16, 197)
			Me.Label25.Name = "Label25"
			Me.Label25.RightToLeft = RightToLeft.No
			Me.Label25.Size = New Size(233, 19)
			Me.Label25.TabIndex = 99
			Me.Label25.Text = "add. Exposure Time"
			Me._label__46.BackColor = SystemColors.Control
			Me._label__46.Cursor = Cursors.[Default]
			Me._label__46.Font = New Font("Microsoft Sans Serif", 9F)
			Me._label__46.ForeColor = SystemColors.ControlText
			Me._label__46.Location = New Point(370, 194)
			Me._label__46.Name = "_label__46"
			Me._label__46.RightToLeft = RightToLeft.No
			Me._label__46.Size = New Size(25, 17)
			Me._label__46.TabIndex = 98
			Me._label__46.Text = "ms"
			Me._tabSettings_TabPage7.Controls.Add(Me.chkJPEG)
			Me._tabSettings_TabPage7.Controls.Add(Me.cmbPDFReso)
			Me._tabSettings_TabPage7.Controls.Add(Me.Label42)
			Me._tabSettings_TabPage7.Controls.Add(Me.Label27)
			Me._tabSettings_TabPage7.Controls.Add(Me.Label94)
			Me._tabSettings_TabPage7.Location = New Point(4, 34)
			Me._tabSettings_TabPage7.Name = "_tabSettings_TabPage7"
			Me._tabSettings_TabPage7.Size = New Size(913, 268)
			Me._tabSettings_TabPage7.TabIndex = 7
			Me._tabSettings_TabPage7.Text = "PDF/JPG"
			Me.chkJPEG.BackColor = SystemColors.Control
			Me.chkJPEG.Cursor = Cursors.[Default]
			Me.chkJPEG.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.chkJPEG.ForeColor = SystemColors.ControlText
			Me.chkJPEG.Location = New Point(24, 160)
			Me.chkJPEG.Name = "chkJPEG"
			Me.chkJPEG.RightToLeft = RightToLeft.No
			Me.chkJPEG.Size = New Size(689, 41)
			Me.chkJPEG.TabIndex = 321
			Me.chkJPEG.Text = "Enable faster Processing of large Documents"
			Me.chkJPEG.UseVisualStyleBackColor = False
			Me.cmbPDFReso.BackColor = SystemColors.Window
			Me.cmbPDFReso.Cursor = Cursors.[Default]
			Me.cmbPDFReso.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.cmbPDFReso.ForeColor = SystemColors.WindowText
			Me.cmbPDFReso.Items.AddRange(New Object() { "100", "125", "150", "175", "200", "225", "250", "275", "300", "325", "350", "375", "400" })
			Me.cmbPDFReso.Location = New Point(24, 84)
			Me.cmbPDFReso.Name = "cmbPDFReso"
			Me.cmbPDFReso.RightToLeft = RightToLeft.No
			Me.cmbPDFReso.Size = New Size(185, 24)
			Me.cmbPDFReso.TabIndex = 127
			Me.Label42.BackColor = SystemColors.Control
			Me.Label42.Cursor = Cursors.[Default]
			Me.Label42.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label42.ForeColor = Color.Blue
			Me.Label42.Location = New Point(227, 104)
			Me.Label42.Name = "Label42"
			Me.Label42.RightToLeft = RightToLeft.No
			Me.Label42.Size = New Size(662, 33)
			Me.Label42.TabIndex = 198
			Me.Label42.Text = "might be necessary in order to accelerate the Exposure Process."
			Me.Label27.BackColor = SystemColors.Control
			Me.Label27.Cursor = Cursors.[Default]
			Me.Label27.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label27.ForeColor = Color.Blue
			Me.Label27.Location = New Point(231, 72)
			Me.Label27.Name = "Label27"
			Me.Label27.RightToLeft = RightToLeft.No
			Me.Label27.Size = New Size(634, 33)
			Me.Label27.TabIndex = 197
			Me.Label27.Text = "For large Documents lowering the Rendering Resolution"
			Me.Label94.BackColor = SystemColors.Control
			Me.Label94.Cursor = Cursors.[Default]
			Me.Label94.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.Label94.ForeColor = SystemColors.ControlText
			Me.Label94.Location = New Point(24, 68)
			Me.Label94.Name = "Label94"
			Me.Label94.RightToLeft = RightToLeft.No
			Me.Label94.Size = New Size(185, 17)
			Me.Label94.TabIndex = 128
			Me.Label94.Text = "PDF-Resolution"
			Me._tabSettings_TabPage8.Controls.Add(Me.Frame4)
			Me._tabSettings_TabPage8.Location = New Point(4, 34)
			Me._tabSettings_TabPage8.Name = "_tabSettings_TabPage8"
			Me._tabSettings_TabPage8.Size = New Size(913, 268)
			Me._tabSettings_TabPage8.TabIndex = 8
			Me._tabSettings_TabPage8.Text = "Pos/Neg"
			Me.Frame4.BackColor = SystemColors.Control
			Me.Frame4.Controls.Add(Me.radBlackFrame)
			Me.Frame4.Controls.Add(Me.radWhiteFrame)
			Me.Frame4.Controls.Add(Me.Label1)
			Me.Frame4.Controls.Add(Me.txtFrameWidth)
			Me.Frame4.Controls.Add(Me.chkFrame)
			Me.Frame4.Controls.Add(Me.chkInvers)
			Me.Frame4.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Frame4.ForeColor = SystemColors.ControlText
			Me.Frame4.Location = New Point(16, 21)
			Me.Frame4.Name = "Frame4"
			Me.Frame4.Padding = New Padding(0)
			Me.Frame4.RightToLeft = RightToLeft.No
			Me.Frame4.Size = New Size(223, 228)
			Me.Frame4.TabIndex = 199
			Me.Frame4.TabStop = False
			Me.Frame4.Text = "Inversion of Images and Frame"
			Me.radBlackFrame.CheckAlign = ContentAlignment.MiddleRight
			Me.radBlackFrame.Location = New Point(27, 196)
			Me.radBlackFrame.Name = "radBlackFrame"
			Me.radBlackFrame.Size = New Size(162, 20)
			Me.radBlackFrame.TabIndex = 309
			Me.radBlackFrame.TabStop = True
			Me.radBlackFrame.Text = "Black Frame"
			Me.radBlackFrame.UseVisualStyleBackColor = True
			Me.radWhiteFrame.CheckAlign = ContentAlignment.MiddleRight
			Me.radWhiteFrame.Location = New Point(27, 160)
			Me.radWhiteFrame.Name = "radWhiteFrame"
			Me.radWhiteFrame.Size = New Size(162, 20)
			Me.radWhiteFrame.TabIndex = 308
			Me.radWhiteFrame.TabStop = True
			Me.radWhiteFrame.Text = "White Frame"
			Me.radWhiteFrame.UseVisualStyleBackColor = True
			Me.Label1.BackColor = SystemColors.Control
			Me.Label1.Cursor = Cursors.[Default]
			Me.Label1.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label1.ForeColor = SystemColors.ControlText
			Me.Label1.Location = New Point(27, 120)
			Me.Label1.Name = "Label1"
			Me.Label1.RightToLeft = RightToLeft.No
			Me.Label1.Size = New Size(74, 13)
			Me.Label1.TabIndex = 307
			Me.Label1.Text = "Width"
			Me.chkFrame.BackColor = SystemColors.Control
			Me.chkFrame.CheckAlign = ContentAlignment.MiddleRight
			Me.chkFrame.Cursor = Cursors.[Default]
			Me.chkFrame.ForeColor = SystemColors.ControlText
			Me.chkFrame.Location = New Point(24, 80)
			Me.chkFrame.Name = "chkFrame"
			Me.chkFrame.RightToLeft = RightToLeft.No
			Me.chkFrame.Size = New Size(165, 21)
			Me.chkFrame.TabIndex = 201
			Me.chkFrame.Text = "Draw Frame"
			Me.chkFrame.UseVisualStyleBackColor = False
			Me.chkInvers.BackColor = SystemColors.Control
			Me.chkInvers.CheckAlign = ContentAlignment.MiddleRight
			Me.chkInvers.Cursor = Cursors.[Default]
			Me.chkInvers.ForeColor = SystemColors.ControlText
			Me.chkInvers.Location = New Point(24, 44)
			Me.chkInvers.Name = "chkInvers"
			Me.chkInvers.RightToLeft = RightToLeft.No
			Me.chkInvers.Size = New Size(165, 21)
			Me.chkInvers.TabIndex = 200
			Me.chkInvers.Text = "Invert Images"
			Me.chkInvers.UseVisualStyleBackColor = False
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdDownRecords)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdTrailerDown)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdHeaderDown)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdHeaderUp)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdTrailerUp)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdUpRecords)
			Me._tabSettings_TabPage9.Controls.Add(Me.lstTrailer)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdClearLogPath)
			Me._tabSettings_TabPage9.Controls.Add(Me.lstRecords)
			Me._tabSettings_TabPage9.Controls.Add(Me.lstHeader)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmbDelimiter)
			Me._tabSettings_TabPage9.Controls.Add(Me.cmdSetLogPath)
			Me._tabSettings_TabPage9.Controls.Add(Me.chkUseLogFile)
			Me._tabSettings_TabPage9.Controls.Add(Me._Label_2)
			Me._tabSettings_TabPage9.Controls.Add(Me.lblLogFile)
			Me._tabSettings_TabPage9.Controls.Add(Me._Label_1)
			Me._tabSettings_TabPage9.Controls.Add(Me._Label_3)
			Me._tabSettings_TabPage9.Controls.Add(Me._Label_4)
			Me._tabSettings_TabPage9.Controls.Add(Me._Label_5)
			Me._tabSettings_TabPage9.Location = New Point(4, 34)
			Me._tabSettings_TabPage9.Name = "_tabSettings_TabPage9"
			Me._tabSettings_TabPage9.Size = New Size(913, 268)
			Me._tabSettings_TabPage9.TabIndex = 9
			Me._tabSettings_TabPage9.Text = "Log"
			Me.cmdDownRecords.BackColor = SystemColors.Control
			Me.cmdDownRecords.Cursor = Cursors.[Default]
			Me.cmdDownRecords.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdDownRecords.ForeColor = SystemColors.ControlText
			Me.cmdDownRecords.Location = New Point(839, 240)
			Me.cmdDownRecords.Name = "cmdDownRecords"
			Me.cmdDownRecords.RightToLeft = RightToLeft.No
			Me.cmdDownRecords.Size = New Size(38, 23)
			Me.cmdDownRecords.TabIndex = 263
			Me.cmdDownRecords.Text = "Dn"
			Me.cmdDownRecords.UseVisualStyleBackColor = False
			Me.cmdTrailerDown.BackColor = SystemColors.Control
			Me.cmdTrailerDown.Cursor = Cursors.[Default]
			Me.cmdTrailerDown.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdTrailerDown.ForeColor = SystemColors.ControlText
			Me.cmdTrailerDown.Location = New Point(531, 240)
			Me.cmdTrailerDown.Name = "cmdTrailerDown"
			Me.cmdTrailerDown.RightToLeft = RightToLeft.No
			Me.cmdTrailerDown.Size = New Size(38, 23)
			Me.cmdTrailerDown.TabIndex = 262
			Me.cmdTrailerDown.Text = "Dn"
			Me.cmdTrailerDown.UseVisualStyleBackColor = False
			Me.cmdHeaderDown.BackColor = SystemColors.Control
			Me.cmdHeaderDown.Cursor = Cursors.[Default]
			Me.cmdHeaderDown.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdHeaderDown.ForeColor = SystemColors.ControlText
			Me.cmdHeaderDown.Location = New Point(250, 240)
			Me.cmdHeaderDown.Name = "cmdHeaderDown"
			Me.cmdHeaderDown.RightToLeft = RightToLeft.No
			Me.cmdHeaderDown.Size = New Size(38, 23)
			Me.cmdHeaderDown.TabIndex = 261
			Me.cmdHeaderDown.Text = "Dn"
			Me.cmdHeaderDown.UseVisualStyleBackColor = False
			Me.cmdHeaderUp.BackColor = SystemColors.Control
			Me.cmdHeaderUp.Cursor = Cursors.[Default]
			Me.cmdHeaderUp.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdHeaderUp.ForeColor = SystemColors.ControlText
			Me.cmdHeaderUp.Location = New Point(250, 140)
			Me.cmdHeaderUp.Name = "cmdHeaderUp"
			Me.cmdHeaderUp.RightToLeft = RightToLeft.No
			Me.cmdHeaderUp.Size = New Size(38, 23)
			Me.cmdHeaderUp.TabIndex = 260
			Me.cmdHeaderUp.Text = "Up"
			Me.cmdHeaderUp.UseVisualStyleBackColor = False
			Me.cmdTrailerUp.BackColor = SystemColors.Control
			Me.cmdTrailerUp.Cursor = Cursors.[Default]
			Me.cmdTrailerUp.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdTrailerUp.ForeColor = SystemColors.ControlText
			Me.cmdTrailerUp.Location = New Point(532, 140)
			Me.cmdTrailerUp.Name = "cmdTrailerUp"
			Me.cmdTrailerUp.RightToLeft = RightToLeft.No
			Me.cmdTrailerUp.Size = New Size(38, 23)
			Me.cmdTrailerUp.TabIndex = 259
			Me.cmdTrailerUp.Text = "Up"
			Me.cmdTrailerUp.UseVisualStyleBackColor = False
			Me.cmdUpRecords.BackColor = SystemColors.Control
			Me.cmdUpRecords.Cursor = Cursors.[Default]
			Me.cmdUpRecords.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdUpRecords.ForeColor = SystemColors.ControlText
			Me.cmdUpRecords.Location = New Point(840, 140)
			Me.cmdUpRecords.Name = "cmdUpRecords"
			Me.cmdUpRecords.RightToLeft = RightToLeft.No
			Me.cmdUpRecords.Size = New Size(38, 23)
			Me.cmdUpRecords.TabIndex = 258
			Me.cmdUpRecords.Text = "Up"
			Me.cmdUpRecords.UseVisualStyleBackColor = False
			Me.lstTrailer.BackColor = SystemColors.Window
			Me.lstTrailer.Cursor = Cursors.[Default]
			Me.lstTrailer.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.lstTrailer.ForeColor = SystemColors.WindowText
			Me.lstTrailer.Items.AddRange(New Object() { "first filename on film", "last filename on film", "# of exposed frames", "# of exposed images", "# of Lev 2 documents", "# of Lev 3 folders", "Date", "Date/Time" })
			Me.lstTrailer.Location = New Point(303, 140)
			Me.lstTrailer.Name = "lstTrailer"
			Me.lstTrailer.RightToLeft = RightToLeft.No
			Me.lstTrailer.Size = New Size(225, 123)
			Me.lstTrailer.TabIndex = 256
			Me.cmdClearLogPath.BackColor = SystemColors.Control
			Me.cmdClearLogPath.Cursor = Cursors.[Default]
			Me.cmdClearLogPath.ForeColor = SystemColors.ControlText
			Me.cmdClearLogPath.Location = New Point(144, 51)
			Me.cmdClearLogPath.Name = "cmdClearLogPath"
			Me.cmdClearLogPath.RightToLeft = RightToLeft.No
			Me.cmdClearLogPath.Size = New Size(32, 32)
			Me.cmdClearLogPath.TabIndex = 170
			Me.cmdClearLogPath.Text = "c"
			Me.cmdClearLogPath.UseVisualStyleBackColor = False
			Me.lstRecords.BackColor = SystemColors.Window
			Me.lstRecords.Cursor = Cursors.[Default]
			Me.lstRecords.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.lstRecords.ForeColor = SystemColors.WindowText
			Me.lstRecords.Items.AddRange(New Object() { "Filename", "Full Filename", "Documentsize", "Extension", "BLIP-Positions", "Linear Frame Pos", "Filesize", "Modification-Date", "Page Number" })
			Me.lstRecords.Location = New Point(587, 140)
			Me.lstRecords.Name = "lstRecords"
			Me.lstRecords.RightToLeft = RightToLeft.No
			Me.lstRecords.Size = New Size(249, 123)
			Me.lstRecords.TabIndex = 164
			Me.lstHeader.BackColor = SystemColors.Window
			Me.lstHeader.Cursor = Cursors.[Default]
			Me.lstHeader.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.lstHeader.ForeColor = SystemColors.WindowText
			Me.lstHeader.Items.AddRange(New Object() { "Rollnumber", "Date", "Date/Time", "User", "Computer" })
			Me.lstHeader.Location = New Point(21, 140)
			Me.lstHeader.Name = "lstHeader"
			Me.lstHeader.RightToLeft = RightToLeft.No
			Me.lstHeader.Size = New Size(225, 123)
			Me.lstHeader.TabIndex = 162
			Me.cmbDelimiter.BackColor = SystemColors.Window
			Me.cmbDelimiter.Cursor = Cursors.[Default]
			Me.cmbDelimiter.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbDelimiter.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.cmbDelimiter.ForeColor = SystemColors.WindowText
			Me.cmbDelimiter.Items.AddRange(New Object() { ",", ";" })
			Me.cmbDelimiter.Location = New Point(144, 91)
			Me.cmbDelimiter.Name = "cmbDelimiter"
			Me.cmbDelimiter.RightToLeft = RightToLeft.No
			Me.cmbDelimiter.Size = New Size(181, 24)
			Me.cmbDelimiter.TabIndex = 161
			Me.cmdSetLogPath.BackColor = SystemColors.Control
			Me.cmdSetLogPath.Cursor = Cursors.[Default]
			Me.cmdSetLogPath.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdSetLogPath.ForeColor = SystemColors.ControlText
			Me.cmdSetLogPath.Location = New Point(841, 52)
			Me.cmdSetLogPath.Name = "cmdSetLogPath"
			Me.cmdSetLogPath.RightToLeft = RightToLeft.No
			Me.cmdSetLogPath.Size = New Size(38, 23)
			Me.cmdSetLogPath.TabIndex = 159
			Me.cmdSetLogPath.Text = "..."
			Me.cmdSetLogPath.UseVisualStyleBackColor = False
			Me.chkUseLogFile.BackColor = SystemColors.Control
			Me.chkUseLogFile.CheckAlign = ContentAlignment.MiddleRight
			Me.chkUseLogFile.Cursor = Cursors.[Default]
			Me.chkUseLogFile.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.chkUseLogFile.ForeColor = SystemColors.ControlText
			Me.chkUseLogFile.Location = New Point(21, 20)
			Me.chkUseLogFile.Name = "chkUseLogFile"
			Me.chkUseLogFile.RightToLeft = RightToLeft.No
			Me.chkUseLogFile.Size = New Size(182, 17)
			Me.chkUseLogFile.TabIndex = 158
			Me.chkUseLogFile.Text = "Write Protocol"
			Me.chkUseLogFile.UseVisualStyleBackColor = False
			Me._Label_2.BackColor = SystemColors.Control
			Me._Label_2.Cursor = Cursors.[Default]
			Me._Label_2.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label_2.ForeColor = SystemColors.ControlText
			Me._Label_2.Location = New Point(300, 123)
			Me._Label_2.Name = "_Label_2"
			Me._Label_2.RightToLeft = RightToLeft.No
			Me._Label_2.Size = New Size(85, 17)
			Me._Label_2.TabIndex = 254
			Me._Label_2.Text = "Trailer"
			Me.lblLogFile.BorderStyle = BorderStyle.Fixed3D
			Me.lblLogFile.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.lblLogFile.Location = New Point(184, 55)
			Me.lblLogFile.Name = "lblLogFile"
			Me.lblLogFile.Size = New Size(651, 23)
			Me.lblLogFile.TabIndex = 178
			Me._Label_1.BackColor = SystemColors.Control
			Me._Label_1.Cursor = Cursors.[Default]
			Me._Label_1.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label_1.ForeColor = SystemColors.ControlText
			Me._Label_1.Location = New Point(584, 123)
			Me._Label_1.Name = "_Label_1"
			Me._Label_1.RightToLeft = RightToLeft.No
			Me._Label_1.Size = New Size(85, 17)
			Me._Label_1.TabIndex = 165
			Me._Label_1.Text = "Records"
			Me._Label_3.BackColor = SystemColors.Control
			Me._Label_3.Cursor = Cursors.[Default]
			Me._Label_3.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label_3.ForeColor = SystemColors.ControlText
			Me._Label_3.Location = New Point(20, 123)
			Me._Label_3.Name = "_Label_3"
			Me._Label_3.RightToLeft = RightToLeft.No
			Me._Label_3.Size = New Size(85, 17)
			Me._Label_3.TabIndex = 163
			Me._Label_3.Text = "Header"
			Me._Label_4.BackColor = SystemColors.Control
			Me._Label_4.Cursor = Cursors.[Default]
			Me._Label_4.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label_4.ForeColor = SystemColors.ControlText
			Me._Label_4.Location = New Point(21, 92)
			Me._Label_4.Name = "_Label_4"
			Me._Label_4.RightToLeft = RightToLeft.No
			Me._Label_4.Size = New Size(88, 17)
			Me._Label_4.TabIndex = 160
			Me._Label_4.Text = "Separator"
			Me._Label_5.BackColor = SystemColors.Control
			Me._Label_5.Cursor = Cursors.[Default]
			Me._Label_5.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label_5.ForeColor = SystemColors.ControlText
			Me._Label_5.Location = New Point(21, 56)
			Me._Label_5.Name = "_Label_5"
			Me._Label_5.RightToLeft = RightToLeft.No
			Me._Label_5.Size = New Size(109, 17)
			Me._Label_5.TabIndex = 157
			Me._Label_5.Text = "Directory"
			Me._tabSettings_TabPage10.Controls.Add(Me.Image2)
			Me._tabSettings_TabPage10.Location = New Point(4, 34)
			Me._tabSettings_TabPage10.Name = "_tabSettings_TabPage10"
			Me._tabSettings_TabPage10.Size = New Size(913, 268)
			Me._tabSettings_TabPage10.TabIndex = 10
			Me._tabSettings_TabPage10.Text = "Tab 10"
			Me.Image2.Cursor = Cursors.[Default]
			Me.Image2.Image = Resources.Startbild
			Me.Image2.Location = New Point(3, 72)
			Me.Image2.Name = "Image2"
			Me.Image2.Size = New Size(889, 137)
			Me.Image2.SizeMode = PictureBoxSizeMode.StretchImage
			Me.Image2.TabIndex = 0
			Me.Image2.TabStop = False
			Me.cmdNeu.BackColor = SystemColors.Control
			Me.cmdNeu.Cursor = Cursors.[Default]
			Me.cmdNeu.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdNeu.ForeColor = SystemColors.ControlText
			Me.cmdNeu.Location = New Point(384, 216)
			Me.cmdNeu.Name = "cmdNeu"
			Me.cmdNeu.RightToLeft = RightToLeft.No
			Me.cmdNeu.Size = New Size(157, 57)
			Me.cmdNeu.TabIndex = 25
			Me.cmdNeu.Text = "Reexpose all Documents"
			Me.cmdNeu.UseVisualStyleBackColor = False
			Me.txtFilmNr.AcceptsReturn = True
			Me.txtFilmNr.BackColor = SystemColors.Window
			Me.txtFilmNr.Cursor = Cursors.IBeam
			Me.txtFilmNr.ForeColor = Color.Red
			Me.txtFilmNr.Location = New Point(88, 304)
			Me.txtFilmNr.MaxLength = 0
			Me.txtFilmNr.Name = "txtFilmNr"
			Me.txtFilmNr.[ReadOnly] = True
			Me.txtFilmNr.RightToLeft = RightToLeft.No
			Me.txtFilmNr.Size = New Size(81, 20)
			Me.txtFilmNr.TabIndex = 23
			Me.txtFilmNr.TextAlign = HorizontalAlignment.Right
			Me.txtPage.AcceptsReturn = True
			Me.txtPage.BackColor = SystemColors.Window
			Me.txtPage.Cursor = Cursors.IBeam
			Me.txtPage.Font = New Font("Arial", 8.25F)
			Me.txtPage.ForeColor = SystemColors.WindowText
			Me.txtPage.Location = New Point(752, 338)
			Me.txtPage.MaxLength = 0
			Me.txtPage.Name = "txtPage"
			Me.txtPage.[ReadOnly] = True
			Me.txtPage.RightToLeft = RightToLeft.No
			Me.txtPage.Size = New Size(57, 20)
			Me.txtPage.TabIndex = 21
			Me.txtPage.TextAlign = HorizontalAlignment.Right
			Me.cmdNewRoll.BackColor = SystemColors.Control
			Me.cmdNewRoll.Cursor = Cursors.[Default]
			Me.cmdNewRoll.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdNewRoll.ForeColor = SystemColors.ControlText
			Me.cmdNewRoll.Location = New Point(552, 216)
			Me.cmdNewRoll.Name = "cmdNewRoll"
			Me.cmdNewRoll.RightToLeft = RightToLeft.No
			Me.cmdNewRoll.Size = New Size(157, 57)
			Me.cmdNewRoll.TabIndex = 20
			Me.cmdNewRoll.Text = "New Roll"
			Me.cmdNewRoll.UseVisualStyleBackColor = False
			Me.txtRestAufnahmen.AcceptsReturn = True
			Me.txtRestAufnahmen.BackColor = SystemColors.Window
			Me.txtRestAufnahmen.Cursor = Cursors.IBeam
			Me.txtRestAufnahmen.ForeColor = Color.Red
			Me.txtRestAufnahmen.Location = New Point(198, 342)
			Me.txtRestAufnahmen.MaxLength = 0
			Me.txtRestAufnahmen.Name = "txtRestAufnahmen"
			Me.txtRestAufnahmen.[ReadOnly] = True
			Me.txtRestAufnahmen.RightToLeft = RightToLeft.No
			Me.txtRestAufnahmen.Size = New Size(81, 20)
			Me.txtRestAufnahmen.TabIndex = 19
			Me.txtRestAufnahmen.TextAlign = HorizontalAlignment.Right
			Me.cmbTemplate.BackColor = SystemColors.Window
			Me.cmbTemplate.Cursor = Cursors.[Default]
			Me.cmbTemplate.DropDownStyle = ComboBoxStyle.DropDownList
			Me.cmbTemplate.Font = New Font("Arial", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmbTemplate.ForeColor = SystemColors.WindowText
			Me.cmbTemplate.Location = New Point(88, 414)
			Me.cmbTemplate.Name = "cmbTemplate"
			Me.cmbTemplate.RightToLeft = RightToLeft.No
			Me.cmbTemplate.Size = New Size(285, 24)
			Me.cmbTemplate.TabIndex = 5
			Me._Label1_8.BackColor = SystemColors.Control
			Me._Label1_8.Cursor = Cursors.[Default]
			Me._Label1_8.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label1_8.ForeColor = SystemColors.ControlText
			Me._Label1_8.Location = New Point(104, 288)
			Me._Label1_8.Name = "_Label1_8"
			Me._Label1_8.RightToLeft = RightToLeft.No
			Me._Label1_8.Size = New Size(65, 17)
			Me._Label1_8.TabIndex = 333
			Me._Label1_8.Text = "internal"
			Me._Label1_7.BackColor = SystemColors.Control
			Me._Label1_7.Cursor = Cursors.[Default]
			Me._Label1_7.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label1_7.ForeColor = SystemColors.ControlText
			Me._Label1_7.Location = New Point(244, 288)
			Me._Label1_7.Name = "_Label1_7"
			Me._Label1_7.RightToLeft = RightToLeft.No
			Me._Label1_7.Size = New Size(86, 17)
			Me._Label1_7.TabIndex = 332
			Me._Label1_7.Text = "on Film"
			Me.Label34.BackColor = SystemColors.Control
			Me.Label34.Cursor = Cursors.[Default]
			Me.Label34.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label34.ForeColor = SystemColors.ControlText
			Me.Label34.Location = New Point(555, 344)
			Me.Label34.Name = "Label34"
			Me.Label34.RightToLeft = RightToLeft.No
			Me.Label34.Size = New Size(175, 17)
			Me.Label34.TabIndex = 292
			Me.Label34.Text = "last filmed document"
			Me.txtLastDocument.Font = New Font("Arial", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.txtLastDocument.Location = New Point(553, 362)
			Me.txtLastDocument.Name = "txtLastDocument"
			Me.txtLastDocument.Size = New Size(340, 20)
			Me.txtLastDocument.TabIndex = 179
			Me.txtLastDocument.TextAlign = HorizontalAlignment.Right
			Me._Label1_1.BackColor = SystemColors.Control
			Me._Label1_1.Cursor = Cursors.[Default]
			Me._Label1_1.Font = New Font("Arial", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._Label1_1.ForeColor = SystemColors.ControlText
			Me._Label1_1.Location = New Point(290, 343)
			Me._Label1_1.Name = "_Label1_1"
			Me._Label1_1.RightToLeft = RightToLeft.No
			Me._Label1_1.Size = New Size(21, 17)
			Me._Label1_1.TabIndex = 129
			Me._Label1_1.Text = "m"
			Me._Label1_3.BackColor = SystemColors.Control
			Me._Label1_3.Cursor = Cursors.[Default]
			Me._Label1_3.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label1_3.ForeColor = SystemColors.ControlText
			Me._Label1_3.Location = New Point(16, 378)
			Me._Label1_3.Name = "_Label1_3"
			Me._Label1_3.RightToLeft = RightToLeft.No
			Me._Label1_3.Size = New Size(69, 17)
			Me._Label1_3.TabIndex = 126
			Me._Label1_3.Text = "Head"
			Me._Label1_2.BackColor = SystemColors.Control
			Me._Label1_2.Cursor = Cursors.[Default]
			Me._Label1_2.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._Label1_2.ForeColor = SystemColors.ControlText
			Me._Label1_2.Location = New Point(16, 305)
			Me._Label1_2.Name = "_Label1_2"
			Me._Label1_2.RightToLeft = RightToLeft.No
			Me._Label1_2.Size = New Size(69, 17)
			Me._Label1_2.TabIndex = 24
			Me._Label1_2.Text = "Roll No"
			Me.Label15.BackColor = SystemColors.Control
			Me.Label15.Cursor = Cursors.[Default]
			Me.Label15.ForeColor = SystemColors.ControlText
			Me.Label15.Location = New Point(948, 272)
			Me.Label15.Name = "Label15"
			Me.Label15.RightToLeft = RightToLeft.No
			Me.Label15.Size = New Size(33, 17)
			Me.Label15.TabIndex = 22
			Me.Label15.Text = "Seite"
			Me.Label15.Visible = False
			Me._Label1_5.BackColor = SystemColors.Control
			Me._Label1_5.Cursor = Cursors.[Default]
			Me._Label1_5.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label1_5.ForeColor = SystemColors.ControlText
			Me._Label1_5.Location = New Point(16, 344)
			Me._Label1_5.Name = "_Label1_5"
			Me._Label1_5.RightToLeft = RightToLeft.No
			Me._Label1_5.Size = New Size(180, 21)
			Me._Label1_5.TabIndex = 18
			Me._Label1_5.Text = "Free Film Len"
			Me._Label13_0.BackColor = SystemColors.Control
			Me._Label13_0.Cursor = Cursors.[Default]
			Me._Label13_0.ForeColor = SystemColors.ControlText
			Me._Label13_0.Location = New Point(948, 236)
			Me._Label13_0.Name = "_Label13_0"
			Me._Label13_0.RightToLeft = RightToLeft.No
			Me._Label13_0.Size = New Size(105, 12)
			Me._Label13_0.TabIndex = 17
			Me._Label13_0.Text = "Letzte Aufnahme"
			Me._Label13_0.Visible = False
			Me.lblLevel.BackColor = SystemColors.Control
			Me.lblLevel.BorderStyle = BorderStyle.Fixed3D
			Me.lblLevel.Cursor = Cursors.[Default]
			Me.lblLevel.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.lblLevel.ForeColor = Color.Red
			Me.lblLevel.Location = New Point(88, 169)
			Me.lblLevel.Name = "lblLevel"
			Me.lblLevel.RightToLeft = RightToLeft.No
			Me.lblLevel.Size = New Size(69, 28)
			Me.lblLevel.TabIndex = 16
			Me.lblLevel.TextAlign = ContentAlignment.TopRight
			Me._label__7.BackColor = SystemColors.Control
			Me._label__7.Cursor = Cursors.[Default]
			Me._label__7.Font = New Font("Arial", 11.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me._label__7.ForeColor = SystemColors.ControlText
			Me._label__7.Location = New Point(22, 176)
			Me._label__7.Name = "_label__7"
			Me._label__7.RightToLeft = RightToLeft.No
			Me._label__7.Size = New Size(57, 16)
			Me._label__7.TabIndex = 15
			Me._label__7.Text = "Level"
			Me.Label7.BackColor = SystemColors.Control
			Me.Label7.Cursor = Cursors.[Default]
			Me.Label7.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label7.ForeColor = Color.Red
			Me.Label7.Location = New Point(144, 4)
			Me.Label7.Name = "Label7"
			Me.Label7.RightToLeft = RightToLeft.No
			Me.Label7.Size = New Size(777, 21)
			Me.Label7.TabIndex = 8
			Me.Label7.Text = "The shown Metrics are not representative!"
			Me._Label1_6.BackColor = SystemColors.Control
			Me._Label1_6.Cursor = Cursors.[Default]
			Me._Label1_6.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me._Label1_6.ForeColor = SystemColors.ControlText
			Me._Label1_6.Location = New Point(16, 416)
			Me._Label1_6.Name = "_Label1_6"
			Me._Label1_6.RightToLeft = RightToLeft.No
			Me._Label1_6.Size = New Size(73, 17)
			Me._Label1_6.TabIndex = 7
			Me._Label1_6.Text = "Job"
			Me.lblPos.BackColor = SystemColors.Control
			Me.lblPos.BorderStyle = BorderStyle.Fixed3D
			Me.lblPos.Cursor = Cursors.[Default]
			Me.lblPos.ForeColor = Color.Blue
			Me.lblPos.Location = New Point(40, 4)
			Me.lblPos.Name = "lblPos"
			Me.lblPos.RightToLeft = RightToLeft.No
			Me.lblPos.Size = New Size(69, 17)
			Me.lblPos.TabIndex = 1
			Me.lblPos.Text = "0"
			Me.lblPos.TextAlign = ContentAlignment.TopRight
			Me._Label1_0.BackColor = SystemColors.Control
			Me._Label1_0.Cursor = Cursors.[Default]
			Me._Label1_0.ForeColor = SystemColors.ControlText
			Me._Label1_0.Location = New Point(12, 4)
			Me._Label1_0.Name = "_Label1_0"
			Me._Label1_0.RightToLeft = RightToLeft.No
			Me._Label1_0.Size = New Size(25, 17)
			Me._Label1_0.TabIndex = 0
			Me._Label1_0.Text = "Pos"
			Me._lblAnno_0.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_0.Location = New Point(42, 139)
			Me._lblAnno_0.Name = "_lblAnno_0"
			Me._lblAnno_0.Size = New Size(120, 20)
			Me._lblAnno_0.TabIndex = 335
			Me._lblAnno_1.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_1.Location = New Point(194, 137)
			Me._lblAnno_1.Name = "_lblAnno_1"
			Me._lblAnno_1.Size = New Size(120, 20)
			Me._lblAnno_1.TabIndex = 336
			Me._lblAnno_2.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_2.Location = New Point(342, 139)
			Me._lblAnno_2.Name = "_lblAnno_2"
			Me._lblAnno_2.Size = New Size(120, 20)
			Me._lblAnno_2.TabIndex = 337
			Me._lblAnno_3.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_3.Location = New Point(486, 139)
			Me._lblAnno_3.Name = "_lblAnno_3"
			Me._lblAnno_3.Size = New Size(120, 20)
			Me._lblAnno_3.TabIndex = 338
			Me._lblAnno_4.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_4.Location = New Point(633, 139)
			Me._lblAnno_4.Name = "_lblAnno_4"
			Me._lblAnno_4.Size = New Size(120, 20)
			Me._lblAnno_4.TabIndex = 339
			Me._lblAnno_5.Font = New Font("Courier New", 6F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me._lblAnno_5.Location = New Point(790, 139)
			Me._lblAnno_5.Name = "_lblAnno_5"
			Me._lblAnno_5.Size = New Size(120, 20)
			Me._lblAnno_5.TabIndex = 340
			Me.cmdStart.BackColor = Color.FromArgb(192, 255, 192)
			Me.cmdStart.Cursor = Cursors.[Default]
			Me.cmdStart.Font = New Font("Arial", 15F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdStart.ForeColor = SystemColors.ControlText
			Me.cmdStart.Location = New Point(19, 216)
			Me.cmdStart.Name = "cmdStart"
			Me.cmdStart.RightToLeft = RightToLeft.No
			Me.cmdStart.Size = New Size(170, 57)
			Me.cmdStart.TabIndex = 341
			Me.cmdStart.Text = "Start Exposure"
			Me.cmdStart.UseVisualStyleBackColor = False
			Me.cmdCancel.BackColor = Color.FromArgb(255, 192, 192)
			Me.cmdCancel.Cursor = Cursors.[Default]
			Me.cmdCancel.Font = New Font("Arial", 15F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdCancel.ForeColor = SystemColors.ControlText
			Me.cmdCancel.Location = New Point(716, 216)
			Me.cmdCancel.Name = "cmdCancel"
			Me.cmdCancel.RightToLeft = RightToLeft.No
			Me.cmdCancel.Size = New Size(183, 57)
			Me.cmdCancel.TabIndex = 342
			Me.cmdCancel.Text = "Back"
			Me.cmdCancel.UseVisualStyleBackColor = False
			Me.cmdNewTemplate.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdNewTemplate.Location = New Point(553, 393)
			Me.cmdNewTemplate.Name = "cmdNewTemplate"
			Me.cmdNewTemplate.Size = New Size(156, 52)
			Me.cmdNewTemplate.TabIndex = 343
			Me.cmdNewTemplate.Text = "New Template"
			Me.cmdNewTemplate.UseVisualStyleBackColor = True
			Me.cmdSaveTemplate.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdSaveTemplate.Location = New Point(385, 393)
			Me.cmdSaveTemplate.Name = "cmdSaveTemplate"
			Me.cmdSaveTemplate.Size = New Size(156, 52)
			Me.cmdSaveTemplate.TabIndex = 344
			Me.cmdSaveTemplate.Text = "Save Template"
			Me.cmdSaveTemplate.UseVisualStyleBackColor = True
			Me.cmdSetLastDoc.Font = New Font("Microsoft Sans Serif", 9.75F)
			Me.cmdSetLastDoc.Location = New Point(815, 335)
			Me.cmdSetLastDoc.Name = "cmdSetLastDoc"
			Me.cmdSetLastDoc.Size = New Size(78, 25)
			Me.cmdSetLastDoc.TabIndex = 345
			Me.cmdSetLastDoc.Text = "modify"
			Me.cmdSetLastDoc.UseVisualStyleBackColor = True
			Me.cmdFirst.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdFirst.Location = New Point(212, 169)
			Me.cmdFirst.Name = "cmdFirst"
			Me.cmdFirst.Size = New Size(69, 28)
			Me.cmdFirst.TabIndex = 346
			Me.cmdFirst.Text = "| <<"
			Me.cmdFirst.UseVisualStyleBackColor = True
			Me.cmdPagePrevious.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdPagePrevious.Location = New Point(296, 169)
			Me.cmdPagePrevious.Name = "cmdPagePrevious"
			Me.cmdPagePrevious.Size = New Size(69, 28)
			Me.cmdPagePrevious.TabIndex = 347
			Me.cmdPagePrevious.Text = "<<"
			Me.cmdPagePrevious.UseVisualStyleBackColor = True
			Me.cmdPrevious.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdPrevious.Location = New Point(379, 169)
			Me.cmdPrevious.Name = "cmdPrevious"
			Me.cmdPrevious.Size = New Size(69, 28)
			Me.cmdPrevious.TabIndex = 348
			Me.cmdPrevious.Text = "<"
			Me.cmdPrevious.UseVisualStyleBackColor = True
			Me.cmdNext.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdNext.Location = New Point(468, 169)
			Me.cmdNext.Name = "cmdNext"
			Me.cmdNext.Size = New Size(69, 28)
			Me.cmdNext.TabIndex = 349
			Me.cmdNext.Text = ">"
			Me.cmdNext.UseVisualStyleBackColor = True
			Me.cmdPageNext.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdPageNext.Location = New Point(558, 169)
			Me.cmdPageNext.Name = "cmdPageNext"
			Me.cmdPageNext.Size = New Size(69, 28)
			Me.cmdPageNext.TabIndex = 350
			Me.cmdPageNext.Text = ">>"
			Me.cmdPageNext.UseVisualStyleBackColor = True
			Me.cmdLast.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdLast.Location = New Point(644, 169)
			Me.cmdLast.Name = "cmdLast"
			Me.cmdLast.Size = New Size(69, 28)
			Me.cmdLast.TabIndex = 351
			Me.cmdLast.Text = ">> |"
			Me.cmdLast.UseVisualStyleBackColor = True
			Me.OpenFileDialog1.FileName = "OpenFileDialog1"
			MyBase.AutoScaleDimensions = New SizeF(6F, 13F)
			MyBase.AutoScaleMode = AutoScaleMode.Font
			Me.BackColor = SystemColors.Control
			MyBase.ClientSize = New Size(916, 769)
			MyBase.Controls.Add(Me._ShpFilmed_0)
			MyBase.Controls.Add(Me._ShpFilmed_1)
			MyBase.Controls.Add(Me._ShpFilmed_2)
			MyBase.Controls.Add(Me._ShpFilmed_3)
			MyBase.Controls.Add(Me._ShpFilmed_4)
			MyBase.Controls.Add(Me._ShpFilmed_5)
			MyBase.Controls.Add(Me._ShpBLIP_0)
			MyBase.Controls.Add(Me._ShpBLIP_1)
			MyBase.Controls.Add(Me._ShpBLIP_2)
			MyBase.Controls.Add(Me._ShpBLIP_3)
			MyBase.Controls.Add(Me._ShpBLIP_4)
			MyBase.Controls.Add(Me._ShpBLIP_5)
			MyBase.Controls.Add(Me.cmdLast)
			MyBase.Controls.Add(Me.cmdPageNext)
			MyBase.Controls.Add(Me.cmdNext)
			MyBase.Controls.Add(Me.cmdPrevious)
			MyBase.Controls.Add(Me.cmdPagePrevious)
			MyBase.Controls.Add(Me.cmdFirst)
			MyBase.Controls.Add(Me.cmdSetLastDoc)
			MyBase.Controls.Add(Me.cmdSaveTemplate)
			MyBase.Controls.Add(Me.cmdNewTemplate)
			MyBase.Controls.Add(Me.cmdCancel)
			MyBase.Controls.Add(Me.cmdStart)
			MyBase.Controls.Add(Me._lblAnno_5)
			MyBase.Controls.Add(Me._lblAnno_4)
			MyBase.Controls.Add(Me._lblAnno_3)
			MyBase.Controls.Add(Me._lblAnno_2)
			MyBase.Controls.Add(Me._lblAnno_1)
			MyBase.Controls.Add(Me._lblAnno_0)
			MyBase.Controls.Add(Me.txtFilmNrAufFilm)
			MyBase.Controls.Add(Me.cmdFortsetzung)
			MyBase.Controls.Add(Me.cmdRefilm)
			MyBase.Controls.Add(Me.cmdCalcSpace)
			MyBase.Controls.Add(Me.cmdAbspulen)
			MyBase.Controls.Add(Me.cmdVorspann)
			MyBase.Controls.Add(Me.cmbKopf)
			MyBase.Controls.Add(Me._Picture1_6)
			MyBase.Controls.Add(Me.chkNoPreview)
			MyBase.Controls.Add(Me._Picture1_5)
			MyBase.Controls.Add(Me._Picture1_4)
			MyBase.Controls.Add(Me._Picture1_3)
			MyBase.Controls.Add(Me._Picture1_2)
			MyBase.Controls.Add(Me._Picture1_1)
			MyBase.Controls.Add(Me._Picture1_0)
			MyBase.Controls.Add(Me.tabSettings)
			MyBase.Controls.Add(Me.cmdNeu)
			MyBase.Controls.Add(Me.txtFilmNr)
			MyBase.Controls.Add(Me.txtPage)
			MyBase.Controls.Add(Me.cmdNewRoll)
			MyBase.Controls.Add(Me.txtRestAufnahmen)
			MyBase.Controls.Add(Me.cmbTemplate)
			MyBase.Controls.Add(Me._Label1_8)
			MyBase.Controls.Add(Me._Label1_7)
			MyBase.Controls.Add(Me.Label34)
			MyBase.Controls.Add(Me.txtLastDocument)
			MyBase.Controls.Add(Me._Label1_1)
			MyBase.Controls.Add(Me._Label1_3)
			MyBase.Controls.Add(Me._Label1_2)
			MyBase.Controls.Add(Me.Label15)
			MyBase.Controls.Add(Me._Label1_5)
			MyBase.Controls.Add(Me._Label13_0)
			MyBase.Controls.Add(Me.lblLevel)
			MyBase.Controls.Add(Me._label__7)
			MyBase.Controls.Add(Me.Label7)
			MyBase.Controls.Add(Me._Label1_6)
			MyBase.Controls.Add(Me.lblPos)
			MyBase.Controls.Add(Me._Label1_0)
			Me.Cursor = Cursors.[Default]
			MyBase.Location = New Point(4, 169)
			MyBase.Name = "frmFilmPreview"
			Me.RightToLeft = RightToLeft.No
			MyBase.StartPosition = FormStartPosition.Manual
			Me.Text = "Vorschau des Films"
			MyBase.TransparencyKey = Color.FromArgb(128, 64, 64)
			CType(Me._Picture1_6, ISupportInitialize).EndInit()
			CType(Me._Picture1_5, ISupportInitialize).EndInit()
			CType(Me._Picture1_4, ISupportInitialize).EndInit()
			CType(Me._Picture1_3, ISupportInitialize).EndInit()
			CType(Me._Picture1_2, ISupportInitialize).EndInit()
			CType(Me._Picture1_1, ISupportInitialize).EndInit()
			CType(Me._Picture1_0, ISupportInitialize).EndInit()
			Me.tabSettings.ResumeLayout(False)
			Me._tabSettings_TabPage0.ResumeLayout(False)
			Me._tabSettings_TabPage0.PerformLayout()
			Me.frbAusrichtung.ResumeLayout(False)
			Me.Frame1.ResumeLayout(False)
			Me.Frame9.ResumeLayout(False)
			Me.Frame9.PerformLayout()
			Me.Frame15.ResumeLayout(False)
			Me.Frame14.ResumeLayout(False)
			Me.Frame3.ResumeLayout(False)
			Me._tabSettings_TabPage1.ResumeLayout(False)
			Me.Frame8.ResumeLayout(False)
			Me.Frame8.PerformLayout()
			Me.frmPosition.ResumeLayout(False)
			Me.Frame2.ResumeLayout(False)
			Me._tabSettings_TabPage2.ResumeLayout(False)
			Me.frbFormat.ResumeLayout(False)
			Me.frbFormat.PerformLayout()
			Me._tabSettings_TabPage3.ResumeLayout(False)
			Me.tabFrames.ResumeLayout(False)
			Me._tabFrames_TabPage0.ResumeLayout(False)
			Me._tabFrames_TabPage0.PerformLayout()
			Me.Frame12.ResumeLayout(False)
			Me.Frame12.PerformLayout()
			Me._tabFrames_TabPage1.ResumeLayout(False)
			Me._tabFrames_TabPage2.ResumeLayout(False)
			Me._tabFrames_TabPage2.PerformLayout()
			Me._tabFrames_TabPage3.ResumeLayout(False)
			Me._tabSettings_TabPage4.ResumeLayout(False)
			Me._Frame__2.ResumeLayout(False)
			Me._Frame__2.PerformLayout()
			Me._Frame__5.ResumeLayout(False)
			Me._Frame__5.PerformLayout()
			Me._Frame__3.ResumeLayout(False)
			Me._Frame__3.PerformLayout()
			Me._Frame__4.ResumeLayout(False)
			Me._Frame__4.PerformLayout()
			Me._Frame__1.ResumeLayout(False)
			Me._Frame__1.PerformLayout()
			Me._Frame__0.ResumeLayout(False)
			Me._Frame__0.PerformLayout()
			Me._tabSettings_TabPage5.ResumeLayout(False)
			Me._tabSettings_TabPage5.PerformLayout()
			Me._tabSettings_TabPage6.ResumeLayout(False)
			Me._tabSettings_TabPage6.PerformLayout()
			Me.Frame7.ResumeLayout(False)
			Me.Frame7.PerformLayout()
			CType(Me.Image1, ISupportInitialize).EndInit()
			Me._tabSettings_TabPage7.ResumeLayout(False)
			Me._tabSettings_TabPage8.ResumeLayout(False)
			Me.Frame4.ResumeLayout(False)
			Me.Frame4.PerformLayout()
			Me._tabSettings_TabPage9.ResumeLayout(False)
			Me._tabSettings_TabPage10.ResumeLayout(False)
			CType(Me.Image2, ISupportInitialize).EndInit()
			MyBase.ResumeLayout(False)
			MyBase.PerformLayout()
		End Sub

		' Token: 0x170001A8 RID: 424
		' (get) Token: 0x06000768 RID: 1896 RVA: 0x00036203 File Offset: 0x00034403
		' (set) Token: 0x06000769 RID: 1897 RVA: 0x0003620B File Offset: 0x0003440B
		Friend Overridable Property _lblAnno_0 As Label

		' Token: 0x170001A9 RID: 425
		' (get) Token: 0x0600076A RID: 1898 RVA: 0x00036214 File Offset: 0x00034414
		' (set) Token: 0x0600076B RID: 1899 RVA: 0x0003621C File Offset: 0x0003441C
		Friend Overridable Property _lblAnno_1 As Label

		' Token: 0x170001AA RID: 426
		' (get) Token: 0x0600076C RID: 1900 RVA: 0x00036225 File Offset: 0x00034425
		' (set) Token: 0x0600076D RID: 1901 RVA: 0x0003622D File Offset: 0x0003442D
		Friend Overridable Property _lblAnno_2 As Label

		' Token: 0x170001AB RID: 427
		' (get) Token: 0x0600076E RID: 1902 RVA: 0x00036236 File Offset: 0x00034436
		' (set) Token: 0x0600076F RID: 1903 RVA: 0x0003623E File Offset: 0x0003443E
		Friend Overridable Property _lblAnno_3 As Label

		' Token: 0x170001AC RID: 428
		' (get) Token: 0x06000770 RID: 1904 RVA: 0x00036247 File Offset: 0x00034447
		' (set) Token: 0x06000771 RID: 1905 RVA: 0x0003624F File Offset: 0x0003444F
		Friend Overridable Property _lblAnno_4 As Label

		' Token: 0x170001AD RID: 429
		' (get) Token: 0x06000772 RID: 1906 RVA: 0x00036258 File Offset: 0x00034458
		' (set) Token: 0x06000773 RID: 1907 RVA: 0x00036260 File Offset: 0x00034460
		Friend Overridable Property _lblAnno_5 As Label

		' Token: 0x170001AE RID: 430
		' (get) Token: 0x06000774 RID: 1908 RVA: 0x00036269 File Offset: 0x00034469
		' (set) Token: 0x06000775 RID: 1909 RVA: 0x00036274 File Offset: 0x00034474
		Public Overridable Property cmdStart As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdStart
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdStart_Click
				Dim cmdStart As Button = Me._cmdStart
				If cmdStart IsNot Nothing Then
					RemoveHandler cmdStart.Click, value2
				End If
				Me._cmdStart = value
				cmdStart = Me._cmdStart
				If cmdStart IsNot Nothing Then
					AddHandler cmdStart.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001AF RID: 431
		' (get) Token: 0x06000776 RID: 1910 RVA: 0x000362B7 File Offset: 0x000344B7
		' (set) Token: 0x06000777 RID: 1911 RVA: 0x000362C0 File Offset: 0x000344C0
		Public Overridable Property cmdCancel As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdCancel
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdCancel_Click
				Dim cmdCancel As Button = Me._cmdCancel
				If cmdCancel IsNot Nothing Then
					RemoveHandler cmdCancel.Click, value2
				End If
				Me._cmdCancel = value
				cmdCancel = Me._cmdCancel
				If cmdCancel IsNot Nothing Then
					AddHandler cmdCancel.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B0 RID: 432
		' (get) Token: 0x06000778 RID: 1912 RVA: 0x00036303 File Offset: 0x00034503
		' (set) Token: 0x06000779 RID: 1913 RVA: 0x0003630C File Offset: 0x0003450C
		Friend Overridable Property cmdNewTemplate As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdNewTemplate
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdNewTemplate_Click
				Dim cmdNewTemplate As Button = Me._cmdNewTemplate
				If cmdNewTemplate IsNot Nothing Then
					RemoveHandler cmdNewTemplate.Click, value2
				End If
				Me._cmdNewTemplate = value
				cmdNewTemplate = Me._cmdNewTemplate
				If cmdNewTemplate IsNot Nothing Then
					AddHandler cmdNewTemplate.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B1 RID: 433
		' (get) Token: 0x0600077A RID: 1914 RVA: 0x0003634F File Offset: 0x0003454F
		' (set) Token: 0x0600077B RID: 1915 RVA: 0x00036358 File Offset: 0x00034558
		Friend Overridable Property cmdSaveTemplate As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdSaveTemplate
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdSaveTemplate_Click
				Dim cmdSaveTemplate As Button = Me._cmdSaveTemplate
				If cmdSaveTemplate IsNot Nothing Then
					RemoveHandler cmdSaveTemplate.Click, value2
				End If
				Me._cmdSaveTemplate = value
				cmdSaveTemplate = Me._cmdSaveTemplate
				If cmdSaveTemplate IsNot Nothing Then
					AddHandler cmdSaveTemplate.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B2 RID: 434
		' (get) Token: 0x0600077C RID: 1916 RVA: 0x0003639B File Offset: 0x0003459B
		' (set) Token: 0x0600077D RID: 1917 RVA: 0x000363A4 File Offset: 0x000345A4
		Friend Overridable Property cmdSetLastDoc As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdSetLastDoc
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdSetLastDoc_Click
				Dim cmdSetLastDoc As Button = Me._cmdSetLastDoc
				If cmdSetLastDoc IsNot Nothing Then
					RemoveHandler cmdSetLastDoc.Click, value2
				End If
				Me._cmdSetLastDoc = value
				cmdSetLastDoc = Me._cmdSetLastDoc
				If cmdSetLastDoc IsNot Nothing Then
					AddHandler cmdSetLastDoc.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B3 RID: 435
		' (get) Token: 0x0600077E RID: 1918 RVA: 0x000363E7 File Offset: 0x000345E7
		' (set) Token: 0x0600077F RID: 1919 RVA: 0x000363F0 File Offset: 0x000345F0
		Friend Overridable Property cmdFirst As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdFirst
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdFirst_Click
				Dim cmdFirst As Button = Me._cmdFirst
				If cmdFirst IsNot Nothing Then
					RemoveHandler cmdFirst.Click, value2
				End If
				Me._cmdFirst = value
				cmdFirst = Me._cmdFirst
				If cmdFirst IsNot Nothing Then
					AddHandler cmdFirst.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B4 RID: 436
		' (get) Token: 0x06000780 RID: 1920 RVA: 0x00036433 File Offset: 0x00034633
		' (set) Token: 0x06000781 RID: 1921 RVA: 0x0003643C File Offset: 0x0003463C
		Friend Overridable Property cmdPagePrevious As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdPagePrevious
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdPagePrevious_Click
				Dim cmdPagePrevious As Button = Me._cmdPagePrevious
				If cmdPagePrevious IsNot Nothing Then
					RemoveHandler cmdPagePrevious.Click, value2
				End If
				Me._cmdPagePrevious = value
				cmdPagePrevious = Me._cmdPagePrevious
				If cmdPagePrevious IsNot Nothing Then
					AddHandler cmdPagePrevious.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B5 RID: 437
		' (get) Token: 0x06000782 RID: 1922 RVA: 0x0003647F File Offset: 0x0003467F
		' (set) Token: 0x06000783 RID: 1923 RVA: 0x00036488 File Offset: 0x00034688
		Friend Overridable Property cmdPrevious As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdPrevious
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdPrevious_Click
				Dim cmdPrevious As Button = Me._cmdPrevious
				If cmdPrevious IsNot Nothing Then
					RemoveHandler cmdPrevious.Click, value2
				End If
				Me._cmdPrevious = value
				cmdPrevious = Me._cmdPrevious
				If cmdPrevious IsNot Nothing Then
					AddHandler cmdPrevious.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B6 RID: 438
		' (get) Token: 0x06000784 RID: 1924 RVA: 0x000364CB File Offset: 0x000346CB
		' (set) Token: 0x06000785 RID: 1925 RVA: 0x000364D4 File Offset: 0x000346D4
		Friend Overridable Property cmdNext As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdNext
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdNext_Click
				Dim cmdNext As Button = Me._cmdNext
				If cmdNext IsNot Nothing Then
					RemoveHandler cmdNext.Click, value2
				End If
				Me._cmdNext = value
				cmdNext = Me._cmdNext
				If cmdNext IsNot Nothing Then
					AddHandler cmdNext.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B7 RID: 439
		' (get) Token: 0x06000786 RID: 1926 RVA: 0x00036517 File Offset: 0x00034717
		' (set) Token: 0x06000787 RID: 1927 RVA: 0x00036520 File Offset: 0x00034720
		Friend Overridable Property cmdPageNext As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdPageNext
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdPageNext_Click
				Dim cmdPageNext As Button = Me._cmdPageNext
				If cmdPageNext IsNot Nothing Then
					RemoveHandler cmdPageNext.Click, value2
				End If
				Me._cmdPageNext = value
				cmdPageNext = Me._cmdPageNext
				If cmdPageNext IsNot Nothing Then
					AddHandler cmdPageNext.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B8 RID: 440
		' (get) Token: 0x06000788 RID: 1928 RVA: 0x00036563 File Offset: 0x00034763
		' (set) Token: 0x06000789 RID: 1929 RVA: 0x0003656C File Offset: 0x0003476C
		Friend Overridable Property cmdLast As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdLast
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdLast_Click
				Dim cmdLast As Button = Me._cmdLast
				If cmdLast IsNot Nothing Then
					RemoveHandler cmdLast.Click, value2
				End If
				Me._cmdLast = value
				cmdLast = Me._cmdLast
				If cmdLast IsNot Nothing Then
					AddHandler cmdLast.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001B9 RID: 441
		' (get) Token: 0x0600078A RID: 1930 RVA: 0x000365AF File Offset: 0x000347AF
		' (set) Token: 0x0600078B RID: 1931 RVA: 0x000365B8 File Offset: 0x000347B8
		Friend Overridable Property Button1 As Button
			<CompilerGenerated()>
			Get
				Return Me._Button1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Button1_Click
				Dim button As Button = Me._Button1
				If button IsNot Nothing Then
					RemoveHandler button.Click, value2
				End If
				Me._Button1 = value
				button = Me._Button1
				If button IsNot Nothing Then
					AddHandler button.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BA RID: 442
		' (get) Token: 0x0600078C RID: 1932 RVA: 0x000365FB File Offset: 0x000347FB
		' (set) Token: 0x0600078D RID: 1933 RVA: 0x00036604 File Offset: 0x00034804
		Friend Overridable Property Button3 As Button
			<CompilerGenerated()>
			Get
				Return Me._Button3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Button3_Click
				Dim button As Button = Me._Button3
				If button IsNot Nothing Then
					RemoveHandler button.Click, value2
				End If
				Me._Button3 = value
				button = Me._Button3
				If button IsNot Nothing Then
					AddHandler button.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BB RID: 443
		' (get) Token: 0x0600078E RID: 1934 RVA: 0x00036647 File Offset: 0x00034847
		' (set) Token: 0x0600078F RID: 1935 RVA: 0x00036650 File Offset: 0x00034850
		Friend Overridable Property Button2 As Button
			<CompilerGenerated()>
			Get
				Return Me._Button2
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Button2_Click
				Dim button As Button = Me._Button2
				If button IsNot Nothing Then
					RemoveHandler button.Click, value2
				End If
				Me._Button2 = value
				button = Me._Button2
				If button IsNot Nothing Then
					AddHandler button.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BC RID: 444
		' (get) Token: 0x06000790 RID: 1936 RVA: 0x00036693 File Offset: 0x00034893
		' (set) Token: 0x06000791 RID: 1937 RVA: 0x0003669C File Offset: 0x0003489C
		Friend Overridable Property cmdPfadEndSymbole As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdPfadEndSymbole
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Button4_Click
				Dim cmdPfadEndSymbole As Button = Me._cmdPfadEndSymbole
				If cmdPfadEndSymbole IsNot Nothing Then
					RemoveHandler cmdPfadEndSymbole.Click, value2
				End If
				Me._cmdPfadEndSymbole = value
				cmdPfadEndSymbole = Me._cmdPfadEndSymbole
				If cmdPfadEndSymbole IsNot Nothing Then
					AddHandler cmdPfadEndSymbole.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BD RID: 445
		' (get) Token: 0x06000792 RID: 1938 RVA: 0x000366DF File Offset: 0x000348DF
		' (set) Token: 0x06000793 RID: 1939 RVA: 0x000366E8 File Offset: 0x000348E8
		Friend Overridable Property cmdTestPortrait As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdTestPortrait
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdTestPortrait_Click
				Dim cmdTestPortrait As Button = Me._cmdTestPortrait
				If cmdTestPortrait IsNot Nothing Then
					RemoveHandler cmdTestPortrait.Click, value2
				End If
				Me._cmdTestPortrait = value
				cmdTestPortrait = Me._cmdTestPortrait
				If cmdTestPortrait IsNot Nothing Then
					AddHandler cmdTestPortrait.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BE RID: 446
		' (get) Token: 0x06000794 RID: 1940 RVA: 0x0003672B File Offset: 0x0003492B
		' (set) Token: 0x06000795 RID: 1941 RVA: 0x00036734 File Offset: 0x00034934
		Public Overridable Property cmdDownRecords As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdDownRecords
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdDownRecords_Click
				Dim cmdDownRecords As Button = Me._cmdDownRecords
				If cmdDownRecords IsNot Nothing Then
					RemoveHandler cmdDownRecords.Click, value2
				End If
				Me._cmdDownRecords = value
				cmdDownRecords = Me._cmdDownRecords
				If cmdDownRecords IsNot Nothing Then
					AddHandler cmdDownRecords.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001BF RID: 447
		' (get) Token: 0x06000796 RID: 1942 RVA: 0x00036777 File Offset: 0x00034977
		' (set) Token: 0x06000797 RID: 1943 RVA: 0x00036780 File Offset: 0x00034980
		Public Overridable Property cmdTrailerDown As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdTrailerDown
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdTrailerDown_Click
				Dim cmdTrailerDown As Button = Me._cmdTrailerDown
				If cmdTrailerDown IsNot Nothing Then
					RemoveHandler cmdTrailerDown.Click, value2
				End If
				Me._cmdTrailerDown = value
				cmdTrailerDown = Me._cmdTrailerDown
				If cmdTrailerDown IsNot Nothing Then
					AddHandler cmdTrailerDown.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001C0 RID: 448
		' (get) Token: 0x06000798 RID: 1944 RVA: 0x000367C3 File Offset: 0x000349C3
		' (set) Token: 0x06000799 RID: 1945 RVA: 0x000367CC File Offset: 0x000349CC
		Public Overridable Property cmdHeaderDown As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdHeaderDown
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdHeaderDown_Click
				Dim cmdHeaderDown As Button = Me._cmdHeaderDown
				If cmdHeaderDown IsNot Nothing Then
					RemoveHandler cmdHeaderDown.Click, value2
				End If
				Me._cmdHeaderDown = value
				cmdHeaderDown = Me._cmdHeaderDown
				If cmdHeaderDown IsNot Nothing Then
					AddHandler cmdHeaderDown.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001C1 RID: 449
		' (get) Token: 0x0600079A RID: 1946 RVA: 0x0003680F File Offset: 0x00034A0F
		' (set) Token: 0x0600079B RID: 1947 RVA: 0x00036818 File Offset: 0x00034A18
		Public Overridable Property cmdHeaderUp As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdHeaderUp
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdHeaderUp_Click
				Dim cmdHeaderUp As Button = Me._cmdHeaderUp
				If cmdHeaderUp IsNot Nothing Then
					RemoveHandler cmdHeaderUp.Click, value2
				End If
				Me._cmdHeaderUp = value
				cmdHeaderUp = Me._cmdHeaderUp
				If cmdHeaderUp IsNot Nothing Then
					AddHandler cmdHeaderUp.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001C2 RID: 450
		' (get) Token: 0x0600079C RID: 1948 RVA: 0x0003685B File Offset: 0x00034A5B
		' (set) Token: 0x0600079D RID: 1949 RVA: 0x00036864 File Offset: 0x00034A64
		Public Overridable Property cmdTrailerUp As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdTrailerUp
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdTrailerUp_Click
				Dim cmdTrailerUp As Button = Me._cmdTrailerUp
				If cmdTrailerUp IsNot Nothing Then
					RemoveHandler cmdTrailerUp.Click, value2
				End If
				Me._cmdTrailerUp = value
				cmdTrailerUp = Me._cmdTrailerUp
				If cmdTrailerUp IsNot Nothing Then
					AddHandler cmdTrailerUp.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001C3 RID: 451
		' (get) Token: 0x0600079E RID: 1950 RVA: 0x000368A7 File Offset: 0x00034AA7
		' (set) Token: 0x0600079F RID: 1951 RVA: 0x000368B0 File Offset: 0x00034AB0
		Public Overridable Property cmdUpRecords As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdUpRecords
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdUpRecords_Click
				Dim cmdUpRecords As Button = Me._cmdUpRecords
				If cmdUpRecords IsNot Nothing Then
					RemoveHandler cmdUpRecords.Click, value2
				End If
				Me._cmdUpRecords = value
				cmdUpRecords = Me._cmdUpRecords
				If cmdUpRecords IsNot Nothing Then
					AddHandler cmdUpRecords.Click, value2
				End If
			End Set
		End Property

		' Token: 0x170001C4 RID: 452
		' (get) Token: 0x060007A0 RID: 1952 RVA: 0x000368F3 File Offset: 0x00034AF3
		' (set) Token: 0x060007A1 RID: 1953 RVA: 0x000368FB File Offset: 0x00034AFB
		Friend Overridable Property OpenFileDialog1 As OpenFileDialog

		' Token: 0x170001C5 RID: 453
		' (get) Token: 0x060007A2 RID: 1954 RVA: 0x00036904 File Offset: 0x00034B04
		' (set) Token: 0x060007A3 RID: 1955 RVA: 0x0003690C File Offset: 0x00034B0C
		Public Overridable Property Label1 As Label

		' Token: 0x170001C6 RID: 454
		' (get) Token: 0x060007A4 RID: 1956 RVA: 0x00036915 File Offset: 0x00034B15
		' (set) Token: 0x060007A5 RID: 1957 RVA: 0x0003691D File Offset: 0x00034B1D
		Public Overridable Property txtFrameWidth As TextBox

		' Token: 0x170001C7 RID: 455
		' (get) Token: 0x060007A6 RID: 1958 RVA: 0x00036926 File Offset: 0x00034B26
		' (set) Token: 0x060007A7 RID: 1959 RVA: 0x0003692E File Offset: 0x00034B2E
		Public Overridable Property chkStartBlipAtOne As CheckBox

		' Token: 0x170001C8 RID: 456
		' (get) Token: 0x060007A8 RID: 1960 RVA: 0x00036937 File Offset: 0x00034B37
		' (set) Token: 0x060007A9 RID: 1961 RVA: 0x0003693F File Offset: 0x00034B3F
		Friend Overridable Property radBlackFrame As RadioButton

		' Token: 0x170001C9 RID: 457
		' (get) Token: 0x060007AA RID: 1962 RVA: 0x00036948 File Offset: 0x00034B48
		' (set) Token: 0x060007AB RID: 1963 RVA: 0x00036950 File Offset: 0x00034B50
		Friend Overridable Property radWhiteFrame As RadioButton

		' Token: 0x170001CA RID: 458
		' (get) Token: 0x060007AC RID: 1964 RVA: 0x00036959 File Offset: 0x00034B59
		' (set) Token: 0x060007AD RID: 1965 RVA: 0x00036961 File Offset: 0x00034B61
		Public Overridable Property frbFormat As GroupBox

		' Token: 0x170001CB RID: 459
		' (get) Token: 0x060007AE RID: 1966 RVA: 0x0003696A File Offset: 0x00034B6A
		' (set) Token: 0x060007AF RID: 1967 RVA: 0x00036972 File Offset: 0x00034B72
		Public Overridable Property txtAnnoBlipLen As TextBox

		' Token: 0x170001CC RID: 460
		' (get) Token: 0x060007B0 RID: 1968 RVA: 0x0003697B File Offset: 0x00034B7B
		' (set) Token: 0x060007B1 RID: 1969 RVA: 0x00036983 File Offset: 0x00034B83
		Public Overridable Property Label3 As Label

		' Token: 0x170001CD RID: 461
		' (get) Token: 0x060007B2 RID: 1970 RVA: 0x0003698C File Offset: 0x00034B8C
		' (set) Token: 0x060007B3 RID: 1971 RVA: 0x00036994 File Offset: 0x00034B94
		Public Overridable Property optBlipAnno As RadioButton

		' Token: 0x170001CE RID: 462
		' (get) Token: 0x060007B4 RID: 1972 RVA: 0x0003699D File Offset: 0x00034B9D
		' (set) Token: 0x060007B5 RID: 1973 RVA: 0x000369A5 File Offset: 0x00034BA5
		Public Overridable Property txtIgnoreCharsCount As TextBox

		' Token: 0x170001CF RID: 463
		' (get) Token: 0x060007B6 RID: 1974 RVA: 0x000369AE File Offset: 0x00034BAE
		' (set) Token: 0x060007B7 RID: 1975 RVA: 0x000369B6 File Offset: 0x00034BB6
		Public Overridable Property Label6 As Label

		' Token: 0x170001D0 RID: 464
		' (get) Token: 0x060007B8 RID: 1976 RVA: 0x000369BF File Offset: 0x00034BBF
		' (set) Token: 0x060007B9 RID: 1977 RVA: 0x000369C7 File Offset: 0x00034BC7
		Public Overridable Property chkIgnoreChars As CheckBox

		' Token: 0x170001D1 RID: 465
		' (get) Token: 0x060007BA RID: 1978 RVA: 0x000369D0 File Offset: 0x00034BD0
		' (set) Token: 0x060007BB RID: 1979 RVA: 0x000369D8 File Offset: 0x00034BD8
		Public Overridable Property optDreiTeilig As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optDreiTeilig
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optDreiTeilig_CheckedChanged_1
				Dim optDreiTeilig As RadioButton = Me._optDreiTeilig
				If optDreiTeilig IsNot Nothing Then
					RemoveHandler optDreiTeilig.CheckedChanged, value2
				End If
				Me._optDreiTeilig = value
				optDreiTeilig = Me._optDreiTeilig
				If optDreiTeilig IsNot Nothing Then
					AddHandler optDreiTeilig.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170001D2 RID: 466
		' (get) Token: 0x060007BC RID: 1980 RVA: 0x00036A1B File Offset: 0x00034C1B
		' (set) Token: 0x060007BD RID: 1981 RVA: 0x00036A23 File Offset: 0x00034C23
		Public Overridable Property chkLateStart As CheckBox

		' Token: 0x170001D3 RID: 467
		' (get) Token: 0x060007BE RID: 1982 RVA: 0x00036A2C File Offset: 0x00034C2C
		' (set) Token: 0x060007BF RID: 1983 RVA: 0x00036A34 File Offset: 0x00034C34
		Public Overridable Property cmbPapierGroesse As ComboBox

		' Token: 0x170001D4 RID: 468
		' (get) Token: 0x060007C0 RID: 1984 RVA: 0x00036A3D File Offset: 0x00034C3D
		' (set) Token: 0x060007C1 RID: 1985 RVA: 0x00036A45 File Offset: 0x00034C45
		Public Overridable Property chkShowSize As CheckBox

		' Token: 0x170001D5 RID: 469
		' (get) Token: 0x060007C2 RID: 1986 RVA: 0x00036A4E File Offset: 0x00034C4E
		' (set) Token: 0x060007C3 RID: 1987 RVA: 0x00036A58 File Offset: 0x00034C58
		Public Overridable Property optNamen As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optNamen
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optNamen_CheckedChanged_1
				Dim optNamen As RadioButton = Me._optNamen
				If optNamen IsNot Nothing Then
					RemoveHandler optNamen.CheckedChanged, value2
				End If
				Me._optNamen = value
				optNamen = Me._optNamen
				If optNamen IsNot Nothing Then
					AddHandler optNamen.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170001D6 RID: 470
		' (get) Token: 0x060007C4 RID: 1988 RVA: 0x00036A9B File Offset: 0x00034C9B
		' (set) Token: 0x060007C5 RID: 1989 RVA: 0x00036AA4 File Offset: 0x00034CA4
		Public Overridable Property optNummer As RadioButton
			<CompilerGenerated()>
			Get
				Return Me._optNummer
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As RadioButton)
				Dim value2 As EventHandler = AddressOf Me.optNummer_CheckedChanged_1
				Dim optNummer As RadioButton = Me._optNummer
				If optNummer IsNot Nothing Then
					RemoveHandler optNummer.CheckedChanged, value2
				End If
				Me._optNummer = value
				optNummer = Me._optNummer
				If optNummer IsNot Nothing Then
					AddHandler optNummer.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170001D7 RID: 471
		' (get) Token: 0x060007C6 RID: 1990 RVA: 0x00036AE7 File Offset: 0x00034CE7
		' (set) Token: 0x060007C7 RID: 1991 RVA: 0x00036AEF File Offset: 0x00034CEF
		Public Overridable Property txtStart As TextBox

		' Token: 0x170001D8 RID: 472
		' (get) Token: 0x060007C8 RID: 1992 RVA: 0x00036AF8 File Offset: 0x00034CF8
		' (set) Token: 0x060007C9 RID: 1993 RVA: 0x00036B00 File Offset: 0x00034D00
		Public Overridable Property txtLen As TextBox

		' Token: 0x170001D9 RID: 473
		' (get) Token: 0x060007CA RID: 1994 RVA: 0x00036B09 File Offset: 0x00034D09
		' (set) Token: 0x060007CB RID: 1995 RVA: 0x00036B11 File Offset: 0x00034D11
		Public Overridable Property optMulti As RadioButton

		' Token: 0x170001DA RID: 474
		' (get) Token: 0x060007CC RID: 1996 RVA: 0x00036B1A File Offset: 0x00034D1A
		' (set) Token: 0x060007CD RID: 1997 RVA: 0x00036B22 File Offset: 0x00034D22
		Public Overridable Property Label5 As Label

		' Token: 0x170001DB RID: 475
		' (get) Token: 0x060007CE RID: 1998 RVA: 0x00036B2B File Offset: 0x00034D2B
		' (set) Token: 0x060007CF RID: 1999 RVA: 0x00036B33 File Offset: 0x00034D33
		Public Overridable Property Label4 As Label

		' Token: 0x170001DC RID: 476
		' (get) Token: 0x060007D0 RID: 2000 RVA: 0x00036B3C File Offset: 0x00034D3C
		' (set) Token: 0x060007D1 RID: 2001 RVA: 0x00036B44 File Offset: 0x00034D44
		Public Overridable Property chkTwoLines As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkTwoLines
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkTwoLines_CheckedChanged
				Dim chkTwoLines As CheckBox = Me._chkTwoLines
				If chkTwoLines IsNot Nothing Then
					RemoveHandler chkTwoLines.CheckedChanged, value2
				End If
				Me._chkTwoLines = value
				chkTwoLines = Me._chkTwoLines
				If chkTwoLines IsNot Nothing Then
					AddHandler chkTwoLines.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170001DD RID: 477
		' (get) Token: 0x060007D2 RID: 2002 RVA: 0x00036B87 File Offset: 0x00034D87
		' (set) Token: 0x060007D3 RID: 2003 RVA: 0x00036B8F File Offset: 0x00034D8F
		Public Overridable Property chkSimDupFilenames As CheckBox

		' Token: 0x170001DE RID: 478
		' (get) Token: 0x060007D4 RID: 2004 RVA: 0x00036B98 File Offset: 0x00034D98
		' (set) Token: 0x060007D5 RID: 2005 RVA: 0x00036BA0 File Offset: 0x00034DA0
		Public Overridable Property Label10 As Label

		' Token: 0x060007D6 RID: 2006 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkA3PortraitDrehen_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007D7 RID: 2007 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkA4LSDrehen_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007D8 RID: 2008 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkAnnotation_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007D9 RID: 2009 RVA: 0x00036BB4 File Offset: 0x00034DB4
		Private Sub chkAutoAlign_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.chkAutoAlign.CheckState = CheckState.Checked Then
				Me.frbAusrichtung.Enabled = True
				Me.Frame1.Enabled = False
			Else
				Me.frbAusrichtung.Enabled = False
				Me.Frame1.Enabled = True
			End If
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007DA RID: 2010 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkAutoAlign180_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007DB RID: 2011 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkBLIP_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007DC RID: 2012 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkDuplex_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007DD RID: 2013 RVA: 0x00036C08 File Offset: 0x00034E08
		Private Sub chkFesteBelegzahl_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Dim num As Integer = 0
			Dim text As String
			Dim value As Integer
			Do
				If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "KOPFNAME" + Conversions.ToString(num)), modDeclares.glbKopf, False) = 0 Then
					value = num
				End If
				num += 1
			Loop While num <= 3
			If Me.chkFesteBelegzahl.CheckState = CheckState.Checked Then
				Operators.CompareString(Me.txtRestAufnahmen.Text, "", False)
				Return
			End If
			Dim txtRestAufnahmen As TextBox = Me.txtRestAufnahmen
			Dim text2 As String = modMain.GiveIni(text, "SYSTEM", "RESTLAENGE" + Conversions.ToString(value))
			txtRestAufnahmen.Text = Support.Format(Conversion.Val(modMain.KommazuPunkt(text2)), "##0.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
		End Sub

		' Token: 0x060007DE RID: 2014 RVA: 0x00036CB8 File Offset: 0x00034EB8
		Private Sub chkFramesWiederholen_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.chkFramesWiederholen.CheckState = CheckState.Checked Then
				Me.cmdFortsetzung.Visible = True
				Return
			End If
			If Me.chkRollewirdfortgesetzt.CheckState = CheckState.Unchecked And Me.chkRolleistFortsetzung.CheckState = CheckState.Unchecked Then
				Me.cmdFortsetzung.Visible = False
			End If
		End Sub

		' Token: 0x060007DF RID: 2015 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkInvers_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007E0 RID: 2016 RVA: 0x00036D0B File Offset: 0x00034F0B
		Private Sub chkNoPreview_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			modDeclares.NO_PREVIEW = (Me.chkNoPreview.CheckState = CheckState.Checked)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007E1 RID: 2017 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkNullen_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007E2 RID: 2018 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkOneToOne_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007E3 RID: 2019 RVA: 0x00036D28 File Offset: 0x00034F28
		Private Sub chkRolleistFortsetzung_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.chkRolleistFortsetzung.CheckState = CheckState.Checked Then
				Me.cmdFortsetzung.Visible = True
				Return
			End If
			If Me.chkRollewirdfortgesetzt.CheckState = CheckState.Unchecked And Me.chkFramesWiederholen.CheckState = CheckState.Unchecked Then
				Me.cmdFortsetzung.Visible = False
			End If
		End Sub

		' Token: 0x060007E4 RID: 2020 RVA: 0x00036D7C File Offset: 0x00034F7C
		Private Sub chkRollewirdfortgesetzt_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.chkRollewirdfortgesetzt.CheckState = CheckState.Checked Then
				Me.cmdFortsetzung.Visible = True
				Return
			End If
			If Me.chkFramesWiederholen.CheckState = CheckState.Unchecked And Me.chkRolleistFortsetzung.CheckState = CheckState.Unchecked Then
				Me.cmdFortsetzung.Visible = False
			End If
		End Sub

		' Token: 0x060007E5 RID: 2021 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkShowSize_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007E6 RID: 2022 RVA: 0x00036DCF File Offset: 0x00034FCF
		Private Sub chkStepsImageToImage_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.CheckDistance()
		End Sub

		' Token: 0x060007E7 RID: 2023 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub cmbBlipLevel1_SelectedIndexChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007E8 RID: 2024 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub cmbBlipLevel2_SelectedIndexChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007E9 RID: 2025 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub cmbBlipLevel3_SelectedIndexChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x060007EA RID: 2026 RVA: 0x00036DD8 File Offset: 0x00034FD8
		Private Sub cmbMaxDocumentSize_SelectedIndexChanged(eventSender As Object, eventArgs As EventArgs)
			Select Case Me.cmbMaxDocumentSize.SelectedIndex
				Case 0
					Me.txtSplitBreite.Text = Conversions.ToString(210)
					Me.txtSplitLaenge.Text = Conversions.ToString(297)
					Me.txtSplitBreite.[ReadOnly] = True
					Me.txtSplitLaenge.[ReadOnly] = True
					Return
				Case 1
					Me.txtSplitBreite.Text = Conversions.ToString(297)
					Me.txtSplitLaenge.Text = Conversions.ToString(420)
					Me.txtSplitBreite.[ReadOnly] = True
					Me.txtSplitLaenge.[ReadOnly] = True
					Return
				Case 2
					Me.txtSplitBreite.Text = Conversions.ToString(420)
					Me.txtSplitLaenge.Text = Conversions.ToString(594)
					Me.txtSplitBreite.[ReadOnly] = True
					Me.txtSplitLaenge.[ReadOnly] = True
					Return
				Case 3
					Me.txtSplitBreite.Text = Conversions.ToString(594)
					Me.txtSplitLaenge.Text = Conversions.ToString(840)
					Me.txtSplitBreite.[ReadOnly] = True
					Me.txtSplitLaenge.[ReadOnly] = True
					Return
				Case 4
					Me.txtSplitBreite.Text = Conversions.ToString(840)
					Me.txtSplitLaenge.Text = Conversions.ToString(1188)
					Me.txtSplitBreite.[ReadOnly] = True
					Me.txtSplitLaenge.[ReadOnly] = True
					Return
				Case 5
					Me.txtSplitBreite.[ReadOnly] = False
					Me.txtSplitLaenge.[ReadOnly] = False
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x060007EB RID: 2027 RVA: 0x00036F78 File Offset: 0x00035178
		Private Sub cmbTemplate_SelectedIndexChanged(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			If Operators.CompareString(Me.cmbTemplate.Text, "", False) <> 0 Then
				Me.DisableLayoutUpdate()
				Dim text2 As String = Me.cmbTemplate.Text
				Me.LoadData(text2)
				Me.EnableLayoutUpdate()
				text2 = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + Me.cmbTemplate.Text
				modDeclares.glbKopf = modMain.GiveIni(text2, "TEMPLATE", "CAMERAHEAD")
				Dim num As Short = 0S
				Dim value As Short
				Do
					If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "KOPFNAME" + Conversions.ToString(CInt(num))), modDeclares.glbKopf, False) = 0 Then
						value = num
					End If
					num += 1S
				Loop While num <= 3S
				modDeclares.glbOrientation = (Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "Portrait" + Conversions.ToString(CInt(value))), "1", False) = 0)
				Dim txtRestAufnahmen As TextBox = Me.txtRestAufnahmen
				text2 = modMain.GiveIni(text, "SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(value)))
				txtRestAufnahmen.Text = Support.Format(Conversion.Val(modMain.KommazuPunkt(text2)), "##0.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				If Me.chkFesteBelegzahl.CheckState = CheckState.Checked Then
					Me.txtRestAufnahmen.Text = modMain.GiveIni(text, "SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(value)))
				End If
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x060007EC RID: 2028 RVA: 0x000370FC File Offset: 0x000352FC
		Private Sub cmdAbspulen_Click(eventSender As Object, eventArgs As EventArgs)
			modDeclares.Outputs = 0
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim num As Short = 0S
			Dim num2 As Short
			Do
				If Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num)), modDeclares.glbKopf, False) = 0 Then
					num2 = num
				End If
				num += 1S
			Loop While num <= 3S
			Dim text As String = "TXT_REALLY_FULL_WIND"
			Dim text2 As String = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Soll der Film tatsächlich abgespult werden?"
			End If
			Dim num3 As Short = 4S
			text = "file-converter"
			If modMain.msgbox2(text2, num3, text) = 6S Then
				MyBase.Enabled = False
				MyProject.Forms.frmFilmAbspulen.Show()
				MyProject.Forms.frmFilmAbspulen.lblRest.Text = Me.txtRestAufnahmen.Text
				Application.DoEvents()
				Dim num4 As Integer
				Dim num5 As Integer
				num4 = CInt(Math.Round(Conversion.Val(MyProject.Forms.frmFilmAbspulen.lblRest.Text) * 1000.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
				num5 = CInt(Math.Round(500.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
				If modDeclares.SystemData.NeuerMagnet Then
					modMultiFly.MagnetPlatteHoch()
				End If
				modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
				Do
					num3 = 1S
					Dim filmspeed As Integer() = modDeclares.SystemData.filmspeed
					Dim num6 As Integer = CInt(num2)
					Dim num7 As Integer = 1
					Dim num8 As Integer = 0
					Dim num9 As Integer = 0
					modMultiFly.FahreMotor(num3, num5, filmspeed(num6), num7, num8, num9, modDeclares.SystemData.FResolution(CInt(num2)))
					While True
						num3 = 1S
						If Not modMultiFly.MotorIsRunning(num3) Then
							Exit For
						End If
						Application.DoEvents()
						If Operators.ConditionalCompareObjectEqual(MyProject.Forms.frmFilmAbspulen.Tag, "END", False) Then
							text = "TXT_MOTOR_WILL_STOP"
							text2 = modMain.GetText(text)
							If Operators.CompareString(text2, "", False) = 0 Then
								text2 = "Motor wird angehalten"
							End If
							MyProject.Forms.frmFilmAbspulen.cmdStop.Text = text2
						End If
					End While
					MyProject.Forms.frmFilmAbspulen.lblRest.Text = Conversions.ToString(Conversion.Val(MyProject.Forms.frmFilmAbspulen.lblRest.Text) - 0.5)
					num4 -= num5
					Me.txtRestAufnahmen.Text = Conversions.ToString(Conversions.ToDouble(Me.txtRestAufnahmen.Text) - 0.5)
					Application.DoEvents()
				Loop While Not Conversions.ToBoolean(Operators.OrObject(Operators.CompareObjectEqual(MyProject.Forms.frmFilmAbspulen.Tag, "END", False), num4 < 0))
				MyProject.Forms.frmFilmAbspulen.Close()
				MyProject.Forms.frmFilmAbspulen.Dispose()
				If modDeclares.SystemData.NeuerMagnet Then
					modMultiFly.MagnetPlatteRunter()
				End If
				If Conversion.Val(Me.txtRestAufnahmen.Text) < 0.0 Then
					Me.txtRestAufnahmen.Text = "0"
				End If
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Me.txtRestAufnahmen.Text, lpFileName) > False)
				MyProject.Forms.frmFilmAbspulen.Close()
				MyBase.Enabled = True
				MyBase.Show()
			End If
		End Sub

		' Token: 0x060007ED RID: 2029 RVA: 0x0003743C File Offset: 0x0003563C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdCalcSpace_Click(eventSender As Object, eventArgs As EventArgs)
			modDeclares.UseDebug = True
			modDeclares.SystemData.SIMULATIONDELAY = 0
			Dim text As String = Me.txtLastDocument.Text
			Dim text2 As String = Me.txtPage.Text
			Dim text3 As String = Me.txtFilmNr.Text
			Dim text4 As String = Me.txtRestAufnahmen.Text
			Me.txtRestAufnahmen.Text = Conversions.ToString(1000000)
			modDeclares.CalcModus = True
			Me.StartFilming()
			modDeclares.CalcModus = False
			Dim num As Double = 1000000.0
			Dim text5 As String = Me.txtRestAufnahmen.Text
			Dim num2 As Double = num - Conversion.Val(modMain.KommazuPunkt(text5))
			text5 = "TXT_DOCUMENTS_NEED1"
			Dim text6 As String = modMain.GetText(text5)
			text5 = "TXT_DOCUMENTS_NEED2"
			Dim text7 As String = modMain.GetText(text5)
			If Operators.CompareString(text6, "", False) = 0 Then
				text6 = "Dokumente benötigen"
				text7 = "m Film"
			End If
			text5 = String.Concat(New String() { text6, " ", Support.Format(num2, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), " ", text7 })
			Dim num3 As Short = 0S
			Dim text8 As String = "file-converter"
			modMain.msgbox2(text5, num3, text8)
			Me.txtLastDocument.Text = text
			Me.txtPage.Text = text2
			Me.txtFilmNr.Text = text3
			Me.txtRestAufnahmen.Text = text4
			Dim num4 As Short = CShort(FileSystem.FreeFile())
			FileSystem.FileOpen(CInt(num4), MyProject.Application.Info.DirectoryPath + "\CalcProt.txt", OpenMode.Append, OpenAccess.[Default], OpenShare.[Default], -1)
			FileSystem.PrintLine(CInt(num4), New Object() { String.Concat(New String() { vbCrLf, text6, " ", Support.Format(num2, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), " ", text7 }) })
			FileSystem.FileClose(New Integer() { CInt(num4) })
			Interaction.Shell("notepad.exe " + MyProject.Application.Info.DirectoryPath + "\CalcProt.txt", AppWinStyle.MaximizedFocus, False, -1)
			If Not modDeclares.UseDebug Then
				text8 = "SYSTEM"
				text5 = "SIMULATION"
				Dim nDefault As Integer = 0
				Dim text9 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				modDeclares.UseDebug = (modDeclares.GetPrivateProfileInt(text8, text5, nDefault, text9) = 1)
				modDeclares.UseDebug = True
			End If
		End Sub

		' Token: 0x060007EE RID: 2030 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdCancel_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007EF RID: 2031 RVA: 0x00037696 File Offset: 0x00035896
		Private Sub cmdChangeFilmNo_Click()
			New frmGetFilmNo() With { .txtFilmNo = { .Text = Me.txtFilmNr.Text } }.ShowDialog()
		End Sub

		' Token: 0x060007F0 RID: 2032 RVA: 0x000376B9 File Offset: 0x000358B9
		Private Sub cmdClearLogPath_Click(eventSender As Object, eventArgs As EventArgs)
			Me.lblLogFile.Text = ""
		End Sub

		' Token: 0x060007F1 RID: 2033 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdDownRecords_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007F2 RID: 2034 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdFirst_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007F3 RID: 2035 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdHeaderDown_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007F4 RID: 2036 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdHeaderUp_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007F5 RID: 2037 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdLast_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007F6 RID: 2038 RVA: 0x000376CC File Offset: 0x000358CC
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdLog_Click()
			Dim num9 As Integer
			Dim num12 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim num2 As Short = CShort(FileSystem.FreeFile())
				IL_09:
				num = 2
				FileSystem.FileOpen(CInt(num2), MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG.txt", OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
				IL_2E:
				num = 3
				Dim num3 As Short = CShort(FileSystem.FreeFile())
				IL_38:
				num = 4
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\BAYHSTA\LOG-" + Support.Format(DateAndTime.Today, "yyyy-mm-dd", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1) + ".txt"
				IL_70:
				num = 5
				FileSystem.FileOpen(CInt(num3), text, OpenMode.Output, OpenAccess.[Default], OpenShare.[Default], -1)
				IL_7F:
				num = 6
				Dim num4 As Short = 0S
				Dim text3 As String
				Dim text4 As String
				While True
					IL_450:
					num = 8
					If FileSystem.EOF(CInt(num2)) Then
						GoTo IL_45D
					End If
					IL_89:
					num = 9
					num4 += 1S
					IL_93:
					num = 10
					Dim text2 As String = FileSystem.LineInput(CInt(num2))
					IL_9E:
					num = 11
					Dim num5 As Integer = Strings.InStr(1, text2, ";", Microsoft.VisualBasic.CompareMethod.Binary)
					IL_B1:
					num = 12
					Dim num6 As Integer = num5
					IL_B8:
					num = 13
					If num5 < 0 Then
						Exit For
					End If
					IL_E6:
					num = 16
					num5 = Strings.InStr(num5 + 1, text2, ";", Microsoft.VisualBasic.CompareMethod.Binary)
					IL_FC:
					num = 17
					If num5 < 0 Then
						GoTo IL_104
					End If
					IL_12A:
					num = 20
					Dim num7 As Integer = Strings.InStrRev(text2, ";", -1, Microsoft.VisualBasic.CompareMethod.Binary)
					IL_13D:
					num = 21
					If num7 < 0 Then
						GoTo IL_145
					End If
					IL_16B:
					num = 24
					num7 = Strings.InStrRev(text2, ";", num7 - 1, Microsoft.VisualBasic.CompareMethod.Binary)
					IL_181:
					num = 25
					If num7 < 0 Then
						GoTo IL_189
					End If
					IL_1AF:
					num = 28
					Dim flag As Boolean = False
					IL_1B5:
					num = 29
					If Operators.CompareString(Strings.Mid(text2, num7 + 1, 1), "Y", False) = 0 Or Operators.CompareString(Strings.Mid(text2, num7 + 1, 1), "N", False) = 0 Then
						IL_1EF:
						num = 30
						If Operators.CompareString(Strings.Mid(text2, num5 + 1, 1), "N", False) <> 0 And Operators.CompareString(Strings.Mid(text2, num5 + 1, 1), "Y", False) <> 0 Then
							IL_229:
							num = 31
							flag = True
						End If
					End If
					IL_22F:
					num = 32
					Dim str As String = Strings.Left(text2, num6 - 1)
					IL_23F:
					num = 33
					If flag Then
						IL_249:
						num = 34
						Dim num8 As Short = CShort(FileSystem.FreeFile())
						IL_254:
						num = 35
						text3 = Me.lblLogFile.Text
						IL_264:
						num = 36
						text4 = text3 + "\" + str + ".txt"
						IL_27C:
						ProjectData.ClearProjectError()
						num9 = 1
						IL_283:
						num = 38
						FileSystem.FileOpen(CInt(num8), text4, OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
						IL_293:
						num = 39
						If Information.Err().Number <> 0 Then
							GoTo IL_2A5
						End If
						Dim text6 As String
						Dim text7 As String
						Dim text8 As String
						While True
							IL_388:
							num = 45
							If FileSystem.EOF(CInt(num8)) Then
								Exit For
							End If
							IL_2DA:
							num = 46
							Dim text5 As String = FileSystem.LineInput(CInt(num8))
							IL_2E6:
							num = 47
							Dim num10 As Short = CShort(Strings.InStr(text5, "=", Microsoft.VisualBasic.CompareMethod.Binary))
							IL_2F9:
							num = 48
							Dim left As String = Strings.Left(text5, CInt((num10 - 1S)))
							If Operators.CompareString(left, "first filename on film", False) <> 0 Then
								If Operators.CompareString(left, "# of exposed images", False) <> 0 Then
									If Operators.CompareString(left, "Date/Time", False) = 0 Then
										IL_378:
										num = 55
										text6 = Strings.Mid(text5, CInt((num10 + 1S)))
									End If
								Else
									IL_366:
									num = 53
									text7 = Strings.Mid(text5, CInt((num10 + 1S)))
								End If
							Else
								IL_338:
								num = 50
								text8 = Strings.Mid(text5, CInt((num10 + 1S)))
								IL_348:
								num = 51
								text8 = Strings.Mid(text8, Strings.InStrRev(text8, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) + 1)
							End If
						End While
						IL_397:
						num = 58
						FileSystem.FileClose(New Integer() { CInt(num8) })
						IL_3AA:
						num = 59
						FileSystem.PrintLine(CInt(num3), New Object() { String.Concat(New String() { Strings.Left(text2, num5 - 1), Strings.Left(Strings.Mid(text2, num7), 3), text6, ";", text8, ";bayhsta_kriegsstammrollen_", Strings.Mid(text2, num7 + 3), ";", text7, Strings.Mid(text2, num5, num7 - num5), ";" }) })
					Else
						IL_43B:
						num = 61
						FileSystem.PrintLine(CInt(num3), New Object() { text2 })
					End If
				End While
				IL_C0:
				num = 14
				Interaction.MsgBox("Fehler in Zeile " + Conversions.ToString(CInt(num4)) + vbCr & "1. ; nicht gefunden!", MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_49A
				IL_104:
				num = 18
				Interaction.MsgBox("Fehler in Zeile " + Conversions.ToString(CInt(num4)) + vbCr & "2. ; nicht gefunden!", MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_49A
				IL_145:
				num = 22
				Interaction.MsgBox("Fehler in Zeile " + Conversions.ToString(CInt(num4)) + vbCr & "Letztes ; nicht gefunden!", MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_49A
				IL_189:
				num = 26
				Interaction.MsgBox("Fehler in Zeile " + Conversions.ToString(CInt(num4)) + vbCr & "Vorletztes ; nicht gefunden!", MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_49A
				IL_2A5:
				num = 40
				Interaction.MsgBox(text4 + " konnte nicht geöffnet werden, bitte überprüfen!" & vbCr & "Die Protokolle werden im Verzeichnis: " + text3 + " erwartet!!", MsgBoxStyle.OkOnly, Nothing)
				IL_2C3:
				num = 41
				FileSystem.FileClose(New Integer() { CInt(num2) })
				GoTo IL_49A
				IL_45D:
				num = 63
				FileSystem.FileClose(New Integer() { CInt(num3) })
				IL_470:
				num = 64
				FileSystem.FileClose(New Integer() { CInt(num2) })
				IL_482:
				num = 65
				Interaction.Shell("notepad.exe " + text, AppWinStyle.MaximizedFocus, False, -1)
				IL_49A:
				GoTo IL_5F4
				IL_49F:
				Dim num11 As Integer = num12 + 1
				num12 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num11)
				IL_5B5:
				GoTo IL_5E9
				IL_5B7:
				num12 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num9)
				IL_5C7:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num9 <> 0 And num12 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_5B7
			End Try
			IL_5E9:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_5F4:
			If num12 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x060007F7 RID: 2039 RVA: 0x00037CF4 File Offset: 0x00035EF4
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdNeu_Click(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = "TXT_REXPOSE_DOCUMENTS"
			Dim left As String = modMain.GetText(text)
			If Operators.CompareString(left, "", False) = 0 Then
				left = "Really reexpose all the Documents?"
			End If
			Dim num As Short = 4S
			text = "file-converter"
			If modMain.msgbox2(left, num, text) = 6S Then
				text = "TXT_USE_NEW_ROLL"
				left = modMain.GetText(text)
				If Operators.CompareString(left, "", False) = 0 Then
					left = "Do you want to insert a new Film Roll?"
				End If
				Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				Dim value As Short = -1S
				Dim num2 As Short = 0S
				Do
					If Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "KOPFNAME" + Conversions.ToString(CInt(num2))), modDeclares.glbKopf, False) = 0 Then
						value = num2
					End If
					num2 += 1S
				Loop While num2 <= 3S
				num = 4S
				text = "file-converter"
				If modMain.msgbox2(left, num, text) = 6S Then
					Me.txtRestAufnahmen.Text = Conversions.ToString(0)
					Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
					Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "BelegeVerfuegbar" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
					Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Else
					modDeclares.NEWPROTOCOLHEADER = True
					Dim flag4 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "NEWPROTOCOLHEADER", "1", lpFileName) > False)
				End If
				Dim flag5 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Me.cmdFortsetzung.Tag = "0"
				Dim cmdFortsetzung As ButtonBase = Me.cmdFortsetzung
				text = "TXT_ROLL_IS_NOT_CONT"
				cmdFortsetzung.Text = modMain.GetText(text)
				If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) = 0 Then
					Me.cmdFortsetzung.Text = "Rolle ist KEINE Fortsetzung"
				End If
				Me.txtLastDocument.Text = ""
				Me.txtPage.Text = ""
				Dim num3 As Short = CShort(FileSystem.FreeFile())
				Dim value2 As String = vbCrLf
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
					FileSystem.Kill(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt")
					If Operators.CompareString(Information.Err().Description, "", False) <> 0 Then
						Interaction.MsgBox(Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
					End If
				End If
				Using streamWriter As StreamWriter = New StreamWriter(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", True, Encoding.Unicode)
					streamWriter.Write(value2)
					streamWriter.Close()
				End Using
				If modPaint.pos = 0 Then
					modDeclares.NoImageUpdate = True
				End If
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x060007F8 RID: 2040 RVA: 0x00037FF8 File Offset: 0x000361F8
		Private Sub cmdNewRoll_Click(eventSender As Object, eventArgs As EventArgs)
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim num As Short = 0S
			Do
				If Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "KOPFNAME" + Conversions.ToString(CInt(num))), modDeclares.glbKopf, False) = 0 Then
				End If
				num += 1S
			Loop While num <= 3S
			Dim text As String = "TXT_INSERT_NEW_ROLL"
			Dim left As String = modMain.GetText(text)
			If Operators.CompareString(left, "", False) = 0 Then
				left = "Wollen Sie tatsächlich eine neue Rolle einlegen?"
				left = "Do you really want to insert a new Film Roll?"
			End If
			Dim num2 As Short = 4S
			text = "file-converter"
			If modMain.msgbox2(left, num2, text) = 6S Then
				Me.txtRestAufnahmen.Text = Conversions.ToString(0)
				lpFileName = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				Dim value As Short = -1S
				num = 0S
				Do
					If Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "KOPFNAME" + Conversions.ToString(CInt(num))), modDeclares.glbKopf, False) = 0 Then
						value = num
					End If
					num += 1S
				Loop While num <= 3S
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Dim lpString As String = "0"
				Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "BELEGEVERFUEGBAR" + Conversions.ToString(CInt(value)), lpString, lpFileName) > False)
			End If
		End Sub

		' Token: 0x060007F9 RID: 2041 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdNewTemplate_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FA RID: 2042 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdNext_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FB RID: 2043 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPageNext_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FC RID: 2044 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPagePrevious_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FD RID: 2045 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadEndSymbole_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FE RID: 2046 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadFortsetzungsSymbole1_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060007FF RID: 2047 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadFortsetzungsSymbole2_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000800 RID: 2048 RVA: 0x00038174 File Offset: 0x00036374
		Private Sub cmdPfadStartSymbole_ClickEvent(eventSender As Object, eventArgs As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadStartSymbole.Text
				IL_19:
				num2 = 3
				Me.lblPfadStartSymbole.Text = modDeclares.mdlFktSelectedDirectory
				IL_2B:
				GoTo IL_8A
				IL_2D:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_4B:
				GoTo IL_7F
				IL_4D:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_5D:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_4D
			End Try
			IL_7F:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_8A:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000801 RID: 2049 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPrevious_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000802 RID: 2050 RVA: 0x00038224 File Offset: 0x00036424
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdRefilm_Click(eventSender As Object, eventArgs As EventArgs)
			MyProject.Forms.frmSelectRoll.ShowDialog()
			If Operators.CompareString(modDeclares.rcfrmSelectRoll, "", False) <> 0 Then
				Me.txtFilmNr.Tag = Me.txtFilmNr.Text
				FileSystem.FileCopy(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", MyProject.Application.Info.DirectoryPath + "\LastDocument.txt.org")
				Me.txtLastDocument.Tag = Me.txtLastDocument.Text
				Me.txtPage.Tag = Me.txtPage.Text
				Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				Dim value As Short = -1S
				Dim num As Short = 0S
				Do
					If Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "KOPFNAME" + Conversions.ToString(CInt(num))), modDeclares.glbKopf, False) = 0 Then
						value = num
					End If
					num += 1S
				Loop While num <= 3S
				Me.txtRestAufnahmen.Text = Conversions.ToString(0)
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "FRAMECOUNTER" + Conversions.ToString(CInt(value)), "0", lpFileName) > False)
				Me.txtFilmNr.Text = Support.Format(Conversion.Val(modDeclares.rcfrmSelectRoll) - 1.0, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				Dim text As String = MyProject.Application.Info.DirectoryPath + "\ROLLDESCS\" + modDeclares.rcfrmSelectRoll + ".desc"
				modMain.GiveIniW(text, "INFO", "FIRSTFILE")
				Dim text2 As String = "INFO"
				Dim text3 As String = "CONTINUATION"
				Dim privateProfileInt As Integer = modDeclares.GetPrivateProfileInt(text2, text3, 0, text)
				Dim cmdRefilm As Control = Me.cmdRefilm
				text3 = "INFO"
				text2 = "FIRSTFILEINDEX"
				cmdRefilm.Tag = modDeclares.GetPrivateProfileInt(text3, text2, 0, text) - 1
				modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(CInt(value)), Support.Format(privateProfileInt, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), lpFileName)
				If privateProfileInt = 1 Then
					Me.cmdFortsetzung.Tag = "1"
					Dim cmdFortsetzung As ButtonBase = Me.cmdFortsetzung
					text2 = "TXT_ROLL_IS_CONT"
					cmdFortsetzung.Text = modMain.GetText(text2)
					If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) = 0 Then
						Me.cmdFortsetzung.Text = "Rolle ist eine Fortsetzung"
					End If
				Else
					Me.cmdFortsetzung.Tag = "0"
					Dim cmdFortsetzung2 As ButtonBase = Me.cmdFortsetzung
					text2 = "TXT_ROLL_IS_NOT_CONT"
					cmdFortsetzung2.Text = modMain.GetText(text2)
					If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) = 0 Then
						Me.cmdFortsetzung.Text = "Rolle ist KEINE Fortsetzung"
					End If
				End If
				If Me.CheckData() Then
					Me.StartFilming()
				End If
				Me.cmdRefilm.Tag = ""
				Me.txtFilmNr.Text = Conversions.ToString(Me.txtFilmNr.Tag)
				FileSystem.FileCopy(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt.org", MyProject.Application.Info.DirectoryPath + "\LastDocument.txt")
				Me.txtLastDocument.Text = Conversions.ToString(Me.txtLastDocument.Tag)
				Me.txtPage.Text = Conversions.ToString(Me.txtPage.Tag)
				text2 = "Die Verfilmung wird jetzt hinter Rolle Nr. " + Me.txtFilmNr.Text + " fortgesetzt!"
				Dim num2 As Short = 0S
				text3 = "file-converter"
				modMain.msgbox2(text2, num2, text3)
			End If
		End Sub

		' Token: 0x06000803 RID: 2051 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdSaveTemplate_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000804 RID: 2052 RVA: 0x000385D8 File Offset: 0x000367D8
		Private Sub cmdSet_Click()
			New frmGetFirstDoc() With { .txtPage = { .Text = Me.txtPage.Text }, .txtDoc = { .Text = Me.txtLastDocument.Text, .SelectionStart = 0, .SelectionLength = Strings.Len(MyProject.Forms.frmGetFirstDoc.txtDoc.Text) } }.ShowDialog()
			Me.UpdateLayout()
		End Sub

		' Token: 0x06000805 RID: 2053 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdSetLastDoc_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000806 RID: 2054 RVA: 0x00038654 File Offset: 0x00036854
		Private Sub cmdSetLogPath_Click(eventSender As Object, eventArgs As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblLogFile.Text
				IL_19:
				num2 = 3
				Me.OpenFileDialog1.ValidateNames = False
				IL_27:
				num2 = 4
				Me.OpenFileDialog1.CheckFileExists = False
				IL_35:
				num2 = 5
				Me.OpenFileDialog1.FileName = "Select the Source Folder"
				IL_47:
				num2 = 6
				Me.OpenFileDialog1.ShowDialog()
				IL_55:
				num2 = 7
				Me.lblLogFile.Text = Strings.Left(Me.OpenFileDialog1.FileName, Strings.InStrRev(Me.OpenFileDialog1.FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
				IL_8B:
				num2 = 8
				Application.DoEvents()
				IL_92:
				GoTo IL_105
				IL_94:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_C6:
				GoTo IL_FA
				IL_C8:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_D8:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_C8
			End Try
			IL_FA:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_105:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000807 RID: 2055 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdStart_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000808 RID: 2056 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdTestPortrait_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000809 RID: 2057 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdUpRecords_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x0600080A RID: 2058 RVA: 0x00038780 File Offset: 0x00036980
		Private Sub cmdVorspann_Click(eventSender As Object, eventArgs As EventArgs)
			modDeclares.Outputs = 0
			Dim num As Short = 0S
			Dim num2 As Short
			Do
				If Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num)), modDeclares.glbKopf, False) = 0 Then
					num2 = num
				End If
				num += 1S
			Loop While num <= 3S
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim txtRestAufnahmen As TextBox
			Dim text As String
			Dim num3 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.nachspann) * 10.0 * modDeclares.SystemData.schrittepromm(CInt(num2))))
			MyProject.Forms.frmFilmTransport.Show()
			MyProject.Forms.frmFilmTransport.Text = "Leader"
			Application.DoEvents()
			If modDeclares.SystemData.NeuerMagnet Then
				modMultiFly.MagnetPlatteHoch()
			End If
			modMultiFly.SetStepMode(modDeclares.SystemData.VResolution, modDeclares.SystemData.FResolution(CInt(num2)))
			Dim num4 As Short = 1S
			Dim num5 As Integer = CInt(CShort(modDeclares.SystemData.filmspeed(CInt(num2))))
			Dim speedFromSteps As Integer = modMultiFly.GetSpeedFromSteps(num3, num5)
			Dim num6 As Integer = 1
			Dim num7 As Integer = 0
			Dim num8 As Integer = 0
			modMultiFly.FahreMotor(num4, num3, speedFromSteps, num6, num7, num8, modDeclares.SystemData.FResolution(CInt(num2)))
			While True
				num4 = 1S
				If Not modMultiFly.MotorIsRunning(num4) Then
					Exit For
				End If
				Application.DoEvents()
			End While
			If modDeclares.SystemData.NeuerMagnet Then
				modMultiFly.MagnetPlatteRunter()
			End If
			MyProject.Forms.frmFilmTransport.Close()
			Application.DoEvents()
			txtRestAufnahmen = Me.txtRestAufnahmen
			text = Me.txtRestAufnahmen.Text
			txtRestAufnahmen.Text = Support.Format(Conversion.Val(modMain.KommazuPunkt(text)) - CDbl(modDeclares.SystemData.vorspann) / 100.0, "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(num2)), Me.txtRestAufnahmen.Text, lpFileName) > False)
		End Sub

		' Token: 0x0600080B RID: 2059 RVA: 0x0003894C File Offset: 0x00036B4C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub frmFilmPreview_Load(eventSender As Object, eventArgs As EventArgs)
			Dim num11 As Integer
			Dim num13 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim text As String = ""
				IL_09:
				num = 2
				Me.Image2.Image = Image.FromFile(MyProject.Application.Info.DirectoryPath + "\Schemes\StartBild.bmp")
				IL_34:
				num = 3
				Dim text4 As String
				Dim num2 As Short
				Dim num3 As Short
				MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - Support.PixelsToTwipsX(CDbl(MyBase.Width)) / 2.0)))
				IL_81:
				num = 4
				MyBase.Top = CInt(Math.Round(Support.TwipsToPixelsY(Support.PixelsToTwipsY(CDbl(Screen.PrimaryScreen.Bounds.Height)) / 2.0 - Support.PixelsToTwipsY(CDbl(MyBase.Height)) / 2.0)))
				IL_CE:
				num = 5
				Dim isSMA As Boolean = modDeclares.IsSMA
				IL_D6:
				num = 6
				Dim smci As Boolean = modDeclares.SystemData.SMCI
				IL_E3:
				num = 7
				If Not modDeclares.IsSMA Then
					GoTo IL_11F
				End If
				IL_EC:
				num = 8
				If Not modDeclares.issma16 Then
					GoTo IL_101
				End If
				IL_F5:
				num = 9
				If modDeclares.IsSI Then
					GoTo IL_10A
				End If
				GoTo IL_10A
				IL_101:
				num = 11
				Dim isSI As Boolean = modDeclares.IsSI
				IL_10A:
				num = 12
				If modDeclares.SMAVersion <> 57S Then
					GoTo IL_11F
				End If
				IL_116:
				num = 13
				Dim isSI2 As Boolean = modDeclares.IsSI
				IL_11F:
				num = 14
				If Not modDeclares.IsSI Then
					GoTo IL_1D4
				End If
				IL_12C:
				num = 15
				If modDeclares.SMAVersion <> 51S Then
					GoTo IL_164
				End If
				IL_138:
				num = 16
				Me.Image2.Image = Image.FromFile(MyProject.Application.Info.DirectoryPath + "\SI-51-H800_FH.bmp")
				IL_164:
				num = 17
				If modDeclares.SMAVersion <> 57S Then
					GoTo IL_19C
				End If
				IL_170:
				num = 18
				Me.Image2.Image = Image.FromFile(MyProject.Application.Info.DirectoryPath + "\SI-57-H800_FH.bmp")
				IL_19C:
				num = 19
				If modDeclares.SMAVersion <> 16S Then
					GoTo IL_1D4
				End If
				IL_1A8:
				num = 20
				Me.Image2.Image = Image.FromFile(MyProject.Application.Info.DirectoryPath + "\SI-16-H800_FH.bmp")
				IL_1D4:
				num = 21
				Dim enableInfoWindow As Boolean = modDeclares.SystemData.EnableInfoWindow
				IL_1E2:
				num = 22
				Dim text2 As String = "SYSTEM"
				Dim text3 As String = "ANNOFONTSIZE"
				Dim nDefault As Integer = 8
				text4 = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				num2 = CShort(modDeclares.GetPrivateProfileInt(text2, text3, nDefault, text4))
				IL_21D:
				num = 23
				num3 = 0S
				Do
					IL_223:
					num = 24
					Me.SetLblAnnoFontSize(CInt(num3), CLng(num2))
					IL_231:
					num = 25
					num3 += 1S
				Loop While num3 <= 5S
				IL_240:
				num = 26
				num3 = 0S
				Dim value As Short
				Do
					IL_246:
					num = 27
					If Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num3)), modDeclares.glbKopf, False) = 0 Then
						IL_263:
						num = 28
						value = num3
					End If
					IL_26A:
					num = 29
					num3 += 1S
				Loop While num3 <= 3S
				IL_279:
				num = 30
				Me.cmbKopf.Items.Clear()
				IL_28C:
				num = 31
				Me.cmbKopf.Items.Add("16 mm")
				IL_2A5:
				num = 32
				Me.cmbKopf.Items.Add("35 mm")
				IL_2BE:
				num = 33
				Me.cmbKopf.Items.Add("16 mm A3/A4")
				IL_2D7:
				num = 34
				Me.cmbKopf.Items.Add("35 mm Portrait")
				IL_2F0:
				num = 35
				modDeclares.NO_PREVIEW = (Me.chkNoPreview.CheckState = CheckState.Checked)
				IL_306:
				num = 36
				Me.cmbSplitCount.SelectedIndex = 0
				IL_315:
				num = 37
				text4 = "TXT_FIRST"
				Dim text5 As String = modMain.GetText(text4)
				IL_328:
				num = 38
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_350
				End If
				IL_33A:
				num = 39
				Me.ToolTip1.SetToolTip(Me.cmdFirst, text5)
				IL_350:
				num = 40
				text4 = "TXT_NEXT_DOC"
				text5 = modMain.GetText(text4)
				IL_363:
				num = 41
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_38B
				End If
				IL_375:
				num = 42
				Me.ToolTip1.SetToolTip(Me.cmdPageNext, text5)
				IL_38B:
				num = 43
				text4 = "TXT_PREV_DOC"
				text5 = modMain.GetText(text4)
				IL_39E:
				num = 44
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_3C6
				End If
				IL_3B0:
				num = 45
				Me.ToolTip1.SetToolTip(Me.cmdPagePrevious, text5)
				IL_3C6:
				num = 46
				text4 = "TXT_PREV"
				text5 = modMain.GetText(text4)
				IL_3D9:
				num = 47
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_401
				End If
				IL_3EB:
				num = 48
				Me.ToolTip1.SetToolTip(Me.cmdPrevious, text5)
				IL_401:
				num = 49
				text4 = "TXT_NEXT"
				text5 = modMain.GetText(text4)
				IL_414:
				num = 50
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_43C
				End If
				IL_426:
				num = 51
				Me.ToolTip1.SetToolTip(Me.cmdNext, text5)
				IL_43C:
				num = 52
				text4 = "TXT_LAST"
				text5 = modMain.GetText(text4)
				IL_44F:
				num = 53
				If Operators.CompareString(text5, "", False) = 0 Then
					GoTo IL_477
				End If
				IL_461:
				num = 54
				Me.ToolTip1.SetToolTip(Me.cmdLast, text5)
				IL_477:
				num = 55
				Me.tabSettings.SelectedIndex = 3
				IL_486:
				num = 56
				Dim form As Form = Me
				modMain.SetTexts(form)
				IL_493:
				num = 57
				Dim text6 As String
				Dim num4 As Short
				modMain.HeaderCount = CShort(Me.lstHeader.Items.Count)
				IL_4AC:
				num = 58
				modMain.RecordCount = CShort(Me.lstRecords.Items.Count)
				IL_4C5:
				num = 59
				modMain.TrailerCount = CShort(Me.lstTrailer.Items.Count)
				IL_4DE:
				num = 60
				text6 = Application.StartupPath + "\fileconverter.txt"
				IL_4F2:
				num = 61
				text4 = "TXT_FILE_PRESENT"
				If Operators.CompareString(modMain.GetText(text4), "", False) = 0 Then
					GoTo IL_645
				End If
				IL_513:
				num = 62
				Me.lstHeader.Items.Clear()
				IL_526:
				num = 63
				num4 = modMain.HeaderCount - 1S
				num3 = 0S
				While num3 <= num4
					IL_538:
					num = 64
					Me.lstHeader.Items.Add(modMain.GiveIni(text6, "frmFilmPreview", "lstHeader." + Conversions.ToString(CInt(num3))))
					IL_569:
					num = 65
					num3 += 1S
				End While
				IL_579:
				num = 66
				Me.lstRecords.Items.Clear()
				IL_58C:
				num = 67
				Dim num5 As Short = modMain.RecordCount - 1S
				num3 = 0S
				While num3 <= num5
					IL_59E:
					num = 68
					Me.lstRecords.Items.Add(modMain.GiveIni(text6, "frmFilmPreview", "lstRecords." + Conversions.ToString(CInt(num3))))
					IL_5CF:
					num = 69
					num3 += 1S
				End While
				IL_5DF:
				num = 70
				Me.lstTrailer.Items.Clear()
				IL_5F2:
				num = 71
				Dim num6 As Short = modMain.TrailerCount - 1S
				num3 = 0S
				While num3 <= num6
					IL_604:
					num = 72
					Me.lstTrailer.Items.Add(modMain.GiveIni(text6, "frmFilmPreview", "lstTrailer." + Conversions.ToString(CInt(num3))))
					IL_635:
					num = 73
					num3 += 1S
				End While
				IL_645:
				num = 74
				Dim num7 As Short = modMain.HeaderCount - 1S
				num3 = 0S
				While num3 <= num7
					IL_657:
					num = 75
					modMain.Headers(CInt(num3)) = Conversions.ToString(Me.lstHeader.Items(CInt(num3)))
					IL_679:
					num = 76
					num3 += 1S
				End While
				IL_689:
				num = 77
				Dim num8 As Short = modMain.TrailerCount - 1S
				num3 = 0S
				While num3 <= num8
					IL_69B:
					num = 78
					modMain.Trailers(CInt(num3)) = Conversions.ToString(Me.lstTrailer.Items(CInt(num3)))
					IL_6BD:
					num = 79
					num3 += 1S
				End While
				IL_6CD:
				num = 80
				Dim num9 As Short = modMain.RecordCount - 1S
				num3 = 0S
				While num3 <= num9
					IL_6DF:
					num = 81
					modMain.Records(CInt(num3)) = Conversions.ToString(Me.lstRecords.Items(CInt(num3)))
					IL_701:
					num = 82
					num3 += 1S
				End While
				IL_711:
				num = 83
				Dim num10 As Short = CShort(FileSystem.FreeFile())
				IL_71C:
				num = 84
				num3 = 0S
				Do
					IL_722:
					num = 85
					Me.SetShpFilmedBackColor(CInt(num3), ColorTranslator.FromOle(Information.RGB(255, 255, 255)))
					IL_746:
					num = 86
					num3 += 1S
				Loop While num3 <= 5S
				IL_755:
				num = 87
				text5 = ""
				IL_75F:
				ProjectData.ClearProjectError()
				num11 = 1
				IL_766:
				num = 89
				FileSystem.FileOpen(CInt(num10), MyProject.Application.Info.DirectoryPath + "\CurrentFilmNo.txt", OpenMode.Input, OpenAccess.[Default], OpenShare.[Default], -1)
				IL_78D:
				num = 90
				Dim str As String = FileSystem.LineInput(CInt(num10))
				IL_799:
				num = 91
				FileSystem.FileClose(New Integer() { CInt(num10) })
				IL_7AC:
				num = 92
				Me.txtFilmNr.Text = Conversions.ToString(Conversion.Val("0" + str))
				IL_7D0:
				num = 93
				text5 = ""
				IL_7DA:
				num = 94
				If Not File.Exists(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt") Then
					GoTo IL_872
				End If
				IL_7FD:
				num = 95
				Dim streamReader As StreamReader = New StreamReader(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", Encoding.Unicode)
				IL_825:
				num = 96
				If streamReader.Peek() = -1 Then
					GoTo IL_83E
				End If
				IL_832:
				num = 97
				text5 = streamReader.ReadLine()
				IL_83E:
				num = 98
				If streamReader.Peek() = -1 Then
					GoTo IL_868
				End If
				IL_84B:
				num = 99
				Dim value2 As String = streamReader.ReadLine()
				IL_857:
				num = 100
				text = Conversions.ToString(Convert.ToInt32(value2))
				IL_868:
				num = 101
				streamReader.Close()
				IL_872:
				num = 102
				Dim text7 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_890:
				num = 103
				modDeclares.Blip1Counter = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text7, "BLIPS", "Blip1Counter"))))
				IL_8B4:
				num = 104
				modDeclares.Blip2Counter = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text7, "BLIPS", "Blip2Counter"))))
				IL_8D8:
				num = 105
				modDeclares.Blip3Counter = CInt(Math.Round(Conversion.Val(modMain.GiveIni(text7, "BLIPS", "Blip3Counter"))))
				IL_8FC:
				num = 106
				Dim text8 As String = text5
				IL_903:
				num = 107
				Me.txtLastDocument.Text = text8
				IL_913:
				num = 108
				Me.txtPage.Text = text
				IL_923:
				num = 109
				text5 = Conversions.ToString(0)
				IL_92E:
				num = 110
				Dim txtRestAufnahmen As TextBox = Me.txtRestAufnahmen
				Dim text3 As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				text4 = modMain.GiveIni(text3, "SYSTEM", "RESTLAENGE" + Conversions.ToString(CInt(value)))
				txtRestAufnahmen.Text = Support.Format(Conversion.Val(modMain.KommazuPunkt(text4)), "0#.00", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				IL_993:
				num = 111
				modPaint.pos = 0
				IL_99C:
				num = 112
				modPaint.LastIndex = -1S
				IL_9A5:
				num = 113
				Dim glbOrientation As Boolean = modDeclares.glbOrientation
				IL_9AE:
				num = 115
				Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
				IL_9DE:
				num = 116
				modMain.SelImage = 0
				IL_9E7:
				num = 117
				Dim comboBox As ComboBox = Me.cmbTemplate
				IL_9F2:
				num = 118
				comboBox.Items.Clear()
				IL_A01:
				num = 119
				Dim text9 As String = FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\TEMPLATES\*.*", Microsoft.VisualBasic.FileAttribute.Normal)
				While True
					IL_A64:
					num = 121
					If Operators.CompareString(text9, "", False) = 0 Then
						Exit For
					End If
					IL_A26:
					num = 122
					If Operators.CompareString(text9, ".", False) <> 0 And Operators.CompareString(text9, "..", False) <> 0 Then
						IL_A4A:
						num = 123
						comboBox.Items.Add(text9)
					End If
					IL_A5B:
					num = 124
					text9 = FileSystem.Dir()
				End While
				IL_A75:
				comboBox = Nothing
				IL_A78:
				ProjectData.ClearProjectError()
				num11 = 1
				IL_A7F:
				num = 128
				MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_A9F:
				num = 129
				MyProject.Forms.frmLoading.Show()
				IL_AB4:
				num = 130
				MyProject.Forms.frmLoading.ProgressBar1.Visible = True
				IL_ACF:
				num = 131
				Application.DoEvents()
				IL_ADA:
				num = 132
				Me.cmbTemplate.Text = modDeclares.glbTemplate
				IL_AF0:
				num = 133
				MyProject.Forms.frmLoading.Close()
				IL_B05:
				num = 134
				Application.DoEvents()
				IL_B10:
				num = 135
				If modDeclares.SystemData.SplitLicenseOK Then
					GoTo IL_B46
				End If
				IL_B22:
				num = 136
				Me.chkSplit.CheckState = CheckState.Unchecked
				IL_B34:
				num = 137
				Me.chkSplit.Enabled = False
				IL_B46:
				num = 138
				Me.tabSettings.SelectedIndex = 10
				IL_B59:
				num = 139
				Me.tabSettings.Text = ""
				IL_B6F:
				num = 140
				Me.Text = MyProject.Forms.frmSMAMain.Text
				IL_B8A:
				num = 141
				modMain.GetAvailableMem()
				IL_B96:
				GoTo IL_E20
				IL_B9B:
				Dim num12 As Integer = num13 + 1
				num13 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num12)
				IL_DE1:
				GoTo IL_E15
				IL_DE3:
				num13 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num11)
				IL_DF3:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num11 <> 0 And num13 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_DE3
			End Try
			IL_E15:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_E20:
			If num13 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x0600080C RID: 2060 RVA: 0x000397A0 File Offset: 0x000379A0
		Private Function CheckData() As Boolean
			Dim result As Boolean = True
			If Me.chkAnnotation.CheckState = CheckState.Checked Then
				If Conversion.Val("0" + Me.txtAnnoBreite.Text) = 0.0 Or Conversion.Val("0" + Me.txtAnnoHoehe.Text) = 0.0 Then
					Dim text As String = "TXT_ANNOWIN_MISSING"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Die Breite und Höhe des Annotationfensters müssen gesetzt sein!"
						left = "Please enter the dimensions of the annotation window!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					result = False
					Me.tabSettings.SelectedIndex = 4
					Return result
				End If
				Conversions.ToDouble(Me.txtAnnoHoehe.Text)
			End If
			If(Me.chkBlip.CheckState = CheckState.Checked And Me.chkAnnotation.CheckState = CheckState.Checked) AndAlso (Operators.CompareString(Me.txtAnnoBreite.Text, Me.txtQuerBlipBreite.Text, False) = 0 And Operators.CompareString(Me.txtAnnoHoehe.Text, Me.txtQuerBlipHoehe.Text, False) = 0) Then
				Dim text As String = "TXT_ANNOWIN_CHECK"
				Dim left As String = modMain.GetText(text)
				If Operators.CompareString(left, "", False) = 0 Then
					left = "Annotationfenster und Blipfenster sind identisch! Bitte überpüfen!"
					left = "BLip window And Annotation Window are identical. Please check this!"
				End If
				Dim num As Short = 0S
				text = "file-converter"
				modMain.msgbox2(left, num, text)
				result = False
				Me.tabSettings.SelectedIndex = 4
			Else
				If Me.chkStartFrame.CheckState = CheckState.Checked Then
					If Not Versioned.IsNumeric(Me.txtRollNoLen.Text) Then
						Dim text As String = "TXT_NO_LEN_ROLLNO"
						Dim left As String = modMain.GetText(text)
						If Operators.CompareString(left, "", False) = 0 Then
							left = "Bitte einen Wert für die Länge der Rollennummer angeben!!"
							left = "Please enter a numerical value for the roll number length!!"
						End If
						Dim num As Short = 0S
						text = "file-converter"
						modMain.msgbox2(left, num, text)
						result = False
						Me.tabSettings.SelectedIndex = 3
						Me.tabFrames.SelectedIndex = 0
						Me.txtRollNoLen.Focus()
						Return result
					End If
					If Conversion.Val(Me.txtRollNoLen.Text) < 1.0 Then
						Dim text As String = "TXT_WRONG_LEN_ROLLNO"
						Dim left As String = modMain.GetText(text)
						If Operators.CompareString(left, "", False) = 0 Then
							left = "Bitte einen Wert größer Null für die Länge der Rollennummer angeben!!"
							left = "Please enter a value > 0 for the roll number length!!"
						End If
						Dim num As Short = 0S
						text = "file-converter"
						modMain.msgbox2(left, num, text)
						result = False
						Me.tabSettings.SelectedIndex = 3
						Me.tabFrames.SelectedIndex = 0
						Me.txtRollNoLen.Focus()
						Return result
					End If
					If Not Versioned.IsNumeric(Me.txtRollNoSize.Text) Then
						Dim text As String = "TXT_NO_FONT_SIZE_ROLLNO"
						Dim left As String = modMain.GetText(text)
						If Operators.CompareString(left, "", False) = 0 Then
							left = "Bitte einen Wert für die Schriftgröße der Rollennummer angeben!!"
							left = "Please enter a font size for the roll number!!"
						End If
						Dim num As Short = 0S
						text = "file-converter"
						modMain.msgbox2(left, num, text)
						result = False
						Me.tabSettings.SelectedIndex = 3
						Me.tabFrames.SelectedIndex = 0
						Me.txtRollNoSize.Focus()
						Return result
					End If
				End If
				If Me.chkFramesWiederholen.CheckState = CheckState.Checked Then
					If Me.chkBaende.CheckState = CheckState.Checked Then
						Dim text As String = "TXT_BAENDE_AND_REPEAT_CHECKED"
						Dim left As String = modMain.GetText(text)
						If Operators.CompareString(left, "", False) = 0 Then
							left = "Wenn Bände nicht gesplittet werden, kann die Frame-Wiederholung nicht aktiviert werden!"
							left = "You can't repeat frames if volumes aren't split over multiple rolls!"
						End If
						Dim num As Short = 0S
						text = "file-converter"
						modMain.msgbox2(left, num, text)
						result = False
						Me.tabSettings.SelectedIndex = 3
						Me.tabFrames.SelectedIndex = 2
						Me.txtFramesWiederholen.Focus()
						Return result
					End If
					If Not Versioned.IsNumeric(Me.txtFramesWiederholen.Text) Then
						Dim text As String = "TXT_ENTER_REPEAT_FRAMES"
						Dim left As String = modMain.GetText(text)
						If Operators.CompareString(left, "", False) = 0 Then
							left = "Bitte einen numerischen Wert für die Anzahl der zu wiederholenden Frames eingeben!"
							left = "Please enter a numerical value for the number of repetition frames!"
						End If
						Dim num As Short = 0S
						text = "file-converter"
						modMain.msgbox2(left, num, text)
						result = False
						Me.tabSettings.SelectedIndex = 3
						Me.tabFrames.SelectedIndex = 2
						Me.txtFramesWiederholen.Focus()
						Return result
					End If
				End If
				If Me.chkUseLogFile.CheckState = CheckState.Checked AndAlso Operators.CompareString(Me.lblLogFile.Text, "", False) = 0 Then
					Dim text As String = "TXT_SET_LOGFILE_FOLDER"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte einen Ordner für die Log-Dateien festlegen!"
						left = "Please set a folder for the log-files!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					result = False
				ElseIf Not Versioned.IsNumeric(Me.txtSchritteBelichtung.Text) Then
					Dim text As String = "TXT_NO_SHUTTER_STEPS"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte die Anzahl der Belichtungen angeben!"
						left = "Please Enter the number of exposures!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					result = False
				ElseIf Conversion.Val(Me.txtSchritteBelichtung.Text) > 128.0 Then
					Dim text As String = "TXT_WRONG_SHUTTER_STEPS"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Die Anzahl der Belichtungen sollte zwischen 1 und 128 liegen!"
						left = "The number of exposures should be between 1 and 128!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					result = False
				ElseIf Me.chkRollewirdfortgesetzt.CheckState = CheckState.Checked AndAlso Operators.CompareString(Me.lblPfadFortsetzungsSymbole1.Text, "", False) = 0 Then
					Dim text As String = "TXT_ADD_SYMBOLS_PATH_MISSING"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte einen Pfad zu den Zusatzsymbolen angeben!"
						left = "Please specify the path to the additional symbols!"
					End If
					result = False
					Me.tabSettings.SelectedIndex = 3
					Me.tabFrames.SelectedIndex = 2
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
				ElseIf Me.chkRolleistFortsetzung.CheckState = CheckState.Checked AndAlso Operators.CompareString(Me.lblPfadFortsetzungsSymbole2.Text, "", False) = 0 Then
					Dim text As String = "TXT_ADD_SYMBOLS_PATH_MISSING"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte einen Pfad zu den Zusatzsymbolen angeben!"
						left = "Please specify the path to the additional symbols!"
					End If
					result = False
					Me.tabSettings.SelectedIndex = 3
					Me.tabFrames.SelectedIndex = 2
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
				ElseIf Me.chkZusatzStartSymbole.CheckState = CheckState.Checked AndAlso Operators.CompareString(Me.lblPfadStartSymbole.Text, "", False) = 0 Then
					Dim text As String = "TXT_ADD_SYMBOLS_PATH_MISSING"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte einen Pfad zu den Zusatzsymbolen angeben!"
						left = "Please specify the path to the additional symbols!"
					End If
					result = False
					Me.tabSettings.SelectedIndex = 3
					Me.tabFrames.SelectedIndex = 0
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
				ElseIf Me.chkZusatzEndSymbole.CheckState = CheckState.Checked AndAlso Operators.CompareString(Me.lblPfadEndSymbole.Text, "", False) = 0 Then
					Dim text As String = "TXT_ADD_SYMBOLS_PATH_MISSING"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Bitte einen Pfad zu den Zusatzsymbolen angeben!"
						left = "Please specify the path to the additional symbols!"
					End If
					Me.tabSettings.SelectedIndex = 3
					Me.tabFrames.SelectedIndex = 3
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					result = False
				End If
			End If
			Return result
		End Function

		' Token: 0x0600080D RID: 2061 RVA: 0x00039EC8 File Offset: 0x000380C8
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub savedata(ByRef Name_Renamed As String)
			Dim num As Integer
			Dim num15 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\TEMPLATES\*.*", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
					GoTo IL_55
				End If
				IL_35:
				num2 = 3
				FileSystem.MkDir(MyProject.Application.Info.DirectoryPath + "\TEMPLATES")
				IL_55:
				num2 = 4
				Dim text As String = Name_Renamed
				IL_5A:
				num2 = 5
				If Operators.CompareString(Support.Format(Strings.Right(Name_Renamed, 4), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), ".TPL", False) = 0 Then
					GoTo IL_8B
				End If
				IL_7D:
				num2 = 6
				text += ".TPL"
				IL_8B:
				num2 = 7
				text = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + text
				IL_A8:
				num2 = 8
				Dim text2 As String = "0"
				IL_B1:
				num2 = 9
				If Me.chkLateStart.CheckState <> CheckState.Checked Then
					GoTo IL_CC
				End If
				IL_C2:
				num2 = 10
				text2 = "1"
				IL_CC:
				num2 = 11
				Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LateStart", text2, text) > False)
				IL_E6:
				num2 = 12
				text2 = "0"
				IL_F0:
				num2 = 13
				If Me.chkJPEG.CheckState <> CheckState.Checked Then
					GoTo IL_10B
				End If
				IL_101:
				num2 = 14
				text2 = "1"
				IL_10B:
				num2 = 15
				Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "JPEGProcessor", text2, text) > False)
				IL_125:
				num2 = 16
				text2 = "0"
				IL_12F:
				num2 = 17
				If Not Me.optOben.Checked Then
					GoTo IL_149
				End If
				IL_13F:
				num2 = 18
				text2 = "1"
				IL_149:
				num2 = 19
				Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "optOben", text2, text) > False)
				IL_163:
				num2 = 20
				text2 = "0"
				IL_16D:
				num2 = 21
				If Not Me.optUnten.Checked Then
					GoTo IL_187
				End If
				IL_17D:
				num2 = 22
				text2 = "1"
				IL_187:
				num2 = 23
				Dim flag4 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "optUnten", text2, text) > False)
				IL_1A1:
				num2 = 24
				text2 = "0"
				IL_1AB:
				num2 = 25
				If Not Me.optCenter.Checked Then
					GoTo IL_1C5
				End If
				IL_1BB:
				num2 = 26
				text2 = "1"
				IL_1C5:
				num2 = 27
				Dim flag5 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "optCenter", text2, text) > False)
				IL_1DF:
				num2 = 28
				text2 = "0"
				IL_1E9:
				num2 = 29
				If Me.chkA3PortraitDrehen.CheckState <> CheckState.Checked Then
					GoTo IL_204
				End If
				IL_1FA:
				num2 = 30
				text2 = "1"
				IL_204:
				num2 = 31
				Dim flag6 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "A3PORTRAITDREHEN", text2, text) > False)
				IL_21E:
				num2 = 32
				text2 = "0"
				IL_228:
				num2 = 33
				If Me.chkA4LSDrehen.CheckState <> CheckState.Checked Then
					GoTo IL_243
				End If
				IL_239:
				num2 = 34
				text2 = "1"
				IL_243:
				num2 = 35
				Dim flag7 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "A4LSDREHEN", text2, text) > False)
				IL_25D:
				num2 = 36
				text2 = "0"
				IL_267:
				num2 = 37
				If Me.chkDuplex.CheckState <> CheckState.Checked Then
					GoTo IL_282
				End If
				IL_278:
				num2 = 38
				text2 = "1"
				IL_282:
				num2 = 39
				If Operators.CompareString(text2, Support.Format(Conversion.Val("0" + modMain.GiveIni(text, "TEMPLATE", "DUPLEX")), "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), False) = 0 Then
					GoTo IL_34C
				End If
				IL_2C3:
				num2 = 40
				Dim text3 As String = "TXT_DUPLEX_INFO1"
				Dim text4 As String = modMain.GetText(text3)
				IL_2D6:
				num2 = 41
				text3 = "TXT_DUPLEX_INFO2"
				Dim str As String = modMain.GetText(text3)
				IL_2E9:
				num2 = 42
				If Operators.CompareString(text4, "", False) <> 0 Then
					GoTo IL_323
				End If
				IL_2FB:
				num2 = 43
				text4 = "Das Ändern der Duplex Verfilmart wirkt sich erst aus,"
				IL_305:
				num2 = 44
				str = "wenn die Dokumente erneut über 'Neue Verfilmung' geladen werden!"
				IL_30F:
				num2 = 45
				text4 = "Changing the Duplex Exposure Process requires "
				IL_319:
				num2 = 46
				str = "to reload the documents via the New Exposure Button!"
				IL_323:
				num2 = 47
				text3 = text4 + vbCr + str
				Dim num3 As Short = 0S
				Dim text5 As String = "file-converter"
				modMain.msgbox2(text3, num3, text5)
				IL_34C:
				num2 = 48
				Dim flag8 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "DUPLEX", text2, text) > False)
				IL_366:
				num2 = 49
				text2 = "0"
				IL_370:
				num2 = 50
				If Not Me.chkTwoLines.Checked Then
					GoTo IL_38A
				End If
				IL_380:
				num2 = 51
				text2 = "1"
				IL_38A:
				num2 = 52
				Dim flag9 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "TWOLINES", text2, text) > False)
				IL_3A4:
				num2 = 53
				text2 = "0"
				IL_3AE:
				num2 = 54
				If Not Me.chkSimDupFilenames.Checked Then
					GoTo IL_3C8
				End If
				IL_3BE:
				num2 = 55
				text2 = "1"
				IL_3C8:
				num2 = 56
				Dim flag10 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SimDupFilenames", text2, text) > False)
				IL_3E2:
				num2 = 57
				text2 = "0"
				IL_3EC:
				num2 = 58
				If Me.chkSmallLeft.CheckState <> CheckState.Checked Then
					GoTo IL_407
				End If
				IL_3FD:
				num2 = 59
				text2 = "1"
				IL_407:
				num2 = 60
				Dim flag11 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SMALLLEFT", text2, text) > False)
				IL_421:
				num2 = 61
				text2 = "0"
				IL_42B:
				num2 = 62
				If Not Versioned.IsNumeric(Me.txtAddRollStartFrameSteps.Text) Then
					GoTo IL_450
				End If
				IL_440:
				num2 = 63
				text2 = Me.txtAddRollStartFrameSteps.Text
				IL_450:
				num2 = 64
				Dim flag12 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddRollStartFrameSteps", text2, text) > False)
				IL_46A:
				num2 = 65
				text2 = "0"
				IL_474:
				num2 = 66
				If Me.chkBigLeft.CheckState <> CheckState.Checked Then
					GoTo IL_48F
				End If
				IL_485:
				num2 = 67
				text2 = "1"
				IL_48F:
				num2 = 68
				Dim flag13 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BIGLEFT", text2, text) > False)
				IL_4A9:
				num2 = 69
				text2 = "0"
				IL_4B3:
				num2 = 70
				If Me.optLagerichtig.CheckState <> CheckState.Checked Then
					GoTo IL_4CE
				End If
				IL_4C4:
				num2 = 71
				text2 = "1"
				IL_4CE:
				num2 = 72
				Dim flag14 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LAGERICHTIG", text2, text) > False)
				IL_4E8:
				num2 = 73
				If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "MaxDUPLEX"), Me.txtMaxDuplex.Text, False) = 0 Then
					GoTo IL_531
				End If
				IL_50F:
				num2 = 74
				text5 = "Changing the Duplex-Document Size Limit is only affected" & vbLf & "if the documents are reloaded via (New Exposure)!"
				num3 = 0S
				text3 = "file-converter"
				modMain.msgbox2(text5, num3, text3)
				GoTo IL_578
				IL_531:
				num2 = 76
				If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "DUPLEXDISTANCE"), Me.txtDuplexDist.Text, False) = 0 Then
					GoTo IL_578
				End If
				IL_558:
				num2 = 77
				text3 = "Changing the Duplex-Document Distance is only affected" & vbLf & "if the documents are reloaded via (New Exposure)!"
				num3 = 0S
				text5 = "file-converter"
				modMain.msgbox2(text3, num3, text5)
				IL_578:
				num2 = 78
				Dim flag15 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "MaxDUPLEX", Me.txtMaxDuplex.Text, text) > False)
				IL_59B:
				num2 = 79
				Dim flag16 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "DUPLEXDISTANCE", Me.txtDuplexDist.Text, text) > False)
				IL_5BE:
				num2 = 80
				text2 = "0"
				IL_5C8:
				num2 = 81
				If Not Me.optRA3.Checked Then
					GoTo IL_5E2
				End If
				IL_5D8:
				num2 = 82
				text2 = "1"
				IL_5E2:
				num2 = 83
				Dim flag17 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RA3", text2, text) > False)
				IL_5FC:
				num2 = 84
				text2 = "0"
				IL_606:
				num2 = 85
				If Not Me.optRA4.Checked Then
					GoTo IL_620
				End If
				IL_616:
				num2 = 86
				text2 = "1"
				IL_620:
				num2 = 87
				Dim flag18 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RA4", text2, text) > False)
				IL_63A:
				num2 = 88
				text2 = "0"
				IL_644:
				num2 = 89
				If Not Me.optLA3.Checked Then
					GoTo IL_65E
				End If
				IL_654:
				num2 = 90
				text2 = "1"
				IL_65E:
				num2 = 91
				Dim flag19 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LA3", text2, text) > False)
				IL_678:
				num2 = 92
				text2 = "0"
				IL_682:
				num2 = 93
				If Not Me.optLA4.Checked Then
					GoTo IL_69C
				End If
				IL_692:
				num2 = 94
				text2 = "1"
				IL_69C:
				num2 = 95
				Dim flag20 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LA4", text2, text) > False)
				IL_6B6:
				num2 = 96
				Dim lpString As String = "0"
				IL_6C0:
				num2 = 97
				If Me.chkFesteBelegzahl.CheckState <> CheckState.Checked Then
					GoTo IL_6DB
				End If
				IL_6D1:
				num2 = 98
				lpString = "1"
				IL_6DB:
				num2 = 99
				Dim flag21 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FesteBelegzahlProFilm", lpString, text) > False)
				IL_6F5:
				num2 = 100
				Dim lpString2 As String = Conversions.ToString(Interaction.IIf(Me.chkAddRollFrame.CheckState = CheckState.Checked, "1", "0"))
				IL_71C:
				num2 = 101
				Dim flag22 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "EnableAddRollFrame", lpString2, text) > False)
				IL_736:
				num2 = 102
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkAddRollFrameInput.CheckState = CheckState.Checked, "1", "0"))
				IL_75D:
				num2 = 103
				Dim flag23 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddRollFrameInput", lpString2, text) > False)
				IL_777:
				num2 = 104
				Dim flag24 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddRollFrameFontSize", Me.txtAddRollFrameSize.Text, text) > False)
				IL_79A:
				num2 = 105
				Dim flag25 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddRollFrameLen", Me.txtAddRollFrameLen.Text, text) > False)
				IL_7BD:
				num2 = 106
				Dim num4 As Short = 1S
				Do
					IL_7C3:
					num2 = 107
					num4 += 1S
				Loop While num4 <= 4S
				IL_7D2:
				num2 = 108
				Dim flag26 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddStepLevel2", Me.txtAddStepLevel2.Text, text) > False)
				IL_7F5:
				num2 = 109
				Dim flag27 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AddStepLevel3", Me.txtAddStepLevel3.Text, text) > False)
				IL_818:
				num2 = 110
				Dim flag28 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RollNoPrefix", Me.txtRollNoPrefix.Text, text) > False)
				IL_83B:
				num2 = 111
				Dim flag29 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RollNoPostfix", Me.txtRollNoPostfix.Text, text) > False)
				IL_85E:
				num2 = 112
				Dim flag30 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RollNoSize", Me.txtRollNoSize.Text, text) > False)
				IL_881:
				num2 = 113
				Dim flag31 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RollNoLen", Me.txtRollNoLen.Text, text) > False)
				IL_8A4:
				num2 = 114
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkBaende.CheckState = CheckState.Checked, "1", "0"))
				IL_8CB:
				num2 = 115
				Dim flag32 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BaendeVollstaendigBelichten", lpString2, text) > False)
				IL_8E5:
				num2 = 116
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkFramesWiederholen.CheckState = CheckState.Checked, "1", "0"))
				IL_90C:
				num2 = 117
				Dim flag33 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FramesWiederholen", lpString2, text) > False)
				IL_926:
				num2 = 118
				Dim flag34 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FramesWiederholenAnzahl", Me.txtFramesWiederholen.Text, text) > False)
				IL_949:
				num2 = 119
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkZusatzStartSymbole.CheckState = CheckState.Checked, "1", "0"))
				IL_970:
				num2 = 120
				Dim flag35 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ZusatzStartSymbole", lpString2, text) > False)
				IL_98A:
				num2 = 121
				Dim flag36 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "PfadZusatzStartSymbole", Me.lblPfadStartSymbole.Text, text) > False)
				IL_9AD:
				num2 = 122
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkZusatzEndSymbole.CheckState = CheckState.Checked, "1", "0"))
				IL_9D4:
				num2 = 123
				Dim flag37 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ZusatzEndSymbole", lpString2, text) > False)
				IL_9EE:
				num2 = 124
				Dim flag38 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "PfadZusatzEndSymbole", Me.lblPfadEndSymbole.Text, text) > False)
				IL_A11:
				num2 = 125
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkRollewirdfortgesetzt.CheckState = CheckState.Checked, "1", "0"))
				IL_A38:
				num2 = 126
				Dim flag39 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FortsetzungsSymbole1", lpString2, text) > False)
				IL_A52:
				num2 = 127
				Dim flag40 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "PfadFortsetzungsSymbole1", Me.lblPfadFortsetzungsSymbole1.Text, text) > False)
				IL_A75:
				num2 = 128
				lpString2 = Conversions.ToString(Me.cmbFortsetzungsLevel.SelectedIndex + 1)
				IL_A8F:
				num2 = 129
				Dim flag41 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FortsetzungsLevel", lpString2, text) > False)
				IL_AAC:
				num2 = 130
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkRolleistFortsetzung.CheckState = CheckState.Checked, "1", "0"))
				IL_AD6:
				num2 = 131
				Dim flag42 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FortsetzungsSymbole2", lpString2, text) > False)
				IL_AF3:
				num2 = 132
				Dim flag43 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "PfadFortsetzungsSymbole2", Me.lblPfadFortsetzungsSymbole2.Text, text) > False)
				IL_B19:
				num2 = 133
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkNoSpecialSmybolesWhenContinuation.CheckState = CheckState.Checked, "1", "0"))
				IL_B43:
				num2 = 134
				Dim flag44 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "NoSpecialSmybolesWhenContinuation", lpString2, text) > False)
				IL_B60:
				num2 = 135
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkBlip.CheckState = CheckState.Checked, "1", "0"))
				IL_B8A:
				num2 = 136
				Dim flag45 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BLIP", lpString2, text) > False)
				IL_BA7:
				num2 = 137
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkStartBlipAtOne.CheckState = CheckState.Checked, "1", "0"))
				IL_BD1:
				num2 = 138
				Dim flag46 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "StartBlipAtOne", lpString2, text) > False)
				IL_BEE:
				num2 = 139
				Dim flag47 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "PDFRESO", Me.cmbPDFReso.Text, text) > False)
				IL_C14:
				num2 = 140
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkRollEndFrame.CheckState = CheckState.Checked, "1", "0"))
				IL_C3E:
				num2 = 141
				Dim flag48 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RollEndFrame", lpString2, text) > False)
				IL_C5B:
				num2 = 142
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkShowSize.CheckState = CheckState.Checked, "1", "0"))
				IL_C85:
				num2 = 143
				Dim flag49 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ShowSize", lpString2, text) > False)
				IL_CA2:
				num2 = 144
				lpString2 = Conversions.ToString(Me.cmbPapierGroesse.SelectedIndex)
				IL_CBA:
				num2 = 145
				Dim flag50 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "Papiergroesseformat", lpString2, text) > False)
				IL_CD7:
				num2 = 146
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkUseIndex.CheckState = CheckState.Checked, "1", "0"))
				IL_D01:
				num2 = 147
				Dim flag51 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "UseIndex", lpString2, text) > False)
				IL_D1E:
				num2 = 148
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkInvers.CheckState = CheckState.Checked, "1", "0"))
				IL_D48:
				num2 = 149
				Dim flag52 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "INVERS", lpString2, text) > False)
				IL_D65:
				num2 = 150
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkFrame.CheckState = CheckState.Checked, "1", "0"))
				IL_D8F:
				num2 = 151
				Dim flag53 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "USEFRAME", lpString2, text) > False)
				IL_DAC:
				num2 = 152
				lpString2 = "0"
				IL_DB9:
				num2 = 153
				If Not Me.radWhiteFrame.Checked Then
					GoTo IL_DD9
				End If
				IL_DCC:
				num2 = 154
				lpString2 = "1"
				IL_DD9:
				num2 = 155
				Dim flag54 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "optWeisserRahmen_0", lpString2, text) > False)
				IL_DF6:
				num2 = 156
				lpString2 = "0"
				IL_E03:
				num2 = 157
				If Not Me.radBlackFrame.Checked Then
					GoTo IL_E23
				End If
				IL_E16:
				num2 = 158
				lpString2 = "1"
				IL_E23:
				num2 = 159
				Dim flag55 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "optWeisserRahmen_1", lpString2, text) > False)
				IL_E40:
				num2 = 160
				Dim flag56 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "txtRahmendicke", Me.txtFrameWidth.Text, text) > False)
				IL_E66:
				num2 = 161
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkAutoAlign.CheckState = CheckState.Checked, "1", "0"))
				IL_E90:
				num2 = 162
				Dim flag57 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AUTOALIGN", lpString2, text) > False)
				IL_EAD:
				num2 = 163
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkAutoAlign180.CheckState = CheckState.Checked, "1", "0"))
				IL_ED7:
				num2 = 164
				Dim flag58 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AutoAlign180", lpString2, text) > False)
				IL_EF4:
				num2 = 165
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkUseFrameNo.CheckState = CheckState.Checked, "1", "0"))
				IL_F1E:
				num2 = 166
				Dim flag59 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "UseFrameNo", lpString2, text) > False)
				IL_F3B:
				num2 = 167
				lpString2 = "90"
				IL_F48:
				num2 = 168
				If Not Me.opt270.Checked Then
					GoTo IL_F68
				End If
				IL_F5B:
				num2 = 169
				lpString2 = "270"
				IL_F68:
				num2 = 170
				Dim flag60 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AUTOORIENTATION", lpString2, text) > False)
				IL_F85:
				num2 = 171
				lpString2 = "90"
				IL_F92:
				num2 = 172
				If Not Me.optFest180.Checked Then
					GoTo IL_FB2
				End If
				IL_FA5:
				num2 = 173
				lpString2 = "180"
				IL_FB2:
				num2 = 174
				If Not Me.optFest270.Checked Then
					GoTo IL_FD2
				End If
				IL_FC5:
				num2 = 175
				lpString2 = "270"
				IL_FD2:
				num2 = 176
				If Not Me.optFest0.Checked Then
					GoTo IL_FF2
				End If
				IL_FE5:
				num2 = 177
				lpString2 = "0"
				IL_FF2:
				num2 = 178
				Dim flag61 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ROTATION", lpString2, text) > False)
				IL_100F:
				num2 = 179
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkAnnotation.CheckState = CheckState.Checked, "1", "0"))
				IL_1039:
				num2 = 180
				Dim flag62 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ANNOTATION", lpString2, text) > False)
				IL_1056:
				num2 = 181
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkIgnoreChars.CheckState = CheckState.Checked, "1", "0"))
				IL_1080:
				num2 = 182
				Dim flag63 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "IgnoreChars", lpString2, text) > False)
				IL_109D:
				num2 = 183
				lpString2 = Me.txtIgnoreCharsCount.Text
				IL_10B0:
				num2 = 184
				Dim flag64 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "IgnoreCharsCount", lpString2, text) > False)
				IL_10CD:
				num2 = 185
				lpString2 = Conversions.ToString(Interaction.IIf(Me.optNebenBlip.Checked, "1", "0"))
				IL_10F4:
				num2 = 186
				Dim flag65 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "POSITION", lpString2, text) > False)
				IL_1111:
				num2 = 187
				If Not Me.optNamen.Checked Then
					GoTo IL_1131
				End If
				IL_1124:
				num2 = 188
				lpString2 = "0"
				IL_1131:
				num2 = 189
				If Not Me.optNummer.Checked Then
					GoTo IL_1151
				End If
				IL_1144:
				num2 = 190
				lpString2 = "1"
				IL_1151:
				num2 = 191
				If Not Me.optMulti.Checked Then
					GoTo IL_1171
				End If
				IL_1164:
				num2 = 192
				lpString2 = "3"
				IL_1171:
				num2 = 193
				If Not Me.optNummer.Checked Then
					GoTo IL_1191
				End If
				IL_1184:
				num2 = 194
				lpString2 = "4"
				IL_1191:
				num2 = 195
				If Not Me.optDreiTeilig.Checked Then
					GoTo IL_11B1
				End If
				IL_11A4:
				num2 = 196
				lpString2 = "5"
				IL_11B1:
				num2 = 197
				If Not Me.optBlipAnno.Checked Then
					GoTo IL_11D1
				End If
				IL_11C4:
				num2 = 198
				lpString2 = "6"
				IL_11D1:
				num2 = 199
				Dim flag66 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "FORMAT", lpString2, text) > False)
				IL_11EE:
				num2 = 200
				Dim flag67 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AnnoBlipLen", Me.txtAnnoBlipLen.Text, text) > False)
				IL_1214:
				num2 = 201
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkTrailerInfoFrames.CheckState = CheckState.Checked, "1", "0"))
				IL_123E:
				num2 = 202
				Dim flag68 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "TrailerInfoFrames", lpString2, text) > False)
				IL_125B:
				num2 = 203
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkStartFrame.CheckState = CheckState.Checked, "1", "0"))
				IL_1285:
				num2 = 204
				Dim flag69 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "STARTFRAME", lpString2, text) > False)
				IL_12A2:
				num2 = 205
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkSeparateFrame.CheckState = CheckState.Checked, "1", "0"))
				IL_12CC:
				num2 = 206
				Dim flag70 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SEPARATIONFRAME", lpString2, text) > False)
				IL_12E9:
				num2 = 207
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkSplit.CheckState = CheckState.Checked, "1", "0"))
				IL_1313:
				num2 = 208
				Dim flag71 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "DOSPLIT", lpString2, text) > False)
				IL_1330:
				num2 = 209
				lpString2 = Conversions.ToString(Me.cmbMaxDocumentSize.SelectedIndex)
				IL_1348:
				num2 = 210
				Dim flag72 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SIZE-FORMAT", lpString2, text) > False)
				IL_1365:
				num2 = 211
				Dim flag73 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SIZE-X", Me.txtSplitBreite.Text, text) > False)
				IL_138B:
				num2 = 212
				Dim flag74 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SIZE-Y", Me.txtSplitLaenge.Text, text) > False)
				IL_13B1:
				num2 = 213
				Dim flag75 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SPLIT-COUNT", Me.cmbSplitCount.Text, text) > False)
				IL_13D7:
				num2 = 214
				Dim flag76 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "SPLIT-OVERSIZE", Me.txtOverSize.Text, text) > False)
				IL_13FD:
				num2 = 215
				Dim flag77 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "START", Me.txtStart.Text, text) > False)
				IL_1423:
				num2 = 216
				Dim flag78 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LAENGE", Me.txtLen.Text, text) > False)
				IL_1449:
				num2 = 217
				Dim flag79 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BLIPLEVEL1", Support.Format(Me.cmbBlipLevel1.SelectedIndex, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), text) > False)
				IL_1480:
				num2 = 218
				Dim flag80 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BLIPLEVEL2", Support.Format(Me.cmbBlipLevel2.SelectedIndex, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), text) > False)
				IL_14B7:
				num2 = 219
				Dim flag81 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BLIPLEVEL3", Support.Format(Me.cmbBlipLevel3.SelectedIndex, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), text) > False)
				IL_14EE:
				num2 = 220
				Dim flag82 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerHoehe", Me.txtQuerHoehe.Text, text) > False)
				IL_1514:
				num2 = 221
				Dim flag83 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerBreite", Me.txtQuerBreite.Text, text) > False)
				IL_153A:
				num2 = 222
				Dim flag84 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerX", Me.txtQuerX.Text, text) > False)
				IL_1560:
				num2 = 223
				Dim flag85 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerY", Me.txtQuerY.Text, text) > False)
				IL_1586:
				num2 = 224
				Dim flag86 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerBlipBreite", Me.txtQuerBlipBreite.Text, text) > False)
				IL_15AC:
				num2 = 225
				Dim flag87 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerBlipHoehe", Me.txtQuerBlipHoehe.Text, text) > False)
				IL_15D2:
				num2 = 226
				Dim flag88 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerBlipX", Me.txtQuerBlipX.Text, text) > False)
				IL_15F8:
				num2 = 227
				Dim flag89 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerBlipY", Me.txtQuerBlipY.Text, text) > False)
				IL_161E:
				num2 = 228
				Dim flag90 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoBreite", Me.txtInfoBreite.Text, text) > False)
				IL_1644:
				num2 = 229
				Dim flag91 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoHoehe", Me.txtInfoHoehe.Text, text) > False)
				IL_166A:
				num2 = 230
				Dim flag92 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoX", Me.txtInfoX.Text, text) > False)
				IL_1690:
				num2 = 231
				Dim flag93 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoY", Me.txtInfoY.Text, text) > False)
				IL_16B6:
				num2 = 232
				Dim flag94 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AnnoBreite", Me.txtAnnoBreite.Text, text) > False)
				IL_16DC:
				num2 = 233
				Dim flag95 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AnnoHoehe", Me.txtAnnoHoehe.Text, text) > False)
				IL_1702:
				num2 = 234
				Dim flag96 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AnnoX", Me.txtAnnoX.Text, text) > False)
				IL_1728:
				num2 = 235
				Dim flag97 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AnnoY", Me.txtAnnoY.Text, text) > False)
				IL_174E:
				num2 = 236
				Dim flag98 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerAusrichtung", Me.txtQuerAusrichtung.Text, text) > False)
				IL_1774:
				num2 = 237
				Dim flag99 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerAnnoX", Me.txtQuerAnnoX.Text, text) > False)
				IL_179A:
				num2 = 238
				Dim flag100 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerAnnoY", Me.txtQuerAnnoY.Text, text) > False)
				IL_17C0:
				num2 = 239
				Dim flag101 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerFont", Me.txtQuerFont.Text, text) > False)
				IL_17E6:
				num2 = 240
				Dim flag102 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "QuerGewicht", Me.txtQuerGewicht.Text, text) > False)
				IL_180C:
				num2 = 241
				Dim flag103 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoTextAusrichtung", Me.txtInfoTextAusrichtung.Text, text) > False)
				IL_1832:
				num2 = 242
				Dim flag104 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoTextX", Me.txtInfoTextX.Text, text) > False)
				IL_1858:
				num2 = 243
				Dim flag105 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoTextY", Me.txtInfoTextY.Text, text) > False)
				IL_187E:
				num2 = 244
				Dim flag106 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoTextFont", Me.txtInfoTextFont.Text, text) > False)
				IL_18A4:
				num2 = 245
				Dim flag107 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "InfoTextGewicht", Me.txtInfoTextGewicht.Text, text) > False)
				IL_18CA:
				num2 = 246
				num4 = 0S
				IL_18D3:
				num2 = 247
				Dim flag108 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipBreiteGross" + Conversions.ToString(CInt(num4)), Me._txtBlipBreiteGross_0.Text, text) > False)
				IL_1905:
				num2 = 248
				Dim flag109 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipBreiteKlein" + Conversions.ToString(CInt(num4)), Me._txtBlipBreiteKlein_0.Text, text) > False)
				IL_1937:
				num2 = 249
				Dim flag110 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipBreiteMittel" + Conversions.ToString(CInt(num4)), Me._txtBlipBreiteMittel_0.Text, text) > False)
				IL_1969:
				num2 = 250
				Dim flag111 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipHoeheGross" + Conversions.ToString(CInt(num4)), Me._txtBlipHoeheGross_0.Text, text) > False)
				IL_199B:
				num2 = 251
				Dim flag112 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipHoeheKlein" + Conversions.ToString(CInt(num4)), Me._txtBlipHoeheKlein_0.Text, text) > False)
				IL_19CD:
				num2 = 252
				Dim flag113 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BlipHoeheMittel" + Conversions.ToString(CInt(num4)), Me._txtBlipHoeheMittel_0.Text, text) > False)
				IL_19FF:
				num2 = 253
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkStepsImageToImage.CheckState = CheckState.Checked, "1", "0"))
				IL_1A29:
				num2 = 254
				Dim flag114 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "StepsImageToImage", lpString2, text) > False)
				IL_1A46:
				num2 = 255
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkOneToOne.CheckState = CheckState.Checked, "1", "0"))
				IL_1A70:
				num2 = 256
				Dim flag115 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "OneToOneExposure", lpString2, text) > False)
				IL_1A8D:
				num2 = 257
				Dim flag116 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "OneToOneFactor", Me.txtFactor.Text, text) > False)
				IL_1AB3:
				num2 = 258
				Dim flag117 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "Toleranz", Me.txtToleranz.Text, text) > False)
				IL_1AD9:
				num2 = 259
				Dim flag118 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "Schrittweite", Me.txtSchritte.Text, text) > False)
				IL_1AFF:
				num2 = 260
				Dim flag119 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "VerschlussGeschw", Me._txtVerschluss_0.Text, text) > False)
				IL_1B25:
				num2 = 261
				Dim flag120 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "ZusatzBelichtung", Me.txtZusatzBelichtung.Text, text) > False)
				IL_1B4B:
				num2 = 262
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkAutoTrailer.CheckState = CheckState.Checked, "1", "0"))
				IL_1B75:
				num2 = 263
				Dim flag121 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AutoTrailer", lpString2, text) > False)
				IL_1B92:
				num2 = 264
				Dim flag122 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AutoTrailerDistance", Me.txtAutoTrailerDistance.Text, text) > False)
				IL_1BB8:
				num2 = 265
				Dim flag123 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "AutoTrailerLength", Me.txtAutoTrailerLength.Text, text) > False)
				IL_1BDE:
				num2 = 266
				Dim lpString3 As String = Support.Format(Conversion.Val(Me.txtSchritteBelichtung.Text), "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
				IL_1C07:
				num2 = 267
				Dim flag124 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "BELICHTUNG", lpString3, text) > False)
				IL_1C24:
				num2 = 268
				lpString2 = Conversions.ToString(Interaction.IIf(Me.chkNoPreview.CheckState = CheckState.Checked, "1", "0"))
				IL_1C4E:
				num2 = 269
				Dim flag125 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "NoPreview", lpString2, text) > False)
				IL_1C6B:
				num2 = 270
				Dim flag126 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "CAMERAHEAD", Me.cmbKopf.Text, text) > False)
				IL_1C91:
				num2 = 271
				If Me.chkUseLogFile.CheckState <> CheckState.Checked Then
					GoTo IL_1CB4
				End If
				IL_1CA5:
				num2 = 272
				lpString2 = "1"
				GoTo IL_1CC1
				IL_1CB4:
				num2 = 274
				lpString2 = "0"
				IL_1CC1:
				num2 = 275
				Dim flag127 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "USELOGFILE", lpString2, text) > False)
				IL_1CDE:
				num2 = 276
				Dim flag128 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "LOGFILEPATH", Me.lblLogFile.Text, text) > False)
				IL_1D04:
				num2 = 277
				Dim flag129 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "DELIMITER", Me.cmbDelimiter.Text, text) > False)
				IL_1D2A:
				num2 = 278
				num3 = modMain.HeaderCount - 1S
				num4 = 0S
				While num4 <= num3
					IL_1D42:
					num2 = 279
					Dim num5 As Short = modMain.HeaderCount - 1S
					For num6 As Short = 0S To num5
						IL_1D57:
						num2 = 280
						If Operators.CompareString(modMain.Headers(CInt(num4)), Support.GetItemString(Me.lstHeader, CInt(num6)), False) = 0 Then
							IL_1D7A:
							num2 = 281
							lpString = Support.Format(num6, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							IL_1D95:
							num2 = 282
							Dim flag130 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "HEADER" + Conversions.ToString(CInt(num4)), lpString, text) > False)
						End If
						IL_1DBE:
						num2 = 283
					Next
					IL_1DD1:
					num2 = 284
					num4 += 1S
				End While
				IL_1DE7:
				num2 = 285
				Dim num7 As Short = modMain.TrailerCount - 1S
				num4 = 0S
				While num4 <= num7
					IL_1DFF:
					num2 = 286
					Dim num8 As Short = modMain.TrailerCount - 1S
					For num6 As Short = 0S To num8
						IL_1E14:
						num2 = 287
						If Operators.CompareString(modMain.Trailers(CInt(num4)), Support.GetItemString(Me.lstTrailer, CInt(num6)), False) = 0 Then
							IL_1E37:
							num2 = 288
							lpString = Support.Format(num6, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							IL_1E52:
							num2 = 289
							Dim flag131 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "Trailer" + Conversions.ToString(CInt(num4)), lpString, text) > False)
						End If
						IL_1E7B:
						num2 = 290
					Next
					IL_1E8E:
					num2 = 291
					num4 += 1S
				End While
				IL_1EA4:
				num2 = 292
				Dim num9 As Short = modMain.RecordCount - 1S
				num4 = 0S
				While num4 <= num9
					IL_1EBC:
					num2 = 293
					Dim num10 As Short = modMain.RecordCount - 1S
					For num6 As Short = 0S To num10
						IL_1ED1:
						num2 = 294
						If Operators.CompareString(modMain.Records(CInt(num4)), Support.GetItemString(Me.lstRecords, CInt(num6)), False) = 0 Then
							IL_1EF4:
							num2 = 295
							lpString = Support.Format(num6, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							IL_1F0F:
							num2 = 296
							Dim flag132 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RECORDS" + Conversions.ToString(CInt(num4)), lpString, text) > False)
						End If
						IL_1F38:
						num2 = 297
					Next
					IL_1F4B:
					num2 = 298
					num4 += 1S
				End While
				IL_1F61:
				num2 = 299
				Dim num11 As Short = modMain.HeaderCount - 1S
				num4 = 0S
				While num4 <= num11
					IL_1F76:
					num2 = 300
					lpString2 = "0"
					IL_1F83:
					num2 = 301
					If Me.lstHeader.GetItemChecked(CInt(num4)) Then
						IL_1F98:
						num2 = 302
						lpString2 = "1"
					End If
					IL_1FA5:
					num2 = 303
					Dim flag133 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "HEADERSEL" + Conversions.ToString(CInt(num4)), lpString2, text) > False)
					IL_1FCE:
					num2 = 304
					num4 += 1S
				End While
				IL_1FE1:
				num2 = 305
				Dim num12 As Short = modMain.TrailerCount - 1S
				num4 = 0S
				While num4 <= num12
					IL_1FF6:
					num2 = 306
					lpString2 = "0"
					IL_2003:
					num2 = 307
					If Me.lstTrailer.GetItemChecked(CInt(num4)) Then
						IL_2018:
						num2 = 308
						lpString2 = "1"
					End If
					IL_2025:
					num2 = 309
					Dim flag134 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "TRAILERSEL" + Conversions.ToString(CInt(num4)), lpString2, text) > False)
					IL_204E:
					num2 = 310
					num4 += 1S
				End While
				IL_2061:
				num2 = 311
				Dim num13 As Short = modMain.RecordCount - 1S
				num4 = 0S
				While num4 <= num13
					IL_2076:
					num2 = 312
					lpString2 = "0"
					IL_2083:
					num2 = 313
					If Me.lstRecords.GetItemChecked(CInt(num4)) Then
						IL_2098:
						num2 = 314
						lpString2 = "1"
					End If
					IL_20A5:
					num2 = 315
					Dim flag135 As Boolean = -(modDeclares.WritePrivateProfileString("TEMPLATE", "RECORDSSEL" + Conversions.ToString(CInt(num4)), lpString2, text) > False)
					IL_20CE:
					num2 = 316
					num4 += 1S
				End While
				IL_20E1:
				GoTo IL_2627
				IL_20E6:
				Dim num14 As Integer = num15 + 1
				num15 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num14)
				IL_25E8:
				GoTo IL_261C
				IL_25EA:
				num15 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_25FA:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num15 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_25EA
			End Try
			IL_261C:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_2627:
			If num15 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x0600080E RID: 2062 RVA: 0x0003C520 File Offset: 0x0003A720
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

		' Token: 0x0600080F RID: 2063 RVA: 0x0003E9AC File Offset: 0x0003CBAC
		Private Sub frmFilmPreview_FormClosed(eventSender As Object, eventArgs As FormClosedEventArgs)
			MyProject.Forms.frmBlipWinTest.Close()
			MyProject.Forms.frmImageTest.Close()
			MyProject.Forms.frmAnnoWinTest.Close()
			If Not Information.IsNothing(Me._Picture1_0.Image) Then
				Me._Picture1_0.Image.Dispose()
			End If
			If Not Information.IsNothing(Me._Picture1_1.Image) Then
				Me._Picture1_1.Image.Dispose()
			End If
			If Not Information.IsNothing(Me._Picture1_2.Image) Then
				Me._Picture1_2.Image.Dispose()
			End If
			If Not Information.IsNothing(Me._Picture1_3.Image) Then
				Me._Picture1_3.Image.Dispose()
			End If
			If Not Information.IsNothing(Me._Picture1_4.Image) Then
				Me._Picture1_4.Image.Dispose()
			End If
			If Not Information.IsNothing(Me._Picture1_5.Image) Then
				Me._Picture1_5.Image.Dispose()
			End If
			If modDeclares.IsSMA Then
				MyProject.Forms.frmSMAMain.Show()
				Return
			End If
			MyProject.Forms.frmSMAMain.Show()
		End Sub

		' Token: 0x06000810 RID: 2064 RVA: 0x0003EAD8 File Offset: 0x0003CCD8
		Private Sub lblLevel_Click(eventSender As Object, eventArgs As EventArgs)
			MyProject.Forms.frmList.Show()
			Dim imagecount As Integer = modDeclares.imagecount
			For i As Integer = 0 To imagecount
				MyProject.Forms.frmList.List1.Items.Add(modDeclares.Images(i).Name)
			Next
		End Sub

		' Token: 0x06000811 RID: 2065 RVA: 0x0003EB30 File Offset: 0x0003CD30
		Private Sub lblPos_Click(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = "TXT_INPUT_POS"
			Dim text2 As String = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Please enter the frame number!"
			End If
			Dim text3 As String = Interaction.InputBox(text2, Support.Format(modPaint.pos, "", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "", -1, -1)
			If Versioned.IsNumeric(text3) Then
				' The following expression was wrapped in a unchecked-expression
				modPaint.pos = CInt(Math.Round(Conversion.Val(text3) - 1.0))
				If modPaint.pos > modDeclares.imagecount - 5 Then
					modPaint.pos = modDeclares.imagecount - 5
				End If
				Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000812 RID: 2066 RVA: 0x0003EBF9 File Offset: 0x0003CDF9
		Private Sub lblPos_DoubleClick(eventSender As Object, eventArgs As EventArgs)
			MyProject.Forms.frmPathsInfo.ShowDialog()
		End Sub

		' Token: 0x06000813 RID: 2067 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub opt270_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000814 RID: 2068 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub opt90_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000815 RID: 2069 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optCenter_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000816 RID: 2070 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optDreiTeilig_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000817 RID: 2071 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optFest0_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000818 RID: 2072 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optFest180_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000819 RID: 2073 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optFest270_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x0600081A RID: 2074 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optFest90_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x0600081B RID: 2075 RVA: 0x0003EC60 File Offset: 0x0003CE60
		Private Sub cmdFortsetzung_Click(eventSender As Object, eventArgs As EventArgs)
			If Operators.ConditionalCompareObjectEqual(Me.cmdFortsetzung.Tag, "1", False) Then
				Me.cmdFortsetzung.Tag = "0"
			Else
				Me.cmdFortsetzung.Tag = "1"
				Dim flag As Boolean = Me.chkFramesWiederholen.CheckState = CheckState.Checked And Operators.CompareString(Me.txtFramesWiederholen.Text, "0", False) <> 0
			End If
			If Operators.ConditionalCompareObjectEqual(Me.cmdFortsetzung.Tag, "1", False) Then
				Dim cmdFortsetzung As ButtonBase = Me.cmdFortsetzung
				Dim text As String = "TXT_ROLL_IS_CONT"
				cmdFortsetzung.Text = modMain.GetText(text)
				If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) = 0 Then
					Me.cmdFortsetzung.Text = "Rolle ist Fortsetzung"
					Me.cmdFortsetzung.Text = "Roll is Continuation"
				End If
			Else
				Dim cmdFortsetzung2 As ButtonBase = Me.cmdFortsetzung
				Dim text As String = "TXT_ROLL_IS_NOT_CONT"
				cmdFortsetzung2.Text = modMain.GetText(text)
				If Operators.CompareString(Me.cmdFortsetzung.Text, "", False) = 0 Then
					Me.cmdFortsetzung.Text = "Rolle ist keine Fortsetzung"
					Me.cmdFortsetzung.Text = "Roll is no Continuation"
				End If
			End If
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim num As Integer = 0
			Dim value As Integer
			Do
				If Operators.CompareString(modDeclares.SystemData.kopfname(num), modDeclares.glbKopf, False) = 0 Then
					value = num
				End If
				num += 1
			Loop While num <= 3
			Dim lpString As String = Conversions.ToString(Me.cmdFortsetzung.Tag)
			modDeclares.WritePrivateProfileString("SYSTEM", "CONTINUEROLL" + Conversions.ToString(value), lpString, lpFileName)
		End Sub

		' Token: 0x0600081C RID: 2076 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optLA3_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x0600081D RID: 2077 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optLA4_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x0600081E RID: 2078 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub optLagerichtig_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x0600081F RID: 2079 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optMulti_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000820 RID: 2080 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optNamen_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000821 RID: 2081 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optNebenBlip_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000822 RID: 2082 RVA: 0x0003EDFC File Offset: 0x0003CFFC
		Private Sub optNummer_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				If Me.optNummer.Checked Then
					Me.txtStart.Enabled = True
					Me.Label5.Enabled = True
				Else
					Me.txtStart.Enabled = False
					Me.Label5.Enabled = False
				End If
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000823 RID: 2083 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optOben_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000824 RID: 2084 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optRA3_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000825 RID: 2085 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optRA4_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000826 RID: 2086 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optUeberBlip_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000827 RID: 2087 RVA: 0x0003EC0B File Offset: 0x0003CE0B
		Private Sub optUnten_CheckedChanged(eventSender As Object, eventArgs As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(eventSender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000828 RID: 2088 RVA: 0x0003EE76 File Offset: 0x0003D076
		Private Sub txtFactor_TextChanged(eventSender As Object, eventArgs As EventArgs)
			If Versioned.IsNumeric(Me.txtFactor.Text) AndAlso Conversion.Val(Me.txtFactor.Text) <> 0.0 Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000829 RID: 2089 RVA: 0x0003EEAC File Offset: 0x0003D0AC
		Private Sub txtFactor_KeyPress(eventSender As Object, eventArgs As KeyPressEventArgs)
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(Strings.Asc(eventArgs.KeyChar))
			If num = 13S Then
				Me.UpdateLayout()
			End If
			eventArgs.KeyChar = Strings.Chr(CInt(num))
			If num = 0S Then
				eventArgs.Handled = True
			End If
		End Sub

		' Token: 0x0600082A RID: 2090 RVA: 0x0003EEE8 File Offset: 0x0003D0E8
		Private Sub txtFilmNr_TextChanged(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = Me.txtFilmNr.Text
			While CDbl(Strings.Len(text)) < Conversion.Val("0" + Me.txtRollNoLen.Text)
				text = "0" + text
			End While
			Me.txtFilmNrAufFilm.Text = Me.txtRollNoPrefix.Text + text + Me.txtRollNoPostfix.Text
		End Sub

		' Token: 0x0600082B RID: 2091 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub txtLastDocument_Change(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x0600082C RID: 2092 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub txtLen_TextChanged(eventSender As Object, eventArgs As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x0600082D RID: 2093 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub txtPraefix_TextChanged(eventSender As Object, eventArgs As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x0600082E RID: 2094 RVA: 0x0003EF70 File Offset: 0x0003D170
		Private Sub txtRollNoLen_TextChanged(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = Me.txtFilmNr.Text
			While CDbl(Strings.Len(text)) < Conversion.Val("0" + Me.txtRollNoLen.Text)
				text = "0" + text
			End While
			Me.txtFilmNrAufFilm.Text = Me.txtRollNoPrefix.Text + text + Me.txtRollNoPostfix.Text
		End Sub

		' Token: 0x0600082F RID: 2095 RVA: 0x0003EFE4 File Offset: 0x0003D1E4
		Private Sub txtRollNoPostfix_TextChanged(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = Me.txtFilmNr.Text
			While CDbl(Strings.Len(text)) < Conversion.Val("0" + Me.txtRollNoLen.Text)
				text = "0" + text
			End While
			Me.txtFilmNrAufFilm.Text = Me.txtRollNoPrefix.Text + text + Me.txtRollNoPostfix.Text
		End Sub

		' Token: 0x06000830 RID: 2096 RVA: 0x0003F058 File Offset: 0x0003D258
		Private Sub txtRollNoPrefix_TextChanged(eventSender As Object, eventArgs As EventArgs)
			Dim text As String = Me.txtFilmNr.Text
			While CDbl(Strings.Len(text)) < Conversion.Val("0" + Me.txtRollNoLen.Text)
				text = "0" + text
			End While
			Me.txtFilmNrAufFilm.Text = Me.txtRollNoPrefix.Text + text + Me.txtRollNoPostfix.Text
		End Sub

		' Token: 0x06000831 RID: 2097 RVA: 0x00036DCF File Offset: 0x00034FCF
		Private Sub txtSchritte_Leave(eventSender As Object, eventArgs As EventArgs)
			Me.CheckDistance()
		End Sub

		' Token: 0x06000832 RID: 2098 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub txtStart_TextChanged(eventSender As Object, eventArgs As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x06000833 RID: 2099 RVA: 0x0003F0C9 File Offset: 0x0003D2C9
		Private Sub DisableLayoutUpdate()
			modDeclares.UpdateIsDisabled = True
		End Sub

		' Token: 0x06000834 RID: 2100 RVA: 0x0003F0D1 File Offset: 0x0003D2D1
		Private Sub EnableLayoutUpdate()
			modDeclares.UpdateIsDisabled = False
		End Sub

		' Token: 0x06000835 RID: 2101 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub ReorderDocuments(ByRef start As Integer, ByRef Order As Boolean, ByRef OrderBy As Short)
		End Sub

		' Token: 0x06000836 RID: 2102 RVA: 0x0003F0DC File Offset: 0x0003D2DC
		Private Sub CheckDistance()
			If Me.chkStepsImageToImage.CheckState = CheckState.Checked Then
				If Conversion.Val(Me.txtSchritte.Text) < 1.0 Or Conversion.Val(Me.txtSchritte.Text) > 5.0 Then
					Dim text As String = "TXT_CHECK_DISTANCE1"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Der Frameabstand sollte im Bereich von 1-5 mm liegen! Bitte ueberpruefen sie die Eingabe!"
						left = "The Frame-Distance should be in the range from 1 to 5 mm!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					Return
				End If
			Else
				Dim num2 As Short = 0S
				While Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num2)), Me.cmbKopf.Text, False) <> 0
					num2 += 1S
					If num2 > 3S Then
						Exit While
					End If
				End While
				Dim num3 As Short
				If modDeclares.SystemData.portrait(CInt(num2)) Then
					num3 = CShort(Math.Round(modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) / 1.41))
				Else
					' The following expression was wrapped in a unchecked-expression
					num3 = CShort(Math.Round(modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) * 1.41))
				End If
				If Versioned.IsNumeric(Me.txtSchritte.Text) AndAlso Conversion.Val(Me.txtSchritte.Text) < CDbl((num3 + 1S)) Then
					Dim text As String = "TXT_CHECK_DISTANCE2"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Der Frameabstand sollte mindestens so gross wie die Monitorhoehe auf dem Film sein, um Ueberlappungen zu vermeiden!"
						left = "The Frame - Distance should be at least the monitor height on the film to avoid overlapping images!"
					End If
					Dim num As Short = 0S
					text = "Monitor Height = " + Conversions.ToString(CInt(num3)) + " mm"
					modMain.msgbox2(left, num, text)
				End If
			End If
		End Sub

		' Token: 0x06000837 RID: 2103 RVA: 0x0003F25C File Offset: 0x0003D45C
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub StartFilming()
			modDeclares.UseProzessor = True
			MyProject.Forms.frmBlipWinTest.Close()
			MyProject.Forms.frmImageTest.Close()
			MyProject.Forms.frmInfoWinTest.Close()
			Dim num As Short = 0S
			Dim num2 As Short
			Do
				If Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num)), modDeclares.glbKopf, False) = 0 Then
					num2 = num
				End If
				num += 1S
			Loop While num <= 3S
			modDeclares.SystemData.FrameWidth = Conversions.ToInteger("0" + Me.txtFrameWidth.Text)
			Dim num6 As Short
			If modDeclares.SystemData.SMCI AndAlso modDeclares.SystemData.Trinamic Then
				Dim vresolution As Short = modDeclares.SystemData.VResolution
				Dim num3 As Short = modDeclares.SystemData.FResolution(CInt(num2))
				Dim num4 As Short
				If vresolution = 1S Then
					num4 = 0S
				End If
				If vresolution = 2S Then
					num4 = 1S
				End If
				If vresolution = 4S Then
					num4 = 2S
				End If
				If vresolution = 8S Then
					num4 = 3S
				End If
				Dim num5 As Short
				If num3 = 1S Then
					num5 = 0S
				End If
				If num3 = 2S Then
					num5 = 1S
				End If
				If num3 = 4S Then
					num5 = 2S
				End If
				If num3 = 8S Then
					num5 = 3S
				End If
				If Not modDeclares.UseDebug Then
					num6 = 0S
					Dim flag As Boolean = -(modTrinamic.SetStepperResolutionTrinamic(num6, num4) > False)
					num6 = 1S
					Dim flag2 As Boolean = -(modTrinamic.SetStepperResolutionTrinamic(num6, num5) > False)
				End If
			End If
			modDeclares.SystemData.PortaitA3Drehen = False
			modDeclares.SystemData.LandscapeA4Drehen = False
			If Me.chkA3PortraitDrehen.CheckState = CheckState.Checked Then
				modDeclares.SystemData.PortaitA3Drehen = True
			End If
			If Me.chkA4LSDrehen.CheckState = CheckState.Checked Then
				modDeclares.SystemData.LandscapeA4Drehen = True
			End If
			modDeclares.SystemData.AddRollStartFrameSteps = 0
			If Versioned.IsNumeric(Me.txtAddRollStartFrameSteps.Text) Then
				' The following expression was wrapped in a checked-expression
				modDeclares.SystemData.AddRollStartFrameSteps = CInt(Math.Round(Conversion.Val(Me.txtAddRollStartFrameSteps.Text)))
			End If
			modDeclares.SystemData.A3A4Duplex = False
			If Me.chkDuplex.CheckState = CheckState.Checked Then
				modDeclares.SystemData.A3A4Duplex = True
			End If
			modDeclares.SystemData.optLage = (Me.optLagerichtig.CheckState = CheckState.Checked)
			modDeclares.SystemData.optLage = False
			modDeclares.SystemData.A3L = False
			modDeclares.SystemData.A3R = False
			modDeclares.SystemData.A4L = False
			modDeclares.SystemData.A4R = False
			modDeclares.SystemData.StartBlipAtOne = (Me.chkStartBlipAtOne.CheckState = CheckState.Checked)
			If Me.optRA3.Checked Then
				modDeclares.SystemData.A3R = True
			End If
			If Me.optRA4.Checked Then
				modDeclares.SystemData.A4R = True
			End If
			If Me.optLA3.Checked Then
				modDeclares.SystemData.A3L = True
			End If
			If Me.optLA4.Checked Then
				modDeclares.SystemData.A4L = True
			End If
			modDeclares.SystemData.kopfindex = num2
			modDeclares.SystemData.PDFReso = Conversions.ToInteger(Me.cmbPDFReso.Text)
			modDeclares.SystemData.JPEGProcessor = (Me.chkJPEG.CheckState = CheckState.Checked)
			modDeclares.SystemData.FesteBelegzahlProFilm = Conversions.ToBoolean(Interaction.IIf(Me.chkFesteBelegzahl.CheckState = CheckState.Checked, True, False))
			num = 1S
			Do
				num += 1S
			Loop While num <= 4S
			modDeclares.SystemData.UseAddRollFrame = Conversions.ToBoolean(Interaction.IIf(Me.chkAddRollFrame.CheckState = CheckState.Checked, True, False))
			Dim lpFileName As String
			modDeclares.SystemData.AddRollFrameInputLen = CInt(Math.Round(Conversion.Val("0" + Me.txtAddRollFrameLen.Text)))
			modDeclares.SystemData.AddRollFrameFontSize = CInt(Math.Round(Conversion.Val("0" + Me.txtAddRollFrameSize.Text)))
			modDeclares.SystemData.ShowLastData = Conversions.ToBoolean(Interaction.IIf(Me.chkAddRollFrameInput.CheckState = CheckState.Checked, True, False))
			lpFileName = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "FILMNO" + Conversions.ToString(CInt(num2)), Me.txtFilmNr.Text, lpFileName) > False)
			Dim flag4 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "LASTTEMPLATE", Me.cmbTemplate.Text, lpFileName) > False)
			Dim flag5 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "TEMPLATE", Me.cmbTemplate.Text, lpFileName) > False)
			Dim text As String = "TXT_MISSING_SEP_FILE"
			Dim text2 As String = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Es fehlt das Trennblatt-Image (Trennblatt.bmp)!"
			End If
			If Me.chkSeparateFrame.CheckState = CheckState.Checked AndAlso Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\trennblatt.bmp", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
				num6 = 16S
				text = "file-converter"
				modMain.msgbox2(text2, num6, text)
				Return
			End If
			modDeclares.DoCancel = False
			Me.cmdCancel.Enabled = False
			Application.DoEvents()
			text = "0" + Me.txtAddStepLevel2.Text
			modDeclares.SystemData.AddStepLevel2 = Conversion.Val(modMain.KommazuPunkt(text))
			text = "0" + Me.txtAddStepLevel3.Text
			modDeclares.SystemData.AddStepLevel3 = Conversion.Val(modMain.KommazuPunkt(text))
			modDeclares.SystemData.RollenNrPostfix = Me.txtRollNoPostfix.Text
			modDeclares.SystemData.RollenNrPrefix = Me.txtRollNoPrefix.Text
			modDeclares.SystemData.RollenNrFont = CInt(Math.Round(Conversion.Val("0" + Me.txtRollNoSize.Text)))
			modDeclares.SystemData.RollNoLen = CInt(Math.Round(Conversion.Val("0" + Me.txtRollNoLen.Text)))
			If modDeclares.SystemData.RollNoLen = 0 Then
				modDeclares.SystemData.RollNoLen = 3
			End If
			modDeclares.SystemData.UseSeparateFrame = (Me.chkSeparateFrame.CheckState = CheckState.Checked)
			modDeclares.SystemData.UseStartFrame = (Me.chkStartFrame.CheckState = CheckState.Checked)
			modDeclares.SystemData.UseBlip = (Me.chkBlip.CheckState = CheckState.Checked)
			modDeclares.SystemData.AutoAlign = (Me.chkAutoAlign.CheckState = CheckState.Checked)
			modDeclares.SystemData.AutoAlign180 = (Me.chkAutoAlign180.CheckState = CheckState.Checked)
			modDeclares.SystemData.DoLeftAuto = Me.opt90.Checked
			modDeclares.SystemData.AnnoLen = CShort(Math.Round(Conversion.Val(Me.txtLen.Text)))
			modDeclares.SystemData.AnnoOverBlip = Me.optUeberBlip.Checked
			If Versioned.IsNumeric(Me.txtStart.Text) Then
				modDeclares.SystemData.AnnoStart = Conversions.ToInteger(Me.txtStart.Text)
			Else
				modDeclares.SystemData.AnnoStart = 1
			End If
			modDeclares.SystemData.UseAnno = (Me.chkAnnotation.CheckState = CheckState.Checked)
			modDeclares.SystemData.IgnoreChars = (Me.chkIgnoreChars.CheckState = CheckState.Checked)
			modDeclares.SystemData.IgnoreCharChount = CInt(Math.Round(Conversion.Val("0" + Me.txtIgnoreCharsCount.Text)))
			If Me.optMulti.Checked Then
				modDeclares.SystemData.AnnoStyle = 2S
			End If
			If Me.optNamen.Checked Then
				modDeclares.SystemData.AnnoStyle = 3S
			End If
			If Me.optNummer.Checked Then
				modDeclares.SystemData.AnnoStyle = 4S
			End If
			If Me.optDreiTeilig.Checked Then
				modDeclares.SystemData.AnnoStyle = 5S
			End If
			If Me.optBlipAnno.Checked Then
				modDeclares.SystemData.AnnoStyle = 6S
				modDeclares.SystemData.AnnoBlipLen = CShort(Math.Round(Conversion.Val("0" + Me.txtAnnoBlipLen.Text)))
			End If
			modDeclares.SystemData.Blip1Size = CShort(Me.cmbBlipLevel1.SelectedIndex)
			modDeclares.SystemData.Blip2Size = CShort(Me.cmbBlipLevel2.SelectedIndex)
			modDeclares.SystemData.Blip3Size = CShort(Me.cmbBlipLevel3.SelectedIndex)
			If Me.optFest0.Checked Then
				modDeclares.SystemData.FixRot = 1S
			End If
			If Me.optFest90.Checked Then
				modDeclares.SystemData.FixRot = 2S
			End If
			If Me.optFest180.Checked Then
				modDeclares.SystemData.FixRot = 3S
			End If
			If Me.optFest270.Checked Then
				modDeclares.SystemData.FixRot = 4S
			End If
			modDeclares.SystemData.Breite = CInt(Math.Round(Conversion.Val(Me.txtQuerBreite.Text)))
			modDeclares.SystemData.Hoehe = CInt(Math.Round(Conversion.Val(Me.txtQuerHoehe.Text)))
			modDeclares.SystemData.X = CInt(Math.Round(Conversion.Val(Me.txtQuerX.Text)))
			modDeclares.SystemData.y = CInt(Math.Round(Conversion.Val(Me.txtQuerY.Text)))
			modDeclares.SystemData.BlipBreite = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipBreite.Text)))
			modDeclares.SystemData.BlipHoehe = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipHoehe.Text)))
			modDeclares.SystemData.BlipX = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipX.Text)))
			modDeclares.SystemData.BlipY = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipY.Text)))
			modDeclares.SystemData.InfoX = CInt(Math.Round(Conversion.Val(Me.txtInfoX.Text)))
			modDeclares.SystemData.InfoY = CInt(Math.Round(Conversion.Val(Me.txtInfoY.Text)))
			modDeclares.SystemData.InfoBreite = CInt(Math.Round(Conversion.Val(Me.txtInfoBreite.Text)))
			modDeclares.SystemData.InfoHoehe = CInt(Math.Round(Conversion.Val(Me.txtInfoHoehe.Text)))
			modDeclares.SystemData.AnnoWinX = CInt(Math.Round(Conversion.Val(Me.txtAnnoX.Text)))
			modDeclares.SystemData.AnnoWinY = CInt(Math.Round(Conversion.Val(Me.txtAnnoY.Text)))
			modDeclares.SystemData.AnnoWinBreite = CInt(Math.Round(Conversion.Val(Me.txtAnnoBreite.Text)))
			modDeclares.SystemData.AnnoWinHoehe = CInt(Math.Round(Conversion.Val(Me.txtAnnoHoehe.Text)))
			modDeclares.SystemData.Ausrichtung = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerAusrichtung.Text)))
			modDeclares.SystemData.Font = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerFont.Text)))
			modDeclares.SystemData.Gewicht = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerGewicht.Text)))
			modDeclares.SystemData.AnnoX = Conversions.ToInteger(Me.txtQuerAnnoX.Text)
			modDeclares.SystemData.AnnoY = Conversions.ToInteger(Me.txtQuerAnnoY.Text)
			modDeclares.SystemData.InfoTextAusrichtung = CInt(Math.Round(Conversion.Val("0" + Me.txtInfoTextAusrichtung.Text)))
			modDeclares.SystemData.InfoTextFont = CInt(Math.Round(Conversion.Val("0" + Me.txtInfoTextFont.Text)))
			modDeclares.SystemData.InfoTextGewicht = CInt(Math.Round(Conversion.Val("0" + Me.txtInfoTextGewicht.Text)))
			modDeclares.SystemData.InfoTextX = CInt(Math.Round(Conversion.Val("0" + Me.txtInfoTextX.Text)))
			modDeclares.SystemData.InfoTextY = CInt(Math.Round(Conversion.Val("0" + Me.txtInfoTextY.Text)))
			modDeclares.SystemData.LateAnnoNumbering = (Me.chkLateStart.CheckState = CheckState.Checked)
			modDeclares.SystemData.UseFrameNo = Conversions.ToBoolean(Interaction.IIf(Me.chkUseFrameNo.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.UseEndFrame = Conversions.ToBoolean(Interaction.IIf(Me.chkRollEndFrame.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.Invers = False
			If Me.chkInvers.CheckState = CheckState.Checked Then
				modDeclares.SystemData.Invers = True
			End If
			modDeclares.SystemData.UseFrame = False
			If Me.chkFrame.CheckState = CheckState.Checked Then
				modDeclares.SystemData.UseFrame = True
			End If
			modDeclares.SystemData.WhiteFrame = Me.radWhiteFrame.Checked
			modDeclares.SystemData.DoSplit = False
			If Me.chkSplit.CheckState = CheckState.Checked Then
				modDeclares.SystemData.DoSplit = True
				modDeclares.SystemData.SplitCount = CShort(Math.Round(Conversion.Val(Me.cmbSplitCount.Text)))
				modDeclares.SystemData.SplitSizeX = CInt(Math.Round(Conversion.Val(Me.txtSplitBreite.Text)))
				modDeclares.SystemData.SplitSizeY = CInt(Math.Round(Conversion.Val(Me.txtSplitLaenge.Text)))
				modDeclares.SystemData.SplitOversize = Conversions.ToDouble("0" + Me.txtOverSize.Text)
			End If
			modDeclares.SystemData.optOben = Me.optOben.Checked
			modDeclares.SystemData.optUnten = Me.optUnten.Checked
			modDeclares.SystemData.optCenter = Me.optCenter.Checked
			modDeclares.SystemData.Duplex = Me.chkDuplex.Checked
			modDeclares.SystemData.SimDupFilenames = Me.chkSimDupFilenames.Checked
			modDeclares.SystemData.TwoLines = Me.chkTwoLines.Checked
			modDeclares.SystemData.OneToOneExposure = False
			If Me.chkOneToOne.CheckState = CheckState.Checked Then
				modDeclares.SystemData.OneToOneExposure = True
			End If
			text = "0" + Me.txtFactor.Text
			modDeclares.SystemData.Factor = Conversion.Val(modMain.KommazuPunkt(text))
			modDeclares.SystemData.Tolerance = Conversion.Val("0" + Me.txtToleranz.Text)
			text = Me.txtSchritte.Text
			modDeclares.SystemData.schrittweite = Conversion.Val(modMain.KommazuPunkt(text))
			modDeclares.SystemData.verschlussgeschw = Conversions.ToInteger(Me._txtVerschluss_0.Text)
			modDeclares.SystemData.zusatzbelichtung = Conversions.ToDouble("0" + Me.txtZusatzBelichtung.Text)
			modDeclares.SystemData.StepsImageToImage = Conversions.ToBoolean(Interaction.IIf(Me.chkStepsImageToImage.CheckState = CheckState.Checked, True, False))
			Dim txtBlipBreiteGross_ As TextBox = Me._txtBlipBreiteGross_0
			Dim textBox As TextBox = txtBlipBreiteGross_
			text = txtBlipBreiteGross_.Text
			Dim inputStr As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipBreiteGross = CInt(Math.Round(Conversion.Val(inputStr) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			Dim txtBlipBreiteMittel_ As TextBox = Me._txtBlipBreiteMittel_0
			textBox = txtBlipBreiteMittel_
			text = txtBlipBreiteMittel_.Text
			Dim inputStr2 As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipBreiteMittel = CInt(Math.Round(Conversion.Val(inputStr2) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			Dim txtBlipBreiteKlein_ As TextBox = Me._txtBlipBreiteKlein_0
			textBox = txtBlipBreiteKlein_
			text = txtBlipBreiteKlein_.Text
			Dim inputStr3 As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipBreiteKlein = CInt(Math.Round(Conversion.Val(inputStr3) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			Dim txtBlipHoeheGross_ As TextBox = Me._txtBlipHoeheGross_0
			textBox = txtBlipHoeheGross_
			text = txtBlipHoeheGross_.Text
			Dim inputStr4 As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipHoeheGross = CInt(Math.Round(Conversion.Val(inputStr4) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			Dim txtBlipHoeheMittel_ As TextBox = Me._txtBlipHoeheMittel_0
			textBox = txtBlipHoeheMittel_
			text = txtBlipHoeheMittel_.Text
			Dim inputStr5 As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipHoeheMittel = CInt(Math.Round(Conversion.Val(inputStr5) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			Dim txtBlipHoeheKlein_ As TextBox = Me._txtBlipHoeheKlein_0
			textBox = txtBlipHoeheKlein_
			text = txtBlipHoeheKlein_.Text
			Dim inputStr6 As String = modMain.KommazuPunkt(text)
			textBox.Text = text
			modDeclares.SystemData.BlipHoeheKlein = CInt(Math.Round(Conversion.Val(inputStr6) * CDbl(modDeclares.SystemData.Hoehe) / modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2))))
			modDeclares.SystemData.X = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerX.Text)))
			modDeclares.SystemData.y = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerY.Text)))
			modDeclares.SystemData.Breite = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBreite.Text)))
			modDeclares.SystemData.Hoehe = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerHoehe.Text)))
			If Versioned.IsNumeric(Me.txtQuerAnnoX.Text) Then
				modDeclares.SystemData.AnnoX = Conversions.ToInteger(Me.txtQuerAnnoX.Text)
			End If
			If Versioned.IsNumeric(Me.txtQuerAnnoY.Text) Then
				modDeclares.SystemData.AnnoY = Conversions.ToInteger(Me.txtQuerAnnoY.Text)
			End If
			modDeclares.SystemData.DocSizeFormat = CShort(Me.cmbPapierGroesse.SelectedIndex)
			modDeclares.SystemData.ShowDocSize = (Me.chkShowSize.CheckState = CheckState.Checked)
			modDeclares.SystemData.Ausrichtung = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerAusrichtung.Text)))
			modDeclares.SystemData.Font = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerFont.Text)))
			modDeclares.SystemData.Gewicht = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerGewicht.Text)))
			modDeclares.SystemData.BlipX = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBlipX.Text)))
			modDeclares.SystemData.BlipY = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBlipY.Text)))
			modDeclares.SystemData.BlipBreite = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBlipBreite.Text)))
			modDeclares.SystemData.BlipHoehe = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBlipHoehe.Text)))
			Dim belichtung As Integer = CInt(Math.Round(Conversion.Val("0" + Me.txtSchritteBelichtung.Text) * CDbl(modDeclares.SystemData.SchritteVolleUmdrehung) / CDbl(modDeclares.SystemData.schlitze) * (18.0 / modDeclares.SystemData.Verschlussmotorgradzahl)))
			modDeclares.SystemData.belichtung = belichtung
			modDeclares.SystemData.zusatzbelichtung = Conversion.Val("0" + Me.txtZusatzBelichtung.Text)
			modDeclares.SystemData.UseLogFile = False
			If Me.chkUseLogFile.CheckState = CheckState.Checked Then
				modDeclares.SystemData.UseLogFile = True
			End If
			modDeclares.SystemData.LogfileName = Me.lblLogFile.Text
			If modDeclares.SystemData.UseLogFile AndAlso Operators.CompareString(FileSystem.Dir(modDeclares.SystemData.LogfileName, Microsoft.VisualBasic.FileAttribute.Directory), "", False) = 0 Then
				modDeclares.SystemData.UseLogFile = False
				text = "Path to Logfiles " + modDeclares.SystemData.LogfileName + " doesn't exist. Logging will be deaktivated!"
				num6 = 0S
				Dim text3 As String = "file-converter"
				modMain.msgbox2(text, num6, text3)
			End If
			modDeclares.SystemData.Delimiter = Me.cmbDelimiter.Text
			num6 = modMain.HeaderCount - 1S
			num = 0S
			While num <= num6
				modDeclares.SystemData.Headers(CInt(num)) = Conversions.ToString(Me.lstHeader.Items(CInt(num)))
				modDeclares.SystemData.HeadersSel(CInt(num)) = Me.lstHeader.GetItemChecked(CInt(num))
				num += 1S
			End While
			Dim num7 As Short = modMain.TrailerCount - 1S
			num = 0S
			While num <= num7
				modDeclares.SystemData.Trailers(CInt(num)) = Conversions.ToString(Me.lstTrailer.Items(CInt(num)))
				modDeclares.SystemData.TrailerSel(CInt(num)) = Me.lstTrailer.GetItemChecked(CInt(num))
				num += 1S
			End While
			Dim num8 As Short = modMain.RecordCount - 1S
			num = 0S
			While num <= num8
				modDeclares.SystemData.Records(CInt(num)) = Conversions.ToString(Me.lstRecords.Items(CInt(num)))
				modDeclares.SystemData.RecordsSel(CInt(num)) = Me.lstRecords.GetItemChecked(CInt(num))
				num += 1S
			End While
			If Me.chkAutoTrailer.CheckState = CheckState.Checked Then
				modDeclares.SystemData.Autotrailer = True
				Dim text3 As String = Me.txtAutoTrailerDistance.Text
				modDeclares.SystemData.AutoTrailerDistance = Conversion.Val(modMain.KommazuPunkt(text3))
				text3 = Me.txtAutoTrailerLength.Text
				modDeclares.SystemData.AutoTrailerLength = Conversion.Val(modMain.KommazuPunkt(text3))
				modDeclares.SystemData.TrailerInfoFrames = False
				If Me.chkTrailerInfoFrames.CheckState = CheckState.Checked Then
					modDeclares.SystemData.TrailerInfoFrames = True
				End If
			Else
				modDeclares.SystemData.Autotrailer = False
			End If
			modDeclares.SystemData.UseStartSymbole = Conversions.ToBoolean(Interaction.IIf(Me.chkZusatzStartSymbole.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.UseEndSymbole = Conversions.ToBoolean(Interaction.IIf(Me.chkZusatzEndSymbole.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.PfadStartSymbole = Me.lblPfadStartSymbole.Text
			modDeclares.SystemData.PfadEndSymbole = Me.lblPfadEndSymbole.Text
			modDeclares.SystemData.PfadForsetzungsSymbole1 = Me.lblPfadFortsetzungsSymbole1.Text
			modDeclares.SystemData.PfadForsetzungsSymbole2 = Me.lblPfadFortsetzungsSymbole2.Text
			modDeclares.SystemData.FortsetzungsLevel = Me.cmbFortsetzungsLevel.SelectedIndex + 1
			If modDeclares.SystemData.FortsetzungsLevel = 0 Then
				modDeclares.SystemData.FortsetzungsLevel = 1
			End If
			modDeclares.SystemData.UseForsetzungsSymbole1 = Conversions.ToBoolean(Interaction.IIf(Me.chkRollewirdfortgesetzt.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.UseForsetzungsSymbole2 = Conversions.ToBoolean(Interaction.IIf(Me.chkRolleistFortsetzung.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.BaendeVollstaendigBelichten = Conversions.ToBoolean(Interaction.IIf(Me.chkBaende.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.DoRepeatFrames = Conversions.ToBoolean(Interaction.IIf(Me.chkFramesWiederholen.CheckState = CheckState.Checked, True, False))
			modDeclares.SystemData.NumberOfRepetetionFrames = CInt(Math.Round(Conversion.Val("0" + Me.txtFramesWiederholen.Text)))
			modDeclares.SystemData.NoSpecialSmybolesWhenContinuation = Conversions.ToBoolean(Interaction.IIf(Me.chkNoSpecialSmybolesWhenContinuation.CheckState = CheckState.Checked, True, False))
			lpFileName = MyProject.Application.Info.DirectoryPath + "\FCPrep.Ini"
			text2 = Conversions.ToString(modDeclares.SystemData.Breite)
			Dim flag6 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "Breite", text2, lpFileName) > False)
			text2 = Conversions.ToString(modDeclares.SystemData.Hoehe)
			Dim flag7 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "Hoehe", text2, lpFileName) > False)
			text2 = Conversions.ToString(Interaction.IIf(modDeclares.SystemData.AutoAlign, "1", "0"))
			Dim flag8 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "AutoAlign", text2, lpFileName) > False)
			text2 = Conversions.ToString(Interaction.IIf(modDeclares.SystemData.DoLeftAuto, "1", "0"))
			Dim flag9 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "DoLeftAuto", text2, lpFileName) > False)
			text2 = Conversions.ToString(CInt(modDeclares.SystemData.FixRot))
			Dim flag10 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "FixRot", text2, lpFileName) > False)
			text2 = Conversions.ToString(modDeclares.SystemData.PDFReso)
			Dim flag11 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "PDFReso", text2, lpFileName) > False)
			text2 = Conversions.ToString(Interaction.IIf(modDeclares.SystemData.DoSplit, "1", "0"))
			Dim flag12 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "DoSplit", text2, lpFileName) > False)
			text2 = Conversions.ToString(CInt(modDeclares.SystemData.SplitCount))
			Dim flag13 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SplitCount", text2, lpFileName) > False)
			text2 = Conversions.ToString(modDeclares.SystemData.SplitSizeX)
			Dim flag14 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SplitSizeX", text2, lpFileName) > False)
			text2 = Conversions.ToString(modDeclares.SystemData.SplitSizeY)
			Dim flag15 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SplitSizeY", text2, lpFileName) > False)
			text2 = Conversions.ToString(modDeclares.SystemData.SplitOversize)
			Dim flag16 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SplitOversize", text2, lpFileName) > False)
			text2 = Conversions.ToString(Interaction.IIf(modDeclares.SystemData.Invers, "1", "0"))
			Dim flag17 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "Invers", text2, lpFileName) > False)
			text2 = Conversions.ToString(Interaction.IIf(modDeclares.SystemData.UseFrame, "1", "0"))
			Dim flag18 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "UseFrame", text2, lpFileName) > False)
			If modDeclares.SystemData.UseAnno AndAlso (modDeclares.SystemData.AnnoWinBreite = 0 Or modDeclares.SystemData.AnnoWinHoehe = 0) Then
				modDeclares.SystemData.AnnoWinBreite = modDeclares.SystemData.BlipBreite
				modDeclares.SystemData.AnnoWinHoehe = modDeclares.SystemData.BlipHoehe
				modDeclares.SystemData.AnnoWinX = modDeclares.SystemData.BlipX
				modDeclares.SystemData.AnnoWinY = modDeclares.SystemData.BlipY
			End If
			MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - 11287.5)))
			MyProject.Forms.frmFilming.Show()
			If modDeclares.CalcModus Then
				Dim text3 As String = "TXT_CAPTION_CALC_FILM"
				text2 = modMain.GetText(text3)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "Berechnung der notwendigen Filmlänge"
				End If
				MyProject.Forms.frmFilming.Text = text2
				text3 = "TXT_FILM_NEEDED"
				text2 = modMain.GetText(text3)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "notw. Filmlänge"
				End If
				MyProject.Forms.frmFilming.Label4.Text = text2
				text3 = "TXT_END_CALC"
				text2 = modMain.GetText(text3)
				If Operators.CompareString(text2, "", False) = 0 Then
					text2 = "Berechnung beenden"
				End If
				MyProject.Forms.frmFilming.cmdEnd.Text = text2
			End If
			MyBase.Enabled = False
			modExpose.ExposeDocs()
			MyBase.Enabled = True
			Me.cmdCancel.Enabled = True
			MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - Support.PixelsToTwipsX(CDbl(MyBase.Width)) / 2.0)))
			If modDeclares.SystemData.SMCI And Not modDeclares.UseDebug Then
				modSMCi.LEDAnSMCi()
				modSMCi.VakuumAusSMCi()
			End If
			MyBase.Enabled = True
			MyBase.Activate()
		End Sub

		' Token: 0x06000838 RID: 2104 RVA: 0x00040E18 File Offset: 0x0003F018
		Private Function ErrorInCoreDetected() As Boolean
			Return modDeclares.ErrorInCore
		End Function

		' Token: 0x06000839 RID: 2105 RVA: 0x00040E2C File Offset: 0x0003F02C
		Private Function MakeDuplexImage(ByRef simhandle As Integer, ByRef duphandle As Integer) As Object
			Dim result As Object
			Return result
		End Function

		' Token: 0x0600083A RID: 2106 RVA: 0x00040E3A File Offset: 0x0003F03A
		Private Sub txtToleranz_TextChanged(eventSender As Object, eventArgs As EventArgs)
			If Versioned.IsNumeric(Me.txtToleranz.Text) AndAlso Conversion.Val(Me.txtToleranz.Text) <> 0.0 Then
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x0600083B RID: 2107 RVA: 0x00040E70 File Offset: 0x0003F070
		Private Sub txtToleranz_KeyPress(eventSender As Object, eventArgs As KeyPressEventArgs)
			' The following expression was wrapped in a checked-expression
			Dim num As Short = CShort(Strings.Asc(eventArgs.KeyChar))
			If num = 13S Then
				Me.UpdateLayout()
			End If
			eventArgs.KeyChar = Strings.Chr(CInt(num))
			If num = 0S Then
				eventArgs.Handled = True
			End If
		End Sub

		' Token: 0x0600083C RID: 2108 RVA: 0x00040EAC File Offset: 0x0003F0AC
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Public Sub UpdateLayout()
			Dim num2 As Integer
			Dim num38 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				Dim fileSystemObject As FileSystemObject = New FileSystemObjectClass()
				IL_09:
				num = 2
				If modDeclares.UpdateIsDisabled Then
					GoTo IL_1F37
				End If
				IL_15:
				ProjectData.ClearProjectError()
				num2 = 2
				IL_1C:
				num = 5
				modDeclares.SystemData.Breite = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerBreite.Text)))
				IL_48:
				num = 6
				modDeclares.SystemData.Hoehe = CInt(Math.Round(Conversion.Val("0" + Me.txtQuerHoehe.Text)))
				IL_74:
				num = 7
				If modDeclares.SystemData.Breite <> 0 Then
					GoTo IL_8F
				End If
				IL_82:
				num = 8
				modDeclares.SystemData.Breite = 1
				IL_8F:
				num = 9
				If modDeclares.SystemData.Hoehe <> 0 Then
					GoTo IL_AC
				End If
				IL_9E:
				num = 10
				modDeclares.SystemData.Hoehe = 1
				IL_AC:
				num = 11
				Dim i As Integer = 0
				Dim num3 As Short
				Do
					IL_B1:
					num = 12
					If Operators.CompareString(modDeclares.SystemData.kopfname(i), modDeclares.glbKopf, False) = 0 Then
						IL_CD:
						num = 13
						num3 = CShort(i)
					End If
					IL_D4:
					num = 14
					i += 1
				Loop While i <= 3
				IL_DF:
				num = 15
				Dim no_PREVIEW As Boolean = modDeclares.NO_PREVIEW
				IL_E8:
				num = 16
				Dim num4 As Integer = 5
				Dim num5 As Integer = modMain.min(num4, modDeclares.imagecount)
				i = 0
				While i <= num5
					IL_103:
					num = 17
					If MyProject.Forms.frmLoading.ProgressBar1.Visible Then
						IL_11C:
						num = 18
						MyProject.Forms.frmLoading.ProgressBar1.Minimum = 0
						IL_134:
						num = 19
						Dim progressBar As ProgressBar = MyProject.Forms.frmLoading.ProgressBar1
						num4 = 5
						progressBar.Maximum = modMain.min(num4, modDeclares.imagecount)
						IL_15A:
						num = 20
						MyProject.Forms.frmLoading.ProgressBar1.Value = i
					End If
					IL_172:
					num = 21
					Dim text As String
					Dim num6 As Integer
					Dim num7 As Integer
					Dim num8 As Double
					Dim num9 As Double
					If Not(modDeclares.NO_PREVIEW Or modDeclares.NoImageUpdate) Then
						IL_185:
						num = 22
						If modMain.IsUnicode(modDeclares.Images(i + modPaint.pos).Name) Then
							IL_1A8:
							num = 23
							text = MyProject.Application.Info.DirectoryPath + "\X.IMG"
							IL_1C6:
							num = 24
							If Operators.CompareString(Support.Format(Strings.Right(modDeclares.Images(i + modPaint.pos).Name, 3), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), "PDF", False) = 0 Then
								IL_1FE:
								num = 25
								text = MyProject.Application.Info.DirectoryPath + "\X.PDF"
							End If
							IL_21C:
							num = 26
							fileSystemObject.CopyFile(modDeclares.Images(i + modPaint.pos).Name, text, True)
						Else
							IL_241:
							num = 28
							text = modDeclares.Images(i + modPaint.pos).Name
						End If
						IL_25C:
						num = 29
						If Not modDeclares.Images(i + modPaint.pos).IsPDF Then
							IL_331:
							num = 41
							If modMain.GetNumberOfPagesInTIFF(text) = 1L And Operators.CompareString(Strings.Right(text, 3), "DUP", False) <> 0 Then
								IL_35B:
								num = 42
								Dim shellFile As ShellFile = ShellFile.FromFilePath(text)
								IL_367:
								num = 43
								Dim extraLargeBitmap As Bitmap = shellFile.Thumbnail.ExtraLargeBitmap
								IL_378:
								num = 44
								modMain.glImage = extraLargeBitmap
								IL_382:
								num = 45
								Using fileStream As FileStream = New FileStream(text, FileMode.Open, FileAccess.Read)
									Using image As Image = Image.FromStream(fileStream, False, False)
										Dim width As Single = image.PhysicalDimension.Width
										Dim height As Single = image.PhysicalDimension.Height
										Dim horizontalResolution As Single = image.HorizontalResolution
										Dim verticalResolution As Single = image.VerticalResolution
										MyProject.Forms.frmImageXpress.IWidth = CLng(Math.Round(CDbl(width)))
										MyProject.Forms.frmImageXpress.IHeight = CLng(Math.Round(CDbl(height)))
										MyProject.Forms.frmImageXpress.IResX = CLng(Math.Round(CDbl(horizontalResolution)))
										MyProject.Forms.frmImageXpress.IResY = CLng(Math.Round(CDbl(verticalResolution)))
										num6 = CInt(Math.Round(CDbl(width)))
										num7 = CInt(Math.Round(CDbl(height)))
										num8 = CDbl(horizontalResolution)
										num9 = CDbl(verticalResolution)
									End Using
									GoTo IL_559
								End Using
								GoTo IL_470
							End If
							GoTo IL_470
							IL_559:
							num = 56
							Dim iresX As Long = MyProject.Forms.frmImageXpress.IResX
							IL_56C:
							num = 57
							Dim num10 As Double = 0.5
							IL_57A:
							num = 58
							Dim num11 As Double = CDbl(num6) / CDbl(num7)
							IL_586:
							num = 59
							Dim flag As Boolean = False
							IL_58C:
							num = 60
							If num10 > 1.0 And num11 > 1.0 Then
								IL_5AC:
								num = 61
								flag = True
							End If
							IL_5B2:
							num = 62
							If num10 < 1.0 And num11 < 1.0 Then
								IL_5D2:
								num = 63
								flag = True
								GoTo IL_5D8
							End If
							GoTo IL_5D8
							IL_470:
							num = 47
							MyProject.Forms.frmImageXpress.OpenRasterDocument(text, modDeclares.Images(i + modPaint.pos).page)
							IL_49B:
							num = 48

								MyProject.Forms.frmImageXpress.IWidth = CLng(modMain.glImage.Width)
								IL_4B8:
								num = 49
								MyProject.Forms.frmImageXpress.IHeight = CLng(modMain.glImage.Height)
								IL_4D5:
								num = 50

							MyProject.Forms.frmImageXpress.IResX = CLng(Math.Round(CDbl(modMain.glImage.HorizontalResolution)))
							IL_4F8:
							num = 51
							MyProject.Forms.frmImageXpress.IResY = CLng(Math.Round(CDbl(modMain.glImage.VerticalResolution)))
							IL_51B:
							num = 52
							num6 = modMain.glImage.Width
							IL_52A:
							num = 53
							num7 = modMain.glImage.Height
							IL_539:
							num = 54
							num8 = CDbl(modMain.glImage.HorizontalResolution)
							IL_549:
							num = 55
							num9 = CDbl(modMain.glImage.VerticalResolution)
							GoTo IL_559
						End If
						IL_27A:
						num = 30
						If Not Information.IsNothing(modMain.glImage) Then
							IL_289:
							num = 31
							modMain.glImage.Dispose()
						End If
						IL_296:
						num = 32
						If Not Information.IsNothing(modMain.glImage) Then
							IL_2A5:
							num = 33
							modMain.glImage.Dispose()
						End If
						IL_2B2:
						num = 34
						Dim frmImageXpress As frmImageXpress = MyProject.Forms.frmImageXpress
						Dim images As modDeclares.typImage() = modDeclares.Images
						Dim num12 As Integer = i + modPaint.pos
						num4 = 72
						frmImageXpress.OpenPDFDocumentAlt(text, images(num12).page, num4, modMain.glImage)
						IL_2E8:
						num = 35
						Dim glImage As Bitmap = New Bitmap(modMain.glImage)
						IL_2F7:
						num = 36
						modMain.glImage.Dispose()
						IL_304:
						num = 37
						modMain.glImage = glImage
						IL_30E:
						num = 38
						num6 = modMain.glImage.Width
						IL_31D:
						num = 39
						num7 = modMain.glImage.Height
					End If
					IL_5D8:
					num = 64
					If Me.chkBlip.CheckState = CheckState.Checked Then
						IL_5E9:
						num = 65
						Me.SetShpBlipVisible(i, True)
						IL_5F4:
						num = 66
						Me.SetLabelVisible(i, True)
					Else
						IL_601:
						num = 68
						Me.SetShpBlipVisible(i, False)
						IL_60C:
						num = 69
						Me.SetLabelVisible(i, False)
					End If
					IL_617:
					num = 70
					If Me.chkAnnotation.CheckState = CheckState.Checked Then
						IL_628:
						num = 71
						Me.SetlblAnnoVisible(i, True)
					Else
						IL_635:
						num = 73
						Me.SetlblAnnoVisible(i, False)
					End If
					IL_640:
					num = 74
					If modDeclares.glbOrientation Then
						IL_64D:
						num = 75
						If Me.chkAnnotation.CheckState = CheckState.Checked Then
							IL_661:
							num = 76
							If Me.chkBlip.CheckState = CheckState.Unchecked Or Me.optUeberBlip.Checked Then
								IL_680:
								num = 77
								Me.SetLblAnnoLeft(i, Me.GetShpBLIP_Left(i))
							End If
							IL_691:
							num = 78
							If Me.chkBlip.CheckState = CheckState.Unchecked Then
								IL_6A1:
								num = 79
								Me.SetLblAnnoTop(i, 145)
							End If
							IL_6B0:
							num = 80
							If Me.chkBlip.CheckState = CheckState.Checked And Not Me.optUeberBlip.Checked Then
								IL_6D2:
								num = 81
								Me.SetLblAnnoLeft(i, CInt(Math.Round(Support.TwipsToPixelsX(CDbl((660 + i * 2220))))))
							End If
							IL_6F5:
							num = 82
							If Me.optUeberBlip.Checked And Me.chkBlip.CheckState = CheckState.Checked Then
								IL_714:
								num = 83
								Me.SetLblAnnoTop(i, 128)
								IL_723:
								num = 84
								Me.SetLblAnnoLeft(i, Me.GetShpBLIP_Left(i))
							End If
							IL_734:
							num = 85
							If Me.optNebenBlip.Checked And Me.chkBlip.CheckState = CheckState.Checked Then
								IL_753:
								num = 86
								Me.SetLblAnnoTop(i, 145)
							End If
						End If
						IL_762:
						num = 87
						Dim flag2 As Boolean = Me.chkBlip.CheckState = CheckState.Unchecked And Me.chkAnnotation.CheckState = CheckState.Unchecked
						IL_783:
						num = 88
						Dim num13 As Integer
						Dim num14 As Integer
						Dim num15 As Integer
						If Me.chkBlip.CheckState = CheckState.Checked Then
							IL_794:
							num = 89
							If Me.chkAnnotation.CheckState = CheckState.Checked Then
								IL_7A5:
								num = 90
								If Me.optUeberBlip.Checked Then
									IL_7B5:
									num = 91
									num13 = 57
									IL_7BC:
									num = 92
									num14 = 77
									IL_7C3:
									num = 93
									num15 = 44
								Else
									IL_7CC:
									num = 95
									num13 = 65
									IL_7D3:
									num = 96
									num14 = 93
									IL_7DA:
									num = 97
									num15 = 44
								End If
							Else
								IL_7E3:
								num = 99
								num13 = 65
								IL_7EA:
								num = 100
								num14 = 93
								IL_7F1:
								num = 101
								num15 = 44
							End If
						Else
							IL_7FA:
							num = 103
							If Me.chkAnnotation.CheckState = CheckState.Unchecked Then
								IL_80A:
								num = 104
								num13 = 77
								IL_811:
								num = 105
								num14 = 109
								IL_818:
								num = 106
								num15 = 44
							Else
								IL_821:
								num = 108
								num13 = 65
								IL_828:
								num = 109
								num14 = 93
								IL_82F:
								num = 110
								num15 = 44
							End If
						End If
						IL_836:
						num = 111
						Me.SetPictureDims(i, num13, num14, num15)
					Else
						IL_84B:
						num = 113
						If Me.chkAnnotation.CheckState = CheckState.Checked Then
							IL_85F:
							num = 114
							If Me.chkBlip.CheckState = CheckState.Unchecked Or Me.optUeberBlip.Checked Then
								IL_87E:
								num = 115
								Me.SetLblAnnoLeft(i, Me.GetShpBLIP_Left(i))
							End If
							IL_88F:
							num = 116
							If Me.chkBlip.CheckState = CheckState.Unchecked Then
								IL_89F:
								num = 117
								Me.SetLblAnnoTop(i, 145)
							End If
							IL_8AE:
							num = 118
							If Me.chkBlip.CheckState = CheckState.Checked And Not Me.optUeberBlip.Checked Then
								IL_8D0:
								num = 119
								Me.SetLblAnnoLeft(i, 44 + i * 148)
							End If
							IL_8E4:
							num = 120
							If Me.optUeberBlip.Checked And Me.chkBlip.CheckState = CheckState.Checked Then
								IL_903:
								num = 121
								Me.SetLblAnnoTop(i, 128)
								IL_912:
								num = 122
								Me.SetLblAnnoLeft(i, Me.GetShpBLIP_Left(i))
							End If
							IL_923:
							num = 123
							If Me.optNebenBlip.Checked And Me.chkBlip.CheckState = CheckState.Checked Then
								IL_942:
								num = 124
								Me.SetLblAnnoTop(i, 145)
							End If
						End If
						IL_951:
						num = 125
						Dim flag3 As Boolean = Me.chkBlip.CheckState = CheckState.Unchecked And Me.chkAnnotation.CheckState = CheckState.Unchecked
						IL_972:
						num = 126
						Dim num13 As Integer
						Dim num14 As Integer
						Dim num15 As Integer
						If Me.chkBlip.CheckState = CheckState.Checked Then
							IL_986:
							num = 127
							If Me.chkAnnotation.CheckState = CheckState.Checked Then
								IL_997:
								num = 128
								If Me.optUeberBlip.Checked Then
									IL_9AA:
									num = 129
									num13 = 113
									IL_9B4:
									num = 130
									num14 = 81
									IL_9BE:
									num = 131
									num15 = 44
								Else
									IL_9CD:
									num = 133
									num13 = 129
									IL_9DA:
									num = 134
									num14 = 89
									IL_9E4:
									num = 135
									num15 = 44
								End If
							Else
								IL_9F0:
								num = 137
								num13 = 129
								IL_9FD:
								num = 138
								num14 = 89
								IL_A07:
								num = 139
								num15 = 44
							End If
						Else
							IL_A13:
							num = 141
							If Me.chkAnnotation.CheckState = CheckState.Unchecked Then
								IL_A26:
								num = 142
								num13 = 141
								IL_A33:
								num = 143
								num14 = 105
								IL_A3D:
								num = 144
								num15 = 44
							Else
								IL_A49:
								num = 146
								num13 = 129
								IL_A56:
								num = 147
								num14 = 89
								IL_A60:
								num = 148
								num15 = 44
							End If
						End If
						IL_A6A:
						num = 149

							Me.SetPictureCoords(i, CLng(num13), CLng(num14), CLng(num15))

					End If
					IL_A80:
					num = 150
					Dim j As Integer
					If Me.chkAnnotation.CheckState = CheckState.Checked Then
						IL_A97:
						num = 151
						Dim text2 As String
						If Me.optBlipAnno.Checked Then
							IL_AAA:
							num = 152
							text2 = "BLIP-INDEX"
						Else
							IL_ABC:
							num = 154
							If Me.optNamen.Checked Then
								IL_AD2:
								num = 155
								text2 = modDeclares.Images(i + modPaint.pos).DokumentName
								IL_AF0:
								num = 156
								text2 = modDeclares.Images(i + modPaint.pos).Name
								IL_B0E:
								num = 157
								If Strings.InStrRev(text2, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) > 0 Then
									IL_B25:
									num = 158
									text2 = Strings.Left(text2, Strings.InStrRev(text2, ".", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
								End If
								IL_B44:
								num = 159
								If Strings.InStrRev(text2, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) > 0 Then
									IL_B5E:
									num = 160
									text2 = Strings.Right(text2, Strings.Len(text2) - Strings.InStrRev(text2, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary))
								End If
							Else
								IL_B88:
								num = 162
								text2 = ""
								IL_B95:
								num = 163
								Dim text3 As String = ""
								IL_BA2:
								num = 164
								num4 = CInt(Math.Round(Conversion.Val(Me.txtLen.Text)))
								j = 1
								While j <= num4
									IL_BC5:
									num = 165
									text3 += "0"
									IL_BD9:
									num = 166
									j += 1
								End While
								IL_BEB:
								num = 167
								text2 += Support.Format(CDbl((i + modPaint.pos)) + Conversion.Val(Me.txtStart.Text), text3, FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
							End If
						End If
						IL_C21:
						num = 168
						Me.SetLblAnnoText(i, text2)
						IL_C30:
						num = 169
						Me.SetLblAnnoTooltip(i, modDeclares.Images(i + modPaint.pos).Name)
					End If
					IL_C53:
					num = 170
					If Not(modDeclares.NO_PREVIEW Or modDeclares.NoImageUpdate) Then
						IL_C69:
						num = 171
						Dim num13 As Integer = Me.GetPictureWidth(i)
						IL_C78:
						num = 172
						Dim num14 As Integer = Me.GetPictureHeight(i)
						IL_C87:
						num = 173
						If Me.chkInvers.CheckState = CheckState.Checked Then
							IL_C9B:
							num = 174
							MyProject.Forms.frmImageXpress.Negate()
						End If
						IL_CB1:
						num = 175
						If Me.chkAutoAlign.CheckState = CheckState.Unchecked Then
							IL_CC7:
							num = 176
							If Not Me.optFest0.Checked Then
								IL_CDD:
								num = 177
								If Me.optFest90.Checked Then
									IL_CF0:
									num = 178
									j = 1
									IL_CF9:
									num = 179
									MyProject.Forms.frmImageXpress.Rotate(90L)
								End If
								IL_D12:
								num = 180
								If Me.optFest180.Checked Then
									IL_D25:
									num = 181
									j = 2
									IL_D2E:
									num = 182
									MyProject.Forms.frmImageXpress.Rotate(180L)
								End If
								IL_D4A:
								num = 183
								If Me.optFest270.Checked Then
									IL_D5D:
									num = 184
									j = 3
									IL_D66:
									num = 185
									MyProject.Forms.frmImageXpress.Rotate(270L)
								End If
							End If
						End If
						IL_D82:
						num = 186
						Dim num16 As Integer
						Dim num17 As Integer
						If modDeclares.Images(i + modPaint.pos).IsPDF Then
							IL_DA0:
							num = 187
							num16 = modMain.glImage.Width
							IL_DB2:
							num = 188
							num17 = modMain.glImage.Height
							IL_DC4:
							num = 189
							num8 = CDbl(modMain.glImage.HorizontalResolution)
							IL_DD7:
							num = 190
							num9 = CDbl(modMain.glImage.VerticalResolution)
						Else
							IL_DEC:
							num = 192
							num16 = modMain.glImage.Width
							IL_DFE:
							num = 193
							num17 = modMain.glImage.Height
						End If
						IL_E10:
						num = 194
						IL_E16:
						num = 195
						Dim bitmap As Bitmap = New Bitmap(modMain.glImage)
						IL_E28:
						num = 196
						If num8 = 0.0 Then
							IL_E3B:
							num = 197
							num8 = 300.0
						End If
						IL_E4C:
						num = 198
						If num9 = 0.0 Then
							IL_E5F:
							num = 199
							num9 = 300.0
						End If
						IL_E70:
						num = 200
						Dim num18 As Double
						Dim num19 As Double

							num18 = CDbl(num16) / num8 * 25.4
							IL_E88:
							num = 201
							num19 = CDbl(num17) / num9 * 25.4
							IL_EA0:
							num = 202

						If Me.chkOneToOne.CheckState = CheckState.Checked Then
							IL_EB7:
							num = 203
							If Operators.CompareString(Me.txtFactor.Text, "", False) = 0 Then
								IL_ED5:
								num = 204
								Me.txtFactor.Text = "24"
							End If
							IL_EEB:
							num = 205
							If num8 = 0.0 Then
								IL_EFE:
								num = 206
								num8 = 200.0
							End If
							IL_F0F:
							num = 207
							Dim num10 As Double = CDbl(num14) / CDbl(num13)
							IL_F1E:
							num = 208
							Dim num11 As Double = CDbl(num16) / CDbl(num17)
							IL_F2D:
							num = 209
							Dim flag As Boolean = False
							IL_F36:
							num = 210
							If num10 > 1.0 And num11 > 1.0 Then
								IL_F59:
								num = 211
								flag = True
							End If
							IL_F62:
							num = 212
							If num10 < 1.0 And num11 < 1.0 Then
								IL_F85:
								num = 213
								flag = True
							End If
							IL_F8E:
							num = 214
							Dim num20 As Short
							If modDeclares.SystemData.portrait(CInt(num3)) Then
								IL_FA3:
								num = 215
								num20 = 90S
								IL_FAD:
								num = 216
								If flag And modDeclares.SystemData.optLage Then
									IL_FC2:
									num = 217
									num20 = 0S
								End If
							Else
								IL_FCD:
								num = 219
								num20 = 0S
								IL_FD6:
								num = 220
								If Not flag And modDeclares.SystemData.optLage Then
									IL_FEE:
									num = 221
									num20 = 90S
								End If
							End If
							IL_FF8:
							num = 222
							If modDeclares.SystemData.FixRot = 3S Then
								IL_100B:
								num = 223
								num20 += 180S
							End If
							IL_101C:
							num = 224
							If modDeclares.SystemData.FixRot = 2S Then
								IL_102F:
								num = 225
								num20 += 90S
							End If
							IL_103D:
							num = 226
							If modDeclares.SystemData.FixRot = 4S Then
								IL_1050:
								num = 227
								num20 += 270S
							End If
							IL_1061:
							num = 228
							Dim flag4 As Boolean = num20 <> 0S And num20 <> 360S
							IL_107A:
							num = 229
							If num20 = 90S Or num20 = 270S Then
								IL_1092:
								num = 230
								Dim num15 As Integer = num16
								IL_109C:
								num = 231
								num16 = num17
								IL_10A6:
								num = 232
								num17 = num15
							End If
							IL_10B0:
							num = 233
							If Me.chkA4LSDrehen.CheckState = CheckState.Checked Then
								IL_10C7:
								num = 234
								If CDbl(num7) * 25.4 / num8 < 230.0 And CDbl(num7) / CDbl(num6) < 1.0 Then
									IL_10FD:
									num = 235
									If Me.optRA4.Checked Then
										IL_1110:
										num = 236
										bitmap.RotateFlip(RotateFlipType.Rotate90FlipNone)
									Else
										IL_1120:
										num = 238
										bitmap.RotateFlip(RotateFlipType.Rotate270FlipNone)
									End If
									IL_112E:
									num = 239
									Dim num15 As Integer = CInt(Math.Round(num19))
									IL_113E:
									num = 240
									num19 = num18
									IL_1148:
									num = 241
									num18 = CDbl(num15)
									IL_1153:
									num = 242
									num15 = num6
									IL_115D:
									num = 243
									num6 = num7
									IL_1167:
									num = 244
									num7 = num15
								End If
							End If
							IL_1171:
							num = 245
							If Me.chkA3PortraitDrehen.CheckState = CheckState.Checked Then
								IL_1188:
								num = 246
								If CDbl(num7) * 25.4 / num8 > 400.0 Then
									IL_11A9:
									num = 247
									If Me.optRA3.Checked Then
										IL_11BC:
										num = 248
										bitmap.RotateFlip(RotateFlipType.Rotate90FlipNone)
									Else
										IL_11CC:
										num = 250
										bitmap.RotateFlip(RotateFlipType.Rotate270FlipNone)
									End If
									IL_11DA:
									num = 251
									Dim num15 As Integer = CInt(Math.Round(num19))
									IL_11EA:
									num = 252
									num19 = num18
									IL_11F4:
									num = 253
									num18 = CDbl(num15)
									IL_11FF:
									num = 254
									num15 = num6
									IL_1209:
									num = 255
									num6 = num7
									IL_1213:
									num = 256
									num7 = num15
								End If
							End If
							IL_121D:
							num = 257
							Dim num23 As Double
							Dim num24 As Double

								Dim left As Object = CDbl(num6) * 400.0 / num8
								IL_123A:
								num = 258
								Dim num21 As Double = CDbl(num7) * 400.0 / num9
								IL_1252:
								num = 259
								Dim num22 As Double = CDbl(modDeclares.SystemData.Hoehe) / CDbl(num14)
								IL_1269:
								num = 260
								num23 = Conversions.ToDouble(Operators.DivideObject(Operators.MultiplyObject(left, modDeclares.SystemData.Factor), num22))
								IL_1298:
								num = 261
								num24 = num21 * modDeclares.SystemData.Factor / num22
								IL_12B0:
								num = 262
								Dim text4 As String = "scaled_pixel_on_screen_width=" + Conversions.ToString(num23)
								modDeclares.OutputDebugString(text4)
								IL_12D0:
								num = 263
								text4 = "scaled_pixel_on_screen_height=" + Conversions.ToString(num24)
								modDeclares.OutputDebugString(text4)
								IL_12F0:
								num = 264
								Dim num26 As Double
								Dim num25 As Double = num26
								IL_12FA:
								num = 265
								If num23 > CDbl(num13) Then
									IL_1307:
									num = 266
									Dim text3 As String = Conversions.ToString(num23 / CDbl(num13))
									IL_131A:
									num = 267
									num23 = CDbl(num13)
									IL_1325:
									num = 268
									num24 /= Conversions.ToDouble(text3)
								End If
								IL_1337:
								num = 269
								If num24 > CDbl(num14) Then
									IL_1344:
									num = 270
									Dim text3 As String = Conversions.ToString(num24 / CDbl(num14))
									IL_1357:
									num = 271
									num24 = CDbl(num14)
									IL_1362:
									num = 272
									num23 /= Conversions.ToDouble(text3)
								End If
								IL_1374:
								num = 273
								Dim num27 As Double = modDeclares.SystemData.MonitorHeightOnFilm(CInt(num3))
								text4 = Me.txtFactor.Text
								Dim num28 As Double = num27 * Conversion.Val(modMain.KommazuPunkt(text4))
								IL_13A3:
								num = 274
								Dim num29 As Double = modDeclares.SystemData.MonitorHeightOnFilm(CInt(num3)) * CDbl(modDeclares.SystemData.Breite) / CDbl(modDeclares.SystemData.Hoehe)
								text4 = Me.txtFactor.Text
								Dim num30 As Double = num29 * Conversion.Val(modMain.KommazuPunkt(text4))
								IL_13EA:
								num = 275
								Dim num31 As Double = num19 / num28 * CDbl(modDeclares.SystemData.Hoehe)
								IL_1403:
								num = 276
								num26 = num18 / num30 * CDbl(modDeclares.SystemData.Breite)
								IL_141C:
								num = 277
								num25 = num26
								IL_1426:
								num = 278
								If num31 > num25 Then
									IL_1432:
									num = 279
									num25 = num31
								End If
								IL_143C:
								num = 280

							Dim bitmap2 As Bitmap = frmFilmPreview.ResizeImage(bitmap, CInt(Math.Round(num23)), CInt(Math.Round(num24)))
							IL_145B:
							num = 281
							Me.DisposePictureImage(i)
							IL_1468:
							num = 282
							bitmap2.Save(MyProject.Application.Info.DirectoryPath + "\test" + i.ToString() + ".bmp")
							IL_149A:
							num = 283
							Me.SetPictureImage(i, MyProject.Application.Info.DirectoryPath + "\test" + i.ToString() + ".bmp")
							IL_14CC:
							num = 284
							Application.DoEvents()
						Else
							IL_14DC:
							num = 286
							Dim num32 As Double
							Dim num33 As Double
							If Me.chkAutoAlign.CheckState = CheckState.Checked Then
								IL_14F3:
								num = 287
								num32 = CDbl(num13) / CDbl(num14)
								IL_1502:
								num = 288
								num33 = num18 / num19
								IL_1511:
								num = 289
								If(num32 < 1.0 And num33 > 1.0) Or (num32 > 1.0 And num33 < 1.0) Then
									IL_1550:
									num = 290
									Dim a As Double
									If Me.opt90.Checked Then
										IL_1563:
										num = 291
										j = 1
										IL_156C:
										num = 292
										a = 270.0
									End If
									IL_157D:
									num = 293
									If Me.opt270.Checked Then
										IL_1590:
										num = 294
										j = 3
										IL_1599:
										num = 295
										a = 90.0
									End If
									IL_15AA:
									num = 296
									MyProject.Forms.frmImageXpress.Rotate(CLng(Math.Round(a)))
								Else
									IL_15CA:
									num = 298
									If Me.chkAutoAlign180.CheckState = CheckState.Checked Then
										IL_15DE:
										num = 299
										modMain.glImage.RotateFlip(RotateFlipType.Rotate180FlipNone)
									End If
								End If
							End If
							IL_15EF:
							num = 300
							num32 = CDbl(num13) / CDbl(num14)
							IL_15FE:
							num = 301
							num18 = CDbl(MyProject.Forms.frmImageXpress.IWidth)
							IL_1616:
							num = 302
							num19 = CDbl(MyProject.Forms.frmImageXpress.IHeight)
							IL_162E:
							num = 303
							num33 = num18 / num19
							IL_163D:
							num = 304
							Dim num34 As Integer = num13
							IL_1647:
							num = 305
							Dim num35 As Integer = CInt(Math.Round(CDbl(num34) / num33))
							IL_165B:
							num = 306
							If num35 > num14 Then
								IL_1667:
								num = 307
								num35 = num14
								IL_1671:
								num = 308
								num34 = CInt(Math.Round(CDbl(num14) * num33))
							End If
							IL_1685:
							num = 309
							If j <= 4 Then
								If j <> 1 Then
									If j = 4 Then
										IL_16B1:
										num = 313
									End If
								Else
									IL_16A9:
									num = 311
								End If
							ElseIf j <> 8 Then
								If j = 24 Then
									IL_16C1:
									num = 317
								End If
							Else
								IL_16B9:
								num = 315
							End If
							IL_16C7:
							num = 319
							modMain.glImage = frmFilmPreview.ResizeImage(CType(modMain.glImage, Bitmap), num34, num35)
							IL_16E5:
							num = 320
							Me.SetPictureImage(i)
							IL_16F2:
							num = 321
							modMain.glImage.Dispose()
						End If
					End If
					IL_1702:
					num = 322
					Me.SetLblBlipText(i, Conversions.ToString(CInt(modDeclares.Images(i + modPaint.pos).Level)))
					IL_172A:
					num = 323
					If modDeclares.gllevel = 1 Then
						IL_173B:
						num = 324
						Dim level As Short = modDeclares.Images(i + modPaint.pos).Level
						If level <> 1S Then
							If level = 2S Then
								IL_1769:
								num = 326
								Select Case Me.cmbBlipLevel2.SelectedIndex
									Case 0
										IL_1794:
										num = 328
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_17BA:
										num = 330
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_17E0:
										num = 332
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
								End Select
							End If
						Else
							IL_1806:
							num = 335
							Select Case Me.cmbBlipLevel3.SelectedIndex
								Case 0
									IL_182E:
									num = 337
									Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
								Case 1
									IL_1851:
									num = 339
									Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
								Case 2
									IL_1874:
									num = 341
									Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
							End Select
						End If
					End If
					IL_1895:
					num = 344
					If modDeclares.gllevel = 2 Then
						IL_18A6:
						num = 345
						Select Case modDeclares.Images(i + modPaint.pos).Level
							Case 1S
								IL_1A18:
								num = 365
								Select Case Me.cmbBlipLevel3.SelectedIndex
									Case 0
										IL_1A40:
										num = 367
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_1A63:
										num = 369
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1A86:
										num = 371
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
							Case 2S
								IL_197B:
								num = 356
								Select Case Me.cmbBlipLevel2.SelectedIndex
									Case 0
										IL_19A6:
										num = 358
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_19CC:
										num = 360
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_19F2:
										num = 362
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
							Case 3S
								IL_18DE:
								num = 347
								Select Case Me.cmbBlipLevel1.SelectedIndex
									Case 0
										IL_1909:
										num = 349
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_192F:
										num = 351
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1955:
										num = 353
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
						End Select
					End If
					IL_1AA7:
					num = 374
					If modDeclares.gllevel = 3 Then
						IL_1AB8:
						num = 375
						Select Case modDeclares.Images(i + modPaint.pos).Level
							Case 1S
								IL_1CCB:
								num = 404
								Select Case Me.cmbBlipLevel3.SelectedIndex
									Case 0
										IL_1CF3:
										num = 406
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_1D16:
										num = 408
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1D39:
										num = 410
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
							Case 2S
								IL_1C2E:
								num = 395
								Select Case Me.cmbBlipLevel2.SelectedIndex
									Case 0
										IL_1C59:
										num = 397
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_1C7F:
										num = 399
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1CA5:
										num = 401
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
							Case 3S
								IL_1B91:
								num = 386
								Select Case Me.cmbBlipLevel1.SelectedIndex
									Case 0
										IL_1BBC:
										num = 388
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_1BE2:
										num = 390
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1C08:
										num = 392
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
							Case 4S
								IL_1AF4:
								num = 377
								Select Case Me.cmbBlipLevel1.SelectedIndex
									Case 0
										IL_1B1F:
										num = 379
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(200.0))))
									Case 1
										IL_1B45:
										num = 381
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(300.0))))
									Case 2
										IL_1B6B:
										num = 383
										Me.SetShpBlipWidth(i, CInt(Math.Round(Support.TwipsToPixelsX(400.0))))
								End Select
						End Select
					End If
					IL_1D5A:
					num = 413
					If Me.chkAnnotation.CheckState = CheckState.Checked And Me.optNebenBlip.Checked And Me.chkBlip.CheckState = CheckState.Checked Then
						IL_1D8B:
						num = 414
						Me.SetLblAnnoLeft(i, CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Me.GetlblAnnot_Left(i))) + Support.PixelsToTwipsX(CDbl(Me.GetShpBLIP_Width(i))) - 200.0))))
					End If
					IL_1DC8:
					num = 415
					If modMain.IsUnicode(modDeclares.Images(i + modPaint.pos).Name) Then
						IL_1DEB:
						num = 416
						FileSystem.Kill(text)
					End If
					IL_1DF8:
					num = 417
					i += 1
				End While
				IL_1E0A:
				num = 418
				Dim lastIndex As Short = modPaint.LastIndex
				IL_1E18:
				num = 419
				Dim pos As Integer = modPaint.pos
				Dim pos2 As Integer = modPaint.pos
				Dim num36 As Integer = 5
				Dim num37 As Integer = pos2 + modMain.min(num36, modDeclares.imagecount)
				i = pos
				While i <= num37
					IL_1E40:
					num = 420
					If Operators.CompareString(modDeclares.Images(i).Name, Me.txtLastDocument.Text, False) < 0 Or (Operators.CompareString(modDeclares.Images(i).Name, Me.txtLastDocument.Text, False) = 0 And CDbl(modDeclares.Images(i).page) <= Conversion.Val(Me.txtPage.Text)) Then
						IL_1EB8:
						num = 421
						Me.SetShpFilmedBackColor(i - modPaint.pos, ColorTranslator.FromOle(Information.RGB(255, 255, 255)))
					Else
						IL_1EE6:
						num = 423
						Me.SetShpFilmedBackColor(i - modPaint.pos, ColorTranslator.FromOle(Information.RGB(0, 255, 0)))
					End If
					IL_1F0A:
					num = 424
					i += 1
				End While
				IL_1F37:
				GoTo IL_2639
				IL_1F1E:
				num = 426
				ProjectData.ClearProjectError()
				If num38 <> 0 Then
					GoTo IL_1F3C
				End If
				Throw ProjectData.CreateProjectError(-2146828268)
				IL_1F3C:
				Dim num39 As Integer = num38 + 1
				num38 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num39)
				IL_25F6:
				GoTo IL_262E
				IL_25F8:
				num38 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_260C:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num38 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_25F8
			End Try
			IL_262E:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_2639:
			If num38 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x0600083D RID: 2109 RVA: 0x00043548 File Offset: 0x00041748
		Private Sub SetShpBlipVisible(i As Integer, val As Boolean)
			Select Case i
				Case 0
					Me._ShpBLIP_0.Visible = val
					Return
				Case 1
					Me._ShpBLIP_1.Visible = val
					Return
				Case 2
					Me._ShpBLIP_2.Visible = val
					Return
				Case 3
					Me._ShpBLIP_3.Visible = val
					Return
				Case 4
					Me._ShpBLIP_4.Visible = val
					Return
				Case 5
					Me._ShpBLIP_5.Visible = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600083E RID: 2110 RVA: 0x000435C4 File Offset: 0x000417C4
		Private Sub SetLabelVisible(i As Integer, val As Boolean)
			Select Case i
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600083F RID: 2111 RVA: 0x000435F4 File Offset: 0x000417F4
		Private Sub SetlblAnnoVisible(i As Integer, val As Boolean)
			Select Case i
				Case 0
					Me._lblAnno_0.Visible = val
					Return
				Case 1
					Me._lblAnno_1.Visible = val
					Return
				Case 2
					Me._lblAnno_2.Visible = val
					Return
				Case 3
					Me._lblAnno_3.Visible = val
					Return
				Case 4
					Me._lblAnno_4.Visible = val
					Return
				Case 5
					Me._lblAnno_5.Visible = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000840 RID: 2112 RVA: 0x00043670 File Offset: 0x00041870
		Private Sub SetPictureCoords(i As Integer, w As Long, h As Long, t As Long)
			' The following expression was wrapped in a checked-statement
			Select Case i
				Case 0
					Me._Picture1_0.Top = CInt(t)
					Me._Picture1_0.Width = CInt(w)
					Me._Picture1_0.Height = CInt(h)
					Return
				Case 1
					Me._Picture1_1.Top = CInt(t)
					Me._Picture1_1.Width = CInt(w)
					Me._Picture1_1.Height = CInt(h)
					Return
				Case 2
					Me._Picture1_2.Top = CInt(t)
					Me._Picture1_2.Width = CInt(w)
					Me._Picture1_2.Height = CInt(h)
					Return
				Case 3
					Me._Picture1_3.Top = CInt(t)
					Me._Picture1_3.Width = CInt(w)
					Me._Picture1_3.Height = CInt(h)
					Return
				Case 4
					Me._Picture1_4.Top = CInt(t)
					Me._Picture1_4.Width = CInt(w)
					Me._Picture1_4.Height = CInt(h)
					Return
				Case 5
					Me._Picture1_5.Top = CInt(t)
					Me._Picture1_5.Width = CInt(w)
					Me._Picture1_5.Height = CInt(h)
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000841 RID: 2113 RVA: 0x00043794 File Offset: 0x00041994
		Private Sub SetLblBlipText(i As Integer, val As String)
			Select Case i
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000842 RID: 2114 RVA: 0x000437C4 File Offset: 0x000419C4
		Public Sub SetShpFilmedBackColor(i As Integer, val As Color)
			Select Case i
				Case 0
					Me._ShpFilmed_0.BackColor = val
					Return
				Case 1
					Me._ShpFilmed_1.BackColor = val
					Return
				Case 2
					Me._ShpFilmed_2.BackColor = val
					Return
				Case 3
					Me._ShpFilmed_3.BackColor = val
					Return
				Case 4
					Me._ShpFilmed_4.BackColor = val
					Return
				Case 5
					Me._ShpFilmed_5.BackColor = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000843 RID: 2115 RVA: 0x00043840 File Offset: 0x00041A40
		Private Sub SetLblAnnoFontSize(i As Integer, val As Long)
			Select Case i
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000844 RID: 2116 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdStart__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000845 RID: 2117 RVA: 0x0004386D File Offset: 0x00041A6D
		Private Sub cmdCancel__Enter(sender As Object, e As EventArgs)
			MyBase.Close()
			modDeclares.HeapCompact(modDeclares.GetProcessHeap(), 0)
			modMain.GetAvailableMem()
		End Sub

		' Token: 0x06000846 RID: 2118 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdNewTemplate__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000847 RID: 2119 RVA: 0x00043888 File Offset: 0x00041A88
		Private Sub cmdNewTemplate_Click(sender As Object, e As EventArgs)
			If Me.CheckData() Then
				MyProject.Forms.frmNewJob.ShowDialog()
				Dim text As String = modDeclares.frmNewJob_Name
				If Operators.CompareString(text, "", False) <> 0 Then
					Me.cmbKopf.Text = modDeclares.frmNewJob_kopf
					If Me.CheckData() Then
						If Operators.CompareString(Support.Format(Strings.Right(text, 4), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), ".TPL", False) <> 0 Then
							text += ".TPL"
						End If
						Dim text2 As String = text
						Me.savedata(text2)
						Me.cmbTemplate.Items.Add(text)
						Me.cmbTemplate.Text = text
					End If
				End If
			End If
		End Sub

		' Token: 0x06000848 RID: 2120 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdSaveTemplate__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000849 RID: 2121 RVA: 0x00043930 File Offset: 0x00041B30
		Private Sub cmdSaveTemplate_Click(sender As Object, e As EventArgs)
			If Operators.CompareString(Me.cmbTemplate.Text, "", False) <> 0 AndAlso Me.CheckData() Then
				Dim text As String = Me.cmbTemplate.Text
				Me.savedata(text)
			End If
		End Sub

		' Token: 0x0600084A RID: 2122 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdSetLastDoc__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600084B RID: 2123 RVA: 0x00043974 File Offset: 0x00041B74
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdSetLastDoc_Click(sender As Object, e As EventArgs)
			Strings.InStrRev(Me.txtLastDocument.Text, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary)
			Me.OpenFileDialog1.FileName = Me.txtLastDocument.Text
			Me.OpenFileDialog1.ShowDialog()
			modDeclares.mdlFktSelectedFile = Me.OpenFileDialog1.FileName
			If Operators.CompareString(modDeclares.mdlFktSelectedFile, "", False) <> 0 Then
				Dim flag As Boolean = False
				Dim imagecount As Integer = modDeclares.imagecount
				For i As Integer = 0 To imagecount
					If Operators.CompareString(modDeclares.Images(i).Name, modDeclares.mdlFktSelectedFile, False) = 0 Then
						flag = True
						Exit For
					End If
				Next
				If Not flag Then
					Dim text As String = "TXT_DOC_NOT_FOUND"
					Dim left As String = modMain.GetText(text)
					If Operators.CompareString(left, "", False) = 0 Then
						left = "Dokument nicht gefunden!" & vbCr & "Auswahl kann nicht gesetzt werden!"
					End If
					Dim num As Short = 0S
					text = "file-converter"
					modMain.msgbox2(left, num, text)
					Return
				End If
				Me.txtLastDocument.Text = modDeclares.mdlFktSelectedFile
				Me.txtPage.Text = "1"
				Dim value As String = modDeclares.mdlFktSelectedFile + vbCrLf & "1"
				If Not modDeclares.CalcModus Then
					If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", Microsoft.VisualBasic.FileAttribute.Normal), "", False) <> 0 Then
						FileSystem.Kill(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt")
					End If
					Using streamWriter As StreamWriter = New StreamWriter(MyProject.Application.Info.DirectoryPath + "\LastDocument.txt", True, Encoding.Unicode)
						streamWriter.Write(value)
						streamWriter.Close()
					End Using
				End If
			End If
		End Sub

		' Token: 0x0600084C RID: 2124 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdFirst__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600084D RID: 2125 RVA: 0x00043B30 File Offset: 0x00041D30
		Private Sub cmdFirst_Click(sender As Object, e As EventArgs)
			modPaint.pos = 0
			Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
			Me.UpdateLayout()
		End Sub

		' Token: 0x0600084E RID: 2126 RVA: 0x00043B6C File Offset: 0x00041D6C
		Private Sub cmdLast_Click(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-statement
			modPaint.pos = modDeclares.imagecount - 5
			Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
			Me.UpdateLayout()
		End Sub

		' Token: 0x0600084F RID: 2127 RVA: 0x00043BB8 File Offset: 0x00041DB8
		Private Sub cmdPageNext_Click(sender As Object, e As EventArgs)
			Dim num As Short
			Dim num2 As Short
			num = CShort((modPaint.pos + 1))
			num2 = CShort((modDeclares.imagecount - 6))
			For num3 As Short = num To num2
				If modDeclares.Images(CInt(num3)).Level > 1S Then
					modPaint.pos = CInt(num3)
					Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
					Me.UpdateLayout()
					Return
				End If
			Next
		End Sub

		' Token: 0x06000850 RID: 2128 RVA: 0x00043C30 File Offset: 0x00041E30
		Private Sub cmdNext_Click(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-statement
			If modPaint.pos < modDeclares.imagecount - 5 Then
				modPaint.pos += 1
				Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000851 RID: 2129 RVA: 0x00043C8C File Offset: 0x00041E8C
		Private Sub cmdPrevious_Click(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-statement
			If modPaint.pos > 0 Then
				modPaint.pos -= 1
				Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
				Me.UpdateLayout()
			End If
		End Sub

		' Token: 0x06000852 RID: 2130 RVA: 0x00043CE0 File Offset: 0x00041EE0
		Private Sub cmdPagePrevious_Click(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-statement
			For i As Integer = modPaint.pos - 1 To 0 Step -1
				If modDeclares.Images(i).Level > 1S Then
					modPaint.pos = i
					Me.lblPos.Text = Conversions.ToString(modPaint.pos + 1) + "\" + Conversions.ToString(modDeclares.imagecount + 1)
					Me.UpdateLayout()
					Return
				End If
			Next
		End Sub

		' Token: 0x06000853 RID: 2131 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadStartSymbole_Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000854 RID: 2132 RVA: 0x00043D4C File Offset: 0x00041F4C
		Private Sub Button1_Click(sender As Object, e As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadStartSymbole.Text
				IL_19:
				ProjectData.ClearProjectError()
				num = 1
				IL_20:
				num2 = 4
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadStartSymbole.Text
				IL_32:
				num2 = 5
				Me.OpenFileDialog1.ValidateNames = False
				IL_40:
				num2 = 6
				Me.OpenFileDialog1.CheckFileExists = False
				IL_4E:
				num2 = 7
				Me.OpenFileDialog1.FileName = "Select the Source Folder"
				IL_60:
				num2 = 8
				Me.OpenFileDialog1.InitialDirectory = modDeclares.mdlFktSelectedDirectory
				IL_72:
				num2 = 9
				Me.OpenFileDialog1.ShowDialog()
				IL_81:
				num2 = 10
				Me.lblPfadStartSymbole.Text = Strings.Left(Me.OpenFileDialog1.FileName, Strings.InStrRev(Me.OpenFileDialog1.FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
				IL_B8:
				num2 = 11
				Application.DoEvents()
				IL_C0:
				GoTo IL_13F
				IL_C2:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_100:
				GoTo IL_134
				IL_102:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_112:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_102
			End Try
			IL_134:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_13F:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000855 RID: 2133 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadFortsetzungsSymbole1_Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000856 RID: 2134 RVA: 0x00043EBC File Offset: 0x000420BC
		Private Sub Button2_Click(sender As Object, e As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				ProjectData.ClearProjectError()
				num = 1
				IL_0E:
				Dim num2 As Integer = 3
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadFortsetzungsSymbole1.Text
				IL_20:
				ProjectData.ClearProjectError()
				num = 1
				IL_27:
				num2 = 5
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadStartSymbole.Text
				IL_39:
				num2 = 6
				Me.OpenFileDialog1.ValidateNames = False
				IL_47:
				num2 = 7
				Me.OpenFileDialog1.CheckFileExists = False
				IL_55:
				num2 = 8
				Me.OpenFileDialog1.FileName = "Select the Source Folder"
				IL_67:
				num2 = 9
				Me.OpenFileDialog1.InitialDirectory = modDeclares.mdlFktSelectedDirectory
				IL_7A:
				num2 = 10
				Me.OpenFileDialog1.ShowDialog()
				IL_89:
				num2 = 11
				Me.lblPfadFortsetzungsSymbole1.Text = Strings.Left(Me.OpenFileDialog1.FileName, Strings.InStrRev(Me.OpenFileDialog1.FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
				IL_C0:
				num2 = 12
				Application.DoEvents()
				IL_C8:
				GoTo IL_14E
				IL_CD:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_10F:
				GoTo IL_143
				IL_111:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_121:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_111
			End Try
			IL_143:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_14E:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000857 RID: 2135 RVA: 0x0004403C File Offset: 0x0004223C
		Private Sub cmdPfadFortsetzungsSymbole2_Enter(sender As Object, e As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadFortsetzungsSymbole2.Text
				IL_19:
				num2 = 3
				Me.lblPfadFortsetzungsSymbole2.Text = modDeclares.mdlFktSelectedDirectory
				IL_2B:
				GoTo IL_8A
				IL_2D:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_4B:
				GoTo IL_7F
				IL_4D:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_5D:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_4D
			End Try
			IL_7F:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_8A:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000858 RID: 2136 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdPfadEndSymbole_Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000859 RID: 2137 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdApply_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600085A RID: 2138 RVA: 0x000440EC File Offset: 0x000422EC
		Private Sub cmdTestPortrait_Click(sender As Object, e As EventArgs)
			Dim num As Short = 0S
			Do
				Operators.CompareString(modDeclares.SystemData.kopfname(CInt(num)), Me.cmbKopf.Text, False)
				num += 1S
			Loop While num <= 3S
			MyProject.Forms.frmImageTest.Close()
			modDeclares.SystemData.UseBlip = True
			modDeclares.SystemData.UseAnno = True
			modDeclares.SystemData.X = CInt(Math.Round(Conversion.Val(Me.txtQuerX.Text)))
			modDeclares.SystemData.y = CInt(Math.Round(Conversion.Val(Me.txtQuerY.Text)))
			modDeclares.SystemData.Breite = CInt(Math.Round(Conversion.Val(Me.txtQuerBreite.Text)))
			modDeclares.SystemData.Hoehe = CInt(Math.Round(Conversion.Val(Me.txtQuerHoehe.Text)))
			modDeclares.SystemData.BlipX = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipX.Text)))
			modDeclares.SystemData.BlipY = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipY.Text)))
			modDeclares.SystemData.BlipBreite = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipBreite.Text)))
			modDeclares.SystemData.BlipHoehe = CInt(Math.Round(Conversion.Val(Me.txtQuerBlipHoehe.Text)))
			modDeclares.SystemData.InfoX = CInt(Math.Round(Conversion.Val(Me.txtInfoX.Text)))
			modDeclares.SystemData.InfoY = CInt(Math.Round(Conversion.Val(Me.txtInfoY.Text)))
			modDeclares.SystemData.InfoBreite = CInt(Math.Round(Conversion.Val(Me.txtInfoBreite.Text)))
			modDeclares.SystemData.InfoHoehe = CInt(Math.Round(Conversion.Val(Me.txtInfoHoehe.Text)))
			modDeclares.SystemData.AnnoWinX = CInt(Math.Round(Conversion.Val(Me.txtAnnoX.Text)))
			modDeclares.SystemData.AnnoWinY = CInt(Math.Round(Conversion.Val(Me.txtAnnoY.Text)))
			modDeclares.SystemData.AnnoWinBreite = CInt(Math.Round(Conversion.Val(Me.txtAnnoBreite.Text)))
			modDeclares.SystemData.AnnoWinHoehe = CInt(Math.Round(Conversion.Val(Me.txtAnnoHoehe.Text)))
			modDeclares.SystemData.Gewicht = CInt(Math.Round(Conversion.Val(Me.txtQuerGewicht.Text)))
			modDeclares.SystemData.Ausrichtung = CInt(Math.Round(Conversion.Val(Me.txtQuerAusrichtung.Text)))
			modDeclares.SystemData.AnnoX = CInt(Math.Round(Conversion.Val(Me.txtQuerAnnoX.Text)))
			modDeclares.SystemData.AnnoY = CInt(Math.Round(Conversion.Val(Me.txtQuerAnnoY.Text)))
			modDeclares.SystemData.Font = Conversions.ToInteger(Me.txtQuerFont.Text)
			modDeclares.SystemData.Anno = "ANNOTATION-12345678-Sample"
			modDeclares.SystemData.InfoTextGewicht = CInt(Math.Round(Conversion.Val(Me.txtInfoTextGewicht.Text)))
			modDeclares.SystemData.InfoTextAusrichtung = CInt(Math.Round(Conversion.Val(Me.txtInfoTextAusrichtung.Text)))
			modDeclares.SystemData.InfoTextX = CInt(Math.Round(Conversion.Val(Me.txtInfoTextX.Text)))
			modDeclares.SystemData.InfoTextY = CInt(Math.Round(Conversion.Val(Me.txtInfoTextY.Text)))
			modDeclares.SystemData.InfoTextFont = CInt(Math.Round(Conversion.Val(Me.txtInfoTextFont.Text)))
			modDeclares.SystemData.InfoText = "12345678901234567890123456789012345678901234567890123456789012345678901234567890"
			modDeclares.SystemData.Hoehe = Conversions.ToInteger(Me.txtQuerHoehe.Text)
			MyProject.Forms.frmBlipWinTest.ShpBLIP.Width = CInt(Math.Round(Support.TwipsToPixelsX(CDbl((modDeclares.SystemData.BlipBreiteGross * 15)))))
			MyProject.Forms.frmBlipWinTest.ShpBLIP.Height = CInt(Math.Round(Support.TwipsToPixelsY(CDbl((modDeclares.SystemData.BlipHoeheGross * 15)))))
			MyProject.Forms.frmImageTest.Show()
		End Sub

		' Token: 0x0600085B RID: 2139 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdTrailerDown_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x0600085C RID: 2140 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdTrailerUp_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x0600085D RID: 2141 RVA: 0x00044524 File Offset: 0x00042724
		Private Sub cmdHeaderUp_Click(sender As Object, e As EventArgs)
			Dim lstHeader As CheckedListBox = Me.lstHeader
			If lstHeader.SelectedIndex > 0 Then
				Dim num As Short = CShort(lstHeader.SelectedIndex)
				Dim itemChecked As Boolean = lstHeader.GetItemChecked(CInt(num))
				lstHeader.SetItemChecked(CInt(num), lstHeader.GetItemChecked(CInt((num - 1S))))
				lstHeader.SetItemChecked(CInt((num - 1S)), itemChecked)
				Dim text As String = Support.GetItemString(Me.lstHeader, CInt(num))
				text = Conversions.ToString(Me.lstHeader.Items(CInt(num)))
				Me.lstHeader.Items(CInt(num)) = RuntimeHelpers.GetObjectValue(Me.lstHeader.Items(CInt((num - 1S))))
				Me.lstHeader.Items(CInt((num - 1S))) = text
				Support.SetItemString(Me.lstHeader, CInt(num), Support.GetItemString(Me.lstHeader, CInt((num - 1S))))
				Support.SetItemString(Me.lstHeader, CInt((num - 1S)), text)
				lstHeader.SelectedIndex = CInt((num - 1S))
			End If
		End Sub

		' Token: 0x0600085E RID: 2142 RVA: 0x00044604 File Offset: 0x00042804
		Private Sub cmdHeaderDown_Click(sender As Object, e As EventArgs)
			Dim lstHeader As CheckedListBox = Me.lstHeader
			If lstHeader.SelectedIndex + 1 < lstHeader.Items.Count Then
				Dim num As Short = CShort(lstHeader.SelectedIndex)
				Dim itemChecked As Boolean = lstHeader.GetItemChecked(CInt(num))
				lstHeader.SetItemChecked(CInt(num), lstHeader.GetItemChecked(CInt((num + 1S))))
				lstHeader.SetItemChecked(CInt((num + 1S)), itemChecked)
				Dim itemString As String = Support.GetItemString(Me.lstHeader, CInt(num))
				Support.SetItemString(Me.lstHeader, CInt(num), Support.GetItemString(Me.lstHeader, CInt((num + 1S))))
				Support.SetItemString(Me.lstHeader, CInt((num + 1S)), itemString)
				lstHeader.SelectedIndex = CInt((num + 1S))
			End If
		End Sub

		' Token: 0x0600085F RID: 2143 RVA: 0x00044698 File Offset: 0x00042898
		Private Sub cmdTrailerUp_Click(sender As Object, e As EventArgs)
			Dim lstTrailer As CheckedListBox = Me.lstTrailer
			If lstTrailer.SelectedIndex > 0 Then
				Dim num As Short = CShort(lstTrailer.SelectedIndex)
				Dim itemChecked As Boolean = lstTrailer.GetItemChecked(CInt(num))
				lstTrailer.SetItemChecked(CInt(num), lstTrailer.GetItemChecked(CInt((num - 1S))))
				lstTrailer.SetItemChecked(CInt((num - 1S)), itemChecked)
				Dim itemString As String = Support.GetItemString(Me.lstTrailer, CInt(num))
				Support.SetItemString(Me.lstTrailer, CInt(num), Support.GetItemString(Me.lstTrailer, CInt((num - 1S))))
				Support.SetItemString(Me.lstTrailer, CInt((num - 1S)), itemString)
				lstTrailer.SelectedIndex = CInt((num - 1S))
			End If
		End Sub

		' Token: 0x06000860 RID: 2144 RVA: 0x00044720 File Offset: 0x00042920
		Private Sub cmdTrailerDown_Click(sender As Object, e As EventArgs)
			Dim lstTrailer As CheckedListBox = Me.lstTrailer
			If lstTrailer.SelectedIndex + 1 < lstTrailer.Items.Count Then
				Dim num As Short = CShort(lstTrailer.SelectedIndex)
				Dim itemChecked As Boolean = lstTrailer.GetItemChecked(CInt(num))
				lstTrailer.SetItemChecked(CInt(num), lstTrailer.GetItemChecked(CInt((num + 1S))))
				lstTrailer.SetItemChecked(CInt((num + 1S)), itemChecked)
				Dim itemString As String = Support.GetItemString(Me.lstTrailer, CInt(num))
				Support.SetItemString(Me.lstTrailer, CInt(num), Support.GetItemString(Me.lstTrailer, CInt((num + 1S))))
				Support.SetItemString(Me.lstTrailer, CInt((num + 1S)), itemString)
				lstTrailer.SelectedIndex = CInt((num + 1S))
			End If
		End Sub

		' Token: 0x06000861 RID: 2145 RVA: 0x000447B4 File Offset: 0x000429B4
		Private Sub cmdDownRecords_Click(sender As Object, e As EventArgs)
			Dim lstRecords As CheckedListBox = Me.lstRecords
			If lstRecords.SelectedIndex + 1 < lstRecords.Items.Count Then
				Dim num As Short = CShort(lstRecords.SelectedIndex)
				Dim itemChecked As Boolean = lstRecords.GetItemChecked(CInt(num))
				lstRecords.SetItemChecked(CInt(num), lstRecords.GetItemChecked(CInt((num + 1S))))
				lstRecords.SetItemChecked(CInt((num + 1S)), itemChecked)
				Dim itemString As String = Support.GetItemString(Me.lstRecords, CInt(num))
				Support.SetItemString(Me.lstRecords, CInt(num), Support.GetItemString(Me.lstRecords, CInt((num + 1S))))
				Support.SetItemString(Me.lstRecords, CInt((num + 1S)), itemString)
				lstRecords.SelectedIndex = CInt((num + 1S))
			End If
		End Sub

		' Token: 0x06000862 RID: 2146 RVA: 0x00044848 File Offset: 0x00042A48
		Private Sub cmdUpRecords_Click(sender As Object, e As EventArgs)
			Dim lstRecords As CheckedListBox = Me.lstRecords
			If lstRecords.SelectedIndex > 0 Then
				Dim num As Short = CShort(lstRecords.SelectedIndex)
				Dim itemChecked As Boolean = lstRecords.GetItemChecked(CInt(num))
				lstRecords.SetItemChecked(CInt(num), lstRecords.GetItemChecked(CInt((num - 1S))))
				lstRecords.SetItemChecked(CInt((num - 1S)), itemChecked)
				Dim itemString As String = Support.GetItemString(Me.lstRecords, CInt(num))
				Support.SetItemString(Me.lstRecords, CInt(num), Support.GetItemString(Me.lstRecords, CInt((num - 1S))))
				Support.SetItemString(Me.lstRecords, CInt((num - 1S)), itemString)
				lstRecords.SelectedIndex = CInt((num - 1S))
			End If
		End Sub

		' Token: 0x06000863 RID: 2147 RVA: 0x000448D0 File Offset: 0x00042AD0
		Private Sub Button4_Click(sender As Object, e As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadEndSymbole.Text
				IL_19:
				ProjectData.ClearProjectError()
				num = 1
				IL_20:
				num2 = 4
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadStartSymbole.Text
				IL_32:
				num2 = 5
				Me.OpenFileDialog1.ValidateNames = False
				IL_40:
				num2 = 6
				Me.OpenFileDialog1.CheckFileExists = False
				IL_4E:
				num2 = 7
				Me.OpenFileDialog1.FileName = "Select the Source Folder"
				IL_60:
				num2 = 8
				Me.OpenFileDialog1.InitialDirectory = modDeclares.mdlFktSelectedDirectory
				IL_72:
				num2 = 9
				Me.OpenFileDialog1.ShowDialog()
				IL_81:
				num2 = 10
				Me.lblPfadEndSymbole.Text = Strings.Left(Me.OpenFileDialog1.FileName, Strings.InStrRev(Me.OpenFileDialog1.FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
				IL_B8:
				num2 = 11
				Application.DoEvents()
				IL_C0:
				GoTo IL_13F
				IL_C2:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_100:
				GoTo IL_134
				IL_102:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_112:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_102
			End Try
			IL_134:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_13F:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000864 RID: 2148 RVA: 0x00044A40 File Offset: 0x00042C40
		Private Sub cmdCancel_Click(sender As Object, e As EventArgs)
			modMain.DeleteTempFiles(modDeclares.SystemData.PDFKONVERTERTEMP)
			If Not Information.IsNothing(modMain.glImage) Then
				modMain.glImage.Dispose()
			End If
			Dim text As String = "taskkill /F /T /IM PDFRenderer.exe"
			modMonitorTest.ExecCmd(text)
			text = "taskkill /F /T /IM PDFRenderer2.exe"
			modMonitorTest.ExecCmd(text)
			modDeclares.Sleep(1000)
			modMain.DeleteTempFiles()
			MyBase.Close()
		End Sub

		' Token: 0x06000865 RID: 2149 RVA: 0x00044AA4 File Offset: 0x00042CA4
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub cmdStart_Click(sender As Object, e As EventArgs)
			Dim flag As Boolean = False
			modDeclares.DisablePDFRenderImageDelete = False
			modMain.DeleteTempFiles(modDeclares.SystemData.PDFKONVERTERTEMP)
			Dim text As String
			If Operators.CompareString(modMain.GiveIni(text, "SYSTEM", "NEWPROTOCOLHEADER"), "1", False) = 0 Then
				modDeclares.NEWPROTOCOLHEADER = True
			Else
				modDeclares.NEWPROTOCOLHEADER = True
			End If
			Dim text2 As String = "taskkill /F /T /IM PDFRenderer.exe"
			modMonitorTest.ExecCmd(text2)
			text2 = "taskkill /F /T /IM PDFRenderer2.exe"
			modMonitorTest.ExecCmd(text2)
			modDeclares.Sleep(1000)
			modMain.DeleteTempFiles()
			modMain.LastLoadedPDF = ""
			If Not modDeclares.UseDebug And modDeclares.SystemData.Trinamic Then
				While Not flag AndAlso Not modTrinamic.TrinamicSupplyVoltageOK()
					MyProject.Forms.frmNoVoltage.ShowDialog()
					If modDeclares.UseDebug Then
						Exit While
					End If
				End While
			End If
			If Not modMonitorTest.TestMonitor() Then
				text2 = "The exposure monitor seems to have a problem!" & vbCr & "Please turn it off, check the cables, turn it back on again And check the required resolution!" & vbCr & "Then restart this application And retry to expose."
				Dim num As Short = 0S
				Dim text3 As String = "file-converter"
				modMain.msgbox2(text2, num, text3)
				ProjectData.EndApp()
				Return
			End If
			modMain.GetAvailableMem()
			If Me.CheckData() Then
				Me.StartFilming()
			End If
		End Sub

		' Token: 0x06000866 RID: 2150 RVA: 0x00044BA4 File Offset: 0x00042DA4
		Private Sub DisposePictureImage(i As Integer)
			Select Case i
				Case 0
					If Not Information.IsNothing(Me._Picture1_0.Image) Then
						Me._Picture1_0.Image.Dispose()
						Return
					End If
				Case 1
					If Not Information.IsNothing(Me._Picture1_1.Image) Then
						Me._Picture1_1.Image.Dispose()
						Return
					End If
				Case 2
					If Not Information.IsNothing(Me._Picture1_2.Image) Then
						Me._Picture1_2.Image.Dispose()
						Return
					End If
				Case 3
					If Not Information.IsNothing(Me._Picture1_3.Image) Then
						Me._Picture1_3.Image.Dispose()
						Return
					End If
				Case 4
					If Not Information.IsNothing(Me._Picture1_4.Image) Then
						Me._Picture1_4.Image.Dispose()
						Return
					End If
				Case 5
					If Not Information.IsNothing(Me._Picture1_5.Image) Then
						Me._Picture1_5.Image.Dispose()
					End If
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000867 RID: 2151 RVA: 0x00044CAC File Offset: 0x00042EAC
		Private Sub SetPictureImage(i As Integer, f As String)
			Select Case i
				Case 0
					If Not Information.IsNothing(Me._Picture1_0.Image) Then
						Me._Picture1_0.Image.Dispose()
					End If
					Me._Picture1_0.Image = Image.FromFile(f)
					Return
				Case 1
					If Not Information.IsNothing(Me._Picture1_1.Image) Then
						Me._Picture1_1.Image.Dispose()
					End If
					Me._Picture1_1.Image = Image.FromFile(f)
					Return
				Case 2
					If Not Information.IsNothing(Me._Picture1_2.Image) Then
						Me._Picture1_2.Image.Dispose()
					End If
					Me._Picture1_2.Image = Image.FromFile(f)
					Return
				Case 3
					If Not Information.IsNothing(Me._Picture1_3.Image) Then
						Me._Picture1_3.Image.Dispose()
					End If
					Me._Picture1_3.Image = Image.FromFile(f)
					Return
				Case 4
					If Not Information.IsNothing(Me._Picture1_4.Image) Then
						Me._Picture1_4.Image.Dispose()
					End If
					Me._Picture1_4.Image = Image.FromFile(f)
					Return
				Case 5
					If Not Information.IsNothing(Me._Picture1_5.Image) Then
						Me._Picture1_5.Image.Dispose()
					End If
					Me._Picture1_5.Image = Image.FromFile(f)
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000868 RID: 2152 RVA: 0x00044E14 File Offset: 0x00043014
		Private Sub SetPictureImage(i As Integer)
			Dim image As Bitmap = New Bitmap(modMain.glImage)
			Select Case i
				Case 0
					If Not Information.IsNothing(Me._Picture1_0.Image) Then
						Me._Picture1_0.Image.Dispose()
					End If
					Me._Picture1_0.Image = image
					Me._Picture1_0.Refresh()
					Return
				Case 1
					If Not Information.IsNothing(Me._Picture1_1.Image) Then
						Me._Picture1_1.Image.Dispose()
					End If
					Me._Picture1_1.Image = image
					Me._Picture1_1.Refresh()
					Return
				Case 2
					If Not Information.IsNothing(Me._Picture1_2.Image) Then
						Me._Picture1_2.Image.Dispose()
					End If
					Me._Picture1_2.Image = image
					Me._Picture1_2.Refresh()
					Return
				Case 3
					If Not Information.IsNothing(Me._Picture1_3.Image) Then
						Me._Picture1_3.Image.Dispose()
					End If
					Me._Picture1_3.Image = image
					Me._Picture1_3.Refresh()
					Return
				Case 4
					If Not Information.IsNothing(Me._Picture1_4.Image) Then
						Me._Picture1_4.Image.Dispose()
					End If
					Me._Picture1_4.Image = image
					Me._Picture1_4.Refresh()
					Return
				Case 5
					If Not Information.IsNothing(Me._Picture1_5.Image) Then
						Me._Picture1_5.Image.Dispose()
					End If
					Me._Picture1_5.Image = image
					Me._Picture1_5.Refresh()
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000869 RID: 2153 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Frame9_Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600086A RID: 2154 RVA: 0x00044FA8 File Offset: 0x000431A8
		Private Sub SetLblAnnoLeft(i As Integer, val As Integer)
			Select Case i
				Case 0
					Me._lblAnno_0.Left = val
					Return
				Case 1
					Me._lblAnno_1.Left = val
					Return
				Case 2
					Me._lblAnno_2.Left = val
					Return
				Case 3
					Me._lblAnno_3.Left = val
					Return
				Case 4
					Me._lblAnno_4.Left = val
					Return
				Case 5
					Me._lblAnno_5.Left = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600086B RID: 2155 RVA: 0x00045024 File Offset: 0x00043224
		Private Sub SetLblAnnoTop(i As Integer, val As Integer)
			Select Case i
				Case 0
					Me._lblAnno_0.Top = val
					Return
				Case 1
					Me._lblAnno_1.Top = val
					Return
				Case 2
					Me._lblAnno_2.Top = val
					Return
				Case 3
					Me._lblAnno_3.Top = val
					Return
				Case 4
					Me._lblAnno_4.Top = val
					Return
				Case 5
					Me._lblAnno_5.Top = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600086C RID: 2156 RVA: 0x000450A0 File Offset: 0x000432A0
		Private Function GetShpBLIP_Left(i As Integer) As Integer
			Dim left As Integer
			Select Case i
				Case 0
					left = Me._ShpBLIP_0.Left
				Case 1
					left = Me._ShpBLIP_1.Left
				Case 2
					left = Me._ShpBLIP_2.Left
				Case 3
					left = Me._ShpBLIP_3.Left
				Case 4
					left = Me._ShpBLIP_4.Left
				Case 5
					left = Me._ShpBLIP_5.Left
			End Select
			Return left
		End Function

		' Token: 0x0600086D RID: 2157 RVA: 0x00045124 File Offset: 0x00043324
		Private Sub SetPictureDims(i As Integer, w As Integer, h As Integer, t As Integer)
			Select Case i
				Case 0
					Me._Picture1_0.Top = t
					Me._Picture1_0.Width = w
					Me._Picture1_0.Height = h
					Return
				Case 1
					Me._Picture1_1.Top = t
					Me._Picture1_1.Width = w
					Me._Picture1_1.Height = h
					Return
				Case 2
					Me._Picture1_2.Top = t
					Me._Picture1_2.Width = w
					Me._Picture1_2.Height = h
					Return
				Case 3
					Me._Picture1_3.Top = t
					Me._Picture1_3.Width = w
					Me._Picture1_3.Height = h
					Return
				Case 4
					Me._Picture1_4.Top = t
					Me._Picture1_4.Width = w
					Me._Picture1_4.Height = h
					Return
				Case 5
					Me._Picture1_5.Top = t
					Me._Picture1_5.Width = w
					Me._Picture1_5.Height = h
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600086E RID: 2158 RVA: 0x00045238 File Offset: 0x00043438
		Private Sub SetLblAnnoText(i As Integer, str_Renamed As String)
			Select Case i
				Case 0
					Me._lblAnno_0.Text = str_Renamed
					Return
				Case 1
					Me._lblAnno_1.Text = str_Renamed
					Return
				Case 2
					Me._lblAnno_2.Text = str_Renamed
					Return
				Case 3
					Me._lblAnno_3.Text = str_Renamed
					Return
				Case 4
					Me._lblAnno_4.Text = str_Renamed
					Return
				Case 5
					Me._lblAnno_5.Text = str_Renamed
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x0600086F RID: 2159 RVA: 0x000452B4 File Offset: 0x000434B4
		Private Sub SetLblAnnoTooltip(i As Integer, str_Renamed As String)
			Select Case i
				Case 0
					Me.ToolTip1.SetToolTip(Me._lblAnno_0, str_Renamed)
					Return
				Case 1
					Me.ToolTip1.SetToolTip(Me._lblAnno_1, str_Renamed)
					Return
				Case 2
					Me.ToolTip1.SetToolTip(Me._lblAnno_2, str_Renamed)
					Return
				Case 3
					Me.ToolTip1.SetToolTip(Me._lblAnno_3, str_Renamed)
					Return
				Case 4
					Me.ToolTip1.SetToolTip(Me._lblAnno_4, str_Renamed)
					Return
				Case 5
					Me.ToolTip1.SetToolTip(Me._lblAnno_5, str_Renamed)
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000870 RID: 2160 RVA: 0x00045354 File Offset: 0x00043554
		Private Function GetlblAnnot_Left(i As Integer) As Integer
			Dim left As Integer
			Select Case i
				Case 0
					left = Me._lblAnno_0.Left
				Case 1
					left = Me._lblAnno_1.Left
				Case 2
					left = Me._lblAnno_2.Left
				Case 3
					left = Me._lblAnno_3.Left
				Case 4
					left = Me._lblAnno_4.Left
				Case 5
					left = Me._lblAnno_5.Left
			End Select
			Return left
		End Function

		' Token: 0x06000871 RID: 2161 RVA: 0x000453D8 File Offset: 0x000435D8
		Private Function GetShpBLIP_Width(i As Integer) As Integer
			Dim width As Integer
			Select Case i
				Case 0
					width = Me._ShpBLIP_0.Width
				Case 1
					width = Me._ShpBLIP_1.Width
				Case 2
					width = Me._ShpBLIP_2.Width
				Case 3
					width = Me._ShpBLIP_3.Width
				Case 4
					width = Me._ShpBLIP_4.Width
				Case 5
					width = Me._ShpBLIP_5.Width
			End Select
			Return width
		End Function

		' Token: 0x06000872 RID: 2162 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Shape1_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000873 RID: 2163 RVA: 0x0004545C File Offset: 0x0004365C
		Private Function GetPictureWidth(i As Integer) As Integer
			Dim width As Integer
			Select Case i
				Case 0
					width = Me._Picture1_0.Width
				Case 1
					width = Me._Picture1_1.Width
				Case 2
					width = Me._Picture1_2.Width
				Case 3
					width = Me._Picture1_3.Width
				Case 4
					width = Me._Picture1_4.Width
				Case 5
					width = Me._Picture1_5.Width
			End Select
			Return width
		End Function

		' Token: 0x06000874 RID: 2164 RVA: 0x000454E0 File Offset: 0x000436E0
		Private Function GetPictureHeight(i As Integer) As Integer
			Dim height As Integer
			Select Case i
				Case 0
					height = Me._Picture1_0.Height
				Case 1
					height = Me._Picture1_1.Height
				Case 2
					height = Me._Picture1_2.Height
				Case 3
					height = Me._Picture1_3.Height
				Case 4
					height = Me._Picture1_4.Height
				Case 5
					height = Me._Picture1_5.Height
			End Select
			Return height
		End Function

		' Token: 0x06000875 RID: 2165 RVA: 0x00045564 File Offset: 0x00043764
		Private Sub SetShpBlipWidth(i As Integer, val As Integer)
			Select Case i
				Case 0
					Me._ShpBLIP_0.Width = val
					Return
				Case 1
					Me._ShpBLIP_1.Width = val
					Return
				Case 2
					Me._ShpBLIP_2.Width = val
					Return
				Case 3
					Me._ShpBLIP_3.Width = val
					Return
				Case 4
					Me._ShpBLIP_4.Width = val
					Return
				Case 5
					Me._ShpBLIP_5.Width = val
					Return
				Case Else
					Return
			End Select
		End Sub

		' Token: 0x06000876 RID: 2166 RVA: 0x000455E0 File Offset: 0x000437E0
		Public Shared Function ResizeImage(bmSource As Bitmap, TargetWidth As Integer, TargetHeight As Integer) As Bitmap
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
				Else
					obj5 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.MultiplyObject(Operators.DivideObject(1, obj), obj4) }, Nothing, Nothing, Nothing)))
					obj3 = Convert.ToInt32(RuntimeHelpers.GetObjectValue(NewLateBinding.LateGet(Nothing, GetType(Math), "Floor", New Object() { Operators.DivideObject(Operators.SubtractObject(bitmap.Height, obj5), 2) }, Nothing, Nothing, Nothing)))
				End If
			End If
			Using obj6 As Object = Graphics.FromImage(bitmap)
				Dim obj7 As Object = obj6
				NewLateBinding.LateSetComplex(obj7, Nothing, "CompositingQuality", New Object() { CompositingQuality.HighQuality }, Nothing, Nothing, False, True)
				NewLateBinding.LateSetComplex(obj7, Nothing, "InterpolationMode", New Object() { InterpolationMode.HighQualityBicubic }, Nothing, Nothing, False, True)
				NewLateBinding.LateSetComplex(obj7, Nothing, "PixelOffsetMode", New Object() { PixelOffsetMode.HighQuality }, Nothing, Nothing, False, True)
				NewLateBinding.LateSetComplex(obj7, Nothing, "SmoothingMode", New Object() { SmoothingMode.AntiAlias }, Nothing, Nothing, False, True)
				NewLateBinding.LateSetComplex(obj7, Nothing, "CompositingMode", New Object() { CompositingMode.SourceOver }, Nothing, Nothing, False, True)
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
			Return bitmap
		End Function

		' Token: 0x06000877 RID: 2167 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub chkBlip_CheckedChanged(sender As Object, e As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x06000878 RID: 2168 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub chkAnnotation_CheckedChanged(sender As Object, e As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x06000879 RID: 2169 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _chk1PAgePDFs_0_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600087A RID: 2170 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub chkNullen_CheckedChanged(sender As Object, e As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x0600087B RID: 2171 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub txtTrennzeichen_TextChanged(sender As Object, e As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x0600087C RID: 2172 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub optDatei_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600087D RID: 2173 RVA: 0x00045914 File Offset: 0x00043B14
		Private Sub chkShowSize_CheckedChanged(sender As Object, e As EventArgs)
			If Me.chkShowSize.CheckState = CheckState.Checked Then
				Me.cmbPapierGroesse.Enabled = True
				Return
			End If
			Me.cmbPapierGroesse.Enabled = False
		End Sub

		' Token: 0x0600087E RID: 2174 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkLateStart_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600087F RID: 2175 RVA: 0x0003EF59 File Offset: 0x0003D159
		Private Sub cmbPapierGroesse_SelectedIndexChanged(sender As Object, e As EventArgs)
			modDeclares.NoImageUpdate = True
			Me.UpdateLayout()
			modDeclares.NoImageUpdate = False
		End Sub

		' Token: 0x06000880 RID: 2176 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkInvers_CheckedChanged(sender As Object, e As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x06000881 RID: 2177 RVA: 0x00036BA9 File Offset: 0x00034DA9
		Private Sub chkFrame_CheckedChanged(sender As Object, e As EventArgs)
			Me.UpdateLayout()
		End Sub

		' Token: 0x06000882 RID: 2178 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_0_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000883 RID: 2179 RVA: 0x0004593D File Offset: 0x00043B3D
		Private Sub _Picture1_0_DoubleClick(sender As Object, e As EventArgs)
			Me.StartIV(modPaint.pos)
		End Sub

		' Token: 0x06000884 RID: 2180 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_2_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000885 RID: 2181 RVA: 0x0004594C File Offset: 0x00043B4C
		Private Sub Button3_Click(sender As Object, e As EventArgs)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				modDeclares.mdlFktSelectedDirectory = Me.lblPfadFortsetzungsSymbole2.Text
				IL_19:
				num2 = 3
				Me.OpenFileDialog1.ValidateNames = False
				IL_27:
				num2 = 4
				Me.OpenFileDialog1.CheckFileExists = False
				IL_35:
				num2 = 5
				Me.OpenFileDialog1.FileName = "Select the Source Folder"
				IL_47:
				num2 = 6
				Me.OpenFileDialog1.InitialDirectory = modDeclares.mdlFktSelectedDirectory
				IL_59:
				num2 = 7
				Me.OpenFileDialog1.ShowDialog()
				IL_67:
				num2 = 8
				Me.lblPfadFortsetzungsSymbole2.Text = Strings.Left(Me.OpenFileDialog1.FileName, Strings.InStrRev(Me.OpenFileDialog1.FileName, "\", -1, Microsoft.VisualBasic.CompareMethod.Binary) - 1)
				IL_9D:
				num2 = 9
				Application.DoEvents()
				IL_A5:
				GoTo IL_11C
				IL_A7:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_DD:
				GoTo IL_111
				IL_DF:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_EF:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_DF
			End Try
			IL_111:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_11C:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000886 RID: 2182 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub lstRecords_SelectedIndexChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000887 RID: 2183 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _tabSettings_TabPage3_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000888 RID: 2184 RVA: 0x00045A90 File Offset: 0x00043C90
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub StartIV(index As Integer)
			Dim num As Integer
			Dim num4 As Integer
			Dim obj As Object
			Try
				IL_00:
				ProjectData.ClearProjectError()
				num = 1
				IL_07:
				Dim num2 As Integer = 2
				If Operators.CompareString(FileSystem.Dir("c:\programme\irfanview\i_view32.exe", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_2B
				End If
				IL_21:
				num2 = 3
				Dim text As String = "c:\programme\irfanview"
				GoTo IL_98
				IL_2B:
				num2 = 5
				If Operators.CompareString(FileSystem.Dir("c:\program files\irfanview\i_view32.exe", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_4F
				End If
				IL_45:
				num2 = 6
				text = "c:\program files\irfanview"
				GoTo IL_98
				IL_4F:
				num2 = 8
				If Operators.CompareString(FileSystem.Dir("d:\programme\irfanview\i_view32.exe", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_74
				End If
				IL_69:
				num2 = 9
				text = "d:\programme\irfanview"
				GoTo IL_98
				IL_74:
				num2 = 11
				If Operators.CompareString(FileSystem.Dir("d:\program files\irfanview\i_view32.exe", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_98
				End If
				IL_8F:
				num2 = 12
				text = "d:\program files\irfanview"
				IL_98:
				num2 = 13
				If Operators.CompareString(text, "", False) = 0 Then
					GoTo IL_E0
				End If
				IL_A9:
				num2 = 14
				Dim name As String = modDeclares.Images(index).Name
				IL_BE:
				num2 = 15
				Dim pathName As String = text + "\i_view32 " + name
				IL_D0:
				num2 = 16
				Interaction.Shell(pathName, AppWinStyle.MaximizedFocus, False, -1)
				GoTo IL_139
				IL_E0:
				num2 = 18
				If Operators.CompareString(FileSystem.Dir("C:\Program Files\IrfanView\i_view64.exe", Microsoft.VisualBasic.FileAttribute.Normal), "", False) = 0 Then
					GoTo IL_139
				End If
				IL_FB:
				num2 = 19
				text = "C:\Program Files\IrfanView\i_view64.exe"
				IL_104:
				num2 = 20
				name = modDeclares.Images(index).Name
				IL_119:
				num2 = 21
				pathName = text + " " + name
				IL_12B:
				num2 = 22
				Interaction.Shell(pathName, AppWinStyle.MaximizedFocus, False, -1)
				IL_139:
				GoTo IL_1EB
				IL_13E:
				Dim num3 As Integer = num4 + 1
				num4 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num3)
				IL_1AC:
				GoTo IL_1E0
				IL_1AE:
				num4 = num2
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num)
				IL_1BE:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num <> 0 And num4 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_1AE
			End Try
			IL_1E0:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_1EB:
			If num4 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000889 RID: 2185 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_1_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600088A RID: 2186 RVA: 0x00045CAC File Offset: 0x00043EAC
		Private Sub _Picture1_1_DoubleClick(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			Me.StartIV(modPaint.pos + 1)
		End Sub

		' Token: 0x0600088B RID: 2187 RVA: 0x00045CBB File Offset: 0x00043EBB
		Private Sub _Picture1_2_DoubleClick(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			Me.StartIV(modPaint.pos + 2)
		End Sub

		' Token: 0x0600088C RID: 2188 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_3_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600088D RID: 2189 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_4_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600088E RID: 2190 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _Picture1_5_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600088F RID: 2191 RVA: 0x00045CCA File Offset: 0x00043ECA
		Private Sub _Picture1_5_DoubleClick(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			Me.StartIV(modPaint.pos + 5)
		End Sub

		' Token: 0x06000890 RID: 2192 RVA: 0x00045CD9 File Offset: 0x00043ED9
		Private Sub _Picture1_3_DoubleClick(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			Me.StartIV(modPaint.pos + 3)
		End Sub

		' Token: 0x06000891 RID: 2193 RVA: 0x00045CE8 File Offset: 0x00043EE8
		Private Sub _Picture1_4_DoubleClick(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			Me.StartIV(modPaint.pos + 4)
		End Sub

		' Token: 0x06000892 RID: 2194 RVA: 0x00045CF8 File Offset: 0x00043EF8
		Private Sub chkNoPreview_CheckedChanged(sender As Object, e As EventArgs)
			modDeclares.NO_PREVIEW = Me.chkNoPreview.Checked
			If modDeclares.NO_PREVIEW Then
				Me._Picture1_0.Image = Nothing
				Me._Picture1_1.Image = Nothing
				Me._Picture1_2.Image = Nothing
				Me._Picture1_3.Image = Nothing
				Me._Picture1_4.Image = Nothing
				Me._Picture1_5.Image = Nothing
				Return
			End If
			Me.UpdateLayout()
		End Sub

		' Token: 0x06000893 RID: 2195 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub txtSchritteBelichtung_TextChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000894 RID: 2196 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkOneToOne_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000895 RID: 2197 RVA: 0x00045D6C File Offset: 0x00043F6C
		Private Sub optNummer_CheckedChanged_1(sender As Object, e As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(sender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				If Me.optNummer.Checked Then
					Me.txtStart.Enabled = True
					Me.Label5.Enabled = True
				Else
					Me.txtStart.Enabled = False
					Me.Label5.Enabled = False
				End If
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000896 RID: 2198 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optNamen_CheckedChanged_1(sender As Object, e As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(sender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000897 RID: 2199 RVA: 0x0003EC2F File Offset: 0x0003CE2F
		Private Sub optDreiTeilig_CheckedChanged_1(sender As Object, e As EventArgs)
			If Conversions.ToBoolean(NewLateBinding.LateGet(sender, Nothing, "Checked", New Object(-1) {}, Nothing, Nothing, Nothing)) Then
				modDeclares.NoImageUpdate = True
				Me.UpdateLayout()
				modDeclares.NoImageUpdate = False
			End If
		End Sub

		' Token: 0x06000898 RID: 2200 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkTwoLines_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000899 RID: 2201 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub _tabSettings_TabPage2_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600089A RID: 2202 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Label31_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600089B RID: 2203 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub txtQuerBlipBreite_TextChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600089C RID: 2204 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub txtQuerBlipHoehe_TextChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0600089D RID: 2205 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub txtQuerBlipY_TextChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x04000444 RID: 1092
		Private components As IContainer

		' Token: 0x04000445 RID: 1093
		Public ToolTip1 As ToolTip
	End Class
End Namespace
