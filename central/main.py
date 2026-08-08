import asyncio
import argparse
import signal
import time

from bleak import BleakClient, BleakScanner


TARGET_NAME = "LBUartBLE"
CHAR_UUID = "F681"
PACKETS = [
    bytes([0xAA, 0xAA, 0xAA]),
    bytes([0xBB, 0xBB, 0xBB]),
    bytes([0xCC, 0xCC, 0xCC]),
]


async def run(with_rsp: bool, delay_ms: int) -> None:
    print(f"Scanning for BLE device named '{TARGET_NAME}'...")
    device = await BleakScanner.find_device_by_name(TARGET_NAME, timeout=10.0)
    if device is None:
        raise RuntimeError(f"Could not find BLE device named '{TARGET_NAME}'.")

    print(f"Found device: {device.address}")
    client = BleakClient(device)
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    registered_signals: list[signal.Signals] = []

    def request_shutdown() -> None:
        if not stop_event.is_set():
            print("Ctrl+C detected, stopping sender...")
            stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown)
            registered_signals.append(sig)
        except NotImplementedError:
            pass

    await client.connect()
    print("Connected. Sending packets in an infinite loop...")

    try:
        while not stop_event.is_set():
            for packet in PACKETS:
                if stop_event.is_set():
                    break

                # Writes are issued back-to-back unless a delay is explicitly configured.
                await client.write_gatt_char(CHAR_UUID, packet, response=with_rsp)
                timestamp_ms = time.time_ns() // 1_000_000
                packet_hex = " ".join(f"0x{b:02X}" for b in packet)
                print(f"[{timestamp_ms} ms] {packet_hex}")
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)

            if stop_event.is_set():
                break

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                pass
    finally:
        for sig in registered_signals:
            loop.remove_signal_handler(sig)

        if client.is_connected:
            print("Disconnecting from device...")
            await client.disconnect()
        print("Shutdown complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="BLE packet sender")
    parser.add_argument(
        "--with-rsp",
        action="store_true",
        help="Write with response (sets response=True for write_gatt_char).",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=0,
        metavar="MS",
        help="Delay in milliseconds between each write_gatt_char call (default: 0).",
    )
    args = parser.parse_args()

    if args.delay < 0:
        parser.error("--delay must be >= 0")

    try:
        asyncio.run(run(with_rsp=args.with_rsp, delay_ms=args.delay))
    except KeyboardInterrupt:
        # Fallback for environments where signal handlers are not available.
        print("Interrupted by user.")


if __name__ == "__main__":
    main()
