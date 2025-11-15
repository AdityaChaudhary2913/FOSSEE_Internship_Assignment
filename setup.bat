@echo off
REM Quick Setup Script for Chemical Equipment Visualizer (Windows)
REM Run this script to set up all components quickly

echo Setting up Chemical Equipment Visualizer...
echo.

REM Backend Setup
echo Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Copy environment file if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo Please edit backend\.env and set your SECRET_KEY
)

REM Run migrations
python manage.py makemigrations
python manage.py migrate

echo Backend setup complete!
echo.

REM Deactivate virtual environment
deactivate

cd ..

REM Web Frontend Setup
echo Setting up Web Frontend...
cd web-frontend

REM Install dependencies
call npm install

echo Web frontend setup complete!
echo.

cd ..

REM Desktop Frontend Setup
echo Setting up Desktop Frontend...
cd desktop-frontend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

echo Desktop frontend setup complete!
echo.

REM Deactivate virtual environment
deactivate

cd ..

echo Setup complete!
echo.
echo To start the application:
echo 1. Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python manage.py runserver
echo 2. Web:      cd web-frontend ^&^& npm run dev
echo 3. Desktop:  cd desktop-frontend ^&^& venv\Scripts\activate ^&^& python main.py
echo.
echo See README.md for detailed instructions
pause
