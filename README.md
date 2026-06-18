# Odoo Custom Module

This is a template project for setting up a split-configuration architecture with local development on Windows and production on Linux server using Docker.

## Deployment Notes

This repository uses a split-configuration architecture with local development on Windows and production on Linux server.

### Local Development Architecture (Windows)

- **`docker-compose.yml`**: Contains standard, production-safe settings.
- **`docker-compose.override.yml`**: Automatically injects `user: root` _only_ on local Windows machines. This prevents Docker Desktop/WSL2 from hitting file-locking permissions when you create new modules via VS Code.
- _Note: The override file is explicitly ignored by Git (`.gitignore`) so it never touches production._

### Production Deployment Steps (Linux Server)

When transferring this repository to a live Linux server, the official Odoo container will automatically drop privileges and run as a secure, limited system user (**`odoo`**, UID `101`).

Because Git does not preserve Linux user ownership, you **must** run the following command sequence on your Linux server immediately after cloning or pulling the repository:

<details><summary><b>Show instructions</b></summary>

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

</details>

## Local Development Troubleshooting (Windows / VS Code)

If your custom Odoo module is not appearing in your web browser interface, execute these checks in your Windows terminal/PowerShell sequentially.

<details><summary><b>Show instructions</b></summary>

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

### Getting Auto-Complete and IntelliSense working locally

If your IDE shows an unresolved reference for `import odoo`, run this command in your PowerShell terminal to pull the framework files into your workspace:

```powershell
docker exec <container_id_or_web> tar -cf /tmp/odoo_core.tar -C /usr/lib/python3/dist-packages odoo && docker cp <container_id_or_web>:/tmp/odoo_core.tar ./odoo_core.tar && tar -xf ./odoo_core.tar -C ./ && mkdir odoo_core -Force && move odoo odoo_core/ && rm ./odoo_core.tar
```

</details>

## Model Change to PostgreSQL Troubleshooting

This guide describes how to configure, structure, and troubleshoot custom Odoo modules inside a Docker environment. It provides a systematic checklist to resolve common development issues like missing database tables, hidden menus, registry synchronization blockages, and Docker container connection errors.

### Standard Module Structural Architecture

Odoo relies on strict file paths and folder names to correctly parse business logic, security parameters, and frontend interfaces. Always adhere to this structural standard:

<details><summary><b>Show file structure</b></summary>

```text
your_module/
├── __init__.py                  # Root initialization file
├── __manifest__.py              # Module manifest (Metadata & file registries)
├── security/
│   └── ir.model.access.csv      # Security groups and Access Control Lists (ACL)
├── models/
│   ├── __init__.py              # Models subdirectory execution mapping
│   └── your_model.py            # Python model definitions (ORM layers)
└── views/
    └── your_model_views.xml     # UI element layouts (Actions, Menus, Windows)
```

</details>

### Proper Architectural Implementations

Double check the logs and see if the web container sends any warning. Here are potential problems:

<details><summary><b>Show problems</b></summary>

#### Python Scope & Initialization Routing

To prevent critical circular dependency errors (`ImportError: cannot import name...`), route module execution through subdirectory layers rather than referencing individual data models at the base folder layer.

**Root Initializer (`your_module/__init__.py`):**

```python
from . import models
```

**Subdirectory Initializer (`your_module/models/__init__.py`):**

```python
from . import your_model
```

#### Naming Conventions & System Mutations

Always write model identifier tags using Odoo's standard dot notation format. Odoo uses this schema for internal module mappings and automatically replaces the dots with underscores when generating PostgreSQL database relations.

```python
from odoo import fields, models

class YourModelClass(models.Model):
    _name = "your.model.name"     # Database table becomes: your_model_name
    _description = "A Clear Human Readable Description"

    name = fields.Char(required=True)
```

#### Security Layer Dependencies

Odoo blocks relational database table generation if a model definition lacks explicit user access configuration. Ensure your access controls strictly follow this framework:

**File Location:** `your_module/security/ir.model.access.csv`

**Syntax Blueprint:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_your_model_name,access.your.model.name,model_your_model_name,,1,1,1,1
```

_(Note: Replace dots in the original model name string with underscores and append the `model_`prefix for the`model*id:id` column).*

</details>

### Systematic Registry Reset & Table Extraction Pipeline

If you modify configuration manifests, secure permissions, or backend Python models while an app is partially loaded, the Odoo schema sync process can crash. This leaves the model without a corresponding PostgreSQL table, often displaying database validation warning loops.

<details><summary><b>Show instructions</b></summary>

#### 1. Initialize the Core Containers

Ensure your active environment stack is running in detached background mode so database networks, engine files, and interface sockets can bind correctly.

```bash
docker compose up -d
```

#### 2. Wipe Stale In-Memory State Trace Registry

Clear corrupted model signatures from the Odoo system tracking layers and reset the core installation status marker for your custom app:

```bash
# Delete the broken database metadata entry
docker compose exec db psql -U odoo -d your_db_name -c "DELETE FROM ir_model WHERE model = 'your.model.name';"

# Revert module status back to a pristine deployment target status
docker compose exec db psql -U odoo -d your_db_name -c "UPDATE ir_module_module SET state='to install' WHERE name='your_module_folder_name';"
```

#### 3. Execute an Explicit Forced Compilation Run

Spin up an isolated initialization instance to bypass interface locks, force-read manifest configurations, and write the underlying PostgreSQL schema directly to disk.

```bash
docker compose run --rm web odoo -d your_db_name -i your_module_folder_name --stop-after-init
```

#### 4. Validate the Database Schema Generation

Query your live running database directly to confirm the engine successfully compiled the target table.

```bash
docker compose exec db psql -U odoo -d your_db_name -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'your_module%';"
```

</details>
