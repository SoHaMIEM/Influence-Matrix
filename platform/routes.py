from flask import Flask, send_from_directory, render_template, request, redirect, url_for, flash, session
import os
from app import app
from models import db, User, Campaign, CampaignRequest, Bookmark, Influencer, Transaction, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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

@app.route('/complete_profile')
def complete_profile():
    return render_template('complete_profile.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/sponsor')
def sponsor():
    return render_template('sponsor.html')

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
    

    if role == 'Influencer':
        return redirect(url_for('complete_profile'))
    elif role == 'Admin':
        return redirect(url_for('admin'))
    elif role == 'Sponsor':
        return redirect(url_for('sponsor'))

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

