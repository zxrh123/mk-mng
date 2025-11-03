#!/bin/bash

echo "?? AI-Powered MikroTik Network Management Platform"
echo "=================================================="
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "?? Starting with Docker..."
    docker-compose up --build
else
    echo "?? Starting without Docker..."
    echo ""
    echo "Starting Backend..."
    cd backend && bash start.sh &
    BACKEND_PID=$!
    
    echo "Starting Frontend..."
    cd ../frontend && bash start.sh &
    FRONTEND_PID=$!
    
    echo ""
    echo "? Services started!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
    wait
fi
