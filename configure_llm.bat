@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" copy /y ".env.example" ".env" >nul

echo Two windows will open:
echo 1. Create and copy a Groq API key in your browser.
echo 2. Paste it after GROQ_API_KEY= in Notepad, then save.
echo.
start "Groq API Key" "https://console.groq.com/keys"
start "ResiliChain Environment" notepad.exe ".env"
pause
