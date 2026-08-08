# BLE Central Sender

This folder contains a Python BLE central script, [main.py](main.py), that:

- Scans for a BLE peripheral by name.
- Connects to the peripheral.
- Writes 3 packets repeatedly to characteristic `F681`:
	- `AA AA AA`
	- `BB BB BB`
	- `CC CC CC`
- Prints a timestamp (milliseconds) before each sent packet.
- Sleeps 1 second after each 3-packet batch.
- Handles Ctrl+C and disconnects gracefully.

## Prerequisites

- Python 3.11+
- BLE enabled on your machine
- The target peripheral advertising with name `LBUartBLE`

Dependencies are defined in [pyproject.toml](pyproject.toml) and include `bleak`.

## Run

From this folder:

```bash
uv run main.py
```

Or with plain Python (if environment already has dependencies):

```bash
python main.py
```

## Options

- `--with-rsp`
	- Use write with response (`response=True`) for `write_gatt_char`.
	- Default is without response (`response=False`).

- `--delay MS`
	- Add a delay between each packet write in a batch.
	- Value is in milliseconds.
	- Default is `0` (no delay).

## Example Commands

No response, no extra write delay:

```bash
uv run main.py
```

Write with response:

```bash
uv run main.py --with-rsp
```

Add 10 ms delay between writes:

```bash
uv run main.py --delay 10
```

Use both options:

```bash
uv run main.py --with-rsp --delay 10
```

## Stop

Press Ctrl+C to stop. The script will:

- stop the send loop,
- disconnect from the BLE device,
- print shutdown messages.
