# Odoo Custom Module

Description WIP

---

## Deployment Notes

This repository uses a split-configuration architecture with local development on Windows and production on Linux server.

### Local Development Architecture (Windows)

- **`docker-compose.yml`**: Contains standard, production-safe settings.
- **`docker-compose.override.yml`**: Automatically injects `user: root` _only_ on local Windows machines. This prevents Docker Desktop/WSL2 from hitting file-locking permissions when you create new modules via VS Code.
- _Note: The override file is explicitly ignored by Git (`.gitignore`) so it never touches production._

---

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
