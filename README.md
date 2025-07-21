# 💼 Billax – AI-Powered Personal Finance Assistant

[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![Plaid](https://img.shields.io/badge/Plaid-API-purple.svg)](https://plaid.com/)

**Billax** is an intelligent personal finance assistant that helps you understand, organize, and project your finances with AI-powered insights and real-time bank integration.

## 🚀 Live Demo

- **Landing Page**: [View Landing Page](https://adolfo2231.github.io/billax)
- **GitHub Repository**: [View Source Code](https://github.com/Adolfo2231/billax)

## ✨ Key Features

### 🏦 **Bank Account Integration**
- Connect your bank accounts securely with Plaid integration
- Real-time transaction synchronization
- Automatic categorization of spending patterns
- Support for multiple financial institutions

### 🤖 **AI Financial Assistant**
- Ask questions about your finances in natural language
- Get intelligent insights and spending recommendations
- Personalized financial advice based on your habits
- 24/7 AI-powered support

### 📊 **Smart Analytics & Goals**
- Visual progress tracking for financial goals
- Detailed spending analytics and reports
- Budget planning and monitoring
- Savings target management

### 💳 **Debt Management**
- Track multiple debts and credit cards
- Apply snowball or avalanche strategies

### 🧾 **Transaction Management**
- Comprehensive transaction history
- Advanced filtering and search
- Receipt and document storage

## 🛠️ Technology Stack

### **Frontend**
- **React.js** - Modern UI framework
- **CSS3** - Custom styling with animations
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication

### **Backend**
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database

### **External Integrations**
- **OpenAI GPT-4** - AI-powered financial insights
- **Plaid API** - Bank account integration
- **JWT** - Secure authentication
- **Flask-Mail** - Email notifications

### **DevOps**
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server and reverse proxy

## 📱 Screenshots

### Landing Page
![Landing Page](https://via.placeholder.com/800x400/11998e/ffffff?text=Billax+Landing+Page)

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/38ef7d/ffffff?text=Billax+Dashboard)

### AI Chat
![AI Chat](https://via.placeholder.com/800x400/667eea/ffffff?text=AI+Financial+Assistant)

## 🚀 Quick Start

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- PostgreSQL (v15 or higher)
- Docker and Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Adolfo2231/billax.git
   cd billax
   ```

2. **Start with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

3. **Manual Setup**

   **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   flask run
   ```

   **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Environment Configuration**
   
   Create `.env` files in both `backend/` and `frontend/` directories:
   
   **Backend (.env):**
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://username:password@localhost/billax
   JWT_SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   PLAID_CLIENT_ID=your-plaid-client-id
   PLAID_SECRET=your-plaid-secret
   ```

## 📊 Project Structure

```
billax/
├── frontend/                 # React.js frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   │   ├── Landing.jsx  # Landing page
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── ...
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API services
│   │   └── contexts/        # React contexts
│   └── public/
├── backend/                  # Flask backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── extensions/     # Flask extensions
│   ├── migrations/         # Database migrations
│   └── requirements.txt
├── docker-compose.yml       # Docker configuration
└── README.md
```

## 🎯 Portfolio Project Features

This project was developed as a **Portfolio Project** for Holberton School, demonstrating:

- ✅ **Full-stack development** with modern technologies
- ✅ **Professional landing page** with responsive design
- ✅ **AI integration** for intelligent financial insights
- ✅ **Real-time bank integration** via Plaid API
- ✅ **Secure authentication** and user management
- ✅ **Containerized deployment** with Docker
- ✅ **Professional documentation** and code organization

## 👨‍💻 Developer

**Adolfo Rodriguez**
- **Role**: Full Stack Developer & Software Architect
- **LinkedIn**: [Adolfo Rodriguez](https://www.linkedin.com/in/adolfo-rodriguez-22b178330/)
- **GitHub**: [Adolfo2231](https://github.com/Adolfo2231)


## 🔒 Security Features

- JWT-based authentication
- Secure API endpoints
- Encrypted data transmission
- Plaid's bank-level security
- Environment variable protection

## 🚀 Deployment

### GitHub Pages (Landing Page)
```bash
cd frontend
npm install --save-dev gh-pages
npm run deploy
```

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
