from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,RadioField,DateField,FloatField,DateTimeField,SelectField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Optional
from gem.models import User
import re

class RegistrationForm(FlaskForm):
	name=StringField('Name',validators=[DataRequired()])
	username=StringField('Username',validators=[DataRequired()])
	email=StringField('Email',validators=[DataRequired(),Email()])
	pno=StringField('Phone No.',validators=[DataRequired()])
	password=PasswordField('password',validators=[DataRequired()])
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	register=SubmitField('Register')

	def validate_username(self,username):
		u=User.query.filter_by(username=username.data).first()
		if u is not None:
			raise ValidationError('Username already taken.')

	def validate_email(self,email):
		u=User.query.filter_by(email=email.data).first()
		if u is not None:
			raise ValidationError('Email already used.')
	
	def validate_pno(self,pno):
		u=User.query.filter_by(pno=pno.data).first()
		if u is not None:
			raise ValidationError('Phone No. already used.')

class LoginForm(FlaskForm):
	username=StringField('Userame',validators=[DataRequired()])
	password=PasswordField('password',validators=[DataRequired()])
	signin=SubmitField('Sign In')

class UpdateProfileForm(FlaskForm):
	name=StringField('Name',validators=[Optional()])
	username=StringField('Username',validators=[Optional()])	
	email=StringField('Email',validators=[Email(),Optional()])
	pno=StringField('Phone No.',validators=[Optional()])
	city=StringField('City',validators=[Optional()])
	gender=RadioField('Gender',choices=[('Male','Male'),('Female','Female'),('Other','Other')],validators=[Optional()])
	save=SubmitField('Save',validators=[Optional()])
	dob = DateField('Date of Birth', format='%Y-%m-%d',validators=[Optional()])
	
	def validate_email(self,email):
		u=User.query.filter_by(email=email.data).first()
		if u is not None and u.username is not current_user.username:
			raise ValidationError('Email already used.')
	
	def validate_pno(self,pno):
		u=User.query.filter_by(pno=pno.data).first()
		if u is not None and u.username is not current_user.username:
			raise ValidationError('Phone No. already used.')

class ChangePasswordForm(FlaskForm):
	current_password=PasswordField('Current Password',validators=[DataRequired()])
	new_password=PasswordField('New Password',validators=[DataRequired()])
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('new_password')])
	change_password=SubmitField('Change Password')	

class AddGroupForm(FlaskForm):
	name=StringField('Group Name',validators=[DataRequired()])
	desc=StringField('Group Description',validators=[Optional()])
	save=SubmitField('Save')

class AddFriendForm(FlaskForm):
	email=StringField('Add Friend',validators=[DataRequired(),Email()])
	addf=SubmitField('Add')

class AddTransactionForm(FlaskForm):
	friend=StringField("Friend's Email",validators=[DataRequired(),Email()])
	money=FloatField("Money",validators=[DataRequired()])
	direction=RadioField('Give or Take',choices=[('1','give'),('0','take'),('2','split equal'),('3','split unequal')],validators=[DataRequired()])
	temp=FloatField('temp',validators=[Optional()])
	addt=SubmitField('Add')

class SettleUpForm(FlaskForm):
	SettleUp=SubmitField('Settle',validators=[Optional()])
	Payer=StringField('Payer',validators=[Optional()])
	Receiver=StringField('Receiver',validators=[Optional()])
	TimeStamp=DateTimeField('DT',validators=[Optional()])
	Balance=FloatField('Bal',validators=[Optional()])

class UnfriendForm(FlaskForm):
	unfriend_id=StringField('Unfriend_id',validators=[Optional()])

def check_paid(form,field):
			if form.pay.data=='2':
				sum=0
				print('out1')
				pattern1=re.compile(' paid:')
				for f in form:
					if pattern1.search(f.label.text)!=None:
						print('in1')
						sum=sum+f.data
				if sum!=field.data:
					raise ValidationError('Amount paid not equal to total')


def check_shared(form,field):
			if form.split.data=='2':
				sum=0
				print('out2')
				pattern1=re.compile(' share:')
				for f in form:
					if pattern1.search(f.label.text)!=None:
						print('in2')
						sum=sum+f.data
				if sum!=field.data:
					raise ValidationError('Amount shared not equal to total')


def form_builder(people):
	class GroupTransactionForm(FlaskForm):
		desc=StringField('Description',validators=[DataRequired()])
		tot=FloatField('Total Amount',validators=[DataRequired(),check_paid,check_shared])
		pay=RadioField('Paid by',choices=[('1','single person'),('2','Multiple people')],validators=[DataRequired()])
		split=RadioField('Split',choices=[('1','equally'),('2','unequally')],validators=[DataRequired()])
		save=SubmitField('save')
		singlepayer=SelectField('Payer',choices=[],coerce=int,validators=[Optional()])


	for (i,ele) in enumerate(people):
		setattr(GroupTransactionForm,'person_pay_%d' %i,FloatField(label=ele+' paid:',validators=[Optional()],default=0))
	for (i,ele) in enumerate(people):
		setattr(GroupTransactionForm,'person_share_%d' %i,FloatField(label=ele+"'s share:",validators=[Optional()],default=0))
	return GroupTransactionForm()

class Settlegroupform(FlaskForm):
	payer=FloatField('payer',validators=[DataRequired()])
	receiver=FloatField('receiver',validators=[DataRequired()])
	amt=FloatField('amt',validators=[DataRequired()])
	settleup=SubmitField('settleup')

class SplitUnequalForm(FlaskForm):
	amount=FloatField('amount',validators=[DataRequired()])
	submit=StringField('Submit')