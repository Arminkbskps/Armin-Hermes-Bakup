---
name: mobile-linux-remote-access
description: "Use when setting up SSH or AI tools on mobile Linux."
category: software-development
---

# Mobile Linux Remote Access & Tooling (Termux, PRoot & Android Debian)

Use this skill when establishing lightweight remote terminal or SSH access, or running developer tooling and AI coding agents on a mobile phone or tablet running Linux (Termux, PRoot, UserLAnd, or Android Debian environments).

## Core Principles & Constraints

1. **Carrier NAT (CGNAT) & No Inbound Ports**:
   - Mobile network carriers (cellular data and home Wi-Fi behind ISP NAT) do not provide public IPv4 addresses.
   - Inbound connections directly to the phone IP fail. Always use an outbound reverse-tunnel mechanism (e.g. `tmate`, `pinggy`, or Cloudflare Tunnel) rather than waiting for direct inbound SSH.

2. **Privilege & Port Restrictions (Ports < 1024)**:
   - PRoot and non-rooted Android environments cannot bind privileged ports (ports below 1024 like port 22) and will throw permission denied errors.
   - For SSH daemons, use lightweight servers on unprivileged ports:
     - Install `dropbear` (RAM footprint < 5MB): `dropbear -p 2222`
     - Reverse forward via SSH: `ssh -R 0:localhost:2222 tcp.pinggy.io`

3. **Zero-Config Web/SSH Tunnel via `tmate` (Fastest & Lightest)**:
   - `tmate` requires no open ports, no port-forwarding, and no passwords.
   - **Critical Pitfall ($TMUX variable inheritance)**:
     Inside Termux or terminal multiplexers, `tmate` refuses to start with:
     `sessions should be nested with care, unset $TMUX to force`
   - **Fix**: Setting `TMUX=` (empty string) in Bash does NOT unset the variable from the environment; it sets it to an empty string `""`, which still trips the nested session check.
   - Always run with `env -u TMUX`:
     ```bash
     env -u TMUX tmate
     ```
   - **Headless One-Liner (Keeps local terminal clean and outputs only the SSH connection string)**:
     ```bash
     env -u TMUX tmate -S /tmp/t.sock new-session -d && env -u TMUX tmate -S /tmp/t.sock wait tmate-ready && env -u TMUX tmate -S /tmp/t.sock display -p '#{tmate_ssh}'
     ```
   - Clean shutdown: `killall tmate`

4. **Web-Based Terminal Tools (sshx.io) Pitfalls on Mobile / Restricted Networks**:
   - `sshx.io` generates a web browser URL (`https://sshx.io/s/...`) rather than standard terminal SSH access, preventing direct CLI scripting from the agent.
   - Its WebSocket relays frequently suffer TCP resets and packet drops on restricted mobile networks. Prefer `tmate` over `sshx`.

5. **Strict Personal Device Non-Intrusive Isolation Rule**:
   - When connected to a user's mobile device or personal machine, observe strict non-destructive isolation:
     - Never list directory trees, open personal files, or make modifications outside the user's explicit instructions.
     - Execute solely the requested commands and report the output.

6. **Running Lightweight AI Coding Agent Web GUIs (Aider / Code-Server) on Mobile**:
   - **Debian 12 (Bookworm) PEP 668 & Package Locks**:
     Debian 12 blocks direct system `pip install` without `--break-system-packages`. Install system prerequisites first:
     ```bash
     apt update && apt install python3 python3-pip python3-venv python-is-python3 -y
     pip install --break-system-packages "aider-chat[gui]"
     ```
     If an `apt` or `dpkg` process was previously interrupted, recover with:
     ```bash
     dpkg --configure -a && apt --fix-broken install -y
     ```
   - **Aider CLI Flag Pitfall**:
     `aider` does NOT have a `--port` CLI argument. Passing `aider --gui --port 8080` errors with:
     `aider: error: unrecognized arguments: --port`
     The web interface is powered by Streamlit (default port `8501`). To bind a custom port, pass it via environment variable:
     ```bash
     STREAMLIT_SERVER_PORT=8080 aider --gui --no-browser
     ```
     If running outside a Git repository, append `--no-git` to bypass repository checks:
     ```bash
     aider --gui --no-browser --no-git
     ```
   - **Local Browser Access**:
     Access the web GUI directly on the device browser at `http://localhost:8501` (or `http://localhost:8080`), avoiding heavy desktop environments or VNC wrappers.
