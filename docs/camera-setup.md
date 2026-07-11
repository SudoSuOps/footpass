# Camera setup

FootPass captures photos **on the ZimaBoard**, using a USB camera connected
directly to it, and streams the preview to your browser. The browser never
requests camera permission — this is deliberate (works on any device, avoids
mobile-browser camera restrictions and local-HTTPS requirements).

## Detect the camera

```bash
make camera-test        # or: bash scripts/detect-camera.sh
```

You should see `/dev/video0` (a USB UVC camera usually also exposes `/dev/video1`
for metadata). For detailed capabilities:

```bash
sudo apt-get install -y v4l-utils
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
```

## Attach the camera to the camera service (Phase 2)

The camera device is mapped into `footpass-camera` in `docker-compose.yml`:

```yaml
footpass-camera:
  devices:
    - "/dev/video0:/dev/video0"
  group_add:
    - "video"
```

(These lines are present as comments in Phase 1 and become active in Phase 2.)

## Configurable settings (Phase 2)

Device index, resolution, focus, exposure, and orientation are exposed via
settings and the first-run flow. MJPEG is the default preview transport for
stability on a LAN; WebRTC is a later option.

## Troubleshooting

- **No `/dev/video*`** — replug the camera; check `dmesg | tail`.
- **Permission denied** — ensure the container has `group_add: ["video"]` and
  the host user is in the `video` group.
- **Busy device** — another app (or a second container) may hold the camera.
