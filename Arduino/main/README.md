
```
├───lib
│   ├───AnalogSensors
│   ├───Communication
│   ├───DebounceInput
│   ├───Define
│   ├───Servo
│   ├───ST3215_Comm
│   ├───StarWheelServo
│   ├───UnloaderServo
│   └───Valve
└───src
    └───main.cpp
```



### Communication Protocol
#### Format
|         |            |                | Header | Target | Action | Param-1 | Param-2 | Param-3 | CRC_H | CRC_L |   return   |
| :-----: | :--------: | :------------: | :----: | :----: | :----: | :-----: | :-----: | :-----: | :---: | :---: | :--------: |
| Action  |            |                |  0XAA  |        |        |         |         |         |       |       |            |
|         | Star Wheel |                |        |  0x01  |        |         |         |         |       |       |            |
|         |            |   Move Step    |        |        |  0x01  |  0x??   |  0x00   |  0x00   |       |       |    ACK     |
|         |            |      Turn      |        |        |  0x02  |  0x??   |  0x00   |  0x00   |       |       |    N/A     |
|         |            |     Homing     |        |        |  0x03  |  0x00   |  0x00   |  0x00   |       |       |   STATUS   |
|         |            |  Move by time  |        |        |  0x05  |  0x??   |  0x??   |  0x00   |       |       |   STATUS   |
|         |            |  Reset Error   |        |        |  0x06  |  0x00   |  0x00   |  0x00   |       |       |    ACK     |
|         |            | Move by Count  |        |        |  0x07  |  0x??   |  0x00   |  0x00   |       |       |    ACK     |
|         |            | Save to EEPROM |        |        |  0x08  |  0x??   |  0x??   |  0x00   |       |       |    ACK     |
|         |  Unloader  |                |        |  0x02  |        |         |         |         |       |       |            |
|         |            |     Unload     |        |        |  0x01  |  0x00   |  0x00   |  0x00   |       |       |   STATUS   |
|         |            |      Home      |        |        |  0x03  |  0x00   |  0x00   |  0x00   |       |       |   STATUS   |
|         |            |  Reset Error   |        |        |  0x06  |  0x00   |  0x00   |  0x00   |       |       |    ACK     |
|         |            |  Get position  |        |        |  0x0A  |  0x00   |  0x00   |  0x00   |       |       |    POS     |
|         |    Valve   |                |        |  0x04  |        |         |         |         |       |       |            |
|         |            |     Set Delay  |        |        |  0x01  |  0x??   |  0x??   |  0x00   |       |       |    ACK     |
|         |            |     Turn ON    |        |        |  0x02  |  0x00   |  0x00   |  0x00   |       |       |    ACK     |
|         |            |     Turn OFF   |        |        |  0x03  |  0x00   |  0x00   |  0x00   |       |       |    ACK     |
| Sensing |            |                |  0xBB  |        |        |         |         |         |       |       |            |
|         | Star Wheel |                |        |  0x01  |        |         |         |         |       |       |            |
|         |            |  Error Status  |        |        |  0x01  |  0x00   |  0x00   |  0x00   |       |       |            |
|         |  Unloader  |                |        |  0x02  |        |         |         |         |       |       |            |
|         |            |  Error Status  |        |        |  0x01  |  0x00   |  0x00   |  0x00   |       |       | ERROR MSG  |
|         |    GPIO    |                |        |  0x03  |        |         |         |         |       |       |            |
|         |            |  Pin reading   |        |        |  0x00  |  0x00   |  0x00   |  0x00   |       |       | SENSOR MSG |

#### Argument
| Description                | Hex  | type   | position(s)      | Remark                  |
| -------------------------- | ---- | ------ | ---------------- | ----------------------- |
| Start Wheel Steps          | 0x01 | int8   | PARAM_1          | Number of step          |
| Start Wheel Turn           | 0x02 | int8   | PARAM_1          | *NOT DEVELOPED*         |
| Start Wheel Step by time   | 0x05 | uint16 | PARAM_1, PARAM_2 | time in 600ms - 1500 ms |
| Start Wheel Count          | 0x07 | uint16 | PARAM_1, PARAM_2 | Encoder Count           |
| Start Wheel save to EEPROM | 0x08 | uint16 | PARAM_1, PARAM_2 | Encoder Count           |

#### Feedback
| **Description** \ Byte position | 0    | 1    | 2    | 3    | 4    | 5    | 6     | 7     |
| ------------------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ----- | ----- |
| ACK                             | 0x41 | 0x43 | 0x4B | 0x00 | 0x00 | 0x00 | 0x00  | 0x00  |
| STATUS                          | 0xCC | 0x00 | 0x00 | 0x?? | 0x00 | 0x00 | CRC_H | CRC_L |
| ERROR MSG                       | 0xCC | 0x03 | 0x?? | 0x00 | 0x00 | 0x00 | CRC_H | CRC_L |
| SENSOR MSG                      | 0xCC | 0x03 | 0x?? | 0x?? | 0x?? | 0x?? | CRC_H | CRC_L |


### Load and step speed relateion
![Load/ms graph](doc/Inversely%20Proportional%20Fit.png)
```
Its inversely proportional fit with equation:
load = (207458.549078)/ms - 3.393769
with factor, load*1.1 + 40
``` 