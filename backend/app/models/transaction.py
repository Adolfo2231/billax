from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    plaid_transaction_id = db.Column(db.String(255), unique=True, nullable=False)
    account_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic transaction info
    name = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    authorized_date = db.Column(db.Date, nullable=True)
    
    # Merchant info
    merchant_name = db.Column(db.String(255), nullable=True)
    merchant_entity_id = db.Column(db.String(255), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    
    # Categories
    category_primary = db.Column(db.String(100), nullable=True)
    category_detailed = db.Column(db.String(100), nullable=True)
    category_confidence = db.Column(db.String(50), nullable=True)
    
    # Payment info
    payment_channel = db.Column(db.String(50), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    pending = db.Column(db.Boolean, default=False)
    
    # Location info
    location_address = db.Column(db.String(500), nullable=True)
    location_city = db.Column(db.String(100), nullable=True)
    location_region = db.Column(db.String(100), nullable=True)
    location_postal_code = db.Column(db.String(20), nullable=True)
    location_country = db.Column(db.String(100), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lon = db.Column(db.Float, nullable=True)
    
    # Metadata
    transaction_type = db.Column(db.String(50), nullable=True)
    transaction_code = db.Column(db.String(50), nullable=True)
    check_number = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.name} - ${self.amount} - {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'plaid_transaction_id': self.plaid_transaction_id,
            'account_id': self.account_id,
            'name': self.name,
            'amount': float(self.amount),
            'date': self.date.isoformat() if self.date else None,
            'authorized_date': self.authorized_date.isoformat() if self.authorized_date else None,
            'merchant_name': self.merchant_name,
            'logo_url': self.logo_url,
            'website': self.website,
            'category_primary': self.category_primary,
            'category_detailed': self.category_detailed,
            'category_confidence': self.category_confidence,
            'payment_channel': self.payment_channel,
            'pending': self.pending,
            'location': {
                'address': self.location_address,
                'city': self.location_city,
                'region': self.location_region,
                'postal_code': self.location_postal_code,
                'country': self.location_country,
                'lat': self.location_lat,
                'lon': self.location_lon
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 