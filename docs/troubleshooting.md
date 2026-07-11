# Troubleshooting

## `http://footpass.local` doesn't resolve
- Use the IP instead: `hostname -I` → `http://<ip>/`.
- Enable mDNS: `sudo bash scripts/configure-hostname.sh`.
- Some networks block mDNS; the IP always works.

## Port 80 already in use
- Another web server/container holds it. Stop it, or change the proxy port
  mapping in `docker-compose.yml` (`"8080:80"`) and browse `:8080`.

## Containers won't start
```bash
make status
make logs
docker compose ps
```
- `footpass-api` waiting on DB is normal for ~20s on first boot (it runs
  migrations, then serves).

## `/api/health` not healthy
```bash
docker compose logs footpass-api --tail=100
docker compose logs footpass-db --tail=50
```
- Check `.env` has a real `POSTGRES_PASSWORD` (the installer generates one).

## Disk full (small eMMC boards)
```bash
df -h /
docker system df
docker builder prune       # reclaim build cache
```
- Keep `${FOOTPASS_DATA_DIR}` on the largest volume you have.

## Camera not detected
- See [camera-setup.md](camera-setup.md). `make camera-test`.

## Reset everything (keeps images, drops DB)
```bash
make stop
docker volume rm footpass_footpass-db-data   # WARNING: wipes the metadata DB
make start
```

## Rebuild after code changes
```bash
make update      # pull + build + up
```
