from gem import gem,db
from flask import request,render_template,redirect,flash,url_for
from gem.forms import RegistrationForm,LoginForm,UpdateProfileForm,ChangePasswordForm,AddFriendForm,AddTransactionForm,SettleUpForm,UnfriendForm,AddGroupForm,form_builder,Settlegroupform,SplitUnequalForm
from gem.models import User,Balance,Groups,Group_transactions,Tpay,Tshare,Group_settle,ActivityLog
from flask_login import login_user,logout_user,login_required,current_user
import re


@gem.route('/',methods=['GET','POST'])
@gem.route('/index',methods=['GET','POST'])
@gem.route('/register',methods=['GET','POST'])
def register():
	del mem_list[:]
	if current_user.is_authenticated:
		return redirect(url_for('profile',name=current_user.username))
	form=RegistrationForm()
	if form.validate_on_submit():
		user=User(name=form.name.data,username=form.username.data,email=form.email.data,pno=form.pno.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		user_activity = ActivityLog()
		user_activity.user_id=user.id
		s = "You registered successfully"
		user_activity.activity=s
		db.session.add(user_activity)
		db.session.commit()
		flash('register success')
		return redirect(url_for('login'))
	return render_template('reg.html',form=form)

@gem.route('/groups/<username>',methods=['GET','POST'])
@login_required
def groups(username=None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 1' + " " + username)
		return redirect(url_for('friends',username=current_user.username))
	else:
		return render_template('groups.html',user=current_user)

@gem.route('/disp_trans/<username>/<grpid>/<id>',methods=['GET','POST'])
@login_required
def disp_trans(username=None,id=None,grpid=None):
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 10' + " " + username)
		return redirect(url_for('group',username=current_user.username))
	else:
		form=Settlegroupform()
		grp=Groups.query.filter_by(id=grpid).first()
		if grp is None:
			flash('No such group exists')
			return redirect(url_for('groups',username=current_user.username))
		else:
			tr = Group_transactions.query.filter_by(id=id).first()
			if tr is None:
				flash("Not a valid Transaction")
				return redirect(url_for('disp_group',username=current_user.username,id=grpid))
			else:
				return render_template('disp_trans.html',user=current_user,tr=tr,form3=form)


@gem.route('/disp_group/<username>/<id>',methods=['GET','POST'])
@login_required
def disp_group(username=None,id=None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 1' + " " + username)
		return redirect(url_for('friends',username=current_user.username))
	else:
		a=Groups.query.filter_by(id=id).first()
		if a is None:
			flash('Group Does Not Exist')
			return redirect(url_for('groups',username=current_user.username))
		b=a.members.all()
		z=a.transactions.all()
		li=[]
		li1=[]
		li2=[]
		del li1[:]
		del li2[:]
		for c in b:
			li.append(c.username)
		if current_user.username not in li:
			flash('Access Denied 2')
			del li
			return redirect(url_for('groups',username=current_user.username))
		else:
			del li
			return render_template('disp_group.html',user=current_user,b=b,a=a,z=z)
mem_list=[]

@gem.route('/group_transaction_create/<username>/<idgrp>',methods=['GET','POST'])
@login_required
def group_transaction_create(username=None,idgrp=None,idtrans=None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 1' + " " + username)
		return redirect(url_for('friends',username=current_user.username))
	else:
		grp=Groups.query.filter_by(id=idgrp).first()
		if grp is None:
			flash('No such group exists')
			return redirect(url_for('groups',username=current_user.username))
		else:
			people=[(i.username) for i in grp.members]
			form=form_builder(people)
			singlepayers=[(p.id,p.username) for p in grp.members.all() ]
			form.singlepayer.choices=singlepayers
			if form.validate_on_submit() and form.save.data:
			
					pattern1=re.compile(' paid:')
					pattern2=re.compile(' share:')
				
					t=Group_transactions(desc=form.desc.data,grp=grp.id,added_by=current_user.username,tot=form.tot.data)
					db.session.add(t)
					db.session.commit()
					if form.pay.data == '1':
						tt=User.query.filter_by(username=dict(form.singlepayer.choices).get(form.singlepayer.data)).first()
						q=Tpay(transaction_id=t.id,p=tt.id,amount=form.tot.data)
						#flash(form.singlepayer.data)
						db.session.add(q)
						for m in grp.members:
							if m.username!=dict(form.singlepayer.choices).get(form.singlepayer.data):
								q=Tpay(transaction_id=t.id,p=m.id,amount=0)
								db.session.add(q)
					else:
						for f in form  :
							if pattern1.search(f.label.text)!=None:
								tt=User.query.filter_by(username=f.label.text[:-6]).first()
								q=Tpay(transaction_id=t.id,p=tt.id,amount=f.data)
								db.session.add(q)
					if form.split.data == '2':
						for f in form :
							if pattern2.search(f.label.text)!=None:
								tt=User.query.filter_by(username=f.label.text[:-9]).first()
								w=Tshare(transaction_id=t.id,p=tt.id,amount=f.data)
								db.session.add(w)
					else:
						for m in grp.members:
							w=Tshare(transaction_id=t.id,p=m.id,amount=(form.tot.data/grp.num_mem))
							db.session.add(w)
					db.session.commit()
					user_activity = ActivityLog()
					user_activity.user_id=current_user.id
					s = "Transaction " + str(t.id) + " added"
					user_activity.activity=s
					db.session.add(user_activity)
					db.session.commit()
					flash('transaction added')
					return redirect(url_for('transadj',username=current_user.username,tid=t.id))
			return render_template('group_transaction_add.html',form=form,people=people,user=current_user)	


@gem.route('/transadj/<username>/<tid>')
@login_required
def transadj(username=None,tid=None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 1' + " " + username)
		return redirect(url_for('friends',username=current_user.username))
	else:
		trans=Group_transactions.query.filter_by(id=tid).first()
		if trans is None:
			flash('No such transaction exists')
			return redirect(url_for('groups',username=username))
		else:
			receivers=[]
			givers=[]
			for p in trans.payers.all():
				for q in trans.splitters.all():
					if q.person==p.payer:
						if p.amount>q.amount:
							receivers.append([p,p.amount-q.amount])
						elif q.amount>p.amount:
							givers.append([p,q.amount-p.amount])
			print('r==',receivers)
			print('g==',givers)
			for r in receivers:
				amt=r[1]
				for g in givers :
					if amt>0:
						if g[1]<=0:
							continue
						if g[1]<amt:
							a=Group_settle(giverID=g[0].p,receiverID=r[0].p,amt=g[1],groupID=trans.id)
							amt=amt-g[1]
							g[1]=0
						elif g[1]>amt:
							a=Group_settle(giverID=g[0].p,receiverID=r[0].p,amt=amt,groupID=trans.id)
							g[1]=g[1]-amt
							amt=0
						else:
							a=Group_settle(giverID=g[0].p,receiverID=r[0].p,amt=g[1],groupID=trans.id)
							amt=0
							g[1]=0
					else:
						print('break')
						break
					print(amt,g[1])
					db.session.add(a)
					db.session.commit()

			return redirect(url_for('disp_group',username=username,id=trans.grp))

				



@gem.route('/create_group/<username>',methods=['GET','POST'])
@login_required
def create_group(username=None):
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 3')
		return redirect(url_for('friends',username=current_user.username))
	else:
		val=0
		form_group=AddGroupForm()
		form_mem=AddFriendForm()
		if form_mem.validate_on_submit() and form_mem.addf.data:
			u=User.query.filter_by(email=form_mem.email.data).first()
			if u is None:
				flash('no one found')
			else:
				if current_user.is_friend(u) and u is not current_user:
					if u in mem_list:
						flash('Alredy Member')
					else:
						mem_list.append(u)
						flash(u.name + "added")
				else:
					flash('not in friend list')
		if form_group.validate_on_submit() and form_group.save.data:
			g=Groups()
			g.name=form_group.name.data
			g.description=form_group.desc.data
			g.creator=current_user.username
			g.num_mem=len(mem_list)+1
			db.session.add(g)
			db.session.commit()
			g=Groups.query.filter_by(id=g.id).first()
			g.add_mem(current_user)
			for i in mem_list:
				g=Groups.query.filter_by(id=g.id).first()
				g.add_mem(i)
			del mem_list[:]
			return redirect(url_for('groups',username=current_user.username))
		temp_list=mem_list[:]
		if form_group.save.data:
			return render_template('create_group.html',form_group=form_group,form_mem=form_mem,user=current_user,list=temp_list,val=1)
		elif form_mem.addf.data:
			return render_template('create_group.html',form_group=form_group,form_mem=form_mem,user=current_user,list=temp_list,val=2)
		else:
			return render_template('create_group.html',form_group=form_group,form_mem=form_mem,user=current_user,list=temp_list,val=0)

			

@gem.route('/profile/<name>')
@login_required
def profile(name = None):
	del mem_list[:]
	if name is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif name!=current_user.username:
		flash('Access Denied 4')
		return redirect(url_for('profile',name=current_user.username))
	else:
		user = User.query.filter_by(username=name).first()
		if user:
			return render_template('pd.html',title=user.name,user=user)
		else:
			return redirect(url_for('login'))



@gem.route('/login',methods=['GET','POST'])
def login():
	del mem_list[:]
	if current_user.is_authenticated:
		return redirect(url_for('register'))
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password.')
			return redirect(url_for('login'))
		login_user(user)
		flash('Success!')
		return redirect(url_for('profile',name=user.username))
	return render_template('login.html',title='Sign In',form=form)

@gem.route('/logout')
def logout():
	del mem_list[:]
	logout_user()
	flash('Logout Successfull.')
	return redirect(url_for('login'))

@gem.route('/update_profile/<username>',methods=['GET','POST'])
@login_required
def update_profile(username = None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 5')
		return redirect(url_for('update_profile',username=current_user.username))
	else:
		form=UpdateProfileForm()
		form2=ChangePasswordForm()
		user=User.query.filter_by(username=username).first()
		if form.validate_on_submit() and form.save.data:
			if form.name.data:
				user.name=form.name.data
			if form.email.data:
				user.email=form.email.data
			if form.pno.data:
				user.pno=form.pno.data
			if form.city.data:
				user.city=form.city.data
			if form.gender.data in ['Male','Female','Other']:
				user.gender=form.gender.data
			if form.dob.data:
				user.dob=form.dob.data
			db.session.commit()
			flash('Changes applied successfully.')
		if form2.validate_on_submit() and form2.change_password.data:
			if user.check_password(form2.current_password.data):
				user.set_password(form2.new_password.data)
				flash('Password updated successfully')
				db.session.commit()
				return redirect(url_for('profile',name=user.username))
				flash("Incorrect Password")
			return redirect(url_for('update_profile',username=user.username))
		if form2.change_password.data:
			return render_template('edit_pd.html',user=user,form=form,form2=form2,val=1)
		else:
			return render_template('edit_pd.html',user=user,form=form,form2=form2,val=0)


@gem.route('/friends/<username>',methods=['GET','POST'])
@login_required
def friends(username=None):
	del mem_list[:]
	val=0
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 6')
		return redirect(url_for('friends',username=current_user.username))
	else:
		user=User.query.filter_by(username=username).first()
		form=AddFriendForm()
		form2=AddTransactionForm()
		form3=SettleUpForm()
		form_unfriend=UnfriendForm()
		form_unequal=SplitUnequalForm()
		if form.validate_on_submit() and form.addf.data:
			search=User.query.filter_by(email=form.email.data).first()
			if search is None:
				flash('No one found')
			else:
				user.add_friend(search)
				user_activity = ActivityLog()
				user_activity.user_id=user.id
				s = search.name + "	added successfully"
				user_activity.activity=s
				db.session.add(user_activity)
				db.session.commit()
				flash(search.name + ' added')


		if form2.validate_on_submit() and form2.addt.data:
			f=User.query.filter_by(email=form2.friend.data).first()
			if user.is_friend(f):
				user_activity = ActivityLog()
				friend_activity = ActivityLog()
				user_activity.user_id=user.id
				friend_activity.user_id=f.id
				if form2.direction.data == '1':
					#Owe1.append(user.name + " owes " + f.name + " " + str(form2.money.data))
					a = Balance.query.filter_by(payerID=user.id,receiverID=f.id).first()
					money = form2.money.data
					s= "You owe " + f.name + " " + str(money)
					t= user.name + " owes you " + str(money)
					user_activity.activity=s
					friend_activity.activity=t
					if a is not None:
						a.balance = float(a.balance) + float(form2.money.data)
					else:
						rev_a=Balance.query.filter_by(payerID=f.id,receiverID=user.id).first()
						if rev_a is not None:
							if rev_a.balance > form2.money.data:
								rev_a.balance = float(rev_a.balance) - float(form2.money.data)
							elif rev_a.balance == form2.money.data:
								s= "You and " + f.name + " are Settled"
								t= "You and " + user.name + " are settled"
								user_activity.activity=s
								friend_activity.activity=t
								db.session.delete(rev_a)
								flash('You and {} are settled'.format(f.username))
							else:
								transaction=Balance(payer=user,receiver=f,balance=float(money)-float(rev_a.balance))
								db.session.delete(rev_a)
						else:
							transaction=Balance(payer=user,receiver=f,balance=money)
					db.session.add(user_activity)
					db.session.add(friend_activity)
					# if a is not None and f1 is not None:
					# 	money = int(Balance.query.filter_by(payerID=user.id).first().balance) + int(form2.money.data)
					# else:
					# 	transaction=Balance(payer=user,receiver=f,balance=money)
				elif form2.direction.data =='0':
					#Owe1.append(f.name + " owes " + user.name + " " + str(form2.money.data))
					a = Balance.query.filter_by(payerID=f.id,receiverID=user.id).first()
					money = form2.money.data
					s= f.name + " owes you " + str(money)
					t= "You owe" + user.name + str(money)
					user_activity.activity=s
					friend_activity.activity=t
					if a is not None:
						a.balance = float(a.balance) + float(form2.money.data)
					else:
						rev_a=Balance.query.filter_by(payerID=user.id,receiverID=f.id).first()
						if rev_a is not None:
							if rev_a.balance > form2.money.data:
								rev_a.balance = float(rev_a.balance) - float(form2.money.data)
							elif rev_a.balance == form2.money.data:
								s= "You and " + f.name + " are Settled"
								t= "You and " + user.name + " are settled"
								user_activity.activity=s
								friend_activity.activity=t
								db.session.delete(rev_a)
								flash('You and {} are settled'.format(f.username))
							else:
								transaction=Balance(payer=f,receiver=user,balance=float(money)-float(rev_a.balance))
								db.session.delete(rev_a)
						else:
							transaction=Balance(payer=f,receiver=user,balance=money)
					db.session.add(user_activity)
					db.session.add(friend_activity)
				#db.session.add(transaction)
				elif form2.direction.data == '2':
					a = Balance.query.filter_by(payerID=f.id,receiverID=user.id).first()
					money = form2.money.data
					s= f.name + " owes you " + str(money)
					t= "You owe" + user.name + str(money)
					user_activity.activity=s
					friend_activity.activity=t
					if a is not None:
						a.balance = float(a.balance) + float(money/2)
					else:
						rev_a=Balance.query.filter_by(payerID=user.id,receiverID=f.id).first()
						if rev_a is not None:
							if float(rev_a.balance) > float(money/2):
								rev_a.balance = float(rev_a.balance) - float(money/2)
							elif float(rev_a.balance) == float(money/2):
								s= "You and " + f.name + " are Settled"
								t= "You and " + user.name + " are settled"
								user_activity.activity=s
								friend_activity.activity=t
								db.session.delete(rev_a)
								flash('You and {} are settled'.format(f.username))
							else:
								transaction=Balance(payer=f,receiver=user,balance=float(money)-float(rev_a.balance))
								db.session.delete(rev_a)
						else:
							transaction=Balance(payer=f,receiver=user,balance=money/2)
					db.session.add(user_activity)
					db.session.add(friend_activity)
				elif form2.direction.data == '3':
					# flash('settle_unequal')
					# flash(form2.temp.data)
					a = Balance.query.filter_by(payerID=f.id,receiverID=user.id).first()
					money = float(form2.money.data)-float(form2.temp.data)
					s= f.name + " owes you " + str(money)
					t= "You owe" + user.name + str(money)
					user_activity.activity=s
					friend_activity.activity=t
					if a is not None:
						a.balance = float(a.balance) + float(money)
					else:
						rev_a=Balance.query.filter_by(payerID=user.id,receiverID=f.id).first()
						if rev_a is not None:
							if rev_a.balance > money:
								rev_a.balance = float(rev_a.balance) - float(money)
							elif rev_a.balance == money:
								s= "You and " + f.name + " are Settled"
								t= "You and " + user.name + " are settled"
								user_activity.activity=s
								friend_activity.activity=t
								db.session.delete(rev_a)
								flash('You and {} are settled'.format(f.username))
							else:
								transaction=Balance(payer=f,receiver=user,balance=float(money)-float(rev_a.balance))
								db.session.delete(rev_a)
						else:
							transaction=Balance(payer=f,receiver=user,balance=money)
					db.session.add(user_activity)
					db.session.add(friend_activity)
				db.session.commit()
			else:
				flash('email not in friend list')

		if form.addf.data :
			#render_template('friends.html',form=form,form2=form2,form3=form3,form_unfriend=form_unfriend,user=user,val=1,form_unequal=form_unequal)
			return redirect(url_for('friends',username=current_user.username))
		elif form2.addt.data:
			#return render_template('friends.html',form=form,form2=form2,form3=form3,form_unfriend=form_unfriend,user=user,val=2,form_unequal=form_unequal)
			return redirect(url_for('friends',username=current_user.username))
		else:
			return render_template('friends.html',form=form,form2=form2,form3=form3,form_unfriend=form_unfriend,user=user,val=0,form_unequal=form_unequal)

@gem.route('/settle_entry',methods=["POST"])
@login_required
def settle_entry():
	del mem_list[:]
	print('erfvsd')
	form=SettleUpForm(request.form)
	if request.method == 'POST':
		p=User.query.filter_by(username=form.Payer.data).first()
		r=User.query.filter_by(username=form.Receiver.data).first()
		a=Balance.query.filter_by(payerID=p.id,receiverID=r.id).first()
		if a is not None:
			db.session.delete(a)
			db.session.commit()
			user_activity = ActivityLog()
			friend_activity = ActivityLog()
			user_activity.user_id=p.id
			friend_activity.user_id=r.id
			s= "You and " + r.name + " are Settled"
			t= "You and " + p.name + " are settled"
			user_activity.activity=s
			friend_activity.activity=t
			db.session.add(user_activity)
			db.session.add(friend_activity)
			db.session.commit()
			if current_user == p:
				flash("You and " + r.username + " are now settled")
			else:
				flash("You and " + p.username + " are now settled")

		return redirect(url_for('friends',username=current_user.username))

@gem.route('/settle_trans',methods=["POST"])
@login_required
def settle_trans():
	del mem_list[:]
	form=Settlegroupform(request.form)
	if request.method=='POST':
		g=Group_settle.query.filter_by(giverID=form.payer.data,receiverID=form.receiver.data).first()
		id=g.group.grp
		print(id)
		grp=g.group
		if len(g.group.neededtrans.all())==1:
			db.session.delete(g)
			db.session.delete(grp)
			s= g.group.desc + ' is settled'
			for m in g.group.group.members.all():
				user_activity = ActivityLog()
				user_activity.user_id=m.id
				user_activity.activity=s
				db.session.add(user_activity)
			flash( g.group.desc + ' is settled')
		else:
			db.session.delete(g)
			user_activity = ActivityLog()
			friend_activity = ActivityLog()
			user_activity.user_id=g.giver.id
			friend_activity.user_id=g.receiver.id
			s= g.giver.name + ' and ' + g.receiver.name + " are Settled in Group " + g.group.group.name
			user_activity.activity=s
			friend_activity.activity=s
			db.session.add(user_activity)
			db.session.add(friend_activity)
			flash(g.giver.username+ ' and '+ g.receiver.username+ ' are settled')
		db.session.commit()
		return redirect(url_for('disp_group',username=current_user.username,id=id))

@gem.route('/unfriend',methods=["POST"])
@login_required
def unfriend():
	del mem_list[:]
	form=UnfriendForm(request.form)
	if request.method == 'POST':
		del_frnd=User.query.filter_by(username=form.unfriend_id.data).first()
		if del_frnd is not None:
			bal1=Balance.query.filter_by(payerID=current_user.id,receiverID=del_frnd.id).first()
			bal2=Balance.query.filter_by(receiverID=current_user.id,payerID=del_frnd.id).first()
			if bal1 or bal2:
				flash('transactions pending')
			else:
				current_user.remove_friend(del_frnd)
		return redirect(url_for('friends',username=current_user.username))

@gem.route('/activity/<username>',methods=['GET','POST'])
@login_required
def activity(username=None):
	del mem_list[:]
	if username is None:
		flash('Please login to proceed.')
		return redirect(url_for('login'))
	elif username!=current_user.username:
		flash('Access Denied 7')
		return redirect(url_for('activity',username=current_user.username))
	else:
		a = ActivityLog.query.filter_by(user_id=current_user.id).all()
		# for i in a:
		# 	flash(i.activity)
		return render_template('activity.html',user=current_user,a=a)
