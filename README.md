# ExpenseSense Pro - Backend API

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Server will run on: `http://localhost:5000`

### API Endpoints

- `GET /` - API info
- `GET /api/health` - Health check
- `POST /api/signup` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/add_expense` - Add expense
- `GET /api/expenses/<user_id>` - Get expenses
- `GET /api/analysis/<user_id>` - Get analysis

## 📦 Deployment (Render)

1. Push code to GitHub
2. Connect to Render.com
3. Create Web Service
4. Deploy!

**Environment Variables:**
- `SECRET_KEY` - Your secret key
- `PORT` - Auto-set by Render

## 🔧 Tech Stack

- Flask 3.1.3
- Flask-CORS
- Pandas
- NumPy
- Scikit-learn
