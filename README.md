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
