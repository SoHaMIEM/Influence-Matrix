from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    budget = IntegerField('Budget', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])
    submit = SubmitField('Create Campaign')

class AdRequestForm(FlaskForm):
    campaign_id = IntegerField('Campaign ID', validators=[DataRequired()])
    influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = IntegerField('Payment Amount', validators=[DataRequired()])
    submit = SubmitField('Create Ad Request')
