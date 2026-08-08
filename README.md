# esp32-c3-mini-defer-write-issue

Contaminated data buffers of Characteristic onWrite() when Central device writes characteristic too frequently


The Bluetooth LE central device sends 3 data packets to ESP32-C3-MINI-1 without delays as following codes:

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

We've tried to add some delays such as 10ms between each writeCharacteristic() at Central device, and ESP32-C3-MINI can receives correct contents. However, we need to keep backward compatibility with BLE central devices since those BLE central devices were shipped, is there any way to resolve this issue?


## Hardware

Both [ESP32-C3 SuperMini board](https://github.com/sidharthmohannair/Tutorial-ESP32-C3-Super-Mini) and our custom module can reproduce this issue.

SuperMini board does not connect GPIOs to any other device / board.



## Real-case

In normal situation, the ESP32-C3 can receive correct data contents from BLE central device as below:

```text
19:15:10.859 -> [119161 ms] Received Bytes (hex): 55 03 F5 02 00 4F
19:15:11.053 -> [119386 ms] Received Bytes (hex): 55 03 E2 00 01 3B

19:15:11.151 -> [119476 ms] Received Bytes (hex): 55 03 F5 02 01 50
19:15:11.382 -> [119702 ms] Received Bytes (hex): 55 03 E2 1F 01 5A

19:15:11.481 -> [119791 ms] Received Bytes (hex): 55 03 F5 02 01 50
19:15:11.710 -> [120016 ms] Received Bytes (hex): 55 03 E2 00 00 3A
```

But, sometimes, the ESP32-C3 receives wrong data contents as below:

```text
19:15:10.859 -> [119161 ms] Received Bytes (hex): 55 03 F5 02 00 4F
19:15:11.053 -> [119386 ms] Received Bytes (hex): 55 03 E2 00 01 3B

19:15:11.151 -> [119476 ms] Received Bytes (hex): 55 03 F5 02 01 50
19:15:11.382 -> [119702 ms] Received Bytes (hex): 55 03 E2 1F 01 5A

19:15:11.481 -> [119791 ms] Received Bytes (hex): 55 03 E2 00 00 3A
19:15:11.710 -> [120016 ms] Received Bytes (hex): 55 03 E2 00 00 3A
```

Note the last two packets are the same, which is not expected. (In this case, the motor is not working properly because the command is not correct.)