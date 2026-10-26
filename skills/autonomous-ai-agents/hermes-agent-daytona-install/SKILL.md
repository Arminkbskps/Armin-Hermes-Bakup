---
name: hermes-agent-daytona-install
description: "Install Hermes from source on Daytona/LXC environments."
version: 1.0.0
---

# Daytona / Blocked IP Hermes Agent Installation

When installing Hermes Agent in a Daytona workspace (e.g. `ssh.app.daytona.io`) or other environments where the primary CDN (`hermes-agent.nousresearch.com` / Vercel DNS) blocks the host IP, the standard `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash` will fail with SSL reset or 404 errors.

## The Workaround (Source Install)

Instead of the shell installer, clone the source and use `uv` directly.
Always use `--depth 1` on `git clone` to avoid long `index-pack` times in container environments:

```bash
# 1. Clone the repository (--depth 1 avoids timeout on git index-pack)
git clone --depth 1 https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 2. Install uv system-wide
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" sh

# 3. Create venv (uv automatically downloads managed Python e.g. 3.14) and install
uv venv
uv pip install --python .venv -e .

# 4. Expose hermes CLI globally and ensure doctor checks pass
sudo ln -sf "$(pwd)/.venv/bin/hermes" /usr/local/bin/hermes
mkdir -p ~/.local/bin && ln -sf "$(pwd)/.venv/bin/hermes" ~/.local/bin/hermes
sudo apt-get update -y && sudo apt-get install -y ripgrep

# 5. Run health check
hermes doctor
```

## Nested QEMU VM in Daytona (Port 2222)

When running a nested Ubuntu cloud VM inside Daytona via QEMU (e.g., `-netdev user,id=net0,hostfwd=tcp::2222-:22`):

1. **Access from Daytona host**:
   ```bash
   sudo apt-get install -y sshpass
   sshpass -p "<password>" ssh -p 2222 ubuntu@127.0.0.1
   ```
2. **Setup passwordless SSH & one-word shortcut**:
   ```bash
   [ -f ~/.ssh/id_rsa ] || ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ''
   sshpass -p "<password>" ssh-copy-id -o StrictHostKeyChecking=no -p 2222 ubuntu@127.0.0.1
   
   # Add helper binary /usr/local/bin/vm
   sudo bash -c 'cat << "EOF" > /usr/local/bin/vm
   #!/bin/bash
   exec ssh -p 2222 -o StrictHostKeyChecking=no ubuntu@127.0.0.1 "$@"
   EOF
   chmod +x /usr/local/bin/vm'
   echo 'alias vm="/usr/local/bin/vm"' >> ~/.bashrc
   echo 'alias vm="/usr/local/bin/vm"' >> ~/.zshrc
   ```
   Now typing `vm` on Daytona immediately lands inside the guest Ubuntu VM.

## Note on Daemons (Daytona/LXC)

Daytona workspaces and LXC containers often do not run `systemd` as PID 1 (`System has not been booted with systemd as init system`). 

Never use `systemctl` in these environments. Manage services (like docker) with standard SysV init scripts:

```bash
service docker start
service docker status
```