## RPI GPIO

| _Odd pins description_ | _Pin name_  |     | _Pin name_  | _Even pin description_  |
| ---------------------- | ----------- | --- | ----------- | ----------------------- |
| 3V3 power              | 3V3 (1)     |     | (2) 5V      |                         |
| sensors sda OUT        | GPIO2 (3)   |     | (4) 5V      |                         |
| sensors scl OUT        | GPIO3 (5)   |     | (6) GND     | GND                     |
|                        | GPIO4 (7)   |     | (8) GPIO14  | sensor 1 data IN        |
|                        | GND (9)     |     | (10) GPIO15 | sensor 2 data IN        |
| DFplayer io1 OUT       | GPIO17 (11) |     | (12) GPIO18 | LED display control OUT |
| DFplayer io2 OUT       | GPIO27 (13) |     | (14) GND    |                         |
|                        | GPIO22 (15) |     | (16) GPIO23 |                         |
|                        | 3V3 (17)    |     | (18) GPIO24 |                         |
|                        | GPIO10 (19) |     | (20) GND    |                         |
|                        | GPIO9 (21)  |     | (22) GPIO25 |                         |
|                        | GPIO11 (23) |     | (24) GPIO8  |                         |
|                        | GND (25)    |     | (26) GPIO7  |                         |
|                        | GPIO0 (27)  |     | (28) GPIO1  |                         |
| Encoder left IN        | GPIO5 (29)  |     | (30) GND    |                         |
| Encoder right IN       | GPIO6 (31)  |     | (32) GPIO12 |                         |
|                        | GPIO13 (33) |     | (34) GND    |                         |
| Button 3 IN            | GPIO19 (35) |     | (36) GPIO16 | Button 4 IN             |
| Button 1 IN            | GPIO26 (37) |     | (38) GPIO20 | Button 2 IN             |
|                        | GND (39)    |     | (40) GPIO21 |                         |

## Sensor pins

| _Pin description_ | _PCB-Label_ | Additional comments                                                                                                            |
| ----------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Power line        | VCC         |                                                                                                                                |
| Ground            | GND         |                                                                                                                                |
| I2C communication | SCL         | Reading and writing registers.                                                                                                 |
| I2C communication | SDA         | Reading and writing registers.                                                                                                 |
| Auxilary sensor   | XDA         | Unused. For external sensors.                                                                                                  |
| Auxilary sensor   | XCL         | Unused. For external sensors.                                                                                                  |
| Address pin       | AD0         | Putting this pin HIGH sets the sensors I2C address to 0x69 (0x68 by default). One of the broken sensors pulls power from here. |
| Interrupt pin     | INT         | This pin is set to HIGH once the sensor detects motion.                                                                        |
