
class Keys:
    OK = 'OK'
    # Mode component
    Off = 'Off'
    On = 'On'
    Idle = 'Idle'

    Start = 'Start'
    Stop = 'Stop'
    Ready = 'Ready'
    Sleep = 'Sleep'

    LeakTest = 'Leak test'
    SystemBake = 'System bake'
    Manual = 'Manual'

    TurningOn3 = 'Turning on (3)'
    TurningOn4 = 'Turning on (4)'
    TurningOn5 = 'Turning on (5)'

    TurningOff6 = 'Turning off (6)'
    TurningOff7 = 'Turning off (7)'

    TurningIdle8 = 'Turning idle (8)'
    TurningIdle9 = 'Turning idle (9)'
    TurningIdle10 = 'Turning idle (10)'

    Error = 'Error'

    Degas = 'Degas'

    Filament1 = 'Fil. 1'
    Filament2 = 'Fil. 2'

    BakeOn = 'Bake on'
    SampleOn = 'Sample on'

    # Gauge
    Pirani = 'Pirani'
    Roughting = 'Roughing'
    CM = 'CM'
    Bypass = 'Bypass'
    IG = 'IG'
    Chamber = 'Chamber'

    # Unit
    Torr = 'torr'
    Pascal = 'pascal'
    MilliBar = 'mbar'
    Bar = 'bar'

    # Heater
    Elbow = 'Elbow'
    SampleLine = 'Sample line'
    Capillary = 'Capillary'

    LeakTestOn = 'Leak test on'
    LeakTestOff = 'Leak test off'
    SystemBakeOn = 'System bake on'
    SystemBakeOff = 'System bake off'

    ErrorMessageDict = {
        OK: 0,
        'Set OK (1)': 1,
        'Invalid Command (9)': 9,
        'Incomplete Command (10)': 10,
        'Illegal Command (11)': 11,
        'Not a query (12)': 12,
        'Missing Parameter (13)': 13,
        'Extra Parameter (14)': 14,
        'Out of range (15)': 15,
        'Bad parameter (16)': 16,
        'Missing comma (17)': 17,
        'Extra comma (18)': 18,
        'Null string (19)': 19,
        'Not a number (20)': 20,

        'RGA on network (22)': 22,
        'Command buffer full (23)': 23,
        'RGA buffer full (24)': 24,
        'RGA unavailable (25)': 25,
        'String too long (26)': 26,
        'Illegal character (27)': 27,
        'RGA OFF (28)': 28,
        'Leak Test ON (29)': 29,
        'Bypass pump OFF (30)': 30,
        'Bypass pump ON (31)': 31,
        'Bypass valve CLOSED (32)': 32,
        'Bypass valve OPEN (33)': 33,
        'Sample valve OPEN (34)': 34,
        'Sample pressure HIGH (35)': 35,
        'Roughing pump OFF (36)': 36,
        'Roughing pump ON (37)': 37,
        'Rough pressure HIGH (38)': 38,
        'Turbo pump OFF (39)': 39,
        'Turbo pump ON (40)': 40,
        'Turbo pump running (41)': 41,
        'Turbo not ready (42)': 42,
        'RGA ON (43)': 43,
        'RGA  OFF (44)': 44,
        'RGA busy (45)': 45,
        'IG ON (46)': 46,
        'Leak Test  ON (47)': 47,
        'System Bake ON (48)': 48,
        'AUTO sequence ON (49)': 49,
        'Interlock triggered (50)': 50,
        'Pressure Interlock off (51)': 51,
        'Leak test timeout (52)': 52,
        'Fac. Default Loaded (53)': 53,

        'Heater initialize (61)': 61,
        'Elbow Heater T/C (62)': 62,
        'Chamber Heater T/C (63)': 63,
        'Sample Heater T/C (64)': 64,
        'Capillary Heater T/C (65)': 65,
        'Temp. Set Failed (66)': 66,
        'No Sample Heater (67)': 67,

        'No IG detected (73)': 73,
        'IG unexpected off (74)': 74,

        'IG voltage (76)': 76,
        'IG emission (77)': 77,
        'IG off failed (78)': 78,

        'RGA off failed (80)': 80,
        'No Mux detected (81)': 81,
        'Mux malfunction (82)': 82,

        'No Vent valve (85)': 85,

        'AUX comm. error (89)': 89,
        'Main board reset (90)': 90,

        'No PG detected (92)': 92,
        'No PG filament (93)': 93,
        'PG short-circuited (94)': 94,
        'PG malfunction (95)': 95,
        'CM malfunction (96)': 96,

        'BP too high (98)': 98,
        'BV too high (99)': 99,
        'SV too high (100)': 100,
        'BP too low (101)': 101,
        'RP too high (102)': 102,

        'TP too high (104)': 104,
        'IG too high (105)': 105,

        'No TP controller (109)': 109,
        'TP stop failed (110)': 110,
        'TP current (111)': 111,
        'No TP connected (112)': 112,
        'TP overload (113)': 113,
        'TP bearing hot (114)': 114,
        'TP hot (115)': 115,
        'TP start (116)': 116,
        'TP input voltage (117)': 117,
        'TP op voltage (118)': 118,
        'TP low voltage (119)': 119,
        'TP soft start (120)': 120,

        'Too many Errors (126)': 126,
    }
