<h1 align="center">
  Music LED Strip Control (MLSC)
</h1>

<p align="center">
    <img src="https://user-images.githubusercontent.com/24798198/107574531-1d6d7300-6bef-11eb-8d7f-83c42a5784d2.png" alt="Logo" />
</p>

<p align="center">
  <a style="text-decoration:none" href="https://www.python.org/downloads/release/python-3919/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg?color=3498DB&style=flat-square" alt="Python Version" />
  </a>
  <a style="text-decoration:none" href="https://discord.gg/bMmWYGcz/">
    <img src="https://img.shields.io/discord/774182494277992478?color=3498DB&style=flat-square&label=discord" alt="Discord" />
  </a>
  <a style="text-decoration:none" href="https://github.com/TobKra96/music_led_strip_control/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/TobKra96/music_led_strip_control?color=3498DB&style=flat-square" alt="GitHub" />
  </a>
</p>


<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#installing">Installing</a>
      <ul>
        <li><a href="#automated-installation">Automated installation</a></li>
      </ul>
    </li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


## Features

- 🎵 Audio visualization in real time.
- ✨ Modern web interface.
- 📝 REST API with extensive documentation using SwaggerUI.
- 🔒 Optional dashboard PIN lock.
- 📈 System status dashboard.
- 💡 27 effects with many configuration options.
- 🎨 Customizable colors and color schemes.
- ⚡ Multicore optimized for large LED strips (900+ LEDs).
- 🖥️ Multi-device support.
- 🎙️ Standalone and client compatible for audio processing.


## Installing

