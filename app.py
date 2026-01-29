import os
from flask import Flask, render_template, redirect, url_for, abort, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_migrate import Migrate

from models import db, Admin, House, Captain, Member, Achievement

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kj3hegh32h4u5gj34nb312cuh4iry8fd7df7d89d8796asuhjc437726fhbejbuy23yuhbe32g43'  

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = Admin.query.get(int(user_id))
    if user:
        return user
    return Captain.query.get(int(user_id))

@app.route('/')
def home():
    houses = House.query.all()
    return render_template('homepage.html', houses=houses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = (
            Admin.query.filter_by(username=username).first()
            or Captain.query.filter_by(username=username).first()
        )

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            if isinstance(user, Admin):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('captain_dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        abort(403)

    houses = House.query.all()
    return render_template('admin_dashboard.html', houses=houses)

@app.route('/captain_dashboard')
@login_required
def captain_dashboard():
    if not isinstance(current_user, Captain):
        abort(403)

    house = House.query.get_or_404(current_user.house_id)
    members = Member.query.filter_by(house_id=house.id).all()
    return render_template(
        'dashboard_captain.html',
        house=house,
        members=members
    )

if __name__ == '__main__':
    app.run(debug=True)
