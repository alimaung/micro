VB.NET Source Code Analysis
Here are the key functions that handle step and speed scaling:
1. Film Motor Movement (FahreFilmMotorTrinamic)
Public Sub FahreFilmMotorTrinamic(Schritte As Long, ByRef Freq As Integer, ByRef res As Integer)
    ' Set speed first
    modTrinamic.SetMaximumSpeedTrinamic(1, CShort(Freq), CShort(res))
    
    ' Scale steps based on resolution
    If res = 1 Then
        Schritte = CLng(Math.Round(CDbl(Schritte) / 8.0))
    End If
    If res = 2 Then
        Schritte = CLng(Math.Round(CDbl(Schritte) / 4.0))
    End If
    If res = 4 Then
        Schritte = CLng(Math.Round(CDbl(Schritte) / 2.0))
    End If
    If res = 8 Then
        Schritte = Schritte  ' No scaling
    End If
    
    ' Send to controller
    modTrinamic.SendBinComandToTrinamic(1, 4, 1, 1, Schritte, False)
End Sub
2. Speed Scaling (SetMaximumSpeedTrinamic)
Public Function SetMaximumSpeedTrinamic(ByRef Motor_ As Short, Speed As Short, res As Short) As Boolean
    If Motor_ = 1 Then  ' Film motor
        If res = 1 Then
            Speed = CShort(Math.Round(CDbl(Speed) / 4.0))
        End If
        If res = 2 Then
            Speed = CShort(Math.Round(CDbl(Speed) / 2.0))
        End If
        If res = 8 Then
            Speed *= 2
        End If
    Else  ' Shutter motor (Motor 0)
        If res = 4 Then
            Speed = CShort(Math.Round(CDbl(Speed) / 2.0))
        End If
        If res = 2 Then
            Speed = CShort(Math.Round(CDbl(Speed) / 4.0))
        End If
        If res = 1 Then
            Speed = CShort(Math.Round(CDbl(Speed) / 8.0))
        End If
    End If
    
    ' Send to controller
    modTrinamic.SendBinComandToTrinamic(1, 5, Motor_, 4, Speed, False)
End Function
3. Shutter Motor Movement (FahreVerschlussMotorTrinamic)
Public Sub FahreVerschlussMotorTrinamic(Schritte As Integer, ByRef Freq As Integer, ByRef Richtung As Integer, ByRef Res As Integer)
    ' Set speed first
    modTrinamic.SetMaximumSpeedTrinamic(0, CShort(Freq), CShort(Res))
    
    ' Scale steps based on resolution
    If Res = 4 Then
        Schritte = CInt(Math.Round(CDbl(Schritte) / 2.0))
    End If
    If Res = 2 Then
        Schritte = CInt(Math.Round(CDbl(Schritte) / 4.0))
    End If
    If Res = 1 Then
        Schritte = CInt(Math.Round(CDbl(Schritte) / 8.0))
    End If
    
    ' Send to controller
    modTrinamic.SendBinComandToTrinamic(0, 4, 0, 1, Schritte, False)
End Sub
4. Distance Calculation Example
From the exposure code:
' Example: Calculate steps for vacuum movement
Dim num102 As Integer = CInt(Math.Round(CDbl(modDeclares.SystemData.VacSteps) * modDeclares.SystemData.schrittepromm(CInt(num2))))

' Example: Calculate steps for image width 
num40 = CInt(Math.Round(CDbl(modDeclares.SystemData.Breite) * modDeclares.SystemData.MonitorHeightOnFilm(CInt(num2)) / CDbl(modDeclares.SystemData.Hoehe) * modDeclares.SystemData.schrittepromm(CInt(num2))))

Comprehensive Resolution & Speed Scaling Table
Motor	Resolution	Input Steps<br/>(for 10mm)	VB.NET Step Scaling<br/>(÷ factor)	Final Steps<br/>Sent to Controller	Input Speed<br/>(e.g., 2000)	VB.NET Speed Scaling	Final Speed<br/>Sent to Controller	Actual Distance<br/>Achieved
Film Motor (1)	1 (Full Step)	1,398	÷ 8	175	2000	÷ 4	500	10.000mm
Film Motor (1)	2 (Half Step)	1,398	÷ 4	350	2000	÷ 2	1000	10.000mm
Film Motor (1)	4 (Quarter Step)	1,398	÷ 2	699	2000	No scaling	2000	10.000mm
Film Motor (1)	8 (Eighth Step)	1,398	No scaling	1,398	2000	× 2	4000	10.000mm
Shutter Motor (0)	1 (Full Step)	1,398	÷ 8	175	2000	÷ 8	250	10.000mm
Shutter Motor (0)	2 (Half Step)	1,398	÷ 4	350	2000	÷ 4	500	10.000mm
Shutter Motor (0)	4 (Quarter Step)	1,398	÷ 2	699	2000	÷ 2	1000	10.000mm
Shutter Motor (0)	8 (Eighth Step)	1,398	No scaling	1,398	2000	No scaling	2000	10.000mm
Python Calculator Reverse Logic
To achieve the same 10mm distance, my Python calculator needs to reverse the VB.NET scaling:
Motor	Resolution	Base Steps<br/>(10mm × 139.8)	Python Scaling<br/>(× factor)	Steps to Send<br/>to CLI	VB.NET Will Scale<br/>(÷ factor)	Final Steps<br/>to Controller	Result
Film Motor (1)	1	1,398	× 8	11,184	÷ 8	1,398	✅ 10mm
Film Motor (1)	2	1,398	× 4	5,592	÷ 4	1,398	✅ 10mm
Film Motor (1)	4	1,398	× 2	2,796	÷ 2	1,398	✅ 10mm
Film Motor (1)	8	1,398	× 1	1,398	× 1	1,398	✅ 10mm
Key Insights
The VB.NET code applies scaling at TWO levels:
Step scaling in FahreFilmMotorTrinamic/FahreVerschlussMotorTrinamic
Speed scaling in SetMaximumSpeedTrinamic
Different motors have different scaling patterns:
Film motor (1): More aggressive speed scaling at low resolutions
Shutter motor (0): Consistent scaling pattern for both steps and speed
The base calculation is always:
   steps = distance_mm * schrittepromm(film_format)