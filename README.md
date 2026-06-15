# HIDCAS - Document Management System with RAG & Chat

A full-stack application for document management with Role-Based Access Control (RBAC), OCR capabilities, and AI-powered chat using Retrieval Augmented Generation (RAG).

## Features

✅ **User Authentication** - Secure login and registration  
✅ **RBAC System** - Role-based permissions (User, Admin)  
✅ **Document Management** - Upload, view, and delete documents  
✅ **OCR Service** - Extract text from images and documents  
✅ **Embedding Service** - Generate vector embeddings for documents  
✅ **RAG Chat** - AI-powered chat with document context  
✅ **Chunking Service** - Smart document chunking for processing  

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript
- Responsive Design

## Local Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/HIDCAS.git
cd HIDCAS
```

### 2. Setup Backend
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows
source venv/bin/activate    # On Mac/Linux

pip install -r backend/requirements.txt
```

### 3. Configure Database
```bash
# Create database
createdb hidcas

# Update backend/.env.local with your credentials
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hidcas
```

### 4. Run Backend
```bash
cd backend
python -m uvicorn main:app --reload
```
Backend runs on: `http://localhost:8000`

### 5. Open Frontend
- Open `Frontend/index.html` in your browser
- Or use Live Server extension in VS Code

## Deployment

### Deploy to Render (Recommended - Free)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed steps.

Quick summary:
1. Push code to GitHub
2. Create backend service on Render.com
3. Create frontend static site on Render.com
4. Update API endpoint in Frontend
5. Get live URL

## API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document
- `DELETE /documents/{id}` - Delete document

### Chat
- `POST /chat/` - Send chat message
- `GET /chat/history` - Get chat history

### Admin
- `POST /rbac/permissions` - Manage permissions
- `GET /rbac/roles` - List roles

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
ENVIRONMENT=development|production
SECRET_KEY=your-secret-key
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

**Backend won't start:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Run: `pip install -r backend/requirements.txt`

**Database connection error:**
- Ensure `hidcas` database exists
- Check credentials in .env file
- PostgreSQL service must be running

**Frontend API errors:**
- Update `API_BASE` in Frontend/script.js
- Check CORS settings in backend/main.py
- Verify backend is running

## File Structure

```
HIDCAS/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── database.py       # Database setup
│   ├── models.py         # SQLAlchemy models
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── requirements.txt  # Python dependencies
│   └── .env.local        # Local config
├── Frontend/
│   ├── index.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── script.js         # Frontend logic
│   └── style.css         # Styling
└── Vector_Store/         # Document indexes
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

---

**Project Version:** 1.0  
**Last Updated:** 2026-06-16  
**Status:** ✅ Production Ready
