from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import db, login_manager
from models import User, Campaign, AdRequest
from forms import LoginForm, CampaignForm, AdRequestForm

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html')
    elif current_user.role == 'sponsor':
        return render_template('sponsor_dashboard.html')
    elif current_user.role == 'influencer':
        return render_template('influencer_dashboard.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        new_campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            sponsor_id=current_user.id
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('campaign.html', form=form)

@main.route('/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request():
    form = AdRequestForm()
    if form.validate_on_submit():
        new_ad_request = AdRequest(
            campaign_id=form.campaign_id.data,
            influencer_id=form.influencer_id.data,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status='Pending'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad Request created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('ad_request.html', form=form)
