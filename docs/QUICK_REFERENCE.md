# Quick Reference - Chemical Equipment Visualizer

## 🚀 Quick Start Commands

### First Time Setup (Choose one):

**macOS/Linux:**
```bash
cd /Users/adityachaudhary/Desktop/FOSSEE/chemical-equipment-visualizer
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd C:\path\to\chemical-equipment-visualizer
setup.bat
```

---

## 🏃 Running the Application

### Terminal 1 - Backend (Django)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python manage.py runserver
```
**Access:** http://localhost:8000  
**API Docs:** http://localhost:8000/swagger/

### Terminal 2 - Web Frontend (React)
```bash
cd web-frontend
npm run dev
```
**Access:** http://localhost:3000

### Terminal 3 - Desktop App (PyQt5)
```bash
cd desktop-frontend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

---

## 🔧 Common Commands

### Backend

**Create Superuser:**
```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

**Run Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Run Tests:**
```bash
python manage.py test
```

**Admin Panel:**
http://localhost:8000/admin/

### Web Frontend

**Install Dependencies:**
```bash
cd web-frontend
npm install
```

**Build for Production:**
```bash
npm run build
```

**Preview Build:**
```bash
npm run preview
```

### Desktop Frontend

**Install Dependencies:**
```bash
cd desktop-frontend
pip install -r requirements.txt
```

**Run Application:**
```bash
python main.py
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Find process
lsof -ti:8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Frontend (3000):**
```bash
# Find and kill
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000  # Windows
```

### Virtual Environment Issues

**Recreate venv:**
```bash
# Delete old venv
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Create new
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Issues

**Reset Database:**
```bash
cd backend
rm db.sqlite3
rm -rf equipment/migrations/
python manage.py makemigrations equipment
python manage.py migrate
```

### Node Modules Issues

**Reinstall:**
```bash
cd web-frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📁 Important Paths

```
/Users/adityachaudhary/Desktop/FOSSEE/chemical-equipment-visualizer/
├── backend/
│   ├── config/settings.py          # Django settings
│   ├── equipment/                  # Main app
│   ├── db.sqlite3                  # Database
│   └── manage.py                   # Django CLI
├── web-frontend/
│   ├── src/                        # React source
│   ├── package.json                # Dependencies
│   └── vite.config.js              # Vite config
├── desktop-frontend/
│   ├── main.py                     # App entry
│   ├── ui/                         # UI components
│   └── services/                   # API service
├── README.md                       # Main documentation
├── DEMO_GUIDE.md                   # Video guide
└── PROJECT_STATUS.md               # Completion status
```

---

## 🧪 Testing Checklist

- [ ] Backend server starts (port 8000)
- [ ] API docs accessible (/swagger/)
- [ ] Web frontend starts (port 3000)
- [ ] Desktop app launches
- [ ] User registration works
- [ ] User login works (web + desktop)
- [ ] CSV upload works (use sample_equipment_data.csv)
- [ ] Data visualization displays
- [ ] PDF generation works
- [ ] History shows last 5 datasets
- [ ] Delete dataset works
- [ ] Logout works

---

## 📦 Sample Data

**File:** `sample_equipment_data.csv` (in workspace root)

**Format:**
```csv
Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency
EQ001,Pump,75.5,2.3,150.0,92.5
...
```

**Test User:**
- Username: demo_user
- Password: demo123!@#
- Email: demo@example.com

---

## 🌐 URLs Reference

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | Django REST API |
| Swagger Docs | http://localhost:8000/swagger/ | API documentation |
| ReDoc | http://localhost:8000/redoc/ | Alternative API docs |
| Admin Panel | http://localhost:8000/admin/ | Django admin |
| Web App | http://localhost:3000 | React frontend |

---

## 📊 API Endpoints Quick Reference

**Auth:**
- POST `/api/auth/register/` - Register
- POST `/api/auth/login/` - Login
- POST `/api/auth/logout/` - Logout

**Datasets:**
- GET `/api/datasets/` - List all
- POST `/api/datasets/upload_csv/` - Upload CSV
- GET `/api/datasets/history/` - Last 5
- GET `/api/datasets/{id}/summary/` - Get summary
- GET `/api/datasets/{id}/generate_pdf/` - Download PDF
- DELETE `/api/datasets/{id}/` - Delete

---

## 🔑 Environment Variables

Create `.env` file in `backend/`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📝 Git Commands

**Initial Setup:**
```bash
cd /Users/adityachaudhary/Desktop/FOSSEE/chemical-equipment-visualizer
git init
git add .
git commit -m "Initial commit: Chemical Equipment Visualizer"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

**Regular Updates:**
```bash
git add .
git commit -m "Description of changes"
git push
```

---

## 🎯 Quick Demo Script

1. **Start all services** (3 terminals)
2. **Register user** (web or desktop)
3. **Upload CSV** (sample_equipment_data.csv)
4. **View charts** (pie + bar)
5. **Download PDF**
6. **Check history**
7. **Delete dataset**
8. **Logout**

**Time:** 2-3 minutes

---

## 💡 Tips

- Always activate virtual environment before running Python commands
- Check ports 8000 and 3000 are free before starting
- Use Swagger UI for testing API endpoints
- Check browser console for web frontend errors
- Use Qt Designer for UI modifications (desktop app)
- Run migrations after model changes
- Clear browser cache if web app acts strange

---

## 📞 Help Resources

- **README.md** - Complete setup guide
- **DEMO_GUIDE.md** - Video creation guide
- **PROJECT_STATUS.md** - Feature checklist
- **Django Docs** - https://docs.djangoproject.com/
- **React Docs** - https://react.dev/
- **PyQt5 Docs** - https://www.riverbankcomputing.com/static/Docs/PyQt5/

---

**Last Updated:** $(date)
**Quick Reference Version:** 1.0.0
