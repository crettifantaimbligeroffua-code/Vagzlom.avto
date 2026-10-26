SELF-PING BOT (best effort)

The app now has a /healthz endpoint and a background bot that requests it every 7 minutes by default.
The interval is configurable with SELF_PING_INTERVAL_MINUTES and is clamped to 5-10 minutes.
The public URL is read from SITE_URL, or Render's RENDER_EXTERNAL_URL.

Render setup:
- If SITE_URL is already configured, it should be the public base URL of this same service.
- Otherwise Render usually provides RENDER_EXTERNAL_URL automatically.
- Optional: set SELF_PING_INTERVAL_MINUTES=7.

Important: a self-ping loop is only best-effort. If Render stops the service/process, the loop stops too, so this does not guarantee the service will stay awake on a free plan. It also does NOT make local SQLite/uploads persistent. Use persistent storage or a managed database for that.
