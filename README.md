# esp32-c3-mini-defer-write-issue

Contaminated data buffers of Characteristic onWrite() when Central device writes characteristic too frequently


The Bluetooth LE central device sends 3 data packets to ESP32-C3-MINI-1 without delays (and without response confirmation) as following codes:

```javascript
writeCharacteristic(0xAA, 0xAA, 0xAA, 0xAA, 0xAA);
writeCharacteristic(0xBB, 0xBB, 0xBB, 0xBB, 0xBB);
writeCharacteristic(0xCC, 0xCC, 0xCC, 0xCC, 0xCC);
```

ESP32's `onWrite()` receives 3 packets but the content of 3 times of callback functions are not as expected:

```text
1st packet: [0xCC, 0xCC, 0xCC, 0xCC, 0xCC]
2nd packet: [0xCC, 0xCC, 0xCC, 0xCC, 0xCC]
3rd packet: [0xCC, 0xCC, 0xCC, 0xCC, 0xCC]
```

With the same central codes, our previous BLE module (based on nRF51822) can receive 3 times of callback and correct data contents.

We've tried to add some delays such as 30 ~ 60ms between each writeCharacteristic() at Central device, and ESP32-C3-MINI can receives correct contents. However, we need to keep backward compatibility with BLE central devices since those BLE central devices were shipped, is there any way to resolve this issue?



## Issue Reproduction

To reproduce this issue, 

1. Flash the arduino sketch [UART.ino](arduino/UART/UART.ino) to ESP32-C3-MINI-1.
2. Run the Python BLE central script [main.py](central/main.py) on Mac OS X to send 3 packets to ESP32-C3-MINI-1.

