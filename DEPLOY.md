# Deploying AI Workspace Pro

Start here: **Streamlit Community Cloud** if you want it public and free in ten
minutes. Use **Docker on a VPS** if you need the SQLite data to survive restarts.

---

## 1. Streamlit Community Cloud (free, recommended)

Free tier: 1 GB RAM, public repos, app sleeps after inactivity and wakes on visit.

1. Push the project to a **public** GitHub repo:

   ```bash
   cd ai_workspace_pro
   git init && git add . && git commit -m "AI Workspace Pro"
   git branch -M main
   git remote add origin https://github.com/<you>/ai-workspace-pro.git
   git push -u origin main
   ```

   Confirm `.env` and `.streamlit/secrets.toml` are **not** in the commit —
   `.gitignore` already excludes them.

2. Go to share.streamlit.io → **New app** → pick the repo, branch `main`,
   main file `app.py`.

3. Open **Advanced settings → Secrets** and paste:

   ```toml
   GEMINI_API_KEY = "your_key_here"
   GEMINI_MODEL = "gemini-3.6-flash"
   ```

4. Deploy. `packages.txt` installs Tesseract automatically, so OCR works.

**Memory note:** `faiss-cpu` plus Streamlit is tight on the 1 GB tier. If the
build gets killed, delete the `faiss-cpu` line from `requirements.txt` — PDF Chat
falls back to the scikit-learn search path with no code changes.

**Storage note:** the filesystem is ephemeral. Stats and planner tasks reset
whenever the app restarts. Fine for a demo; see option 3 for persistence.

---

## 2. Hugging Face Spaces (free, no sleep)

1. Create a Space → SDK **Streamlit** → clone it locally.
2. Copy the project files in, keeping `requirements.txt` and `packages.txt` at
   the root. Rename `app.py` to `app.py` (already the expected entrypoint).
3. Add `GEMINI_API_KEY` under **Settings → Variables and secrets → New secret**.
4. `git push`. The Space builds and serves itself.

Same ephemeral-storage caveat as Streamlit Cloud.

---

## 3. Docker on a VPS (persistent data, full control)

Works on any host with Docker — DigitalOcean, Hetzner, Linode, EC2, your own box.

```bash
export GEMINI_API_KEY=your_key_here
docker compose up -d --build
```

The app is on port 8501, and `./data` is mounted as a volume so the SQLite
database survives rebuilds.

Put Caddy in front for HTTPS on your own domain:

```
# /etc/caddy/Caddyfile
workspace.yourdomain.com {
    reverse_proxy localhost:8501
}
```

Caddy provisions the TLS certificate automatically. Then restrict 8501 to
localhost in `docker-compose.yml` (`"127.0.0.1:8501:8501"`) so it's only
reachable through the proxy.

---

## 4. Render / Railway / Fly.io

All three detect the `Dockerfile` and need no extra config.

- **Render** — New → Web Service → connect repo → runtime Docker. Add
  `GEMINI_API_KEY` as an environment variable. Attach a Disk mounted at
  `/app/data` if you want persistence. Free instances spin down when idle.
- **Railway** — New Project → Deploy from GitHub. Add the variable, attach a
  Volume at `/app/data`. Usage-based pricing.
- **Fly.io** — `fly launch` (it reads the Dockerfile), then
  `fly secrets set GEMINI_API_KEY=...` and `fly volumes create data` mounted at
  `/app/data`.

---

## Before you go live

- **Never commit the key.** It belongs in the platform's secrets UI. Users can
  also paste their own key in Settings, which keeps it in their session only.
- **Set a quota.** In Google AI Studio, cap spending on the key — a public app
  means anyone's requests bill to you. Or ship it key-less and require each
  visitor to enter their own in Settings.
- **Upload limit.** `.streamlit/config.toml` caps uploads at 50 MB. Lower it on
  small instances: large PDFs get chunked and vectorized in RAM.
- **SQLite and concurrency.** Fine for tens of simultaneous users. Beyond that,
  swap `core/db.py` for Postgres — the module boundary is already clean, so only
  the connection helper and SQL dialect change.
- **Test the no-key path.** Load the deployed app before adding the secret and
  confirm every page still renders. That's your failure mode when quota runs out.
