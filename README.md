# BenQ ScreenBar HALO 2 · ESPHome radio bridge

[![Validate](https://github.com/Termina1/benq-screenbar-halo2-esphome/actions/workflows/validate.yml/badge.svg)](https://github.com/Termina1/benq-screenbar-halo2-esphome/actions/workflows/validate.yml)

Control a **BenQ ScreenBar HALO 2** from Home Assistant using a **BM5602** radio module and an **M5Stack ATOM Lite**. The bridge supports power, front/back light, both brightness channels, color temperature, lamp mode, ultrasonic presence mode, and state updates from the original wireless controller.

This is working firmware, not a packet-engine mock: transmission is synchronized to the BM5602 `TBCLK` output and uses the stock on-air framing and CRC.

## What works

- Power on/off
- Front and rear light selection
- Front brightness: 1–100
- Rear brightness: 1–100
- Color temperature: 2700–6500 K
- Ultrasonic presence mode
- Passive reception of original-controller state changes
- ESPHome API, OTA, web UI and Home Assistant REST compatibility

## Hardware

- M5Stack ATOM Lite (ESP32)
- BM5602 2.4 GHz transceiver module
- Seven wires, including the required `GIO3/TBCLK` synchronization wire
- Fine soldering tools for BM5602 pin 8

See **[Wiring and soldering](docs/WIRING.md)** before powering the boards.

## Files

| Path | Purpose |
|---|---|
| `screenbar-halo2.yaml` | Production ESPHome configuration |
| `bm5602_halo2.h` | Minimal BM5602 SPI, direct TX, CRC and passive RX driver |
| `secrets.example.yaml` | Safe configuration template |
| `home-assistant/package.yaml` | Optional authenticated REST integration with guarded controller-state synchronization |
| `home-assistant/dashboard.yaml` | Compact stock-card dashboard |
| `home-assistant/secrets.example.yaml` | Matching Home Assistant web credentials |

## Install

### 1. Copy the ESPHome files

Copy these files into the same ESPHome configuration directory:

```text
screenbar-halo2.yaml
bm5602_halo2.h
```

Copy `secrets.example.yaml` to `secrets.yaml` and replace all placeholders. Generate the API key with `openssl rand -base64 32`. Use a unique web password; it protects the control/state endpoints used by the optional HA package. Never commit `secrets.yaml`.

### 2. Flash over USB

```bash
esphome run screenbar-halo2.yaml
```

After boot, the node advertises as:

```text
screenbar-halo2
screenbar-halo2.local
```

Authenticated web UI:

```text
http://screenbar-halo2/
```

Use `web_username` and `web_password` from ESPHome `secrets.yaml`. Web-based firmware upload is disabled; OTA updates use the separately protected native ESPHome OTA service.

Future updates:

```bash
esphome run screenbar-halo2.yaml --device screenbar-halo2
```

### 3. Add to Home Assistant

The simplest option is the native ESPHome integration:

1. Open **Settings → Devices & services → Add integration → ESPHome**.
2. Enter `screenbar-halo2` and port `6053`.
3. Use the exposed switches, numbers, select and buttons directly.

For the included compact dashboard and explicit polling synchronization, copy:

```text
home-assistant/package.yaml   -> config/packages/screenbar_halo2.yaml
home-assistant/dashboard.yaml -> config/dashboards/screenbar_halo2.yaml
```

Merge the two values from `home-assistant/secrets.example.yaml` into Home Assistant's `config/secrets.yaml`. They must match `web_username` and `web_password` in ESPHome.

Enable packages and register the YAML dashboard in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages

lovelace:
  dashboards:
    screenbar-yaml:
      mode: yaml
      title: ScreenBar
      icon: mdi:monitor-shimmer
      show_in_sidebar: true
      filename: dashboards/screenbar_halo2.yaml
```

Validate before restarting:

```bash
ha core check
ha core restart
```

The package accesses authenticated endpoints below `http://screenbar-halo2/...`; no fixed IP is embedded. A synchronization guard prevents received controller state from being echoed back as a new command, and HA startup waits for a valid bridge state instead of overwriting the lamp with restored helper values.

## Radio details

Tested configuration:

```text
Channel:              5 / 2405 MHz
Register address:     9C EA BB 86
Direct air address:   86 BB EA 9C
Data path:            GIO2 / GPIO33
Synchronization:      GIO3 TBCLK / GPIO25
Bit order:            MSB first
Data update edge:     TBCLK low
CRC:                  CRC-CCITT, polynomial 0x1021
CRC initial state:    0xEFDF before the four-byte on-air address
```

The tested lamp uses address `9C EA BB 86`. Other controller/lamp pairs may use a different address. If yours does, update `RADIO_ADDRESS` in `bm5602_halo2.h` only after capturing your own stock traffic; the direct on-air order and post-address CRC state are derived automatically.

### RX state rule

Only even-PID request frames are treated as authoritative controller state. Odd-PID lamp replies are deliberately ignored for synchronization: their control byte is response metadata and can differ from the requested state.

## Reliability notes

- RX polling is deliberately limited to 50 ms. Aggressive synchronous 10 ms FIFO draining can starve ESPHome API, HTTP and OTA while ICMP still appears alive.
- Transmission always returns the BM5602 to passive RX mode.
- Passive RX accepts only exact 13-byte stock requests with a valid CRC and in-range brightness/temperature values.
- The native ESPHome API uses encryption. HTTP control uses unique basic-auth credentials, and web OTA is disabled.
- Local transmission success is not described as a lamp acknowledgement. The implementation was validated using the transmitted frame, an independently received lamp response, and visible lamp reaction.

## Prior art and research

The interoperability work was informed by the public BM5602 examples and by [kuzmin-no/BenQ_ScreenBar_HALO_2_HA_integration](https://github.com/kuzmin-no/BenQ_ScreenBar_HALO_2_HA_integration). This repository provides an independently implemented ESP-IDF/ESPHome C++ direct-mode driver, the recovered framing/CRC behavior, and the Home Assistant integration used by this project.

## Disclaimer

This is an unofficial community project and is not affiliated with or endorsed by BenQ. BenQ and ScreenBar are trademarks of their respective owner. Modifying hardware can damage it and may void its warranty.

## License

MIT. See [LICENSE](LICENSE).
