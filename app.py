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
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    '330bf9312848e19d9a88482a033cb4f566c4cbe06911fe1e452ebade42f0bc4c'
)

# Session config for cross-origin cookies
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
)

# ✅ Global CORS (THIS is the only CORS you need)
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "https://darsahouse.netlify.app",
                "https://houses-web.onrender.com",
            ]
        }
    }
)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# =====================
# Auth helpers
# =====================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated

def captain_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Captain):
            abort(403)
        return f(*args, **kwargs)
    return decorated

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id)) or Captain.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

# =====================
# PUBLIC API
# =====================

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
    return jsonify([
        {
            "rank": i + 1,
            "name": h.name,
            "points": h.house_points,
            "description": h.description
        }
        for i, h in enumerate(houses)
    ])

@app.route('/api/members')
def members():
    house_name = request.args.get('house')
    houses = (
        [House.query.filter_by(name=house_name).first()]
        if house_name else
        House.query.order_by(House.name).all()
    )

    if house_name and not houses[0]:
        return jsonify({"error": "House not found"}), 404

    return jsonify([
        {
            "house": {
                "id": h.id,
                "name": h.name,
                "description": h.description
            },
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "role": m.role
                }
                for m in Member.query.filter_by(house_id=h.id).all()
            ]
        }
        for h in houses
    ])

@app.route('/api/announcements')
def announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at.isoformat(),
            "house": {"id": a.house.id, "name": a.house.name},
            "captain": {
                "id": a.captain.id,
                "username": a.captain.username,
                "name": a.captain.name
            }
        }
        for a in anns
    ])

# =====================
# LOGIN / LOGOUT
# =====================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = (
        Admin.query.filter_by(username=username).first()
        or Captain.query.filter_by(username=username).first()
    )

    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=True)

        base_url = os.environ.get(
            'BASE_URL',
            'https://houses-web.onrender.com'
        )

        return jsonify({
            "success": True,
            "role": "admin" if isinstance(user, Admin) else "captain",
            "redirect": (
                f"{base_url}/admin/dashboard"
                if isinstance(user, Admin)
                else f"{base_url}/captain/dashboard"
            )
        })

    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/me')
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "role": "admin" if isinstance(current_user, Admin) else "captain"
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    frontend = os.environ.get(
        'FRONTEND_URL',
        'https://darsahouse.netlify.app'
    )
    return redirect(f"{frontend}/login")

# =====================
# DASHBOARDS
# =====================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    houses = House.query.order_by(House.house_points.desc()).all()
    tx = PointTransaction.query.order_by(
        PointTransaction.timestamp.desc()
    ).limit(10).all()
    return render_template(
        'dashboard_admin.html',
        houses=houses,
        recent_transactions=tx
    )

@app.route('/captain/dashboard')
@login_required
@captain_required
def captain_dashboard():
    house = House.query.get(current_user.house_id)
    members = Member.query.filter_by(house_id=current_user.house_id).all()
    anns = Announcement.query.filter_by(
        captain_id=current_user.id
    ).order_by(Announcement.created_at.desc()).all()
    return render_template(
        'dashboard_captain.html',
        house=house,
        members=members,
        my_announcements=anns
    )

# =====================
# ERRORS
# =====================

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
