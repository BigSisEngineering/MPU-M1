; ============================================ 
;                  Network                   
; ============================================

M550 P"A0-3"                         ; set printer name

if {network.interfaces[0].type = "ethernet"}
    M553 P255.255.0.0
    M552 P10.207.13.10 S1
else
    M552 S1

; ============================================ 
;                    Lower Hose                
; ============================================ 

; Bed
M308 S0 P"spi.cs0" Y"rtd-max31865" A"hose_down"
M950 H0 C"out1" T0 Q10  A"hose_down"                         ; create bed heater output on bedheat and map it to sensor 0
M307 H0 R0.314 K0.140:0.000 D43.92 E1.35 S1.00 B0       ; enable bang-bang mode for the bed heater and set PWM limit
M140 H0                                                 ; map heated bed to heater 0
M143 H0 S100                                            ; set temperature limit for heater 0 to 100C

; ============================================ 
;                  Main Tank               
; ============================================ 

M308 S1 P"temp1" Y"thermistor" A"main_tank" T100000 B3950 
M950 H1 C"out2" T1 A"main_tank"                              ; create nozzle heater output on e0heat and map it to sensor 1
M307 H1 R0.571 K0.158:0.000 D6.56 E1.35 S1.00 B0
M141 H1

; ============================================ 
;                  Upper Hose                  
; ============================================ 

M308 S2 P"spi.cs1" Y"rtd-max31865" A"hose_up"             ; configure sensor 2 as an RTD on spi.cs1, named hose2
M950 H2 C"out3" T2 A"hose_up"                             ; create heater 2 on out3 and map it to sensor 2
M307 H2 R0.400 K0.200:0.000 D30.00 E1.50 S1.00 B0       ; set PID parameters for heater 2
M143 H2 S100                                            ; set temperature limit for heater 2 to 100C

; Define Tool for Hose2
M563 P0 H2 S"hose_up"                                      ; define tool 1 using heater 2, named hose2
G10 P0 R0 S0                                             ; set tool 1 active and standby temperatures to 0


