M550 P"A0-3"                         ; set printer name

if {network.interfaces[0].type = "ethernet"}
    M553 P255.255.0.0
    M552 P10.207.13.10 S1
else
    M552 S1
	
; ============================================ 
;                    Heaters                   
; ============================================ 
M308 S0 P"spi.cs0" Y"rtd-max31865" A"hose"

M950 H0 C"out1" T0 Q10  A"hose"                         ; create bed heater output on bedheat and map it to sensor 0
M307 H0 R0.314 K0.140:0.000 D43.92 E1.35 S1.00 B0       ; enable bang-bang mode for the bed heater and set PWM limit
M140 H0                                                 ; map heated bed to heater 0
M143 H0 S100                                            ; set temperature limit for heater 0 to 120C

M308 S1 P"temp1" Y"thermistor" A"tank" T100000 B3950 
M950 H1 C"out2" T1 A"tank"                              ; create nozzle heater output on e0heat and map it to sensor 1
M307 H1 R0.571 K0.158:0.000 D6.56 E1.35 S1.00 B0
M141 H1

M308 S2 P"temp2" Y"thermistor" A"nozzle"
M950 H2 C"out3" T2 A"nozzle"
M143 H2 S90  
M307 H2 B0 S1.00 
M307 H2 R0.759 K0.610:0.000 D28.33 E1.35 S1.00 B0 V23.9
M563 S"nozzle" P0 H2                                    ; set temperature limit for heater 1 to 100C 


M563 P0 H2                                              ; define tool 0 
M563 P1 H3
