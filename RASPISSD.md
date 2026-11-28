# Install Raspberry Pi OS (64-bit) on a Raspberry Pi 4B with an SSD

Install the latest **Raspberry Pi OS (64-bit)** on a Raspberry Pi 4B and boot it from a USB SSD. The current image, released 6 October 2026, is Debian 13 (Trixie) with the Raspberry Pi Desktop and the 64-bit kernel 6.18 series. A Pi 4B with a bootloader from September 2020 or later can boot from USB with no SD card installed.

## What you need

- Raspberry Pi 4B
- USB SSD, or a 2.5-inch SATA SSD in a USB 3 enclosure or adapter
- Official Raspberry Pi 15 W USB-C power supply (5 V, 3 A)
- Ethernet cable to your network
- Another computer with [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- Optional: a microSD card, only if this Pi 4B has never had its bootloader updated

Use a blue USB 3 port on the Pi. A portable SSD that draws too much power can disconnect under load. If that happens, use a powered enclosure.

## 1. Update an old bootloader

Skip this if the Pi has already booted a recent Raspberry Pi OS. USB boot has been the default since the September 2020 bootloader.

If the board is older, boot once from a microSD card with any current Raspberry Pi OS, then run:

```bash
sudo rpi-eeprom-update
```

If `CURRENT` is older than September 2020, or an update is available:

```bash
sudo rpi-eeprom-update -a
sudo reboot
```

Shut the Pi down and remove the microSD card. Leave it out for the rest of this install. With the default boot order, an inserted SD card is tried before USB.

## 2. Write Raspberry Pi OS (64-bit) to the SSD

1. Connect the SSD to the computer you are using to write the image, not to the Pi.
2. Open Raspberry Pi Imager.
3. Choose **Raspberry Pi 4**.
4. Choose **Raspberry Pi OS (64-bit)**. That is the current desktop image: Debian 13 (Trixie). Do not choose **Raspberry Pi OS (other)**, which lists Lite and Full, or **Raspberry Pi OS (Legacy)**, which is still Debian 12 (Bookworm).
5. Choose the SSD as storage. Confirm the name and size. Imager erases the whole drive. The installed system needs about 6.5 GB.
6. Choose **Next**, then edit the settings:
   - Hostname, for example `mlsc`
   - Username and password
   - Enable SSH
   - Time zone
   - Wi-Fi country
7. Leave the Wi-Fi network blank if this Pi will use Ethernet. That keeps `wlan0` free.
8. Write the image and wait until Imager says you can remove the drive.

## 3. Boot from the SSD

1. Eject the SSD from the computer.
2. Confirm there is no microSD card in the Pi.
3. Plug the SSD into a blue USB 3 port.
4. Connect Ethernet.
5. Connect power.

The first boot resizes the filesystem and can take a few minutes before SSH answers. With a monitor attached, the Raspberry Pi Desktop appears after that resize. A green activity LED that blinks, then settles, usually means the SSD is being read.

Connect from another computer on the same network:

```bash
ssh <username>@mlsc.local
```

If `mlsc.local` does not resolve, use the Pi’s Ethernet address from your router.

## 4. Confirm the OS and the SSD

```bash
cat /etc/os-release
uname -m
uname -r
findmnt -n -o SOURCE /
lsblk -o NAME,TRAN,SIZE,TYPE,MOUNTPOINT,MODEL
```

You want:

- `VERSION_CODENAME=trixie` and a kernel in the 6.18 series
- `uname -m` printing `aarch64`
- `/` mounted from a USB disk such as `/dev/sda2`, with `TRAN` showing `usb`
- no root filesystem on `mmcblk0`

Then update and reboot:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

SSH in again after it comes back.

## 5. Optional: prefer USB when an SD card is also installed

The default order tries the SD card first. Change it only if a card should stay in the slot and the SSD should still win:

```bash
sudo raspi-config
```

Open **Advanced Options** → **Boot Order** → **USB Boot**, finish, and reboot.

That sets `BOOT_ORDER=0xf14`, which is read right to left: USB, then SD card, then repeat. Check it with:

```bash
vcgencmd bootloader_config | grep BOOT_ORDER
```

## If it does not boot

- **No activity, or it never appears on the network.** Remove any microSD card, move the SSD to the other blue USB 3 port, and try another cable or enclosure. Then confirm the bootloader date from step 1.
- **The SSD is slow to power on.** Some drives miss the two-second USB scan. After booting from a temporary SD card, raise the wait:

  ```bash
  sudo -E rpi-eeprom-config --edit
  ```

  Set `USB_MSD_DISCOVER_TIMEOUT=5000` (milliseconds), save, reboot, shut down, remove the SD card, and boot from the SSD again.

- **It boots, then disks vanish or copies stall.** Some USB–SATA adapters fail when Linux enables UAS. Find the adapter’s USB ID with `lsusb`, then add a quirk. For an ID such as `174c:55aa`:

  ```bash
  echo 'usb-storage.quirks=174c:55aa:u' | sudo tee /boot/firmware/cmdline.txt
  ```

  Put that option on the existing single line in `cmdline.txt`, separated by a space. Do not add a new line. Reboot afterward.

- **Random disconnects under load.** The SSD is asking for more current than the Pi can spare. Use a powered enclosure and the official 3 A supply.
