#!/usr/bin/env bash
# ==============================================================================
# 🚦 AURA v2.0: Unified Intelligent Traffic Management System Orchestrator
# Multi-Agent Reinforcement Learning • WebSocket Bridge • Live Web Dashboard
# ==============================================================================

set -e

# Styling & Colors
BOLD='\033[1m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
PURPLE='\033[35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/traffic-backend"
DASHBOARD_DIR="${SCRIPT_DIR}/traffic-dashboard"
AI_DIR="${SCRIPT_DIR}/traffic-ai"
VENV_PY="${AI_DIR}/venv/bin/python"

# Track Child PIDs for Graceful Teardown
BACKEND_PID=""
FRONTEND_PID=""
AI_PID=""

cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down AURA Subsystems gracefully...${NC}"
    if [ -n "$AI_PID" ] && kill -0 "$AI_PID" 2>/dev/null; then
        echo -e "   Stopping TraCI Simulation Agent (PID: $AI_PID)..."
        kill "$AI_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "   Stopping Vite Dashboard (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "   Stopping Node.js WebSocket Bridge (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}🏁 All AURA services closed cleanly. Have a great day!${NC}\n"
    exit 0
}

trap cleanup INT TERM EXIT

print_banner() {
    clear 2>/dev/null || true
    echo -e "${CYAN}${BOLD}"
    cat << "EOF"
    ___   __  ______  ___      _   _____   ____ 
   /   | / / / / __ \/   |    | | / /__ \ / __ \
  / /| |/ / / / /_/ / /| |    | |/ /__/ // / / /
 / ___ / /_/ / _, _/ ___ |    | |// __// /_/ / 
/_/  |_\____/_/ |_/_/  |_|    |___/____/\____(_) 
EOF
    echo -e "${NC}"
    echo -e "${BOLD}Adaptive Urban Routing & Actuation • Resilient Multi-Agent RL${NC}"
    echo -e "IEEE Transactions on Intelligent Transportation Systems (T-ITS) Edition"
    echo -e "----------------------------------------------------------------------"
}

# Pre-flight environment check
preflight_check() {
    echo -e "\n${BOLD}🔍 Running Pre-Flight Sanity Checks...${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js (v18+).${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}✓${NC} Node.js: $(node --version)"

    # Check SUMO
    if ! command -v sumo &> /dev/null; then
        echo -e "${RED}❌ Eclipse SUMO is not found in PATH.${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}✓${NC} SUMO: $(sumo --version 2>&1 | head -n 1)"

    # Check Virtual Environment
    if [ ! -f "$VENV_PY" ]; then
        echo -e "${YELLOW}⚠️ Virtual environment not detected at traffic-ai/venv. Creating...${NC}"
        python3 -m venv "${AI_DIR}/venv"
        "${AI_DIR}/venv/bin/pip" install -r "${AI_DIR}/requirements.txt"
    fi
    echo -e "   ${GREEN}✓${NC} Python Venv: $("${VENV_PY}" --version)"

    # Check Ports
    for PORT in 3000 5173; do
        STALE_PID=$(lsof -ti :$PORT 2>/dev/null || true)
        if [ -n "$STALE_PID" ]; then
            echo -e "   ${YELLOW}⚠️ Port $PORT is occupied by PID $STALE_PID. Freeing port...${NC}"
            kill -9 $STALE_PID 2>/dev/null || true
            sleep 0.5
        fi
    done
    echo -e "   ${GREEN}✓${NC} Ports 3000 & 5173 Available"
    echo -e "${GREEN}✅ All Pre-Flight checks passed!${NC}\n"
}

# Benchmark mode
run_edge_benchmark() {
    print_banner
    echo -e "${PURPLE}${BOLD}⚡ Executing AURA Edge Deployment & ONNX Micro-Benchmark...${NC}\n"
    CUDA_VISIBLE_DEVICES="" "${VENV_PY}" "${AI_DIR}/benchmark_edge_onnx.py"
    exit 0
}

# Manhattan GUI Mode
run_manhattan_gui_mode() {
    print_banner
    preflight_check
    echo -e "${CYAN}${BOLD}🏙️  Launching Midtown Manhattan (177 Intersections) in SUMO-GUI...${NC}\n"
    cd "$BACKEND_DIR"
    node server.js > /dev/null 2>&1 &
    BACKEND_PID=$!
    sleep 1
    cd "$DASHBOARD_DIR"
    npm run dev -- --port 5173 --host > /dev/null 2>&1 &
    FRONTEND_PID=$!
    sleep 1.5
    cd "$AI_DIR"
    CUDA_VISIBLE_DEVICES="" "$VENV_PY" run_manhattan_gui.py &
    AI_PID=$!
    echo -e "\n${GREEN}${BOLD}✨ Manhattan SUMO-GUI & Web Dashboard are Active!${NC}"
    wait "$AI_PID"
    exit 0
}

# Manhattan mode
run_manhattan_mode() {
    print_banner
    echo -e "${CYAN}${BOLD}🏙️  Executing Midtown Manhattan 177-Intersection Benchmark...${NC}\n"
    CUDA_VISIBLE_DEVICES="" "${VENV_PY}" "${AI_DIR}/evaluate_real_manhattan.py"
    exit 0
}

# Vision Detection Mode
run_vision_mode() {
    print_banner
    preflight_check
    echo -e "${PURPLE}${BOLD}📹 Launching AURA Edge Computer Vision Pipeline...${NC}\n"
    cd "$BACKEND_DIR"
    node server.js > /dev/null 2>&1 &
    BACKEND_PID=$!
    sleep 1
    cd "$AI_DIR"
    CUDA_VISIBLE_DEVICES="" "$VENV_PY" vision_detector.py
    exit 0
}

