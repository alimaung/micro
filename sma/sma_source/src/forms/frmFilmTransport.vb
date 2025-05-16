Imports System
Imports System.ComponentModel
Imports System.Diagnostics
Imports System.Drawing
Imports System.Runtime.CompilerServices
Imports System.Windows.Forms
Imports Microsoft.VisualBasic.Compatibility.VB6
Imports Microsoft.VisualBasic.CompilerServices

Namespace fileconverter
	' Token: 0x0200001A RID: 26
	<DesignerGenerated()>
	Friend Class frmFilmTransport
		Inherits Form

		' Token: 0x060008AE RID: 2222 RVA: 0x000462D3 File Offset: 0x000444D3
		<DebuggerNonUserCode()>
		Public Sub New()
			AddHandler MyBase.Load, AddressOf Me.frmFilmTransport_Load
			AddHandler MyBase.Activated, AddressOf Me.frmFilmTransport_Activated
			Me.InitializeComponent()
		End Sub

		' Token: 0x060008AF RID: 2223 RVA: 0x00046305 File Offset: 0x00044505
		<DebuggerNonUserCode()>
		Protected Overrides Sub Dispose(Disposing As Boolean)
			If Disposing AndAlso Me.components IsNot Nothing Then
				Me.components.Dispose()
			End If
			MyBase.Dispose(Disposing)
		End Sub

		' Token: 0x170001E4 RID: 484
		' (get) Token: 0x060008B0 RID: 2224 RVA: 0x00046324 File Offset: 0x00044524
		' (set) Token: 0x060008B1 RID: 2225 RVA: 0x0004632C File Offset: 0x0004452C
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

		' Token: 0x170001E5 RID: 485
		' (get) Token: 0x060008B2 RID: 2226 RVA: 0x0004636F File Offset: 0x0004456F
		' (set) Token: 0x060008B3 RID: 2227 RVA: 0x00046378 File Offset: 0x00044578
		Public Overridable Property Label1 As Label
			<CompilerGenerated()>
			Get
				Return Me._Label1
			End Get
			<CompilerGenerated()>
			<MethodImpl(MethodImplOptions.Synchronized)>
			Set(value As Label)
				Dim value2 As EventHandler = AddressOf Me.Label1_Click
				Dim label As Label = Me._Label1
				If label IsNot Nothing Then
					RemoveHandler label.Click, value2
				End If
				Me._Label1 = value
				label = Me._Label1
				If label IsNot Nothing Then
					AddHandler label.Click, value2
				End If
			End Set
		End Property

		' Token: 0x060008B4 RID: 2228 RVA: 0x000463BC File Offset: 0x000445BC
		<DebuggerStepThrough()>
		Private Sub InitializeComponent()
			Me.components = New Container()
			Dim componentResourceManager As ComponentResourceManager = New ComponentResourceManager(GetType(frmFilmTransport))
			Me.ToolTip1 = New ToolTip(Me.components)
			Me.Timer1 = New Timer(Me.components)
			Me.Label1 = New Label()
			MyBase.SuspendLayout()
			Me.Timer1.Enabled = True
			Me.Timer1.Interval = 400
			Me.Label1.BackColor = SystemColors.Control
			Me.Label1.Cursor = Cursors.[Default]
			Me.Label1.Font = New Font("Microsoft Sans Serif", 20.25F, FontStyle.Regular, GraphicsUnit.Point, 0)
			Me.Label1.ForeColor = Color.Red
			Me.Label1.Location = New Point(48, 8)
			Me.Label1.Name = "Label1"
			Me.Label1.RightToLeft = RightToLeft.No
			Me.Label1.Size = New Size(521, 41)
			Me.Label1.TabIndex = 0
			Me.Label1.Text = "Film is transported !!!"
			Me.Label1.TextAlign = ContentAlignment.TopCenter
			MyBase.AutoScaleDimensions = New SizeF(6F, 13F)
			MyBase.AutoScaleMode = AutoScaleMode.Font
			Me.BackColor = SystemColors.Control
			MyBase.ClientSize = New Size(613, 58)
			MyBase.Controls.Add(Me.Label1)
			Me.Cursor = Cursors.[Default]
			MyBase.Icon = CType(componentResourceManager.GetObject("$this.Icon"), Icon)
			MyBase.Location = New Point(4, 30)
			MyBase.Name = "frmFilmTransport"
			Me.RightToLeft = RightToLeft.No
			MyBase.StartPosition = FormStartPosition.Manual
			MyBase.ResumeLayout(False)
		End Sub

		' Token: 0x060008B5 RID: 2229 RVA: 0x00046588 File Offset: 0x00044788
		Private Sub frmFilmTransport_Load(eventSender As Object, eventArgs As EventArgs)
			Dim form As Form = Me
			modMain.SetTexts(form)
			MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - Support.PixelsToTwipsX(CDbl(MyBase.Width)) / 2.0)))
			MyBase.Top = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Height)) / 2.0 - Support.PixelsToTwipsX(CDbl(MyBase.Height)) / 2.0)))
		End Sub

		' Token: 0x060008B6 RID: 2230 RVA: 0x00046632 File Offset: 0x00044832
		Private Sub Timer1_Tick(eventSender As Object, eventArgs As EventArgs)
			Me.Label1.Visible = Not Me.Label1.Visible
		End Sub

		' Token: 0x060008B7 RID: 2231 RVA: 0x0001A972 File Offset: 0x00018B72
		Private Sub Label1_Click(sender As Object, e As EventArgs)
		End Sub

		' Token: 0x060008B8 RID: 2232 RVA: 0x00046650 File Offset: 0x00044850
		Private Sub frmFilmTransport_Activated(sender As Object, e As EventArgs)
			' The following expression was wrapped in a checked-expression
			' The following expression was wrapped in a unchecked-expression
			MyBase.Left = CInt(Math.Round(Support.TwipsToPixelsX(Support.PixelsToTwipsX(CDbl(Screen.PrimaryScreen.Bounds.Width)) / 2.0 - Support.PixelsToTwipsX(CDbl(MyBase.Width)) / 2.0)))
		End Sub

		' Token: 0x040005BE RID: 1470
		Private components As IContainer

		' Token: 0x040005BF RID: 1471
		Public ToolTip1 As ToolTip
	End Class
End Namespace
