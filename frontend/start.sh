#!/bin/bash

echo "?? Starting Frontend..."

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting Vite development server..."
npm run dev
