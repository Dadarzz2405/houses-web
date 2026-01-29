import os
from flask import Flask, render_template, redirect, url_for, abort, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from functools import wraps

from models import Announcement, PointTransaction, db, Admin, House, Captain, Member, Achievement

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def captain_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Captain):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    user = Admin.query.get(int(user_id))
    if user:
        return user
    return Captain.query.get(int(user_id))
#=========================================================
#=========================================================
#=========================================================
@app.route('/')
def home():
    houses = House.query.order_by(House.name).all()
    return render_template('homepage.html', houses=houses)

@app.route('/live-scores')
def live_scores():
    houses = House.query.order_by(House.house_points.desc()).all()
    for rank, house in enumerate(houses, start=1):
        house.rank = rank
    return render_template('live_scores.html', houses=houses)

@app.route('/members')
def members():
    house_filter = request.args.get('house')
    if house_filter:
        house = House.query.filter_by(name=house_filter).first_or_400()
        houses = [house]
    else:
        houses = House.query.order_by(House.name).all()

    houses_with_members = []
    for house in houses:
        members = Member.query.filter_by(house_id=house.id).all()
        houses_with_members.append({
            'house': house,
            'members': members
        })
    
    all_houses = House.query.order_by(House.name).all()

    return render_template(
        'members.html', 
        houses_with_members=houses_with_members,
        selected_house=house_filter,
        all_houses=all_houses
        )

@app.route('/announcements')
def announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html', announcements=announcements)
#=========================================================
#=========================================================
#=========================================================
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

@app.route('/admin/points/add', methods=['POST'])
@login_required
@admin_required
def admin_add_points():
    house_id = request.form.get('house_id', type=int)
    points = request.form.get('points', type=int)
    reason = request.form.get('reason').strip()

    if not house_id or not points or not reason:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    if points <= 0:
        flash('Points must be a positive integer.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    house = House.query.get_or_404(house_id)

    house.house_points += points

    trasnaction = PointTransaction(
        house_id=house.id,
        points_change=points,
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(trasnaction)
    db.session.commit()
    flash(f'Successfully added {points} points to {house.name}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/points/deduct', methods=['POST'])
@login_required
@admin_required
def admin_deduct_points():
    house_id = request.form('house_id, trype=int')
    points = request.form('points', type=int)
    reason = request.form('reason').strip()

    if not house_id or not points or not reason:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    if points <= 0:
        flash('Points must be a positive integer.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    house = House.query.get_or_404(house_id)

    house.house_points -= points

    trasnaction = PointTransaction(
        house_id=house.id,
        points_change=points,
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(trasnaction)
    db.session.commit()
    flash(f'Successfully deduct {points} points to {house.name}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/captain_dashboard')
@login_required
def captain_dashboard():
    house = None
    members = None

    my_announcements = Announcement.query.filter_by(
        captain_id=current_user.id
        ).order_by(Announcement.created_at.desc()).all()
    
    return render_template(
        'dashboard_captain.html',
        house=house,
        members=members
    )

@app.route('/captain/announcements/create', methods=['GET', 'POST'])
@login_required
@captain_required
def captain_create_announcement():
    if request.method == 'POST':
        title = request.form('title', '').strip()
        content = request.form('content', '').strip()

        if not title or not content:
            flash('Title and content are required.', 'error')
            return redirect(url_for('captain_create_announcement'))
        
        if len(title) > 200:
            flash('Title must be less than 200 characters.', 'error')
            return redirect(url_for('captain_create_announcement'))
        
        announcements = Announcement(
            title=title,
            content=content,
            house_id=current_user.house_id,
            captain_id=current_user.id
        )

        db.session.add(announcements)
        db.session.commit()

        flash('Announcement created successfully.', 'success')
        return redirect(url_for('captain_dashboard'))
    
    return render_template('create_announcement.html')

@app.route('/captain/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
@captain_required
def captain_delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    if announcement.captain_id != current_user.id:
        abort(403)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted successfully.', 'success')
    return redirect(url_for('captain_dashboard'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
