#!/bin/bash

# Quick Setup Script for Chemical Equipment Visualizer
# Run this script to set up all components quickly

echo "🚀 Setting up Chemical Equipment Visualizer..."
echo ""

# Backend Setup
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and set your SECRET_KEY"
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

echo "✅ Backend setup complete!"
echo ""

# Deactivate virtual environment
deactivate

cd ..

# Web Frontend Setup
echo "🌐 Setting up Web Frontend..."
cd web-frontend

# Install dependencies
npm install

echo "✅ Web frontend setup complete!"
echo ""

cd ..

# Desktop Frontend Setup
echo "🖥  Setting up Desktop Frontend..."
cd desktop-frontend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Desktop frontend setup complete!"
echo ""

# Deactivate virtual environment
deactivate

cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "2. Web:      cd web-frontend && npm run dev"
echo "3. Desktop:  cd desktop-frontend && source venv/bin/activate && python main.py"
echo ""
echo "📖 See README.md for detailed instructions"
