Imports System
Imports System.ComponentModel
Imports System.Diagnostics
Imports System.Drawing
Imports System.Runtime.CompilerServices
Imports System.Windows.Forms
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x02000017 RID: 23
	<DesignerGenerated()>
	Friend Class frmFilming
		Inherits Form

		' Token: 0x060004A0 RID: 1184 RVA: 0x0001EDEF File Offset: 0x0001CFEF
		<DebuggerNonUserCode()>
		Public Sub New()
			AddHandler MyBase.Load, AddressOf Me.frmFilming_Load
			Me.InitializeComponent()
		End Sub

		' Token: 0x060004A1 RID: 1185 RVA: 0x0001EE0F File Offset: 0x0001D00F
		<DebuggerNonUserCode()>
		Protected Overrides Sub Dispose(Disposing As Boolean)
			If Disposing AndAlso Me.components IsNot Nothing Then
				Me.components.Dispose()
			End If
			MyBase.Dispose(Disposing)
		End Sub

		' Token: 0x1700004A RID: 74
		' (get) Token: 0x060004A2 RID: 1186 RVA: 0x0001EE2E File Offset: 0x0001D02E
		' (set) Token: 0x060004A3 RID: 1187 RVA: 0x0001EE38 File Offset: 0x0001D038
		Public Overridable Property lstInfo As ListBox
			<CompilerGenerated()>
			Get
				Return Me._lstInfo
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As ListBox)
				Dim value2 As EventHandler = AddressOf Me.lstInfo_SelectedIndexChanged
				Dim lstInfo As ListBox = Me._lstInfo
				If lstInfo IsNot Nothing Then
					RemoveHandler lstInfo.SelectedIndexChanged, value2
				End If
				Me._lstInfo = value
				lstInfo = Me._lstInfo
				If lstInfo IsNot Nothing Then
					AddHandler lstInfo.SelectedIndexChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700004B RID: 75
		' (get) Token: 0x060004A4 RID: 1188 RVA: 0x0001EE7B File Offset: 0x0001D07B
		' (set) Token: 0x060004A5 RID: 1189 RVA: 0x0001EE83 File Offset: 0x0001D083
		Public Overridable Property lblilmNrAufFilm As Label

		' Token: 0x1700004C RID: 76
		' (get) Token: 0x060004A6 RID: 1190 RVA: 0x0001EE8C File Offset: 0x0001D08C
		' (set) Token: 0x060004A7 RID: 1191 RVA: 0x0001EE94 File Offset: 0x0001D094
		Public Overridable Property Label8 As Label

		' Token: 0x1700004D RID: 77
		' (get) Token: 0x060004A8 RID: 1192 RVA: 0x0001EE9D File Offset: 0x0001D09D
		' (set) Token: 0x060004A9 RID: 1193 RVA: 0x0001EEA5 File Offset: 0x0001D0A5
		Public Overridable Property Label15 As Label

		' Token: 0x1700004E RID: 78
		' (get) Token: 0x060004AA RID: 1194 RVA: 0x0001EEAE File Offset: 0x0001D0AE
		' (set) Token: 0x060004AB RID: 1195 RVA: 0x0001EEB6 File Offset: 0x0001D0B6
		Public Overridable Property lblTimeRemaining As Label

		' Token: 0x1700004F RID: 79
		' (get) Token: 0x060004AC RID: 1196 RVA: 0x0001EEBF File Offset: 0x0001D0BF
		' (set) Token: 0x060004AD RID: 1197 RVA: 0x0001EEC7 File Offset: 0x0001D0C7
		Public Overridable Property Label13 As Label

		' Token: 0x17000050 RID: 80
		' (get) Token: 0x060004AE RID: 1198 RVA: 0x0001EED0 File Offset: 0x0001D0D0
		' (set) Token: 0x060004AF RID: 1199 RVA: 0x0001EED8 File Offset: 0x0001D0D8
		Public Overridable Property lblExposedFrames As Label

		' Token: 0x17000051 RID: 81
		' (get) Token: 0x060004B0 RID: 1200 RVA: 0x0001EEE1 File Offset: 0x0001D0E1
		' (set) Token: 0x060004B1 RID: 1201 RVA: 0x0001EEE9 File Offset: 0x0001D0E9
		Public Overridable Property Label12 As Label

		' Token: 0x17000052 RID: 82
		' (get) Token: 0x060004B2 RID: 1202 RVA: 0x0001EEF2 File Offset: 0x0001D0F2
		' (set) Token: 0x060004B3 RID: 1203 RVA: 0x0001EEFA File Offset: 0x0001D0FA
		Public Overridable Property lblFolder As Label

		' Token: 0x17000053 RID: 83
		' (get) Token: 0x060004B4 RID: 1204 RVA: 0x0001EF03 File Offset: 0x0001D103
		' (set) Token: 0x060004B5 RID: 1205 RVA: 0x0001EF0B File Offset: 0x0001D10B
		Public Overridable Property Label10 As Label

		' Token: 0x17000054 RID: 84
		' (get) Token: 0x060004B6 RID: 1206 RVA: 0x0001EF14 File Offset: 0x0001D114
		' (set) Token: 0x060004B7 RID: 1207 RVA: 0x0001EF1C File Offset: 0x0001D11C
		Public Overridable Property lblFileName As Label

		' Token: 0x17000055 RID: 85
		' (get) Token: 0x060004B8 RID: 1208 RVA: 0x0001EF25 File Offset: 0x0001D125
		' (set) Token: 0x060004B9 RID: 1209 RVA: 0x0001EF2D File Offset: 0x0001D12D
		Public Overridable Property lblAktDoc As Label

		' Token: 0x17000056 RID: 86
		' (get) Token: 0x060004BA RID: 1210 RVA: 0x0001EF36 File Offset: 0x0001D136
		' (set) Token: 0x060004BB RID: 1211 RVA: 0x0001EF3E File Offset: 0x0001D13E
		Public Overridable Property lblAnzahlFrames As Label

		' Token: 0x17000057 RID: 87
		' (get) Token: 0x060004BC RID: 1212 RVA: 0x0001EF47 File Offset: 0x0001D147
		' (set) Token: 0x060004BD RID: 1213 RVA: 0x0001EF4F File Offset: 0x0001D14F
		Public Overridable Property Label11 As Label

		' Token: 0x17000058 RID: 88
		' (get) Token: 0x060004BE RID: 1214 RVA: 0x0001EF58 File Offset: 0x0001D158
		' (set) Token: 0x060004BF RID: 1215 RVA: 0x0001EF60 File Offset: 0x0001D160
		Public Overridable Property lblAktPage As Label

		' Token: 0x17000059 RID: 89
		' (get) Token: 0x060004C0 RID: 1216 RVA: 0x0001EF69 File Offset: 0x0001D169
		' (set) Token: 0x060004C1 RID: 1217 RVA: 0x0001EF71 File Offset: 0x0001D171
		Public Overridable Property Label9 As Label

		' Token: 0x1700005A RID: 90
		' (get) Token: 0x060004C2 RID: 1218 RVA: 0x0001EF7A File Offset: 0x0001D17A
		' (set) Token: 0x060004C3 RID: 1219 RVA: 0x0001EF82 File Offset: 0x0001D182
		Public Overridable Property Label7 As Label

		' Token: 0x1700005B RID: 91
		' (get) Token: 0x060004C4 RID: 1220 RVA: 0x0001EF8B File Offset: 0x0001D18B
		' (set) Token: 0x060004C5 RID: 1221 RVA: 0x0001EF93 File Offset: 0x0001D193
		Public Overridable Property Label6 As Label

		' Token: 0x1700005C RID: 92
		' (get) Token: 0x060004C6 RID: 1222 RVA: 0x0001EF9C File Offset: 0x0001D19C
		' (set) Token: 0x060004C7 RID: 1223 RVA: 0x0001EFA4 File Offset: 0x0001D1A4
		Public Overridable Property Label5 As Label

		' Token: 0x1700005D RID: 93
		' (get) Token: 0x060004C8 RID: 1224 RVA: 0x0001EFAD File Offset: 0x0001D1AD
		' (set) Token: 0x060004C9 RID: 1225 RVA: 0x0001EFB5 File Offset: 0x0001D1B5
		Public Overridable Property _Shape1_8 As Panel

		' Token: 0x1700005E RID: 94
		' (get) Token: 0x060004CA RID: 1226 RVA: 0x0001EFBE File Offset: 0x0001D1BE
		' (set) Token: 0x060004CB RID: 1227 RVA: 0x0001EFC6 File Offset: 0x0001D1C6
		Public Overridable Property _Shape1_7 As Panel

		' Token: 0x1700005F RID: 95
		' (get) Token: 0x060004CC RID: 1228 RVA: 0x0001EFCF File Offset: 0x0001D1CF
		' (set) Token: 0x060004CD RID: 1229 RVA: 0x0001EFD7 File Offset: 0x0001D1D7
		Public Overridable Property _Shape1_6 As Panel

		' Token: 0x17000060 RID: 96
		' (get) Token: 0x060004CE RID: 1230 RVA: 0x0001EFE0 File Offset: 0x0001D1E0
		' (set) Token: 0x060004CF RID: 1231 RVA: 0x0001EFE8 File Offset: 0x0001D1E8
		Public Overridable Property _Shape1_5 As Panel

		' Token: 0x17000061 RID: 97
		' (get) Token: 0x060004D0 RID: 1232 RVA: 0x0001EFF1 File Offset: 0x0001D1F1
		' (set) Token: 0x060004D1 RID: 1233 RVA: 0x0001EFF9 File Offset: 0x0001D1F9
		Public Overridable Property _Shape1_4 As Panel

		' Token: 0x17000062 RID: 98
		' (get) Token: 0x060004D2 RID: 1234 RVA: 0x0001F002 File Offset: 0x0001D202
		' (set) Token: 0x060004D3 RID: 1235 RVA: 0x0001F00A File Offset: 0x0001D20A
		Public Overridable Property _Shape1_3 As Panel

		' Token: 0x17000063 RID: 99
		' (get) Token: 0x060004D4 RID: 1236 RVA: 0x0001F013 File Offset: 0x0001D213
		' (set) Token: 0x060004D5 RID: 1237 RVA: 0x0001F01B File Offset: 0x0001D21B
		Public Overridable Property _Shape1_2 As Panel

		' Token: 0x17000064 RID: 100
		' (get) Token: 0x060004D6 RID: 1238 RVA: 0x0001F024 File Offset: 0x0001D224
		' (set) Token: 0x060004D7 RID: 1239 RVA: 0x0001F02C File Offset: 0x0001D22C
		Public Overridable Property _Shape1_1 As Panel

		' Token: 0x17000065 RID: 101
		' (get) Token: 0x060004D8 RID: 1240 RVA: 0x0001F035 File Offset: 0x0001D235
		' (set) Token: 0x060004D9 RID: 1241 RVA: 0x0001F03D File Offset: 0x0001D23D
		Public Overridable Property _Shape1_0 As Panel

		' Token: 0x17000066 RID: 102
		' (get) Token: 0x060004DA RID: 1242 RVA: 0x0001F046 File Offset: 0x0001D246
		' (set) Token: 0x060004DB RID: 1243 RVA: 0x0001F04E File Offset: 0x0001D24E
		Public Overridable Property Label2 As Label

		' Token: 0x17000067 RID: 103
		' (get) Token: 0x060004DC RID: 1244 RVA: 0x0001F057 File Offset: 0x0001D257
		' (set) Token: 0x060004DD RID: 1245 RVA: 0x0001F05F File Offset: 0x0001D25F
		Public Overridable Property Label3 As Label

		' Token: 0x17000068 RID: 104
		' (get) Token: 0x060004DE RID: 1246 RVA: 0x0001F068 File Offset: 0x0001D268
		' (set) Token: 0x060004DF RID: 1247 RVA: 0x0001F070 File Offset: 0x0001D270
		Public Overridable Property lblFilmNr As Label

		' Token: 0x17000069 RID: 105
		' (get) Token: 0x060004E0 RID: 1248 RVA: 0x0001F079 File Offset: 0x0001D279
		' (set) Token: 0x060004E1 RID: 1249 RVA: 0x0001F081 File Offset: 0x0001D281
		Public Overridable Property Label4 As Label

		' Token: 0x1700006A RID: 106
		' (get) Token: 0x060004E2 RID: 1250 RVA: 0x0001F08A File Offset: 0x0001D28A
		' (set) Token: 0x060004E3 RID: 1251 RVA: 0x0001F092 File Offset: 0x0001D292
		Public Overridable Property lblRestframes As Label

		' Token: 0x1700006B RID: 107
		' (get) Token: 0x060004E4 RID: 1252 RVA: 0x0001F09B File Offset: 0x0001D29B
		' (set) Token: 0x060004E5 RID: 1253 RVA: 0x0001F0A3 File Offset: 0x0001D2A3
		Public Overridable Property lblImages As Label

		' Token: 0x1700006C RID: 108
		' (get) Token: 0x060004E6 RID: 1254 RVA: 0x0001F0AC File Offset: 0x0001D2AC
		' (set) Token: 0x060004E7 RID: 1255 RVA: 0x0001F0B4 File Offset: 0x0001D2B4
		Public Overridable Property Label1 As Label

		' Token: 0x060004E8 RID: 1256 RVA: 0x0001F0C0 File Offset: 0x0001D2C0
		<DebuggerStepThrough()>
		Private Sub InitializeComponent()
			Me.components = New Container()
			Dim componentResourceManager As ComponentResourceManager = New ComponentResourceManager(GetType(frmFilming))
			Me.ToolTip1 = New ToolTip(Me.components)
			Me._Shape1_8 = New Panel()
			Me._Shape1_7 = New Panel()
			Me._Shape1_6 = New Panel()
			Me._Shape1_5 = New Panel()
			Me._Shape1_4 = New Panel()
			Me._Shape1_3 = New Panel()
			Me._Shape1_2 = New Panel()
			Me._Shape1_1 = New Panel()
			Me._Shape1_0 = New Panel()
			Me.lstInfo = New ListBox()
			Me.lblilmNrAufFilm = New Label()
			Me.Label8 = New Label()
			Me.Label15 = New Label()
			Me.lblTimeRemaining = New Label()
			Me.Label13 = New Label()
			Me.lblExposedFrames = New Label()
			Me.Label12 = New Label()
			Me.lblFolder = New Label()
			Me.Label10 = New Label()
			Me.lblFileName = New Label()
			Me.lblAktDoc = New Label()
			Me.lblAnzahlFrames = New Label()
			Me.Label11 = New Label()
			Me.lblAktPage = New Label()
			Me.Label9 = New Label()
			Me.Label7 = New Label()
			Me.Label6 = New Label()
			Me.Label5 = New Label()
			Me.Label2 = New Label()
			Me.Label3 = New Label()
			Me.lblFilmNr = New Label()
			Me.Label4 = New Label()
			Me.lblRestframes = New Label()
			Me.lblImages = New Label()
			Me.Label1 = New Label()
			Me.cmdEnd = New Button()
			MyBase.SuspendLayout()
			Me._Shape1_8.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_8.Location = New Point(449, 591)
			Me._Shape1_8.Name = "_Shape1_8"
			Me._Shape1_8.Size = New Size(21, 17)
			Me._Shape1_8.TabIndex = 0
			Me._Shape1_7.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_7.Location = New Point(429, 591)
			Me._Shape1_7.Name = "_Shape1_7"
			Me._Shape1_7.Size = New Size(21, 17)
			Me._Shape1_7.TabIndex = 0
			Me._Shape1_6.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_6.Location = New Point(409, 591)
			Me._Shape1_6.Name = "_Shape1_6"
			Me._Shape1_6.Size = New Size(21, 17)
			Me._Shape1_6.TabIndex = 0
			Me._Shape1_5.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_5.Location = New Point(449, 575)
			Me._Shape1_5.Name = "_Shape1_5"
			Me._Shape1_5.Size = New Size(21, 17)
			Me._Shape1_5.TabIndex = 0
			Me._Shape1_4.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_4.Location = New Point(429, 575)
			Me._Shape1_4.Name = "_Shape1_4"
			Me._Shape1_4.Size = New Size(21, 17)
			Me._Shape1_4.TabIndex = 0
			Me._Shape1_3.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_3.Location = New Point(409, 575)
			Me._Shape1_3.Name = "_Shape1_3"
			Me._Shape1_3.Size = New Size(21, 17)
			Me._Shape1_3.TabIndex = 0
			Me._Shape1_2.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_2.Location = New Point(449, 559)
			Me._Shape1_2.Name = "_Shape1_2"
			Me._Shape1_2.Size = New Size(21, 17)
			Me._Shape1_2.TabIndex = 0
			Me._Shape1_1.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_1.Location = New Point(429, 559)
			Me._Shape1_1.Name = "_Shape1_1"
			Me._Shape1_1.Size = New Size(21, 17)
			Me._Shape1_1.TabIndex = 0
			Me._Shape1_0.BackColor = Color.FromArgb(224, 224, 224)
			Me._Shape1_0.Location = New Point(409, 559)
			Me._Shape1_0.Name = "_Shape1_0"
			Me._Shape1_0.Size = New Size(21, 17)
			Me._Shape1_0.TabIndex = 0
			Me.lstInfo.BackColor = SystemColors.Window
			Me.lstInfo.Cursor = Cursors.[Default]
			Me.lstInfo.ForeColor = SystemColors.WindowText
			Me.lstInfo.ItemHeight = 20
			Me.lstInfo.Location = New Point(37, 530)
			Me.lstInfo.Margin = New Padding(5)
			Me.lstInfo.Name = "lstInfo"
			Me.lstInfo.RightToLeft = RightToLeft.No
			Me.lstInfo.Size = New Size(225, 184)
			Me.lstInfo.TabIndex = 24
			Me.lblilmNrAufFilm.BackColor = SystemColors.Control
			Me.lblilmNrAufFilm.BorderStyle = BorderStyle.Fixed3D
			Me.lblilmNrAufFilm.Cursor = Cursors.[Default]
			Me.lblilmNrAufFilm.ForeColor = SystemColors.ControlText
			Me.lblilmNrAufFilm.Location = New Point(196, 68)
			Me.lblilmNrAufFilm.Margin = New Padding(5, 0, 5, 0)
			Me.lblilmNrAufFilm.Name = "lblilmNrAufFilm"
			Me.lblilmNrAufFilm.RightToLeft = RightToLeft.No
			Me.lblilmNrAufFilm.Size = New Size(395, 34)
			Me.lblilmNrAufFilm.TabIndex = 26
			Me.lblilmNrAufFilm.Text = "0"
			Me.lblilmNrAufFilm.TextAlign = ContentAlignment.MiddleRight
			Me.Label8.BackColor = SystemColors.Control
			Me.Label8.Cursor = Cursors.[Default]
			Me.Label8.ForeColor = SystemColors.ControlText
			Me.Label8.Location = New Point(-32, 83)
			Me.Label8.Margin = New Padding(5, 0, 5, 0)
			Me.Label8.Name = "Label8"
			Me.Label8.RightToLeft = RightToLeft.No
			Me.Label8.Size = New Size(201, 24)
			Me.Label8.TabIndex = 25
			Me.Label8.Text = "on Film"
			Me.Label8.TextAlign = ContentAlignment.TopRight
			Me.Label15.BackColor = SystemColors.Control
			Me.Label15.Cursor = Cursors.[Default]
			Me.Label15.ForeColor = SystemColors.ControlText
			Me.Label15.Location = New Point(-102, 487)
			Me.Label15.Margin = New Padding(5, 0, 5, 0)
			Me.Label15.Name = "Label15"
			Me.Label15.RightToLeft = RightToLeft.No
			Me.Label15.Size = New Size(289, 24)
			Me.Label15.TabIndex = 23
			Me.Label15.Text = "rem. Time"
			Me.Label15.TextAlign = ContentAlignment.TopRight
			Me.lblTimeRemaining.BackColor = SystemColors.Control
			Me.lblTimeRemaining.BorderStyle = BorderStyle.Fixed3D
			Me.lblTimeRemaining.Cursor = Cursors.[Default]
			Me.lblTimeRemaining.ForeColor = SystemColors.ControlText
			Me.lblTimeRemaining.Location = New Point(196, 483)
			Me.lblTimeRemaining.Margin = New Padding(5, 0, 5, 0)
			Me.lblTimeRemaining.Name = "lblTimeRemaining"
			Me.lblTimeRemaining.RightToLeft = RightToLeft.No
			Me.lblTimeRemaining.Size = New Size(395, 34)
			Me.lblTimeRemaining.TabIndex = 22
			Me.lblTimeRemaining.Text = "0"
			Me.lblTimeRemaining.TextAlign = ContentAlignment.MiddleRight
			Me.Label13.BackColor = SystemColors.Control
			Me.Label13.Cursor = Cursors.[Default]
			Me.Label13.ForeColor = SystemColors.ControlText
			Me.Label13.Location = New Point(-102, 403)
			Me.Label13.Margin = New Padding(5, 0, 5, 0)
			Me.Label13.Name = "Label13"
			Me.Label13.RightToLeft = RightToLeft.No
			Me.Label13.Size = New Size(289, 24)
			Me.Label13.TabIndex = 21
			Me.Label13.Text = "exposed Frames"
			Me.Label13.TextAlign = ContentAlignment.TopRight
			Me.lblExposedFrames.BackColor = SystemColors.Control
			Me.lblExposedFrames.BorderStyle = BorderStyle.Fixed3D
			Me.lblExposedFrames.Cursor = Cursors.[Default]
			Me.lblExposedFrames.ForeColor = SystemColors.ControlText
			Me.lblExposedFrames.Location = New Point(196, 395)
			Me.lblExposedFrames.Margin = New Padding(5, 0, 5, 0)
			Me.lblExposedFrames.Name = "lblExposedFrames"
			Me.lblExposedFrames.RightToLeft = RightToLeft.No
			Me.lblExposedFrames.Size = New Size(395, 34)
			Me.lblExposedFrames.TabIndex = 20
			Me.lblExposedFrames.Text = "0"
			Me.lblExposedFrames.TextAlign = ContentAlignment.MiddleRight
			Me.Label12.BackColor = SystemColors.Control
			Me.Label12.Cursor = Cursors.[Default]
			Me.Label12.ForeColor = SystemColors.ControlText
			Me.Label12.Location = New Point(-8, 121)
			Me.Label12.Margin = New Padding(5, 0, 5, 0)
			Me.Label12.Name = "Label12"
			Me.Label12.RightToLeft = RightToLeft.No
			Me.Label12.Size = New Size(195, 24)
			Me.Label12.TabIndex = 19
			Me.Label12.Text = "Directory"
			Me.Label12.TextAlign = ContentAlignment.TopRight
			Me.lblFolder.BorderStyle = BorderStyle.Fixed3D
			Me.lblFolder.Location = New Point(196, 107)
			Me.lblFolder.Margin = New Padding(5, 0, 5, 0)
			Me.lblFolder.Name = "lblFolder"
			Me.lblFolder.Size = New Size(395, 46)
			Me.lblFolder.TabIndex = 18
			Me.Label10.BackColor = SystemColors.Control
			Me.Label10.Cursor = Cursors.[Default]
			Me.Label10.ForeColor = SystemColors.ControlText
			Me.Label10.Location = New Point(-8, 211)
			Me.Label10.Margin = New Padding(5, 0, 5, 0)
			Me.Label10.Name = "Label10"
			Me.Label10.RightToLeft = RightToLeft.No
			Me.Label10.Size = New Size(195, 24)
			Me.Label10.TabIndex = 17
			Me.Label10.Text = "Filename"
			Me.Label10.TextAlign = ContentAlignment.TopRight
			Me.lblFileName.BorderStyle = BorderStyle.Fixed3D
			Me.lblFileName.Font = New Font("Microsoft Sans Serif", 8.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.lblFileName.Location = New Point(196, 205)
			Me.lblFileName.Margin = New Padding(5, 0, 5, 0)
			Me.lblFileName.Name = "lblFileName"
			Me.lblFileName.Size = New Size(395, 34)
			Me.lblFileName.TabIndex = 16
			Me.lblAktDoc.BorderStyle = BorderStyle.Fixed3D
			Me.lblAktDoc.Location = New Point(196, 158)
			Me.lblAktDoc.Margin = New Padding(5, 0, 5, 0)
			Me.lblAktDoc.Name = "lblAktDoc"
			Me.lblAktDoc.Size = New Size(395, 34)
			Me.lblAktDoc.TabIndex = 15
			Me.lblAnzahlFrames.BackColor = SystemColors.Control
			Me.lblAnzahlFrames.BorderStyle = BorderStyle.Fixed3D
			Me.lblAnzahlFrames.Cursor = Cursors.[Default]
			Me.lblAnzahlFrames.ForeColor = SystemColors.ControlText
			Me.lblAnzahlFrames.Location = New Point(196, 439)
			Me.lblAnzahlFrames.Margin = New Padding(5, 0, 5, 0)
			Me.lblAnzahlFrames.Name = "lblAnzahlFrames"
			Me.lblAnzahlFrames.RightToLeft = RightToLeft.No
			Me.lblAnzahlFrames.Size = New Size(395, 34)
			Me.lblAnzahlFrames.TabIndex = 14
			Me.lblAnzahlFrames.Text = "0"
			Me.lblAnzahlFrames.TextAlign = ContentAlignment.MiddleRight
			Me.Label11.BackColor = SystemColors.Control
			Me.Label11.Cursor = Cursors.[Default]
			Me.Label11.ForeColor = SystemColors.ControlText
			Me.Label11.Location = New Point(-102, 447)
			Me.Label11.Margin = New Padding(5, 0, 5, 0)
			Me.Label11.Name = "Label11"
			Me.Label11.RightToLeft = RightToLeft.No
			Me.Label11.Size = New Size(289, 24)
			Me.Label11.TabIndex = 13
			Me.Label11.Text = "available Frames"
			Me.Label11.TextAlign = ContentAlignment.TopRight
			Me.lblAktPage.BackColor = SystemColors.Control
			Me.lblAktPage.BorderStyle = BorderStyle.Fixed3D
			Me.lblAktPage.Cursor = Cursors.[Default]
			Me.lblAktPage.ForeColor = SystemColors.ControlText
			Me.lblAktPage.Location = New Point(196, 256)
			Me.lblAktPage.Margin = New Padding(5, 0, 5, 0)
			Me.lblAktPage.Name = "lblAktPage"
			Me.lblAktPage.RightToLeft = RightToLeft.No
			Me.lblAktPage.Size = New Size(395, 34)
			Me.lblAktPage.TabIndex = 12
			Me.lblAktPage.TextAlign = ContentAlignment.MiddleRight
			Me.Label9.BackColor = SystemColors.Control
			Me.Label9.Cursor = Cursors.[Default]
			Me.Label9.ForeColor = SystemColors.ControlText
			Me.Label9.Location = New Point(-102, 264)
			Me.Label9.Margin = New Padding(5, 0, 5, 0)
			Me.Label9.Name = "Label9"
			Me.Label9.RightToLeft = RightToLeft.No
			Me.Label9.Size = New Size(289, 24)
			Me.Label9.TabIndex = 11
			Me.Label9.Text = "current Page"
			Me.Label9.TextAlign = ContentAlignment.TopRight
			Me.Label7.BackColor = SystemColors.Control
			Me.Label7.Cursor = Cursors.[Default]
			Me.Label7.ForeColor = SystemColors.ControlText
			Me.Label7.Location = New Point(-102, 166)
			Me.Label7.Margin = New Padding(5, 0, 5, 0)
			Me.Label7.Name = "Label7"
			Me.Label7.RightToLeft = RightToLeft.No
			Me.Label7.Size = New Size(289, 24)
			Me.Label7.TabIndex = 10
			Me.Label7.Text = "current Document"
			Me.Label7.TextAlign = ContentAlignment.TopRight
			Me.Label6.BackColor = SystemColors.Control
			Me.Label6.Cursor = Cursors.[Default]
			Me.Label6.ForeColor = SystemColors.ControlText
			Me.Label6.Location = New Point(594, 352)
			Me.Label6.Margin = New Padding(5, 0, 5, 0)
			Me.Label6.Name = "Label6"
			Me.Label6.RightToLeft = RightToLeft.No
			Me.Label6.Size = New Size(29, 29)
			Me.Label6.TabIndex = 9
			Me.Label6.Text = "m"
			Me.Label6.TextAlign = ContentAlignment.TopRight
			Me.Label5.BackColor = SystemColors.Control
			Me.Label5.BorderStyle = BorderStyle.Fixed3D
			Me.Label5.Cursor = Cursors.[Default]
			Me.Label5.ForeColor = SystemColors.ControlText
			Me.Label5.Location = New Point(440, 625)
			Me.Label5.Margin = New Padding(5, 0, 5, 0)
			Me.Label5.Name = "Label5"
			Me.Label5.RightToLeft = RightToLeft.No
			Me.Label5.Size = New Size(71, 24)
			Me.Label5.TabIndex = 8
			Me.Label5.Text = "OFF"
			Me.Label5.Visible = False
			Me.Label2.BackColor = SystemColors.Control
			Me.Label2.Cursor = Cursors.[Default]
			Me.Label2.ForeColor = SystemColors.ControlText
			Me.Label2.Location = New Point(340, 625)
			Me.Label2.Margin = New Padding(5, 0, 5, 0)
			Me.Label2.Name = "Label2"
			Me.Label2.RightToLeft = RightToLeft.No
			Me.Label2.Size = New Size(86, 24)
			Me.Label2.TabIndex = 7
			Me.Label2.Text = "Splitting"
			Me.Label2.TextAlign = ContentAlignment.TopRight
			Me.Label3.BackColor = SystemColors.Control
			Me.Label3.Cursor = Cursors.[Default]
			Me.Label3.ForeColor = SystemColors.ControlText
			Me.Label3.Location = New Point(-40, 31)
			Me.Label3.Margin = New Padding(5, 0, 5, 0)
			Me.Label3.Name = "Label3"
			Me.Label3.RightToLeft = RightToLeft.No
			Me.Label3.Size = New Size(221, 24)
			Me.Label3.TabIndex = 6
			Me.Label3.Text = "No of Roll"
			Me.Label3.TextAlign = ContentAlignment.TopRight
			Me.lblFilmNr.BackColor = SystemColors.Control
			Me.lblFilmNr.BorderStyle = BorderStyle.Fixed3D
			Me.lblFilmNr.Cursor = Cursors.[Default]
			Me.lblFilmNr.ForeColor = SystemColors.ControlText
			Me.lblFilmNr.Location = New Point(196, 23)
			Me.lblFilmNr.Margin = New Padding(5, 0, 5, 0)
			Me.lblFilmNr.Name = "lblFilmNr"
			Me.lblFilmNr.RightToLeft = RightToLeft.No
			Me.lblFilmNr.Size = New Size(395, 34)
			Me.lblFilmNr.TabIndex = 5
			Me.lblFilmNr.Text = "0"
			Me.lblFilmNr.TextAlign = ContentAlignment.MiddleRight
			Me.Label4.BackColor = SystemColors.Control
			Me.Label4.Cursor = Cursors.[Default]
			Me.Label4.ForeColor = SystemColors.ControlText
			Me.Label4.Location = New Point(-102, 353)
			Me.Label4.Margin = New Padding(5, 0, 5, 0)
			Me.Label4.Name = "Label4"
			Me.Label4.RightToLeft = RightToLeft.No
			Me.Label4.Size = New Size(289, 24)
			Me.Label4.TabIndex = 3
			Me.Label4.Text = "available Film"
			Me.Label4.TextAlign = ContentAlignment.TopRight
			Me.lblRestframes.BackColor = SystemColors.Control
			Me.lblRestframes.BorderStyle = BorderStyle.Fixed3D
			Me.lblRestframes.Cursor = Cursors.[Default]
			Me.lblRestframes.ForeColor = SystemColors.ControlText
			Me.lblRestframes.Location = New Point(196, 347)
			Me.lblRestframes.Margin = New Padding(5, 0, 5, 0)
			Me.lblRestframes.Name = "lblRestframes"
			Me.lblRestframes.RightToLeft = RightToLeft.No
			Me.lblRestframes.Size = New Size(395, 34)
			Me.lblRestframes.TabIndex = 2
			Me.lblRestframes.Text = "0"
			Me.lblRestframes.TextAlign = ContentAlignment.MiddleRight
			Me.lblImages.BackColor = SystemColors.Control
			Me.lblImages.BorderStyle = BorderStyle.Fixed3D
			Me.lblImages.Cursor = Cursors.[Default]
			Me.lblImages.ForeColor = SystemColors.ControlText
			Me.lblImages.Location = New Point(196, 303)
			Me.lblImages.Margin = New Padding(5, 0, 5, 0)
			Me.lblImages.Name = "lblImages"
			Me.lblImages.RightToLeft = RightToLeft.No
			Me.lblImages.Size = New Size(395, 34)
			Me.lblImages.TabIndex = 1
			Me.lblImages.Text = "0"
			Me.lblImages.TextAlign = ContentAlignment.MiddleRight
			Me.Label1.BackColor = SystemColors.Control
			Me.Label1.Cursor = Cursors.[Default]
			Me.Label1.ForeColor = SystemColors.ControlText
			Me.Label1.Location = New Point(52, 313)
			Me.Label1.Margin = New Padding(5, 0, 5, 0)
			Me.Label1.Name = "Label1"
			Me.Label1.RightToLeft = RightToLeft.No
			Me.Label1.Size = New Size(135, 24)
			Me.Label1.TabIndex = 0
			Me.Label1.Text = "to expose"
			Me.Label1.TextAlign = ContentAlignment.TopRight
			Me.cmdEnd.BackColor = Color.FromArgb(255, 192, 192)
			Me.cmdEnd.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdEnd.Location = New Point(313, 671)
			Me.cmdEnd.Margin = New Padding(5)
			Me.cmdEnd.Name = "cmdEnd"
			Me.cmdEnd.Size = New Size(310, 49)
			Me.cmdEnd.TabIndex = 28
			Me.cmdEnd.Text = "Stop Exposure"
			Me.cmdEnd.UseVisualStyleBackColor = False
			MyBase.AutoScaleDimensions = New SizeF(9F, 20F)
			MyBase.AutoScaleMode = AutoScaleMode.Font
			Me.BackColor = SystemColors.Control
			MyBase.ClientSize = New Size(637, 729)
			MyBase.Controls.Add(Me.cmdEnd)
			MyBase.Controls.Add(Me.lstInfo)
			MyBase.Controls.Add(Me.lblilmNrAufFilm)
			MyBase.Controls.Add(Me.Label8)
			MyBase.Controls.Add(Me.Label15)
			MyBase.Controls.Add(Me.lblTimeRemaining)
			MyBase.Controls.Add(Me.Label13)
			MyBase.Controls.Add(Me.lblExposedFrames)
			MyBase.Controls.Add(Me.Label12)
			MyBase.Controls.Add(Me.lblFolder)
			MyBase.Controls.Add(Me.Label10)
			MyBase.Controls.Add(Me.lblFileName)
			MyBase.Controls.Add(Me.lblAktDoc)
			MyBase.Controls.Add(Me.lblAnzahlFrames)
			MyBase.Controls.Add(Me.Label11)
			MyBase.Controls.Add(Me.lblAktPage)
			MyBase.Controls.Add(Me.Label9)
			MyBase.Controls.Add(Me.Label7)
			MyBase.Controls.Add(Me.Label6)
			MyBase.Controls.Add(Me.Label5)
			MyBase.Controls.Add(Me.Label2)
			MyBase.Controls.Add(Me.Label3)
			MyBase.Controls.Add(Me.lblFilmNr)
			MyBase.Controls.Add(Me.Label4)
			MyBase.Controls.Add(Me.lblRestframes)
			MyBase.Controls.Add(Me.lblImages)
			MyBase.Controls.Add(Me.Label1)
			Me.Cursor = Cursors.[Default]
			Me.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			MyBase.Icon = CType(componentResourceManager.GetObject("$this.Icon"), Icon)
			MyBase.Location = New Point(4, 23)
			MyBase.Margin = New Padding(5)
			MyBase.Name = "frmFilming"
			Me.RightToLeft = RightToLeft.No
			MyBase.StartPosition = FormStartPosition.Manual
			Me.Text = "Exposure of Documents"
			MyBase.ResumeLayout(False)
		End Sub

		' Token: 0x1700006D RID: 109
		' (get) Token: 0x060004E9 RID: 1257 RVA: 0x00020BA3 File Offset: 0x0001EDA3
		' (set) Token: 0x060004EA RID: 1258 RVA: 0x00020BAC File Offset: 0x0001EDAC
		Friend Overridable Property cmdEnd As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdEnd
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdEnd_Click
				Dim cmdEnd As Button = Me._cmdEnd
				If cmdEnd IsNot Nothing Then
					RemoveHandler cmdEnd.Click, value2
				End If
				Me._cmdEnd = value
				cmdEnd = Me._cmdEnd
				If cmdEnd IsNot Nothing Then
					AddHandler cmdEnd.Click, value2
				End If
			End Set
		End Property

		' Token: 0x060004EB RID: 1259 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdEnd_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x060004EC RID: 1260 RVA: 0x00020BF0 File Offset: 0x0001EDF0
		Private Sub frmFilming_Load(eventSender As Object, eventArgs As EventArgs)
			Dim num As Short
			MyBase.Top = CInt(Math.Round(Support.TwipsToPixelsY(Support.PixelsToTwipsY(CDbl(Screen.PrimaryScreen.Bounds.Height)) / 2.0 - Support.PixelsToTwipsY(CDbl(MyBase.Height)) / 2.0)))
			MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(modDeclares.ffrmFilmPreview.Width)) + Support.PixelsToTwipsX(CDbl(modDeclares.ffrmFilmPreview.Left)))))
			Dim form As Form = Me
			modMain.SetTexts(form)
			If modDeclares.SystemData.DoSplit Then
				Dim splitCount As Short = modDeclares.SystemData.SplitCount
				Return
			End If
			num = 0S
			Do
				num += 1S
			Loop While num <= 8S
			Me.Label5.Visible = True
		End Sub

		' Token: 0x060004ED RID: 1261 RVA: 0x00020CB8 File Offset: 0x0001EEB8
		Private Sub lblFilmNr_Change()
			Dim text As String = Conversions.ToString(Conversion.Val("0" + Me.lblFilmNr.Text))
			While CDbl(Strings.Len(text)) < Conversion.Val("0" + modDeclares.ffrmFilmPreview.txtRollNoLen.Text)
				text = "0" + text
			End While
			Me.lblilmNrAufFilm.Text = modDeclares.ffrmFilmPreview.txtRollNoPrefix.Text + text + modDeclares.ffrmFilmPreview.txtRollNoPostfix.Text
		End Sub

		' Token: 0x060004EE RID: 1262 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdEnd__Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x060004EF RID: 1263 RVA: 0x00020D49 File Offset: 0x0001EF49
		Private Sub cmdEnd_Click(sender As Object, e As EventArgs)
			modDeclares.DoCancel = True
		End Sub

		' Token: 0x060004F0 RID: 1264 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub lstInfo_SelectedIndexChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x0400041E RID: 1054
		Private components As IContainer

		' Token: 0x0400041F RID: 1055
		Public ToolTip1 As ToolTip
	End Class
End Namespace
