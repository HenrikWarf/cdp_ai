#!/bin/bash
# Start All Services for AetherSegment AI CDP
# Mac/Linux Bash Script
# Make executable: chmod +x start_services.sh
# Run with: ./start_services.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  AetherSegment AI - Starting All Services${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    
    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠ Warning: Virtual environment not found at venv/${NC}"
    echo -e "${YELLOW}   Services will run using system Python${NC}"
fi

echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ ERROR: .env file not found!${NC}"
    echo -e "${RED}   Please create a .env file with required configuration${NC}"
    echo -e "${RED}   See env_template_chat.txt for reference${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Configuration file found (.env)${NC}"
echo ""

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Check if ports are available
PORTS_IN_USE=()
if check_port 5000; then PORTS_IN_USE+=("5000 (Flask API)"); fi
if check_port 8001; then PORTS_IN_USE+=("8001 (Conversational Segmentation)"); fi
if check_port 5500; then PORTS_IN_USE+=("5500 (Frontend)"); fi

if [ ${#PORTS_IN_USE[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: Some ports are already in use:${NC}"
    for port in "${PORTS_IN_USE[@]}"; do
        echo -e "${YELLOW}   - Port $port${NC}"
    done
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Cancelled.${NC}"
        exit 1
    fi
    echo ""
fi

# Create logs directory
mkdir -p logs

echo -e "${CYAN}Starting services...${NC}"
echo ""

# Start Flask API (Port 5000)
echo -e "${YELLOW}1. Starting Flask API (Port 5000)...${NC}"
if [ -d "venv" ]; then
    (source venv/bin/activate && python run.py > logs/flask_api.log 2>&1) &
else
    python run.py > logs/flask_api.log 2>&1 &
fi
FLASK_PID=$!
echo "   PID: $FLASK_PID"
sleep 2

# Start Conversational Segmentation Agent (Port 8001)
echo -e "${YELLOW}2. Starting Conversational Segmentation Agent (Port 8001)...${NC}"
if [ -d "venv" ]; then
    (source venv/bin/activate && python run_segmentation.py > logs/segmentation_agent.log 2>&1) &
else
    python run_segmentation.py > logs/segmentation_agent.log 2>&1 &
fi
ANALYTICS_PID=$!
echo "   PID: $ANALYTICS_PID"
sleep 2

# Start Frontend (Port 5500)
echo -e "${YELLOW}3. Starting Frontend (Port 5500)...${NC}"
(cd frontend && python -m http.server 5500 > ../logs/frontend.log 2>&1) &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"
sleep 2

# Save PIDs to file for easy cleanup
echo "$FLASK_PID" > logs/services.pid
echo "$ANALYTICS_PID" >> logs/services.pid
echo "$FRONTEND_PID" >> logs/services.pid

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  All Services Started Successfully!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${CYAN}Services running:${NC}"
echo -e "${WHITE}  • Flask API:                    http://localhost:5000${NC}"
echo -e "${WHITE}  • Conversational Segmentation:  http://localhost:8001${NC}"
echo -e "${WHITE}  • Frontend:                     http://localhost:5500${NC}"
echo ""
echo -e "${CYAN}Process IDs:${NC}"
echo -e "${WHITE}  • Flask API:                    $FLASK_PID${NC}"
echo -e "${WHITE}  • Conversational Segmentation:  $ANALYTICS_PID${NC}"
echo -e "${WHITE}  • Frontend:                     $FRONTEND_PID${NC}"
echo ""
echo -e "${CYAN}Access the application:${NC}"
echo -e "${WHITE}  • Overview Dashboard:            http://localhost:5500/index.html${NC}"
echo -e "${WHITE}  • Campaign Segmentation:         http://localhost:5500/campaign-segmentation.html${NC}"
echo -e "${WHITE}  • Conversational Segmentation:   http://localhost:5500/conversational-analytics.html${NC}"
echo ""
echo -e "${CYAN}Logs are saved in:${NC}"
echo -e "${WHITE}  • logs/flask_api.log${NC}"
echo -e "${WHITE}  • logs/segmentation_agent.log${NC}"
echo -e "${WHITE}  • logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}To stop all services, run:${NC}"
echo -e "${WHITE}  ./stop_services.sh${NC}"
echo ""
echo -e "${YELLOW}Or manually stop them:${NC}"
echo -e "${WHITE}  kill $FLASK_PID $ANALYTICS_PID $FRONTEND_PID${NC}"
echo ""

# Try to open browser (works on Mac and most Linux with xdg-open)
if command -v open &> /dev/null; then
    echo -e "${YELLOW}Opening browser...${NC}"
    sleep 3
    open "http://localhost:5500/index.html"
    echo -e "${GREEN}✓ Browser opened to application${NC}"
elif command -v xdg-open &> /dev/null; then
    echo -e "${YELLOW}Opening browser...${NC}"
    sleep 3
    xdg-open "http://localhost:5500/index.html"
    echo -e "${GREEN}✓ Browser opened to application${NC}"
else
    echo -e "${YELLOW}Please open your browser to: http://localhost:5500/index.html${NC}"
fi

echo ""
echo -e "${GREEN}Services are running in the background.${NC}"
echo -e "${YELLOW}Use ./stop_services.sh to stop all services.${NC}"
echo ""

