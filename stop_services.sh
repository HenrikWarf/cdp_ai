#!/bin/bash
# Stop All Services for AetherSegment AI CDP
# Mac/Linux Bash Script
# Make executable: chmod +x stop_services.sh
# Run with: ./stop_services.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  AetherSegment AI - Stopping All Services${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Check if PID file exists
if [ -f "logs/services.pid" ]; then
    echo -e "${YELLOW}Reading process IDs from logs/services.pid...${NC}"
    
    # Read PIDs from file
    PIDS=$(cat logs/services.pid)
    
    echo -e "${YELLOW}Stopping services...${NC}"
    
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}  Stopping process $PID...${NC}"
            kill $PID 2>/dev/null
            
            # Wait a moment and check if it's stopped
            sleep 1
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}  Force stopping process $PID...${NC}"
                kill -9 $PID 2>/dev/null
            fi
            echo -e "${GREEN}  ✓ Process $PID stopped${NC}"
        else
            echo -e "${YELLOW}  Process $PID is not running${NC}"
        fi
    done
    
    # Remove PID file
    rm logs/services.pid
    echo ""
    echo -e "${GREEN}✓ All services stopped${NC}"
else
    echo -e "${YELLOW}No PID file found. Attempting to find and stop services by port...${NC}"
    echo ""
    
    # Try to find and kill processes by port
    if command -v lsof &> /dev/null; then
        for PORT in 5000 8000 5500; do
            PID=$(lsof -ti:$PORT)
            if [ ! -z "$PID" ]; then
                echo -e "${YELLOW}  Stopping service on port $PORT (PID: $PID)...${NC}"
                kill $PID 2>/dev/null
                sleep 1
                if lsof -ti:$PORT > /dev/null 2>&1; then
                    kill -9 $PID 2>/dev/null
                fi
                echo -e "${GREEN}  ✓ Service on port $PORT stopped${NC}"
            else
                echo -e "${YELLOW}  No service running on port $PORT${NC}"
            fi
        done
        echo ""
        echo -e "${GREEN}✓ All services stopped${NC}"
    else
        echo -e "${RED}Error: lsof command not found${NC}"
        echo -e "${YELLOW}Please manually stop services:${NC}"
        echo "  1. Find processes: ps aux | grep python"
        echo "  2. Stop them: kill <PID>"
    fi
fi

# Clean up log files (optional)
read -p "Do you want to clear log files? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f logs/*.log
    echo -e "${GREEN}✓ Log files cleared${NC}"
fi

echo ""
echo -e "${GREEN}Services stopped successfully${NC}"
echo ""

