# Running Services Guide

This guide explains how to start and stop all AetherSegment AI services.

## Quick Start

### Windows (PowerShell)

**Start all services:**
```powershell
.\start_services.ps1
```

**Stop all services:**
```powershell
.\stop_services.ps1
```

### Mac/Linux (Bash)

**Make scripts executable (first time only):**
```bash
chmod +x start_services.sh stop_services.sh
```

**Start all services:**
```bash
./start_services.sh
```

**Stop all services:**
```bash
./stop_services.sh
```

---

## What the Scripts Do

### Start Scripts (`start_services.ps1` / `start_services.sh`)

1. ✅ **Checks prerequisites**
   - Virtual environment exists
   - `.env` file is configured
   - Required ports are available (5000, 8000, 5500)

2. 🚀 **Starts all services**
   - **Flask API** (Port 5000) - Main backend for campaigns/segments
   - **Chat Agent** (Port 8000) - FastAPI conversational analytics
   - **Frontend** (Port 5500) - Static file server

3. 🌐 **Opens browser**
   - Automatically opens `http://localhost:5500/index.html`

4. 📝 **Provides access URLs**
   - Shows all service URLs and endpoints

### Stop Scripts (`stop_services.ps1` / `stop_services.sh`)

1. 🛑 **Stops all running services**
   - Finds processes by port
   - Gracefully terminates services
   - Force kills if needed

2. 🧹 **Optional cleanup**
   - Asks if you want to clear log files
   - Removes old logs if confirmed

---

## Service Details

### Flask API (Port 5000)
- **Purpose**: Main backend API
- **Endpoints**: `/api/v1/overview/stats`, `/api/v1/campaigns/analyze`, etc.
- **Log**: `logs/flask_api.log` (Mac/Linux only)
- **Start manually**: `python run.py`

### Chat Agent (Port 8000)
- **Purpose**: Conversational analytics
- **Endpoints**: `/health`, `/chat`, `/adk`
- **Log**: `logs/chat_agent.log` (Mac/Linux only)
- **Start manually**: `python run_chat.py`

### Frontend (Port 5500)
- **Purpose**: Static file server for UI
- **Pages**: `index.html`, `campaign-segmentation.html`, `conversational-analytics.html`
- **Log**: `logs/frontend.log` (Mac/Linux only)
- **Start manually**: `cd frontend && python -m http.server 5500`

---

## Platform Differences

### Windows (PowerShell)
- ✅ Opens each service in **separate PowerShell window**
- ✅ Each window shows live logs/output
- ✅ Color-coded output
- ✅ Port availability check
- ⚠️ No consolidated log files (see terminal windows instead)
- 🛑 Close windows to stop services (or use stop script)

### Mac/Linux (Bash)
- ✅ Runs all services in **background**
- ✅ Saves logs to `logs/` directory
- ✅ Shows process IDs (PIDs)
- ✅ Port availability check
- ✅ Consolidated log files for troubleshooting
- 🛑 Use stop script to terminate services

---

## Troubleshooting

### "Port already in use"
**Problem**: Another service is using ports 5000, 8000, or 5500

**Solution - Windows**:
```powershell
# Find and kill process on port (e.g., 5000)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```

**Solution - Mac/Linux**:
```bash
# Find and kill process on port (e.g., 5000)
lsof -ti:5000 | xargs kill -9
```

### "Virtual environment not found"
**Problem**: Script can't find `venv/`

**Solution**:
```bash
# Create virtual environment
python -m venv venv

# Activate and install dependencies
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### ".env file not found"
**Problem**: No environment configuration

**Solution**:
```bash
# Copy template and edit
cp env_template_chat.txt .env

# Edit with your values
# Windows:
notepad .env
# Mac/Linux:
nano .env
```

### Services won't start
**Problem**: Missing dependencies or configuration errors

**Solution**:
1. Check logs (if available)
2. Try starting manually to see error messages:
   ```bash
   python run.py          # Flask API
   python run_chat.py     # Chat Agent
   ```
3. Verify `.env` has all required values
4. Check Python version: `python --version` (should be 3.9+)

### Browser doesn't open automatically
**Normal on some systems**

**Solution**: 
Manually open browser to: `http://localhost:5500/index.html`

