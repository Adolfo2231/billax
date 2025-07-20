from flask_cors import CORS

def init_cors(app):
    """Initialize CORS with production and development origins"""
    origins = [
        "http://localhost:3000",  # Development
        "https://adolfo2231.github.io"  # Production - GitHub Pages
    ]
    CORS(app, origins=origins, supports_credentials=True)

cors = CORS()