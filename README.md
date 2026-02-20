
[![GitHub Release](https://img.shields.io/github/v/release/karelWeingart/openprinttag-pn5180-rpi)](https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases)
# OpenPrintTag PN5180 RPi

A Raspberry Pi application for reading OpenPrintTags using the PN5180 NFC reader. This project implements a couple of hooks for which callbacks can be registered. 
These callbacks are implemented and may be used out of box
* Simple console logging.
* MQTT publishing. 
* NeoPixel LED feedback.

## Features

- **OpenPrintTag Reading**: Read OpenPrintTag data (material properties, temperatures, colors, etc.)
- **OpenPrintTag Writing**: Writes bin data from mqtt topic to first tag found.
- **Callback System**: Extensible event-driven architecture for custom handlers
- **Tag Caching**: 120-second cache to reduce redundant reads

## Implemented Callbacks
- **MQTT Publishing**: Publish tag information to an MQTT broker.
- **LED Feedback**: Visual feedback using WS281x NeoPixel LED. In this simple implementation one led indicates various events like Error during reading, Invalid tag. Succesfull reading, progress reading multiple blocks etc.

## Hardware Prerequisites

### Required Components
- **Raspberry Pi** (Tested on rPi zero W 2)
- **PN5180 NFC Reader Module**
- **Jumper wires** for GPIO/SPI connections

### Optional Components
- **WS281x NeoPixel LED** (for visual feedback)

### Wiring Pinout

#### PN5180 NFC Reader to Raspberry Pi

**GPIO Signal Pins (Defined in `src/main.py`):**

| Signal | RPi GPIO | Physical Pin | Purpose |
|--------|----------|--------------|---------|
| RST | GPIO 7 | Pin 26 | Reset signal (active low) |
| BUSY | GPIO 25 | Pin 22 | Busy status output |


**SPI Communication (SPI0 - Default):**

| Signal | RPi GPIO | Physical Pin | Purpose |
|--------|----------|--------------|---------|
| MOSI | GPIO 10 | Pin 19 | SPI Master Out Slave In |
| MISO | GPIO 9 | Pin 21 | SPI Master In Slave Out |
| SCK | GPIO 11 | Pin 23 | SPI Serial Clock |
| NSS | GPIO 8 | Pin 24 | SPI Chip Select |

**Power & Ground:**

| Signal | RPi Pin | Purpose |
|--------|---------|---------|
| VCC (3.3V) | 3.3V (Pin 1/17) | Microcontroller logic supply (SPI communication and digital control circuits) |
| VCC (5V) | 5V (Pin 2/4) | High-power antenna supply (RF amplification and electromagnetic field generation for tag communication) |
| GND | GND (Pin 6/9/14/20/30/34/39) | GND |

**Configuration:**
- SPI Channel: 0 (default/primary)
- SPI Speed: 1,000,000 bps (1 MHz)
- All GPIO connections use pigpio daemon for hardware access
- Refer to `src/main.py` for GPIO configuration details

#### NeoPixel LED (Optional)

| Component | RPi GPIO | Purpose |
|-----------|----------|---------|
| NeoPixel Data | GPIO 18 | LED data signal |
| NeoPixel VCC | 5V | Power |
| NeoPixel GND | GND | Ground |

## System Prerequisites

### Software Requirements
- **Python**: 3.11 or higher
- **Raspberry Pi OS**: Latest version (or compatible Linux distribution)
- **git**: cloning the repository
- **pigpio daemon**: For GPIO hardware access
- **SPI interface**: Enabled on Raspberry Pi
- **MQTT Broker**: needed for writing openprinttag data into tags. 

### System Setup

1. **Enable SPI Interface**:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → SPI → Enable
   ```

2. **Install pigpio**:
   ```bash
   sudo apt-get update
   sudo apt-get install pigpio
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```

3. **Verify pigpio is Running**:
   ```bash
   ps aux | grep pigpiod
   ```

4. **Install MQTT Broker**:
   ```bash
   sudo apt-get install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   ```

## Installation

1. **Install the package by pip**:
   ```bash
   # Get the latest release and install it
   LATEST_RELEASE=$(curl -s https://api.github.com/repos/karelWeingart/openprinttag-pn5180-rpi/releases/latest | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
   sudo pip install https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases/download/${LATEST_RELEASE}/openprinttag_pn5180_rpi-${LATEST_RELEASE#v}-py3-none-any.whl --break-system-packages --force-reinstall
   ```

## Usage

### Running the Application

```bash
sudo openprinttag
```

**Note**: The application must be run with `sudo` (root privileges) due to NeoPixel LED hardware access requirements.

### Expected Output

The application will:
1. Initialize pigpio connection
2. Set GPIO pin modes
3. Register event callbacks
4. Start the NFC reader thread
5. Begin scanning for OpenPrintTags

## Event Callbacks

The application uses an event-driven architecture. Available callbacks:

### Custom Callbacks

Register custom callbacks:
```python
from common.api import register_callback
from common.enum import TagReadEvent

def my_callback(event: EventDto):
    print(f"Event: {event.event_type}")

register_callback(TagReadEvent.TAG_READ, my_callback)
```

## Troubleshooting

### pigpio daemon not running
```
Error: pigpio daemon not running
Solution: sudo systemctl start pigpiod
```

### SPI not enabled
```
Error: Cannot open /dev/spidev0.0
Solution: Use raspi-config to enable SPI interface
```

### NeoPixel LED Not Working
```
Error: board.D18 not found
Solution: Check GPIO pin configuration and Adafruit CircuitPython board support
Error: RuntimeError: ws2811_init failed with code -9 (Failed to create mailbox device)
Solution: install and run the project as a root.
```

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- New features include appropriate callbacks
- Dependencies are documented in `pyproject.toml`

## References

- [PN5180 Documentation](https://www.nxp.com/docs/en/data-sheet/PN5180.pdf)
- [Raspberry Pi GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [OpenPrintTag Specification](https://github.com/prusa3d/openprinttag)
- [MQTT Protocol](https://mqtt.org/)