# Hardware-in-the-Loop Mode
run_hil_mode() {
    print_banner
    echo -e "${PURPLE}${BOLD}🚦 Launching AURA Hardware-in-the-Loop Physical LED Bridge...${NC}\n"
    cd "$AI_DIR"
    CUDA_VISIBLE_DEVICES="" "$VENV_PY" hil_hardware_bridge.py
    exit 0
}

# Docker Compose Mode
run_docker_mode() {
    print_banner
    echo -e "${CYAN}${BOLD}🐳 Booting AURA via Docker Compose...${NC}\n"
    docker compose up --build
    exit 0
}

# Main Full System Launcher
launch_full_system() {
    USE_GUI="${1:-0}"
    SCENARIO="${2:-corridor}"

    print_banner
    preflight_check

    echo -e "${BOLD}🚀 Starting AURA Unified Subsystems...${NC}"

    # 1. Start Node.js Backend Server
    echo -e "   ${CYAN}[1/3]${NC} Starting Backend & WebSocket Server on Port 3000..."
    cd "$BACKEND_DIR"
    node server.js > /dev/null 2>&1 &
    BACKEND_PID=$!
    sleep 1

    # 2. Start Vite React Dashboard
    echo -e "   ${CYAN}[2/3]${NC} Starting Live React Dashboard on Port 5173..."
    cd "$DASHBOARD_DIR"
    npm run dev -- --port 5173 --host > /dev/null 2>&1 &
    FRONTEND_PID=$!
    sleep 1.5

    # 3. Start Python TraCI Simulation Controller
    cd "$AI_DIR"
    if [ "$SCENARIO" == "demo" ]; then
        echo -e "   ${CYAN}[3/3]${NC} Launching Single Intersection Demo (A0)..."
        SUMO_GUI="$USE_GUI" CUDA_VISIBLE_DEVICES="" "$VENV_PY" run_demo.py &
        AI_PID=$!
    else
        echo -e "   ${CYAN}[3/3]${NC} Launching 10-Intersection Spatial-Temporal GAT MARL Corridor..."
        SUMO_GUI="$USE_GUI" CUDA_VISIBLE_DEVICES="" "$VENV_PY" run_marl_corridor.py &
        AI_PID=$!
    fi

    echo -e "\n${GREEN}${BOLD}✨ AURA SYSTEM IS NOW FULLY LIVE & RUNNING!${NC}"
    echo -e "----------------------------------------------------------------------"
    echo -e "   🖥️  ${BOLD}Web Dashboard:${NC}    ${CYAN}http://localhost:5173${NC}"
    echo -e "   📡 ${BOLD}REST API Bridge:${NC}  ${CYAN}http://localhost:3000/api/traffic${NC}"
    echo -e "   ⚡ ${BOLD}WebSocket Stream:${NC} ${CYAN}ws://localhost:3000${NC}"
    echo -e "   🚨 ${BOLD}Emergency Inject:${NC} ${CYAN}http://localhost:3000/api/inject-ambulance${NC}"
    echo -e "----------------------------------------------------------------------"
    echo -e "${YELLOW}Press [Ctrl+C] at any time to shut down all processes cleanly.${NC}\n"

    # Try to open dashboard in browser if xdg-open exists
    if command -v xdg-open &> /dev/null && [ -n "$DISPLAY" ]; then
        xdg-open "http://localhost:5173" &> /dev/null || true
    fi

    # Wait on child processes
    wait "$AI_PID"
}

# CLI Argument Router
case "$1" in
    --edge-benchmark|--benchmark)
        run_edge_benchmark
        ;;
    --manhattan-gui)
        run_manhattan_gui_mode
        ;;
    --manhattan)
        run_manhattan_mode
        ;;
    --gui)
        launch_full_system 1 "corridor"
        ;;
    --demo)
        launch_full_system 0 "demo"
        ;;
    --demo-gui)
        launch_full_system 1 "demo"
        ;;
    --vision)
        run_vision_mode
        ;;
    --hil)
        run_hil_mode
        ;;
    --docker)
        run_docker_mode
        ;;
    --test)
        print_banner
        preflight_check
        echo -e "${GREEN}Pre-flight test successful!${NC}"
        exit 0
        ;;
    --help|-h)
        print_banner
        echo -e "Usage: ./run_aura.sh [OPTION]"
        echo -e ""
        echo -e "Options:"
        echo -e "  (no args)           Start Full System (Backend + Dashboard + MARL Corridor Headless)"
        echo -e "  --gui               Start Full System with interactive SUMO-GUI window"
        echo -e "  --demo              Start Single Intersection A0 Agent"
        echo -e "  --demo-gui          Start Single Intersection A0 with SUMO-GUI"
        echo -e "  --manhattan         Run 177-Intersection Midtown Manhattan Benchmark"
        echo -e "  --edge-benchmark    Run ONNX sub-millisecond edge latency benchmark"
        echo -e "  --vision            Run Edge Computer Vision Vehicle Detector (CCTV/Webcam)"
        echo -e "  --hil               Run Hardware-in-the-Loop Physical LED Controller Bridge"
        echo -e "  --docker            Launch entire system via Docker Compose"
        echo -e "  --test              Run pre-flight dependency & port sanity check"
        echo -e "  --help, -h          Show this help menu"
        exit 0
        ;;
    *)
        launch_full_system 0 "corridor"
        ;;
esac
