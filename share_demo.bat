@echo off
where cloudflared >nul 2>&1
if errorlevel 1 (
  echo cloudflared is not installed.
  echo Download it from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
  pause
  exit /b 1
)

echo Keep start_demo.bat running in the first window.
echo A public trycloudflare.com URL will appear below. Share that URL with your team.
cloudflared tunnel --url http://127.0.0.1:8080
