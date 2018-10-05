from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from gem import login,db
from flask import flash
from datetime import datetime


@login.user_loader
def userloader(id):
	return User.query.get(int(id))

friends = db.Table('friends',
	db.Column('userID',db.Integer,db.ForeignKey('user.id')),
	db.Column('friendID',db.Integer,db.ForeignKey('user.id'))
)

group_helper_table = db.Table('group_helper_table',
	db.Column('userID',db.Integer,db.ForeignKey('user.id')),
	db.Column('groupID',db.Integer,db.ForeignKey('groups.id'))
)

class User(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(100),index=True)
	username=db.Column(db.String(100),index=True,unique=True)
	email=db.Column(db.String(150),index=True,unique=True)
	pno=db.Column(db.String(20),index=True,unique=True)
	password=db.Column(db.String(100))
	city=db.Column(db.String(50))
	dob = db.Column(db.Date)
	gender = db.Column(db.String)
	friends=db.relationship('User',
		secondary=friends,
		primaryjoin=(friends.c.userID==id),
		secondaryjoin=(friends.c.friendID==id),
		lazy='dynamic'
	)

	def __repr__(self):
		return 'Username:{} ID:{}'.format(self.username,self.id)

	def add_friend(self,user):
		if not self.is_friend(user):
			self.friends.append(user)
			user.friends.append(self)
			db.session.commit()
		else:
			flash('Already friends')

	def remove_friend(self,user):
		if self.is_friend(user):
			self.friends.remove(user)
			user.friends.remove(self)
			db.session.commit()

	def is_friend(self,user):
		return self.friends.filter(
			friends.c.friendID==user.id).count()>0	

	def	set_password(self,pswd):
		self.password=generate_password_hash(pswd)

	def check_password(self,pswd):
		return check_password_hash(self.password,pswd)

class Balance(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	payerID=db.Column(db.Integer,db.ForeignKey('user.id'))
	receiverID=db.Column(db.Integer,db.ForeignKey('user.id'))
	balance=db.Column(db.Float)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)

	payer=db.relationship('User',foreign_keys=payerID,backref=db.backref('pay', lazy='dynamic'))
	receiver=db.relationship('User',foreign_keys=receiverID	,backref=db.backref('receive', lazy='dynamic'))

	def __repr__(self):
		return '{} owes {} --> {}'.format(self.payer.username,self.receiver.username,self.balance)

class Tpay(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	transaction_id=db.Column(db.Integer,db.ForeignKey('group_transactions.id'))
	p=db.Column(db.String(150),db.ForeignKey('user.id'))
	amount=db.Column(db.Float)
	payer=db.relationship('User',foreign_keys=p,backref=db.backref('group_me_pay',lazy='dynamic',cascade="all,delete"))
	transid=db.relationship('Group_transactions',foreign_keys=transaction_id,backref=db.backref('payers',lazy='dynamic',cascade="all,delete"))

class Tshare(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	transaction_id=db.Column(db.Integer,db.ForeignKey('group_transactions.id'))
	p=db.Column(db.String(150),db.ForeignKey('user.id'))
	amount=db.Column(db.Float)
	person=db.relationship('User',foreign_keys=p,backref=db.backref('group_me_share',lazy='dynamic',cascade="all,delete"))
	transid=db.relationship('Group_transactions',foreign_keys=transaction_id,backref=db.backref('splitters',lazy='dynamic',cascade="all,delete"))	


class Group_transactions(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	desc=db.Column(db.String(100))
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
	added_by=db.Column(db.String(100))
	grp=db.Column(db.Integer,db.ForeignKey('groups.id'))
	tot=db.Column(db.Float)

class Group_settle(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	giverID=db.Column(db.Integer,db.ForeignKey('user.id'))
	receiverID=db.Column(db.Integer,db.ForeignKey('user.id'))
	amt=db.Column(db.Float)
	groupID=db.Column(db.Integer,db.ForeignKey('group_transactions.id'))

	giver=db.relationship('User',foreign_keys=giverID,backref=db.backref('g_pay', lazy='dynamic'))
	receiver=db.relationship('User',foreign_keys=receiverID	,backref=db.backref('g_receive', lazy='dynamic'))
	group=db.relationship('Group_transactions',foreign_keys=groupID,backref=db.backref('neededtrans',lazy='dynamic'))

class Groups(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(100))
	num_mem=db.Column(db.Integer)
	creator=db.Column(db.String(100))
	when=db.Column(db.DateTime,default=datetime.utcnow,index=True)
	description=db.Column(db.String(200))
	transactions=db.relationship('Group_transactions',backref='group',lazy='dynamic',cascade="all,delete")
	members=db.relationship('User',
		secondary=group_helper_table,
		backref=db.backref('groups', lazy='dynamic'),lazy='dynamic')

	def add_mem(self,user):
		if not self.is_mem(user):
			self.members.append(user)
			#user.groups.append(self)
			db.session.commit()
		else:
			flash('Already member')

	def remove_mem(self,user):
		if self.is_mem(user):
			self.members.remove(user)
			#user.groups.remove(self)
			db.session.commit()

	def is_mem(self,user):
		return self.members.filter(
			group_helper_table.c.userID==user.id).count()>0	

class ActivityLog(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	user_id=db.Column(db.Integer)
	activity=db.Column(db.String(200))