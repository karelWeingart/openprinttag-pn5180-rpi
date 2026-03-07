#!/bin/bash
echo "Run pre-installation steps..."
if ! command -v curl &> /dev/null;
then
    echo "curl could not be found. Please install curl and try again."
    exit
fi
if ! command -v mosquitto &> /dev/null;
then
    echo "mosquitto could not be found. Please install mosquitto and try again."
    exit
fi
if ! command -v pigpiod &> /dev/null;
then
    echo "pigpiod could not be found. Please install pigpiod and try again."
    exit
fi
if ! command -v tmux &> /dev/null;
then
    echo "tmux could not be found. Please install tmux and try again."
    exit
fi
if [ ! -e /dev/spidev0.0 ]; then
    echo "SPI device not found. Please enable SPI and reboot."
    exit 1
fi

echo "Create directories for the applications... Cleaning up"
mkdir -p "$HOME"/openprinttag
mkdir -p "$HOME"/openprinttag/logs
rm -rf "$HOME"/openprinttag/logs/*
cd "$HOME"/openprinttag

echo "Installing python packages..."
LATEST_RELEASE=$(curl -s https://api.github.com/repos/karelWeingart/openprinttag-pn5180-rpi/releases/latest | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
echo "Latest release: ${LATEST_RELEASE}"

VERSION=${LATEST_RELEASE#v}
mkdir -p packages
curl -LO "https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases/download/${LATEST_RELEASE}/openprinttag_pn5180_shared-${VERSION}-py3-none-any.whl"
curl -LO "https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases/download/${LATEST_RELEASE}/openprinttag_pn5180_rpi-${VERSION}-py3-none-any.whl"
curl -LO "https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases/download/${LATEST_RELEASE}/openprinttag_pn5180_web_api-${VERSION}-py3-none-any.whl"

echo "Cleaning up old packages..."
sudo pip cache purge
sudo pip uninstall openprinttag-pn5180-shared openprinttag-pn5180-rpi openprinttag-pn5180-web-api -y --break-system-packages

echo "Installing shared package..."
sudo pip install "openprinttag_pn5180_shared-${VERSION}-py3-none-any.whl" --break-system-packages --force-reinstall
echo "Installing RPI package..."
sudo pip install "openprinttag_pn5180_rpi-${VERSION}-py3-none-any.whl" --break-system-packages
echo "Installing Web API package..."
sudo pip install "openprinttag_pn5180_web_api-${VERSION}-py3-none-any.whl" --break-system-packages
    

echo "installing web viewer..."
curl -Lo "openprinttag-web-viewer.tar.gz" "https://github.com/karelWeingart/openprinttag-pn5180-rpi/releases/download/${LATEST_RELEASE}/openprinttag-web-viewer-${LATEST_RELEASE}.tar.gz"
mkdir -p static
tar -xzf openprinttag-web-viewer.tar.gz -C static

echo "Starting web viewer..."
nohup openprinttag_web_backend > "$HOME"/openprinttag/logs/web-api.log 2>&1 &
IP_ADDR=$(hostname -I | awk '{print $1}')
echo "Web API started (PID: $!) — serving on http://${IP_ADDR}:8000"
sleep 5 && head -10 "$HOME"/openprinttag/logs/web-api.log

echo "Starting OpenPrintTag reader service..."
tmux kill-session -t openprinttag 2>/dev/null
tmux new -d -s openprinttag 'sudo openprinttag'

sleep 2
if tmux has-session -t openprinttag 2>/dev/null; then
    echo "OpenPrintTag reader is running in tmux session 'openprinttag'"
else
    echo "ERROR: OpenPrintTag reader failed to start. Check logs."
    exit 1
fi

echo "Installation complete. If any error happened check the logs"
