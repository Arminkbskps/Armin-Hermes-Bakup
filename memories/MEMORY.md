Typst 0.13.0, WeasyPrint 70, poppler-utils (pdftoppm), and Vazirmatn fonts are installed on the system. Python STEM libraries include SymPy, SciPy, NumPy, Matplotlib, Shapely, and ChemPy. Custom STEM skills available: math-geometry-drawer, stem-solver-verified, exam-pdf-typesetter.
§
voidclubs.ir passive baseline Oct 2026: HSTS, SAMEORIGIN, nosniff present; no Content-Security-Policy; robots disallows /api/ /payping/ /tools/ /data/ /account /checkout /login; sitemap.xml and llms.txt public.
§
Daytona host SSD is only 10GB; user forbids bulky installs. Active 30m cron watchdog `disk-space-watchdog` alerts to Telegram when free space <= 10%.
§
Google Drive Web App upload endpoint saved at ~/.config/gdrive/endpoint.txt; CLI helper `gdrive-upload <path>` uploads directly to user's 5TB Drive folder Hermes_Files.
§
Personal agent email address: armin-hermes@agentmail.to (AgentMail). Full send & receive capability, valid for GitHub/services. CLI helper `agentmail send <to> <subject> <body>`, `agentmail check`, `agentmail read`, `agentmail wait <seconds>`. Config at ~/.config/mail/agentmail.json.
§
GitHub account armin-hermes configured with git credential helper (~/.git-credentials) and email armin-hermes@agentmail.to.
§
Cloudflare account armin-hermes@agentmail.to (Account ID: 525732c062f45d7b5c30fc9be7c55f79) configured with API token at ~/.config/cloudflare/credentials.json and GitHub CI/CD on armin-hermes/hermes-showcase deploying to Cloudflare Pages (hermes-showcase.pages.dev).
§
Deployed personal VLESS & Trojan tunnel on Cloudflare Workers at hermes-tunnel.armin-hermes.workers.dev (sub at /sub) via repo armin-hermes/hermes-tunnel with UUID f2fa065d-1dff-468a-a7cb-3faf1352b8ce and Rightel Fragment presets.
§
Hermes 6h backup (`~/scripts/hermes_backup.py`) auto-chunks >20MB archives into multi-part uploads to Google Drive (excludes *.mp3/*.mp4/*.gif/*.wav); disk watchdog script is at `~/.hermes/scripts/disk_watchdog.py`.
§
Standing rule: Never open Gmail, Google Accounts, or *.google.com in a browser or OAuth flow without explicit user permission (prevents bot ban on user's linked Google accounts).