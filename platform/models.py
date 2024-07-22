from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    niche = db.Column(db.String(120), nullable=True)
    dob = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)
    goals = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    niche = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    flagged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('campaigns', lazy=True))

    def __repr__(self):
        return f'<Campaign {self.name}>'

class Influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(250), nullable=True)
    niche = db.Column(db.String(120), nullable=True)
    reach = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(120), nullable=True)
    bank_balance = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('influencers', lazy=True))

    def __repr__(self):
        return f'<Influencer {self.name}>'

class CampaignRequest(db.Model):
    __tablename__ = 'campaign_request'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completion_confirmed = db.Column(db.Boolean, default=False)
    payment_done = db.Column(db.Boolean, default=False)
    rating_done = db.Column(db.Boolean, default=False)

    campaign = db.relationship('Campaign', backref=db.backref('requests', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('requests', lazy=True))

    def __repr__(self):
        return f'<CampaignRequest {self.id}>'

class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    campaign = db.relationship('Campaign', backref=db.backref('bookmarks', lazy=True))
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))

    def __repr__(self):
        return f'<Bookmark {self.id}>'

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('campaign_request.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)

    influencer = db.relationship('Influencer', backref=db.backref('transactions', lazy=True))
    ad_request = db.relationship('CampaignRequest', backref=db.backref('transactions', lazy=True))
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.id}>'

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    transaction = db.relationship('Transaction', backref=db.backref('ratings', lazy=True))
    rater = db.relationship('User', foreign_keys=[rater_id], backref=db.backref('given_ratings', lazy=True))
    ratee = db.relationship('User', foreign_keys=[ratee_id], backref=db.backref('received_ratings', lazy=True))

    def __repr__(self):
        return f'<Rating {self.id}>'

with app.app_context():
    db.create_all()