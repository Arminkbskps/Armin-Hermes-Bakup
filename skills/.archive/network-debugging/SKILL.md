---
name: network-debugging
description: "Diagnose high network usage and track down rogue processes."
---

# Network Debugging

Use when a process is consuming high network bandwidth and you need to identify the culprit.

## Diagnostic Steps

1. **Check active connections:**
   Use `netstat -ano | findstr ESTABLISHED` to see current connections and their PIDs.

2. **Map PID to Process:**
   Use `tasklist /FI "PID eq <pid>"` to identify the executable.

3. **Check for proxy/VPN usage:**
   Check if the traffic is routed through a proxy (like xray, v2ray, etc.) which might aggregate traffic from multiple apps.

## Scripts

### `scripts/monitor-network.sh`
Run this script to monitor network usage in real-time.

```bash
#!/bin/bash
echo "Monitoring network connections..."
while true; do
    netstat -ano | findstr ESTABLISHED
    sleep 3
done
```
