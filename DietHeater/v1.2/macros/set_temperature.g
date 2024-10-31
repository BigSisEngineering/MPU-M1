; Set temperatures for tank and hoses

; Set main tank (chamber) temperature to 65C
M141 S65 H1

; Set lower hose (bed, heater 0) temperature to 70C
M140 S70 H0

; Set upper hose (tool 0) temperature to 70C
M104 S70 H2

; Ensure upper hose (tool 0) is active
T0 ; Select tool 0 (hose2)
M116 ; Wait for the temperature to stabilize
