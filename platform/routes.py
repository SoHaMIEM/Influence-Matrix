from flask import Flask, send_from_directory, render_template, request, redirect, url_for, flash, session
import os
from app import app
from models import db, User, Campaign, CampaignRequest, Bookmark, Influencer, Transaction, Rating, Sponsor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps


def admin_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session: 
            flash('Please login to continue')
            return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user.role=='Admin':
            flash("You are not authorized to access this page")
            return redirect(url_for('index'))
        return func(*args,**kwargs)
    return inner

def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else: 
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')



@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if not email or not password or not role:
        flash('Please fill out all the fields')
        return redirect(url_for('login'))
    user=User.query.filter_by(email=email).first()

    if not user:
        flash('User does not exist')
        return redirect(url_for('login'))
    
    if not check_password_hash(user.password, password):
        flash('Incorrect password')
        return redirect(url_for('login'))

    if user.role != role:
        flash('Incorrect role selected')
        return redirect(url_for('login'))
    
    session['user_id'] = user.id


    if role == 'Influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        if influencer and influencer.profile_picture and influencer.niche and influencer.platform and influencer.reach:
            return render_template('influencer.html')
        else:
            return redirect(url_for('complete_profile'))
    elif role == 'Admin':
        return redirect(url_for('admin'))
    elif role == 'Sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        if sponsor and sponsor.profile_picture and sponsor.company and sponsor.bank_balance:
            return render_template('sponsor.html',sponsor=sponsor)
        else:
            return redirect(url_for('complete_sponsor_profile'))
    

    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    email = request.form.get('email')
    dob = request.form.get('dob')
    password = request.form.get('password')
    role = request.form.get('role')
    niche = request.form.get('niche')

    if not name or not email or not dob or not password or not role or not niche:
        flash('Please fill out all the fields')
        return redirect(url_for('register'))
    
    user=User.query.filter_by(email=email).first()

    if user:
        flash('Username already exists')
        return redirect(url_for('register'))
    
    password_hash = generate_password_hash(password)

    dob = datetime.strptime(dob, '%Y-%m-%d').date()
    new_user = User(email=email,name=name,password=password_hash,dob=dob,role=role,niche=niche)
    
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))





@app.route('/profile')
@auth_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/complete_profile')
def complete_profile():
    return render_template('complete_profile.html')

@app.route('/complete_profile', methods=['POST'])
@auth_required
def complete_profile_post():

    if request.method == 'POST':
        profile_pic = request.form.get('profile_picture')
        platform = request.form.get('platform')
        niche = request.form.get('niche')
        reach = request.form.get('reach')

        if not profile_pic or not reach or not platform or not niche:
            flash('Please fill out all the fields')
            return redirect(url_for('complete_profile'))

        influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
        if not influencer:
            user = User.query.get(session['user_id'])
            influencer = Influencer(
                user_id=user.id,
                name=user.name,
                email=user.email,
                profile_picture=profile_pic,
                platform=platform,
                niche=niche,
                reach=reach,
                bank_balance=0.0,  
                flagged=False
            )
            db.session.add(influencer)
        else:
            influencer.profile_picture = profile_pic
            influencer.platform = platform
            influencer.niche = niche
            influencer.reach = reach

        db.session.commit()
        flash('Profile updated successfully')
        return render_template('influencer.html',influencer=influencer)
        
    return redirect(url_for('complete_profile'))
    




@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    email = request.form.get('email')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    name = request.form.get('name')

    if not email or not cpassword or not password:
        flash('Please fill out all the required fields')
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not check_password_hash(user.password, cpassword):
        flash('Incorrect password')
        return redirect(url_for('profile'))
    
    if email != user.email:
        new_email = User.query.filter_by(email=email).first()
        if new_email:
            flash('Username already exists')
            return redirect(url_for('profile'))
    
    new_password_hash = generate_password_hash(password)
    user.email = email
    user.password = new_password_hash
    user.name = name
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))



@app.route('/complete_sponsor_profile')
@auth_required
def complete_sponsor_profile():
    return render_template('complete_sponsor_profile.html')


