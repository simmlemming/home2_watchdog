# home2_watchdog

## Protocol
```json
{"name": "temp_01",
"type": "motion_sensor",
"room": "living_room",
"state": 1,
"value": 24,
"cmd": "reset",
"signal": "..."}
```

## Types
```
type = ["temp_sensor" | "humidity_sensor" | "motion_sensor"]
```

## Commands
```
cmd = ["on" | "off" | "reset" | "state"]
```

## States
```
STATE_OFF = 0;
STATE_OK = 1;
STATE_INIT = 2;
STATE_ERROR = 3;
STATE_ALARM = 4;
STATE_PAUSED = 5;
```
