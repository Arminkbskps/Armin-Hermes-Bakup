# HidenCloud Deployment Guide

**HidenCloud** is primarily a game server hosting provider (Minecraft, ARK, Rust, etc.) that also offers a free "Coding" tier. This guide covers deploying the Flask bot-manager panel on HidenCloud's free plan.

## Free Plan Specs

| Resource | Value |
|---|---|
| CPU | 2 vCores |
| RAM | 3 GB |
| Storage | 15 GB SSD |
| OS | Linux (Ubuntu-based container) |
| Access | SSH + web dashboard (`dash.hidencloud.com`) |
| Renewal | Required periodically (free tier) |

## Step-by-Step

### 1. Create a Server
1. Log in to `dash.hidencloud.com`
2. Click **Create Server**
3. Look for a "Coding", "Generic", or "Linux" option. If none exists, create a Minecraft/Game server — the Linux container underneath is still a regular VPS.
4. Note the SSH credentials (IP, port, username, password) shown in the panel.

### 2. SSH In
```bash
ssh <username>@<ip> -p <port>
```

### 3. Install Dependencies
```bash
sudo apt update && sudo apt install python3 python3-pip curl -y
pip3 install flask psutil
```

### 4. Upload the Bot Manager
Three methods:
- **scp** (from local machine): `scp -P <port> bot_manager.py <user>@<ip>:/home/container/`
- **nano + paste**: `nano bot_manager.py`, paste file contents, Ctrl+S, Ctrl+X
- **curl from a raw gist**: `curl -Lo bot_manager.py https://gist.githubusercontent.com/.../raw/...`

### 5. Run
```bash
python3 bot_manager.py
```

If the panel needs a specific port (common on HidenCloud):
```bash
PORT=8080 python3 bot_manager.py
```

### 6. Access
- If HidenCloud gives a public IP: `http://<ip>:<port>`
- If only game ports are open: see "Port Access" below

## Port Access

HidenCloud's free tier is game-server oriented. Port 5000 likely won't be reachable from the internet. Solutions:

### A. Cloudflare Tunnel (Best)
```bash
# Install
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared

# In a second terminal / screen session:
./cloudflared tunnel --url http://localhost:5000
```
Output: `https://<random>.trycloudflare.com` — share this URL.

### B. Port Allocation in Panel
Check the HidenCloud dashboard → **Allocations** or **Ports** tab. You can request additional port mappings.

### C. SSH Tunnel
```bash
# From your local machine:
ssh -L 5000:localhost:5000 <user>@<ip> -p <port>
# Then open http://localhost:5000 on your local browser
```

## Default Credentials
**Change before exposing to the internet:**
```
Panel password: admin123
```
Edit the `PANEL_PASSWORD` variable at the top of `bot_manager.py`.

## Persisting the Panel (keeping it alive)
Use `screen` or `tmux` to keep the panel running after SSH disconnect:
```bash
screen -S panel
python3 bot_manager.py
# Ctrl+A, D to detach
# screen -r panel to reattach
```

Or run in background with nohup:
```bash
nohup python3 bot_manager.py > panel.log 2>&1 &
```
