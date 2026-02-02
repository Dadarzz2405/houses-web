import os
from flask import Flask, render_template, redirect, url_for, abort, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from functools import wraps
from flask_cors import CORS
from models import Announcement, PointTransaction, db, Admin, House, Captain, Member, Achievement

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '330bf9312848e19d9a88482a033cb4f566c4cbe06911fe1e452ebade42f0bc4c')

# Session configuration - use Lax for same-site, None for cross-site
app.config.update(
    SESSION_COOKIE_SAMESITE="None",  # Required for cross-origin requests
    SESSION_COOKIE_SECURE=True,      # Required when SameSite=None
    SESSION_COOKIE_HTTPONLY=True,
)

# CORS configuration - MUST allow credentials for cross-origin cookies
CORS(app, 
     resources={r"/*": {"origins": [
         "http://localhost:5173",
         "http://localhost:5000",
         "https://houses-web.onrender.com",
         "https://darsahouse.netlify.app"
     ]}},
     supports_credentials=True,  # This is critical!
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Set-Cookie"]  # Allow cookies to be sent
)

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

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

#=========================================================
#                   PUBLIC API ROUTES 
#=========================================================

@app.route("/api/houses")
def get_houses():
    houses = House.query.order_by(House.name).all()
    return jsonify([
        {
            "id": h.id,
            "name": h.name,
            "points": h.house_points,
            "description": h.description
        }
        for h in houses
    ])

@app.route('/api/live-points')
def live_scores():
    houses = House.query.order_by(House.house_points.desc()).all()
    data = []
    for index, house in enumerate(houses, start=1):
        data.append({
            'rank': index,
            'name': house.name,
            'points': house.house_points,
            'description': house.description
        })
    
    return jsonify(data)

@app.route('/api/members')
def members():
    house_filter = request.args.get('house')
    if house_filter:
        house = House.query.filter_by(name=house_filter).first()
        if not house:
            return jsonify({"error": "House not found"}), 404
        houses = [house]
    else:
        houses = House.query.order_by(House.name).all()

    result = []

    for house in houses:
        members = Member.query.filter_by(house_id=house.id).all()
        result.append({
            'house': {
                'id': house.id,
                'name': house.name,
                'description': house.description
            },
            'members': [
                {
                    'id': member.id,
                    'name': member.name,
                    'role': member.role
                }
                for member in members
            ]
        })

    return jsonify(result)

@app.route('/api/announcements')
def announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([
        {
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'created_at': a.created_at.isoformat(),
            'house': {
                'id': a.house.id,
                'name': a.house.name
            },
            'captain': {
                'id': a.captain.id,
                'username': a.captain.username,
                'name': a.captain.name
            }
        }
        for a in announcements
    ])

#=========================================================
#                   LOGIN/LOGOUT ROUTES
#=========================================================

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def api_login():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = (
        Admin.query.filter_by(username=username).first()
        or Captain.query.filter_by(username=username).first()
    )
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=True)  # remember=True helps with persistence
        
        # Use environment variable or default to production URL
        base_url = os.environ.get('BASE_URL', 'https://houses-web.onrender.com')
        
        response_data = {
            'success': True,
            'role': 'admin' if isinstance(user, Admin) else 'captain',
            'redirect': f'{base_url}/admin/dashboard' if isinstance(user, Admin) else f'{base_url}/captain/dashboard'
        }
        
        response = jsonify(response_data)
        # Explicitly set CORS headers
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@app.route('/login', methods=['GET'])
def login():
    # Redirect to frontend login page
    frontend_url = os.environ.get('FRONTEND_URL', 'https://darsahouse.netlify.app')
    return redirect(f'{frontend_url}/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    frontend_url = os.environ.get('FRONTEND_URL', 'https://darsahouse.netlify.app')
    return redirect(f'{frontend_url}/login')

@app.route("/api/me")
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "role": "admin" if isinstance(current_user, Admin) else "captain"
    })

#=========================================================
#                   JINJA TEMPLATE ROUTES (Admin)
#=========================================================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    houses = House.query.order_by(House.house_points.desc()).all()
    recent_transactions = PointTransaction.query.order_by(
        PointTransaction.timestamp.desc()
    ).limit(10).all()
    
    return render_template(
        'dashboard_admin.html', 
        houses=houses,
        recent_transactions=recent_transactions
    )

@app.route('/admin/points/add', methods=['POST'])
@login_required
@admin_required
def admin_add_points():
    house_id = request.form.get('house_id', type=int)
    points = request.form.get('points', type=int)
    reason = request.form.get('reason', '').strip()

    if not house_id or not points or not reason:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    if points <= 0:
        flash('Points must be a positive integer.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    house = House.query.get_or_404(house_id)
    house.house_points += points

    transaction = PointTransaction(
        house_id=house.id,
        points_change=points,
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Successfully added {points} points to {house.name}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/points/deduct', methods=['POST'])
@login_required
@admin_required
def admin_deduct_points():
    house_id = request.form.get('house_id', type=int)
    points = request.form.get('points', type=int)
    reason = request.form.get('reason', '').strip()

    if not house_id or not points or not reason:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    if points <= 0:
        flash('Points must be a positive integer.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    house = House.query.get_or_404(house_id)
    house.house_points -= points

    transaction = PointTransaction(
        house_id=house.id,
        points_change=-points,  
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Successfully deducted {points} points from {house.name}.', 'success')
    return redirect(url_for('admin_dashboard'))

#=========================================================
#                   JINJA TEMPLATE ROUTES (Captain)
#=========================================================

@app.route('/captain/dashboard')
@login_required
@captain_required
def captain_dashboard():
    house = House.query.get(current_user.house_id)
    members = Member.query.filter_by(house_id=current_user.house_id).all()

    my_announcements = Announcement.query.filter_by(
        captain_id=current_user.id
    ).order_by(Announcement.created_at.desc()).all()
    
    return render_template(
        'dashboard_captain.html',
        house=house,
        members=members,
        my_announcements=my_announcements
    )

@app.route('/captain/announcements/create', methods=['GET', 'POST'])
@login_required
@captain_required
def captain_create_announcement():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('Title and content are required.', 'error')
            return redirect(url_for('captain_create_announcement'))
        
        if len(title) > 200:
            flash('Title must be less than 200 characters.', 'error')
            return redirect(url_for('captain_create_announcement'))
        
        from datetime import datetime
        announcement = Announcement(
            title=title,
            content=content,
            house_id=current_user.house_id,
            captain_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(announcement)
        db.session.commit()

        flash('Announcement created successfully.', 'success')
        return redirect(url_for('captain_dashboard'))
    
    return render_template('captain_create_announcement.html')

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

#=========================================================
#                   ERROR HANDLERS
#=========================================================

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)