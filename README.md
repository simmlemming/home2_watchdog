# home2_watchdog

## ADR
1. One Input mqtt channel is used by all devices. Also, output channel is the same for all communication.
1. All commands result in status response.

## Protocol
```json
{"name": "temp_01",
"type": "motion_sensor",
"room": "living_room",
"state": 1,
"value": 24,
"cmd": "reset",
"device": "<FCM token>",
"signal": "..."}
```
Note: `device` is deprecated, `value` should be used instaed.

#### Examples
Status message
```json
    {
        "name": "motion_01",
        "room": "living_room",
        "type": "motion_sensor",
        "state": 4,
        "signal": "..."
    }
```
Command message
```json
    {
        "name": "living_motion_1",
        "cmd": "reset"
    }
```

name in command can be `all`, all devices will respond.


## Types
```
type = ["temp_sensor" | "humidity_sensor" | "motion_sensor"]
```

## Commands
```
cmd = ["on" | "off" | "reset" | "state" | "add_device" ]
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
