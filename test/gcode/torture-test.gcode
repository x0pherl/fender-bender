; created using https://help.prusa3d.com/article/prusa-firmware-specific-g-code-commands_112173
G28 ; home
M104 S215 set temp to 215
G1 X125 Y105 Z150 F4800; move the z axis up and centered
M109 S215 T0 ; wait for temp to hit 215

;loop up then down through each of the filaments
T0 ; get filament 1
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T4 ; get filament 5
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
;loop up then down through each of the filaments
T0 ; get filament 1
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T4 ; get filament 5
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
;loop up then down through each of the filaments
T0 ; get filament 1
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T4 ; get filament 5
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
;loop up then down through each of the filaments
T0 ; get filament 1
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T4 ; get filament 5
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
;loop up then down through each of the filaments
T0 ; get filament 1
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T4 ; get filament 5
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T3 ; get filament 4
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T2 ; get filament 3
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off
T1 ; get filament 2
Tc load to nozzle
M106 S225 ; turn the part fan on
G1 E500 F500 ; extrude filament
M106 S0 ; turn the part fan off

M702; unload filament

M104 S0 set temp to 0
