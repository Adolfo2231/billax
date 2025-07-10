# Billax Frontend

A modern React application for the Billax financial management platform.

## Features

- 🔐 **Authentication System**: Login, register, password reset, and protected routes
- 💬 **AI Chat Assistant**: Integrated financial assistant chat
- 📊 **Dashboard**: Financial overview with summary cards
- 🏦 **Accounts**: Manage and sync user bank accounts
- 💸 **Transactions**: View, filter, and manage user transactions
- 🎨 **Modern UI**: Responsive and clean design
- 🚀 **Best Practices**: Organized code and reusable components

## Tech Stack

- **React 18** (JavaScript)
- **React Router** for navigation
- **Axios** for API communication
- **CSS Modules** and custom styles

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.jsx
│   ├── Input.jsx
│   ├── Layout.jsx
│   ├── Navbar.jsx
│   ├── FloatingChat.jsx
│   └── ProtectedRoute.jsx
├── pages/               # Main and auth pages
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── ForgotPassword.jsx
│   ├── ResetPassword.jsx
│   ├── Dashboard.jsx
│   ├── Accounts.jsx
│   ├── Transactions.jsx
│   └── Chat.jsx
├── services/            # API service modules
│   ├── api.js
│   ├── authService.js
│   ├── accountsService.js
│   ├── transactionService.js
│   ├── plaidService.js
│   └── chatService.js
├── utils/               # Utility functions
│   └── format.js
├── index.jsx            # App entry point
├── App.jsx              # Main app component and routing
└── styles/              # CSS files (in pages/components)
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment variables:
Create a `.env` file in the `frontend/` directory with:
```
REACT_APP_API_BASE_URL=http://localhost:5000/api/v1
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Integration

The frontend is configured to work with the Billax backend API. Make sure the backend is running on `http://localhost:5000` before testing the frontend.

### Main API Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/forgot-password` - Password recovery
- `POST /api/v1/auth/reset-password` - Password reset
- `GET /api/v1/accounts/` - Get user accounts
- `POST /api/v1/accounts/sync-accounts` - Sync accounts
- `GET /api/v1/transaction/transactions` - Get user transactions
- `POST /api/v1/transaction/sync-transactions` - Sync transactions
- `GET /api/v1/transaction/summary` - Get transaction summary
- `GET /api/v1/chat/history` - Get chat history
- `POST /api/v1/chat/` - Send chat message

## Main Modules

### Pages
- **Dashboard**: Shows financial summary and quick stats
- **Accounts**: Manage and sync bank accounts
- **Transactions**: View, filter, and manage transactions
- **Chat**: AI assistant for financial questions
- **Login/Register/Forgot/Reset Password**: User authentication flows

### Components
- **Button, Input**: Reusable form and action elements
- **Layout, Navbar**: App structure and navigation
- **FloatingChat**: Floating AI chat widget
- **ProtectedRoute**: Route guard for authenticated access

### Services
- **api.js**: Axios instance with JWT and error handling
- **authService.js**: Authentication API calls
- **accountsService.js**: Account management API calls
- **transactionService.js**: Transaction management API calls
- **plaidService.js**: Plaid integration for bank linking
- **chatService.js**: Chat/AI assistant API calls

### Utils
- **format.js**: Shared helpers for formatting currency, dates, and account icons

## Contributing

- Use functional components and React hooks
- Keep code clean and DRY
- Write clear commit messages
- Do not commit sensitive data (like `.env`)

## License

This project is part of the Billax financial management platform.
