from flask import Flask, render_template, url_for, request, flash, redirect, session, abort, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re


app = Flask(__name__)


SECRET_KEY = '0461dfa311dbd21fe6b55cd70b61dfcf7afadb56'
DEBUG = True

app.config['SECRET_KEY'] = SECRET_KEY
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notices.db'
db = SQLAlchemy(app)


class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='notices')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Notice' + str(self.id)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return 'Notice' + str(self.id)


def is_valid_email(email):
    pattern = r'^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
    return re.match(pattern, email)


@app.route('/')
def home():
    if 'userLogged' in session:
        all_notices = Notice.query.all()
        user = User.query.first()
        username = session['userLogged']
        return render_template('home.html', user=user, notices=all_notices, username=username)
    else:
        return render_template('login.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('home'))
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['userLogged'] = username
            return redirect('/')
        else:
            flash('Невірне ім\'я користувача або пароль', category='error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('userLogged', None)
    session.pop('busket', None)
    return redirect(url_for('login'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', category='error')
            return redirect('/registration')

        if not email or not is_valid_email(email):
            flash('Invalid email address', category='error')
            return redirect('/registration')

        if len(password) < 8:
            flash('Password must be at least 8 characters long', category='error')
            return redirect('/registration')

        new_user = User(username=username, email=email, firstname=firstname, lastname=lastname, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now login.', category='success')
        return redirect('/login')

    return render_template('registration.html')


@app.route('/profile/<string:username>', methods=['GET', 'POST'])
def profile(username):
    if 'userLogged' not in session:
        return redirect('/login')
    elif session['userLogged'] != username:
        abort(401)
    user = User.query.filter_by(username=username).first()
    notices = Notice.query.filter_by(userid=user.id).all()
    return render_template('profile.html', user=user, notices=notices)


@app.route('/new', methods=['GET', 'POST'])
def new_notice():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']

        if int(price) < 1:
            flash('Price must not be 0 or negative', category='error')
            return redirect('/new')

        if len(title) < 8:
            flash('Title must be at least 8 characters long', category='error')
            return redirect('/new')

        if len(description) < 10:
            flash('Descrition must be at least 10 characters long', category='error')
            return redirect('/new')
        current_user = User.query.filter_by(username=session['userLogged']).first()
        notice = Notice(title=title, price=price, description=description, user=current_user)
        db.session.add(notice)
        db.session.commit()

        flash('Notice was created!', category='success')
        return redirect('/')

    return render_template('new_notice.html')


@app.route("/delete/<int:id>/")
def delete(id):
    notice = Notice.query.get_or_404(id)
    if notice.user.username == session['userLogged']:
        db.session.delete(notice)
        db.session.commit()
    else:
        flash('You can delete your notice only', category='error')
        return redirect('/profile/' + session['userLogged'])
    return redirect('/profile/' + session['userLogged'])


@app.route("/edit/<int:id>/", methods=['GET', 'POST'])
def edit(id):
    notice = Notice.query.get_or_404(id)
    if notice.user.username == session['userLogged']:
        if request.method == "POST":
            if notice.user.username == session['userLogged']:
                notice.title = request.form['title']
                notice.description = request.form['description']
                notice.price = request.form['price']
                db.session.commit()
                flash('Notice was edited!', category='success')
                return redirect('/profile/' + session['userLogged'])
        else:
            return render_template("edit.html", notice=notice)
    else:
        flash('You can edit your notice only', category='error')
        return redirect('/profile/' + session['userLogged'])


@app.route("/buy/<int:id>/", methods=['GET', 'POST'])
def add_to_busket(id):
    if 'busket' not in session:
        session['busket'] = []

    notice = Notice.query.get_or_404(id)
    if notice.user.username != session['userLogged']:
        if not any(item['id'] == id for item in session['busket']):
            notice_list = {
                'id': notice.id,
                'title': notice.title,
                'price': notice.price
            }
            session['busket'].append(notice_list)
            flash('You added notice to busket', category='success')
            print(session['busket'])
            return redirect('/')
        else:
            flash('You can\'t buy notice twice', category='error')
            return redirect('/')
    else:
        flash('You can\'t buy your notice', category='error')
        return redirect('/')


@app.route("/remove_from_cart", methods=['POST'])
def remove_from_cart():
    if 'busket' in session:
        item_index = int(request.form.get('item_id'))
        for i, item in enumerate(session['busket']):
            if item['id'] == item_index:
                del session['busket'][i]
                return jsonify({'success': True})
    return jsonify({'success': False})


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error404.html'), 404


@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)