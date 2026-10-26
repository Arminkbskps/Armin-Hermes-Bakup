# Armin Hermes Backup 🛡️

Automated backup repository for **Hermes Agent**.

- **Owner:** [Arminkbskps](https://github.com/Arminkbskps)
- **Target Repo:** `Arminkbskps/Armin-Hermes-Bakup`
- **Last Sync:** 2026-10-26 12:59:17 UTC
- **Sync Interval:** Every 6 hours

---

### 📂 Repository Structure (Main Branch)
- `skills/` — All customized Hermes agent skills & instructions
- `scripts/` — Maintenance, automation & backup scripts
- `memories/` — Core agent persistent memory (`MEMORY.md`, `USER.md`)
- `cron/` — Scheduled jobs configuration (`jobs.json`)
- `config/` — Hermes config and persona definition
- `exam_work/` — Educational materials, solutions & scripts

### 📦 Full System Archives (Releases)
Each 6-hour backup additionally creates a full, standalone compressed `.tar.gz` archive containing all SQLite databases (`state.db`, `kanban.db`, `shared-state.db`), sessions, and runtime states under [Releases](https://github.com/Arminkbskps/Armin-Hermes-Bakup/releases).

#### Quick Restore:
```bash
# Download and unpack full archive (replace URL with release asset):
curl -sL -H "Authorization: token $GITHUB_TOKEN" <RELEASE_ASSET_URL> | tar -xzf - -C /home/daytona
```