@app.route('/complete_sponsor_profile', methods=['POST'])
@auth_required
def complete_sponsor_profile_post():
    if request.method == 'POST':
        profile_pic = request.form.get('profile_picture')
        company = request.form.get('company')
        bank_balance = request.form.get('bank_balance')

        if not profile_pic or not company or not bank_balance:
            flash('Please fill out all the fields')
            return redirect(url_for('complete_sponsor_profile'))

        sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if not sponsor:
            user = User.query.get(session['user_id'])
            sponsor = Sponsor(
                user_id=user.id,
                name=user.name,
                email=user.email,
                profile_picture=profile_pic,
                company=company,
                bank_balance=bank_balance,  
                flagged=False
            )
            db.session.add(sponsor)
        else:
            sponsor.profile_picture = profile_pic
            sponsor.company = company
            sponsor.bank_balance = bank_balance

        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('sponsor'))
        
    return redirect(url_for('complete_sponsor_profile'))



@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')


#Sponsor------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/sponsor')
@auth_required
def sponsor():
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
    
    campaigns = Campaign.query.all()

    return render_template('sponsor.html', sponsor=sponsor, campaigns=campaigns)



@app.route('/add_campaign')
@auth_required
def add_campaign():
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
    return render_template('add_campaign.html',sponsor=sponsor)


@app.route('/edit_campaign')
@auth_required
def edit_campaign():
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
    campaign = Campaign.query.all()
    return render_template('edit_campaign.html',sponsor=sponsor, campaign=campaign)


@app.route('/find_influencer')
@auth_required
def find_influencer():
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
    return render_template('influencer.html',influencer=influencer,sponsor=sponsor)




#Sponsor CRUD------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/sponsor/<int:id>', methods=['GET'])
@auth_required
def view_campaign(id):
    campaign = Campaign.query.get_or_404(id)  
    return render_template('sponsor.html', campaign=campaign)



@app.route('/add_campaign', methods=['POST'])
@auth_required
def add_campaign_post():
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    goals = request.form.get('goals')
    niche = request.form.get('niche')
    user_id = session['user_id']
    visibility = request.form.get('visibility')
    if not name or not description or not start_date or not end_date or not niche or not budget or not goals:
        flash('Please fill out all fields')
        return redirect(url_for('add_campaign'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    campaign = Campaign(name=name,description=description,start_date=start,end_date=end,niche=niche,goals=goals,budget=budget,status="No",flagged=False,user_id=user_id,visibility=visibility)
    db.session.add(campaign)
    db.session.commit()

    flash('Campaign added successfully')
    return redirect(url_for('sponsor'))
    



@app.route('/edit_campaign/<int:id>', methods=['GET', 'POST'])
@auth_required
def edit_campaign_post(id):
    # Ensure user is logged in
    campaign = Campaign.query.get_or_404(id)

    # Ensure the user has permission to edit this campaign
    if campaign.user_id != session['user_id']:
        flash('You do not have permission to edit this campaign.', 'danger')
        return redirect(url_for('sponsor'))

    if request.method == 'POST':
        # Get data from form
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = request.form['start_date']
        campaign.end_date = request.form['end_date']
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form.get('goals')
        campaign.niche = request.form.get('niche')
        campaign.status = request.form['status']
        
        # Commit changes to the database
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('sponsor'))

    # Render the edit form with the current campaign details
    return render_template('edit_campaign.html', campaign=campaign)





@app.route('/sponsor/<int:id>', methods=['POST'])
@auth_required
def delete_campaign(id):
    print(id)
    campaign = Campaign.query.get_or_404(id)  
    try:
        db.session.delete(campaign)  
        db.session.commit()  
        flash('Campaign deleted successfully.', 'success')  
    except Exception as e:
        db.session.rollback()  
        flash('An error occurred while deleting the campaign. Please try again.', 'danger')
    return redirect(url_for('sponsor'))



@app.route('/ajaxfile', methods=['POST'])
def ajaxfile():
    user_id = request.form.get('userid')
    # Query the database for user details
    user = db.session.query(User).filter_by(id=user_id).first()  # Adjust this line based on your User model

    if user:
        # Render the user information as HTML
        html = render_template('response.html', employeelist=[user])
        return html
    return "User not found", 404

















#Influencer-----------------------------------------------------------------------------------------------------------------------------------------



@app.route('/influencer')
def influencer():
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    campaign = Campaign.query.all()
    return render_template('influencer.html',campaign,influencer)
    