In this case, we use [ESP32-C3 SuperMini board](https://docs.zephyrproject.org/latest/boards/others/esp32c3_supermini/doc/index.html) with Mac mini M4, but our custom module can also reproduce this issue.

![](https://docs.zephyrproject.org/latest/_images/esp32c3_supermini.webp)

On Mac OS X, to prepare the Python environment, run:

```bash
$ cd central
$ uv sync
```

Then, run the Python BLE central script:

```bash
$ uv run main.py
```

The python script outputs the sent packets and timestamps on the console, and you can press Ctrl + C to stop the script.

```text
Scanning for BLE device named 'LBUartBLE'...
Found device: C36B5FA0-C008-C7E9-8868-8E10BD0BFBE7
Connected. Sending packets in an infinite loop...
[1786192575020 ms] 0xAA 0xAA 0xAA
[1786192575021 ms] 0xBB 0xBB 0xBB
[1786192575021 ms] 0xCC 0xCC 0xCC
[1786192576022 ms] 0xAA 0xAA 0xAA
[1786192576022 ms] 0xBB 0xBB 0xBB
[1786192576022 ms] 0xCC 0xCC 0xCC
[1786192577024 ms] 0xAA 0xAA 0xAA
[1786192577024 ms] 0xBB 0xBB 0xBB
[1786192577024 ms] 0xCC 0xCC 0xCC
[1786192578026 ms] 0xAA 0xAA 0xAA
[1786192578026 ms] 0xBB 0xBB 0xBB
[1786192578027 ms] 0xCC 0xCC 0xCC
^CCtrl+C detected, stopping sender...
Disconnecting from device...
Shutdown complete.
```

In the Serial Monitor of Arduino IDE, you can see the received packets and timestamps (cpu ticks), that show the received packets are not as expected:

```text
20:16:22.549 -> Started advertising again...
20:36:14.168 -> Device connected
20:36:14.168 -> Notifying Value: 10
20:36:15.086 -> [3931460 ms] Received Bytes (hex): CC CC CC
20:36:15.086 -> [3931461 ms] Received Bytes (hex): CC CC CC
20:36:15.086 -> [3931461 ms] Received Bytes (hex): CC CC CC
20:36:15.151 -> Notifying Value: 11
20:36:16.106 -> [3932450 ms] Received Bytes (hex): CC CC CC
20:36:16.106 -> [3932451 ms] Received Bytes (hex): CC CC CC
20:36:16.106 -> [3932451 ms] Received Bytes (hex): CC CC CC
20:36:16.172 -> Notifying Value: 12
20:36:17.094 -> [3933440 ms] Received Bytes (hex): CC CC CC
20:36:17.094 -> [3933441 ms] Received Bytes (hex): CC CC CC
20:36:17.094 -> [3933441 ms] Received Bytes (hex): CC CC CC
20:36:17.159 -> Notifying Value: 13
20:36:18.110 -> [3934460 ms] Received Bytes (hex): CC CC CC
20:36:18.110 -> [3934461 ms] Received Bytes (hex): CC CC CC
20:36:18.110 -> [3934461 ms] Received Bytes (hex): CC CC CC
20:36:18.175 -> Notifying Value: 14
20:36:18.439 -> Device disconnected
20:36:19.687 -> Started advertising again...
```

If you run the python script with BLE with-response option, the ESP32-C3-MINI-1 can receive correct data contents:

```bash
$ uv run main.py --with-rsp
```

```text
20:36:19.687 -> Started advertising again...
20:40:43.752 -> Device connected
20:40:43.752 -> Notifying Value: 15
20:40:44.671 -> [4200987 ms] Received Bytes (hex): AA AA AA
20:40:44.737 -> [4201047 ms] Received Bytes (hex): BB BB BB
20:40:44.737 -> Notifying Value: 16
20:40:44.803 -> [4201107 ms] Received Bytes (hex): CC CC CC
20:40:45.758 -> Notifying Value: 17
20:40:45.855 -> [4202157 ms] Received Bytes (hex): AA AA AA
20:40:45.921 -> [4202217 ms] Received Bytes (hex): BB BB BB
20:40:45.953 -> [4202277 ms] Received Bytes (hex): CC CC CC
20:40:46.741 -> Notifying Value: 18
20:40:47.004 -> [4203327 ms] Received Bytes (hex): AA AA AA
20:40:47.071 -> [4203387 ms] Received Bytes (hex): BB BB BB
20:40:47.138 -> [4203447 ms] Received Bytes (hex): CC CC CC
20:40:47.762 -> Notifying Value: 19
20:40:47.926 -> Device disconnected
20:40:49.237 -> Started advertising again...
```

Or, you can add some delay between each writeCharacteristic() at Central device, and ESP32-C3-MINI can receives correct contents:

```bash
$ uv run main.py --delay 80
```

```text
0:40:49.237 -> Started advertising again...
20:42:04.092 -> Device connected
20:42:04.092 -> Notifying Value: 20
20:42:04.981 -> [4281298 ms] Received Bytes (hex): AA AA AA
20:42:05.045 -> [4281358 ms] Received Bytes (hex): BB BB BB
20:42:05.079 -> Notifying Value: 21
20:42:05.145 -> [4281448 ms] Received Bytes (hex): CC CC CC
20:42:06.099 -> Notifying Value: 22
20:42:06.230 -> [4282528 ms] Received Bytes (hex): AA AA AA
20:42:06.295 -> [4282618 ms] Received Bytes (hex): BB BB BB
20:42:06.393 -> [4282708 ms] Received Bytes (hex): CC CC CC
20:42:07.080 -> Notifying Value: 23
20:42:07.476 -> [4283788 ms] Received Bytes (hex): AA AA AA
20:42:07.542 -> [4283848 ms] Received Bytes (hex): BB BB BB
20:42:07.641 -> [4283938 ms] Received Bytes (hex): CC CC CC
20:42:08.101 -> Notifying Value: 24
20:42:08.101 -> Device disconnected
20:42:09.581 -> Started advertising again...
```

Unfortunately, we cannot add delays at Central device since those BLE central devices were shipped. And, with the unmodified central devices, our early-generation of BLE module based on nRF51822 can receive correct data contents, but ESP32-C3-MINI-1 cannot. So, we need to find a solution on ESP32-C3-MINI-1 side.