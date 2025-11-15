# Chemical Equipment Parameter Visualizer

A hybrid web and desktop application for visualizing and analyzing chemical equipment data. Built with Django REST Framework backend, React.js web frontend, and PyQt5 desktop frontend.

## 📋 Project Overview

This application allows users to upload CSV files containing chemical equipment data (Equipment Name, Type, Flowrate, Pressure, Temperature) and provides:
- **Data Analysis**: Automatic calculation of summary statistics and equipment type distribution
- **Interactive Visualizations**: Charts using Chart.js (web) and Matplotlib (desktop)
- **History Management**: Store and access the last 5 uploaded datasets
- **PDF Reports**: Generate comprehensive PDF reports for each dataset
- **Authentication**: Secure user authentication and authorization

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Django + Django REST Framework | REST API server |
| Web Frontend | React.js + Chart.js | Interactive web interface |
| Desktop Frontend | PyQt5 + Matplotlib | Native desktop application |
| Data Processing | Pandas + NumPy | CSV parsing and analytics |
| Database | SQLite | Dataset storage |
| Documentation | Swagger/OpenAPI | API documentation |
| PDF Generation | ReportLab | Automated report creation |

## 🏗 Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django backend
│   ├── config/                # Django project settings
│   ├── equipment/             # Main application
│   │   ├── models.py         # Database models
│   │   ├── serializers.py    # DRF serializers
│   │   ├── views.py          # API endpoints
│   │   ├── urls.py           # URL routing
│   │   ├── utils.py          # Helper functions
│   │   └── tests.py          # Unit tests
│   ├── manage.py
│   └── requirements.txt
│
├── web-frontend/              # React web application
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service
│   │   └── utils/           # Utilities
│   ├── package.json
│   └── vite.config.js
│
└── desktop-frontend/          # PyQt5 desktop application
    ├── ui/                   # UI components
    ├── services/             # API service
    ├── main.py              # Application entry point
    └── requirements.txt
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd chemical-equipment-visualizer/backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file and set SECRET_KEY and other variables
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

   The backend API will be available at: `http://localhost:8000`
   - API endpoints: `http://localhost:8000/api/`
   - Admin panel: `http://localhost:8000/admin/`
   - Swagger docs: `http://localhost:8000/swagger/`

### Web Frontend Setup

1. **Navigate to web frontend directory:**
   ```bash
   cd chemical-equipment-visualizer/web-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The web application will be available at: `http://localhost:3000`

4. **Build for production:**
   ```bash
   npm run build
   ```

### Desktop Frontend Setup

1. **Navigate to desktop frontend directory:**
   ```bash
   cd chemical-equipment-visualizer/desktop-frontend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 📝 Usage Guide

### 1. User Registration/Login

**Web Application:**
- Navigate to `http://localhost:3000/register`
- Fill in username, email, and password
- Click "Register" to create account
- Or login at `http://localhost:3000/login`

**Desktop Application:**
- Launch the application
- Use the login dialog to sign in or register

### 2. Upload CSV File

**Required CSV Format:**
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95
Valve-1,Valve,60,4.1,105
```

**Required Columns:**
- Equipment Name (string)
- Type (string)
- Flowrate (numeric, ≥ 0)
- Pressure (numeric, ≥ 0)
- Temperature (numeric)

**Web:**
- Navigate to "Upload" page
- Drag and drop CSV file or click "Browse Files"
- Click "Upload and Analyze"

**Desktop:**
- Go to "Upload CSV" tab
- Click "Select CSV File"
- Click "Upload"

### 3. View Analytics

After upload, you'll see:
- **Summary Statistics**: Total count, averages for all parameters
- **Equipment Type Distribution**: Pie chart showing equipment types
- **Parameter Charts**: Bar charts for flowrate, pressure, temperature
- **Detailed Statistics**: Per-type analysis
- **Data Table**: Complete equipment listing

### 4. Access History

- View last 5 uploaded datasets
- Click on any dataset to view detailed analysis
- Delete old datasets if needed

### 5. Generate PDF Report

- View any dataset details
- Click "Download PDF Report"
- PDF includes:
  - Dataset information
  - Summary statistics
  - Equipment type distribution
  - Formatted tables

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/me/` - Get current user

### Datasets
- `POST /api/datasets/upload_csv/` - Upload CSV file
- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{id}/` - Get dataset details
- `GET /api/datasets/history/` - Get last 5 datasets
- `GET /api/datasets/{id}/summary/` - Get dataset with analysis
- `GET /api/datasets/{id}/generate_pdf/` - Download PDF report
- `DELETE /api/datasets/{id}/` - Delete dataset

### Health Check
- `GET /api/health/` - API health status

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Web Frontend Tests

```bash
cd web-frontend
npm run test
```

## 📊 Sample Data

A sample CSV file is included: `sample_equipment_data.csv`

This file contains 15 equipment entries demonstrating the required format and can be used for testing.

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Web Frontend Configuration

Create `web-frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

### Desktop Frontend Configuration

The desktop app connects to `http://localhost:8000/api` by default. This can be changed in `services/api_service.py`.

## 🚢 Deployment

### Backend Deployment (Example: Heroku)

1. Install Heroku CLI and login
2. Create new Heroku app
3. Add PostgreSQL addon
4. Set environment variables
5. Deploy:
   ```bash
   git push heroku main
   python manage.py migrate
   ```

### Web Frontend Deployment (Example: Vercel)

1. Install Vercel CLI
2. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Deploy:
   ```bash
   vercel --prod
   ```

## 🏆 Features Implemented

✅ **Core Features:**
- CSV file upload with validation
- Data parsing using Pandas
- Summary statistics calculation
- Equipment type distribution analysis
- Interactive data visualization
- Last 5 datasets history management
- PDF report generation
- User authentication

✅ **Best Practices:**
- RESTful API design
- MVC/MVVM patterns
- Error handling and validation
- Responsive UI design
- Code modularity (DRY principle)
- Comprehensive documentation
- Git version control
- API documentation with Swagger

✅ **Security:**
- Token-based authentication
- Password hashing
- CORS configuration
- Input validation
- SQL injection prevention

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
python manage.py runserver 8001
```

**Database errors:**
```bash
rm db.sqlite3
python manage.py migrate
```

### Frontend Issues

**Node modules errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port conflicts:**
Edit `vite.config.js` and change port number

### Desktop App Issues

**PyQt5 installation fails:**
```bash
pip install --upgrade pip
pip install PyQt5 --no-cache-dir
```

**matplotlib display errors:**
```bash
pip install pyqt5-tools
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

## 👤 Author

Built for FOSSEE Internship Screening Task

## 📄 License

This project is created for educational and screening purposes.

## 🙏 Acknowledgments

- FOSSEE for the internship opportunity
- Sample data provided for testing and demonstration
- Open source community for excellent libraries and tools
