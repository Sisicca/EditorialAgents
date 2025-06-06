#!/bin/bash

echo "Starting EditorialAgents Application..."
echo

# Set project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Function to check if conda is available
check_conda() {
    if ! command -v conda &> /dev/null; then
        echo "Error: conda is not installed or not in PATH"
        echo "Please install conda and make sure it's available in your PATH"
        exit 1
    fi
}

# Function to activate conda environment
activate_conda_env() {
    echo "Activating conda environment: DeepEdit"
    
    # Initialize conda for bash
    eval "$(conda shell.bash hook)"
    
    # Activate the environment
    conda activate DeepEdit
    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate conda environment DeepEdit"
        echo "Please make sure conda is installed and DeepEdit environment exists"
        exit 1
    fi
}

# Function to start backend server
start_backend() {
    echo "Starting backend server..."
    
    # Check if we're on macOS or Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && conda activate DeepEdit && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000\""
    else
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Backend Server" -- bash -c "cd '$PROJECT_DIR' && conda activate DeepEdit && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -title "Backend Server" -e "cd '$PROJECT_DIR' && conda activate DeepEdit && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000; bash" &
        elif command -v konsole &> /dev/null; then
            konsole --title "Backend Server" -e bash -c "cd '$PROJECT_DIR' && conda activate DeepEdit && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000; exec bash" &
        else
            echo "Warning: No suitable terminal emulator found. Starting backend in background..."
            nohup bash -c "cd '$PROJECT_DIR' && conda activate DeepEdit && uvicorn web_api.main:app --reload --host 0.0.0.0 --port 8000" > backend.log 2>&1 &
            echo "Backend started in background. Check backend.log for output."
        fi
    fi
}

# Function to start frontend server
start_frontend() {
    echo "Starting frontend server..."
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed or not in PATH"
        echo "Please install Node.js and npm"
        exit 1
    fi
    
    # Check if we're on macOS or Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR/frontend-react' && npm run dev\""
    else
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Frontend Server" -- bash -c "cd '$PROJECT_DIR/frontend-react' && npm run dev; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -title "Frontend Server" -e "cd '$PROJECT_DIR/frontend-react' && npm run dev; bash" &
        elif command -v konsole &> /dev/null; then
            konsole --title "Frontend Server" -e bash -c "cd '$PROJECT_DIR/frontend-react' && npm run dev; exec bash" &
        else
            echo "Warning: No suitable terminal emulator found. Starting frontend in background..."
            nohup bash -c "cd '$PROJECT_DIR/frontend-react' && npm run dev" > frontend.log 2>&1 &
            echo "Frontend started in background. Check frontend.log for output."
        fi
    fi
}

# Function to open browser
open_browser() {
    echo "Opening browser..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open http://localhost:5173
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:5173
        elif command -v firefox &> /dev/null; then
            firefox http://localhost:5173 &
        elif command -v google-chrome &> /dev/null; then
            google-chrome http://localhost:5173 &
        elif command -v chromium-browser &> /dev/null; then
            chromium-browser http://localhost:5173 &
        else
            echo "Could not find a suitable browser. Please open http://localhost:5173 manually."
        fi
    fi
}

# Main execution
check_conda
activate_conda_env

start_backend

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

start_frontend

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 3

echo
echo "========================================"
echo "EditorialAgents Application Started!"
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo

open_browser

echo
echo "Application is running!"
echo "Close the backend and frontend terminal windows to stop the application."
echo