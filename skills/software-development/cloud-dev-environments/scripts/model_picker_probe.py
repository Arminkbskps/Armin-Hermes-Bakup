#!/usr/bin/env python3
"""model_picker_probe.py — reproduce EXACTLY what the Hermes Telegram gateway
shows for /model, without touching Telegram.

Runs the picker's real code path (hermes_cli.model_switch_providers.
list_picker_providers, the same call gateway/slash_commands_model.py makes
with max_models=50) against a config.yaml and prints one ROW per provider.

Usage (inside the sandbox that owns the config, gateway venv!):
  /usr/local/lib/hermes-agent/venv/bin/python /tmp/pick.py \\
      /home/user/.hermes/profiles/user2/config.yaml

Diagnosis rule: if the combo is NOT in the ROW output here, it will NOT
appear in /model on Telegram either — check custom_providers: list first
(that is the ONLY section the picker reads; providers.<slug>.models dict
is ignored by the picker). If it IS here but missing on Telegram, the
gateway is reading a different config (wrong profile path / stale process).
"""
import sys
import yaml

cfgp = sys.argv[1]
cfg = yaml.safe_load(open(cfgp, encoding="utf-8"))
try:
    from hermes_cli.config import get_compatible_custom_providers
    custom_provs = get_compatible_custom_providers(cfg)
    src = "helper"
except Exception as e:  # fall back to raw section
    custom_provs = cfg.get("custom_providers")
    src = "fallback:%r" % (e,)
print("SRC:", src)
print("CUSTOM-PROVS:", custom_provs)
user_provs = cfg.get("providers")
m = cfg.get("model") or {}
from hermes_cli.model_switch_providers import list_picker_providers
providers = list_picker_providers(
    current_provider=str(m.get("provider") or "9router"),
    current_base_url="http://127.0.0.1:20128/v1",
    user_providers=user_provs, custom_providers=custom_provs,
    max_models=50, current_model=str(m.get("default") or ""),
    include_moa=False)
for p in providers:
    print("ROW:", p.get("slug"), "|", p.get("name"),
          "| models:", p.get("models"), "| total:", p.get("total_models"))
print("DONE")
