# Odoo Custom Module

Description WIP

## Deployment Notes

This repository uses a split-configuration architecture with local development on Windows and production on Linux server.

### Local Development Architecture (Windows)

- **`docker-compose.yml`**: Contains standard, production-safe settings.
- **`docker-compose.override.yml`**: Automatically injects `user: root` _only_ on local Windows machines. This prevents Docker Desktop/WSL2 from hitting file-locking permissions when you create new modules via VS Code.
- _Note: The override file is explicitly ignored by Git (`.gitignore`) so it never touches production._

### Production Deployment Steps (Linux Server)

When transferring this repository to a live Linux server, the official Odoo container will automatically drop privileges and run as a secure, limited system user (**`odoo`**, UID `101`).

Because Git does not preserve Linux user ownership, you **must** run the following command sequence on your Linux server immediately after cloning or pulling the repository:

```bash
# 1. Pull the latest code from GitHub to the server
git pull origin main

# 2. Fix the addons directory ownership to match Odoo's internal non-root user (UID 101)
sudo chown -R 101:101 ./addons

# 3. Secure the folder and file access masks (Folders: 755, Files: 644)
sudo find ./addons -type d -exec chmod 755 {} +
sudo find ./addons -type f -exec chmod 644 {} +

# 4. Start your containers safely in production mode
docker compose up -d
```

If you skip the `chown -R 101:101` step on Linux, the Odoo container will log an `Access Denied` error on startup and fail to scan or load any custom modules inside the `/addons` directory. Running this keeps your server protected; if the container is ever compromised, attackers cannot break out into your host system root files.

## Local Development Troubleshooting (Windows / VS Code)

If your custom Odoo module is not appearing in your web browser interface, execute these checks in your Windows terminal/PowerShell sequentially.

### Verify Module Files Presence inside Docker

Ensure Docker Desktop actually mirrors your local Windows directory into the Linux container:

```bash
docker compose exec -it web ls -la /mnt/extra-addons/your_module_name
```

**What to check:** Verify that `__init__.py` and `__manifest__.py` are visible and their file sizes are **greater than 0 bytes**. Empty files will cause Odoo to ignore the entire directory.

### Fix Windows Line Endings (CRLF to LF)

Windows automatically saves files with `CRLF` formatting, which crashes Linux configurations.

**The Fix:** Open your `__manifest__.py` and `__init__.py` files inside VS Code. Look at the bottom-right status bar. If it says **`CRLF`**, click it, switch it to **`LF`**, and re-save the file.

### Check Odoo Configuration Addons Path

If you are using a custom `odoo.conf` file, ensure your mounted folder path is explicitly appended:

```bash
docker compose exec -it web cat /etc/odoo/odoo.conf
```

**The Line to verify:** `addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons`
_Note: The official Odoo image functions perfectly without a physical config file, auto-resolving to `/mnt/extra-addons` by default._

### Trigger Discovery in Odoo UI

Odoo does not auto-scan files during runtime. Force an application list update:

1. Navigate to **Settings** → scroll down and click **Activate the developer mode**.
2. Go to the **Apps** dashboard menu.
3. Click on **Update Apps List** in the top navigation bar, then confirm by clicking **Update**.
4. Clear the default `Apps` search filter query in the search input box and search for your technical module name.