### Can't stop services on Mac/Linux
**Problem**: PID file not found

**Solution**:
```bash
# Manually kill by port
lsof -ti:5000 | xargs kill -9  # Flask API
lsof -ti:8000 | xargs kill -9  # Chat Agent
lsof -ti:5500 | xargs kill -9  # Frontend
```

---

## Manual Service Management

If you prefer to manage services manually:

### Start Each Service (3 Terminals)

**Terminal 1 - Flask API:**
```bash
# Activate venv (if using)
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Start Flask API
python run.py
```

**Terminal 2 - Chat Agent:**
```bash
# Activate venv (if using)
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Start Chat Agent
python run_chat.py
```

**Terminal 3 - Frontend:**
```bash
# No venv needed for static server
cd frontend
python -m http.server 5500
```

### Stop Services
Press `Ctrl+C` in each terminal window

---

## Logs

### Windows
- Logs appear in **separate PowerShell windows**
- Each service has its own window with live output
- No log files created

### Mac/Linux
- Logs saved to `logs/` directory:
  - `logs/flask_api.log`
  - `logs/chat_agent.log`
  - `logs/frontend.log`
- View live logs: `tail -f logs/flask_api.log`
- View all logs: `cat logs/*.log`

---

## Tips

### Development Workflow

1. **Start services once:**
   ```bash
   ./start_services.sh  # or .ps1 on Windows
   ```

2. **Make code changes**
   - Flask API auto-reloads (if `FLASK_DEBUG=True`)
   - Chat Agent requires restart
   - Frontend static files reload automatically

3. **Restart only what changed:**
   - If backend code changed: Restart Flask API or Chat Agent
   - If frontend changed: Just refresh browser
   - If `.env` changed: Restart all services

4. **Stop services when done:**
   ```bash
   ./stop_services.sh  # or .ps1 on Windows
   ```

### Working with VS Code
You can use the scripts directly in VS Code terminal:
1. Open integrated terminal (`` Ctrl+` ``)
2. Run the start script
3. Services appear in separate windows (Windows) or run in background (Mac/Linux)

### Auto-start on System Boot (Optional)

**Mac/Linux** (using cron):
```bash
# Edit crontab
crontab -e

# Add line (adjust path):
@reboot cd /path/to/ai_cdp && ./start_services.sh
```

**Windows** (using Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When I log on"
4. Action: "Start a program"
5. Program: `powershell.exe`
6. Arguments: `-File C:\path\to\ai_cdp\start_services.ps1`

---

## Summary

| Action | Windows | Mac/Linux |
|--------|---------|-----------|
| Start all services | `.\start_services.ps1` | `./start_services.sh` |
| Stop all services | `.\stop_services.ps1` | `./stop_services.sh` |
| View logs | Check PowerShell windows | `tail -f logs/*.log` |
| Manual start Flask | `python run.py` | `python run.py` |
| Manual start Chat | `python run_chat.py` | `python run_chat.py` |
| Manual start Frontend | `cd frontend; python -m http.server 5500` | same |

---

## Access URLs

Once services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Flask API** | http://localhost:5000 | Main backend API |
| **Chat Agent** | http://localhost:8000 | Conversational analytics |
| **Frontend** | http://localhost:5500 | Web interface |
| | | |
| **Overview** | http://localhost:5500/index.html | Dashboard |
| **Campaigns** | http://localhost:5500/campaign-segmentation.html | Campaign builder |
| **Chat** | http://localhost:5500/conversational-analytics.html | Conversational analytics |

---

## Need Help?

- Check service logs for errors
- Ensure `.env` is configured correctly
- Verify all dependencies are installed
- See troubleshooting section above
- Refer to `SETUP_GUIDE.md` for initial setup
- Refer to `CONVERSATIONAL_ANALYTICS_SETUP.md` for chat setup

