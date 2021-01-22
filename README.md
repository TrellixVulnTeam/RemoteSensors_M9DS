# RemoteSensors
SSH monitor for Raspberry Pi

Console based SSH monitor for controlling Raspberry Pi status from remote computers.

Currently monitors:
* Disk space: Monitors de disk space in all mounted devices that are not tmpfs.
* Throttling: Shows throttling status (provided by vcgencmd).
* CPU/GPU temperature (provided by vcgencmd).
* CPU and RAM usage.
* Processes: active and total (provided by vcgencmd).
* Average load last minute, last 5 minutes and last 15 minutes (provided by vcgencmd).
* Current CPU frequency
* Codec information (provided by vcgencmd)

Destination Raspberry Pi needs to have SSH connections enabled.
