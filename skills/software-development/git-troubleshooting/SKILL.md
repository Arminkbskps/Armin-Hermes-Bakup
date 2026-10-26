---
name: git-troubleshooting
description: "Use for Git network failures and insteadOf proxy issues."
---

# Git Troubleshooting

Use this when standard Git operations (clone, pull, fetch, push) fail due to network, SSL, or host resolution issues.

## Diagnostics

Before applying fixes, always check the applied config to see what rules are affecting the repository:
```bash
git config --list --show-origin
```

## Common Pitfalls and Resolutions

### 1. The `disabled.invalid` Host Error
**Symptom:** `fatal: unable to access 'https://disabled.invalid/...': Could not resolve host: disabled.invalid` (or schannel SSL/TLS handshake failures)
**Cause:** A tool, proxy script, or VPN has injected a global `insteadOf` rule rewriting legitimate URLs (like `https://github.com/`) to a disabled or invalid endpoint.
**Diagnosis:** 
```bash
git config -l | grep invalid
# Expect output like: url.https://disabled.invalid/.insteadof=https://github.com/
```
**Resolution:**
Unset the overriding rule in the global configuration:
```bash
git config --global --unset url."https://disabled.invalid/".insteadOf
```

### 2. SSL/TLS Handshake Failures on Windows (schannel)
**Symptom:** `schannel: failed to receive handshake, SSL/TLS connection failed`
**Cause:** Often caused by active VPNs, corporate proxies intercepting SSL traffic, or conflicts with the Windows Secure Channel (schannel) backend.
**Resolution:** 
- Disable the active proxy/VPN if possible.
- Clear local proxy configs: `git config --global --unset http.proxy` and `git config --global --unset https.proxy`.
- Check for rogue `insteadOf` rules (see above) which can manifest as SSL failures before they manifest as DNS failures depending on the proxy setup.
