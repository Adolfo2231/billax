from flask_cors import CORS

def init_cors(app):
    """Initialize CORS with production and development origins"""
    origins = [
        "http://localhost:3000",  # Development
        "http://localhost:5000",  # Development (Flask default)
        "https://adolfo2231.github.io",  # Production - GitHub Pages
        "https://adolfo2231.github.io/billax",  # Production - GitHub Pages with path
        "https://billax-production.up.railway.app"  # Railway domain (for testing)
    ]
    
    CORS(app, 
         origins=origins, 
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type", "Authorization"])

cors = CORS()