Imports System
Imports System.Collections
Imports System.ComponentModel
Imports System.Diagnostics
Imports System.Drawing
Imports System.Runtime.CompilerServices
Imports System.Windows.Forms
Imports fileconverter.My
Imports Microsoft.VisualBasic
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200003B RID: 59
	<DesignerGenerated()>
	Friend Class frmService
		Inherits Form

		' Token: 0x06000AEC RID: 2796 RVA: 0x000589E8 File Offset: 0x00056BE8
		<DebuggerNonUserCode()>
		Public Sub New()
			AddHandler MyBase.KeyDown, AddressOf Me.frmService_KeyDown
			AddHandler MyBase.Load, AddressOf Me.frmService_Load
			AddHandler MyBase.FormClosed, AddressOf Me.frmService_FormClosed
			Me.InitializeComponent()
		End Sub

		' Token: 0x06000AED RID: 2797 RVA: 0x00058A37 File Offset: 0x00056C37
		<DebuggerNonUserCode()>
		Protected Overrides Sub Dispose(Disposing As Boolean)
			If Disposing AndAlso Me.components IsNot Nothing Then
				Me.components.Dispose()
			End If
			MyBase.Dispose(Disposing)
		End Sub

		' Token: 0x17000283 RID: 643
		' (get) Token: 0x06000AEE RID: 2798 RVA: 0x00058A56 File Offset: 0x00056C56
		' (set) Token: 0x06000AEF RID: 2799 RVA: 0x00058A60 File Offset: 0x00056C60
		Public Overridable Property chkLamp As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkLamp
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkLamp_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkLamp_CheckedChanged
				Dim chkLamp As CheckBox = Me._chkLamp
				If chkLamp IsNot Nothing Then
					RemoveHandler chkLamp.CheckStateChanged, value2
					RemoveHandler chkLamp.CheckedChanged, value3
				End If
				Me._chkLamp = value
				chkLamp = Me._chkLamp
				If chkLamp IsNot Nothing Then
					AddHandler chkLamp.CheckStateChanged, value2
					AddHandler chkLamp.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x17000284 RID: 644
		' (get) Token: 0x06000AF0 RID: 2800 RVA: 0x00058ABE File Offset: 0x00056CBE
		' (set) Token: 0x06000AF1 RID: 2801 RVA: 0x00058AC8 File Offset: 0x00056CC8
		Public Overridable Property chkButler As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkButler
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkButler_CheckStateChanged
				Dim chkButler As CheckBox = Me._chkButler
				If chkButler IsNot Nothing Then
					RemoveHandler chkButler.CheckStateChanged, value2
				End If
				Me._chkButler = value
				chkButler = Me._chkButler
				If chkButler IsNot Nothing Then
					AddHandler chkButler.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x17000285 RID: 645
		' (get) Token: 0x06000AF2 RID: 2802 RVA: 0x00058B0B File Offset: 0x00056D0B
		' (set) Token: 0x06000AF3 RID: 2803 RVA: 0x00058B14 File Offset: 0x00056D14
		Public Overridable Property Test As Button
			<CompilerGenerated()>
			Get
				Return Me._Test
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Test_Click
				Dim test As Button = Me._Test
				If test IsNot Nothing Then
					RemoveHandler test.Click, value2
				End If
				Me._Test = value
				test = Me._Test
				If test IsNot Nothing Then
					AddHandler test.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000286 RID: 646
		' (get) Token: 0x06000AF4 RID: 2804 RVA: 0x00058B57 File Offset: 0x00056D57
		' (set) Token: 0x06000AF5 RID: 2805 RVA: 0x00058B60 File Offset: 0x00056D60
		Public Overridable Property cmdTestFilming As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdTestFilming
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdTestFilming_Click
				Dim cmdTestFilming As Button = Me._cmdTestFilming
				If cmdTestFilming IsNot Nothing Then
					RemoveHandler cmdTestFilming.Click, value2
				End If
				Me._cmdTestFilming = value
				cmdTestFilming = Me._cmdTestFilming
				If cmdTestFilming IsNot Nothing Then
					AddHandler cmdTestFilming.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000287 RID: 647
		' (get) Token: 0x06000AF6 RID: 2806 RVA: 0x00058BA3 File Offset: 0x00056DA3
		' (set) Token: 0x06000AF7 RID: 2807 RVA: 0x00058BAC File Offset: 0x00056DAC
		Public Overridable Property Timer1 As Timer
			<CompilerGenerated()>
			Get
				Return Me._Timer1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Timer)
				Dim value2 As EventHandler = AddressOf Me.Timer1_Tick
				Dim timer As Timer = Me._Timer1
				If timer IsNot Nothing Then
					RemoveHandler timer.Tick, value2
				End If
				Me._Timer1 = value
				timer = Me._Timer1
				If timer IsNot Nothing Then
					AddHandler timer.Tick, value2
				End If
			End Set
		End Property

		' Token: 0x17000288 RID: 648
		' (get) Token: 0x06000AF8 RID: 2808 RVA: 0x00058BEF File Offset: 0x00056DEF
		' (set) Token: 0x06000AF9 RID: 2809 RVA: 0x00058BF8 File Offset: 0x00056DF8
		Public Overridable Property chkventil As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkventil
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkventil_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkventil_CheckedChanged
				Dim chkventil As CheckBox = Me._chkventil
				If chkventil IsNot Nothing Then
					RemoveHandler chkventil.CheckStateChanged, value2
					RemoveHandler chkventil.CheckedChanged, value3
				End If
				Me._chkventil = value
				chkventil = Me._chkventil
				If chkventil IsNot Nothing Then
					AddHandler chkventil.CheckStateChanged, value2
					AddHandler chkventil.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x17000289 RID: 649
		' (get) Token: 0x06000AFA RID: 2810 RVA: 0x00058C56 File Offset: 0x00056E56
		' (set) Token: 0x06000AFB RID: 2811 RVA: 0x00058C60 File Offset: 0x00056E60
		Public Overridable Property chkFrameLighting As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkFrameLighting
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkFrameLighting_CheckStateChanged
				Dim chkFrameLighting As CheckBox = Me._chkFrameLighting
				If chkFrameLighting IsNot Nothing Then
					RemoveHandler chkFrameLighting.CheckStateChanged, value2
				End If
				Me._chkFrameLighting = value
				chkFrameLighting = Me._chkFrameLighting
				If chkFrameLighting IsNot Nothing Then
					AddHandler chkFrameLighting.CheckStateChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700028A RID: 650
		' (get) Token: 0x06000AFC RID: 2812 RVA: 0x00058CA3 File Offset: 0x00056EA3
		' (set) Token: 0x06000AFD RID: 2813 RVA: 0x00058CAC File Offset: 0x00056EAC
		Public Overridable Property cmdSensorCheck As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdSensorCheck
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdSensorCheck_Click
				Dim cmdSensorCheck As Button = Me._cmdSensorCheck
				If cmdSensorCheck IsNot Nothing Then
					RemoveHandler cmdSensorCheck.Click, value2
				End If
				Me._cmdSensorCheck = value
				cmdSensorCheck = Me._cmdSensorCheck
				If cmdSensorCheck IsNot Nothing Then
					AddHandler cmdSensorCheck.Click, value2
				End If
			End Set
		End Property

		' Token: 0x1700028B RID: 651
		' (get) Token: 0x06000AFE RID: 2814 RVA: 0x00058CEF File Offset: 0x00056EEF
		' (set) Token: 0x06000AFF RID: 2815 RVA: 0x00058CF8 File Offset: 0x00056EF8
		Public Overridable Property chkVakuumPumpe As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkVakuumPumpe
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkVakuumPumpe_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkVakuumPumpe_CheckedChanged
				Dim chkVakuumPumpe As CheckBox = Me._chkVakuumPumpe
				If chkVakuumPumpe IsNot Nothing Then
					RemoveHandler chkVakuumPumpe.CheckStateChanged, value2
					RemoveHandler chkVakuumPumpe.CheckedChanged, value3
				End If
				Me._chkVakuumPumpe = value
				chkVakuumPumpe = Me._chkVakuumPumpe
				If chkVakuumPumpe IsNot Nothing Then
					AddHandler chkVakuumPumpe.CheckStateChanged, value2
					AddHandler chkVakuumPumpe.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x1700028C RID: 652
		' (get) Token: 0x06000B00 RID: 2816 RVA: 0x00058D56 File Offset: 0x00056F56
		' (set) Token: 0x06000B01 RID: 2817 RVA: 0x00058D5E File Offset: 0x00056F5E
		Public Overridable Property _Shape_3 As Panel

		' Token: 0x1700028D RID: 653
		' (get) Token: 0x06000B02 RID: 2818 RVA: 0x00058D67 File Offset: 0x00056F67
		' (set) Token: 0x06000B03 RID: 2819 RVA: 0x00058D6F File Offset: 0x00056F6F
		Public Overridable Property Label11 As Label

		' Token: 0x1700028E RID: 654
		' (get) Token: 0x06000B04 RID: 2820 RVA: 0x00058D78 File Offset: 0x00056F78
		' (set) Token: 0x06000B05 RID: 2821 RVA: 0x00058D80 File Offset: 0x00056F80
		Public Overridable Property Shape1 As Panel

		' Token: 0x1700028F RID: 655
		' (get) Token: 0x06000B06 RID: 2822 RVA: 0x00058D89 File Offset: 0x00056F89
		' (set) Token: 0x06000B07 RID: 2823 RVA: 0x00058D91 File Offset: 0x00056F91
		Public Overridable Property Shape2 As Panel

		' Token: 0x06000B08 RID: 2824 RVA: 0x00058D9C File Offset: 0x00056F9C
		<DebuggerStepThrough()>
		Private Sub InitializeComponent()
			Me.components = New Container()
			Me.ToolTip1 = New ToolTip(Me.components)
			Me._Shape_3 = New Panel()
			Me.Shape1 = New Panel()
			Me.Shape2 = New Panel()
			Me.chkLamp = New CheckBox()
			Me.chkButler = New CheckBox()
			Me.Test = New Button()
			Me.cmdTestFilming = New Button()
			Me.Timer1 = New Timer(Me.components)
			Me.chkventil = New CheckBox()
			Me.chkFrameLighting = New CheckBox()
			Me.cmdSensorCheck = New Button()
			Me.chkVakuumPumpe = New CheckBox()
			Me.Label11 = New Label()
			Me.cmdExit = New Button()
			Me.cmdLogon = New Button()
			Me.butExitDemo = New Button()
			Me.butReset = New Button()
			Me.Button1 = New Button()
			Me.Label10 = New Label()
			Me.Label2 = New Label()
			Me._Label1_0 = New Label()
			Me.Label8 = New Label()
			Me._Label1_2 = New Label()
			Me._txtSpeed_0 = New TextBox()
			Me.txtSchritte = New TextBox()
			Me.optAchtel = New RadioButton()
			Me.optViertel = New RadioButton()
			Me.optHalb = New RadioButton()
			Me.optEintel = New RadioButton()
			Me.Frame3 = New GroupBox()
			Me.txtSchrittePromm = New TextBox()
			Me._txtSpeed_1 = New TextBox()
			Me.chkFilmMotor = New CheckBox()
			Me.Label3 = New Label()
			Me.Label4 = New Label()
			Me.Label5 = New Label()
			Me.Label6 = New Label()
			Me._Label1_1 = New Label()
			Me.chkBlendenMotor = New CheckBox()
			Me.cmdNull = New CheckBox()
			Me._txtVerschlussSpeed_0 = New TextBox()
			Me.txtVerschlussSchritte = New TextBox()
			Me.txtVerschlussZeit = New TextBox()
			Me.optVEintel = New RadioButton()
			Me.optVHalb = New RadioButton()
			Me.optVViertel = New RadioButton()
			Me.optVAchtel = New RadioButton()
			Me.Frame2 = New GroupBox()
			Me._txtVerschlussSpeed_1 = New TextBox()
			Me.PictureBox1 = New PictureBox()
			Me.PictureBox2 = New PictureBox()
			Me.PictureBox3 = New PictureBox()
			Me.Frame3.SuspendLayout()
			Me.Frame2.SuspendLayout()
			CType(Me.PictureBox1, ISupportInitialize).BeginInit()
			CType(Me.PictureBox2, ISupportInitialize).BeginInit()
			CType(Me.PictureBox3, ISupportInitialize).BeginInit()
			MyBase.SuspendLayout()
			Me._Shape_3.BackColor = Color.FromArgb(128, 128, 128)
			Me._Shape_3.Location = New Point(439, 472)
			Me._Shape_3.Name = "_Shape_3"
			Me._Shape_3.Size = New Size(33, 29)
			Me._Shape_3.TabIndex = 0
			Me.Shape1.BackColor = Color.FromArgb(224, 224, 224)
			Me.Shape1.Location = New Point(40, 304)
			Me.Shape1.Name = "Shape1"
			Me.Shape1.Size = New Size(229, 65)
			Me.Shape1.TabIndex = 0
			Me.Shape2.BackColor = Color.FromArgb(224, 224, 224)
			Me.Shape2.Location = New Point(269, 304)
			Me.Shape2.Name = "Shape2"
			Me.Shape2.Size = New Size(273, 65)
			Me.Shape2.TabIndex = 0
			Me.chkLamp.Appearance = Appearance.Button
			Me.chkLamp.BackColor = SystemColors.Control
			Me.chkLamp.Cursor = Cursors.[Default]
			Me.chkLamp.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkLamp.ForeColor = SystemColors.ControlText
			Me.chkLamp.Location = New Point(593, 176)
			Me.chkLamp.Name = "chkLamp"
			Me.chkLamp.RightToLeft = RightToLeft.No
			Me.chkLamp.Size = New Size(185, 57)
			Me.chkLamp.TabIndex = 55
			Me.chkLamp.Text = "Front-LED"
			Me.chkLamp.TextAlign = ContentAlignment.MiddleCenter
			Me.chkLamp.UseVisualStyleBackColor = False
			Me.chkButler.Appearance = Appearance.Button
			Me.chkButler.BackColor = SystemColors.Control
			Me.chkButler.Cursor = Cursors.[Default]
			Me.chkButler.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkButler.ForeColor = SystemColors.ControlText
			Me.chkButler.Location = New Point(792, 335)
			Me.chkButler.Name = "chkButler"
			Me.chkButler.RightToLeft = RightToLeft.No
			Me.chkButler.Size = New Size(185, 57)
			Me.chkButler.TabIndex = 54
			Me.chkButler.Text = "Butler"
			Me.chkButler.TextAlign = ContentAlignment.MiddleCenter
			Me.chkButler.UseVisualStyleBackColor = False
			Me.chkButler.Visible = False
			Me.Test.BackColor = SystemColors.Control
			Me.Test.Cursor = Cursors.[Default]
			Me.Test.Font = New Font("Microsoft Sans Serif", 12F)
			Me.Test.ForeColor = SystemColors.ControlText
			Me.Test.Location = New Point(682, 458)
			Me.Test.Name = "Test"
			Me.Test.RightToLeft = RightToLeft.No
			Me.Test.Size = New Size(185, 41)
			Me.Test.TabIndex = 49
			Me.Test.Text = "Test"
			Me.Test.UseVisualStyleBackColor = False
			Me.Test.Visible = False
			Me.cmdTestFilming.BackColor = SystemColors.Control
			Me.cmdTestFilming.Cursor = Cursors.[Default]
			Me.cmdTestFilming.Enabled = False
			Me.cmdTestFilming.Font = New Font("Microsoft Sans Serif", 12F)
			Me.cmdTestFilming.ForeColor = SystemColors.ControlText
			Me.cmdTestFilming.Location = New Point(784, 363)
			Me.cmdTestFilming.Name = "cmdTestFilming"
			Me.cmdTestFilming.RightToLeft = RightToLeft.No
			Me.cmdTestFilming.Size = New Size(185, 57)
			Me.cmdTestFilming.TabIndex = 20
			Me.cmdTestFilming.Text = "Test Filming"
			Me.cmdTestFilming.UseVisualStyleBackColor = False
			Me.cmdTestFilming.Visible = False
			Me.Timer1.Interval = 500
			Me.chkventil.Appearance = Appearance.Button
			Me.chkventil.BackColor = SystemColors.Control
			Me.chkventil.Cursor = Cursors.[Default]
			Me.chkventil.Enabled = False
			Me.chkventil.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkventil.ForeColor = SystemColors.ControlText
			Me.chkventil.Location = New Point(593, 104)
			Me.chkventil.Name = "chkventil"
			Me.chkventil.RightToLeft = RightToLeft.No
			Me.chkventil.Size = New Size(185, 57)
			Me.chkventil.TabIndex = 5
			Me.chkventil.Text = "Vacuum Valve"
			Me.chkventil.TextAlign = ContentAlignment.MiddleCenter
			Me.chkventil.UseVisualStyleBackColor = False
			Me.chkFrameLighting.Appearance = Appearance.Button
			Me.chkFrameLighting.BackColor = SystemColors.Control
			Me.chkFrameLighting.Cursor = Cursors.[Default]
			Me.chkFrameLighting.Enabled = False
			Me.chkFrameLighting.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkFrameLighting.ForeColor = SystemColors.ControlText
			Me.chkFrameLighting.Location = New Point(854, 354)
			Me.chkFrameLighting.Name = "chkFrameLighting"
			Me.chkFrameLighting.RightToLeft = RightToLeft.No
			Me.chkFrameLighting.Size = New Size(185, 57)
			Me.chkFrameLighting.TabIndex = 3
			Me.chkFrameLighting.Text = "Frame Exposure"
			Me.chkFrameLighting.TextAlign = ContentAlignment.MiddleCenter
			Me.chkFrameLighting.UseVisualStyleBackColor = False
			Me.chkFrameLighting.Visible = False
			Me.cmdSensorCheck.BackColor = SystemColors.Control
			Me.cmdSensorCheck.Cursor = Cursors.[Default]
			Me.cmdSensorCheck.Font = New Font("Microsoft Sans Serif", 12F)
			Me.cmdSensorCheck.ForeColor = SystemColors.ControlText
			Me.cmdSensorCheck.Location = New Point(593, 335)
			Me.cmdSensorCheck.Name = "cmdSensorCheck"
			Me.cmdSensorCheck.RightToLeft = RightToLeft.No
			Me.cmdSensorCheck.Size = New Size(185, 57)
			Me.cmdSensorCheck.TabIndex = 2
			Me.cmdSensorCheck.Text = "Check Sensors"
			Me.cmdSensorCheck.UseVisualStyleBackColor = False
			Me.chkVakuumPumpe.Appearance = Appearance.Button
			Me.chkVakuumPumpe.BackColor = SystemColors.Control
			Me.chkVakuumPumpe.Cursor = Cursors.[Default]
			Me.chkVakuumPumpe.Enabled = False
			Me.chkVakuumPumpe.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.chkVakuumPumpe.ForeColor = SystemColors.ControlText
			Me.chkVakuumPumpe.Location = New Point(593, 32)
			Me.chkVakuumPumpe.Name = "chkVakuumPumpe"
			Me.chkVakuumPumpe.RightToLeft = RightToLeft.No
			Me.chkVakuumPumpe.Size = New Size(185, 57)
			Me.chkVakuumPumpe.TabIndex = 0
			Me.chkVakuumPumpe.Text = "Vacuum Pump"
			Me.chkVakuumPumpe.TextAlign = ContentAlignment.MiddleCenter
			Me.chkVakuumPumpe.UseVisualStyleBackColor = False
			Me.Label11.BackColor = SystemColors.Control
			Me.Label11.Cursor = Cursors.[Default]
			Me.Label11.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label11.ForeColor = SystemColors.ControlText
			Me.Label11.Location = New Point(827, 484)
			Me.Label11.Name = "Label11"
			Me.Label11.RightToLeft = RightToLeft.No
			Me.Label11.Size = New Size(145, 21)
			Me.Label11.TabIndex = 19
			Me.Label11.Text = "Vacuum Sensor"
			Me.Label11.Visible = False
			Me.cmdExit.BackColor = Color.FromArgb(255, 192, 192)
			Me.cmdExit.Cursor = Cursors.[Default]
			Me.cmdExit.DialogResult = DialogResult.Cancel
			Me.cmdExit.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdExit.ForeColor = Color.Black
			Me.cmdExit.Location = New Point(344, 429)
			Me.cmdExit.Name = "cmdExit"
			Me.cmdExit.RightToLeft = RightToLeft.No
			Me.cmdExit.Size = New Size(217, 65)
			Me.cmdExit.TabIndex = 63
			Me.cmdExit.Text = "Exit"
			Me.cmdExit.UseVisualStyleBackColor = False
			Me.cmdLogon.BackColor = Color.FromArgb(192, 255, 192)
			Me.cmdLogon.Cursor = Cursors.[Default]
			Me.cmdLogon.Font = New Font("Microsoft Sans Serif", 14.25F, FontStyle.Bold, GraphicsUnit.Point, 0)
			Me.cmdLogon.ForeColor = Color.Black
			Me.cmdLogon.Location = New Point(38, 429)
			Me.cmdLogon.Name = "cmdLogon"
			Me.cmdLogon.RightToLeft = RightToLeft.No
			Me.cmdLogon.Size = New Size(217, 65)
			Me.cmdLogon.TabIndex = 65
			Me.cmdLogon.Text = "Logon"
			Me.cmdLogon.UseVisualStyleBackColor = False
			Me.butExitDemo.BackColor = SystemColors.Control
			Me.butExitDemo.Cursor = Cursors.[Default]
			Me.butExitDemo.Enabled = False
			Me.butExitDemo.Font = New Font("Microsoft Sans Serif", 12F)
			Me.butExitDemo.ForeColor = SystemColors.ControlText
			Me.butExitDemo.Location = New Point(707, 324)
			Me.butExitDemo.Name = "butExitDemo"
			Me.butExitDemo.RightToLeft = RightToLeft.No
			Me.butExitDemo.Size = New Size(185, 57)
			Me.butExitDemo.TabIndex = 67
			Me.butExitDemo.Text = "Exit Demo Mode"
			Me.butExitDemo.UseVisualStyleBackColor = False
			Me.butExitDemo.Visible = False
			Me.butReset.BackColor = SystemColors.Control
			Me.butReset.Cursor = Cursors.[Default]
			Me.butReset.Font = New Font("Microsoft Sans Serif", 12F)
			Me.butReset.ForeColor = SystemColors.ControlText
			Me.butReset.Location = New Point(808, 261)
			Me.butReset.Name = "butReset"
			Me.butReset.RightToLeft = RightToLeft.No
			Me.butReset.Size = New Size(185, 57)
			Me.butReset.TabIndex = 68
			Me.butReset.Text = "HW Reset"
			Me.butReset.UseVisualStyleBackColor = False
			Me.butReset.Visible = False
			Me.Button1.Location = New Point(792, 458)
			Me.Button1.Name = "Button1"
			Me.Button1.Size = New Size(75, 23)
			Me.Button1.TabIndex = 69
			Me.Button1.Text = "Button1"
			Me.Button1.UseVisualStyleBackColor = True
			Me.Button1.Visible = False
			Me.Label10.BackColor = Color.Transparent
			Me.Label10.Cursor = Cursors.[Default]
			Me.Label10.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label10.ForeColor = SystemColors.ControlText
			Me.Label10.Location = New Point(34, 196)
			Me.Label10.Name = "Label10"
			Me.Label10.RightToLeft = RightToLeft.No
			Me.Label10.Size = New Size(120, 41)
			Me.Label10.TabIndex = 7
			Me.Label10.Text = "Speed"
			Me.Label10.TextAlign = ContentAlignment.MiddleLeft
			Me.Label2.BackColor = SystemColors.Control
			Me.Label2.Cursor = Cursors.[Default]
			Me.Label2.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label2.ForeColor = SystemColors.ControlText
			Me.Label2.Location = New Point(34, 283)
			Me.Label2.Name = "Label2"
			Me.Label2.RightToLeft = RightToLeft.No
			Me.Label2.Size = New Size(118, 17)
			Me.Label2.TabIndex = 10
			Me.Label2.Text = "Distance"
			Me._Label1_0.BackColor = SystemColors.Control
			Me._Label1_0.Cursor = Cursors.[Default]
			Me._Label1_0.Font = New Font("Microsoft Sans Serif", 8.25F)
			Me._Label1_0.ForeColor = SystemColors.ControlText
			Me._Label1_0.Location = New Point(250, 285)
			Me._Label1_0.Name = "_Label1_0"
			Me._Label1_0.RightToLeft = RightToLeft.No
			Me._Label1_0.Size = New Size(29, 13)
			Me._Label1_0.TabIndex = 48
			Me._Label1_0.Text = "mm"
			Me.Label8.BackColor = SystemColors.Control
			Me.Label8.Cursor = Cursors.[Default]
			Me.Label8.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label8.ForeColor = SystemColors.ControlText
			Me.Label8.Location = New Point(34, 313)
			Me.Label8.Name = "Label8"
			Me.Label8.RightToLeft = RightToLeft.No
			Me.Label8.Size = New Size(138, 19)
			Me.Label8.TabIndex = 52
			Me.Label8.Text = "Steps per mm"
			Me._Label1_2.BackColor = Color.Transparent
			Me._Label1_2.Cursor = Cursors.[Default]
			Me._Label1_2.ForeColor = SystemColors.ControlText
			Me._Label1_2.Location = New Point(250, 219)
			Me._Label1_2.Name = "_Label1_2"
			Me._Label1_2.RightToLeft = RightToLeft.No
			Me._Label1_2.Size = New Size(29, 13)
			Me._Label1_2.TabIndex = 59
			Me._Label1_2.Text = "Hz"
			Me._txtSpeed_0.AcceptsReturn = True
			Me._txtSpeed_0.BackColor = SystemColors.Window
			Me._txtSpeed_0.Cursor = Cursors.IBeam
			Me._txtSpeed_0.Enabled = False
			Me._txtSpeed_0.ForeColor = SystemColors.WindowText
			Me._txtSpeed_0.Location = New Point(178, 196)
			Me._txtSpeed_0.MaxLength = 0
			Me._txtSpeed_0.Name = "_txtSpeed_0"
			Me._txtSpeed_0.RightToLeft = RightToLeft.No
			Me._txtSpeed_0.Size = New Size(65, 20)
			Me._txtSpeed_0.TabIndex = 6
			Me._txtSpeed_0.Text = "1500"
			Me._txtSpeed_0.TextAlign = HorizontalAlignment.Right
			Me.txtSchritte.AcceptsReturn = True
			Me.txtSchritte.BackColor = SystemColors.Window
			Me.txtSchritte.Cursor = Cursors.IBeam
			Me.txtSchritte.Enabled = False
			Me.txtSchritte.ForeColor = SystemColors.WindowText
			Me.txtSchritte.Location = New Point(178, 281)
			Me.txtSchritte.MaxLength = 0
			Me.txtSchritte.Name = "txtSchritte"
			Me.txtSchritte.RightToLeft = RightToLeft.No
			Me.txtSchritte.Size = New Size(65, 20)
			Me.txtSchritte.TabIndex = 9
			Me.txtSchritte.Text = "0"
			Me.txtSchritte.TextAlign = HorizontalAlignment.Right
			Me.optAchtel.BackColor = SystemColors.Control
			Me.optAchtel.Checked = True
			Me.optAchtel.Cursor = Cursors.[Default]
			Me.optAchtel.ForeColor = SystemColors.ControlText
			Me.optAchtel.Location = New Point(103, 48)
			Me.optAchtel.Name = "optAchtel"
			Me.optAchtel.RightToLeft = RightToLeft.No
			Me.optAchtel.Size = New Size(57, 17)
			Me.optAchtel.TabIndex = 44
			Me.optAchtel.TabStop = True
			Me.optAchtel.Text = "1/8"
			Me.optAchtel.UseVisualStyleBackColor = False
			Me.optViertel.BackColor = SystemColors.Control
			Me.optViertel.Cursor = Cursors.[Default]
			Me.optViertel.ForeColor = SystemColors.ControlText
			Me.optViertel.Location = New Point(7, 48)
			Me.optViertel.Name = "optViertel"
			Me.optViertel.RightToLeft = RightToLeft.No
			Me.optViertel.Size = New Size(73, 17)
			Me.optViertel.TabIndex = 45
			Me.optViertel.TabStop = True
			Me.optViertel.Text = "1/4"
			Me.optViertel.UseVisualStyleBackColor = False
			Me.optHalb.BackColor = SystemColors.Control
			Me.optHalb.Cursor = Cursors.[Default]
			Me.optHalb.ForeColor = SystemColors.ControlText
			Me.optHalb.Location = New Point(103, 24)
			Me.optHalb.Name = "optHalb"
			Me.optHalb.RightToLeft = RightToLeft.No
			Me.optHalb.Size = New Size(57, 17)
			Me.optHalb.TabIndex = 46
			Me.optHalb.TabStop = True
			Me.optHalb.Text = "1/2"
			Me.optHalb.UseVisualStyleBackColor = False
			Me.optEintel.BackColor = SystemColors.Control
			Me.optEintel.Cursor = Cursors.[Default]
			Me.optEintel.ForeColor = SystemColors.ControlText
			Me.optEintel.Location = New Point(7, 25)
			Me.optEintel.Name = "optEintel"
			Me.optEintel.RightToLeft = RightToLeft.No
			Me.optEintel.Size = New Size(73, 17)
			Me.optEintel.TabIndex = 47
			Me.optEintel.TabStop = True
			Me.optEintel.Text = "1/1"
			Me.optEintel.UseVisualStyleBackColor = False
			Me.Frame3.BackColor = SystemColors.Control
			Me.Frame3.Controls.Add(Me.optEintel)
			Me.Frame3.Controls.Add(Me.optHalb)
			Me.Frame3.Controls.Add(Me.optViertel)
			Me.Frame3.Controls.Add(Me.optAchtel)
			Me.Frame3.Enabled = False
			Me.Frame3.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Frame3.ForeColor = SystemColors.ControlText
			Me.Frame3.Location = New Point(38, 99)
			Me.Frame3.Name = "Frame3"
			Me.Frame3.Padding = New Padding(0)
			Me.Frame3.Size = New Size(185, 73)
			Me.Frame3.TabIndex = 43
			Me.Frame3.TabStop = False
			Me.Frame3.Text = "Resolution"
			Me.txtSchrittePromm.AcceptsReturn = True
			Me.txtSchrittePromm.BackColor = SystemColors.Window
			Me.txtSchrittePromm.Cursor = Cursors.IBeam
			Me.txtSchrittePromm.Enabled = False
			Me.txtSchrittePromm.ForeColor = SystemColors.WindowText
			Me.txtSchrittePromm.Location = New Point(178, 312)
			Me.txtSchrittePromm.MaxLength = 0
			Me.txtSchrittePromm.Name = "txtSchrittePromm"
			Me.txtSchrittePromm.RightToLeft = RightToLeft.No
			Me.txtSchrittePromm.Size = New Size(65, 20)
			Me.txtSchrittePromm.TabIndex = 50
			Me.txtSchrittePromm.Text = "0"
			Me.txtSchrittePromm.TextAlign = HorizontalAlignment.Right
			Me._txtSpeed_1.AcceptsReturn = True
			Me._txtSpeed_1.BackColor = Color.FromArgb(224, 224, 224)
			Me._txtSpeed_1.BorderStyle = BorderStyle.FixedSingle
			Me._txtSpeed_1.Cursor = Cursors.IBeam
			Me._txtSpeed_1.Enabled = False
			Me._txtSpeed_1.ForeColor = SystemColors.WindowText
			Me._txtSpeed_1.Location = New Point(178, 217)
			Me._txtSpeed_1.MaxLength = 0
			Me._txtSpeed_1.Name = "_txtSpeed_1"
			Me._txtSpeed_1.[ReadOnly] = True
			Me._txtSpeed_1.RightToLeft = RightToLeft.No
			Me._txtSpeed_1.Size = New Size(65, 20)
			Me._txtSpeed_1.TabIndex = 57
			Me._txtSpeed_1.Text = "1500"
			Me._txtSpeed_1.TextAlign = HorizontalAlignment.Right
			Me.chkFilmMotor.Appearance = Appearance.Button
			Me.chkFilmMotor.BackColor = SystemColors.Control
			Me.chkFilmMotor.Cursor = Cursors.[Default]
			Me.chkFilmMotor.Enabled = False
			Me.chkFilmMotor.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkFilmMotor.ForeColor = SystemColors.ControlText
			Me.chkFilmMotor.Location = New Point(38, 32)
			Me.chkFilmMotor.Name = "chkFilmMotor"
			Me.chkFilmMotor.RightToLeft = RightToLeft.No
			Me.chkFilmMotor.Size = New Size(185, 57)
			Me.chkFilmMotor.TabIndex = 64
			Me.chkFilmMotor.Text = "Start Film Motor"
			Me.chkFilmMotor.TextAlign = ContentAlignment.MiddleCenter
			Me.chkFilmMotor.UseVisualStyleBackColor = False
			Me.Label3.BackColor = Color.Transparent
			Me.Label3.Cursor = Cursors.[Default]
			Me.Label3.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label3.ForeColor = SystemColors.ControlText
			Me.Label3.Location = New Point(331, 196)
			Me.Label3.Name = "Label3"
			Me.Label3.RightToLeft = RightToLeft.No
			Me.Label3.Size = New Size(121, 41)
			Me.Label3.TabIndex = 12
			Me.Label3.Text = "Speed"
			Me.Label3.TextAlign = ContentAlignment.MiddleLeft
			Me.Label4.BackColor = SystemColors.Control
			Me.Label4.Cursor = Cursors.[Default]
			Me.Label4.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label4.ForeColor = SystemColors.ControlText
			Me.Label4.Location = New Point(331, 259)
			Me.Label4.Name = "Label4"
			Me.Label4.RightToLeft = RightToLeft.No
			Me.Label4.Size = New Size(108, 18)
			Me.Label4.TabIndex = 14
			Me.Label4.Text = "Steps"
			Me.Label5.BackColor = SystemColors.Control
			Me.Label5.Cursor = Cursors.[Default]
			Me.Label5.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label5.ForeColor = SystemColors.ControlText
			Me.Label5.Location = New Point(331, 291)
			Me.Label5.Name = "Label5"
			Me.Label5.RightToLeft = RightToLeft.No
			Me.Label5.Size = New Size(108, 17)
			Me.Label5.TabIndex = 16
			Me.Label5.Text = "Time"
			Me.Label6.BackColor = SystemColors.Control
			Me.Label6.Cursor = Cursors.[Default]
			Me.Label6.Font = New Font("Microsoft Sans Serif", 8.25F)
			Me.Label6.ForeColor = SystemColors.ControlText
			Me.Label6.Location = New Point(532, 291)
			Me.Label6.Name = "Label6"
			Me.Label6.RightToLeft = RightToLeft.No
			Me.Label6.Size = New Size(26, 17)
			Me.Label6.TabIndex = 17
			Me.Label6.Text = "ms"
			Me._Label1_1.BackColor = Color.Transparent
			Me._Label1_1.Cursor = Cursors.[Default]
			Me._Label1_1.ForeColor = SystemColors.ControlText
			Me._Label1_1.Location = New Point(532, 219)
			Me._Label1_1.Name = "_Label1_1"
			Me._Label1_1.RightToLeft = RightToLeft.No
			Me._Label1_1.Size = New Size(26, 13)
			Me._Label1_1.TabIndex = 58
			Me._Label1_1.Text = "Hz"
			Me.chkBlendenMotor.Appearance = Appearance.Button
			Me.chkBlendenMotor.BackColor = SystemColors.Control
			Me.chkBlendenMotor.Cursor = Cursors.[Default]
			Me.chkBlendenMotor.Enabled = False
			Me.chkBlendenMotor.Font = New Font("Microsoft Sans Serif", 12F)
			Me.chkBlendenMotor.ForeColor = SystemColors.ControlText
			Me.chkBlendenMotor.Location = New Point(349, 32)
			Me.chkBlendenMotor.Name = "chkBlendenMotor"
			Me.chkBlendenMotor.RightToLeft = RightToLeft.No
			Me.chkBlendenMotor.Size = New Size(185, 57)
			Me.chkBlendenMotor.TabIndex = 1
			Me.chkBlendenMotor.Text = "Start Shutter"
			Me.chkBlendenMotor.TextAlign = ContentAlignment.MiddleCenter
			Me.chkBlendenMotor.UseVisualStyleBackColor = False
			Me.cmdNull.Appearance = Appearance.Button
			Me.cmdNull.BackColor = SystemColors.Control
			Me.cmdNull.Cursor = Cursors.[Default]
			Me.cmdNull.Font = New Font("Microsoft Sans Serif", 12F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.cmdNull.ForeColor = SystemColors.ControlText
			Me.cmdNull.Location = New Point(349, 335)
			Me.cmdNull.Name = "cmdNull"
			Me.cmdNull.RightToLeft = RightToLeft.No
			Me.cmdNull.Size = New Size(185, 57)
			Me.cmdNull.TabIndex = 8
			Me.cmdNull.Text = "Calibrate Shutter"
			Me.cmdNull.TextAlign = ContentAlignment.MiddleCenter
			Me.cmdNull.UseVisualStyleBackColor = False
			Me._txtVerschlussSpeed_0.AcceptsReturn = True
			Me._txtVerschlussSpeed_0.BackColor = SystemColors.Window
			Me._txtVerschlussSpeed_0.Cursor = Cursors.IBeam
			Me._txtVerschlussSpeed_0.Enabled = False
			Me._txtVerschlussSpeed_0.ForeColor = SystemColors.WindowText
			Me._txtVerschlussSpeed_0.Location = New Point(462, 196)
			Me._txtVerschlussSpeed_0.MaxLength = 0
			Me._txtVerschlussSpeed_0.Name = "_txtVerschlussSpeed_0"
			Me._txtVerschlussSpeed_0.RightToLeft = RightToLeft.No
			Me._txtVerschlussSpeed_0.Size = New Size(65, 20)
			Me._txtVerschlussSpeed_0.TabIndex = 11
			Me._txtVerschlussSpeed_0.Text = "1463"
			Me._txtVerschlussSpeed_0.TextAlign = HorizontalAlignment.Right
			Me.txtVerschlussSchritte.AcceptsReturn = True
			Me.txtVerschlussSchritte.BackColor = SystemColors.Window
			Me.txtVerschlussSchritte.Cursor = Cursors.IBeam
			Me.txtVerschlussSchritte.Enabled = False
			Me.txtVerschlussSchritte.ForeColor = SystemColors.WindowText
			Me.txtVerschlussSchritte.Location = New Point(462, 258)
			Me.txtVerschlussSchritte.MaxLength = 0
			Me.txtVerschlussSchritte.Name = "txtVerschlussSchritte"
			Me.txtVerschlussSchritte.RightToLeft = RightToLeft.No
			Me.txtVerschlussSchritte.Size = New Size(65, 20)
			Me.txtVerschlussSchritte.TabIndex = 13
			Me.txtVerschlussSchritte.Text = "0"
			Me.txtVerschlussSchritte.TextAlign = HorizontalAlignment.Right
			Me.txtVerschlussZeit.AcceptsReturn = True
			Me.txtVerschlussZeit.BackColor = SystemColors.Window
			Me.txtVerschlussZeit.Cursor = Cursors.IBeam
			Me.txtVerschlussZeit.Enabled = False
			Me.txtVerschlussZeit.ForeColor = SystemColors.WindowText
			Me.txtVerschlussZeit.Location = New Point(462, 289)
			Me.txtVerschlussZeit.MaxLength = 0
			Me.txtVerschlussZeit.Name = "txtVerschlussZeit"
			Me.txtVerschlussZeit.RightToLeft = RightToLeft.No
			Me.txtVerschlussZeit.Size = New Size(65, 20)
			Me.txtVerschlussZeit.TabIndex = 15
			Me.txtVerschlussZeit.Text = "0"
			Me.txtVerschlussZeit.TextAlign = HorizontalAlignment.Right
			Me.optVEintel.BackColor = SystemColors.Control
			Me.optVEintel.Cursor = Cursors.[Default]
			Me.optVEintel.ForeColor = SystemColors.ControlText
			Me.optVEintel.Location = New Point(16, 24)
			Me.optVEintel.Name = "optVEintel"
			Me.optVEintel.RightToLeft = RightToLeft.No
			Me.optVEintel.Size = New Size(73, 17)
			Me.optVEintel.TabIndex = 39
			Me.optVEintel.TabStop = True
			Me.optVEintel.Text = "1/1"
			Me.optVEintel.UseVisualStyleBackColor = False
			Me.optVHalb.BackColor = SystemColors.Control
			Me.optVHalb.Cursor = Cursors.[Default]
			Me.optVHalb.ForeColor = SystemColors.ControlText
			Me.optVHalb.Location = New Point(112, 24)
			Me.optVHalb.Name = "optVHalb"
			Me.optVHalb.RightToLeft = RightToLeft.No
			Me.optVHalb.Size = New Size(57, 17)
			Me.optVHalb.TabIndex = 40
			Me.optVHalb.TabStop = True
			Me.optVHalb.Text = "1/2"
			Me.optVHalb.UseVisualStyleBackColor = False
			Me.optVViertel.BackColor = SystemColors.Control
			Me.optVViertel.Cursor = Cursors.[Default]
			Me.optVViertel.ForeColor = SystemColors.ControlText
			Me.optVViertel.Location = New Point(16, 48)
			Me.optVViertel.Name = "optVViertel"
			Me.optVViertel.RightToLeft = RightToLeft.No
			Me.optVViertel.Size = New Size(73, 17)
			Me.optVViertel.TabIndex = 41
			Me.optVViertel.TabStop = True
			Me.optVViertel.Text = "1/4"
			Me.optVViertel.UseVisualStyleBackColor = False
			Me.optVAchtel.BackColor = SystemColors.Control
			Me.optVAchtel.Checked = True
			Me.optVAchtel.Cursor = Cursors.[Default]
			Me.optVAchtel.ForeColor = SystemColors.ControlText
			Me.optVAchtel.Location = New Point(112, 48)
			Me.optVAchtel.Name = "optVAchtel"
			Me.optVAchtel.RightToLeft = RightToLeft.No
			Me.optVAchtel.Size = New Size(57, 17)
			Me.optVAchtel.TabIndex = 42
			Me.optVAchtel.TabStop = True
			Me.optVAchtel.Text = "1/8"
			Me.optVAchtel.UseVisualStyleBackColor = False
			Me.Frame2.BackColor = SystemColors.Control
			Me.Frame2.Controls.Add(Me.optVAchtel)
			Me.Frame2.Controls.Add(Me.optVViertel)
			Me.Frame2.Controls.Add(Me.optVHalb)
			Me.Frame2.Controls.Add(Me.optVEintel)
			Me.Frame2.Enabled = False
			Me.Frame2.Font = New Font("Microsoft Sans Serif", 9.75F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Frame2.ForeColor = SystemColors.ControlText
			Me.Frame2.Location = New Point(349, 98)
			Me.Frame2.Name = "Frame2"
			Me.Frame2.Padding = New Padding(0)
			Me.Frame2.RightToLeft = RightToLeft.No
			Me.Frame2.Size = New Size(185, 74)
			Me.Frame2.TabIndex = 38
			Me.Frame2.TabStop = False
			Me.Frame2.Text = "Resolution"
			Me._txtVerschlussSpeed_1.AcceptsReturn = True
			Me._txtVerschlussSpeed_1.BackColor = Color.FromArgb(224, 224, 224)
			Me._txtVerschlussSpeed_1.BorderStyle = BorderStyle.FixedSingle
			Me._txtVerschlussSpeed_1.Cursor = Cursors.IBeam
			Me._txtVerschlussSpeed_1.Enabled = False
			Me._txtVerschlussSpeed_1.ForeColor = SystemColors.WindowText
			Me._txtVerschlussSpeed_1.Location = New Point(462, 217)
			Me._txtVerschlussSpeed_1.MaxLength = 0
			Me._txtVerschlussSpeed_1.Name = "_txtVerschlussSpeed_1"
			Me._txtVerschlussSpeed_1.[ReadOnly] = True
			Me._txtVerschlussSpeed_1.RightToLeft = RightToLeft.No
			Me._txtVerschlussSpeed_1.Size = New Size(65, 20)
			Me._txtVerschlussSpeed_1.TabIndex = 56
			Me._txtVerschlussSpeed_1.Text = "1463"
			Me._txtVerschlussSpeed_1.TextAlign = HorizontalAlignment.Right
			Me.PictureBox1.BackColor = Color.Transparent
			Me.PictureBox1.BorderStyle = BorderStyle.FixedSingle
			Me.PictureBox1.Location = New Point(12, 12)
			Me.PictureBox1.Name = "PictureBox1"
			Me.PictureBox1.Size = New Size(272, 399)
			Me.PictureBox1.TabIndex = 72
			Me.PictureBox1.TabStop = False
			Me.PictureBox2.BackColor = Color.Transparent
			Me.PictureBox2.BorderStyle = BorderStyle.FixedSingle
			Me.PictureBox2.Location = New Point(294, 12)
			Me.PictureBox2.Name = "PictureBox2"
			Me.PictureBox2.Size = New Size(267, 399)
			Me.PictureBox2.TabIndex = 73
			Me.PictureBox2.TabStop = False
			Me.PictureBox3.BackColor = Color.Transparent
			Me.PictureBox3.BorderStyle = BorderStyle.FixedSingle
			Me.PictureBox3.Location = New Point(572, 12)
			Me.PictureBox3.Name = "PictureBox3"
			Me.PictureBox3.Size = New Size(230, 399)
			Me.PictureBox3.TabIndex = 74
			Me.PictureBox3.TabStop = False
			MyBase.AutoScaleDimensions = New SizeF(6F, 13F)
			MyBase.AutoScaleMode = AutoScaleMode.Font
			Me.BackColor = SystemColors.Control
			MyBase.ClientSize = New Size(816, 504)
			MyBase.Controls.Add(Me.Label3)
			MyBase.Controls.Add(Me.Frame2)
			MyBase.Controls.Add(Me.Label4)
			MyBase.Controls.Add(Me.chkBlendenMotor)
			MyBase.Controls.Add(Me.Label5)
			MyBase.Controls.Add(Me.Label10)
			MyBase.Controls.Add(Me.Label6)
			MyBase.Controls.Add(Me.Label2)
			MyBase.Controls.Add(Me._Label1_1)
			MyBase.Controls.Add(Me.Frame3)
			MyBase.Controls.Add(Me._txtVerschlussSpeed_0)
			MyBase.Controls.Add(Me._Label1_0)
			MyBase.Controls.Add(Me.txtVerschlussSchritte)
			MyBase.Controls.Add(Me.chkFilmMotor)
			MyBase.Controls.Add(Me._txtVerschlussSpeed_1)
			MyBase.Controls.Add(Me.Label8)
			MyBase.Controls.Add(Me.txtVerschlussZeit)
			MyBase.Controls.Add(Me.cmdNull)
			MyBase.Controls.Add(Me._txtSpeed_1)
			MyBase.Controls.Add(Me._Label1_2)
			MyBase.Controls.Add(Me._txtSpeed_0)
			MyBase.Controls.Add(Me.Button1)
			MyBase.Controls.Add(Me.txtSchritte)
			MyBase.Controls.Add(Me.butReset)
			MyBase.Controls.Add(Me.txtSchrittePromm)
			MyBase.Controls.Add(Me.butExitDemo)
			MyBase.Controls.Add(Me.cmdLogon)
			MyBase.Controls.Add(Me.cmdExit)
			MyBase.Controls.Add(Me.chkLamp)
			MyBase.Controls.Add(Me.chkButler)
			MyBase.Controls.Add(Me.Test)
			MyBase.Controls.Add(Me.cmdTestFilming)
			MyBase.Controls.Add(Me.chkventil)
			MyBase.Controls.Add(Me.chkFrameLighting)
			MyBase.Controls.Add(Me.cmdSensorCheck)
			MyBase.Controls.Add(Me.chkVakuumPumpe)
			MyBase.Controls.Add(Me.Label11)
			MyBase.Controls.Add(Me.PictureBox1)
			MyBase.Controls.Add(Me.PictureBox2)
			MyBase.Controls.Add(Me.PictureBox3)
			Me.Cursor = Cursors.[Default]
			MyBase.KeyPreview = True
			MyBase.Location = New Point(4, 23)
			MyBase.Name = "frmService"
			Me.RightToLeft = RightToLeft.No
			MyBase.StartPosition = FormStartPosition.CenterScreen
			Me.Text = "Service Functions "
			Me.Frame3.ResumeLayout(False)
			Me.Frame2.ResumeLayout(False)
			CType(Me.PictureBox1, ISupportInitialize).EndInit()
			CType(Me.PictureBox2, ISupportInitialize).EndInit()
			CType(Me.PictureBox3, ISupportInitialize).EndInit()
			MyBase.ResumeLayout(False)
			MyBase.PerformLayout()
		End Sub

		' Token: 0x17000290 RID: 656
		' (get) Token: 0x06000B09 RID: 2825 RVA: 0x0005B950 File Offset: 0x00059B50
		' (set) Token: 0x06000B0A RID: 2826 RVA: 0x0005B958 File Offset: 0x00059B58
		Public Overridable Property cmdExit As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdExit
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdCancel_Click
				Dim cmdExit As Button = Me._cmdExit
				If cmdExit IsNot Nothing Then
					RemoveHandler cmdExit.Click, value2
				End If
				Me._cmdExit = value
				cmdExit = Me._cmdExit
				If cmdExit IsNot Nothing Then
					AddHandler cmdExit.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000291 RID: 657
		' (get) Token: 0x06000B0B RID: 2827 RVA: 0x0005B99B File Offset: 0x00059B9B
		' (set) Token: 0x06000B0C RID: 2828 RVA: 0x0005B9A4 File Offset: 0x00059BA4
		Public Overridable Property cmdLogon As Button
			<CompilerGenerated()>
			Get
				Return Me._cmdLogon
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.cmdLogon_Click
				Dim cmdLogon As Button = Me._cmdLogon
				If cmdLogon IsNot Nothing Then
					RemoveHandler cmdLogon.Click, value2
				End If
				Me._cmdLogon = value
				cmdLogon = Me._cmdLogon
				If cmdLogon IsNot Nothing Then
					AddHandler cmdLogon.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000292 RID: 658
		' (get) Token: 0x06000B0D RID: 2829 RVA: 0x0005B9E7 File Offset: 0x00059BE7
		' (set) Token: 0x06000B0E RID: 2830 RVA: 0x0005B9F0 File Offset: 0x00059BF0
		Public Overridable Property butExitDemo As Button
			<CompilerGenerated()>
			Get
				Return Me._butExitDemo
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.butExitDemo_Click
				Dim butExitDemo As Button = Me._butExitDemo
				If butExitDemo IsNot Nothing Then
					RemoveHandler butExitDemo.Click, value2
				End If
				Me._butExitDemo = value
				butExitDemo = Me._butExitDemo
				If butExitDemo IsNot Nothing Then
					AddHandler butExitDemo.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000293 RID: 659
		' (get) Token: 0x06000B0F RID: 2831 RVA: 0x0005BA33 File Offset: 0x00059C33
		' (set) Token: 0x06000B10 RID: 2832 RVA: 0x0005BA3C File Offset: 0x00059C3C
		Public Overridable Property butReset As Button
			<CompilerGenerated()>
			Get
				Return Me._butReset
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.butReset_Click
				Dim butReset As Button = Me._butReset
				If butReset IsNot Nothing Then
					RemoveHandler butReset.Click, value2
				End If
				Me._butReset = value
				butReset = Me._butReset
				If butReset IsNot Nothing Then
					AddHandler butReset.Click, value2
				End If
			End Set
		End Property

		' Token: 0x17000294 RID: 660
		' (get) Token: 0x06000B11 RID: 2833 RVA: 0x0005BA7F File Offset: 0x00059C7F
		' (set) Token: 0x06000B12 RID: 2834 RVA: 0x0005BA88 File Offset: 0x00059C88
		Friend Overridable Property Button1 As Button
			<CompilerGenerated()>
			Get
				Return Me._Button1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Button)
				Dim value2 As EventHandler = AddressOf Me.Button1_Click_1
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

		' Token: 0x17000295 RID: 661
		' (get) Token: 0x06000B13 RID: 2835 RVA: 0x0005BACB File Offset: 0x00059CCB
		' (set) Token: 0x06000B14 RID: 2836 RVA: 0x0005BAD3 File Offset: 0x00059CD3
		Public Overridable Property Label10 As Label

		' Token: 0x17000296 RID: 662
		' (get) Token: 0x06000B15 RID: 2837 RVA: 0x0005BADC File Offset: 0x00059CDC
		' (set) Token: 0x06000B16 RID: 2838 RVA: 0x0005BAE4 File Offset: 0x00059CE4
		Public Overridable Property Label2 As Label

		' Token: 0x17000297 RID: 663
		' (get) Token: 0x06000B17 RID: 2839 RVA: 0x0005BAED File Offset: 0x00059CED
		' (set) Token: 0x06000B18 RID: 2840 RVA: 0x0005BAF5 File Offset: 0x00059CF5
		Public Overridable Property _Label1_0 As Label

		' Token: 0x17000298 RID: 664
		' (get) Token: 0x06000B19 RID: 2841 RVA: 0x0005BAFE File Offset: 0x00059CFE
		' (set) Token: 0x06000B1A RID: 2842 RVA: 0x0005BB06 File Offset: 0x00059D06
		Public Overridable Property Label8 As Label

		' Token: 0x17000299 RID: 665
		' (get) Token: 0x06000B1B RID: 2843 RVA: 0x0005BB0F File Offset: 0x00059D0F
		' (set) Token: 0x06000B1C RID: 2844 RVA: 0x0005BB17 File Offset: 0x00059D17
		Public Overridable Property _Label1_2 As Label

		' Token: 0x1700029A RID: 666
		' (get) Token: 0x06000B1D RID: 2845 RVA: 0x0005BB20 File Offset: 0x00059D20
		' (set) Token: 0x06000B1E RID: 2846 RVA: 0x0005BB28 File Offset: 0x00059D28
		Public Overridable Property _txtSpeed_0 As TextBox
			<CompilerGenerated()>
			Get
				Return Me.__txtSpeed_0
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtSpeed_TextChanged
				Dim _txtSpeed_ As TextBox = Me.__txtSpeed_0
				If _txtSpeed_ IsNot Nothing Then
					RemoveHandler _txtSpeed_.TextChanged, value2
				End If
				Me.__txtSpeed_0 = value
				_txtSpeed_ = Me.__txtSpeed_0
				If _txtSpeed_ IsNot Nothing Then
					AddHandler _txtSpeed_.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x1700029B RID: 667
		' (get) Token: 0x06000B1F RID: 2847 RVA: 0x0005BB6B File Offset: 0x00059D6B
		' (set) Token: 0x06000B20 RID: 2848 RVA: 0x0005BB73 File Offset: 0x00059D73
		Public Overridable Property txtSchritte As TextBox

		' Token: 0x1700029C RID: 668
		' (get) Token: 0x06000B21 RID: 2849 RVA: 0x0005BB7C File Offset: 0x00059D7C
		' (set) Token: 0x06000B22 RID: 2850 RVA: 0x0005BB84 File Offset: 0x00059D84
		Public Overridable Property optAchtel As RadioButton

		' Token: 0x1700029D RID: 669
		' (get) Token: 0x06000B23 RID: 2851 RVA: 0x0005BB8D File Offset: 0x00059D8D
		' (set) Token: 0x06000B24 RID: 2852 RVA: 0x0005BB95 File Offset: 0x00059D95
		Public Overridable Property optViertel As RadioButton

		' Token: 0x1700029E RID: 670
		' (get) Token: 0x06000B25 RID: 2853 RVA: 0x0005BB9E File Offset: 0x00059D9E
		' (set) Token: 0x06000B26 RID: 2854 RVA: 0x0005BBA6 File Offset: 0x00059DA6
		Public Overridable Property optHalb As RadioButton

		' Token: 0x1700029F RID: 671
		' (get) Token: 0x06000B27 RID: 2855 RVA: 0x0005BBAF File Offset: 0x00059DAF
		' (set) Token: 0x06000B28 RID: 2856 RVA: 0x0005BBB7 File Offset: 0x00059DB7
		Public Overridable Property optEintel As RadioButton

		' Token: 0x170002A0 RID: 672
		' (get) Token: 0x06000B29 RID: 2857 RVA: 0x0005BBC0 File Offset: 0x00059DC0
		' (set) Token: 0x06000B2A RID: 2858 RVA: 0x0005BBC8 File Offset: 0x00059DC8
		Public Overridable Property Frame3 As GroupBox
			<CompilerGenerated()>
			Get
				Return Me._Frame3
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As GroupBox)
				Dim value2 As EventHandler = AddressOf Me.Frame3_Enter
				Dim frame As GroupBox = Me._Frame3
				If frame IsNot Nothing Then
					RemoveHandler frame.Enter, value2
				End If
				Me._Frame3 = value
				frame = Me._Frame3
				If frame IsNot Nothing Then
					AddHandler frame.Enter, value2
				End If
			End Set
		End Property

		' Token: 0x170002A1 RID: 673
		' (get) Token: 0x06000B2B RID: 2859 RVA: 0x0005BC0B File Offset: 0x00059E0B
		' (set) Token: 0x06000B2C RID: 2860 RVA: 0x0005BC13 File Offset: 0x00059E13
		Public Overridable Property txtSchrittePromm As TextBox

		' Token: 0x170002A2 RID: 674
		' (get) Token: 0x06000B2D RID: 2861 RVA: 0x0005BC1C File Offset: 0x00059E1C
		' (set) Token: 0x06000B2E RID: 2862 RVA: 0x0005BC24 File Offset: 0x00059E24
		Public Overridable Property _txtSpeed_1 As TextBox

		' Token: 0x170002A3 RID: 675
		' (get) Token: 0x06000B2F RID: 2863 RVA: 0x0005BC2D File Offset: 0x00059E2D
		' (set) Token: 0x06000B30 RID: 2864 RVA: 0x0005BC38 File Offset: 0x00059E38
		Public Overridable Property chkFilmMotor As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkFilmMotor
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkFilmMotor_CheckedChanged
				Dim chkFilmMotor As CheckBox = Me._chkFilmMotor
				If chkFilmMotor IsNot Nothing Then
					RemoveHandler chkFilmMotor.CheckedChanged, value2
				End If
				Me._chkFilmMotor = value
				chkFilmMotor = Me._chkFilmMotor
				If chkFilmMotor IsNot Nothing Then
					AddHandler chkFilmMotor.CheckedChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170002A4 RID: 676
		' (get) Token: 0x06000B31 RID: 2865 RVA: 0x0005BC7B File Offset: 0x00059E7B
		' (set) Token: 0x06000B32 RID: 2866 RVA: 0x0005BC83 File Offset: 0x00059E83
		Public Overridable Property Label3 As Label

		' Token: 0x170002A5 RID: 677
		' (get) Token: 0x06000B33 RID: 2867 RVA: 0x0005BC8C File Offset: 0x00059E8C
		' (set) Token: 0x06000B34 RID: 2868 RVA: 0x0005BC94 File Offset: 0x00059E94
		Public Overridable Property Label4 As Label

		' Token: 0x170002A6 RID: 678
		' (get) Token: 0x06000B35 RID: 2869 RVA: 0x0005BC9D File Offset: 0x00059E9D
		' (set) Token: 0x06000B36 RID: 2870 RVA: 0x0005BCA5 File Offset: 0x00059EA5
		Public Overridable Property Label5 As Label

		' Token: 0x170002A7 RID: 679
		' (get) Token: 0x06000B37 RID: 2871 RVA: 0x0005BCAE File Offset: 0x00059EAE
		' (set) Token: 0x06000B38 RID: 2872 RVA: 0x0005BCB6 File Offset: 0x00059EB6
		Public Overridable Property Label6 As Label

		' Token: 0x170002A8 RID: 680
		' (get) Token: 0x06000B39 RID: 2873 RVA: 0x0005BCBF File Offset: 0x00059EBF
		' (set) Token: 0x06000B3A RID: 2874 RVA: 0x0005BCC7 File Offset: 0x00059EC7
		Public Overridable Property _Label1_1 As Label

		' Token: 0x170002A9 RID: 681
		' (get) Token: 0x06000B3B RID: 2875 RVA: 0x0005BCD0 File Offset: 0x00059ED0
		' (set) Token: 0x06000B3C RID: 2876 RVA: 0x0005BCD8 File Offset: 0x00059ED8
		Public Overridable Property chkBlendenMotor As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._chkBlendenMotor
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.chkBlendenMotor_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.chkBlendenMotor_CheckedChanged
				Dim chkBlendenMotor As CheckBox = Me._chkBlendenMotor
				If chkBlendenMotor IsNot Nothing Then
					RemoveHandler chkBlendenMotor.CheckStateChanged, value2
					RemoveHandler chkBlendenMotor.CheckedChanged, value3
				End If
				Me._chkBlendenMotor = value
				chkBlendenMotor = Me._chkBlendenMotor
				If chkBlendenMotor IsNot Nothing Then
					AddHandler chkBlendenMotor.CheckStateChanged, value2
					AddHandler chkBlendenMotor.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x170002AA RID: 682
		' (get) Token: 0x06000B3D RID: 2877 RVA: 0x0005BD36 File Offset: 0x00059F36
		' (set) Token: 0x06000B3E RID: 2878 RVA: 0x0005BD40 File Offset: 0x00059F40
		Public Overridable Property cmdNull As CheckBox
			<CompilerGenerated()>
			Get
				Return Me._cmdNull
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As CheckBox)
				Dim value2 As EventHandler = AddressOf Me.cmdNull_CheckStateChanged
				Dim value3 As EventHandler = AddressOf Me.cmdNull_CheckedChanged
				Dim cmdNull As CheckBox = Me._cmdNull
				If cmdNull IsNot Nothing Then
					RemoveHandler cmdNull.CheckStateChanged, value2
					RemoveHandler cmdNull.CheckedChanged, value3
				End If
				Me._cmdNull = value
				cmdNull = Me._cmdNull
				If cmdNull IsNot Nothing Then
					AddHandler cmdNull.CheckStateChanged, value2
					AddHandler cmdNull.CheckedChanged, value3
				End If
			End Set
		End Property

		' Token: 0x170002AB RID: 683
		' (get) Token: 0x06000B3F RID: 2879 RVA: 0x0005BD9E File Offset: 0x00059F9E
		' (set) Token: 0x06000B40 RID: 2880 RVA: 0x0005BDA8 File Offset: 0x00059FA8
		Public Overridable Property _txtVerschlussSpeed_0 As TextBox
			<CompilerGenerated()>
			Get
				Return Me.__txtVerschlussSpeed_0
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As TextBox)
				Dim value2 As EventHandler = AddressOf Me.txtVerschlussSpeed_TextChanged
				Dim _txtVerschlussSpeed_ As TextBox = Me.__txtVerschlussSpeed_0
				If _txtVerschlussSpeed_ IsNot Nothing Then
					RemoveHandler _txtVerschlussSpeed_.TextChanged, value2
				End If
				Me.__txtVerschlussSpeed_0 = value
				_txtVerschlussSpeed_ = Me.__txtVerschlussSpeed_0
				If _txtVerschlussSpeed_ IsNot Nothing Then
					AddHandler _txtVerschlussSpeed_.TextChanged, value2
				End If
			End Set
		End Property

		' Token: 0x170002AC RID: 684
		' (get) Token: 0x06000B41 RID: 2881 RVA: 0x0005BDEB File Offset: 0x00059FEB
		' (set) Token: 0x06000B42 RID: 2882 RVA: 0x0005BDF3 File Offset: 0x00059FF3
		Public Overridable Property txtVerschlussSchritte As TextBox

		' Token: 0x170002AD RID: 685
		' (get) Token: 0x06000B43 RID: 2883 RVA: 0x0005BDFC File Offset: 0x00059FFC
		' (set) Token: 0x06000B44 RID: 2884 RVA: 0x0005BE04 File Offset: 0x0005A004
		Public Overridable Property txtVerschlussZeit As TextBox

		' Token: 0x170002AE RID: 686
		' (get) Token: 0x06000B45 RID: 2885 RVA: 0x0005BE0D File Offset: 0x0005A00D
		' (set) Token: 0x06000B46 RID: 2886 RVA: 0x0005BE15 File Offset: 0x0005A015
		Public Overridable Property optVEintel As RadioButton

		' Token: 0x170002AF RID: 687
		' (get) Token: 0x06000B47 RID: 2887 RVA: 0x0005BE1E File Offset: 0x0005A01E
		' (set) Token: 0x06000B48 RID: 2888 RVA: 0x0005BE26 File Offset: 0x0005A026
		Public Overridable Property optVHalb As RadioButton

		' Token: 0x170002B0 RID: 688
		' (get) Token: 0x06000B49 RID: 2889 RVA: 0x0005BE2F File Offset: 0x0005A02F
		' (set) Token: 0x06000B4A RID: 2890 RVA: 0x0005BE37 File Offset: 0x0005A037
		Public Overridable Property optVViertel As RadioButton

		' Token: 0x170002B1 RID: 689
		' (get) Token: 0x06000B4B RID: 2891 RVA: 0x0005BE40 File Offset: 0x0005A040
		' (set) Token: 0x06000B4C RID: 2892 RVA: 0x0005BE48 File Offset: 0x0005A048
		Public Overridable Property optVAchtel As RadioButton

		' Token: 0x170002B2 RID: 690
		' (get) Token: 0x06000B4D RID: 2893 RVA: 0x0005BE51 File Offset: 0x0005A051
		' (set) Token: 0x06000B4E RID: 2894 RVA: 0x0005BE59 File Offset: 0x0005A059
		Public Overridable Property Frame2 As GroupBox

		' Token: 0x170002B3 RID: 691
		' (get) Token: 0x06000B4F RID: 2895 RVA: 0x0005BE62 File Offset: 0x0005A062
		' (set) Token: 0x06000B50 RID: 2896 RVA: 0x0005BE6A File Offset: 0x0005A06A
		Public Overridable Property _txtVerschlussSpeed_1 As TextBox

		' Token: 0x170002B4 RID: 692
		' (get) Token: 0x06000B51 RID: 2897 RVA: 0x0005BE73 File Offset: 0x0005A073
		' (set) Token: 0x06000B52 RID: 2898 RVA: 0x0005BE7B File Offset: 0x0005A07B
		Friend Overridable Property PictureBox1 As PictureBox

		' Token: 0x170002B5 RID: 693
		' (get) Token: 0x06000B53 RID: 2899 RVA: 0x0005BE84 File Offset: 0x0005A084
		' (set) Token: 0x06000B54 RID: 2900 RVA: 0x0005BE8C File Offset: 0x0005A08C
		Friend Overridable Property PictureBox2 As PictureBox

		' Token: 0x170002B6 RID: 694
		' (get) Token: 0x06000B55 RID: 2901 RVA: 0x0005BE95 File Offset: 0x0005A095
		' (set) Token: 0x06000B56 RID: 2902 RVA: 0x0005BE9D File Offset: 0x0005A09D
		Friend Overridable Property PictureBox3 As PictureBox

		' Token: 0x06000B57 RID: 2903 RVA: 0x0005BEA8 File Offset: 0x0005A0A8
		Private Sub chkButler_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "chkButler_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkButler.CheckState = CheckState.Unchecked
				Return
			End If
			Me.comm_active = True
			MyBase.Enabled = False
			If Me.chkButler.CheckState = CheckState.Checked Then
				modSMCi.ButlerAnSMCi()
			Else
				modSMCi.ButlerAusSMCi()
			End If
			MyBase.Enabled = True
			Me.comm_active = False
		End Sub

		' Token: 0x06000B58 RID: 2904 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkFilmMotor_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B59 RID: 2905 RVA: 0x0005BF30 File Offset: 0x0005A130
		<MethodImpl(MethodImplOptions.NoInlining Or MethodImplOptions.NoOptimization)>
		Private Sub chkFrameLighting_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			Dim num2 As Integer
			Dim num6 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				If Me.chkFrameLighting.CheckState <> CheckState.Checked Then
					GoTo IL_1F3
				End If
				IL_13:
				num = 2
				If Operators.CompareString(FileSystem.Dir(MyProject.Application.Info.DirectoryPath + "\TEMPLATES\SERVICE.TPL", FileAttribute.Normal), "", False) <> 0 Then
					GoTo IL_55
				End If
				IL_41:
				num = 3
				Interaction.MsgBox("Kein Service Template gefunden! Bitte zuerst erstellen!", MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_205
				IL_55:
				num = 5
				Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_71:
				num = 6
				Dim left As String = modMain.GiveIni(lpFileName, "SYSTEM", "LASTSERVICEIMAGE")
				IL_86:
				num = 7
				If Operators.CompareString(left, "", False) = 0 Then
					GoTo IL_9E
				End If
				IL_97:
				ProjectData.ClearProjectError()
				num2 = 1
				IL_9E:
				num = 9
				If Operators.CompareString(modDeclares.mdlFktSelectedFile, "", False) = 0 Then
					GoTo IL_205
				End If
				IL_B6:
				num = 10
				modDeclares.WritePrivateProfileString("SYSTEM", "LASTSERVICEIMAGE", modDeclares.mdlFktSelectedFile, lpFileName)
				IL_CF:
				num = 11
				Dim text As String = "SERVICE"
				Me.LoadData(text)
				IL_E1:
				num = 12
				MyProject.Forms.frmImage.Show()
				IL_F3:
				num = 13
				MyProject.Forms.frmImage.NoPaint = True
				IL_106:
				num = 14
				modDeclares.SetWindowPos(MyProject.Forms.frmImage.Handle.ToInt32(), -1, 0, 0, 0, 0, 3)
				IL_12D:
				num = 15
				Application.DoEvents()
				IL_135:
				num = 16
				modDeclares.ShowLib = False
				IL_13E:
				num = 17
				Dim num3 As Integer = CInt(MyBase.Handle)
				Dim num4 As Integer = 1
				modMain.FH_IG_load_file(modDeclares.mdlFktSelectedFile, num3, num4)
				IL_160:
				num = 18
				modDeclares.SystemData.RollenNr = ""
				IL_172:
				num = 19
				Application.DoEvents()
				IL_17A:
				num = 20
				modDeclares.UseAccusoft = True
				IL_183:
				num = 21
				MyProject.Forms.frmImage.ImagXpress1.Visible = False
				IL_19B:
				num = 22
				Application.DoEvents()
				IL_1A3:
				num = 23
				modDeclares.glbOrientation = (Operators.CompareString(modMain.GiveIni(lpFileName, "SYSTEM", "Portrait" + Conversions.ToString(CInt(modDeclares.SystemData.kopfindex))), "1", False) = 0)
				IL_1DE:
				num = 24
				modPaint.RepaintImageAccusoft2(modDeclares.SystemData.kopfindex)
				GoTo IL_205
				IL_1F3:
				num = 26
				MyProject.Forms.frmImage.Close()
				IL_205:
				GoTo IL_2C3
				IL_20A:
				Dim num5 As Integer = num6 + 1
				num6 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num5)
				IL_284:
				GoTo IL_2B8
				IL_286:
				num6 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num2)
				IL_296:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num2 <> 0 And num6 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_286
			End Try
			IL_2B8:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_2C3:
			If num6 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000B5A RID: 2906 RVA: 0x0005C224 File Offset: 0x0005A424
		Private Sub chkLamp_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "chkLamp_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkLamp.CheckState = CheckState.Unchecked
				Return
			End If
			Me.comm_active = True
			MyBase.Enabled = False
			If Me.chkLamp.CheckState = CheckState.Checked Then
				If modDeclares.SystemData.Trinamic Then
					modTrinamic.LEDAnTrinamic()
				Else
					modSMCi.LEDAnSMCi()
				End If
			ElseIf modDeclares.SystemData.Trinamic Then
				modTrinamic.LEDAusTrinamic()
			Else
				modSMCi.LEDAusSMCi()
			End If
			MyBase.Enabled = True
			Me.comm_active = False
		End Sub

		' Token: 0x06000B5B RID: 2907 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkPort_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B5C RID: 2908 RVA: 0x0005C2D4 File Offset: 0x0005A4D4
		Private Sub chkventil_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.comm_active AndAlso Me.comm_active Then
				Me.ComAction = "chkventil_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkventil.CheckState = CheckState.Unchecked
				Return
			End If
			Me.comm_active = True
			MyBase.Enabled = False
			If modDeclares.SystemData.SMCI Then
				If Me.chkventil.CheckState = CheckState.Checked Then
					modSMCi.MagnetAnSMCi()
				Else
					modSMCi.MagnetAusSMCi()
				End If
			Else
				If Me.chkventil.CheckState = CheckState.Checked Then
					modDeclares.Outputs = modDeclares.Outputs Or 32
				Else
					modDeclares.Outputs = modDeclares.Outputs And 223
				End If
				Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
			End If
			MyBase.Enabled = True
			Me.comm_active = False
		End Sub

		' Token: 0x06000B5D RID: 2909 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkBlendenMotor_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B5E RID: 2910 RVA: 0x0005C3CC File Offset: 0x0005A5CC
		Private Sub chkVakuumPumpe_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "chkVakuumPumpe_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkVakuumPumpe.CheckState = CheckState.Unchecked
				Return
			End If
			Me.comm_active = True
			MyBase.Enabled = False
			If modDeclares.SystemData.SMCI Then
				If Me.chkVakuumPumpe.CheckState = CheckState.Checked Then
					modSMCi.VakuumAnSMCi()
				Else
					modSMCi.VakuumAusSMCi()
				End If
			Else
				If Me.chkVakuumPumpe.CheckState = CheckState.Checked Then
					modDeclares.Outputs = modDeclares.Outputs Or 64
				Else
					modDeclares.Outputs = modDeclares.Outputs And 191
				End If
				Dim text As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 0
				text = modMultiFly.Comm_Read(num, True)
			End If
			MyBase.Enabled = True
			Me.comm_active = False
		End Sub

		' Token: 0x06000B5F RID: 2911 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdExit_ClickEvent(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B60 RID: 2912 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub cmdNull_CheckStateChanged(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B61 RID: 2913 RVA: 0x0005C4BC File Offset: 0x0005A6BC
		Private Sub cmdSensorCheck_Click(eventSender As Object, eventArgs As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "cmdSensorCheck_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) <> 0 Then
				Me.Timer1.Enabled = False
				MyProject.Forms.frmSensors.ShowDialog()
				Me.Timer1.Enabled = True
			End If
		End Sub

		' Token: 0x06000B62 RID: 2914 RVA: 0x0005C528 File Offset: 0x0005A728
		Private Sub cmdTestFilming_Click(eventSender As Object, eventArgs As EventArgs)
			Dim num5 As Integer
			Dim num18 As Integer
			Dim obj As Object
			Try
				IL_00:
				Dim num As Integer = 1
				MyBase.Enabled = False
				IL_09:
				num = 2
				modMultiFly.CleanBuffer()
				IL_11:
				num = 3
				modDeclares.FW = modMultiFly.GetFirmware()
				IL_1D:
				num = 4
				If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
					GoTo IL_7FB
				End If
				IL_34:
				num = 6
				Me.comm_active = True
				IL_3D:
				num = 7
				MyProject.Forms.frmFilmTest.Show()
				IL_4E:
				num = 8
				MyProject.Forms.frmFilmTest.lblFilmCounter.Text = "0"
				IL_69:
				num = 9
				MyProject.Forms.frmFilmTest.lblVacuumErrors.Text = "0"
				IL_85:
				num = 10
				Dim num2 As Double = Conversions.ToDouble(Me.txtSchrittePromm.Text)
				IL_9A:
				num = 11
				Dim num3 As Short = 8S
				IL_A0:
				num = 12
				If Not Me.optVViertel.Checked Then
					GoTo IL_B6
				End If
				IL_B0:
				num = 13
				num3 = 4S
				IL_B6:
				num = 14
				If Not Me.optVHalb.Checked Then
					GoTo IL_CC
				End If
				IL_C6:
				num = 15
				num3 = 2S
				IL_CC:
				num = 16
				If Not Me.optVEintel.Checked Then
					GoTo IL_E2
				End If
				IL_DC:
				num = 17
				num3 = 1S
				IL_E2:
				num = 18
				Dim num4 As Short = 8S
				IL_E8:
				num = 19
				If Not Me.optViertel.Checked Then
					GoTo IL_FE
				End If
				IL_F8:
				num = 20
				num4 = 4S
				IL_FE:
				num = 21
				If Not Me.optHalb.Checked Then
					GoTo IL_114
				End If
				IL_10E:
				num = 22
				num4 = 2S
				IL_114:
				num = 23
				If Not Me.optEintel.Checked Then
					GoTo IL_12A
				End If
				IL_124:
				num = 24
				num4 = 1S
				IL_12A:
				ProjectData.ClearProjectError()
				num5 = 2
				IL_131:
				num = 26
				MyProject.Application.Info.DirectoryPath + "\docufile.ini"
				IL_14E:
				num = 27
				modMain.LoadSystemData()
				IL_156:
				num = 28
				modDeclares.stoptest = False
				IL_15F:
				ProjectData.ClearProjectError()
				num5 = 1
				IL_166:
				num = 30
				modDeclares.SystemData.belichtung = modDeclares.SystemData.SchritteVolleUmdrehung
				IL_17D:
				num = 31
				modDeclares.SystemData.schrittweite = 4.0
				IL_193:
				num = 32
				Dim num6 As Integer = CInt(Math.Round(modDeclares.SystemData.schrittweite * num2))
				IL_1AB:
				num = 33
				Conversions.ToInteger(Me._txtSpeed_0.Text)
				IL_1BF:
				num = 34
				Dim num7 As Integer = modDeclares.SystemData.verschlussgeschw
				IL_1CE:
				num = 35
				num7 = 4000
				IL_1D8:
				num = 36
				Dim num8 As Double = modDeclares.SystemData.zusatzbelichtung / 1000.0
				IL_1F1:
				num = 37
				modDeclares.Outputs = 0
				IL_1FA:
				num = 38
				Dim num9 As Short = 2S
				Dim num10 As Integer = 0
				Dim num11 As Integer = 0
				Dim num12 As Integer = 1
				Dim num13 As Integer = 1
				Dim num14 As Integer = 1
				modMultiFly.FahreMotor(num9, num10, num11, num12, num13, num14, num3)
				Do
					IL_223:
					num = 40
					num9 = 2S
				Loop While modMultiFly.MotorIsRunning(num9)
				IL_232:
				num = 42
				modDeclares.Sleep(2000)
				IL_23F:
				num = 43
				If Not modDeclares.SystemData.CheckVakuum Then
					GoTo IL_25E
				End If
				IL_24E:
				num = 44
				modDeclares.Outputs = modDeclares.Outputs Or 64
				IL_25E:
				num = 45
				modDeclares.Outputs = modDeclares.Outputs Or 32
				IL_26E:
				num = 46
				Dim [string] As String = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				IL_28B:
				num = 47
				modMultiFly.Comm_Send([string])
				IL_296:
				num = 48
				num14 = 0
				[string] = modMultiFly.Comm_Read(num14, True)
				IL_2A5:
				num = 49
				modDeclares.Sleep(2000)
				IL_2B2:
				num = 50
				modDeclares.Outputs = modDeclares.Outputs Or 8
				IL_2C1:
				num = 51
				[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				IL_2DE:
				num = 52
				modMultiFly.Comm_Send([string])
				IL_2E9:
				num = 53
				num14 = 0
				[string] = modMultiFly.Comm_Read(num14, True)
				IL_2F8:
				num = 54
				Dim num15 As Short = 0S
				IL_2FE:
				num = 55
				modDeclares.finish = False
				Do
					IL_307:
					num = 57
					If num8 = 0.0 Then
						IL_317:
						num = 58
						num9 = 2S
						num14 = 1
						num13 = 0
						num12 = 0
						modMultiFly.FahreMotor(num9, modDeclares.SystemData.belichtung, num7, num14, num13, num12, num3)
					Else
						IL_347:
						num = 60
						num9 = 2S
						num12 = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
						num13 = 1
						num14 = 0
						num11 = 0
						modMultiFly.FahreMotor(num9, num12, num7, num13, num14, num11, num3)
						Do
							IL_387:
							num = 62
							num9 = 2S
						Loop While modMultiFly.MotorIsRunning(num9)
						IL_396:
						num = 64
						modDeclares.Sleep(CInt(Math.Round(num8 * 1000.0)))
						IL_3B0:
						num = 65
						num9 = 2S
						num11 = CInt(Math.Round(CDbl(modDeclares.SystemData.belichtung) / 2.0))
						num14 = 1
						num13 = 0
						num12 = 0
						modMultiFly.FahreMotor(num9, num11, num7, num14, num13, num12, num3)
					End If
					Do
						IL_3F0:
						num = 67
						num9 = 2S
					Loop While modMultiFly.MotorIsRunning(num9)
					IL_3FF:
					num = 69
					Application.DoEvents()
					IL_407:
					num = 70
					If CInt(num15) = modDeclares.SystemData.schlitze - 1 Then
						IL_41D:
						num = 71
						[string] = ChrW(25) & "="
						IL_426:
						num = 72
						modMultiFly.Comm_Send([string])
						IL_431:
						num = 73
						num12 = 0
						[string] = modMultiFly.Comm_Read(num12, True)
						IL_440:
						num = 74
						Dim num16 As Integer = Strings.Asc([string])
						IL_44B:
						num = 75
						If(num16 And 1) = 0 Then
							IL_457:
							num = 77
							num9 = 2S
							num12 = 0
							num13 = 0
							num14 = 1
							num11 = 1
							num10 = 1
							modMultiFly.FahreMotor(num9, num12, num13, num14, num11, num10, num3)
							Do
								IL_480:
								num = 79
								num9 = 2S
							Loop While modMultiFly.MotorIsRunning(num9)
							IL_48F:
							num = 81
							modDeclares.Sleep(1000)
						End If
						IL_49C:
						num = 82
						num15 = 0S
					Else
						IL_4A4:
						num = 84
						num15 += 1S
					End If
					IL_4AE:
					num = 85
					modDeclares.Outputs = modDeclares.Outputs And 223
					IL_4C1:
					num = 86
					[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					IL_4DE:
					num = 87
					modMultiFly.Comm_Send([string])
					IL_4E9:
					num = 88
					num10 = 0
					[string] = modMultiFly.Comm_Read(num10, True)
					IL_4F8:
					num = 89
					If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOff(modDeclares.SystemData.VacuumOff))) Then
						IL_516:
						num = 90
						Dim text As String = "TXT_ERR_VACUUM_OFF"
						Dim left As String = modMain.GetText(text)
						IL_529:
						num = 91
						If Operators.CompareString(left, "", False) = 0 Then
							IL_53B:
							num = 92
							left = "Vakuum konnte nicht ausgeschaltet werden!"
						End If
						IL_545:
						num = 93
						num9 = 0S
						text = "file-converter"
						modMain.msgbox2(left, num9, text)
					Else
						IL_560:
						num = 95
						modDeclares.Outputs = modDeclares.Outputs And -9
						IL_570:
						num = 96
						[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						IL_58D:
						num = 97
						modMultiFly.Comm_Send([string])
						IL_598:
						num = 98
						num10 = 0
						[string] = modMultiFly.Comm_Read(num10, True)
					End If
					IL_5A7:
					num = 99
					If Not modDeclares.finish Then
						IL_5B1:
						num = 100
						num9 = 1S
						num12 = Conversions.ToInteger(Me._txtSpeed_0.Text)
						num10 = modMultiFly.GetSpeedFromSteps(num6, num12)
						num11 = 1
						num14 = 0
						num13 = 0
						If Not modMultiFly.FahreMotor(num9, num6, num10, num11, num14, num13, num4) Then
							IL_5F2:
							num = 101
							modDeclares.stoptest = True
							IL_5FB:
							num = 102
							MyBase.Enabled = True
							IL_605:
							num = 103
							Application.DoEvents()
						End If
						Do
							IL_60D:
							num = 105
							num9 = 1S
						Loop While modMultiFly.MotorIsRunning(num9)
					End If
					IL_61C:
					num = 107
					If modDeclares.SystemData.CheckVakuum Then
						IL_62B:
						num = 108
						modDeclares.Outputs = modDeclares.Outputs Or 64
					End If
					IL_63B:
					num = 109
					modDeclares.Outputs = modDeclares.Outputs Or 32
					IL_64B:
					num = 110
					[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
					IL_668:
					num = 111
					modMultiFly.Comm_Send([string])
					IL_673:
					num = 112
					num13 = 0
					[string] = modMultiFly.Comm_Read(num13, True)
					IL_682:
					num = 113
					If Conversions.ToBoolean(Operators.NotObject(modMultiFly.WaitForVacuumOn(modDeclares.SystemData.VacuumOn))) Then
						IL_6A0:
						num = 114
						Dim text As String = "TXT_ERR_VACUUM_ON"
						Dim left As String = modMain.GetText(text)
						IL_6B3:
						num = 115
						If Operators.CompareString(left, "", False) = 0 Then
							IL_6C5:
							num = 116
							left = "Vakuum konnte nicht angeschaltet werden!"
						End If
						IL_6CF:
						num = 117
						num9 = 0S
						text = "file-converter"
						modMain.msgbox2(left, num9, text)
					Else
						IL_6EA:
						num = 119
						modDeclares.Outputs = modDeclares.Outputs Or 8
						IL_6F9:
						num = 120
						[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
						IL_716:
						num = 121
						modMultiFly.Comm_Send([string])
						IL_721:
						num = 122
						num13 = 0
						[string] = modMultiFly.Comm_Read(num13, True)
					End If
					IL_730:
					num = 123
					MyProject.Forms.frmFilmTest.lblFilmCounter.Text = Conversions.ToString(Conversions.ToDouble(MyProject.Forms.frmFilmTest.lblFilmCounter.Text) + 1.0)
					IL_76F:
					num = 124
				Loop While Not modDeclares.stoptest
				IL_77C:
				num = 125
				MyProject.Forms.frmFilmTest.Close()
				IL_78E:
				num = 126
				modDeclares.Outputs = 0
				IL_797:
				num = 127
				[string] = ChrW(22) & "!" + Conversions.ToString(Strings.Chr(modDeclares.Outputs))
				IL_7B4:
				num = 128
				modMultiFly.Comm_Send([string])
				IL_7C2:
				num = 129
				num13 = 0
				[string] = modMultiFly.Comm_Read(num13, True)
				IL_7D4:
				num = 130
				Me.comm_active = False
				IL_7FB:
				GoTo IL_A65
				IL_7E3:
				num = 132
				Interaction.MsgBox(Information.Err().Description, MsgBoxStyle.OkOnly, Nothing)
				GoTo IL_7FB
				IL_800:
				Dim num17 As Integer = num18 + 1
				num18 = 0
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num17)
				IL_A22:
				GoTo IL_A5A
				IL_A24:
				num18 = num
				switch(ICSharpCode.Decompiler.ILAst.ILLabel[], num5)
				IL_A38:
			Catch obj2 When endfilter(TypeOf obj Is Exception And num5 <> 0 And num18 = 0)
				Dim ex As Exception = CType(obj2, Exception)
				GoTo IL_A24
			End Try
			IL_A5A:
			Throw ProjectData.CreateProjectError(-2146828237)
			IL_A65:
			If num18 <> 0 Then
				ProjectData.ClearProjectError()
			End If
		End Sub

		' Token: 0x06000B63 RID: 2915 RVA: 0x0005CFC0 File Offset: 0x0005B1C0
		Private Sub frmService_KeyDown(eventSender As Object, eventArgs As KeyEventArgs)
			' The following expression was wrapped in a checked-statement
			Dim num As Short = CShort(eventArgs.KeyCode)
			Dim num2 As Short = CShort((eventArgs.KeyData / Keys.Shift))
			If num = 27S Then
				MyBase.Close()
			End If
			If num = 65S And num2 = 2S Then
				modDeclares.UserLevel = 10S
				Dim form As Form = Me
				Me.SetRights(form, modDeclares.UserLevel)
			End If
		End Sub

		' Token: 0x06000B64 RID: 2916 RVA: 0x0005D010 File Offset: 0x0005B210
		Private Sub frmService_Load(eventSender As Object, eventArgs As EventArgs)
			If modDeclares.UseDebug And modDeclares.SystemData.Trinamic Then
				Me.butExitDemo.Enabled = True
			End If
			Me.butExitDemo.Enabled = False
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				MyBase.Close()
				Return
			End If
			modDeclares.Outputs = 0
			Me.comm_active = False
			Dim form As Form = Me
			modMain.SetTexts(form)
			Dim text As String = "TXT_MOTOR_START"
			Dim text2 As String = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Start Motor"
			End If
			Me.Text = Me.Text + " Firmware " + modDeclares.FW
			Me.chkFilmMotor.Text = text2
			Me.chkFilmMotor.Tag = "0"
			Me.LoadValues()
			form = Me
			Me.SetRights(form, modDeclares.UserLevel)
			MyBase.Tag = Me.Text
			Me.Timer1.Enabled = False
		End Sub

		' Token: 0x06000B65 RID: 2917 RVA: 0x0005D108 File Offset: 0x0005B308
		Private Sub frmService_FormClosed(eventSender As Object, eventArgs As FormClosedEventArgs)
			MyProject.Forms.frmSMAMain.Enabled = True
			If Operators.CompareString(modDeclares.FW, "", False) <> 0 Then
				Dim text As String = ChrW(22) & "!" & vbNullChar
				modMultiFly.Comm_Send(text)
				Dim num As Integer = 500
				text = modMultiFly.Comm_Read(num, True)
			End If
			modSMCi.VakuumAusSMCi()
			modDeclares.NoPaint = False
		End Sub

		' Token: 0x06000B66 RID: 2918 RVA: 0x0005D160 File Offset: 0x0005B360
		Private Sub LoadValues()
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Me.txtSchritte.Text = modMain.GiveIni(text, "SYSTEM", "Schritte")
			Me._txtSpeed_0.Text = modMain.GiveIni(text, "SYSTEM", "Speed")
			Me.txtVerschlussSchritte.Text = modMain.GiveIni(text, "SYSTEM", "VerschlussSchritte")
			Me._txtVerschlussSpeed_0.Text = modMain.GiveIni(text, "SYSTEM", "VerschlussSpeed")
			Me.txtVerschlussZeit.Text = modMain.GiveIni(text, "SYSTEM", "VerschlussZeit")
			Dim txtSchrittePromm As TextBox = Me.txtSchrittePromm
			Dim text2 As String = modMain.GiveIni(text, "SYSTEM", "SchrittePromm")
			txtSchrittePromm.Text = modMain.KommazuPunkt(text2)
			If Operators.CompareString(Me.txtSchrittePromm.Text, "", False) = 0 Then
				Me.txtSchrittePromm.Text = Conversions.ToString(modDeclares.SystemData.schrittepromm(1))
			End If
			text2 = "SYSTEM"
			Dim text3 As String = "SERVICE_VERSCHLUSS_AUFLOESUNG"
			Dim num As Short = CShort(modDeclares.GetPrivateProfileInt(text2, text3, 8, text))
			Select Case num
				Case 1S
					Me.optVEintel.Checked = True
				Case 2S
					Me.optVHalb.Checked = True
				Case 3S
				Case 4S
					Me.optVViertel.Checked = True
				Case Else
					If num = 8S Then
						Me.optVAchtel.Checked = True
					End If
			End Select
			text3 = "SYSTEM"
			text2 = "SERVICE_FILM_AUFLOESUNG"
			num = CShort(modDeclares.GetPrivateProfileInt(text3, text2, 8, text))
			Select Case num
				Case 1S
					Me.optEintel.Checked = True
					Return
				Case 2S
					Me.optHalb.Checked = True
					Return
				Case 3S
				Case 4S
					Me.optViertel.Checked = True
					Return
				Case Else
					If num <> 8S Then
						Return
					End If
					Me.optAchtel.Checked = True
			End Select
		End Sub

		' Token: 0x06000B67 RID: 2919 RVA: 0x0005D344 File Offset: 0x0005B544
		Private Sub SaveValues()
			Dim lpFileName As String = MyProject.Application.Info.DirectoryPath + "\docufile.ini"
			Dim flag As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "Schritte", Me.txtSchritte.Text, lpFileName) > False)
			Dim flag2 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "Speed", Me._txtSpeed_0.Text, lpFileName) > False)
			Dim flag3 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "VerschlussSchritte", Me.txtVerschlussSchritte.Text, lpFileName) > False)
			Dim flag4 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "VerschlussSpeed", Me._txtVerschlussSpeed_0.Text, lpFileName) > False)
			Dim flag5 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "VerschlussZeit", Me.txtVerschlussZeit.Text, lpFileName) > False)
			Dim flag6 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SchrittePromm", Me.txtSchrittePromm.Text, lpFileName) > False)
			Dim lpString As String = "8"
			If Me.optVViertel.Checked Then
				lpString = "4"
			End If
			If Me.optVHalb.Checked Then
				lpString = "2"
			End If
			If Me.optVEintel.Checked Then
				lpString = "1"
			End If
			Dim flag7 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SERVICE_VERSCHLUSS_AUFLOESUNG", lpString, lpFileName) > False)
			lpString = "8"
			If Me.optViertel.Checked Then
				lpString = "4"
			End If
			If Me.optHalb.Checked Then
				lpString = "2"
			End If
			If Me.optEintel.Checked Then
				lpString = "1"
			End If
			Dim flag8 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "SERVICE_FILM_AUFLOESUNG", lpString, lpFileName) > False)
			Dim flag9 As Boolean = -(modDeclares.WritePrivateProfileString("SYSTEM", "VerschlussZeit", Me.txtVerschlussZeit.Text, lpFileName) > False)
		End Sub

		' Token: 0x06000B68 RID: 2920 RVA: 0x0005D4F8 File Offset: 0x0005B6F8
		Private Sub Test_Click(eventSender As Object, eventArgs As EventArgs)
			Dim num As Short = 8S
			If Me.optVEintel.Checked Then
				num = 1S
			End If
			If Me.optVHalb.Checked Then
				num = 2S
			End If
			If Me.optVViertel.Checked Then
				num = 4S
			End If
			Dim num2 As Integer = Conversions.ToInteger(Me.txtVerschlussSchritte.Text)
			Dim num3 As Integer = Conversions.ToInteger(Me._txtVerschlussSpeed_0.Text)
			Dim num4 As Short = 1S
			Do
				Dim num5 As Short = 2S
				Dim num6 As Integer = 1
				Dim num7 As Integer = 0
				Dim num8 As Integer = 0
				modMultiFly.FahreMotor(num5, num2, num3, num6, num7, num8, num)
				Do
					num5 = 2S
				Loop While modMultiFly.MotorIsRunning(num5)
				num4 += 1S
			Loop While num4 <= 25S
		End Sub

		' Token: 0x06000B69 RID: 2921 RVA: 0x0005D590 File Offset: 0x0005B790
		Private Sub Timer1_Tick(eventSender As Object, eventArgs As EventArgs)
		End Sub

		' Token: 0x06000B6A RID: 2922 RVA: 0x0005D5A0 File Offset: 0x0005B7A0
		Private Sub SetRights(ByRef f As Form, ByRef UserLevel1 As Short)
			Dim text As String = MyProject.Application.Info.DirectoryPath + "\ParameterRights.Ini"
			Try
				For Each obj As Object In f.Controls
					Dim control As Control = CType(obj, Control)
					If Operators.CompareString(modMain.GiveIni(text, f.Name, control.Name), "", False) <> 0 Then
						' The following expression was wrapped in a checked-expression
						Dim num As Short = CShort(Math.Round(Conversion.Val(modMain.GiveIni(text, f.Name, control.Name))))
						Operators.CompareString(control.Name, "chkBlendenMotor", False)
						If num > UserLevel1 Then
							control.Enabled = False
						Else
							control.Enabled = True
						End If
					End If
				Next
			Finally
				Dim enumerator As IEnumerator
				If TypeOf enumerator Is IDisposable Then
					TryCast(enumerator, IDisposable).Dispose()
				End If
			End Try
		End Sub

		' Token: 0x06000B6B RID: 2923 RVA: 0x0005D678 File Offset: 0x0005B878
		Private Sub LoadData(ByRef Name_Renamed As String)
			Dim text As String = Name_Renamed
			If Operators.CompareString(Support.Format(Strings.Right(Name_Renamed, 4), ">", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1), ".TPL", False) <> 0 Then
				text += ".TPL"
			End If
			text = MyProject.Application.Info.DirectoryPath + "\TEMPLATES\" + text
			Dim ptr As modDeclares.typSystem = modDeclares.SystemData
			ptr.Hoehe = Conversions.ToInteger(modMain.GiveIni(text, "TEMPLATE", "QuerHoehe"))
			ptr.Breite = Conversions.ToInteger(modMain.GiveIni(text, "TEMPLATE", "QuerBreite"))
			ptr.X = Conversions.ToInteger(modMain.GiveIni(text, "TEMPLATE", "QuerX"))
			ptr.y = Conversions.ToInteger(modMain.GiveIni(text, "TEMPLATE", "QuerY"))
			ptr.UseBlip = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "BLIP"), "1", False) = 0, True, False))
			ptr.AutoAlign = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AUTOALIGN"), "1", False) = 0, True, False))
			ptr.AutoAlign180 = Conversions.ToBoolean(Interaction.IIf(Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AutoAlign180"), "1", False) = 0, True, False))
			If Operators.CompareString(modMain.GiveIni(text, "TEMPLATE", "AUTOORIENTATION"), "90", False) = 0 Then
				ptr.DoLeftAuto = True
			Else
				ptr.DoLeftAuto = False
			End If
			Dim left As String = modMain.GiveIni(text, "TEMPLATE", "ROTATION")
			If Operators.CompareString(left, "90", False) = 0 Then
				modDeclares.SystemData.FixRot = 2S
			End If
			If Operators.CompareString(left, "180", False) = 0 Then
				modDeclares.SystemData.FixRot = 3S
			End If
			If Operators.CompareString(left, "270", False) = 0 Then
				modDeclares.SystemData.FixRot = 4S
			End If
			If Operators.CompareString(left, "0", False) = 0 Then
				modDeclares.SystemData.FixRot = 1S
			End If
		End Sub

		' Token: 0x06000B6C RID: 2924 RVA: 0x0005D89C File Offset: 0x0005BA9C
		Private Sub txtSpeed_TextChanged(eventSender As Object, eventArgs As EventArgs)
			If Not False AndAlso Versioned.IsNumeric(Me._txtSpeed_0.Text) Then
				Me._txtSpeed_1.Text = Support.Format(Conversions.ToDouble(Me._txtSpeed_0.Text) * 30.517578125, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			End If
		End Sub

		' Token: 0x06000B6D RID: 2925 RVA: 0x0005D8F4 File Offset: 0x0005BAF4
		Private Sub txtVerschlussSpeed_TextChanged(eventSender As Object, eventArgs As EventArgs)
			If Versioned.IsNumeric(Me._txtVerschlussSpeed_0.Text) Then
				Me._txtVerschlussSpeed_1.Text = Support.Format(Conversions.ToDouble(Me._txtVerschlussSpeed_0.Text) * 30.517578125, "0.0", FirstDayOfWeek.Sunday, FirstWeekOfYear.Jan1)
			End If
		End Sub

		' Token: 0x06000B6E RID: 2926 RVA: 0x0005D949 File Offset: 0x0005BB49
		Private Sub cmdCancel_Click(sender As Object, e As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "cmdExit_Click"
				Return
			End If
			Me.SaveValues()
		End Sub

		' Token: 0x06000B6F RID: 2927 RVA: 0x0005D968 File Offset: 0x0005BB68
		Private Sub chkFilmMotor_CheckedChanged(sender As Object, e As EventArgs)
			Dim num As Double = Conversions.ToDouble(Me.txtSchrittePromm.Text)
			If Me.comm_active Then
				Me.ComAction = "chkFilmMotor_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkFilmMotor.Checked = False
				Return
			End If
			Conversions.ToDouble(Me._txtSpeed_0.Text)
			Me.comm_active = True
			MyBase.Enabled = False
			Dim num2 As Short = 8S
			Dim num3 As Short = 3S
			If Me.optVEintel.Checked Then
				num2 = 1S
				num3 = 0S
			End If
			If Me.optVHalb.Checked Then
				num2 = 2S
				num3 = 1S
			End If
			If Me.optVViertel.Checked Then
				num2 = 4S
				num3 = 2S
			End If
			Dim num4 As Short = 8S
			Dim num5 As Short = 3S
			If Me.optEintel.Checked Then
				num4 = 1S
				num5 = 0S
			End If
			If Me.optHalb.Checked Then
				num4 = 2S
				num5 = 1S
			End If
			If Me.optViertel.Checked Then
				num4 = 4S
				num5 = 2S
			End If
			modMultiFly.SetStepMode(num2, num4)
			If modDeclares.SystemData.Trinamic Then
				Dim num6 As Short = 0S
				modTrinamic.SetStepperResolutionTrinamic(num6, num3)
				num6 = 1S
				modTrinamic.SetStepperResolutionTrinamic(num6, num5)
			End If
			Dim text As String = "TXT_MOTOR_STOP"
			Dim text2 As String = modMain.GetText(text)
			If Operators.CompareString(text2, "", False) = 0 Then
				text2 = "Stop Motor"
			End If
			text = "TXT_MOTOR_RUNNING"
			Dim text3 As String = modMain.GetText(text)
			If Operators.CompareString(text3, "", False) = 0 Then
				text3 = "Motor laeuft"
			End If
			text = "TXT_MOTOR_START"
			Dim text4 As String = modMain.GetText(text)
			If Operators.CompareString(text4, "", False) = 0 Then
				text4 = "Start Motor"
			End If
			Me.chkFilmMotor.Enabled = False
			Me.SaveValues()
			If Operators.ConditionalCompareObjectEqual(Me.chkFilmMotor.Tag, "0", False) Then
				Me.chkFilmMotor.Tag = "1"
				Dim num7 As Integer = CInt(Math.Round(Conversions.ToDouble(Me.txtSchritte.Text) * num))
				Dim num8 As Integer = Conversions.ToInteger(Me._txtSpeed_0.Text)
				If num7 = 0 Then
					Me.chkFilmMotor.Text = text2
				Else
					Me.chkFilmMotor.Text = text3
					Me.chkFilmMotor.Refresh()
				End If
				Dim num6 As Short = 1S
				Dim num9 As Integer = 1
				Dim num10 As Integer = 0
				Dim num11 As Integer = 0
				modMultiFly.FahreMotor(num6, num7, num8, num9, num10, num11, num4)
				Do
					num6 = 1S
				Loop While modMultiFly.MotorIsRunning(num6)
				MyBase.Enabled = True
				Me.chkFilmMotor.ForeColor = ColorTranslator.FromOle(0)
				If num7 <> 0 Then
					Me.chkFilmMotor.Text = text4
					Me.chkFilmMotor.Tag = "0"
				End If
				Me.chkFilmMotor.Enabled = True
			Else
				Me.chkFilmMotor.Text = text4
				If Operators.CompareString(Me.chkFilmMotor.Text, "", False) = 0 Then
					Me.chkFilmMotor.Text = "Start Motor"
				End If
				Dim text5 As String = "%"
				modMultiFly.Comm_Send(text5)
				Dim num11 As Integer = 0
				text5 = modMultiFly.Comm_Read(num11, True)
				MyBase.Enabled = True
				Me.chkFilmMotor.Enabled = True
				Me.chkFilmMotor.ForeColor = ColorTranslator.FromOle(0)
				Me.chkFilmMotor.Tag = "0"
			End If
			Me.comm_active = False
		End Sub

		' Token: 0x06000B70 RID: 2928 RVA: 0x0005DCA0 File Offset: 0x0005BEA0
		Private Sub chkBlendenMotor_CheckedChanged(sender As Object, e As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "chkBlendenMotor_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) = 0 Then
				Me.chkBlendenMotor.CheckState = CheckState.Unchecked
				Return
			End If
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) <> 0 Then
				Me.comm_active = True
				MyBase.Enabled = False
				Me.SaveValues()
				Dim num As Short = 8S
				Dim num2 As Short = 3S
				If Me.optVEintel.Checked Then
					num = 1S
					num2 = 0S
				End If
				If Me.optVHalb.Checked Then
					num = 2S
					num2 = 1S
				End If
				If Me.optVViertel.Checked Then
					num = 4S
					num2 = 2S
				End If
				Dim num3 As Short = 8S
				Dim num4 As Short = 3S
				If Me.optEintel.Checked Then
					num3 = 1S
					num4 = 0S
				End If
				If Me.optHalb.Checked Then
					num3 = 2S
					num4 = 1S
				End If
				If Me.optViertel.Checked Then
					num3 = 4S
					num4 = 2S
				End If
				modMultiFly.SetStepMode(num, num3)
				If modDeclares.SystemData.Trinamic Then
					Dim num5 As Short = 0S
					modTrinamic.SetStepperResolutionTrinamic(num5, num2)
					num5 = 1S
					modTrinamic.SetStepperResolutionTrinamic(num5, num4)
				End If
				Dim tickCount As Integer = modDeclares.GetTickCount()
				Dim num6 As Integer = 0
				If Versioned.IsNumeric(Me.txtVerschlussZeit.Text) Then
					num6 = Conversions.ToInteger(Me.txtVerschlussZeit.Text)
				End If
				If Me.chkBlendenMotor.CheckState = CheckState.Checked Then
					Dim num7 As Integer = Conversions.ToInteger(Me.txtVerschlussSchritte.Text)
					If num7 <> 0 Then
						If num6 <> 0 Then
							Dim num8 As Integer = Conversions.ToInteger(Me._txtVerschlussSpeed_0.Text)
							Dim num5 As Short = 2S
							Dim num9 As Integer = CInt(Math.Round(CDbl(num7) / 2.0))
							Dim num10 As Integer = 1
							Dim num11 As Integer = 0
							Dim num12 As Integer = 0
							modMultiFly.FahreMotor(num5, num9, num8, num10, num11, num12, num)
							Do
								num5 = 2S
							Loop While modMultiFly.MotorIsRunning(num5)
							modDeclares.Sleep(num6)
							num5 = 2S
							num12 = CInt(Math.Round(CDbl(num7) / 2.0))
							num11 = 1
							num10 = 0
							num9 = 0
							modMultiFly.FahreMotor(num5, num12, num8, num11, num10, num9, num)
							Do
								num5 = 2S
							Loop While modMultiFly.MotorIsRunning(num5)
							Me.chkBlendenMotor.CheckState = CheckState.Unchecked
						Else
							Dim num8 As Integer = Conversions.ToInteger(Me._txtVerschlussSpeed_0.Text)
							Dim num5 As Short = 2S
							Dim num9 As Integer = 1
							Dim num10 As Integer = 0
							Dim num11 As Integer = 0
							modMultiFly.FahreMotor(num5, num7, num8, num9, num10, num11, num)
							Do
								num5 = 2S
							Loop While modMultiFly.MotorIsRunning(num5)
							Me.chkBlendenMotor.CheckState = CheckState.Unchecked
						End If
					End If
				Else
					Dim text As String = "$"
					modMultiFly.Comm_Send(text)
					Dim num11 As Integer = 0
					text = modMultiFly.Comm_Read(num11, True)
				End If
				Dim num13 As Integer = modDeclares.GetTickCount() - tickCount
				Me.Text = Conversions.ToString(Operators.ConcatenateObject(Operators.ConcatenateObject(Operators.ConcatenateObject(MyBase.Tag, " "), num13), " ms"))
				MyBase.Enabled = True
				Me.comm_active = False
			End If
		End Sub

		' Token: 0x06000B71 RID: 2929 RVA: 0x0005DF80 File Offset: 0x0005C180
		Private Sub cmdNull_CheckedChanged(sender As Object, e As EventArgs)
			If Me.comm_active Then
				Me.ComAction = "cmdNull_Click"
				Return
			End If
			modMultiFly.CleanBuffer()
			modDeclares.FW = modMultiFly.GetFirmware()
			If Operators.CompareString(modDeclares.FW, "", False) <> 0 Then
				Me.comm_active = True
				MyBase.Enabled = False
				If modDeclares.SystemData.SMCI Then
					MyProject.Forms.frmSucheNullpunkt.Show()
					Application.DoEvents()
					modSMCi.FahreVerschlussMotorAufNullpunkt()
					modDeclares.gCancelRefSearch = False
					While True
						Dim num As Short = 2S
						If Not(modMultiFly.MotorIsRunning(num) And Not modDeclares.gCancelRefSearch) Then
							Exit For
						End If
						MyProject.Forms.frmSucheNullpunkt.lblStat.Text = Conversions.ToString(CInt(modTrinamic.NullpunktStatusTrinamic()))
						Application.DoEvents()
					End While
					Dim num2 As Integer = 0
					modTrinamic.StopMotorTrinamic(num2)
					MyProject.Forms.frmSucheNullpunkt.Close()
					MyBase.Show()
				Else
					Dim num As Short
					If modDeclares.SystemData.SmallShutter Then
						num = 2S
						Dim num2 As Integer = 0
						Dim num3 As Integer = 0
						Dim num4 As Integer = CInt((1S - modDeclares.SystemData.SmallShutterFirstDir))
						Dim num5 As Integer = 1
						Dim num6 As Integer = 1
						modMultiFly.FahreMotor(num, num2, num3, num4, num5, num6, modDeclares.SystemData.VResolution)
					Else
						num = 2S
						Dim num6 As Integer = 0
						Dim num5 As Integer = 0
						Dim num4 As Integer = 1
						Dim num3 As Integer = 1
						Dim num2 As Integer = 1
						modMultiFly.FahreMotor(num, num6, num5, num4, num3, num2, modDeclares.SystemData.VResolution)
					End If
					Do
						num = 2S
					Loop While modMultiFly.MotorIsRunning(num)
					modDeclares.Sleep(1000)
				End If
				Me.cmdNull.CheckState = CheckState.Unchecked
				MyBase.Enabled = True
				Me.comm_active = False
			End If
		End Sub

		' Token: 0x06000B72 RID: 2930 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkVakuumPumpe_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000B73 RID: 2931 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkLamp_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000B74 RID: 2932 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub SetUserRights()
		End Sub

		' Token: 0x06000B75 RID: 2933 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Button1_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000B76 RID: 2934 RVA: 0x0005E0F8 File Offset: 0x0005C2F8
		Private Sub cmdLogon_Click(sender As Object, e As EventArgs)
			Dim userLevel As Short = modDeclares.UserLevel
			MyProject.Forms.frmLogin.ShowDialog()
			If userLevel <> modDeclares.UserLevel Then
				Dim form As Form = Me
				Me.SetRights(form, modDeclares.UserLevel)
			End If
		End Sub

		' Token: 0x06000B77 RID: 2935 RVA: 0x0005E130 File Offset: 0x0005C330
		Private Sub butReconnect_Click(sender As Object, e As EventArgs)
			modMain.frmcomm1.DeInit()
			modMain.frmcomm1.Init()
		End Sub

		' Token: 0x06000B78 RID: 2936 RVA: 0x0005E148 File Offset: 0x0005C348
		Private Sub butExitDemo_Click(sender As Object, e As EventArgs)
			modTrinamic.ResetTrinamic()
			Dim text As String
			Dim num As Short
			Dim text2 As String
			If modTrinamic.TrinamicSupplyVoltageOK() Then
				modDeclares.UseDebug = False
				text = "Production Mode enabled!"
				num = 0S
				text2 = "file-converter"
				modMain.msgbox2(text, num, text2)
				Return
			End If
			text2 = "Switch the Power on first and close the Lid!"
			num = 0S
			text = "file-converter"
			modMain.msgbox2(text2, num, text)
		End Sub

		' Token: 0x06000B79 RID: 2937 RVA: 0x0005E1A0 File Offset: 0x0005C3A0
		Private Sub butReset_Click(sender As Object, e As EventArgs)
			modTrinamic.ResetTrinamic()
			modMain.frmcomm1.DeInit()
			MyProject.Forms.frmReset.ShowDialog()
			modMain.frmcomm1.Init()
			Me.chkventil.Checked = False
			Me.chkVakuumPumpe.Checked = False
			Me.chkLamp.Checked = False
		End Sub

		' Token: 0x06000B7A RID: 2938 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub chkventil_CheckedChanged(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x06000B7B RID: 2939 RVA: 0x0005E1FC File Offset: 0x0005C3FC
		Private Sub Button1_Click_1(sender As Object, e As EventArgs)
			Dim schritte As Integer = 40000
			Dim num As Integer = 1000
			Dim num2 As Integer = 1
			Dim num3 As Integer = 1
			modTrinamic.FahreVerschlussMotorTrinamic(schritte, num, num2, num3)
		End Sub

		' Token: 0x06000B7C RID: 2940 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Frame3_Enter(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x040006C0 RID: 1728
		Private components As IContainer

		' Token: 0x040006C1 RID: 1729
		Public ToolTip1 As ToolTip

		' Token: 0x040006F6 RID: 1782
		Private comm_active As Boolean

		' Token: 0x040006F7 RID: 1783
		Private ComAction As String

		' Token: 0x040006F8 RID: 1784
		Private ComExtra As Short
	End Class
End Namespace