Please check if your hardware is listed inside the [Compatible Hardware List](https://github.com/TobKra96/music_led_strip_control/wiki/Compatible-Hardware-List).

# Music LED Strip Control: Raspberry Pi 4B + ESP8266

## Updated for Raspberry Pi OS Lite 64-bit — Debian 13 (Trixie)

These instructions replace the Raspberry Pi/ESP8266 networking portion of the original Music LED Strip Control (MLSC) Installation Guide.

They assume the following architecture:

```text
                       Home LAN
                          │
                          │ Ethernet
                          │
                  ┌───────┴────────┐
                  │ Raspberry Pi 4B │
                  │                 │
                  │ eth0 = Home LAN │
                  │ wlan0 = AP      │
                  │ 172.24.26.1     │
                  └───────┬────────┘
                          │
                   MLSC-Wifi
                    2.4 GHz
                          │
              ┌───────────┴──────────┐
              │                      │
       ESP8266 #1              ESP8266 #2
       172.24.26.10            172.24.26.11
       UDP 7777                UDP 7777
              │                      │
          LED strip               LED strip
```

The Raspberry Pi runs the MLSC server and web interface. Ethernet connects the Pi to your normal network, while its built-in Wi-Fi is dedicated to the ESP8266 clients.

**Important:** perform the hotspot setup while connected to the Raspberry Pi through **Ethernet**, not through `wlan0`. Turning `wlan0` into an access point will disconnect any SSH session using Wi-Fi.

---

# 1. Install Raspberry Pi OS

Use Raspberry Pi Imager to install:

**Raspberry Pi OS Lite (64-bit)**  
Debian 13 / Trixie  
Release: September 15, 2026

The official image uses the 64-bit ARM architecture and Linux 6.18.

In Raspberry Pi Imager's customization screen, configure:

- Hostname, for example `mlsc`
- Username and password
- Enable SSH
- Your timezone
- WLAN country

You do **not** need to configure your normal Wi-Fi network if you will use Ethernet. Keeping `wlan0` unused makes the later hotspot configuration simpler.

Insert the card, connect Ethernet, and boot the Pi.

SSH into it:

```bash
ssh <username>@mlsc.local
```

or use its Ethernet IP address.

---

# 2. Verify Trixie and update the system

Check the OS:

```bash
cat /etc/os-release
```

You should see Debian/Trixie information.

Check the architecture:

```bash
uname -m
```

Expected:

```text
aarch64
```

Check the kernel:

```bash
uname -r
```

A current September 2026 image should be based on the Raspberry Pi 6.18 kernel series.

Update everything:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Reconnect over Ethernet after the reboot.

---

# 3. Set the wireless regulatory country

Wi-Fi can remain disabled or partially restricted until Raspberry Pi OS knows which country's radio rules to use.

Interactive method:

```bash
sudo raspi-config
```

Select:

```text
Localisation Options
    WLAN Country
```

and select your country.

Alternatively:

```bash
sudo raspi-config nonint do_wifi_country US
```

Replace `US` with the appropriate two-letter country code.

Then verify Wi-Fi exists:

```bash
nmcli device status
```

You should see something similar to:

```text
DEVICE  TYPE      STATE         CONNECTION
eth0    ethernet  connected     Wired connection 1
wlan0   wifi      disconnected  --
lo      loopback  connected     lo
```

---

# 4. Install supporting network packages

Raspberry Pi OS Trixie uses NetworkManager instead of the old `dhcpcd` networking system. NetworkManager 1.52 supports both hotspot mode and configurable DHCP ranges.

Install the helper packages NetworkManager uses for connection sharing:

```bash
sudo apt install -y curl ca-certificates dnsmasq-base iptables
```

Do **not** install or configure the standalone `dnsmasq` service.

Do **not** install or configure `hostapd`.

Do **not** edit:

```text
/etc/dhcpcd.conf
/etc/wpa_supplicant/wpa_supplicant.conf
/etc/dnsmasq.conf
/etc/default/hostapd
```

Those instructions belong to the older Raspberry Pi OS networking stack.

---

# 5. Install Music LED Strip Control

The current MLSC installer has changed substantially from the old wiki version. In particular, it explicitly refuses to run as root and now creates a Python virtual environment at `/share/.venv`. It also installs PyAudio from the Debian package and manages the remaining Python dependencies with `uv`.

Therefore, **do not use the old wiki command containing `sudo bash`.**

Run:

```bash
curl -sSL https://raw.githubusercontent.com/TobKra96/music_led_strip_control/master/setup.sh | bash -s -- -b master
```

Do not add `sudo` before `bash`.

The current installer creates:

```text
/share/music_led_strip_control
/share/.venv
```

and installs a systemd service:

```text
mlsc.service
```

The current project requirements include modern Flask, NumPy, SciPy, `rpi_ws281x`, and other updated dependencies; Trixie's default Python is Python 3.13.

When installation completes:

```bash
sudo reboot
```

---

# 6. Verify MLSC

After reboot:

```bash
sudo systemctl status mlsc.service
```

If it is not running:

```bash
sudo systemctl enable --now mlsc.service
```

View recent log messages with:

```bash
sudo journalctl -u mlsc.service -n 100 --no-pager
```

For live logs:

```bash
sudo journalctl -u mlsc.service -f
```

---

# 7. Determine the Pi's Ethernet address

Run:

```bash
ip -4 -br addr show eth0
```

For example:

```text
eth0    UP    192.168.1.50/24
```

In that example, open the MLSC interface from another computer at:

```text
http://192.168.1.50:8080
```

You can also try:

```text
http://mlsc.local:8080
```

The MLSC web server uses port `8080` by default.

---

# 8. Configure the audio input

Connect your USB microphone or USB audio adapter before configuring MLSC.

To see ALSA devices:

```bash
arecord -l
```

You can also temporarily run MLSC interactively to see exactly which audio sources it detects.

First stop the service:

```bash
sudo systemctl stop mlsc.service
```

Then:

```bash
cd /share/music_led_strip_control/server
sudo /share/.venv/bin/python main.py
```

**Do not use:**

```bash
sudo python3 main.py
```

Using `/share/.venv/bin/python` ensures you run MLSC with the dependencies installed by the current setup script.

The console will show the detected audio sources.

Open:

```text
http://<ETHERNET-IP>:8080
```

Go to **General Settings**, select the appropriate audio device, and set the sample rate reported by MLSC—commonly:

```text
44100
```

Save the configuration.

Stop the foreground process with:

```text
Ctrl+C
```

Then restart the system service:

```bash
sudo systemctl start mlsc.service
```

The original guide's audio-device selection procedure remains applicable.

---

# 9. Create the dedicated ESP8266 Wi-Fi network

This replaces the old `dhcpcd + dnsmasq + hostapd` instructions.

We will create:

```text
SSID:             MLSC-Wifi
Raspberry Pi IP:  172.24.26.1
Subnet:           172.24.26.0/24
ESP static range: 172.24.26.10 - 172.24.26.99
DHCP range:       172.24.26.100 - 172.24.26.200
```

Separating the static ESP addresses from the DHCP pool prevents a DHCP client from accidentally receiving the ESP8266's address.

NetworkManager 1.52 supports setting a custom DHCP range specifically for shared connections.

## Check for an existing Wi-Fi connection

Run:

```bash
nmcli connection show
```

If `wlan0` is currently connected to your normal Wi-Fi network, disconnect that connection before continuing.

For example:

```bash
sudo nmcli connection down "My Home WiFi"
```

If you don't want it competing with the MLSC hotspot at boot:

```bash
sudo nmcli connection modify "My Home WiFi" connection.autoconnect no
```

Use the actual connection name displayed by `nmcli connection show`.

Again, make sure you're connected to the Pi over Ethernet before doing this.

---

# 10. Enable Wi-Fi

Run:

```bash
sudo nmcli radio wifi on
```

Verify:

```bash
nmcli radio wifi
```

Expected:

```text
enabled
```

---

# 11. Create the MLSC hotspot

Choose a strong Wi-Fi password of at least 8 characters.

For example:

```bash
sudo nmcli device wifi hotspot \
  ifname wlan0 \
  con-name MLSC-Hotspot \
  ssid MLSC-Wifi \
  band bg \
  channel 1 \
  password 'CHANGE-THIS-PASSWORD'
```

`band bg` is important because ESP8266 hardware operates in the 2.4 GHz Wi-Fi band.

The Raspberry Pi documentation now recommends `nmcli device wifi hotspot` for creating a hosted Wi-Fi network on current Raspberry Pi OS.

---

# 12. Give the hotspot the MLSC address

Configure the Pi's wireless interface as:

```text
172.24.26.1/24
```

Run:

```bash
sudo nmcli connection modify MLSC-Hotspot \
  connection.autoconnect yes \
  connection.autoconnect-priority 100 \
  ipv4.method shared \
  ipv4.addresses 172.24.26.1/24 \
  ipv4.shared-dhcp-range 172.24.26.100,172.24.26.200 \
  ipv6.method disabled
```

NetworkManager's `shared` mode automatically creates DHCP/DNS service for the Wi-Fi clients and handles the necessary packet forwarding.

---

# 13. Force ESP8266-compatible Wi-Fi security

For maximum compatibility with the ESP8266, configure conventional WPA2-PSK/CCMP rather than requiring WPA3 or Protected Management Frames:

```bash
sudo nmcli connection modify MLSC-Hotspot \
  802-11-wireless-security.key-mgmt wpa-psk \
  802-11-wireless-security.proto rsn \
  802-11-wireless-security.pairwise ccmp \
  802-11-wireless-security.pmf disable
```

NetworkManager supports explicitly selecting RSN/WPA2, CCMP, and the PMF policy.

Restart the hotspot so all changes take effect:

```bash
sudo nmcli connection down MLSC-Hotspot
sudo nmcli connection up MLSC-Hotspot
```

---

# 14. Verify the Raspberry Pi access point

Run:

```bash
ip -4 addr show wlan0
```

You should see:

```text
inet 172.24.26.1/24
```

Also check:

```bash
nmcli connection show --active
```

You should see both:

```text
Wired connection 1
MLSC-Hotspot
```

Verify the hotspot settings:

```bash
nmcli connection show MLSC-Hotspot
```

The important values are:

```text
802-11-wireless.ssid:        MLSC-Wifi
802-11-wireless.mode:        ap
802-11-wireless.band:        bg
ipv4.method:                 shared
ipv4.addresses:              172.24.26.1/24
ipv4.shared-dhcp-range:      172.24.26.100,172.24.26.200
```

At this point a phone or laptop should be able to see:

```text
MLSC-Wifi
```

You don't need to use that network for normal administration—it exists primarily for the ESP8266 devices.

---

# 15. Prepare the ESP8266 development environment

On the computer you'll use to flash the ESP8266, install Arduino IDE.

In Arduino IDE, open **Preferences** and add this Additional Boards Manager URL:

```text
https://arduino.esp8266.com/stable/package_esp8266com_index.json
```

The HTTPS URL above is the current URL recommended by the ESP8266 Arduino project.

Open **Boards Manager**, search for:

```text
esp8266
```

and install the ESP8266 platform.

Then select your actual ESP8266 board. For many NodeMCU boards this is:

```text
NodeMCU 1.0 (ESP-12E Module)
```

but select the entry that matches your hardware.

---

# 16. Install NeoPixelBus

In Arduino IDE open **Library Manager** and search for:

```text
NeoPixelBus
```

Install:

```text
NeoPixelBus by Makuna
```

This is also the installation method recommended by the current NeoPixelBus project.

`ESP8266WiFi` and `WiFiUdp` are supplied by the ESP8266 Arduino core, so they do not normally need to be installed as independent libraries.

---

# 17. Open the MLSC ESP8266 firmware

Use the MLSC sketch:

```text
client/udp/esp/nodemcu_client/nodemcu_client.ino
```

from the `music_led_strip_control` repository.

The original MLSC ESP client uses UDP and listens on:

```text
7777
```

by default.

---

# 18. Configure the ESP8266

Edit the sketch.

Set the correct number of LEDs:

```cpp
#define NUM_LEDS 284
```

Replace `284` with your LED count.

Set the hotspot credentials:

```cpp
const char* ssid = "MLSC-Wifi";
const char* password = "CHANGE-THIS-PASSWORD";
```

The password must exactly match the password used when creating the NetworkManager hotspot.

Leave the UDP port at:

```cpp
unsigned int localPort = 7777;
```

Set the first ESP8266 to:

```cpp
IPAddress ip(172, 24, 26, 10);
IPAddress gateway(172, 24, 26, 1);
IPAddress subnet(255, 255, 255, 0);
```

For additional ESP8266 controllers, use:

```text
ESP #1    172.24.26.10
ESP #2    172.24.26.11
ESP #3    172.24.26.12
ESP #4    172.24.26.13
...
```

Keep these below `.100`, because `.100` through `.200` are reserved for NetworkManager's DHCP pool.

The resulting network configuration for ESP #1 is therefore:

```text
SSID:       MLSC-Wifi
ESP IP:     172.24.26.10
Gateway:    172.24.26.1
Subnet:     255.255.255.0
UDP port:   7777
```

The original MLSC firmware deliberately uses a static ESP address so the Raspberry Pi always knows where to send LED data.

---

# 19. Flash the ESP8266

Connect the ESP8266 over USB.

Select the correct:

```text
Tools → Board
Tools → Port
```

Compile and upload the sketch.

Open Serial Monitor at:

```text
115200 baud
```

After booting, you should eventually see that the ESP8266 connected to:

```text
MLSC-Wifi
```

and has the IP address:

```text
172.24.26.10
```

---

# 20. Verify the ESP8266 from the Raspberry Pi

On the Pi:

```bash
ip neigh show dev wlan0
```

Once the ESP8266 is connected, you should see an entry resembling:

```text
172.24.26.10 dev wlan0 lladdr xx:xx:xx:xx:xx:xx REACHABLE
```

Try:

```bash
ping -c 4 172.24.26.10
```

A responding ESP should return replies.

You can also verify the route:

```bash
ip route
```

You should have an entry similar to:

```text
172.24.26.0/24 dev wlan0
```

---

# 21. Configure the ESP8266 as an MLSC output

From a computer on your home network, open:

```text
http://<RASPBERRY-PI-ETHERNET-IP>:8080
```

Go to:

```text
Device Settings
```

Create a new device.

Configure it approximately as follows:

```text
Name:                 ESP8266 LED Strip
Max FPS:              60
LED Count:            <your number of LEDs>
Selected Output Type: Output Network via UDP
IP Address:           172.24.26.10
Port:                 7777
```

Save the device.

The original MLSC documentation specifies **Output Network via UDP**, the ESP IP address, and UDP port `7777` for this configuration.

Return to the dashboard and select an LED effect.

MLSC should now transmit the LED frames:

```text
Raspberry Pi
172.24.26.1
       │
       │ UDP :7777
       ▼
ESP8266
172.24.26.10
       │
       ▼
LED strip
```

---

# 22. ESP8266 LED data wiring

The existing MLSC ESP8266 firmware expects the LED data signal on **GPIO 3 / RX**.

The original MLSC guide specifies GPIO 3, and current NeoPixelBus documentation notes that its ESP8266 DMA implementation uses GPIO3 regardless of the nominal pin argument.

Typical connections are:

```text
ESP8266 GND ─────────── LED power supply GND
       │
       └─────────────── LED strip GND

ESP8266 GPIO3/RX ────── LED strip DATA IN
```

The ESP8266, LED strip, and LED power supply must share a common ground.

Do **not** power a large LED strip through the ESP8266.

For a 5 V WS2812/WS281x installation, a proper 3.3 V-to-5 V logic-level shifter on the data line is preferable for reliable operation.

---

# 23. Verify that MLSC is actually sending UDP packets

For troubleshooting, install `tcpdump`:

```bash
sudo apt install -y tcpdump
```

Then run:

```bash
sudo tcpdump -ni wlan0 udp and host 172.24.26.10 and port 7777
```

Now activate an effect in MLSC.

If everything on the Raspberry Pi side is working, you should see continuous packets such as:

```text
172.24.26.1.xxxxx > 172.24.26.10.7777: UDP
```

This gives you a very useful dividing line when debugging:

```text
Packets visible in tcpdump
        │
        ├── YES → Pi/network/MLSC are probably working.
        │         Check ESP firmware, LED pin, ground,
        │         level shifting, and power.
        │
        └── NO  → Check MLSC output IP, port,
                  selected device, and MLSC logs.
```

---

# 24. Useful troubleshooting commands

### Check NetworkManager

```bash
systemctl status NetworkManager
```

### Check the hotspot

```bash
nmcli connection show MLSC-Hotspot
```

### Check active network interfaces

```bash
nmcli device status
```

### Check the Pi's Wi-Fi address

```bash
ip -4 addr show wlan0
```

Expected:

```text
172.24.26.1/24
```

### Check connected/recent Wi-Fi neighbors

```bash
ip neigh show dev wlan0
```

### Check whether Wi-Fi is blocked

```bash
rfkill
```

If necessary:

```bash
sudo rfkill unblock wifi
```

### Check NetworkManager logs

```bash
sudo journalctl -u NetworkManager -n 100 --no-pager
```

### Check MLSC

```bash
sudo systemctl status mlsc.service
```

### Check MLSC logs

```bash
sudo journalctl -u mlsc.service -n 100 --no-pager
```

### Restart the hotspot

```bash
sudo nmcli connection down MLSC-Hotspot
sudo nmcli connection up MLSC-Hotspot
```

### Restart MLSC

```bash
sudo systemctl restart mlsc.service
```

---

# 25. Common problems

## ESP8266 cannot see `MLSC-Wifi`

Confirm:

```bash
nmcli connection show --active
```

and:

```bash
ip -4 addr show wlan0
```

Make sure the hotspot is using:

```text
band = bg
```

The ESP8266 operates on 2.4 GHz, not 5 GHz.

If necessary, try Wi-Fi channels 1, 6, or 11.

For example:

```bash
sudo nmcli connection modify MLSC-Hotspot 802-11-wireless.channel 6
sudo nmcli connection down MLSC-Hotspot
sudo nmcli connection up MLSC-Hotspot
```

---

## ESP sees the network but cannot connect

Verify that the SSID and password in the Arduino sketch exactly match the NetworkManager configuration.

Check that the hotspot uses:

```text
WPA-PSK
RSN/WPA2
CCMP
PMF disabled
```

---

## ESP connects but has the wrong IP

Because the MLSC sketch calls `WiFi.config()` with a static address, verify:

```cpp
IPAddress ip(172, 24, 26, 10);
IPAddress gateway(172, 24, 26, 1);
IPAddress subnet(255, 255, 255, 0);
```

Also make certain no two ESP8266 devices use the same static address.

---

## ESP connects but LEDs do nothing

First verify UDP traffic:

```bash
sudo tcpdump -ni wlan0 udp port 7777
```

If UDP packets are present, concentrate on:

```text
ESP8266 firmware
NUM_LEDS
GPIO3/RX
common ground
LED power
logic level
LED data direction
NeoPixelBus configuration
```

---

## MLSC does not start after installation

Run:

```bash
sudo journalctl -u mlsc.service -n 100 --no-pager
```

Then test directly with the MLSC virtual environment:

```bash
sudo systemctl stop mlsc.service

cd /share/music_led_strip_control/server

sudo /share/.venv/bin/python main.py
```

Using the virtual environment is important on current Raspberry Pi OS.

---

# Final network configuration

When everything is complete, the system should look like this:

```text
HOME NETWORK
192.168.x.x
     │
     │ Ethernet
     │
     ▼
Raspberry Pi 4B
eth0  = home network address
wlan0 = 172.24.26.1
MLSC Web UI = http://<eth0-address>:8080
     │
     │
     └──── Wi-Fi SSID: MLSC-Wifi
             WPA2
             2.4 GHz
             │
             ├── ESP8266 #1
             │   172.24.26.10
             │   UDP 7777
             │
             ├── ESP8266 #2
             │   172.24.26.11
             │   UDP 7777
             │
             └── ESP8266 #3
                 172.24.26.12
                 UDP 7777
```

The key Trixie-era difference is that **NetworkManager now owns the Raspberry Pi's Wi-Fi access-point configuration**. There should be no need to recreate the old `dhcpcd`, `hostapd`, and standalone `dnsmasq` configuration from the 2021 wiki.

Also, check out the tutorial video I created for the installation:

<p align="center">
  <a style="text-decoration:none" href="https://youtu.be/ShpOVoOpqrQ">
    <img src="https://user-images.githubusercontent.com/24798198/108500735-87051580-72b0-11eb-8841-65f79421277a.png" alt="Tutorial_Github" />
  </a>
</p>

<h2 align="center">
    Setup schematic
</h2>
<p align="center">
  <a style="text-decoration:none" href="https://github.com/TobKra96/music_led_strip_control/wiki/Installation-Guide">
    <img src="https://user-images.githubusercontent.com/24798198/107310140-209c1e00-6a8c-11eb-8bbb-0e99f63e667c.png" alt="Schematic" />
  </a>
</p>


## Demo

<p align="center">
  <a style="text-decoration:none" href="https://youtu.be/DankmP4riOo">
    <img src="https://user-images.githubusercontent.com/24798198/108499122-24127f00-72ae-11eb-8668-7c720f527c46.png" alt="Version2_Github" />
  </a>
  <a style="text-decoration:none" href="https://youtu.be/eUSX9l89th0">
    <img src="https://user-images.githubusercontent.com/24798198/108499722-0abe0280-72af-11eb-9dc1-f37e3df0b0e7.png" alt="Roomtour_Github" />
  </a>
  <a style="text-decoration:none" href="https://youtu.be/jAL1DfeYQI8">
    <img src="https://user-images.githubusercontent.com/24798198/108499975-68eae580-72af-11eb-9115-594b11f503cf.png" alt="Version1_Github" />
  </a>
  <a style="text-decoration:none" href="">
    <img src="https://user-images.githubusercontent.com/24798198/112079905-48999980-8b81-11eb-846f-30a475092874.png" alt="Mockup" />
  </a>
</p>


## Acknowledgements

* [Audio Reactive LED Strip by Scott Lawson](https://github.com/scottlawsonbc/audio-reactive-led-strip)

Thank you for the digital signal processing and some effects. You are the best.

* [rpi_ws281x by Jeremy Garff](https://github.com/jgarff/rpi_ws281x)

Awesome library for the LED output signal. Easy to use.

* [Flask Datta Able by CodedThemes](https://appseed.us/admin-dashboards/flask-datta-able)

Flask admin dashboard.

Scripts included:

[Bootstrap](https://getbootstrap.com/docs/4.6/),
[jQuery](https://jquery.com/),
[jQuery-Scrollbar](https://github.com/gromo/jquery.scrollbar/),
[jQuery-UI](https://jqueryui.com/),
[Pickr](https://github.com/Simonwep/pickr),
[Font Awesome](https://fontawesome.com),
[Tagin](https://github.com/erwinheldy/tagin)


## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/TobKra96/music_led_strip_control/blob/master/LICENSE) for more information.
